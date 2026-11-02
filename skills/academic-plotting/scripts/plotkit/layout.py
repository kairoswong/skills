"""Multi-panel layout: grids and (a)(b)(c) panel labels."""

from typing import Iterable, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .style import FIGSIZE


def panel_label(ax, label: str, x: float = -0.14, y: float = 1.02,
                fontsize: Optional[float] = None, fontweight: str = "bold",
                **text_kwargs):
    """Bold panel letter in axes coordinates, outside the data area."""
    return ax.text(x, y, label, transform=ax.transAxes, ha="left", va="bottom",
                   fontsize=fontsize, fontweight=fontweight, **text_kwargs)


def panel_labels(axes, labels: str = "abcdef", start: int = 0, **kwargs):
    """Label a flat or grid sequence of axes (a), (b), ..."""
    flat = np.asarray(axes, dtype=object).ravel()
    marks = [f"({c})" for c in labels[start:start + flat.size]]
    return [panel_label(ax, mark, **kwargs) for ax, mark in zip(flat, marks)]


def panel_grid(nrows: int = 1, ncols: int = 1, width="double",
               height: Optional[float] = None, aspect: float = 0.66,
               sharex: bool = False, sharey: bool = False, squeeze: bool = True,
               constrained: bool = True, dpi: int = 300, **subplots_kwargs):
    """Figure + axes grid sized from a preset width; panels share one shape."""
    fig_width = FIGSIZE[width][0] if isinstance(width, str) else float(width)
    fig_height = height if height is not None else fig_width * aspect * nrows / ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_width, fig_height), dpi=dpi,
                             sharex=sharex, sharey=sharey, squeeze=squeeze,
                             constrained_layout=constrained, **subplots_kwargs)
    return fig, axes


def grid_axes(axes: Iterable) -> Tuple[list, np.ndarray]:
    """Flatten any subplot return value into a list, keeping the raw array."""
    arr = np.asarray(axes, dtype=object)
    return list(arr.ravel()), arr


def shared_limits(axes: Sequence, axis: str = "y", pad: float = 0.05):
    """Apply one shared axis range (with padding) across panels."""
    flat = np.asarray(axes, dtype=object).ravel()
    getter = "get_ylim" if axis == "y" else "get_xlim"
    setter = "set_ylim" if axis == "y" else "set_xlim"
    lows, highs = zip(*[getattr(ax, getter)() for ax in flat])
    lo, hi = min(lows), max(highs)
    span = hi - lo
    for ax in flat:
        getattr(ax, setter)(lo - span * pad, hi + span * pad)
