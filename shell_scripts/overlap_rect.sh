#!/bin/bash
cd "$(dirname "$0")/.." || exit

bash run_experiment.sh "overlap_rect" 1000 1000 100 "overlap"
