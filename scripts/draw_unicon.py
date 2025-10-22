import argparse
import json
import os
import random

import networkx as nx

from sgd.uniocon import sgd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=".")
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--overlap-removal", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--cluster-overlap-removal", action=argparse.BooleanOptionalAction
    )
    parser.add_argument("--output-suffix", default="", help="Suffix to add to output filenames")
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed (None for random)"
    )
    parser.add_argument("input", nargs="+")
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    for filepath in args.input:
        basename = os.path.basename(filepath)
        graph = nx.node_link_graph(json.load(open(filepath)), link="links")
        clusters = None
        if args.cluster_overlap_removal:
            clusters = [graph.nodes[u]["group"] for u in graph.nodes]
        
        # Generate random seed if not specified
        seed = args.seed if args.seed is not None else random.randint(0, 2**32 - 1)
        
        pos = sgd(
            graph,
            iterations=args.iterations,
            overlap_removal=args.overlap_removal,
            clusters=clusters,
            seed=seed,
        )
        name_without_ext = os.path.splitext(basename)[0]
        output_filename = f"{name_without_ext}{args.output_suffix}.json"
        json.dump(pos, open(os.path.join(args.dest, output_filename), "w"), ensure_ascii=False)


if __name__ == "__main__":
    # main()

    import cProfile

    cProfile.run("main()", filename="main.prof")
