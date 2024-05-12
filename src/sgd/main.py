import math

import numpy as np
import json
from ipsep_cola.constraint import Constraints
import datetime
import os
from ipsep_cola.block import NodeBlocks
from ipsep_cola.QPSC import project
import matplotlib.pyplot as plt
import networkx as nx

from networkx import floyd_warshall_numpy

from majorization.main import weights_of_normalization_constant


def sgd(Z, weight, dist):
    iter = 150
    eps = 0.1

    wmin = np.amax(weight)
    for i in range(n):
        for j in range(n):
            if i != j:
                wmin = min(wmin, weight[i][j])

    eta_max = 1 / wmin
    eta_min = eps / np.amax(weight)
    steps = [
        eta_max * math.exp(1 / (iter - 1) * math.log(eta_min / eta_max) * t)
        for t in range(iter)
    ]
    ij = []
    for i in range(Z.shape[0]):
        for j in range(i + 1, Z.shape[0]):
            ij.append((i, j))

    for eta in steps:
        np.random.shuffle(ij)
        for i, j in ij:
            norm = np.linalg.norm(Z[i] - Z[j], ord=2)
            if norm < 1e-4:
                print(norm, dist[i][j])
                exit()

            r = (norm - dist[i][j]) * (Z[i] - Z[j]) / norm / 2

            myu = weight[i][j] * eta
            myu = min(myu, 1)
            Z[i] -= myu * r
            Z[j] += myu * r

    return Z


def sgd_ipsepcola(Z, weight, dist):
    with open("./src/data/no_cycle_tree.json") as f:
        data = json.load(f)

    nodes = [i for i in range(len(data["nodes"]))]
    n = len(nodes)

    links = [[d["source"], d["target"]] for d in data["links"]]
    constraints = data["constraints"]

    C: dict[str, list] = dict()
    C["y"] = []
    C["x"] = []
    for c in constraints:
        left = c["left"]
        right = c["right"]
        axis = c["axis"]
        C[axis].append([left, right, 20])

    constraints = Constraints(C["y"], n)

    lam = 1
    iter = 150
    eps = 0.1
    wmin = np.amax(weight)
    for i in range(n):
        for j in range(n):
            if i != j:
                wmin = min(wmin, weight[i][j])
    eta_max = 1 / wmin
    print(wmin)
    eta_min = eps / np.amax(weight)
    steps = [
        eta_max * math.exp(1 / (iter - 1) * math.log(eta_min / eta_max) * t)
        for t in range(iter)
    ]
    ij = []
    for i in range(Z.shape[0]):
        for j in range(i + 1, Z.shape[0]):
            ij.append((i, j))
    print(steps)

    edge_colors = [
        "red" if [i + 1, j + 1] or [j + 1, i + 1] in c_edges else "gray"
        for i, j in links
    ]
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")

    # def fig_update(k):
    #     if k != 0:
    #         plt.cla()

    #     np.random.shuffle(ij)
    #     for i, j in ij:
    #         norm = np.linalg.norm(Z[i] - Z[j], ord=2)
    #         if norm < 1e-4:
    #             print(norm, dist[i][j])
    #             exit()

    #         r = (norm - dist[i][j]) * (Z[i] - Z[j]) / norm / 2

    #         myu = weight[i][j] * steps[k]
    #         myu = min(myu, 1)
    #         Z[i] -= myu * r
    #         Z[j] += myu * r

    #     blocks = NodeBlocks(Z[:, 1].flatten())
    #     y = project(constraints, blocks)
    #     Z[:, 1:2] = y.flatten()[:, None]

    #     plt.title(f"SGD ({k}) (seed 0)")

    #     position = {i + 1: Z[i] for i in range(n)}
    #     nx.draw(
    #         G,
    #         pos=position,
    #         node_size=300,
    #         labels={i + 1: i for i in range(n)},
    #         edge_color=edge_colors,
    #         ax=ax,
    #     )

    # ani = anm.FuncAnimation(fig, fig_update, frames=iter - 1, interval=100)
    # ani.save("lposn_after_merge_update.gif")

    for eta in steps:
        np.random.shuffle(ij)
        for i, j in ij:
            norm = np.linalg.norm(Z[i] - Z[j], ord=2)
            if norm < 1e-4:
                print(norm, dist[i][j])
                exit()

            r = (norm - dist[i][j]) * (Z[i] - Z[j]) / norm / 2

            myu = weight[i][j] * eta
            myu = min(myu, 1)
            Z[i] -= myu * r
            Z[j] += myu * r

        blocks = NodeBlocks(Z[:, 1].flatten())
        y = project(constraints, blocks)
        Z[:, 1:2] = y.flatten()[:, None]

    return Z


def sgd_y(Z, weight, dist):
    eta_max = 1 / np.amax(weight)
    lam = 1
    iter = 15
    steps = [eta_max * math.exp(-lam * t) for t in range(iter)]
    ij = []
    for i in range(Z.shape[0]):
        for j in range(i + 1, Z.shape[0]):
            ij.append((i, j))
    for eta in steps:
        np.random.shuffle(ij)
        for i, j in ij:
            norm = np.linalg.norm(Z[i] - Z[j], ord=2)
            r = (norm - dist[i][j]) * (Z[i] - Z[j]) / norm

            myu = weight[i][j] * eta
            Z[i] -= myu * r
            Z[j] += myu * r

    return Z


if __name__ == "__main__":
    with open("./src/data/no_cycle_tree.json") as f:
        data = json.load(f)

    nodes = [i + 1 for i in range(len(data["nodes"]))]
    n = len(nodes)

    links = [[d["source"] + 1, d["target"] + 1] for d in data["links"]]

    constraints = data["constraints"]
    c_edges = [[c["left"] + 1, c["right"] + 1] for c in constraints]

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
    dist *= 40

    # 座標の初期値はランダム
    Z = np.random.rand(n, 2)
    dim = len(Z[0])
    Z[0] = [0 for _ in range(dim)]
    #
    alpha = 2
    weights = weights_of_normalization_constant(alpha, dist)

    np.random.seed(0)
    Z = np.random.rand(n, 2)
    Z[0] = [0, 0]
    Z = sgd_ipsepcola(Z, weight=weights, dist=dist)

    def view():
        G = nx.DiGraph()
        for node in nodes:
            G.add_node(node)
        for link in links:
            G.add_edge(*link)

        edge_colors = [
            "red" if [i + 1, j + 1] or [j + 1, i + 1] in c_edges else "gray"
            for i, j in links
        ]

        position = {i + 1: Z[i] for i in range(n)}
        today = datetime.date.today()
        now = datetime.datetime.now().time()
        os.makedirs(f"result/{today}", exist_ok=True)

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect("equal")

        plt.title("Stress Majorization (seed 0)")
        nx.draw(
            G,
            pos=position,
            node_size=300,
            labels={i + 1: i for i in range(n)},
            edge_color=edge_colors,
            ax=ax,
        )
        plt.savefig(f"result/{today}/{now}.png")

    view()
