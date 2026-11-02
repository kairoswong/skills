"""Apply styles, size canvases, clean axes, save figures."""

import os
from typing import Any, Dict, Optional, Tuple

import matplotlib.pyplot as plt

from .styles import STYLES, get_style, resolve_font

BASE_STYLE: Dict[str, Any] = STYLES["base"]
MM_PER_INCH = 25.4
FIGSIZE: Dict[str, Tuple[float, float]] = {
    "single": (4, 3),
    "single_wide": (8, 3),
    "double": (8, 3),
    "square": (3, 3),
    "half_page": (7.2, 4.5),
}
_FONT_WARNED = False


def mm(width_mm: float, height_mm: float) -> Tuple[float, float]:
    return (width_mm / MM_PER_INCH, height_mm / MM_PER_INCH)


def use_style(style: str = "base",
              override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Apply a registered style, warning once if Arial is unavailable."""
    global _FONT_WARNED
    config = get_style(style)
    config.update(override or {})
    plt.rcParams.update(config)
    if not _FONT_WARNED:
        resolve_font(warn=True)
        _FONT_WARNED = True
    return config


def reset_to_default():
    plt.rcParams.update(plt.rcParamsDefault)


def clean_axes(ax, color: Optional[str] = None):
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    if color:
        ax.tick_params(colors=color)
        for spine in ax.spines.values():
            spine.set_color(color)
        ax.title.set_color(color)
        ax.xaxis.label.set_color(color)
        ax.yaxis.label.set_color(color)


def set_gray_axes(ax, color: str = "#898989"):
    clean_axes(ax, color=color)


def new_axes(size="single", dpi: int = 300, constrained: bool = True, **kwargs):
    """Figure + axes from a FIGSIZE key, an inch tuple, or ``mm(w, h)``."""
    figsize = FIGSIZE.get(size, size) if isinstance(size, str) else size
    return plt.subplots(figsize=figsize, dpi=dpi,
                        constrained_layout=constrained, **kwargs)


def save_fig(fig, name: str, subdir: str = "", root: Optional[str] = None,
             out_dir: Optional[str] = None, dpi: int = 300,
             formats=("svg",), close: bool = False, svg_text: bool = False,
             transparent: bool = False) -> Dict[str, str]:
    """Save to ``out_dir`` (or ``root/assets/subdir``); returns ``{ext: path}``."""
    if out_dir is None:
        base = os.path.join(root or os.getcwd(), "assets")
        out_dir = os.path.join(base, subdir) if subdir else base
    os.makedirs(out_dir, exist_ok=True)
    previous = plt.rcParams["svg.fonttype"]
    if svg_text:
        plt.rcParams["svg.fonttype"] = "none"
    saved: Dict[str, str] = {}
    try:
        for ext in formats:
            path = os.path.join(out_dir, f"{name}.{ext}")
            fig.savefig(path, dpi=dpi, bbox_inches="tight",
                        facecolor="none" if transparent else "white",
                        edgecolor="none",
                        metadata={"Date": None} if ext in ("svg", "pdf", "eps") else None)
            saved[ext] = path
    finally:
        plt.rcParams["svg.fonttype"] = previous
    if close:
        plt.close(fig)
    return saved
