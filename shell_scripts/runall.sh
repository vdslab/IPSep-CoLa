#!/bin/bash
cd "$(dirname "$0")/.." || exit

# for n in `seq -f '%04.0f' 100 100 2000`
# do
#   python scripts/draw_sgd.py --dest data/drawing/sgd/overlap/$n --overlap-removal data/graph/overlap/$n/*
# done

for n in $(seq -f '%04.0f' 100 100 2000); do
	python scripts/draw_webcola.py --dest data/drawing/webcola/overlap/$n --overlap-removal data/graph/overlap/$n/*
done

# for method in sgd webcola
# do
#   for type in random_tree overlap
#   do
#     for n in `seq -f '%04.0f' 100 100 2000`
#     do
#       mkdir -p result/plot/${method}/${type}/${n}
#       for i in `seq -f '%02.0f' 0 19`
#       do
#         node js/src/render.js --graphFile=data/graph/${type}/${n}/node_n\=${n}_${i}.json --drawingFile=data/drawing/${method}/${type}/${n}/node_n\=${n}_${i}.json --output=result/plot/${method}/${type}/${n}/node_n=${n}_${i}.png
#       done
#     done
#   done
# done

for type in overlap; do
	python scripts/calc_stress.py data/graph/$type.csv result/stress/$type-0100-2000.csv
	python scripts/create_boxplot.py result/stress/$type-0100-2000.csv result/stress/$type-0100-2000.png
done
