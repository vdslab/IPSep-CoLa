#!/bin/bash

for n in `seq -w 100 100 2000`; do  python3 src/data/gap_layer_to_fixed_layer.py data/graph/random_tree/$n/*.json --dest data/graph/layer_fix_rel/$n/ ; done
