"""Comparison and matrix figures: family curves, heatmap, bars, radar, fit."""

from typing import Mapping, Optional, Sequence, Tuple

import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Colormap, LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch

from .palettes import (
    FIT, MODEL_LINESTYLES, categorical, register_family, shades, text_color_on,
)


def plot_family_curves(ax, x, data: Mapping[str, Mapping[str, np.ndarray]],
                       family: str, title: Optional[str] = None,
                       x_sorted: bool = True, smooth: int = 200,
                       colors: Optional[Sequence] = None,
                       marker: Optional[str] = None,
                       scatter_size: float = 22, lw: float = 0.8):
    """One family of curves: hue per family, shades per series, shared marker."""
    from scipy.interpolate import PchipInterpolator

    theme, default_marker = register_family(family)
    marker = marker or default_marker
    series = list(data[family].keys())
    cols = list(colors) if colors else shades(theme, len(series))
    legend_ms = 2.0 * np.sqrt(scatter_size / np.pi)
    handles = []
    for idx, name in enumerate(series):
        raw = np.asarray(data[family][name], dtype=float)
        if x_sorted:
            order = np.argsort(x)
            xs_sorted, ys_sorted = np.asarray(x, dtype=float)[order], raw[order]
            xs = np.linspace(xs_sorted.min(), xs_sorted.max(), smooth)
            ys = PchipInterpolator(xs_sorted, ys_sorted)(xs)
        else:
            xs, ys = x, raw
        linestyle = MODEL_LINESTYLES[idx % len(MODEL_LINESTYLES)]
        ax.plot(xs, ys, linestyle, color=cols[idx], linewidth=lw, alpha=0.9)
        ax.scatter(x, raw, marker=marker, facecolors=cols[idx],
                   edgecolors="white", linewidths=0.3, s=scatter_size, zorder=3)
        handles.append(Line2D([], [], color=cols[idx], linestyle=linestyle,
                              marker=marker, markersize=legend_ms,
                              markerfacecolor=cols[idx], markeredgecolor="white",
                              markeredgewidth=0.3, label=name))
    if title:
        ax.set_title(title)
    return handles


