import numpy as np
from networkx import Graph, floyd_warshall_numpy


def stress(X, dist: list[list], weights):
    stress_sum = 0
    for j in range(len(X)):
        for i in range(j):
            mag = np.linalg.norm(X[i] - X[j])
            stress_sum += weights[i][j] * ((mag - dist[i][j]) ** 2)
    return stress_sum


def distance_matrix(graph: Graph, length: int = 1) -> np.ndarray:
    dist = floyd_warshall_numpy(graph)
    dist *= length
    return dist


if __name__ == "__main__":
    import glob
    import json
    import os

    from graph import get_graph_and_constraints

    files = [
        "./src/data/json/download/no_cycle_tree.json",
        "./src/data/json/download/qh882.json",
        "./src/data/json/download/dwt_1005.json",
        "./src/data/json/download/1138_bus.json",
        "./src/data/json/download/dwt_2680.json",
        "./src/data/json/download/USpowerGrid.json",
        "./src/data/json/download/3elt.json",
    ]
    # print(already)
    for file in files:
        try:
            graph, _ = get_graph_and_constraints(file)
            d = {}
            length = 20
            d["length"] = length
            matrix = distance_matrix(graph, length)
            matrix = matrix.tolist()
            d["matrix"] = matrix
            basename = os.path.basename(file)
            print(basename)
            with open(f"src/data/json/dist/{basename}", "w") as f:
                data = json.dump(d, f, indent=2)
        except Exception as e:
            print(e)
            print(file)
            continue
