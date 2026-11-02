"""rcParams presets and the style registry."""

from typing import Any, Dict, List, Optional

FONT_STACK = ["Arial", "Helvetica", "Liberation Sans", "Nimbus Sans", "DejaVu Sans"]

_COMMON: Dict[str, Any] = {
    "font.family": "sans-serif",
    "font.sans-serif": list(FONT_STACK),
    "mathtext.fontset": "cm",
    "axes.unicode_minus": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "path",
}

_RULES = {
    "axes.linewidth": 0.3, "lines.linewidth": 0.3, "patch.linewidth": 0.3,
    "xtick.major.width": 0.3, "ytick.major.width": 0.3,
    "xtick.minor.width": 0.3, "ytick.minor.width": 0.3,
    "xtick.major.size": 4, "ytick.major.size": 4,
    "xtick.minor.size": 2, "ytick.minor.size": 2,
}

_BASE = {**_COMMON, **_RULES,
         "font.size": 12, "axes.labelsize": 12, "axes.titlesize": 12,
         "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 10}

_PRINT = {**_BASE,
          "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
          "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
          "axes.linewidth": 0.5, "lines.linewidth": 0.8, "patch.linewidth": 0.5,
          "xtick.major.width": 0.5, "ytick.major.width": 0.5,
          "xtick.minor.width": 0.5, "ytick.minor.width": 0.5,
          "xtick.major.size": 3, "ytick.major.size": 3}

_PRESENTATION = {**_BASE,
                 "font.size": 16, "axes.labelsize": 16, "axes.titlesize": 16,
                 "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 13,
                 "axes.linewidth": 1.2, "lines.linewidth": 1.6, "patch.linewidth": 1.0,
                 "xtick.major.width": 1.2, "ytick.major.width": 1.2,
                 "xtick.major.size": 5, "ytick.major.size": 5}

STYLES: Dict[str, Dict[str, Any]] = {
    "base": _BASE, "print": _PRINT, "presentation": _PRESENTATION,
}


def available_styles() -> List[str]:
    return sorted(STYLES)


def get_style(name: str = "base") -> Dict[str, Any]:
    if name not in STYLES:
        raise ValueError(f"unknown style {name!r}; available: {available_styles()}")
    return dict(STYLES[name])


def register_style(name: str, base: str = "base",
                   overrides: Optional[Dict[str, Any]] = None,
                   **rcparams: Any) -> Dict[str, Any]:
    """Add a style; kwargs accept ``__`` for ``.`` (``font__size=7``)."""
    config = get_style(base)
    config.update(overrides or {})
    config.update({k.replace("__", "."): v for k, v in rcparams.items()})
    STYLES[name] = config
    return dict(config)


def resolve_font(warn: bool = True) -> str:
    """Name of the font matplotlib actually resolves from ``FONT_STACK``."""
    import warnings

    from matplotlib import font_manager

    installed = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((f for f in FONT_STACK if f in installed), "DejaVu Sans")
    if warn and chosen != FONT_STACK[0]:
        warnings.warn(f"{FONT_STACK[0]!r} not installed; using {chosen!r}",
                      RuntimeWarning, stacklevel=2)
    return chosen
