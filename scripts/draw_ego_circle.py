import argparse
import json
import os

import egraph as eg
import networkx as nx

from sgd.full_ego import sgd
from util.graph import nxgraph_to_egDiGraph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=".")
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--overlap-removal", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--cluster-overlap-removal", action=argparse.BooleanOptionalAction
    )

    parser.add_argument("-c", "--center_nodes_count", type=int, default=1)
    parser.add_argument("input", nargs="+")
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    for filepath in args.input:
        basename = os.path.basename(filepath)
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
        # print({vi[k]: v for k, v in nodeidx_layer.items()})

        if graph.graph.get("constraints") is None:
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
                open(filepath, "w", encoding="utf-8"),
                indent=4,
                ensure_ascii=False,
            )

        if graph.graph.get("distance") is None:
            dist = dict(nx.all_pairs_shortest_path_length(graph))
            n = graph.number_of_nodes()
            dist_matrix = [[0] * n for _ in range(n)]
            for i, v in enumerate(list(graph.nodes)):
                for j, u in enumerate(list(graph.nodes)):
                    dist_matrix[i][j] = dist[v][u]
            graph.graph["distance"] = dist_matrix
            json.dump(
                nx.node_link_data(graph),
                open(filepath, "w", encoding="utf-8"),
                indent=4,
                ensure_ascii=False,
            )

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


if __name__ == "__main__":
    # main()

    import cProfile

    cProfile.run("main()", filename="main.prof")
