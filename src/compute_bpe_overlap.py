#!/usr/bin/env python3

import argparse
import tqdm

args = argparse.ArgumentParser()
args.add_argument("-v1", "--vocab-1", default="data_vocab/wmt19m.de-en.vocab")
args.add_argument("-v2", "--vocab-2", default="data_vocab/All.de-en/orig.vocab")
args.add_argument("-ed", "--explore-difference", action="store_true")
args = args.parse_args()

def load_vocab(f):
    with open(f, "r") as f:
        data = [x.rstrip("\n") for x in f.readlines()]
    return set(data)

vocab1 = load_vocab(args.vocab_1)
vocab2 = load_vocab(args.vocab_2)

def overlap(a, b):
    return 2*len(a & b)/(len(a) + len(b))

print(f"Overlap is: {overlap(vocab1, vocab2):.1%}")

if args.explore_difference:
    print("Missing from v2:", len(vocab1-vocab2), "subwords")
    missing = sorted(vocab1-vocab2, key=lambda x: len(x), reverse=True)
    print(missing)