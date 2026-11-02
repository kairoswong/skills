# Statistical figures

Distribution + individual points + a summary, for small n. Every helper takes
`seed`, so re-running a script reproduces the figure exactly and never touches
the caller's global numpy state.

## Paired raincloud (two conditions, same subjects)

```python
from plotkit import single_paired_raincloud, multi_raincloud

single_paired_raincloud(ax, pre, post, x_pos=0.0)      # one pair
single_paired_raincloud(ax, pre, post, show_p=False, seed=7)

fig, ax = multi_raincloud(
    [(pre1, post1), (pre2, post2)],
    pre_label="Control", post_label="Treatment",
    xticklabels=["Scenario 1", "Scenario 2"],
)
```

Fixed layout per pair: dots ±0.2, boxes ±0.35, half-violins ±0.55. The legend
sits above the axes so it cannot collide with significance bars; move it with
`legend_bbox`, or `legend=False`. Recoloring: `pre_color=` / `post_color=`.

## Independent groups

```python
from plotkit import box_with_jitter

box_with_jitter(ax, groups, labels=["S1", "S2", "S3"],
                palette=None,           # default: categorical colors
                show_all_points=True,   # False -> IQR outliers only
                seed=0, jitter_std=0.08)
```

`BOX_KWS` is the shared box style (0.3 pt lines, white-star mean, no fliers).
Reuse it for a standalone `ax.boxplot(data, **BOX_KWS)`.

## Paired scatter (points only, no distribution)

```python
from plotkit import paired_scatter

paired_scatter(ax, pre_scores, post_scores,
               pre_label="Control", post_label="Treatment", seed=456)
```

Gradient pairing lines, group means as black-edged squares. Use when the
distribution is already shown elsewhere, or when n is very small.

## Which one

| Data | Helper |
|---|---|
| Same subjects, two conditions | `single_paired_raincloud` / `multi_raincloud` |
| Independent groups, n ≲ 30 | `box_with_jitter` |
| Paired values, distribution shown separately | `paired_scatter` |
| Mean ± uncertainty over a continuous axis | `line_with_band` (see [plots.md](./plots.md)) |

Significance: `multi_raincloud(show_p=True)` runs a paired t-test per pair. For
Wilcoxon, corrections, or exact p-values, draw it yourself with
`annotate_test` ([annotate.md](./annotate.md)).
