---
name: academic-plotting
description: >
  Personal academic figure style for matplotlib: publication styling, semantic
  color roles, statistical annotations (stars, p-values, effect sizes),
  multi-panel layouts, error bands, heatmaps, rainclouds, radar charts, and a
  growing library of runnable figure recipes. Use whenever a figure is created,
  edited, reviewed, or debugged for a paper, thesis, report, or talk — plots,
  charts, panels, colorbars, error bars, significance marks, figure export — or
  when the user wants an existing figure style matched. Chinese-speaking users:
  see references/zh.md.
user-invocable: true
---

# Academic plotting

A personal matplotlib style plus a recipe library, portable across projects.
The library is `scripts/plotkit/`; every example is a runnable folder under
`recipes/`.

## Start here

1. **Matching an existing figure?** Open [recipes/index.md](./recipes/index.md),
   pick the closest row, then read that folder's `recipe.md` and `plot.py`.
   Adapt the data, keep the layout calls.
2. **Building something new?** Read
   [references/api-index.md](./references/api-index.md) (one line per public
   function) and pull details from the reference file for that capability.
3. Never copy style code, palette hex values, or significance logic into a new
   script — import it.

## Install into a project

```bash
python scripts/install_plotkit.py --project /path/to/project --mode copy
python scripts/install_plotkit.py --project /path/to/project --check
```

`--mode link` points the host at this skill's copy instead of duplicating it,
which keeps one source of truth while the skill evolves. Without installation,
add the skill's `scripts/` directory to `sys.path` (recipes do exactly that).

## Pick a style

```python
import plotkit as pk
pk.use_style("print")          # 8 pt at final width — journal submission
pk.use_style("base")           # 12 pt house look — screen review, slides-ready
pk.use_style("presentation")   # 16 pt, heavy rules — talks
```

`print` is the default choice for anything destined for a paper; `base` keeps
the familiar large-text look. Fonts fall back Arial → Helvetica → Liberation
Sans → DejaVu Sans, and a warning names the font actually used, so the same
script does not silently change appearance on another machine.

## Standard workflow

1. **Classify** the figure and pick a recipe or a capability file.
2. **Canvas**: `pk.new_axes("single")`, `pk.mm(89, 67)`, or
   `pk.panel_grid(1, 3, width="double")` — never a bare `figsize` guess.
3. **Data artists**: capability helpers (`line_with_band`, `multi_raincloud`,
   `rounded_heatmap`, ...), not hand-rolled imitations.
4. **Statistics**: `pk.compare(...)` / `pk.annotate_test(...)`, never inline
   `***` logic.
5. **Labels**: `pk.panel_labels(axes)` for (a)(b)(c); `pk.panel_label` for one.
6. **Save**: `pk.save_fig(fig, name, out_dir=...)` — SVG first, PNG preview;
   the host project decides the directory.

## Hard rules

- `use_style()` before creating figures; one style per figure.
- Colors come from **roles** (`pk.condition("control")`,
  `pk.categorical(n)`, `pk.shades(hue, n)`), never raw hex in figure code.
  Register project colors with `register_palette` / `register_family`.
- Significance: `p_to_stars`, `add_sig_bar`, `add_bracket`, `annotate_test`;
  report exact p-values when the venue requires them (`exact=True`).
- Legends: `frameon=False`; keep legend markers the same size as data markers.
- Uncertainty: shaded band or error bars, never a bare mean line.
- Vector first (`.svg`, or `.pdf` with `pdf.fonttype=42`); add
  `rasterized=True` to large data layers (dense heatmaps, images).
- Reproducibility: every jitter/scatter helper takes a `seed`; the same
  script must render the same figure twice.
- Do not duplicate library code inside a figure script or notebook.

## Adding a recipe

```
recipes/<NN-slug>/
├── recipe.md    # frontmatter: title, intent, data_shape, functions, not_for, see_also
└── plot.py      # runnable: main(out_dir) + --out flag
```

`plot.py` renders to `--out` and falls back to a temporary directory, so
running a recipe never drops generated figures into the skill.

Then run `python scripts/list_recipes.py` to regenerate the index, and render
the new `plot.py` twice to confirm it reproduces.

## Extending the library

- **New color vocabulary** → `register_palette(...)` in the figure script or a
  module; keep hex values out of plotting code.
- **New style** → `plotkit.styles.register_style("name", base="print", ...)`.
- **New figure type** → new function in `plotkit/plots.py` (everyday) or
  `plotkit/comparison.py` (specialised); export it from `plotkit/__init__.py`,
  document it in `references/api-index.md`, and add a recipe that uses it.
- **Domain module** (maps, networks, ...) → `plotkit/<domain>.py` in the host
  project, importing `style`/`palettes`/`annotate` from this library.

## Verify before delivering

Render the script, then render it again into another directory; the PNGs should
be byte-identical. For library changes, `python -c "import plotkit"` plus one
recipe is enough.

## Reference map

| File | Contents |
|---|---|
| [api-index.md](./references/api-index.md) | every public function, one line each |
| [style.md](./references/style.md) | styles, canvas presets, axes, saving, panels |
| [palettes.md](./references/palettes.md) | roles, registries, colormaps |
| [annotate.md](./references/annotate.md) | stars, p-values, bars, brackets |
| [statistical.md](./references/statistical.md) | raincloud, box+jitter, paired scatter |
| [plots.md](./references/plots.md) | line+band, bars+errors, colorbars |
| [comparison.md](./references/comparison.md) | family curves, heatmap, grouped bars, radar, fit |
| [conventions-paper.md](./references/conventions-paper.md) | optional paper figure naming preset |
| [troubleshooting.md](./references/troubleshooting.md) | fonts, CJK, SVG, log axes |
| [zh.md](./references/zh.md) | Chinese quick reference (API index, rules, troubleshooting) |
