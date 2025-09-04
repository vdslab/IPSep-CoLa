#!/bin/bash

# name,type,n,path
TYPE="layer_fix_rel"
# echo "name,type,n,path"
# for n in `seq -w 100 100 2000`; do for i in `seq -w 0 19`; do echo "node_n=$n\_$i.json,$TYPE,$i,$TYPE/$n/node_n=$n\_$i.json"; done; done

# for n in `seq -w 100 100 2000`; do python scripts/draw_sgd.py --dest data/drawing/sgd/$TYPE/$n data/graph/random_tree/$n/*.json; done
# for n in `seq -w 100 100 2000`; do
#   mkdir -p data/drawing/webcola/$TYPE/$n
# done
for n in `seq -w 100 100 2000`; do for i in `seq -w 0 19`; do  node js/src/draw_webcola.js --graphFile data/graph/random_tree/$n/node_n\=${n}_$i.json --output data/drawing/webcola/$TYPE/$n/node_n\=${n}_$i.json; done; done
python scripts/calc_stress.py data/graph/$TYPE.csv result/stress/$TYPE-100-2000.csv
python scripts/create_boxplot.py result/stress/$TYPE-100-2000.csv result/stress/$TYPE-100-2000.png --title "Webcola stress vs FullSGD stress"