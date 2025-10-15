#!/bin/bash
cd "$(dirname "$0")/.." || exit

bash shell_scripts/run_experiment.sh "scale_free" 100 2000 100 "constraint"
