#!/bin/bash

METHODS=("FullSGD(ours)" "WebCoLa")
CONSTRAINTS=("gap" "layered")

single_run() {
	local file="$1"
	local csv="$2"
	uv run scripts/convex_hull.py "$file" "$csv" --create
}

run_convex() {
	for node in $(seq -f "%04g" "100" "100" "2000"); do
		local filepath="$1"/"$node"
		export -f single_run
		find "$filepath" -name "*.json" -exec bash -c 'single_run "$0" "$1"' {} "$2" \;
	done
}

convex_hull() {
	for method in "${METHODS[@]}"; do
		for constraint in "${CONSTRAINTS[@]}"; do
			local filepath="data/drawing/SNS/${method}/watts_strogatz/neighbor_2/rewire_030/${constraint}"
			local csvfile="${method}_${constraint}_convexhull.csv"
			run_convex "$filepath" "$csvfile"
		done
	done
}

convex_hull
