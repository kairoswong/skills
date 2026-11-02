"""Raincloud, box+jitter and paired-scatter figures."""

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.patches import Patch

from .annotate import add_sig_bar, paired_ttest_stars, sig_bar_height
from .palettes import categorical, condition, paired_gradient_cmap

BOX_KWS = dict(
    widths=0.5, patch_artist=True, showmeans=True,
    medianprops=dict(color="black", linewidth=0.3),
    meanprops=dict(marker="*", markerfacecolor="white",
                   markeredgecolor="black", markeredgewidth=0.3, markersize=5),
    whiskerprops=dict(color="black", linewidth=0.3),
    capprops=dict(color="black", linewidth=0.3),
    boxprops=dict(linewidth=0.3), showfliers=False,
)


def _jitter(positions, n: int, std: float, rng) -> np.ndarray:
    return np.asarray(positions, dtype=float) + rng.normal(0.0, std, n)


def _gradient_lines(ax, x_start, x_end, y_start, y_end, cmap, lw=0.4, alpha=0.5):
    for i in range(len(y_start)):
        xs = np.linspace(x_start[i], x_end[i], 50)
        ys = np.linspace(y_start[i], y_end[i], 50)
        pts = np.array([xs, ys]).T.reshape(-1, 1, 2)
        segments = np.concatenate([pts[:-1], pts[1:]], axis=1)
        lc = LineCollection(segments, cmap=cmap, linewidth=lw, alpha=alpha)
        lc.set_array(np.linspace(0, 1, len(segments)))
        ax.add_collection(lc)


def single_paired_raincloud(ax, pre, post, x_pos: float = 0.0,
                            pre_color: Optional[str] = None,
                            post_color: Optional[str] = None,
                            show_p: bool = True, seed: int = 123,
                            jitter_std: float = 0.04, show_violin: bool = True,
                            show_box: bool = True):
    """One paired raincloud at ``x_pos``; the jitter is local and seeded."""
    pre, post = np.asarray(pre, dtype=float), np.asarray(post, dtype=float)
    pre_color = pre_color or condition("control")
    post_color = post_color or condition("treatment")
    n = len(pre)
    rng = np.random.default_rng(seed)

    pos_scatter = [x_pos - 0.2, x_pos + 0.2]
    pos_box = [x_pos - 0.35, x_pos + 0.35]
    pos_violin = [x_pos - 0.55, x_pos + 0.55]
    jitter = [_jitter(p, n, jitter_std, rng) for p in pos_scatter]

    _gradient_lines(ax, jitter[0], jitter[1], pre, post,
                    paired_gradient_cmap(pre_color, post_color))

    if show_violin:
        for data, pos, color, side in [(pre, pos_violin[0], pre_color, "left"),
                                       (post, pos_violin[1], post_color, "right")]:
            v = ax.violinplot(data, positions=[pos], widths=0.35,
                              showmeans=False, showextrema=False, showmedians=False)
            for body in v["bodies"]:
                verts = body.get_paths()[0].vertices
                verts[:, 0] = np.clip(verts[:, 0],
                                      -np.inf if side == "left" else pos,
                                      pos if side == "left" else np.inf)
                body.set_facecolor(color)
                body.set_alpha(0.45)
                body.set_edgecolor("none")

    if show_box:
        for data, pos, color in [(pre, pos_box[0], pre_color),
                                 (post, pos_box[1], post_color)]:
            bp = ax.boxplot(data, positions=[pos], **dict(BOX_KWS, widths=0.15))
            bp["boxes"][0].set_facecolor(color)
            bp["boxes"][0].set_alpha(0.8)

    ax.scatter(jitter[0], pre, color=pre_color, alpha=0.9, s=22,
               edgecolors="white", linewidths=0.3, zorder=4)
    ax.scatter(jitter[1], post, color=post_color, alpha=0.9, s=22,
               edgecolors="white", linewidths=0.3, zorder=4)

    if show_p:
        add_sig_bar(ax, pos_box[0], pos_box[1],
                    sig_bar_height([pre, post]), paired_ttest_stars(pre, post),
                    fontsize=8)


