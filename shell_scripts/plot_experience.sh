#!/bin/bash
cd "$(dirname "$0")/.." || exit

TYPE="$1"
METHOD="$2"
NUMBER="$3"
IDX="$4"

echo "$TYPE, $METHOD, $NUMBER, $IDX, $ARGS"

python3 scripts/plot.py \
	data/graph/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
	data/drawing/"$METHOD"/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
	result/plot/"$METHOD"/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".png \
	"${@:5}"
