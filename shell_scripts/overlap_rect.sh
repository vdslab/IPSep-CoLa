#!/bin/bash
cd "$(dirname "$0")/.." || exit

if [ "$#" -ne 1 ]; then
	echo "Usage: $0 TYPE"
	exit 1
fi

read -r -e -p "start node count: " START_N
read -r -e -p "end node count: " END_N
bash shell_scripts/run_experiment.sh "$1" "$START_N" "$END_N" 100 "overlap"
