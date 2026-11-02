"""Everyday academic plots: lines with uncertainty, bars with errors, colorbars."""

from typing import Optional, Sequence

import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

from .palettes import categorical, condition


def line_with_band(ax, x, y, band=None, yerr=None,
                   color: Optional[str] = None, label: Optional[str] = None,
                   marker: Optional[str] = "o", markersize: float = 3.5,
                   lw: float = 1.0, band_alpha: float = 0.2,
                   zorder: float = 2):
    """Mean line plus a shaded band from half-widths or ``(lower, upper)``."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    color = color or condition("control")
    half = yerr if yerr is not None else band
    if half is not None:
        half = np.asarray(half, dtype=float)
        if half.ndim == 2 and half.shape[0] == 2:
            lower, upper = half
        else:
            lower, upper = y - half, y + half
        ax.fill_between(x, lower, upper, color=color, alpha=band_alpha,
                        linewidth=0, zorder=zorder - 1)
    return ax.plot(x, y, color=color, marker=marker, markersize=markersize,
                   linewidth=lw, label=label, zorder=zorder)[0]


def bar_with_error(ax, groups: Sequence[str], values,
                   yerr=None, colors=None, width: float = 0.6,
                   labels: Optional[Sequence[str]] = None,
                   label_fmt: Optional[str] = "{:.1f}",
                   capsize: float = 2.0, edgecolor: str = "none"):
    """Bars with error bars and optional value labels a span-fraction above."""
    values = np.asarray(values, dtype=float)
    positions = np.arange(len(groups), dtype=float)
    color_list = list(colors) if colors is not None else categorical(len(groups))
    yerr_arr = None if yerr is None else np.asarray(yerr, dtype=float)
    bars = ax.bar(positions, values, width=width, color=color_list,
                  edgecolor=edgecolor, alpha=0.85, zorder=2)
    if yerr_arr is not None:
        ax.errorbar(positions, values, yerr=yerr_arr, fmt="none", ecolor="black",
                    elinewidth=0.5, capsize=capsize, capthick=0.5, zorder=3)
        top = values + (yerr_arr[1] if yerr_arr.ndim == 2 else yerr_arr)
    else:
        top = values
    ax.set_xticks(positions)
    ax.set_xticklabels(groups)
    ax.margins(y=0.12)
    if label_fmt:
        ylo, yhi = ax.get_ylim()
        pad = (yhi - ylo) * 0.015
        for bar, val, top_val in zip(bars, values, top):
            ax.text(bar.get_x() + bar.get_width() / 2, top_val + pad,
                    label_fmt.format(val), ha="center", va="bottom",
                    fontsize=8, color="#3C3C3C")
    if labels is not None:
        ax.legend(labels, frameon=False, fontsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    return bars


def add_colorbar(fig, mappable, ax=None, label: Optional[str] = None,
                 orientation: str = "vertical", fraction: float = 0.05,
                 pad: float = 0.035, aspect: float = 20.0,
                 ticks: Optional[Sequence[float]] = None,
                 labelsize: float = 8, **colorbar_kwargs):
    """Compact colorbar with the shared frame/outline treatment."""
    cb = fig.colorbar(mappable, ax=ax, orientation=orientation,
                      fraction=fraction, pad=pad, aspect=aspect,
                      ticks=ticks, **colorbar_kwargs)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=labelsize, length=3, width=0.5, pad=2)
    if orientation == "vertical":
        cb.ax.yaxis.set_ticks_position("right")
    if label:
        cb.set_label(label, fontsize=labelsize, labelpad=6)
    return cb


def scalar_mappable(cmap, vmin: float = 0.0, vmax: float = 1.0) -> ScalarMappable:
    """Mappable for a colormap, usable with :func:`add_colorbar`."""
    sm = ScalarMappable(norm=Normalize(vmin, vmax), cmap=cmap)
    sm.set_array([])
    return sm


def uncertainty_band(ax, x, mean, lower, upper, color: Optional[str] = None,
                     alpha: float = 0.2, **line_kwargs):
    """Convenience wrapper: draw a band and its mean line together."""
    return line_with_band(ax, x, mean, band=(lower, upper), color=color,
                          band_alpha=alpha, **line_kwargs)


def resize_y(ax, top_pad: float = 0.18, bottom_pad: float = 0.05):
    """Reserve headroom for legends/annotations above the plotted data."""
    lo, hi = ax.get_ylim()
    span = hi - lo
    ax.set_ylim(lo - span * bottom_pad, hi + span * top_pad)
