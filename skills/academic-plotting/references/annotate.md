# Statistical annotation

Never hand-write `***` logic: tests return p-values, `p_to_stars` maps them to
labels, and the drawing helpers place them.

## p-values to labels

```python
from plotkit import p_to_stars, DEFAULT_THRESHOLDS

p_to_stars(0.0004)              # '***'
p_to_stars(0.03)                # '*'
p_to_stars(0.2)                 # 'ns'
p_to_stars(0.03, exact=True)    # 'p = 0.03'  — venues that forbid stars
p_to_stars(0.0004, exact=True)  # 'p < 0.001'
p_to_stars(0.004, thresholds=((0.005, '†'), (0.05, '*')))
```

`DEFAULT_THRESHOLDS = ((0.001, '***'), (0.01, '**'), (0.05, '*'))`; pass your
own tuple for dagger/symbol schemes. `nan` returns `'ns'`.

## Choosing a test

```python
from plotkit import compare, anova, adjust, describe, effect_size

compare(control, treatment)                    # paired t-test; .p, .effect_size
compare(control, treatment, test="wilcoxon")   # non-parametric paired
compare(control, treatment, test="welch")      # unpaired, unequal variance
compare(a, b, test="mannwhitney")              # non-parametric unpaired
compare(a, b).label()                          # stars for that p
compare(a, b).label(exact=True)                # 'p = 0.03'

anova([g1, g2, g3])                            # one-way ANOVA over k groups
anova([g1, g2, g3], test="kruskal")            # non-parametric equivalent
adjust([0.01, 0.04, 0.2])                      # Holm correction
describe([g1, g2])                             # mean/sd/sem/median/q1/q3/n
effect_size(a, b, paired=True)                 # Cohen's dz / Cohen's d
```

`TESTS = ('auto', 'paired_t', 'welch', 'student', 'wilcoxon', 'mannwhitney')`.
`compare` returns a `TestResult(test, statistic, p, n, paired, effect_size)`.
scipy is imported lazily: `import plotkit` works without it, statistical calls
raise an actionable `ImportError` if it is missing.

## Drawing the label

```python
from plotkit import add_sig_bar, sig_bar_height, add_bracket, annotate_test

y = sig_bar_height([pre, post])          # data max + 8% of range
add_sig_bar(ax, 0.0, 1.0, y, "**")
add_sig_bar(ax, 0.0, 1.0, y, "**", fontsize=8)

add_bracket(ax, 0, 3, 95, "Group A")     # spans several columns
add_bracket(ax, 0, 3, 95, "Group A", dy=3, dt=5)   # hand-tuned data units

annotate_test(ax, 0, 3, a, b, test="welch")        # test + label in one call
```

Both helpers scale their lift by the current y span (defaults: bar tick 2%,
text 5%; bracket lift 2%, text 4%), so the same call works on a 0-5 scale and a
0-110 scale. Call them after the axis limits are final, or pass `y` explicitly.

## Typical two-condition panel

```python
from plotkit import annotate_test, multi_raincloud

fig, ax = multi_raincloud([(pre, post)], xticklabels=["Scenario"])
ax.set_ylabel("Score (%)")
annotate_test(ax, -0.35, 0.35, pre, post)   # paired t-test by default
```

`multi_raincloud` already annotates each pair when `show_p=True` (the default);
use `annotate_test` for custom tests, corrections, or extra comparisons.
