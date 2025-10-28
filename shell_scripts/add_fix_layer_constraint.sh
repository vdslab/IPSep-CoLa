#!/bin/bash
cd "$(dirname "$0")"/.. || exit 1

read -r -e -p "GRAPH_TYPE: " BASE_GRAPH_DIR
read -r -e -p "SAVE_DIR: " SAVE_DIR

mkdir -p "$SAVE_DIR"

for n in $(seq -f "%04g" 100 100 2000); do
	echo "Processing node_$n.json ..."
	seq -f "%02g" 0 19 | parallel --jobs 8 "
		python src/data/add_layer_constraint.py \
			'$BASE_GRAPH_DIR'/'$n'/node_n='$n'_{}.json \
			'$SAVE_DIR'/'$n'/node_n='$n'_{}.json
	"
	python src/data/gap_layer_to_fixed_layer.py \
		"$SAVE_DIR"/"$n"/node_n="$n"_*.json
done
echo "Finished generating orientation files."
