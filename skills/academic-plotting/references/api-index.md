# API index

Every public name, one line each. `pk.` below means `import plotkit as pk`.

## Styles and canvas

| Name | Signature | Purpose |
|---|---|---|
| `use_style` | `(style="base", override=None)` | apply a registered rcParams preset |
| `available_styles` | `()` | list registered style names |
| `get_style` | `(name="base")` | copy of a style dict |
| `register_style` | `(name, base="base", overrides=None, **rc)` | add/replace a style |
| `resolve_font` | `(warn=True)` | font actually used from the stack |
| `FONT_STACK` / `STYLES` / `BASE_STYLE` | constants | font fallbacks, registry, default dict |
| `FIGSIZE` | constant | preset canvases in inches |
| `mm` | `(width_mm, height_mm)` | millimetres → inches |
| `new_axes` | `(size="single", dpi=300, constrained=True, **kw)` | figure + one axes |
| `clean_axes` | `(ax, color=None)` | hide top/right, optional tint |
| `set_gray_axes` | `(ax, color="#898989")` | helper-axes gray mode |
| `reset_to_default` | `()` | matplotlib factory rcParams |
| `save_fig` | `(fig, name, subdir="", root=None, out_dir=None, dpi=300, formats=("svg",), close=False, svg_text=False, transparent=False)` | save, returns `{ext: path}` |

## Layout

| Name | Signature | Purpose |
|---|---|---|
| `panel_grid` | `(nrows=1, ncols=1, width="double", height=None, aspect=0.66, sharex=False, sharey=False, squeeze=True, constrained=True, dpi=300, **kw)` | sized figure + axes grid |
| `panel_label` | `(ax, label, x=-0.14, y=1.02, fontsize=None, fontweight="bold", **text)` | one (a) marker |
| `panel_labels` | `(axes, labels="abcdef", start=0, **kw)` | (a)(b)(c) across a flat or grid sequence |
| `grid_axes` | `(axes)` | flatten subplot output |
| `shared_limits` | `(axes, axis="y", pad=0.05)` | one padded range across panels |

## Color

| Name | Signature | Purpose |
|---|---|---|
| `condition` | `(role="control", dark=False)` | role color; aliases pre/post/ours |
| `ROLE_COLORS` / `SYSTEMS` / `CONDITION_COLORS` | constants | role table and its legacy aliases |
| `categorical` | `(n, colors=None, offset=0)` | n categorical hues |
| `shades` / `sequential` | `(hue, n, lo=0.6, hi=1.15)` | light→dark shades of one hue |
| `soften` | `(hex_color, amount=0.35)` | pastel variant |
| `lighten` | `(hex_color, amount=1.01)` | channel scaling |
| `luminance` | `(rgb)` | perceived luminance 0-1 |
| `text_color_on` | `(rgb, dark="white", light="black")` | contrast-safe text color |
| `register_palette` | `(name, mapping)` | project color vocabulary |
| `palette` | `(name)` | read a registered palette |
| `sweep_colors` | `(values, colors=None)` | `{value: color}` |
| `register_family` | `(name, color=None, marker=None)` | family hue + marker |
| `diverging_cmap` | `(low=None, mid="#F0F0F0", high=None, name="diverging")` | role-based diverging map |
| `sequential_cmap` | `(hue, name="sequential", light=None, dark=None)` | one-hue sequential map |
| `truncated_cmap` | `(name, lo=0.25, hi=0.85, n=256)` | slice of a built-in map |
| `paired_gradient_cmap` | `(pre_color, post_color)` | gradient for pairing lines |
| `diverging_sus_cmap` / `sequential_teal_cmap` / `sequential_blue_cmap` | `()` | legacy aliases |
| `CATEGORICAL` / `TONES` / `ACCENT` / `TEAL` / `STEEL` / `FIT` / `FIT_BAND` / `GRAY_AXES` | constants | general-purpose accents |
| `MODEL_SIZES` / `MODEL_SIZES_SOFT` / `MODEL_SIZE_ORDER` / `MODEL_SIZE_MARKERS` / `MODEL_LINESTYLES` / `LAMBDA` / `BARS` / `CER` / `EMR` / `FAMILY_THEME` / `FAMILY_MARKERS` | constants | example registries, kept for compatibility |

## Statistics and annotation

