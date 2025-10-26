import argparse
import json
import os

import networkx as nx

from sgd.torus_util import draw_torus


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

    draw_torus(graph, pos, output=args.output, node_size=args.node_size, show_violation=args.show_violation)


if __name__ == "__main__":
    main()
