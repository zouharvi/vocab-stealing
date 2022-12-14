#!/usr/bin/env python3

import json
import collections

with open("data_vocab/compute_bpe_all.out", "r") as f:
    data = [json.loads(x) for x in f.readlines()]


out = ""

data_new = collections.defaultdict(dict)

for line in data:
    data_new[
        line["bpe_dataset"]
    ][
        line["target_dataset"]
    ] = line["subword_count"]

# datasets = list(data_new["wmt19"].keys())
bpe_datasets = ["wmt19m", "All", "ParaCrawl", "CCAligned", "EuroPat"]
datasets = ["ParaCrawl", "CCAligned", "EuroPat"]

PRETTY_NAME = {
    "wmt19m": "Victim",
    "All": "All",
    "ParaCrawl": "PCrawl",
    "EuroPat": "Patents",
    "CCAligned": "CCrawl",
}

for bpe_dataset in bpe_datasets:
    data_new_local = data_new[bpe_dataset]
    out += f"& {PRETTY_NAME[bpe_dataset]}"
    for target_dataset in datasets:
        star = r"$\star$" if bpe_dataset == target_dataset else r"\hspace{1.8mm}"
        self_perf = data_new[target_dataset][target_dataset]
        out += f" & {data_new_local[target_dataset]/self_perf:.2f} {star}"
    out += " \\\\ \n"

print(out)
