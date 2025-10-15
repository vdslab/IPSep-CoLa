#!/bin/bash

BASE_GRAPH_DIR="data/graph/scale_free"
SAVE_DIR="data/graph/scale_free"

# seq: m 01 to 10
for n in $(seq -f "%04g" 100 100 2000); do
	echo "Processing node_$n.json ..."
	for m in $(seq -f "%02g" 0 19); do
		python src/util/graph/orient_edges.py \
			"$BASE_GRAPH_DIR"/node_"$n".json \
			"$SAVE_DIR"/"$n"/node_n="$n"_"$m".json
	done
done
echo "Finished generating orientation files."
