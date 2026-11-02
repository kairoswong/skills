---
title: Family curves
intent: Parameter sweep or robustness curves grouped into families, one hue per family
data_shape: "{family: {series: 1-D values}} plus a shared x array"
functions: plot_family_curves, register_family, panel_grid, panel_labels
not_for: Simple two-line comparisons (plain ax.plot is clearer)
see_also: 05-errorband-and-panels
---

# Family curves

One hue per family, shades per series inside it, one marker per family, so a
legend of 8 curves still reads.

```python
pk.register_family("System A", "#6CA6A0", "s")
handles = pk.plot_family_curves(ax, x, data, "System A", title="System A")
ax.legend(handles=handles, fontsize=8)
```

`x_sorted=True` (default) sorts ascending and smooths with a monotone Pchip
spline — use it for non-uniform sweeps. Unregistered families get a fallback
hue and marker instead of silently sharing teal.