| Name | Signature | Purpose |
|---|---|---|
| `compare` | `(a, b, test="auto", paired=None)` | t/Wilcoxon/Mann-Whitney → `TestResult` |
| `anova` | `(groups, test="anova")` | one-way ANOVA or Kruskal-Wallis |
| `adjust` | `(pvalues, method="holm")` | Holm or BH correction |
| `effect_size` | `(a, b, paired=True)` | Cohen's dz or d |
| `describe` | `(groups)` | mean/sd/sem/median/q1/q3/n |
| `TESTS` / `TestResult` | constant / namedtuple | valid test names; result fields |
| `p_to_stars` | `(p, thresholds=None, exact=False)` | p → stars or exact text |
| `paired_ttest_stars` | `(pre, post, exact=False)` | paired t-test → label |
| `add_sig_bar` | `(ax, x1, x2, y, sig, color="black", lw=0.3, tick_frac=0.02, text_dy_frac=0.05, fontsize=None)` | significance bar |
| `add_bracket` | `(ax, x_start, x_end, y, text, color="black", lw=0.3, dy=None, dt=None, lift_frac=0.02, text_frac=0.04, fontsize=None)` | group bracket |
| `sig_bar_height` | `(groups, frac=0.08)` | suggested y for a bar |
| `annotate_test` | `(ax, x1, x2, data_a, data_b, test="auto", paired=None, y=None, exact=False, **bar_kwargs)` | test + label in one call |
| `DEFAULT_THRESHOLDS` | constant | `((0.001, '***'), (0.01, '**'), (0.05, '*'))` |

## Distribution figures

| Name | Signature | Purpose |
|---|---|---|
| `single_paired_raincloud` | `(ax, pre, post, x_pos=0.0, pre_color=None, post_color=None, show_p=True, seed=123, jitter_std=0.04, show_violin=True, show_box=True)` | one paired raincloud |
| `multi_raincloud` | `(scenarios_data, ax=None, x_positions=None, pre_label="Control", post_label="Treatment", pre_color=None, post_color=None, show_p=True, xticklabels=None, legend=True, legend_bbox=(0.5, 1.04), legend_ncol=2, seed=123)` | several pairs |
| `box_with_jitter` | `(ax, groups, labels=None, palette=None, show_all_points=True, seed=0, jitter_std=0.08)` | boxes + deterministic jitter |
| `paired_scatter` | `(ax, pre_scores, post_scores, pre_label="Control", post_label="Treatment", pre_color=None, post_color=None, pre_x=0.0, post_x=1.0, jitter_std=0.04, seed=456)` | pairing lines + means |
| `BOX_KWS` | constant | shared boxplot style |

## Everyday plots

| Name | Signature | Purpose |
|---|---|---|
| `line_with_band` | `(ax, x, y, band=None, yerr=None, color=None, label=None, marker="o", markersize=3.5, lw=1.0, band_alpha=0.2, zorder=2)` | mean ± uncertainty |
| `uncertainty_band` | `(ax, x, mean, lower, upper, color=None, alpha=0.2, **line_kw)` | band + mean line |
| `bar_with_error` | `(ax, groups, values, yerr=None, colors=None, width=0.6, labels=None, label_fmt="{:.1f}", capsize=2.0, edgecolor="none")` | bars + errors |
| `add_colorbar` | `(fig, mappable, ax=None, label=None, orientation="vertical", fraction=0.05, pad=0.035, aspect=20.0, ticks=None, labelsize=8, **cb_kw)` | compact colorbar |
| `scalar_mappable` | `(cmap, vmin=0.0, vmax=1.0)` | mappable for a colorbar |
| `resize_y` | `(ax, top_pad=0.18, bottom_pad=0.05)` | headroom above data |

## Comparison and matrix

| Name | Signature | Purpose |
|---|---|---|
| `plot_family_curves` | `(ax, x, data, family, title=None, x_sorted=True, smooth=200, colors=None, marker=None, scatter_size=22, lw=0.8)` | one family of curves, legend handles |
| `rounded_heatmap` | `(ax, data, cmap, norm, gap=0.15, rounding=0.1, alpha=0.85, values_fmt=None, invert_y=True, equal_aspect=True, fontsize=8, row_labels=None, col_labels=None, show_colorbar=False, colorbar_label=None, colorbar_kwargs=None)` | rounded cells |
| `grouped_bars` | `(ax, groups, means, colors=None, bar_width=0.2, yerr=None, label_fmt="{:.1f}", label_fontsize=8, value_offset=0.015, capsize=2.0)` | grouped bars + errors |
| `radar_chart` | `(ax, dims, series, r_max=None, grid_levels=None, label_r=1.08, label_fontsize=8, show_r_labels=False, fill_alpha=0.3)` | hexagonal radar |
| `scatter_with_fit` | `(ax, xs, ys, color, marker="o", size=45, fit_color=FIT, show_band=True, band_alpha=0.18, t_crit=None, annotate_r2=True, markers=True)` | fit + CI band, returns `(slope, intercept, r2)` |
| `size_colorbar` | `(ax, fig, color, rect=(0.02, 0.1, 0.35, 0.06), norm=None, label=None, show_ticks=True, labelsize=8)` | inset size legend |
