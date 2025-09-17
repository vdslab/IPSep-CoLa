#!/bin/bash
cd "$(dirname "$0")/.." || exit
TYPE="$1"
METHOD="$2"
NUMBER="$3"
IDX="$4"

SGD="FullSGD(ours)"
WEBCOLA="WebCoLa"
UNICON="UNICON"

echo "$TYPE, $METHOD, $NUMBER, $IDX, $ARGS"

case "$METHOD" in
"$SGD")
	python scripts/draw_sgd.py \
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
	python scripts/draw_unicon.py \
		data/graph/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
		--dest data/drawing/"$METHOD"/"$TYPE"/"$NUMBER"/
	;;
*)
	echo "エラー: 未知の手法です - $METHOD" >&2
	echo "$SGD, $WEBCOLA, $UNICON" >&2
	return 1
	;;
esac

python3 scripts/plot.py \
	data/graph/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
	data/drawing/"$METHOD"/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
	result/plot/"$METHOD"/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".png \
	"${@:5}"
