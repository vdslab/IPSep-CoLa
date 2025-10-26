import argparse
import csv
import itertools
import json
import math

import networkx as nx


def main():
    parser = argparse.ArgumentParser(
        description="Calculate stress values for each node pair in a graph drawing"
    )
    parser.add_argument("--graph", required=True, help="Path to graph JSON file")
    parser.add_argument("--drawing", required=True, help="Path to drawing JSON file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    # Load graph
    with open(args.graph) as f:
        graph = nx.node_link_graph(json.load(f))

    # Load drawing
    with open(args.drawing) as f:
        drawing = json.load(f)

    # Get distance matrix
    distance_matrix = graph.graph["distance"]
    nodes = list(graph.nodes)
    n = len(nodes)

    # Calculate stress values for each node pair
    import os

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["node_i", "node_j", "graph_distance", "drawing_distance", "stress_value"]
        )

        for i, j in itertools.combinations(range(n), 2):
            node_i = nodes[i]
            node_j = nodes[j]

            # Graph distance
            d1 = distance_matrix[i][j]

            # Drawing distance (Euclidean)
            pos_i = drawing[node_i]
            pos_j = drawing[node_j]
            d2 = math.hypot(pos_i[0] - pos_j[0], pos_i[1] - pos_j[1])

            # Stress value
            stress = ((d2 - d1) / d1) ** 2

            writer.writerow([node_i, node_j, d1, d2, stress])

    print(f"Stress values saved to {args.output}")
    print(f"Total node pairs: {n * (n - 1) // 2}")


if __name__ == "__main__":
    main()
