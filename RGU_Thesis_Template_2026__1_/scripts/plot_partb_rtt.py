#!/usr/bin/env python3
"""Regenerate the Part B (B1) RTT plots from the per-window ping summaries.

Source: the per-window netlab_gen logs, 20 ICMP echoes per target per window,
as tabulated in Chapter "Two Days, Two Devices" (partb/b1_twodays.tex).

Outputs (written next to the report sources):
    report/images/pl1_rtt_per_window.png   -- PL1, median and p95 per window
    report/images/pl2_p95_by_band.png      -- PL2, p95 grouped by window band
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WINDOWS = ["D1W1", "D1W2", "D1W3", "D2W1", "D2W2", "D2W3"]
DATES = ["22-08", "20-08", "20-08", "21-08", "21-08", "22-08"]

# median / p95 in ms, per teammate, per target
DATA = {
    "T2": {
        "2024CS10300": {"median": [4.0, 7.0, 8.0, 4.0, 5.5, 5.0],
                        "p95": [9.3, 7.3, 17.6, 6.0, 11.1, 22.20]},
        "2024CS10582": {"median": [2.65, 3.83, 5.71, 5.12, 4.46, 3.03],
                        "p95": [6.85, 5.14, 12.80, 5.84, 8.37, 5.73]},
    },
    "T3": {
        "2024CS10300": {"median": [59.0, 48.0, 46.0, 46.0, 45.0, 65.0],
                        "p95": [66.1, 60.1, 53.2, 52.9, 49.0, 69.05]},
        "2024CS10582": {"median": [60.50, 50.35, 45.80, 46.25, 44.60, 59.70],
                        "p95": [61.08, 54.19, 48.27, 51.28, 48.11, 83.09]},
    },
}

TITLES = {"T2": "T2  www.iitd.ac.in  (on-campus)",
          "T3": "T3  8.8.8.8  (off-campus)"}
COLOURS = {"2024CS10300": "#1f77b4", "2024CS10582": "#d62728"}
LIGHT = {"2024CS10300": "#6baed6", "2024CS10582": "#f08080"}
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "report", "images")


def plot_pl1():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    x = np.arange(len(WINDOWS))
    for ax, target in zip(axes, ("T2", "T3")):
        for roll in ("2024CS10300", "2024CS10582"):
            ax.plot(x, DATA[target][roll]["median"], "-o", color=COLOURS[roll],
                    linewidth=2, markersize=7, label=f"{roll} median")
            ax.plot(x, DATA[target][roll]["p95"], "--s", color=LIGHT[roll],
                    linewidth=1.8, markersize=7, label=f"{roll} p95")
        ax.set_title(TITLES[target], fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(WINDOWS)
        ax.set_xlabel("Capture window")
        ax.set_ylabel("RTT (ms)")
        ax.grid(alpha=0.3)
    # mark the two windows recorded on 22-08 on the off-campus panel
    ax3 = axes[1]
    for i in (0, 5):
        ax3.annotate(DATES[i], (x[i], DATA["T3"]["2024CS10300"]["p95"][i]),
                     textcoords="offset points", xytext=(4, -12),
                     fontsize=8, color="0.35")
    axes[0].legend(fontsize=9, loc="upper left")
    fig.suptitle("PL1 — RTT median and p95 to T2 and T3, per capture window, "
                 "both teammates", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(OUTDIR, "pl1_rtt_per_window.png"), dpi=150)
    plt.close(fig)


def plot_pl2():
    bands = ["W1", "W2", "W3"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    x = np.arange(len(bands))
    width = 0.2
    for ax, target in zip(axes, ("T2", "T3")):
        series = []
        for roll in ("2024CS10300", "2024CS10582"):
            p95 = DATA[target][roll]["p95"]
            series.append((f"{roll} D1", p95[0:3], COLOURS[roll], None))
            series.append((f"{roll} D2", p95[3:6], LIGHT[roll], "//"))
        for i, (label, vals, colour, hatch) in enumerate(series):
            ax.bar(x + (i - 1.5) * width, vals, width, label=label,
                   color=colour, hatch=hatch, edgecolor="black", linewidth=0.4)
        ax.set_title(TITLES[target], fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(bands)
        ax.set_xlabel("Window band")
        ax.set_ylabel("RTT p95 (ms)")
        ax.grid(axis="y", alpha=0.3)
        ax.set_axisbelow(True)
    axes[0].legend(fontsize=9, loc="upper left")
    fig.suptitle("PL2 — RTT p95 by window band, grouped per teammate "
                 "(hatched = day 2)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(OUTDIR, "pl2_p95_by_band.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    plot_pl1()
    plot_pl2()
    print("wrote pl1_rtt_per_window.png and pl2_p95_by_band.png to", OUTDIR)
