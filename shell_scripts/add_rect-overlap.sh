#!/bin/bash -eEu
shopt -s inherit_errexit
on_error() {
	echo "[Err] ${BASH_SOURCE[1]}:${BASH_LINENO} - '${BASH_COMMAND}' failed" >&2
}
trap on_error ERR

# -----------------------------------------------------------------------------
# 引数チェック
# -----------------------------------------------------------------------------

read -r -e -p "convert from graph directory: " GRAPH_DIR
read -r -e -p "save directory: " SAVE_DIR

for n in $(seq -f "%04g" 100 100 2000); do
	echo "Processing node_$n.json ..."

	seq -f "%02g" 0 19 | parallel --bar -j 8 "
		python src/data/add_rect-overlap_constraint.py \
			--input '$GRAPH_DIR/$n/node_n=${n}_{}.json' \
			--output '$SAVE_DIR/$n/node_n=${n}_{}.json'
		"
done