def rounded_heatmap(ax, data, cmap: Colormap, norm: Normalize,
                    gap: float = 0.15, rounding: float = 0.1,
                    alpha: float = 0.85, values_fmt: Optional[str] = None,
                    invert_y: bool = True, equal_aspect: bool = True,
                    fontsize: float = 8,
                    row_labels: Optional[Sequence[str]] = None,
                    col_labels: Optional[Sequence[str]] = None,
                    show_colorbar: bool = False,
                    colorbar_label: Optional[str] = None,
                    colorbar_kwargs: Optional[dict] = None):
    """Rounded-cell heatmap with optional labels and colorbar."""
    data = np.asarray(data, dtype=float)
    n_rows, n_cols = data.shape
    for i in range(n_rows):
        for j in range(n_cols):
            value = data[i, j]
            color = cmap(norm(value))
            rect = FancyBboxPatch(
                (j + gap / 2, i + gap / 2), 1 - gap, 1 - gap,
                boxstyle=f"round,pad=0,rounding_size={rounding}",
                facecolor=color, edgecolor="none", alpha=alpha, zorder=2)
            ax.add_patch(rect)
            if values_fmt:
                ax.text(j + 0.5, i + 0.5, values_fmt.format(value),
                        ha="center", va="center", fontsize=fontsize,
                        color=text_color_on(color))
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    if invert_y:
        ax.invert_yaxis()
    if equal_aspect:
        ax.set_aspect("equal")

    if col_labels is not None:
        ax.set_xticks([j + 0.5 for j in range(n_cols)])
        ax.set_xticklabels(col_labels, fontsize=fontsize)
    else:
        ax.set_xticks([])
    if row_labels is not None:
        ax.set_yticks([i + 0.5 for i in range(n_rows)])
        ax.set_yticklabels(row_labels, fontsize=fontsize)
    else:
        ax.set_yticks([])
    ax.tick_params(axis="both", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    if show_colorbar:
        sm = ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        kwargs = dict(fraction=0.04, pad=0.02,
                      ticks=np.linspace(norm.vmin, norm.vmax, 5))
        kwargs.update(colorbar_kwargs or {})
        cb = ax.figure.colorbar(sm, ax=ax, **kwargs)
        cb.outline.set_visible(False)
        cb.ax.tick_params(labelsize=fontsize, length=2, width=0.4)
        if colorbar_label:
            cb.set_label(colorbar_label, fontsize=fontsize, labelpad=4)


def grouped_bars(ax, groups: Sequence[str],
                 means: Mapping[str, Sequence[float]],
                 colors: Optional[Sequence[str]] = None, bar_width: float = 0.2,
                 yerr: Optional[Mapping[str, Sequence[float]]] = None,
                 label_fmt: Optional[str] = "{:.1f}", label_fontsize: float = 8,
                 value_offset: float = 0.015, capsize: float = 2.0):
    """Grouped bars with optional error bars and value labels."""
    positions = np.arange(len(groups), dtype=float)
    conds = list(means.keys())
    colors = list(colors) if colors else categorical(len(conds))
    offsets = np.linspace(-bar_width * 0.7, bar_width * 0.7, len(conds)) if len(conds) > 1 else [0.0]
    for i, cond in enumerate(conds):
        vals = np.asarray(means[cond], dtype=float)
        pos = positions + offsets[i]
        ax.bar(pos, vals, width=bar_width, facecolor=colors[i], alpha=0.85,
               edgecolor="none", label=cond, zorder=2)
        if yerr is not None and cond in yerr:
            err = np.asarray(yerr[cond], dtype=float)
            ax.errorbar(pos, vals, yerr=err, fmt="none", ecolor="black",
                        elinewidth=0.5, capsize=capsize, capthick=0.5, zorder=3)
    ax.set_xticks(positions)
    ax.set_xticklabels(groups)
    ax.set_xlim(positions[0] - 0.8, positions[-1] + 0.8)
    ax.margins(y=0.12)
    if label_fmt:
        ylo, yhi = ax.get_ylim()
        pad = (yhi - ylo) * value_offset
        for i, cond in enumerate(conds):
            vals = np.asarray(means[cond], dtype=float)
            err = (np.asarray(yerr[cond], dtype=float) if yerr and cond in yerr
                   else np.zeros_like(vals))
            top = err[1] if err.ndim == 2 else err
            for j, val in enumerate(vals):
                ax.text(positions[j] + offsets[i], val + top[j] + pad,
                        label_fmt.format(val), ha="center", va="bottom",
                        fontsize=label_fontsize, color=colors[i])
    for spine in ("right", "top"):
        ax.spines[spine].set_visible(False)


def radar_chart(ax, dims: Sequence[str], series: Mapping[str, Tuple[Sequence, str]],
                r_max: Optional[float] = None,
                grid_levels: Optional[Sequence[float]] = None,
                label_r: float = 1.08, label_fontsize: float = 8,
                show_r_labels: bool = False, fill_alpha: float = 0.3):
    """Radar chart, top start, clockwise; ``r_max`` follows the data."""
    num_dims = len(dims)
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
    angles += angles[:1]
    values = [np.asarray(v, dtype=float) for v, _ in series.values()]
    if r_max is None:
        data_max = max((v.max() for v in values if v.size), default=1.0)
        step = grid_levels[1] - grid_levels[0] if grid_levels and len(grid_levels) > 1 else max(data_max / 5.0, 1.0)
        r_max = float(np.ceil(data_max * 1.05 / step) * step)
    if grid_levels is None:
        step = r_max / 5.0
        grid_levels = np.arange(0, r_max + step * 0.5, step)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, r_max)

    for level in grid_levels:
        ax.plot(angles, np.full_like(angles, level), color="gray",
                linestyle="--", alpha=0.5, linewidth=0.5)
    for angle in angles[:-1]:
        ax.plot([angle, angle], [0, max(grid_levels)], color="gray",
                linestyle="--", alpha=0.5, linewidth=0.5)

    ax.spines["polar"].set_visible(False)
    ax.yaxis.grid(False)
    ax.set_xticks([])
    ax.set_xticklabels([])
    ax.set_yticks([])

    for angle, label in zip(angles[:-1], dims):
        ax.text(angle, r_max * label_r, label, ha="center", va="center",
                fontsize=label_fontsize)

    if show_r_labels:
        for level in grid_levels[1:]:
            ax.text(np.pi / 2, level, f"{level:g}", ha="left", va="bottom",
                    fontsize=label_fontsize, color="gray")

    for name, (vals, color) in series.items():
        closed = np.concatenate([np.asarray(vals, dtype=float),
                                 np.asarray(vals, dtype=float)[:1]])
        ax.plot(angles, closed, "o-", color=color, markersize=3,
                linewidth=1.0, label=name)
        ax.fill(angles, closed, alpha=fill_alpha, color=color, linewidth=0)
    return ax


