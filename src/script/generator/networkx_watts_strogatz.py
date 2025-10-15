import argparse
import json

import networkx as nx


class Arg(argparse.Namespace):
    output: str
    node_number: int
    neighbor_number: int
    rewiring_prob: float


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--node-number", type=int, default=100)
    parser.add_argument("--neighbor-number", type=int, default=5)
    parser.add_argument("--rewiring-prob", type=float, default=0.5)
    args = parser.parse_args(namespace=Arg)

    graph = nx.connected_watts_strogatz_graph(
        args.node_number, args.neighbor_number, args.rewiring_prob
    )
    assert nx.is_connected(graph)
    graph = nx.relabel_nodes(graph, lambda x: str(x))

    distance = nx.floyd_warshall_numpy(graph, weight=None)
    graph.graph["distance"] = distance.tolist()
    graph.graph["constraints"] = []
    data = nx.node_link_data(graph)
    json.dump(data, open(args.output, "w"))


if __name__ == "__main__":
    main()
