# Style, canvas, panels and export

## Named styles

```python
from plotkit import use_style, available_styles, register_style

use_style()                     # "base": 12 pt, 0.3 pt rules — house look
use_style("print")              # 8 pt at final width — journal submission
use_style("presentation")       # 16 pt, heavy rules — talks
use_style("print", override={"font.size": 7})
available_styles()              # ['base', 'presentation', 'print']
```

Register your own once, anywhere before plotting:

```python
register_style("thesis", base="print", overrides={"font.size": 9, "axes.linewidth": 0.6})
register_style("draft", font__size=11)      # __ stands for .
```

A style is a plain rcParams dict; `get_style("print")` returns a copy you can
inspect. Every style carries the same font stack and export defaults.

## Fonts

`FONT_STACK = ["Arial", "Helvetica", "Liberation Sans", "Nimbus Sans", "DejaVu Sans"]`.
`use_style()` warns once when the first available font is not Arial and names
the substitute, so a figure does not silently change between machines.
`resolve_font()` returns the font matplotlib actually resolved.

## Canvas presets

```python
from plotkit import FIGSIZE, new_axes, mm

FIGSIZE["single"]            # (4, 3)
FIGSIZE["double"]            # (8, 3)
mm(89, 67)                   # journal single column, in inches
fig, ax = new_axes("single") # figsize + dpi 300 + constrained_layout
fig, ax = new_axes(mm(183, 100), constrained=False)
```

Presets are inches; use `mm()` whenever the target is a journal column width.

## Panels

```python
from plotkit import panel_grid, panel_labels, panel_label, shared_limits

fig, axes = panel_grid(1, 3, width="double", aspect=0.8, sharey=True)
panel_labels(axes)                  # (a) (b) (c), bold, outside each axes
panel_label(axes[0], "a", x=-0.2)   # one panel, custom offset
shared_limits(axes, axis="y")       # one range across panels, with padding
```

`panel_grid` derives the height from `width * aspect * nrows / ncols`, so every
panel keeps its shape no matter how many you add.

## Axes cleanup

```python
from plotkit import clean_axes, set_gray_axes

clean_axes(ax)                     # top/right spines off (already off via style)
clean_axes(ax, color="#898989")    # tint ticks, spines, labels, title
set_gray_axes(ax)                  # gray mode for helper/annotation axes
```

Restore a frame when a figure needs one:

```python
ax.spines["top"].set_visible(True)
ax.spines["right"].set_visible(True)
```

## Saving

```python
from plotkit import save_fig

save_fig(fig, "fig1c", out_dir="assets/fig1")                 # -> SVG, returns {'svg': path}
save_fig(fig, "fig1c", out_dir="assets/fig1", formats=("svg", "png"))
save_fig(fig, "fig1c", subdir="fig1", root=".")               # -> ./assets/fig1/fig1c.svg
save_fig(fig, "fig1c", out_dir="out", svg_text=True)          # keep SVG text editable
```

`out_dir` wins over `root`/`subdir`: the library does not impose a directory
layout. Defaults are `bbox_inches="tight"`, white face, dpi 300, SVG text as
paths (guaranteed appearance), PDF text as Type 42 (editable, accepted by
journals). `close=True` releases the figure; the return value maps
extension → path.

## Layout conventions

- Single column 89 mm, double column 183 mm.
- Stacked pair: `panel_grid(2, 1, width=mm(89, 67)[0], sharex=True)`.
- Side-by-side: `panel_grid(1, 2, width="double")`.
- With `constrained_layout=True`, never hand-set `left/right/bottom/top`.
  Inset axes are exempt from constrained layout; if matplotlib warns, switch
  to explicit `gridspec_kw` margins.
