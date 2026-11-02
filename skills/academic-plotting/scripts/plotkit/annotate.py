"""Statistical testing and significance annotation."""

from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

DEFAULT_THRESHOLDS: Tuple[Tuple[float, str], ...] = ((0.001, "***"), (0.01, "**"), (0.05, "*"))


def p_to_stars(p: float, thresholds: Optional[Sequence[Tuple[float, str]]] = None,
               exact: bool = False) -> str:
    """Stars, or ``p = 0.043`` / ``p < 0.001`` when ``exact``."""
    if p is None or not np.isfinite(p):
        return "ns"
    if exact:
        return "p < 0.001" if p < 0.001 else f"p = {p:.3g}"
    for cut, mark in sorted(thresholds or DEFAULT_THRESHOLDS):
        if p < cut:
            return mark
    return "ns"


def paired_ttest_stars(pre, post, exact: bool = False) -> str:
    from .stats import compare

    return p_to_stars(compare(pre, post, test="paired_t").p, exact=exact)


def add_sig_bar(ax, x1: float, x2: float, y: float, sig: str,
                color: str = "black", lw: float = 0.3,
                tick_frac: float = 0.02, text_dy_frac: float = 0.05,
                fontsize: Optional[float] = None):
    """Two-tick bar + label; lifts are fractions of the current y span."""
    low, high = ax.get_ylim()
    span = high - low
    tick = span * tick_frac
    ax.plot([x1, x1, x2, x2], [y, y + tick, y + tick, y],
            color=color, lw=lw, clip_on=False)
    ax.text((x1 + x2) / 2, y + tick + span * text_dy_frac, sig,
            ha="center", va="bottom", color=color, clip_on=False, fontsize=fontsize)


def add_bracket(ax, x_start: float, x_end: float, y: float, text: str,
                color: str = "black", lw: float = 0.3,
                dy: Optional[float] = None, dt: Optional[float] = None,
                lift_frac: float = 0.02, text_frac: float = 0.04,
                fontsize: Optional[float] = None):
    """Group bracket spanning columns; ``dy``/``dt`` override the span-relative lifts."""
    low, high = ax.get_ylim()
    span = high - low
    lift = dy if dy is not None else span * lift_frac
    text_lift = dt if dt is not None else span * text_frac
    ax.plot([x_start, x_start, x_end, x_end], [y, y + lift, y + lift, y],
            color=color, lw=lw, clip_on=False)
    ax.text((x_start + x_end) / 2, y + text_lift, text, color=color,
            ha="center", va="bottom", clip_on=False, fontsize=fontsize)


def sig_bar_height(data_groups: Sequence, frac: float = 0.08) -> float:
    flat = np.concatenate([np.asarray(g).ravel() for g in data_groups])
    return float(flat.max() + (flat.max() - flat.min()) * frac)


def annotate_test(ax, x1: float, x2: float, data_a, data_b,
                  test: str = "auto", paired: Optional[bool] = None,
                  y: Optional[float] = None, exact: bool = False,
                  **bar_kwargs: Dict[str, Any]) -> str:
    """Run a test on two samples, draw the label, return it."""
    from .stats import compare

    result = compare(data_a, data_b, test=test, paired=paired)
    label = p_to_stars(result.p, exact=exact)
    if y is None:
        y = sig_bar_height([data_a, data_b])
    add_sig_bar(ax, x1, x2, y, label, **bar_kwargs)
    return label
