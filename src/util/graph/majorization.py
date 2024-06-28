import numpy as np
from networkx import Graph, floyd_warshall_numpy


def stress(X, dist: list[list], weights):
    stress_sum = 0
    for i in range(len(X)):
        for j in range(len(X)):
            mag = np.linalg.norm(X[i] - X[j])
            stress_sum += weights[i][j] * ((mag - dist[i][j]) ** 2)
    return stress_sum


def distance_matrix(graph: Graph, length: int = 1):
    dist = floyd_warshall_numpy(graph)
    dist *= length
    return dist
