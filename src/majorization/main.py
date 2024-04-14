import datetime
import json
import os
from math import pow

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from networkx import floyd_warshall_numpy
from scipy.sparse.linalg import cg


def weights_of_normalization_constant(alpha, dist):
    """
    Returns: あるiからjのnormalization_constant
    dist: 二頂点間の最短経路の長さ，到達不可ならfloat('inf')
    """
    n = len(dist)
    weights = [[0.0 for _ in range(n)] for _ in range(n)]
    for i, di in enumerate(dist):
        for j, dij in enumerate(di):
            if dij == float("inf"):
                continue
            weights[i][j] = 0 if dij < 0.000_01 else pow(dij, -alpha)

    return np.array(weights)


# 全体のstress
def stress(X, dist: list[list], weights):
    """
    Returns: 全体のストレス
    """
    # dist: graph-theoretical distance
    #   d_{ij}: the length of the shortest path connecting i and j
    #   Cohen -> the linear-network distance
    #     because: better convey any clustered structure in the graph.
    # weight: normalization constant
    #   w_{ij} = d_{ij}^{ -1 * alpha }
    #   Kamada ans Kawai -> alpha = 2
    #   Cohen -> alpha = 0 and 1

    stress_sum = 0
    for i in range(len(X)):
        for j in range(i + 1, len(X)):
            mag = np.linalg.norm(X[i] - X[j])
            stress_sum += weights[i][j] * (mag - dist[i][j]) * (mag - dist[i][j])
    return stress_sum


def weight_laplacian(weights):
    L = [[-w for w in ws] for ws in weights]
    w_col_sums = [sum(col) for col in zip(*weights)]
    for i in range(len(L)):
        L[i][i] = w_col_sums[i] - weights[i][i]
    return np.array(L)


# A = np.array([[1, 2, 3], [2, 5, 6], [3, 6, 10]])
# LA = weight_laplacian(A)
# assert np.all(np.linalg.eigvals(LA[1:, 1:]) > 0), "err"


def z_laplacian(weights, dist: list[list], Z):
    """
    Z: 頂点数n，d次元として，n*d．座標の配列
    """
    n = len(Z)
    Lz = [[0 for _ in range(n)] for _ in range(n)]
    float_eps = 0.000_1
    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            mag = np.linalg.norm(Z[i] - Z[j])
            invmag = 0 if mag <= float_eps else 1 / mag
            Lzij = -1 * weights[i][j] * dist[i][j] * invmag
            Lz[i][j] = Lzij
            Lz[j][i] = Lzij

    Lz_col_sums = [sum(col) for col in zip(*Lz)]
    for i in range(n):
        Lz[i][i] = -Lz_col_sums[i]

    return np.array(Lz)


def stress_majorization(nodes, links, *, dim=2, initZ=None):
    n = len(nodes)

    sigmas = [[0] * n] * n
    for i, j in links:
        sigmas[i - 1][j - 1] = 1

    G = nx.Graph()
    for node in nodes:
        G.add_node(node)
    for link in links:
        G.add_edge(*link)
    dist = floyd_warshall_numpy(G)

    # 座標の初期値はランダム
    Z = np.random.rand(n, dim)
    if initZ is not None:
        Z = initZ
    dim = len(Z[0])
    Z[0] = [0 for _ in range(dim)]
    #
    alpha = 2
    weights = weights_of_normalization_constant(alpha, dist)

    Lw = weight_laplacian(weights)

    # 終了する閾値
    eps = 0.0_01
    now_stress = stress(Z, dist, weights)
    new_stress = 0.5 * now_stress

    def delta_stress(now, new):
        return (now - new) / now

    while True:
        Lz = z_laplacian(weights, dist, Z)
        for a in range(dim):
            # Ax = b
            Z[1:, a] = cg(Lw[1:, 1:], (Lz @ Z[:, a])[1:])[0]

        new_stress = stress(Z, dist, weights)
        print(f"{now_stress=} -> {new_stress=}")
        print(delta_stress(now_stress, new_stress))
        if delta_stress(now_stress, new_stress) < eps:
            break
        now_stress = new_stress

    return Z


if __name__ == "__main__":
    with open("./src/data/no_acycle_tree.json") as f:
        data = json.load(f)

    nodes = [i + 1 for i in range(len(data["nodes"]))]
    n = len(nodes)

    links = [[d["source"] + 1, d["target"] + 1] for d in data["links"]]

    np.random.seed(0)
    Z = stress_majorization(nodes, links)

    def view():
        G = nx.DiGraph()
        for node in nodes:
            G.add_node(node)
        for link in links:
            G.add_edge(*link)
        position = {i + 1: Z[i] for i in range(n)}
        today = datetime.date.today()
        now = datetime.datetime.now().time()
        os.makedirs(f"result/{today}", exist_ok=True)

        plt.figure(figsize=(10, 10))
        plt.title("Stress Majorization (seed 0)")
        nx.draw(G, pos=position, node_size=300, labels={i + 1: i for i in range(n)})
        plt.savefig(f"result/{today}/{now}.png")

    view()
