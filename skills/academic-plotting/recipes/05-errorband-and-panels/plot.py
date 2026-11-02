"""Three-panel composite: trend with uncertainty, bars with errors, fit scatter."""

import argparse
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))

import plotkit as pk  # noqa: E402


def make_data(seed: int = 4):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 12, 40)
    y = 60 - 2.5 * x + 8 * np.sin(x / 2)
    sem = 1.5 + 0.15 * x
    xs = rng.uniform(0, 10, 40)
    ys = 2.2 * xs + 4 + rng.normal(0, 2.0, 40)
    trial = rng.uniform(0, 1, 40)
    return x, y, sem, xs, ys, trial


def main(out_dir: str = None):
    out_dir = out_dir or tempfile.mkdtemp(prefix="plotkit-")
    pk.use_style("print")
    x, y, sem, xs, ys, trial = make_data()

    fig, axes = pk.panel_grid(1, 3, width="half_page", aspect=0.8)
    trend, bars, fit = axes

    pk.line_with_band(trend, x, y, yerr=sem, color=pk.condition("control"),
                      label="Mean ± SEM", marker=None)
    trend.set_xlabel("Time (s)")
    trend.set_ylabel("Amplitude (a.u.)")
    trend.legend(loc="lower left", fontsize=7)

    pk.bar_with_error(bars, ["Control", "Dose A", "Dose B", "Dose C"],
                      [42.0, 55.5, 61.0, 58.5], yerr=[3.5, 4.0, 3.0, 4.5],
                      colors=pk.categorical(4), label_fmt=None)
    bars.set_ylabel("Response (%)")
    pk.annotate_test(bars, 0, 2, [40, 44, 41], [58, 60, 57], paired=False,
                     fontsize=7)

    slope, intercept, r2 = pk.scatter_with_fit(
        fit, xs, ys, color=pk.condition("treatment"), markers=False)
    points = fit.scatter(xs, ys, c=trial, cmap=pk.sequential_cmap(pk.TEAL),
                         vmin=0, vmax=1, s=16, edgecolors="white",
                         linewidths=0.4, zorder=6)
    fit.set_xlabel("Input")
    fit.set_ylabel("Output")
    pk.add_colorbar(fig, points, ax=fit, label="Trial index")

    pk.panel_labels(axes, x=-0.28, y=1.02)
    pk.save_fig(fig, "figure", out_dir=out_dir, formats=("svg", "png"), close=True)
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None,
                        help="output directory (default: a temporary directory)")
    main(parser.parse_args().out)
