"""Rounded-cell heatmap: rating or matrix data with gaps and optional labels."""

import argparse
import os
import sys
import tempfile

import numpy as np
from matplotlib.colors import Normalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))

import plotkit as pk  # noqa: E402


def make_data(seed: int = 2):
    rng = np.random.default_rng(seed)
    control = rng.integers(1, 6, (10, 12)).astype(float)
    treatment = np.clip(control + rng.integers(-1, 3, control.shape), 1, 5).astype(float)
    return control, treatment


def main(out_dir: str = None):
    out_dir = out_dir or tempfile.mkdtemp(prefix="plotkit-")
    pk.use_style("print")
    control, treatment = make_data()
    cmap, norm = pk.diverging_cmap(), Normalize(1, 5)

    fig, (left, right) = pk.panel_grid(1, 2, width="double")
    pk.rounded_heatmap(left, control, cmap, norm, values_fmt="{:.0f}")
    pk.rounded_heatmap(right, treatment, cmap, norm, values_fmt="{:.0f}",
                       show_colorbar=True, colorbar_label="Score")
    left.set_title("Control", pad=8)
    right.set_title("Treatment", pad=8)
    pk.save_fig(fig, "figure", out_dir=out_dir, formats=("svg", "png"), close=True)
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None,
                        help="output directory (default: a temporary directory)")
    main(parser.parse_args().out)
