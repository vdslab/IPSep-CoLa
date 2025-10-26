#!/bin/bash
cd "$(dirname "$0")/.." || exit

# 1. グラフ生成
echo "Generating NetworkX small graphs..."
python -m src/script/generator/networkx_small_graph_.py \
	--dest data/networkx_small \
	--edge-length 100

# 2. ユークリッド空間とトーラス空間で並列描画
echo "Drawing graphs in Euclidean and Torus spaces (parallel)..."
parallel -j 2 ::: \
	"python scripts/draw.py --space euclidean --dest dest/networkx_small/euclidean --iterations 30 data/networkx_small/*.json" \
	"python scripts/draw.py --space torus --dest dest/networkx_small/torus --iterations 30 data/networkx_small/*.json --overlap-removal"

# 3. 画像保存（全グラフを並列実行）
echo "Plotting Euclidean drawings (parallel)..."
find data/networkx_small -name "*.json" -type f | parallel -j 3 \
	"basename=\$(basename {} .json); python scripts/plot.py {} dest/networkx_small/euclidean/\${basename}.json dest/networkx_small/euclidean/\${basename}.png"

echo "Plotting Torus drawings (parallel)..."
find data/networkx_small -name "*.json" -type f | parallel -j 3 \
	"basename=\$(basename {} .json); python scripts/plot_torus.py {} dest/networkx_small/torus/\${basename}.json dest/networkx_small/torus/\${basename}_004.png"

echo "Done!"
