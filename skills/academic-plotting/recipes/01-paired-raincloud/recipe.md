---
title: Paired raincloud
intent: Paired before/after (or control/treatment) measurements, per-subject change lines
data_shape: "[(pre, post), ...] — one 1-D numeric pair per scenario"
functions: multi_raincloud, single_paired_raincloud, add_sig_bar
not_for: Unpaired or >2-group comparisons (use 04-radar-and-box box_with_jitter)
see_also: 04-radar-and-box
---

# Paired raincloud

Shows the distribution *and* the individual change, which is what reviewers ask
for when n is small.

```python
fig, ax = pk.multi_raincloud(
    [(pre, post), ...],
    pre_label="Control", post_label="Treatment",
    xticklabels=["Scenario 1", "Scenario 2"],
)
ax.set_ylabel("Score (%)")
```

Layout is fixed relative to each `x_pos`: dots ±0.2, boxes ±0.35, violins ±0.55.
`seed` makes the jitter reproducible; `show_p=False` drops the auto paired t-test.

Run `python plot.py --out DIR` to render it outside the skill.
