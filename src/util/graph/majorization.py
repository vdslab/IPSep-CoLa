import numpy as np
from networkx import Graph, floyd_warshall_numpy


def stress(X, dist: list[list], weights):
    stress_sum = 0
    for i in range(len(X)):
        for j in range(len(X)):
            mag = np.linalg.norm(X[i] - X[j])
            stress_sum += weights[i][j] * ((mag - dist[i][j]) ** 2)
    return stress_sum


def distance_matrix(graph: Graph, length: int = 1) -> np.ndarray:
    dist = floyd_warshall_numpy(graph)
    dist *= length
    return dist


if __name__ == "__main__":
    from graph import get_graph_and_constraints

    graph, _ = get_graph_and_constraints("src/data/json/download/no_cycle_tree.json")
    matrix = distance_matrix(graph, 20)
    matrix = matrix.tolist()
    import json

    with open("src/data/no_cycle_tree_dist.json", "w") as f:
        data = json.dump(matrix, f, indent=2)
    print(matrix)
