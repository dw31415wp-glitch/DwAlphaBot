**Per-Sublist Then Aggregate**

- **Overview:** : Compute statistics for each inner list independently, then combine those summaries into global statistics. This is useful when inner lists vary in length, when you need per-group metrics, or when streaming/parallel computation is required.

- **When to use:** : heterogeneous inner lists, memory constraints that prevent flattening, need for per-group diagnostics, or distributed/parallel processing.

**Algorithm (High Level)**

- **Step 1 — Per-sublist pass:** For each inner list `L_i` compute summary statistics: count `n_i`, mean `mu_i`, and variance `var_i` (sample or population as required). Optionally compute min, max, quantiles per list.
- **Step 2 — Aggregate:** Combine per-sublist summaries into overall metrics. Use weighted formulas (by `n_i`) for mean and pooled-variance formulas for variance.

**Key formulas**

- **Weighted mean:**

  Overall mean = (sum_i n_i \* mu_i) / (sum_i n_i)

- **Pooled variance (population):**

  Let N = sum_i n_i. Then pooled variance = (sum_i [n_i * (var_i + mu_i**2)]) / N - overall_mean\*\*2

- **Pooled sample variance (unbiased):**

  If combining sample variances s_i^2 computed with (n_i - 1) denom, compute total_ss = sum_i ((n_i - 1) _ s_i^2 + n_i _ (mu_i - overall_mean)^2) and sample_variance = total_ss / (N - k) where k is number of groups (or use N-1 for overall sample variance depending on desired estimator).

**Python sketch**

```python
from math import inf
from typing import Iterable, List, Tuple

def per_sublist_then_aggregate(lists: Iterable[List[float]]):
    summaries = []  # (n, mean, m2) where m2 is sum((x-mean)^2)
    for L in lists:
        n = 0
        mean = 0.0
        m2 = 0.0
        for x in L:
            n += 1
            delta = x - mean
            mean += delta / n
            delta2 = x - mean
            m2 += delta * delta2
        if n > 0:
            summaries.append((n, mean, m2))

    # Aggregate
    N = sum(n for n,_,_ in summaries)
    if N == 0:
        return {"count": 0, "mean": None, "variance": None}
    overall_mean = sum(n * mu for n,mu,_ in summaries) / N

    # population variance from m2 and between-group squared deviations
    total_ss = sum(m2 + n * (mu - overall_mean)**2 for n,mu,m2 in summaries)
    population_variance = total_ss / N
    sample_variance = total_ss / (N - 1) if N > 1 else None

    return {"count": N, "mean": overall_mean, "population_variance": population_variance, "sample_variance": sample_variance}
```

**Complexity**

- **Time:** O(total_elements) — one pass over each element inside its inner list.
- **Memory:** O(k) for `k` summaries (one per inner list) plus O(1) streaming state per list; does not require storing a full flattened array.

**Notes & Caveats**

- For numeric stability prefer Welford-style accumulation for per-list `m2` and use the two-term aggregation above.
- Choose population vs sample variance carefully when combining; document the estimator semantics for consumers of the metric.
- If inner lists are very small or contain NaNs, decide policy beforehand (skip, treat as zero, or propagate NaN).
- This approach composes well for parallel and distributed settings: compute per-partition summaries, then reduce by the same aggregation formulas.

**Usage patterns**

- **Diagnostics:** keep per-sublist `mean` and `count` for group-level anomaly detection.
- **Streaming:** if sublists arrive over time, compute each summary on arrival and update aggregate with the same formulas.
