#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

# 1. グラフ生成
echo "Generating NetworkX small graphs..."
uv run --project "$REPO_ROOT" python src/script/generator/networkx_small_graph_.py \
	--dest data/networkx_small \
	--edge-length 100

# 2. ユークリッド空間とトーラス空間で並列描画
echo "Drawing graphs in Euclidean and Torus spaces (parallel)..."
parallel -j 2 ::: \
		"uv run --project \"$REPO_ROOT/cli\" draw --space euclidean --dest dest/networkx_small/euclidean --iterations 30 data/networkx_small/*.json" \
		"uv run --project \"$REPO_ROOT/cli\" draw --space torus --dest dest/networkx_small/torus --iterations 30 data/networkx_small/*.json --overlap-removal"

# 3. 画像保存（全グラフを並列実行）
echo "Plotting Euclidean drawings (parallel)..."
find data/networkx_small -name "*.json" -type f | parallel -j 3 \
		"basename=\$(basename {} .json); uv run --project \"$REPO_ROOT/cli\" plot {} dest/networkx_small/euclidean/\${basename}.json dest/networkx_small/euclidean/\${basename}.png"

echo "Plotting Torus drawings (parallel)..."
find data/networkx_small -name "*.json" -type f | parallel -j 3 \
	"basename=\$(basename {} .json); uv run --project \"$REPO_ROOT\" python scripts/plot_torus.py {} dest/networkx_small/torus/\${basename}.json dest/networkx_small/torus/\${basename}_004.png"

echo "Done!"
