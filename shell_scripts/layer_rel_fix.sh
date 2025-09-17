#!/bin/bash
cd "$(dirname "$0")/.." || exit

# 実験の種類: layer_fix_rel
# ノード数: 100から100まで100刻み
# 違反の種類: constraint

bash run_experiment.sh "layer_fix_rel" 100 2000 100 "constraint"
