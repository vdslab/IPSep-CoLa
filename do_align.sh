{
    node js/src/cola/calc_position_random_tree.js &
    wait
    echo "calc position random tree done"
    python3 src/data/calc_stress.py
} &

wait
echo "Done"