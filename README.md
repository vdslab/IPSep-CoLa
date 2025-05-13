# ipsep-cola

## 環境

use rye

- https://rye-up.com/guide/installation/

```bash
rye sync
```

# Workflow

## Generate graphs

```
python src/data/generate_overlap_graphs.py
```

## Generate sgd tree drawing

```
for n in `seq -f '%04.0f' 100 100 2000`
do
  python scripts/draw_sgd.py --dest data/drawing/sgd/random_tree/$n data/graph/random_tree/$n/*
done
```

## Generate webcola tree drawing

```
for n in `seq -f '%04.0f' 100 100 2000`
do
  python scripts/draw_webcola.py --dest data/drawing/webcola/random_tree/$n data/graph/random_tree/$n/*
done
```

## Generate sgd no-overlap drawing

```
for n in `seq -f '%04.0f' 100 100 2000`
do
  python scripts/draw_sgd.py --dest data/drawing/sgd/overlap/$n --overlap-removal data/graph/overlap/$n/*
done
```

## Generate webcola no-overlap drawing

```
for n in `seq -f '%04.0f' 100 100 2000`
do
  python scripts/draw_webcola.py --dest data/drawing/webcola/overlap/$n --overlap-removal data/graph/overlap/$n/*
done
```

## Generate sgd cluster-no-overlap drawing

```
parallel --bar 'python scripts/draw_sgd.py --dest=data/drawing/sgd/cluster/{1} --overlap-removal --cluster-overlap-removal data/graph/cluster/{1}/node_n={1}_{2}.json' ::: $(seq -f '%04.0f' 100 100 2000) ::: $(seq -f '%02.0f' 0 19)
```

## Generate webcola cluster-no-overlap drawing

```
parallel --bar 'python scripts/draw_webcola.py --dest=data/drawing/webcola/cluster/{1} --overlap-removal --cluster-overlap-removal data/graph/cluster/{1}/node_n={1}_{2}.json' ::: $(seq -f '%04.0f' 100 100 2000) ::: $(seq -f '%02.0f' 0 19)
```

## Plot to PNG

```
parallel --bar 'mkdir -p result/plot/{1}/{2}/{3}' ::: sgd webcola ::: random_tree overlap cluster ::: $(seq -f '%04.0f' 100 100 2000)
parallel --bar 'node js/src/render.js --graphFile=data/graph/{2}/{3}/node_n\={3}_{4}.json --drawingFile=data/drawing/{1}/{2}/{3}/node_n\={3}_{4}.json --output=result/plot/{1}/{2}/{3}/node_n={3}_{4}.png' ::: sgd webcola ::: random_tree overlap cluster ::: $(seq -f '%04.0f' 100 100 2000) ::: $(seq -f '%02.0f' 0 19)
```

## Stress comparison

```
for type in cluster
do
  python scripts/calc_stress.py data/graph/$type.csv result/stress/$type-0100-2000.csv
  python scripts/create_boxplot.py result/stress/$type-0100-2000.csv result/stress/$type-0100-2000.png
done
```

## Violation comparison

```
for type in random_tree
do
  python scripts/calc_violation.py data/graph/$type.csv result/stress/$type-0100-2000.csv
  python scripts/create_boxplot.py result/stress/$type-0100-2000.csv result/stress/$type-0100-2000.png
done
```
