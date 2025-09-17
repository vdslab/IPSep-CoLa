import argparse
import json
import os
from typing import Protocol

import egraph as eg
import networkx as nx

from sgd.full import sgd
from util.graph import nxgraph_to_egDiGraph


class Arg(Protocol):
    dest: str
    iterations: int
    overlap_removal: bool
    input: list[str]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=".")
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--overlap-removal", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--cluster-overlap-removal", action=argparse.BooleanOptionalAction
    )

    parser.add_argument("-c", "--center_nodes_count", type=int, default=1)
    parser.add_argument("input")
    args: Arg = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    basename = os.path.basename(args.input)
    graph: nx.Graph = nx.node_link_graph(json.load(open(args.input)), link="links")
    degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes]
    degree.sort(key=lambda x: -x[1])
    egos = [v for v, _ in degree[: args.center_nodes_count]]
    # egos = ["0", "107", "348", "414", "686", "698", "1684", "1912", "3437", "3980"]
    eggraph, indices = nxgraph_to_egDiGraph(graph, egos)
    vi = {v: k for k, v in indices.items()}
    eg.remove_cycle(eggraph)
    longest = eg.LongestPath()
    nodeidx_layer = longest.assign_layers(eggraph)
    print({vi[k]: v for k, v in nodeidx_layer.items()})
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
                "center": None if len(egos) != 1 else degree[0][0],
            }
        )
    # layer_constraints = []
    # from collections import deque

    # que = deque([v for v, _ in degree[: args.center_nodes_count]])
    # visit = set([v for v, _ in degree[: args.center_nodes_count]])
    # layer_constraints = []
    # while que:
    #     v = que.popleft()
    #     for u in graph.neighbors(v):
    #         if u not in visit:
    #             visit.add(u)
    #             que.append(u)
    #             layer_constraints.append(
    #                 {"axis": "y", "left": v, "right": u, "gap": 2}
    #             )

    graph.graph["constraints"] = circle_constraint
    clusters = None
    if args.cluster_overlap_removal:
        clusters = [graph.nodes[u]["group"] for u in graph.nodes]
    pos = sgd(
        graph,
        iterations=args.iterations,
        overlap_removal=args.overlap_removal,
        clusters=clusters,
    )
    json.dump(pos, open(os.path.join(args.dest, basename), "w"), ensure_ascii=False)
    # json.dump(nx.node_link_data(graph), open(f"data/graph/ego{rad}_{basename}"))


if __name__ == "__main__":
    main()
