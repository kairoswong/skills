# Troubleshooting

## `ModuleNotFoundError: plotkit`

The library is not on the path. Either install it
(`python scripts/install_plotkit.py --project . --mode link`) or, for a
throwaway script sitting next to the skill:

```python
import sys
sys.path.insert(0, "/path/to/academic-plotting/scripts")   # folder containing plotkit/
```

`pip install -e scripts/` also works (`pyproject.toml` ships there).

## `ImportError` mentioning scipy

The package imports without scipy; only statistical calls need it
(`compare`, `anova`, `plot_family_curves` smoothing, `scatter_with_fit`).
Install with `pip install scipy`, or use a non-parametric path that does not
need it (e.g. pass explicit error bars instead of running a test).

## Font warning after `use_style()`

`RuntimeWarning: font 'Arial' not installed; using 'Liberation Sans'`. The
figure is fine, but it will not be pixel-identical to a machine with Arial.
Install Arial/Liberation Sans, or accept the fallback — the warning names the
substitute so a PDF review catches the change.

## CJK characters render as boxes

Arial has no CJK glyphs. Register a CJK font and prepend it to the stack:

```python
from matplotlib import font_manager
font_manager.fontManager.addfont("C:/Windows/Fonts/msyh.ttc")   # Microsoft YaHei
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"] + plt.rcParams["font.sans-serif"]
```

`axes.unicode_minus=False` is already set by every style, so minus signs stay
readable after the switch.

## Minus signs render as boxes

Set `plt.rcParams["axes.unicode_minus"] = False` (default in all styles).

## SVG has white padding or clipped labels

`save_fig` uses `bbox_inches="tight"`. If a bracket or legend sits outside the
axes, add `clip_on=False` (the annotation helpers already do), or make room
with `resize_y(ax)`.

## Log-scale axis rejects non-positive values

Start bars at a small positive value instead of 0:

```python
ax.set_yscale("log"); ax.set_ylim(5, 1600); ax.set_yticks([10, 100, 1000])
```

## Reversed x-axis (descending sweep)

```python
ax.set_xlim(35, -15)      # large values on the left
ax.invert_xaxis()         # or, for scatter
```

`plot_family_curves` sorts by ascending x for the spline; the axis direction is
independent of that.

## Pchip interpolation error

`PchipInterpolator` needs strictly increasing x. `plot_family_curves` sorts
internally when `x_sorted=True`; with duplicate x values, aggregate them first
or pass `x_sorted=False`.

## `constrained_layout` warning with inset colorbars

Inset axes are exempt from constrained layout. Drop `constrained_layout` and set
`gridspec_kw=dict(left=..., right=..., bottom=..., top=...)`, or place the
colorbar with `add_colorbar(fig, mappable, ax=ax)` instead of an inset.

## Figure changes between runs

Something is consuming global randomness. Every helper in this library takes a
`seed` and uses `np.random.default_rng`, so check your own code for
`np.random.seed`/`np.random.normal`, and render the script twice into two
directories: the PNGs should be byte-identical.

## Empty or zero-byte output

`save_fig` writes `<out_dir>/<name>.<ext>`; a wrong `out_dir` silently creates a
new directory. Print the returned mapping (`{'svg': path}`) instead of guessing.

## JPEG/PNG looks different from the SVG

PNG rasterises at `dpi=300`; check the figure size before blaming the library.
Use SVG/PDF for delivery and PNG only for previews.
