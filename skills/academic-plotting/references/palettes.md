# Palettes: roles, registries, colormaps

Colors are chosen by **meaning**, never by hex value in figure code.

## 1. Condition roles

```python
from plotkit import condition, ROLE_COLORS

condition("control")            # '#A5DBFD' light blue
condition("treatment")          # '#F9A86A' orange
condition("control", dark=True) # darker variant for error bars / strokes
condition("neutral")            # gray reference series
```

Aliases resolve to roles: `baseline`/`before`/`pre` → `control`,
`ours`/`after`/`post`/`proposed` → `treatment`. Unknown roles raise `KeyError`
listing the valid ones.

## 2. Categorical series

```python
from plotkit import categorical, CATEGORICAL, TONES

categorical(3)                  # first three hues of the fixed order
categorical(4, colors=["#111111", "#222222"])   # your own cycle
CATEGORICAL                     # the seven-color order, readable in print
```

Use for unordered categories (models, sites, participants). For ordered series
use shades instead.

## 3. Ordinal shades of one hue

```python
from plotkit import shades, sequential, soften, lighten

shades("#6CA6A0", 4)            # light -> dark, stays visible on white
sequential("#6CA6A0", 4)        # same thing, explicit ordinal meaning
soften("#6BAED6")               # pastel variant (boxplot fills)
lighten("#7B9CC0", 1.1)         # channel scaling, capped at 1
```

`shades` blends toward white at the light end and toward black above 1.0; the
default range `(0.6, 1.15)` keeps the lightest shade printed, not washed out.

## 4. Project vocabularies (registry)

Keep project words out of plotting code:

```python
from plotkit import register_palette, palette, sweep_colors, register_family

register_palette("devices", {"phone": "#4C72B0", "watch": "#55A868"})
palette("devices")["phone"]
sweep_colors([0.7, 0.8, 0.9])   # {0.7: color, 0.8: color, 0.9: color}
register_family("System A", "#6CA6A0", "s")   # hue + marker for family curves
```

Pre-registered examples, kept for backwards compatibility only:
`SYSTEMS` (= `CONDITION_COLORS`), `MODEL_SIZES`, `MODEL_SIZES_SOFT`,
`MODEL_SIZE_MARKERS`, `MODEL_LINESTYLES`, `LAMBDA`, `BARS`. Treat them as
examples of the pattern; define your own groups for a new project.

## 5. Text contrast on cells

```python
from plotkit import luminance, text_color_on

luminance("#A5DBFD")                    # 0-1 perceived luminance
text_color_on("#F9A86A")                # 'black' on light, 'white' on dark
```

## 6. Colormaps

```python
from plotkit import (diverging_cmap, sequential_cmap, truncated_cmap,
                     paired_gradient_cmap)

diverging_cmap()                        # control - white - treatment
diverging_cmap("#2166AC", high="#B2182B", name="coolwarm_like")
sequential_cmap("#4FBCB8")              # light -> hue -> deep
truncated_cmap("inferno", 0.25, 0.85)   # middle slice of a built-in map
paired_gradient_cmap(pre, post)         # gradient for pairing lines
```

Legacy names `diverging_sus_cmap`, `sequential_teal_cmap`,
`sequential_blue_cmap` still work and are aliases of the factories above.
