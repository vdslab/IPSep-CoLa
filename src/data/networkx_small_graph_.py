import argparse
import json

import networkx as nx


class Arg(argparse.Namespace):
    output: str
    number: int = 10
    edge_length: int = 1
    node_width: int = 20
    node_height: int = 20


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--number", type=int, default=10)
    parser.add_argument("--edge-length", type=int, default=20)
    parser.add_argument("--node-width", type=int, default=20)
    parser.add_argument("--node-height", type=int, default=20)
    args: Arg = parser.parse_args()

    _graph: nx.Graph = nx.petersen_graph()
    graph = nx.Graph()
    graph.add_nodes_from([str(v) for v in _graph.nodes])
    graph.add_edges_from([(str(u), str(v)) for u, v in _graph.edges])

    # for u in graph.nodes:
    #     graph.nodes[u]["shape"] = {
    #         "width": args.node_width,
    #         "height": args.node_height,
    #         "r": args.node_width,
    #     }

    distance = nx.floyd_warshall_numpy(graph, weight=None) * args.edge_length
    graph.graph["distance"] = distance.tolist()
    graph.graph["constraints"] = []

    data = nx.node_link_data(graph)
    json.dump(data, open(args.output, "w"))


if __name__ == "__main__":
    main()
