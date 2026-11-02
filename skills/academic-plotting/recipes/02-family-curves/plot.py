"""Family curves: one hue per family, shades per series, shared marker."""

import argparse
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))

import plotkit as pk  # noqa: E402


SERIES = ["S1", "S2", "S3", "S4"]


def make_data(x):
    curves = {}
    for idx, series in enumerate(SERIES):
        curves[series] = 100 * np.exp(-((x + 5) / 40) ** 2) * (1 + 0.15 * idx)
    curves_b = {}
    for idx, series in enumerate(SERIES):
        curves_b[series] = 80 * np.exp(-((x + 10) / 45) ** 2) * (1 + 0.12 * idx)
    return {"System A": curves, "System B": curves_b}


def main(out_dir: str = None):
    out_dir = out_dir or tempfile.mkdtemp(prefix="plotkit-")
    pk.use_style("print")
    pk.register_family("System A", "#6CA6A0", "s")
    pk.register_family("System B", "#E8886A", "D")

    x = np.array([30, 20, 10, 0, -10], dtype=float)
    data = make_data(x)

    fig, (left, right) = pk.panel_grid(1, 2, width="double")
    for ax, family in zip((left, right), ("System A", "System B")):
        handles = pk.plot_family_curves(ax, x, data, family, title=family)
        ax.legend(handles=handles, loc="upper left", fontsize=8)
        ax.set_xlabel("Sweep variable")
        ax.set_xlim(35, -15)
    left.set_ylabel("Metric (%)")
    pk.panel_labels((left, right))
    pk.save_fig(fig, "figure", out_dir=out_dir, formats=("svg", "png"), close=True)
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None,
                        help="output directory (default: a temporary directory)")
    main(parser.parse_args().out)
