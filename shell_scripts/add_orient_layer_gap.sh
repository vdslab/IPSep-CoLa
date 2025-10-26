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

echo "watts_strogatz = 1"
echo "scale_free    = 2"

echo -n "input graph types:"
read -r graph_type
echo "selected type: $graph_type"

# seq: m 01 to 10
# watts_strogatz
for n in $(seq -f "%04g" 100 100 2000); do
	echo "Processing node_$n.json ..."

	seq -f "%02g" 0 19 | parallel --bar -j 8 "
		case '$graph_type' in
		# watts_strogatz
		1)
			python src/script/generator/networkx_watts_strogatz.py \
				'$SAVE_DIR/$n/node_n=${n}_{}.json' \
				--node-number '$n' \
				--neighbor-number 2 \
				--rewiring-prob 0.3
			;;
		# scale_free
		2)
			python src/script/generator/networkx_scale_free.py \
				'$SAVE_DIR/$n/node_n=${n}_{}.json' \
				--node-size '$n'
			;;
		*)
			echo 'Invalid graph type selected.'
			exit 1
			;;
		esac
		# echo 'add orient ...'
		python src/util/graph/orient_edges.py '$SAVE_DIR/$n/node_n=${n}_{}.json' '$SAVE_DIR/$n/node_n=${n}_{}.json'
	"
done

echo "Finished generating orientation files."
