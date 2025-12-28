
from typing import Generator
from tests.test_find_rfc import DummyPage


def apply_map_reduce():
    pages = [DummyPage(i) for i in range(10)]
    sample_sections = range(5)
    for page in pages:
        for section in sample_sections:
            yield (page.title(), section)

def test_apply_map_reduce():
    results = list(apply_map_reduce())
    assert len(results) == 50  # 10 pages * 5 sections each
    assert results[0] == ("0", 0)
    assert results[-1] == ("9", 4)