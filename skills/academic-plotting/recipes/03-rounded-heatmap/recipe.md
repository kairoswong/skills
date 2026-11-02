---
title: Rounded-cell heatmap
intent: Rating or matrix data where every cell should read as a separate block
data_shape: "2-D array (rows = categories, columns = samples)"
functions: rounded_heatmap, diverging_cmap, add_colorbar
not_for: Continuous fields or large matrices (use ax.imshow with a real colorbar)
see_also: 05-errorband-and-panels
---

# Rounded-cell heatmap

FancyBboxPatch cells with a gap, optional in-cell values with automatic text
contrast, optional row/column labels and colorbar.

```python
cmap, norm = pk.diverging_cmap(), Normalize(1, 5)
pk.rounded_heatmap(ax, scores, cmap, norm,
                   values_fmt="{:.0f}", row_labels=items, col_labels=subjects,
                   show_colorbar=True, colorbar_label="Score")
```

Keep matrices small (roughly < 20 x 20): one patch per cell is what makes the
floating look, and it is also what makes it slow on large grids.
