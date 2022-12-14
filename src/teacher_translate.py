#!/usr/bin/env python3

import argparse
from retry import retry
import tqdm

args = argparse.ArgumentParser()
args.add_argument(
    "--model", default='transformer.wmt19.en-de',
    help="Name of the translation model to use"
)
args.add_argument(
    "-o", "--output", default="data/tmp.txt",
    help="Where to store the data"
)
args.add_argument(
    "-i", "--input", default=None,
)
args.add_argument(
    "-m0", type=int, default=0,
)
args.add_argument(
    "-m1", type=int, default=10**6,
)
args = args.parse_args()

fin = open(args.input, "r")
fout = open(args.output, "w")

@retry(delay=10, jitter=5, tries=10)
def model_wrapper(model):
    import torch
    import fairseq
    if model in {'transformer.wmt19.en-de', 'transformer.wmt19.de-en'}:
        return torch.hub.load(
            'pytorch/fairseq', model,
            checkpoint_file='model1.pt',
            tokenizer='moses', bpe='fastbpe'
        )
    else:
        raise Exception(f"Model {model} not yet covered")


model = model_wrapper(args.model)
model.eval()
# speedup
model = model.bfloat16()
model = model.to("cuda")

batch = []
for line_i, line_src in enumerate(tqdm.tqdm(fin.readlines()[args.m0 * 1000000:args.m1 * 1000000])):
    line_src = line_src.rstrip("\n")
    batch.append(line_src)
    if len(batch) == 2000:
        batch_out = model.translate(batch)
        batch = []
        for line_out in batch_out:
            fout.write(line_out + "\n")
        fout.flush()

if len(batch) != 0:
    batch_out = model.translate(batch)
    batch = []
    for line_out in batch_out:
        fout.write(line_out + "\n")
    fout.flush()

# with bfloat16
# 3:02, 90it/s

# without bfloat16
# 4:00 70it/s