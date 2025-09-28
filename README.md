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
  python scripts/draw.py --dest data/drawing/sgd/random_tree/$n data/graph/random_tree/$n/*
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
  python scripts/draw.py --dest data/drawing/sgd/overlap/$n --overlap-removal data/graph/overlap/$n/*
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
parallel --bar 'python scripts/draw.py --dest=data/drawing/sgd/cluster/{1} --overlap-removal --cluster-overlap-removal data/graph/cluster/{1}/node_n={1}_{2}.json' ::: $(seq -f '%04.0f' 100 100 2000) ::: $(seq -f '%02.0f' 0 19)
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

## vs UNICON

- 1138busの制約を作成
  - 中心から階層を計算、その後辺のノードペアに対して、層の差を距離とした

```bash
python src/data/generate_constraint_by_type.py
```

- stressとviolationの計測
  - `<save directory>`内に中間ファイルとして`compare_seed{i}.json`を生成。

- 形式

```json
{
    "seed": i,
    "iteration": args.iterations,
    "unicon": {"stress": su, "violation": vu, "drawing": posu},
    "constrained_sgd": {"stress": scs, "violation": vcs, "drawing": poscs},
},
```

- 実行方法

```bash
python scripts/drawing_and_stress_violation.py <graph file> <save directory> [option]
```

- 箱ひげ図の生成

```bash
python scripts/compare_stress_violation.py <compared directory> [option]
```


# dataset

- road_central
- 1138 bus

## ego centric graphの作成方法

- グラフから一部を取り出す。距離行列も計算している

```bash
python scripts/convert_large_mtx_to_ego.py <mtx graph file path> <networkx graph file output path> <hub number(中心の数)> <radius(中心からの半径)>
```

- 必要であれば同心円状の制約を付加する。引数のファイルに追加される

```bash
python scripts/add_circle_constraint.py <networkx graph file path>
```

# non Euclidean drawing

## torus

```bash
python scripts/draw.py --space torus [option] <graph file path>
python scripts/plot_torus.py <graph file> <drawing file> <output file>
```

## hyper

```bash
python scripts/draw.py --space hyperbolic [option] <graph file path>
python scripts/plot.py <graph file> <drawing file> <output file>
```

# project

## circle constriant

- 制約の形式

```python
{
    "type": "circle",
    "nodes": list,
    "r": int,
    "center": int | None,
}
```

- 射影のコード
  - `src/sgd/projection/circle_constraints.py`

```
circle_constraints = [
    [
        [indices[v] for v in c["nodes"]],
        c["r"],
        indices[c["center"]] if c.get("center") is not None else None,
    ]
    for c in nx_graph.graph["constraints"]
    if c.get("type", "") == "circle"
]
```
