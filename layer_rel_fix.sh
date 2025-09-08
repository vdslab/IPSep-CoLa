#!/bin/bash

# name,type,n,path
TYPE="layer_fix_rel"
START=100
END=100
STEP=100

GRAPH_DIR="data/graph"
DRAWING_DIR="data/drawing"
STRESS_DIR="result/stress"
VIOLATION_DIR="result/violation"
PLOT_DIR="result/plot"

echo "name,type,n,path" >$GRAPH_DIR/$TYPE.csv
for n in $(seq -f "%04g" $START $STEP $END); do
	for i in $(seq -w 0 19); do
		echo "node_n=${n}_$i.json,$TYPE,$n,$TYPE/$n/node_n=${n}_$i.json" >>$GRAPH_DIR/$TYPE.csv
	done
done

SGD="FullSGD(ours)"
for n in $(seq -f "%04g" $START $STEP $END); do
	python scripts/draw_sgd.py \
		$GRAPH_DIR/$TYPE/"$n"/*.json \
		--dest $DRAWING_DIR/$SGD/$TYPE/"$n"
	for i in $(seq -w 0 5 19); do
		python scripts/plot.py \
			$GRAPH_DIR/$TYPE/"$n"/node_n="$n"_"$i".json \
			$DRAWING_DIR/$SGD/$TYPE/"$n"/node_n="$n"_"$i".json \
			$PLOT_DIR/$SGD/$TYPE/"$n"/node_n="$n"_"$i".png
	done
done

WEBCOLA="WebCoLa"
for n in $(seq -f "%04g" $START $STEP $END); do
	mkdir -p $DRAWING_DIR/$WEBCOLA/$TYPE/"$n"
done
for n in $(seq -f "%04g" $START $STEP $END); do
	for i in $(seq -w 0 19); do
		node js/src/draw_webcola.js \
			--graphFile $GRAPH_DIR/$TYPE/"$n"/node_n="$n"_"$i".json \
			--output $DRAWING_DIR/$WEBCOLA/$TYPE/"$n"/node_n="$n"_"$i".json
	done
	for i in $(seq -w 0 5 19); do
		python scripts/plot.py \
			$GRAPH_DIR/$TYPE/"$n"/node_n="$n"_"$i".json \
			$DRAWING_DIR/$WEBCOLA/$TYPE/"$n"/node_n="$n"_"$i".json \
			$PLOT_DIR/$WEBCOLA/$TYPE/"$n"/node_n="$n"_"$i".png
	done
done

UNICON="UNICON"
for n in $(seq -f "%04g" $START $STEP $END); do
	python scripts/draw_unicon.py \
		--dest $DRAWING_DIR/$UNICON/$TYPE/"$n" \
		$GRAPH_DIR/$TYPE/"$n"/*.json
	for i in $(seq -w 0 5 19); do
		python scripts/plot.py \
			$GRAPH_DIR/$TYPE/"$n"/node_n="$n"_"$i".json \
			$DRAWING_DIR/$UNICON/$TYPE/"$n"/node_n="$n"_"$i".json \
			$PLOT_DIR/$UNICON/$TYPE/"$n"/node_n="$n"_"$i".png
	done
done

python scripts/calc_stress.py \
	$GRAPH_DIR/$TYPE.csv \
	$STRESS_DIR/$TYPE-$START-$END.csv \
	--methods "$SGD" "$WEBCOLA" "$UNICON"

python scripts/create_boxplot.py \
	$STRESS_DIR/$TYPE-$START-$END.csv \
	$STRESS_DIR/$TYPE-$START-$END.png \
	--methods "$UNICON" "$SGD" \
	--title "$UNICON stress vs $SGD stress"

python scripts/calc_violation.py \
	$GRAPH_DIR/$TYPE.csv \
	$VIOLATION_DIR/$TYPE-$START-$END.csv \
	--methods "$SGD" "$WEBCOLA" "$UNICON" \
	--violations constraint

python scripts/create_boxplot.py \
	$VIOLATION_DIR/$TYPE-$START-$END.csv \
	$VIOLATION_DIR/$TYPE-$START-$END.png \
	--methods "$UNICON" "$SGD" \
	--title "$UNICON violation vs $SGD violation"
