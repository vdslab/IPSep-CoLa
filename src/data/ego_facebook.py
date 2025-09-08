import argparse
import json

import networkx as nx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--edge-length", type=int, default=1)
    parser.add_argument("--node-width", type=int, default=100)
    parser.add_argument("--node-height", type=int, default=20)
    args = parser.parse_args()

    graph: nx.Graph = nx.read_edgelist(
        "src/data/facebook_combined.txt.gz", create_using=nx.Graph(), nodetype=str
    )

    # distance = nx.floyd_warshall_numpy(graph, weight=None) * args.edge_length
    # graph.graph["distance"] = distance.tolist()
    graph.graph["constraints"] = []

    data = nx.node_link_data(graph)
    json.dump(data, open(args.output, "w"))


if __name__ == "__main__":
    main()
