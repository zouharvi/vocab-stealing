#!/usr/bin/env python3

import matplotlib.pyplot as plt
import fig_utils
import argparse
import json

# scp euler:/cluster/work/sachan/vilem/vocab-stealing/computed/overlap/*.jsonl computed/overlap/

args = argparse.ArgumentParser()
args.add_argument(
    "--template", default="computed/overlap/wmt19m.teacher-teacher.de-en.SUFFIX.jsonl"
)
args.add_argument(
    "--orig-overlap", type=int, default=0.561,
)
args.add_argument(
    "--teacher-overlap", type=int, default=0.577,
)
args = args.parse_args()

# "uniq_small_lower" "uniq_small"
SUFFIXES = ["uniq", "all", "small_sent", "from_single",]
PRETTY_NAME = {
    "all": "Graybox all",
    "uniq": "Graybox uniq. words",
    "uniq_small": "Graybox unique minimized",
    # "uniq_small_lower": "Graybox uniq. mini. lower.",
    "small_sent": "Graybox sent. mini.",
    "from_single": "From single sent.",
}
SUFFIXES_TEXT_OFFSET = {
    "all": (-1.2, -0.04),
    "uniq": (1, -0.04),
    "uniq_small": (1.8, -0.02),
    "uniq_small_lower": (1.8, -0.02),
    "from_single": (1.8, -0.01),
    "small_sent": (1, -0.025),
}

MARKERS = {
    "all": ".",
    "uniq": ".",
    "uniq_small": ".",
    "uniq_small_lower": ".",
    "from_single": "^",
    "small_sent": ".",
}
MARKERS_SIZE_OFFSET = {
    "all": 0,
    "uniq": 0,
    "uniq_small": 0,
    "uniq_small_lower": 0,
    "from_single": -5,
    "small_sent": 0,
}
SUFFIXES_TEXT_EXTRA = {
    "uniq_small": " (mini.)"
}

# load data
data = {}
for suffix in SUFFIXES:
    with open(args.template.replace("SUFFIX", suffix), "r") as f:
        data[suffix] = [json.loads(x) for x in f.readlines()]


# plot
plt.figure(figsize=(4.8, 3.5))
xticks = []

for s_i, suffix in enumerate(SUFFIXES):
    last_overlap = data[suffix][-1]["overlap"]

        
    end_budget_real = data[suffix][-1]["budget_real"]
    plateau_point = min([
        i for i, x
        in enumerate(data[suffix]) if x["budget_real"] >= end_budget_real
    ])
    
    xticks_local = []
    for i in range(plateau_point+1):
        if i == plateau_point:
            last_budget_real = data[suffix][i]["budget_real"]
            last_budget = data[suffix][i]["budget"]
            last_budget_prev = data[suffix][i]["budget"]//2
            last_budget_point = i + (last_budget_real-last_budget_prev)/last_budget_prev - 1
            xticks_local.append(last_budget_point)
        else:
            xticks_local.append(i)

    print(suffix, last_budget, last_budget_real)

    if len(data[suffix][:plateau_point + 1]) > len(xticks):
        xticks = [x["budget"] for x in data[suffix][:plateau_point + 1]]

    # plot outside of the visible area
    plt.plot(
        [-10], [1], 
        label=PRETTY_NAME[suffix],
        color=fig_utils.COLORS[s_i],
        marker=MARKERS[suffix],
        markersize=15+MARKERS_SIZE_OFFSET[suffix],
    )
    plt.plot(
        xticks_local,
        [x["overlap"] for x in data[suffix][:plateau_point + 1]],
        color=fig_utils.COLORS[s_i],
    )
    plt.plot(
        xticks_local,
        [x["overlap"] for x in data[suffix][:plateau_point + 1]],
        marker=MARKERS[suffix],
        markersize=12+MARKERS_SIZE_OFFSET[suffix],
        alpha=0.5,
        color=fig_utils.COLORS[s_i],
    )
    plt.plot(
        [xticks_local[-1]],
        [data[suffix][plateau_point]["overlap"]],
        marker=MARKERS[suffix],
        markersize=15+MARKERS_SIZE_OFFSET[suffix],
        alpha=1,
    )
    text_offset = SUFFIXES_TEXT_OFFSET[suffix]
    text_extra = SUFFIXES_TEXT_EXTRA[suffix] if suffix in SUFFIXES_TEXT_EXTRA else ""
    plt.text(
        plateau_point + text_offset[0], last_overlap + text_offset[1],
        f"{last_overlap:.1%} [{last_budget_real//1000000}M]" + text_extra,
        # f"{last_overlap:.1%}" + text_extra,
        ha="center",
    )

# plot individual points
plt.scatter(
    [-1], [args.orig_overlap],
    label="Trained locally (original)",
    color=fig_utils.COLORS[6], marker="s"
)
plt.text(
    -0.9, args.orig_overlap + 0.015,
    f"{args.orig_overlap:.1%}", ha="center"
)
plt.scatter(
    [len(xticks) - 1], [args.teacher_overlap],
    label="Trained locally (victim)",
    color=fig_utils.COLORS[5], marker="s"
)
plt.text(
    len(xticks) - 1.04, args.teacher_overlap + 0.015,
    f"{args.teacher_overlap:.1%}", ha="center"
)

plt.xticks(
    [-1] + [i for i in range(len(xticks)) if (i + 1) % 2],
    ["0"] + [
        f"{x/1000000:}".replace(".0", "") + "M"
        for i, x in enumerate(xticks) if (i + 1) % 2
    ],
)
plt.yticks(
    [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    [f"{x:.0%}" for x in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]],
)
plt.xlim(-2)
plt.ylabel("Vocabulary overlap")
plt.xlabel("Subword translation budget (millions, logscaled).")

plt.legend(
    ncol=2,
    bbox_to_anchor=(-0.13, 1, 1.13, 0), loc="lower left", mode="expand"
)
plt.tight_layout(pad=0.1)
plt.savefig("computed/figures/vocab_budget.pdf")
plt.show()
