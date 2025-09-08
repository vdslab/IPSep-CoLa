#!/bin/bash

# name,type,n,path
TYPE="overlap-circle"
# echo "name,type,n,path" > data/graph/$TYPE.csv
# for n in `seq -w 100 100 2000`; do for i in `seq -w 0 19`; do echo "node_n=$n\_$i.json,$TYPE,$n,$TYPE/$n/node_n=$n\_$i.json" >> data/graph/$TYPE.csv; done; done

# for n in `seq -w 100 100 2000`; do python scripts/draw_unicon.py --dest data/drawing/unicon/$TYPE/$n data/graph/$TYPE/$n/*.json; done
for n in `seq -w 100 100 2000`; do python scripts/draw_sgd.py --dest data/drawing/sgd/$TYPE/$n data/graph/$TYPE/$n/*.json; done

python scripts/calc_stress.py data/graph/$TYPE.csv result/stress/$TYPE-100-2000.csv
python scripts/create_boxplot.py result/stress/$TYPE-100-2000.csv result/stress/$TYPE-100-2000.png --title "UNICON stress vs FullSGD stress"

python scripts/calc_violation.py data/graph/$TYPE.csv result/violation/$TYPE-100-2000.csv
python scripts/create_boxplot.py result/violation/$TYPE-100-2000.csv result/violation/$TYPE-100-2000.png --title "UNICON violation vs FullSGD violation"
