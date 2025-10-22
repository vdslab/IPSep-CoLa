import argparse
import importlib
import json
import os
import random

import networkx as nx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--space",
        default="euclidean",
        choices=["euclidean", "hyperbolic", "spherical", "torus", "after_project"],
        help="The space to draw the graph in.",
    )
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
    parser.add_argument("input", nargs="+")
    args = parser.parse_args()

    # Dynamically import the sgd module based on the selected space
    if args.space == "euclidean":
        sgd_module = importlib.import_module("sgd.full")
    elif args.space == "hyperbolic":
        sgd_module = importlib.import_module("sgd.full_hyper")
    else:
        sgd_module = importlib.import_module(f"sgd.full_{args.space}")
    sgd = sgd_module.sgd

    os.makedirs(args.dest, exist_ok=True)
    for filepath in args.input:
        basename = os.path.basename(filepath)
        with open(filepath) as fp:
            graph = nx.node_link_graph(json.load(fp), link="links")
        clusters = None
        if args.cluster_overlap_removal:
            clusters = [graph.nodes[u]["group"] for u in graph.nodes]

        # Generate random seed if not specified
        seed = args.seed if args.seed is not None else random.randint(0, 2**32 - 1)

        # Prepare arguments for the sgd function
        sgd_args = {
            "nx_graph": graph,
            "iterations": args.iterations,
            "overlap_removal": args.overlap_removal,
            "clusters": clusters,
            "seed": seed,
        }

        pos = sgd(**sgd_args)
        name_without_ext = os.path.splitext(basename)[0]
        output_filename = f"{name_without_ext}{args.output_suffix}.json"
        output_path = os.path.join(args.dest, output_filename)
        with open(output_path, "w") as fp:
            json.dump(pos, fp, ensure_ascii=False)


if __name__ == "__main__":
    # main()

    import cProfile

    cProfile.run("main()", filename="main.prof")
