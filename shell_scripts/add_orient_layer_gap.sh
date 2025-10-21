#!/bin/bash -eEu
shopt -s inherit_errexit
on_error() {
	echo "[Err] ${BASH_SOURCE[1]}:${BASH_LINENO} - '${BASH_COMMAND}' failed" >&2
}
trap on_error ERR

# -----------------------------------------------------------------------------
# 引数チェック
# -----------------------------------------------------------------------------
if [ "$#" -ne 1 ]; then
	echo "Usage: $0 TYPE"
	exit 1
fi

SAVE_DIR="data/graph/$1"

# seq: m 01 to 10
for n in $(seq -f "%04g" 100 100 2000); do
	echo "Processing node_$n.json ..."

	for m in $(seq -f "%02g" 0 19); do
		file_name="$SAVE_DIR/$n/node_n=${n}_$m.json"
		echo "$file_name"
		python src/script/generator/networkx_watts_strogatz.py \
			"$file_name" \
			--node-number "$n" \
			--neighbor-number 2 \
			--rewiring-prob 0.5
		python src/util/graph/orient_edges.py "$file_name" "$file_name"
	done
done
echo "Finished generating orientation files."
