#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

TYPE="$1"
METHOD="$2"
NUMBER="$3"
IDX="$4"

echo "$TYPE, $METHOD, $NUMBER, $IDX, extra_args=${*:5}"

uv run --project "$REPO_ROOT/cli" plot \
	data/graph/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
	data/drawing/"$METHOD"/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".json \
	result/plot/"$METHOD"/"$TYPE"/"$NUMBER"/node_n="$NUMBER"_"$IDX".png \
	"${@:5}"
