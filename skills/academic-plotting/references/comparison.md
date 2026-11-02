# Comparison and matrix figures

## Family curves (sweeps, robustness)

```python
from plotkit import plot_family_curves, register_family

register_family("System A", "#6CA6A0", "s")
handles = plot_family_curves(ax, x, data, "System A", title="System A")
ax.legend(handles=handles, loc="upper left", fontsize=8)

plot_family_curves(ax, x, data, "System A", colors=["#111111", "#222222"],
                   marker="D", scatter_size=22)
```

`data[family][series]` is 1-D aligned with `x`. One hue per family, shades per
series, one marker per family. `x_sorted=True` (default) sorts ascending and
smooths with a monotone Pchip spline — use it for non-uniform sweeps. Legend
markers are sized to match the plotted points.

## Rounded-cell heatmap

```python
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from plotkit import rounded_heatmap, diverging_cmap

cmap, norm = diverging_cmap(), Normalize(1, 5)
rounded_heatmap(ax, scores, cmap, norm,
                values_fmt="{:.0f}",
                row_labels=items, col_labels=subjects,
                show_colorbar=True, colorbar_label="Score")
```

One `FancyBboxPatch` per cell with a gap; in-cell text picks black or white by
cell luminance; row/column labels and a colorbar are optional. Keep matrices
small (roughly < 20 × 20) — one patch per cell is what creates the floating
look and what makes large grids slow.

## Grouped bars

```python
from plotkit import grouped_bars

grouped_bars(ax, ["G1", "G2", "G3"],
             {"Control": [10, 20, 30], "Treatment": [12, 18, 26]},
             yerr={"Control": [2, 3, 2], "Treatment": [2, 2, 3]},
             label_fmt="{:.1f}")
```

Values are labelled a fraction of the y span above each bar; `label_fmt=None`
hides them. Error bars accept symmetric or `[lower, upper]` arrays.

## Radar chart

```python
from plotkit import radar_chart, condition

radar_chart(ax, ["Dim 1", "Dim 2", "Dim 3", "Dim 4", "Dim 5", "Dim 6"],
            {"Control": (control_means, condition("control")),
             "Treatment": (treatment_means, condition("treatment"))})
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=7)
```

Top start, clockwise, dashed hexagonal grid. `r_max` defaults to the data
maximum rounded to the grid step (pass a number to share a scale between two
radars). Radial tick labels are off by default because they collide on small
panels; `show_r_labels=True` places them on the vertical spoke. Pass an axes
created with `subplot_kw=dict(polar=True)`.

## Scatter with regression fit

```python
from plotkit import scatter_with_fit

slope, intercept, r2 = scatter_with_fit(ax, xs, ys, "#6BAED6", marker="o")
scatter_with_fit(ax, xs, ys, color="none", markers=False)   # fit only
```

Dashed gray line, 95% CI band, R² annotation. `markers=False` keeps the fit and
skips the points, so you can color points by a third variable and add a
meaningful colorbar with `add_colorbar`.

## Inset size-scale colorbar

```python
from matplotlib.colors import Normalize
from plotkit import size_colorbar

size_colorbar(ax, fig, color="#E8886A", rect=(0.02, 0.1, 0.35, 0.06),
              norm=Normalize(0, 1.5), label="Size")
```
