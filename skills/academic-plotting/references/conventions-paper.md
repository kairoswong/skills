# Optional: paper figure conventions

This is a **preset**, not a rule of the skill. Adopt it when a project numbers
figures the usual way; otherwise let the project decide and just pass
`out_dir=` to `save_fig`.

| Object | Convention | Example |
|---|---|---|
| Notebook | one per main figure | `fig1.ipynb`, `si_fig1.ipynb` (supplementary) |
| Script | one panel per script | `fig1c.py`, `si_fig2a.py` |
| Output | one folder per figure | `assets/fig1/fig1c.svg` |
| Panel id | main `fig<N><letter>`; supplementary `si_fig<N><letter>` | `fig1c`, `si_fig1a` |
| Shared code | library, never a notebook cell blob | `plotkit/statistical.py` |

No version suffixes (`_final_v2`, `—copy`): re-running overwrites the output.

## Wiring it up

```python
from pathlib import Path
from plotkit import save_fig, use_style

PANEL = "fig1c"
OUT = Path("assets") / PANEL[:-1]          # assets/fig1
use_style("print")
# ... build fig ...
save_fig(fig, PANEL, out_dir=OUT, formats=("svg", "png"), close=True)
```

If the project keeps figure code in notebooks, add the installed package once:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent / "src"))   # if installed into src/
```

Prefer installing with `install_plotkit.py --project . --mode link` and a real
import over per-notebook `sys.path` edits.