def multi_raincloud(scenarios_data, ax=None, x_positions: Optional[Sequence] = None,
                    pre_label: str = "Control", post_label: str = "Treatment",
                    pre_color: Optional[str] = None,
                    post_color: Optional[str] = None,
                    show_p: bool = True, xticklabels: Optional[Sequence[str]] = None,
                    legend: bool = True, legend_bbox=(0.5, 1.04),
                    legend_ncol: int = 2, seed: int = 123):
    """Several paired rainclouds side by side. ``scenarios_data = [(pre, post), ...]``."""
    n = len(scenarios_data)
    pre_color = pre_color or condition("control")
    post_color = post_color or condition("treatment")
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 3), dpi=300, constrained_layout=True)
    else:
        fig = ax.figure
    if x_positions is None:
        x_positions = [i * 2 for i in range(n)]

    for i, (pre, post) in enumerate(scenarios_data):
        single_paired_raincloud(ax, pre, post, x_pos=x_positions[i],
                                pre_color=pre_color, post_color=post_color,
                                show_p=show_p, seed=seed + i)

    all_data = np.concatenate([np.asarray(pair, dtype=float).ravel()
                               for pair in scenarios_data])
    y_min, y_max = float(all_data.min()), float(all_data.max())
    y_range = y_max - y_min if y_max > y_min else 1.0

    ax.set_xticks(x_positions)
    ax.set_xticklabels(xticklabels if xticklabels is not None else [""] * n)
    ax.set_ylim(y_min - y_range * 0.10, y_max + y_range * 0.38)
    ax.set_xlim(x_positions[0] - 1.0, x_positions[-1] + 1.0)
    if legend:
        handles = [Patch(facecolor=pre_color, edgecolor="none", label=pre_label),
                   Patch(facecolor=post_color, edgecolor="none", label=post_label)]
        ax.legend(handles=handles, ncol=legend_ncol, loc="lower center",
                  bbox_to_anchor=legend_bbox, frameon=False, fontsize=8)
    return fig, ax


def box_with_jitter(ax, groups, labels=None, palette=None, show_all_points: bool = True,
                    seed: int = 0, jitter_std: float = 0.08):
    """Boxplot plus jittered dots; deterministic for a given ``seed``."""
    if palette is None:
        palette = categorical(len(groups))
    bp = ax.boxplot(groups, positions=range(1, len(groups) + 1), **BOX_KWS)
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(palette[i])
        patch.set_alpha(0.8)

    rng = np.random.default_rng(seed)
    for i, values in enumerate(groups):
        arr = np.asarray(values, dtype=float)
        if show_all_points:
            pts, marker, alpha = arr, "o", 0.6
        else:
            q1, q3 = np.percentile(arr, [25, 75])
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            pts, marker, alpha = arr[(arr < lo) | (arr > hi)], "D", 0.8
        if len(pts) > 0:
            x = rng.normal(i + 1, jitter_std, size=len(pts))
            ax.scatter(x, pts, marker=marker, color=palette[i], alpha=alpha,
                       s=10, edgecolors="white", linewidths=0.5, zorder=4)

    ax.set_xticks(range(1, len(groups) + 1))
    if labels is not None:
        ax.set_xticklabels(labels)
    return ax


def paired_scatter(ax, pre_scores, post_scores,
                   pre_label: str = "Control", post_label: str = "Treatment",
                   pre_color: Optional[str] = None,
                   post_color: Optional[str] = None,
                   pre_x: float = 0.0, post_x: float = 1.0,
                   jitter_std: float = 0.04, seed: int = 456):
    """Paired scatter with gradient lines; group means are black-edged squares."""
    pre_scores = np.asarray(pre_scores, dtype=float)
    post_scores = np.asarray(post_scores, dtype=float)
    pre_color = pre_color or condition("control")
    post_color = post_color or condition("treatment")
    rng = np.random.default_rng(seed)
    n = len(pre_scores)
    x_pre = np.full(n, pre_x) + rng.normal(0, jitter_std, n)
    x_post = np.full(n, post_x) + rng.normal(0, jitter_std, n)

    _gradient_lines(ax, x_pre, x_post, pre_scores, post_scores,
                    paired_gradient_cmap(pre_color, post_color), lw=0.6)

    ax.scatter(x_pre, pre_scores, color=pre_color, alpha=0.9, s=28,
               edgecolors="white", linewidth=0.5, zorder=2)
    ax.scatter(x_post, post_scores, color=post_color, alpha=0.9, s=28,
               edgecolors="white", linewidth=0.5, zorder=2)
    ax.scatter(pre_x, pre_scores.mean(), color=pre_color, s=70, marker="s",
               edgecolors="black", linewidth=0.6, zorder=3)
    ax.scatter(post_x, post_scores.mean(), color=post_color, s=70, marker="s",
               edgecolors="black", linewidth=0.6, zorder=3)

    ax.set_xticks([pre_x, post_x])
    ax.set_xticklabels([pre_label, post_label])
    return ax
