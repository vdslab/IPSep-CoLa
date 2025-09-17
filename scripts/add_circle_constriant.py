import argparse
import json
import os

import egraph as eg
import networkx as nx

from sgd.full_ego import sgd
from util.graph import nxgraph_to_egDiGraph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    parser.add_argument("out")
    args = parser.parse_args()

    filepath = args.filepath
    graph: nx.Graph = nx.node_link_graph(json.load(open(filepath)), link="links")
    egos = graph.graph["egos"]

    eggraph, indices = nxgraph_to_egDiGraph(graph, egos)
    vi = {v: k for k, v in indices.items()}

    eg.remove_cycle(eggraph)
    longest = eg.LongestPath()
    nodeidx_layer = longest.assign_layers(eggraph)
    max_layer = max(nodeidx_layer.values())
    layer_nodeidx = dict()
    for k, v in nodeidx_layer.items():
        layer_nodeidx.setdefault(v, []).append(k)

    circle_constraint = []
    for i in range(max_layer + 1):
        circle_constraint.append(
            {
                "type": "circle",
                "nodes": [vi[j] for j in layer_nodeidx[i]],
                "r": i + (1 if len(egos) != 1 else 0),
                "center": None if len(egos) != 1 else egos[0],
            }
        )
    graph.graph["constraints"] = circle_constraint
    json.dump(
        nx.node_link_data(graph),
        open(args.out, "w", encoding="utf-8"),
        indent=4,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    # main()

    import cProfile

    cProfile.run("main()", filename="main.prof")
