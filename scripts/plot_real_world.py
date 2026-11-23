#!/usr/bin/env python3
"""Generate the real-world multi-task results bar chart (Figure ``fig:realworld``).

Grouped bar chart in the style of ReconVLA Fig. 6: tasks on the x-axis,
success rate (%) on the y-axis, one bar per method, legend on top.
Only the "Ours" bars are value-labelled (selective direct labels).

Usage:
    python scripts/plot_real_world.py
Output:
    Figures/real_results.pdf

To update the numbers or add tasks/methods, edit TASKS / METHODS / COLORS / DATA
below and re-run. Keep SG-WAM (Ours) last so it is drawn on the right of each group.
Numbers are placeholders (multiples of 2, since each task uses 50 trials).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------- data (edit me)
TASKS   = ["Put Kiwi\ninto Basket", "Stack Bowls\nin Order", "Fill Pan\nin Order",
           "Lift Pot\n(Bimanual)", "Put Kiwi\ninto Basket\n(Height)", "Fill Pan\nin Order\n(Light)"]   # 4 tasks + 2 generalization

METHODS = ["GE-Act", "FastWAM", "SG-WAM (Ours)"]
# DualCoT-style pastels (sampled from image.png), saturation slightly boosted
COLORS  = ["#BFF3FF", "#D4FFC7", "#FFAE99"]
DATA = {                                            # success rate (%) per task
    "GE-Act":        [68, 72, 60, 64, 56, 60],
    "FastWAM":       [72, 76, 64, 68, 52, 56],
    "SG-WAM (Ours)": [84, 88, 76, 80, 72, 76],
}
OUT = os.path.join(os.path.dirname(__file__), os.pardir, "Figures", "real_results.pdf")
# -----------------------------------------------------------------------------

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Nimbus Roman", "Times New Roman", "DejaVu Serif"],
    "font.size": 8, "axes.linewidth": 0.6, "pdf.fonttype": 42,
})

tasks = TASKS
data = DATA

x = np.arange(len(tasks))
n = len(METHODS)
w = 0.84 / n
fig, ax = plt.subplots(figsize=(4.4, 2.5))
for i, m in enumerate(METHODS):
    xs = x - 0.42 + w * (i + 0.5)
    ax.bar(xs, data[m], width=w * 0.95, color=COLORS[i], label=m,
           edgecolor="white", linewidth=0.5, zorder=3)

ax.set_ylim(0, 100)
ax.set_yticks(range(0, 101, 20))
ax.set_xlim(-0.55, len(tasks) - 0.45)   # trim side whitespace
ax.set_xticks(x)
ax.set_xticklabels(tasks, fontsize=8.5)
ax.yaxis.grid(True, color="#cccccc", linewidth=0.5, alpha=0.7, zorder=0)
ax.set_axisbelow(True)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
ax.tick_params(length=2.5, labelsize=9)
# SR (%) label at top-left, horizontal (ReconVLA style), instead of a vertical y-label
ax.text(0.0, 1.03, "Success Rate (%)", transform=ax.transAxes, ha="left", va="bottom", fontsize=11)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.10), ncol=len(METHODS),
          frameon=False, fontsize=10, columnspacing=1.2, handlelength=1.3,
          handletextpad=0.4)
fig.tight_layout(pad=0.4)
fig.savefig(OUT, bbox_inches="tight", pad_inches=0.02)
print("saved", os.path.normpath(OUT))
