#!/bin/bash
cd "$(dirname "$0")/.." || exit

# 実験の種類: layer_fix_rel
# ノード数: 100から100まで100刻み
# 違反の種類: constraint

if [ "$#" -ne 1 ]; then
	echo "Usage: $0 TYPE"
	exit 1
fi

bash ./shell_scripts/run_experiment.sh "$1" 100 2000 100 "constraint"
