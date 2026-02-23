import argparse
import json
import os
import random

import networkx as nx

from sgd.uniocon import sgd
from util.timer import profiler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=".")
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--overlap-removal", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--cluster-overlap-removal", action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "--output-suffix", default="", help="Suffix to add to output filenames"
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed (None for random)"
    )
    parser.add_argument(
        "--timing-level",
        type=int,
        default=0,
        choices=[0, 1, 2, 3],
        help="Timing level (0=off, 1=total, 2=iterations, 3=detailed)",
    )
    parser.add_argument(
        "--timing-output",
        default=None,
        help="Output file path for timing results (without extension)",
    )
    parser.add_argument(
        "--timing-quiet",
        action="store_true",
        help="Suppress timing output to console (still saves to file if --timing-output is specified)",
    )
    parser.add_argument("input", nargs="+")
    args = parser.parse_args()

    # Apply profiler if timing is enabled
    sgd_func = sgd
    if args.timing_level > 0:
        sgd_func = profiler(sgd, timing_level=args.timing_level, timing_output_file=args.timing_output, quiet=args.timing_quiet)

    os.makedirs(args.dest, exist_ok=True)
    for filepath in args.input:
        basename = os.path.basename(filepath)
        graph = nx.node_link_graph(json.load(open(filepath)), edges="links")
        clusters = None
        if args.cluster_overlap_removal:
            clusters = [graph.nodes[u]["group"] for u in graph.nodes]

        # Generate random seed if not specified
        seed = args.seed if args.seed is not None else random.randint(0, 2**32 - 1)

        pos = sgd_func(
            graph,
            iterations=args.iterations,
            overlap_removal=args.overlap_removal,
            clusters=clusters,
            seed=seed,
        )
        name_without_ext = os.path.splitext(basename)[0]
        output_filename = f"{name_without_ext}{args.output_suffix}.json"
        json.dump(
            pos, open(os.path.join(args.dest, output_filename), "w"), ensure_ascii=False
        )


if __name__ == "__main__":
    # main()

    import cProfile

    # cProfile.run("main()", filename="main.prof")
    main()
