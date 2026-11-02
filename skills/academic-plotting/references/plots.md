# Everyday plots: lines, bars, colorbars

## Line with uncertainty

```python
from plotkit import line_with_band, uncertainty_band

line_with_band(ax, x, mean, yerr=sem, label="Mean ± SEM")
line_with_band(ax, x, mean, band=(lower, upper), color="#4C72B0", marker="o")

# equivalent, when lower/upper are separate arrays:
uncertainty_band(ax, x, mean, lower, upper, color="#4C72B0")
```

`band` accepts either symmetric half-widths (`mean ± band`) or a
`(lower, upper)` pair; `yerr` is an alias for the symmetric form. The band is
drawn behind the line; `marker=None` gives a clean mean curve.

## Bars with errors

```python
from plotkit import bar_with_error

bar_with_error(ax, ["Control", "Dose A", "Dose B"],
               values=[42.0, 55.5, 61.0],
               yerr=[3.5, 4.0, 3.0],
               colors=None,          # default: categorical colors
               label_fmt=None)       # None hides the per-bar value labels
```

Value labels are offset by a fraction of the y span, so the call survives unit
changes. For several conditions side by side use `grouped_bars`
([comparison.md](./comparison.md)), which takes the same `yerr` mapping.

## Colorbars

```python
from plotkit import scalar_mappable, add_colorbar, sequential_cmap

sm = scalar_mappable(sequential_cmap("#4FBCB8"), 0, 1)
add_colorbar(fig, sm, ax=ax, label="Density")
add_colorbar(fig, points, ax=ax, label="Trial index")   # from ax.scatter(...)
add_colorbar(fig, sm, ax=ax, orientation="horizontal", fraction=0.06)
```

`add_colorbar` drops the outline, sets tick size/width and puts vertical ticks
on the right. Pass the object returned by `scatter`/`imshow`/`pcolormesh`
directly when the colors encode data; use `scalar_mappable` for an empty scale.

## Headroom for legends and annotations

```python
from plotkit import resize_y

resize_y(ax, top_pad=0.18)     # 18% headroom above the data
```

Use it before adding legends outside the data area or significance brackets
above the highest point.
