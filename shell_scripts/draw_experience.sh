#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"
TYPE="$1"
METHOD="$2"
NUMBER="$3"
IDX="$4"

SGD="FullSGD(ours)"
WEBCOLA="WebCoLa"
UNICON="UNICON"

echo "$TYPE, $METHOD, $NUMBER, $IDX, extra_args=${*:5}"

case "$METHOD" in
"$SGD")
	uv run --project "$REPO_ROOT/cli" draw --space euclidean \
		data/graph/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
		--dest data/drawing/"$METHOD"/"$TYPE"/"$NUMBER"/
	;;
"$WEBCOLA")
	node js/src/draw_webcola.js \
		--graphFile data/graph/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
		--output data/drawing/"$METHOD"/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
		--overlapRemoval
	;;
"$UNICON")
	uv run --project "$REPO_ROOT/cli" draw-unicon \
		data/graph/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
		--dest data/drawing/"$METHOD"/"$TYPE"/"$NUMBER"/
	;;
*)
	echo "エラー: 未知の手法です - $METHOD" >&2
	echo "$SGD, $WEBCOLA, $UNICON" >&2
	return 1
	;;
esac

uv run --project "$REPO_ROOT/cli" plot \
	data/graph/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
	data/drawing/"$METHOD"/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
	result/plot/"$METHOD"/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".png \
	"${@:5}"
