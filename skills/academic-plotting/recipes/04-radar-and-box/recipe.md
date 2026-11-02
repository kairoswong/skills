---
title: Radar and box
intent: Multi-dimension profile beside a per-group distribution
data_shape: "radar: {name: (per-dim values, color)}; box: list of 1-D groups"
functions: radar_chart, box_with_jitter, shades, panel_labels
not_for: More than ~7 radar dimensions, or data that fits a bar chart
see_also: 01-paired-raincloud
---

# Radar and box

Radar for the shape of a multi-dimension score, box+jitter for the spread that
backs it up.

```python
pk.radar_chart(ax, dims, {"Control": (control, pk.condition("control")),
                          "Treatment": (treatment, pk.condition("treatment"))})
pk.box_with_jitter(ax2, groups, labels, pk.shades("#6CA6A0", len(groups)))
```

`r_max` defaults to the data maximum rounded to the grid step; pass it
explicitly only when two radars must share a scale. Radial tick labels are off
by default because they collide on small charts — set `show_r_labels=True` for
large panels.
