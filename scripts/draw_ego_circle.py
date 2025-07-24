import argparse
import json
import os

import egraph as eg
import networkx as nx

from sgd.full import sgd
from util.graph import nxgraph_to_eggraph


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
        # TODO: ソーシャルグラフでの円形制約
        # TODO: e-graphでのoverlap removal(OverwrapRemoval)
        graph = nx.node_link_graph(json.load(open(filepath)), link="links")
        # degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes]
        # deg_max = max([m[1] for m in degree])
        # deg_index = [m[1] for m in degree].index(deg_max)
        # deg_max_node = list(graph.nodes)[deg_index]
        # rad = 5
        # graph = nx.ego_graph(graph, deg_max_node, radius=rad)
        # eggraph = eg.GraphAdapter().new_digraph(graph)
        eggraph, indices = nxgraph_to_eggraph(graph)
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
                    "r": (i + 1) * 0.5,
                    "center": None,
                }
            )
        graph.graph["constraint"] = circle_constraint
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
    # main()

    import cProfile

    cProfile.run("main()", filename="main.prof")
