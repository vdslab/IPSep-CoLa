import argparse
import json

import networkx as nx


class Arg(argparse.Namespace):
    output: str
    node_number: int
    neighbor_number: int
    rewiring_prob: float
    edge_length: float


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--node-number", type=int, default=100)
    parser.add_argument("--neighbor-number", type=int, default=5)
    parser.add_argument("--rewiring-prob", type=float, default=0.5)
    parser.add_argument("--edge-length", type=float, default=100.0)
    args = parser.parse_args(namespace=Arg)

    for i in range(10):
        graph = nx.newman_watts_strogatz_graph(
            args.node_number, args.neighbor_number, args.rewiring_prob
        )
        if nx.is_connected(graph):
            break
    else:
        raise ValueError("Could not generate a connected graph after 10 attempts.")
    graph = nx.relabel_nodes(graph, lambda x: str(x))

    distance = nx.floyd_warshall_numpy(graph, weight=None)
    distance *= args.edge_length
    graph.graph["distance"] = distance.tolist()
    graph.graph["constraints"] = []
    data = nx.node_link_data(graph)
    import os

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    json.dump(data, open(args.output, "w"))


if __name__ == "__main__":
    main()
