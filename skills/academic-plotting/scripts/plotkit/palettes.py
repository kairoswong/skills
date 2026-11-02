"""Semantic color roles, project registries, colormaps."""

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

ROLE_COLORS: Dict[str, str] = {
    "control": "#A5DBFD", "treatment": "#F9A86A", "neutral": "#8C8C8C",
    "control_dark": "#7BBFE0", "treatment_dark": "#E8924F", "neutral_dark": "#6E6E6E",
}
_ROLE_ALIASES = {
    "baseline": "control", "before": "control", "pre": "control",
    "ours": "treatment", "after": "treatment", "post": "treatment",
    "proposed": "treatment", "ours_dark": "treatment_dark",
    "baseline_dark": "control_dark",
}


def condition(role: str = "control", dark: bool = False) -> str:
    """Role color; aliases: baseline/before/pre and ours/after/post/proposed."""
    key = _ROLE_ALIASES.get(str(role).lower(), str(role).lower())
    key = f"{key}_dark" if dark else key
    if key not in ROLE_COLORS:
        raise KeyError(f"unknown condition role {role!r}; known: {sorted(ROLE_COLORS)}")
    return ROLE_COLORS[key]


SYSTEMS = {
    "baseline": condition("control"), "ours": condition("treatment"),
    "baseline_dark": condition("control", dark=True),
    "ours_dark": condition("treatment", dark=True),
}
CONDITION_COLORS = SYSTEMS
TONES = ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD", "#DE8F62"]
CATEGORICAL = TONES
ACCENT, TEAL, STEEL = "#E8886A", "#4FBCB8", "#6A8FB5"
FIT, FIT_BAND, GRAY_AXES = "#7a7a7a", "#9a9a9a", "#898989"


def categorical(n: int, colors: Optional[Sequence[str]] = None,
                offset: int = 0) -> List[str]:
    order = list(colors or CATEGORICAL)
    if not order:
        raise ValueError("categorical() needs at least one color")
    return [order[(i + offset) % len(order)] for i in range(n)]


def shades(base_hex: str, n: int, lo: float = 0.6, hi: float = 1.15) -> List[Tuple[float, ...]]:
    """n light-to-dark shades; ``lo`` toward white, ``hi`` > 1 toward black."""
    base = np.array(matplotlib.colors.to_rgb(base_hex))
    out = []
    for t in np.linspace(lo, hi, n):
        rgb = np.ones(3) + (base - np.ones(3)) * t if t <= 1.0 else base * (2.0 - t)
        out.append(tuple(np.clip(rgb, 0.0, 1.0)))
    return out


def sequential(hue: str, n: int, lo: float = 0.6, hi: float = 1.15):
    return shades(hue, n, lo=lo, hi=hi)


def soften(hex_color: str, amount: float = 0.35) -> Tuple[float, ...]:
    base = np.asarray(matplotlib.colors.to_rgb(hex_color))
    return tuple(np.clip(1.0 + (base - 1.0) * (1.0 - amount), 0, 1))


def lighten(hex_color: str, amount: float = 1.01) -> Tuple[float, ...]:
    r, g, b = matplotlib.colors.to_rgb(hex_color)
    return (min(r * amount, 1.0), min(g * amount, 1.0), min(b * amount, 1.0))


def luminance(rgb) -> float:
    r, g, b = np.asarray(rgb)[:3]
    return float(0.299 * r + 0.587 * g + 0.114 * b)


def text_color_on(rgb, dark: str = "white", light: str = "black") -> str:
    """White text on dark cells, black on light ones (luminance < 0.6)."""
    return dark if luminance(rgb) < 0.6 else light


_PALETTES: Dict[str, Dict[Any, str]] = {}


def register_palette(name: str, mapping: Mapping[Any, str]) -> Dict[Any, str]:
    _PALETTES[name] = dict(mapping)
    return _PALETTES[name]


def palette(name: str) -> Dict[Any, str]:
    if name not in _PALETTES:
        raise KeyError(f"unknown palette {name!r}; registered: {sorted(_PALETTES)}")
    return dict(_PALETTES[name])


def sweep_colors(values: Iterable[Any],
                 colors: Optional[Sequence[str]] = None) -> Dict[Any, str]:
    values = list(values)
    return dict(zip(values, categorical(len(values), colors)))


register_palette("training", {"total": "#A6A6A6", "trainable": "#F2B8AC", "frozen": "#B4B6B9"})

MODEL_SIZE_ORDER = ["tiny", "base", "small", "medium"]
MODEL_SIZES = register_palette("model-sizes", {
    "tiny": "#6BAED6", "base": "#FB9C53", "small": "#74C476", "medium": "#9E9AC8",
})
MODEL_SIZE_MARKERS = {"tiny": "o", "base": "D", "small": "s", "medium": "^"}
MODEL_SIZES_SOFT = [soften(MODEL_SIZES[k]) for k in MODEL_SIZE_ORDER]
MODEL_LINESTYLES = ["-", "--", "-.", ":"]

FAMILY_THEME: Dict[str, str] = {}
FAMILY_MARKERS: Dict[str, str] = {}
_MARKERS = ["s", "D", "o", "^", "v", "P"]


def register_family(name: str, color: Optional[str] = None,
                    marker: Optional[str] = None) -> Tuple[str, str]:
    """Register a family hue/marker; returns the effective pair."""
    index = len(FAMILY_THEME)
    FAMILY_THEME.setdefault(name, color or CATEGORICAL[index % len(CATEGORICAL)])
    FAMILY_MARKERS.setdefault(name, marker or _MARKERS[index % len(_MARKERS)])
    return FAMILY_THEME[name], FAMILY_MARKERS[name]


LAMBDA = sweep_colors([0.7, 0.8, 0.9])
BARS = palette("training")
CER, EMR = TEAL, STEEL


def truncated_cmap(name: str, lo: float = 0.25, hi: float = 0.85,
                   n: int = 256) -> ListedColormap:
    return ListedColormap(plt.get_cmap(name)(np.linspace(lo, hi, n)), name=f"{name}_trunc")


def diverging_cmap(low: Optional[str] = None, mid: str = "#F0F0F0",
                   high: Optional[str] = None, name: str = "diverging") -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list(
        name, [low or condition("control"), mid, high or condition("treatment")])


def sequential_cmap(hue: str, name: str = "sequential",
                    light: Optional[str] = None,
                    dark: Optional[str] = None) -> LinearSegmentedColormap:
    light = light or lighten(hue, 1.55)
    dark = dark or tuple(np.clip(np.asarray(matplotlib.colors.to_rgb(hue)) * 0.55, 0, 1))
    return LinearSegmentedColormap.from_list(name, [light, hue, dark])


def diverging_sus_cmap() -> LinearSegmentedColormap:
    return diverging_cmap(name="sus_diverging")


def sequential_teal_cmap() -> LinearSegmentedColormap:
    return sequential_cmap(TEAL, name="cer_teal")


def sequential_blue_cmap() -> LinearSegmentedColormap:
    return sequential_cmap(STEEL, name="emr_blue")


def paired_gradient_cmap(pre_color: str, post_color: str) -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list("grad", [pre_color, post_color])
