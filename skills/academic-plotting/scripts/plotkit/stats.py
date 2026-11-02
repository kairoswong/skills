"""Statistical tests, effect sizes, multiple-comparison correction."""

from typing import Any, Dict, List, NamedTuple, Optional, Sequence

import numpy as np

TESTS = ("auto", "paired_t", "welch", "student", "wilcoxon", "mannwhitney")


class TestResult(NamedTuple):
    test: str
    statistic: float
    p: float
    n: int
    paired: bool
    effect_size: float

    def label(self, exact: bool = False, **kwargs: Any) -> str:
        from .annotate import p_to_stars

        return p_to_stars(self.p, exact=exact, **kwargs)


def _scipy():
    try:
        from scipy import stats
    except ImportError as exc:
        raise ImportError("scipy is required for statistical tests; pip install scipy") from exc
    return stats


def _arrays(a, b):
    x, y = np.asarray(a, dtype=float).ravel(), np.asarray(b, dtype=float).ravel()
    if x.size == 0 or y.size == 0:
        raise ValueError("both samples must be non-empty")
    return x, y


def effect_size(a, b, paired: bool = True) -> float:
    """Cohen's dz when paired, Cohen's d otherwise."""
    x, y = _arrays(a, b)
    if paired:
        diff = y - x
        sd = diff.std(ddof=1)
        return float(diff.mean() / sd) if sd > 0 else float("nan")
    pooled = np.sqrt(((x.size - 1) * x.var(ddof=1) + (y.size - 1) * y.var(ddof=1))
                     / (x.size + y.size - 2))
    return float((y.mean() - x.mean()) / pooled) if pooled > 0 else float("nan")


def compare(a, b, test: str = "auto", paired: Optional[bool] = None) -> TestResult:
    """Compare two samples; ``auto`` picks paired t-test or Welch."""
    if test not in TESTS:
        raise ValueError(f"unknown test {test!r}; choose from {TESTS}")
    x, y = _arrays(a, b)
    is_paired = bool(paired) if paired is not None else test in ("paired_t", "wilcoxon")
    if test == "auto":
        test = "paired_t" if is_paired else "welch"
    if is_paired and x.size != y.size:
        raise ValueError(f"paired test needs equal sample sizes, got {x.size} and {y.size}")

    stats = _scipy()
    if test == "paired_t":
        result = stats.ttest_rel(y, x)
    elif test == "student":
        result = stats.ttest_ind(x, y, equal_var=True)
    elif test == "welch":
        result = stats.ttest_ind(x, y, equal_var=False)
    elif test == "wilcoxon":
        result = stats.wilcoxon(x, y)
        is_paired = True
    else:
        result = stats.mannwhitneyu(x, y, alternative="two-sided")
        is_paired = False
    return TestResult(test, float(result.statistic), float(result.pvalue),
                      int(x.size if is_paired else x.size + y.size),
                      is_paired, effect_size(x, y, paired=is_paired))


def anova(groups: Sequence, test: str = "anova") -> TestResult:
    """One-way ANOVA, or Kruskal-Wallis with ``test="kruskal"``."""
    if len(groups) < 2:
        raise ValueError("anova() needs at least two groups")
    arrays = [np.asarray(g, dtype=float).ravel() for g in groups]
    stats = _scipy()
    if test == "kruskal":
        result = stats.kruskal(*arrays)
    elif test == "anova":
        result = stats.f_oneway(*arrays)
    else:
        raise ValueError("test must be 'anova' or 'kruskal'")
    return TestResult(test, float(result.statistic), float(result.pvalue),
                      int(sum(a.size for a in arrays)), False, float("nan"))


def adjust(pvalues: Sequence[float], method: str = "holm") -> List[float]:
    """Holm (default) or Benjamini-Hochberg correction."""
    p = np.asarray(pvalues, dtype=float)
    n = p.size
    order = np.argsort(p)
    ranked = p[order]
    if method == "holm":
        adjusted = np.maximum.accumulate(ranked * (n - np.arange(n)))
    elif method in ("fdr_bh", "bh"):
        adjusted = np.minimum.accumulate((ranked * n / np.arange(1, n + 1))[::-1])[::-1]
    else:
        raise ValueError("method must be 'holm' or 'fdr_bh'")
    out = np.empty_like(adjusted)
    out[order] = np.clip(adjusted, 0.0, 1.0)
    return [float(v) for v in out]


def describe(groups: Sequence) -> Dict[str, np.ndarray]:
    """Mean, SD, SEM, median, quartiles and n per group."""
    stats: Dict[str, List[float]] = {k: [] for k in
                                     ("mean", "sd", "sem", "median", "q1", "q3", "n")}
    for group in groups:
        arr = np.asarray(group, dtype=float).ravel()
        sd = float(arr.std(ddof=1)) if arr.size > 1 else 0.0
        q1, median, q3 = np.percentile(arr, [25, 50, 75])
        stats["mean"].append(float(arr.mean()))
        stats["sd"].append(sd)
        stats["sem"].append(sd / np.sqrt(arr.size) if arr.size > 1 else 0.0)
        stats["median"].append(float(median))
        stats["q1"].append(float(q1))
        stats["q3"].append(float(q3))
        stats["n"].append(float(arr.size))
    return {k: np.asarray(v) for k, v in stats.items()}
