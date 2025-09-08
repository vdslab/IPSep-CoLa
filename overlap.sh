#!/bin/bash
for n in `seq -w 100 100 2000`; do python scripts/draw_sgd.py --overlap-removal --dest data/drawing/sgd/overlap/$n data/graph/overlap/$n/*.json; done
for n in `seq -w 100 100 2000`; do
  mkdir -p data/drawing/webcola/overlap/$n
done
for n in `seq -w 100 100 2000`; do for i in `seq -w 0 19`; do  node js/src/draw_webcola.js --graphFile data/graph/overlap/$n/node_n\=${n}_$i.json --output data/drawing/webcola/overlap/$n/node_n\=${n}_$i.json --overlapRemoval; done; done
python scripts/calc_stress.py data/graph/overlap.csv result/stress/overlap-100-2000.csv
python scripts/create_boxplot.py result/stress/overlap-100-2000.csv result/stress/overlap-100-2000.png --title "Webcola stress vs FullSGD stress"