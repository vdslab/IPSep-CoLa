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

    graph: nx.Graph = nx.les_miserables_graph()

    degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes]
    deg_max = max([m[1] for m in degree])
    deg_index = [m[1] for m in degree].index(deg_max)
    deg_max_node = list(graph.nodes)[deg_index]
    rad = graph.number_of_nodes()
    graph = nx.ego_graph(graph, deg_max_node, radius=rad)

    for u in graph.nodes:
        graph.nodes[u]["shape"] = {
            "width": args.node_width,
            "height": args.node_height,
        }

    distance = nx.floyd_warshall_numpy(graph, weight=None) * args.edge_length
    graph.graph["distance"] = distance.tolist()
    graph.graph["constraints"] = []

    data = nx.node_link_data(graph)
    json.dump(data, open(args.output, "w"))


if __name__ == "__main__":
    main()
