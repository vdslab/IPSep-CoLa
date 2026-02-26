#!/usr/bin/env bash
set -euo pipefail

# CLI usage examples for IPSep-CoLa graph drawing.
#
# How to run (from anywhere in this repo):
#   bash cli/examples/graph_drawing.sh
#
# Prerequisites:
#   - uv is installed
#   - dependencies are installed once via: uv sync (optionally: uv sync --extra dev)
#
# Outputs:
#   result/cli-example/

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
EXAMPLE_DIR="$REPO_ROOT/cli/examples"

GRAPH_FILE="$SCRIPT_DIR/tree.json"
OUT_ROOT="${1:-$EXAMPLE_DIR/result}"

DRAW_UNICON_OUT="$OUT_ROOT/drawing/unicon"
DRAW_WEBCOLA_OUT="$OUT_ROOT/drawing/webcola"
PLOT_OUT="$OUT_ROOT/plot"

echo $GRAPH_FILE $OUT_ROOT $DRAW_UNICON_OUT $DRAW_WEBCOLA_OUT $PLOT_OUT

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' not found. Install uv first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

mkdir -p "$DRAW_UNICON_OUT" "$DRAW_WEBCOLA_OUT" "$PLOT_OUT"

echo "[1/4] Show help (optional)"
uv run --project "$REPO_ROOT" draw-unicon --help >/dev/null
uv run --project "$REPO_ROOT" plot --help >/dev/null

echo "[2/4] Draw (UNICON)"
uv run --project "$REPO_ROOT" draw-unicon \
  --dest "$DRAW_UNICON_OUT" \
  --iterations 30 \
  --seed 0 \
  "$GRAPH_FILE"

echo "[3/4] Plot (UNICON -> PNG)"
uv run --project "$REPO_ROOT" plot \
  "$GRAPH_FILE" \
  "$DRAW_UNICON_OUT/tree.json" \
  "$PLOT_OUT/tree-unicon.png" \
  --show-violation \
  --node-size 40

echo "[4/4] Draw + plot (WebCoLa)"
# Note: draw-webcola calls Node.js internally (js/src/draw_webcola.js).
uv run --project "$REPO_ROOT" draw-webcola \
  --dest "$DRAW_WEBCOLA_OUT" \
  "$GRAPH_FILE"

uv run --project "$REPO_ROOT" plot \
  "$GRAPH_FILE" \
  "$DRAW_WEBCOLA_OUT/tree.json" \
  "$PLOT_OUT/tree-webcola.png" \
  --show-violation \
  --node-size 40

echo "done: $OUT_ROOT"
