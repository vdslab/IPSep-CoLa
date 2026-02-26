#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

for n in $(seq -w 100 100 2000); do
	uv run --project "$REPO_ROOT/cli" draw --space euclidean --overlap-removal \
		--dest "data/drawing/sgd/overlap/$n" \
		data/graph/overlap/"$n"/*.json
done
for n in $(seq -w 100 100 2000); do
	mkdir -p data/drawing/webcola/overlap/$n
done
for n in $(seq -w 100 100 2000); do for i in $(seq -w 0 19); do node js/src/draw_webcola.js --graphFile data/graph/overlap/$n/node_n\=${n}_$i.json --output data/drawing/webcola/overlap/$n/node_n\=${n}_$i.json --overlapRemoval; done; done
uv run --project "$REPO_ROOT" python scripts/calc_stress.py data/graph/overlap.csv result/stress/overlap-100-2000.csv
uv run --project "$REPO_ROOT" python scripts/create_boxplot.py result/stress/overlap-100-2000.csv result/stress/overlap-100-2000.png --title "Webcola stress vs FullSGD stress"
