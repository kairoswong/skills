---
title: Error band and panels
intent: Multi-panel figure with a trend ± uncertainty, bars with errors, and a fit
data_shape: "x/y arrays with per-point SEM, plus group means and their errors"
functions: panel_grid, panel_labels, line_with_band, bar_with_error, scatter_with_fit, add_colorbar
not_for: Single-panel figures (use new_axes and one helper)
see_also: 02-family-curves, 03-rounded-heatmap
---

# Error band and panels

The workhorse composite: (a) trend with a shaded uncertainty band, (b) bars with
error bars and a significance bar, (c) scatter with a regression fit and a
colorbar.

```python
fig, axes = pk.panel_grid(1, 3, width="half_page", aspect=0.8)
pk.line_with_band(axes[0], x, y, yerr=sem)
pk.bar_with_error(axes[1], ["Control", "Dose A"], [42, 55], yerr=[3.5, 4.0])
pk.annotate_test(axes[1], 0, 1, a, b, paired=False)
pk.panel_labels(axes, x=-0.28)
```

`panel_grid` keeps every panel on the same shape and sizes the figure from a
preset width; `panel_labels` handles the (a)(b)(c) letters.
