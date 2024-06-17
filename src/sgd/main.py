import datetime
import glob
import math
import os
import time

import numpy as np
from ipsep_cola import NodeBlocks, project
from majorization.main import stress, weights_of_normalization_constant
from networkx import floyd_warshall_numpy
from util.constraint import Constraints, get_constraints_dict
from util.graph import get_graph_and_constraints, init_positions, plot_graph


def get_eta_steps(n, weight, iter, eps):
    wmin = np.amax(weight)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if weight[i][j] == 0:
                continue
            wmin = min(wmin, weight[i][j])
    eta_max = 1 / wmin
    eta_min = eps / np.amax(weight)
    steps = [
        eta_max * math.exp(1 / (iter - 1) * math.log(eta_min / eta_max) * t)
        for t in range(iter)
    ]
    return steps


def sgd_with_project(file_path, edge_length, gap, iter_count, eps):
    """
    # Returns
    Z: ndarray
        - The positions of the nodes.

    stresses: list[float]
        - The stress of the positions at each iteration.

    times: list[float]
        - The time taken to compute the positions at each iteration.
    """

    graph, constraints_data = get_graph_and_constraints(file_path)
    dist = floyd_warshall_numpy(graph)
    dist *= edge_length
    Z = init_positions(graph, 2, 0)
    weights = weights_of_normalization_constant(2, dist)
    C = get_constraints_dict(constraints_data, default_gap=gap)
    constraints = Constraints(C["y"], Z.shape[0])
    # constraints = Constraints([], Z.shape[0])
    steps = get_eta_steps(Z.shape[0], weights, iter_count, eps)

    ij = []
    for i in range(Z.shape[0]):
        for j in range(i + 1, Z.shape[0]):
            ij.append((i, j))

    stresses = []
    times = []
    start_time = time.time()

    def move(eta):
        for i, j in ij:
            norm = np.linalg.norm(Z[i] - Z[j], ord=2)

            r = (norm - dist[i][j]) * (Z[i] - Z[j]) / norm / 2 if norm > 1e-4 else 0

            if weights[i][j] == 0:
                myu = eta
            else:
                myu = weights[i][j] * eta
            myu = min(myu, 1)
            Z[i] -= myu * r
            Z[j] += myu * r

        blocks = NodeBlocks(Z[:, 1].flatten())
        y = project(constraints, blocks)
        Z[:, 1:2] = y.flatten()[:, None]

    for eta in steps:
        print(eta)
        np.random.shuffle(ij)
        move(eta)
        stresses.append(stress(Z, dist, weights))
        times.append(time.time() - start_time)

    return Z, stresses, times


if __name__ == "__main__":
    print(glob.glob("src/data/*.json"))

    gaps = np.arange(10, 51, 10)
    edge_lengths = np.arange(10.0, 51.0, 10.0)
    today = datetime.date.today()
    now = datetime.datetime.now()
    save_dir = f"result/SGD/{today}/{now}"
    os.makedirs(save_dir, exist_ok=True)

    Z, _, _ = sgd_with_project("./src/data/no_cycle_tree.json", 20, 20, 150, 0.01)
    graph = get_graph_and_constraints("./src/data/no_cycle_tree.json")[0]
    plot_graph(graph, Z, save_dir, "no_cycle_tree.png")
