"""Radar + box: multi-dimension profile next to a group distribution."""

import argparse
import os
import sys
import tempfile

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))

import plotkit as pk  # noqa: E402


def make_data(seed: int = 3):
    rng = np.random.default_rng(seed)
    dims = ["Dim 1", "Dim 2", "Dim 3", "Dim 4", "Dim 5", "Dim 6"]
    control = rng.uniform(25, 45, len(dims))
    treatment = rng.uniform(15, 35, len(dims))
    groups = [rng.normal(m, 8, 20) for m in (55, 48, 40, 33)]
    return dims, control, treatment, groups


def main(out_dir: str = None):
    out_dir = out_dir or tempfile.mkdtemp(prefix="plotkit-")
    pk.use_style("print")
    dims, control, treatment, groups = make_data()

    fig = plt.figure(figsize=(8, 3), dpi=300, constrained_layout=True)
    radar = fig.add_subplot(1, 2, 1, polar=True)
    pk.radar_chart(radar, dims, {
        "Control": (control, pk.condition("control")),
        "Treatment": (treatment, pk.condition("treatment")),
    })
    radar.legend(loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=7)

    box = fig.add_subplot(1, 2, 2)
    pk.box_with_jitter(box, groups, ["S1", "S2", "S3", "S4"],
                       pk.shades("#6CA6A0", len(groups)))
    box.set_ylabel("Metric (%)")

    pk.panel_labels((radar, box), x=-0.05)
    pk.save_fig(fig, "figure", out_dir=out_dir, formats=("svg", "png"), close=True)
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None,
                        help="output directory (default: a temporary directory)")
    main(parser.parse_args().out)
