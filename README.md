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

## Plot to PNG

```
for method in sgd webcola
do
  for type in random_tree overlap
  do
    for n in `seq -f '%04.0f' 100 100 2000`
    do
      mkdir -p result/plot/${method}/${type}/${n}
      for i in `seq -f '%02.0f' 0 19`
      do
        node js/src/render.js --graphFile=data/graph/${type}/${n}/node_n\=${n}_${i}.json --drawingFile=data/drawing/${method}/${type}/${n}/node_n\=${n}_${i}.json --output=result/plot/${method}/${type}/${n}/node_n=${n}_${i}.png
      done
    done
  done
done
```

## Stress comparison

```
for type in random_tree overlap
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
