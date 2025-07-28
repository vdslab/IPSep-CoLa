import argparse
import json
import os

import networkx as nx

from sgd.full_torus import sgd
from sgd.torus_util import draw_torus


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=".")
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--overlap-removal", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--cluster-overlap-removal", action=argparse.BooleanOptionalAction
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
        pos = sgd(
            graph,
            iterations=args.iterations,
            overlap_removal=args.overlap_removal,
            clusters=clusters,
        )
        draw_torus(graph, pos)
        json.dump(pos, open(os.path.join(args.dest, basename), "w"), ensure_ascii=False)


if __name__ == "__main__":
    # main()

    import cProfile

    cProfile.run("main()", filename="main.prof")
