"""Paired raincloud: per-subject lines, half-violins, boxes, significance."""

import argparse
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))

import plotkit as pk  # noqa: E402


def make_data(seed: int = 0):
    rng = np.random.default_rng(seed)
    n = 12
    return [
        (rng.normal(55, 15, n), rng.normal(38, 12, n)),
        (rng.normal(62, 14, n), rng.normal(42, 13, n)),
        (rng.normal(70, 16, n), rng.normal(45, 14, n)),
    ]


def main(out_dir: str = None):
    out_dir = out_dir or tempfile.mkdtemp(prefix="plotkit-")
    pk.use_style("print")
    fig, ax = pk.multi_raincloud(
        make_data(),
        pre_label="Control",
        post_label="Treatment",
        xticklabels=["Scenario 1", "Scenario 2", "Scenario 3"],
    )
    ax.set_ylabel("Score (%)")
    pk.save_fig(fig, "figure", out_dir=out_dir, formats=("svg", "png"), close=True)
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None,
                        help="output directory (default: a temporary directory)")
    main(parser.parse_args().out)