def scatter_with_fit(ax, xs, ys, color, marker: str = "o", size: float = 45,
                     fit_color: str = FIT, show_band: bool = True,
                     band_alpha: float = 0.18, t_crit: Optional[float] = None,
                     annotate_r2: bool = True, markers: bool = True):
    """Scatter + regression line + 95% CI; returns ``(slope, intercept, r2)``."""
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    slope, intercept = np.polyfit(xs, ys, 1)
    resid = ys - (slope * xs + intercept)
    n, xbar = len(xs), xs.mean()
    if n < 3:
        raise ValueError("scatter_with_fit needs at least 3 points")
    s = np.sqrt(np.sum(resid ** 2) / (n - 2))
    sxx = np.sum((xs - xbar) ** 2)
    if sxx == 0:
        raise ValueError("all x values are identical; no regression is defined")
    r2 = 1.0 - np.sum(resid ** 2) / np.sum((ys - ys.mean()) ** 2)

    if t_crit is None:
        from scipy import stats as _stats
        t_crit = float(_stats.t.ppf(0.975, n - 2))

    x_fit = np.linspace(xs.min(), xs.max(), 200)
    y_fit = slope * x_fit + intercept
    ci = t_crit * s * np.sqrt(1.0 / n + (x_fit - xbar) ** 2 / sxx)
    if show_band:
        ax.fill_between(x_fit, y_fit - ci, y_fit + ci, color=fit_color,
                        alpha=band_alpha, linewidth=0, zorder=1)
    ax.plot(x_fit, y_fit, color=fit_color, linewidth=1.0,
            linestyle=(0, (4, 2)), zorder=2.5)
    if annotate_r2:
        ax.text(0.96, 0.06, f"$R^2$ = {r2:.3f}", transform=ax.transAxes,
                fontsize=8, color=fit_color, ha="right", va="bottom")

    if markers:
        ax.scatter(xs, ys, marker=marker, color=color, s=size,
                   edgecolors="white", linewidth=0.5, zorder=6)
    return slope, intercept, r2


def size_colorbar(ax, fig, color: str, rect=(0.02, 0.1, 0.35, 0.06),
                  norm: Optional[Normalize] = None, label: Optional[str] = None,
                  show_ticks: bool = True, labelsize: float = 8):
    """Inset horizontal size-scale colorbar (point-size legend)."""
    if norm is None:
        norm = Normalize(vmin=0, vmax=1)
    cax = ax.inset_axes(rect)
    cmap = LinearSegmentedColormap.from_list("size_scale", ["white", color])
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    ticks = None if not show_ticks else [
        norm.vmin + (norm.vmax - norm.vmin) * f for f in (0.0, 0.5, 1.0)]
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=ticks)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=labelsize, pad=2, length=3, width=0.5,
                      direction="out", labelbottom=show_ticks)
    if label:
        cb.ax.text(1.1, 0.15, label, transform=cb.ax.transAxes,
                   fontsize=labelsize, ha="left", va="center")
    return cb
