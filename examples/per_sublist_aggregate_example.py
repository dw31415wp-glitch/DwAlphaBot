"""Example: Per-sublist then Aggregate

This script implements per-sublist summaries (Welford) and aggregates
them into overall mean and variance. It also verifies results by
computing statistics on the flattened data.
"""
from typing import Iterable, List, Tuple, Optional


def summarize_list(L: Iterable[float]) -> Tuple[int, float, float]:
    """Return (n, mean, m2) using Welford's algorithm where m2 is sum((x-mean)^2)."""
    n = 0
    mean = 0.0
    m2 = 0.0
    for x in L:
        n += 1
        delta = x - mean
        mean += delta / n
        delta2 = x - mean
        m2 += delta * delta2
    return n, mean, m2


def aggregate_summaries(summaries: Iterable[Tuple[int, float, float]]) -> dict:
    """Aggregate (n, mean, m2) summaries into overall count, mean, population and sample variance."""
    summaries = list(summaries)
    N = sum(n for n, _, _ in summaries)
    if N == 0:
        return {"count": 0, "mean": None, "population_variance": None, "sample_variance": None}

    overall_mean = sum(n * mu for n, mu, _ in summaries) / N
    total_ss = sum(m2 + n * (mu - overall_mean) ** 2 for n, mu, m2 in summaries)
    population_variance = total_ss / N
    sample_variance = total_ss / (N - 1) if N > 1 else None

    return {
        "count": N,
        "mean": overall_mean,
        "population_variance": population_variance,
        "sample_variance": sample_variance,
    }


def flatten_stats(lists: Iterable[Iterable[float]]) -> dict:
    """Compute naive stats by flattening (for verification)."""
    data = []
    for L in lists:
        data.extend(list(L))
    N = len(data)
    if N == 0:
        return {"count": 0, "mean": None, "population_variance": None, "sample_variance": None}
    mean = sum(data) / N
    ss = sum((x - mean) ** 2 for x in data)
    return {
        "count": N,
        "mean": mean,
        "population_variance": ss / N,
        "sample_variance": ss / (N - 1) if N > 1 else None,
    }


def demo():
    groups = [
        [1.0, 2.0, 3.0],
        [10.0, 12.0],
        [5.5],
        [],
        [7.0, 8.0, 9.0, 10.0],
    ]

    summaries = [summarize_list(g) for g in groups]
    aggregated = aggregate_summaries(summaries)
    flattened = flatten_stats(groups)

    print("Per-sublist summaries (n, mean, m2):")
    for s in summaries:
        print("  ", s)
    print()
    print("Aggregated:")
    for k, v in aggregated.items():
        print(f"  {k}: {v}")
    print()
    print("Flattened verification:")
    for k, v in flattened.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    demo()
