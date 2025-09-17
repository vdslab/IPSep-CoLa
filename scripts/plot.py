import argparse
import json
import os

import networkx as nx

from util.graph.plot import plot_graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file")
    parser.add_argument("drawing_file")
    parser.add_argument("output")
    parser.add_argument("--show-violation", action=argparse.BooleanOptionalAction)
    parser.add_argument("--node-size", type=int, default=30)

    args = parser.parse_args()

    graph = nx.node_link_graph(json.load(open(args.graph_file)))
    pos = json.load(open(args.drawing_file))
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    plot_graph(
        graph,
        pos,
        args.output,
        show_violation=args.show_violation,
        node_size=args.node_size,
    )


if __name__ == "__main__":
    main()
