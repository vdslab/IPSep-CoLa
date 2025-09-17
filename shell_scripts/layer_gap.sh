#!/bin/bash
cd "$(dirname "$0")/.." || exit

bash run_experiment.sh "layer_gap" 100 2000 100 "constraint"
