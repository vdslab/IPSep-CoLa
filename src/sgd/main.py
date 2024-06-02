import math

import numpy as np
import json
from ipsep_cola.constraint import Constraints
import datetime
import os
from ipsep_cola.block import NodeBlocks
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from ipsep_cola.QPSC import project

from networkx import floyd_warshall_numpy

from majorization.main import weights_of_normalization_constant, stress

sys.setrecursionlimit(10000000)


def sgd(Z, weight, dist):
    iter = 500
    eps = 0.1
    n = Z.shape[0]

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


def sgd_ipsepcola(Z, weight, dist, gap, data):
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
        # gap = c["gap"]
        C[axis].append([left, right, gap])
    constraint_graph = nx.Graph()
    for l, r, g in C["y"]:
        constraint_graph.add_edge(l, r, gap=gap)

    constraints = Constraints(C["y"], n)

    lam = 1
    iter = 300
    eps = 0.1
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
    ij = []
    for i in range(Z.shape[0]):
        for j in range(i + 1, Z.shape[0]):
            ij.append((i, j))

    # fig, ax = plt.subplots(figsize=(10, 10))
    # ax.set_aspect("equal")

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

    stresses = []
    times = []
    for eta in steps:
        np.random.shuffle(ij)
        for i, j in ij:
            norm = np.linalg.norm(Z[i] - Z[j], ord=2)
            if norm < 1e-4:
                print(norm, dist[i][j])
                exit()

            r = (norm - dist[i][j]) * (Z[i] - Z[j]) / norm / 2

            if weight[i][j] == 0:
                myu = eta
            else:
                myu = weight[i][j] * eta
            myu = min(myu, 1)
            Z[i] -= myu * r
            Z[j] += myu * r

        blocks = NodeBlocks(Z[:, 1].flatten())
        y = project(constraints, blocks)
        # y = sgd_project(Z[:, 1].flatten(), constraint_graph)
        Z[:, 1:2] = y.flatten()[:, None]
        stresses.append(stress(Z, dist, weight))
        times.append(time.time())

    return Z, stresses, times


# from numpy import ndarray


# def sgd_project(
#     positions1D: ndarray,
#     # graph: nx.Graph,
#     constraint_graph: nx.Graph,
#     node_blocks: NodeBlocks = None,
# ):
#     if positions1D.ndim != 1:
#         raise ValueError("positions must be a 1D array")

#     c_node_len = len(constraint_graph.nodes)
#     if c_node_len == 0:
#         return

#     if node_blocks is None:
#         node_blocks = NodeBlocks(positions1D)

#     node_len = constraint_graph.number_of_nodes()
#     edge_len = constraint_graph.number_of_edges()
#     blocks = node_blocks.blocks
#     offset = node_blocks.offset
#     B = node_blocks.B

#     def get_edge_data(edge_index: int):
#         edge_index = int(edge_index)
#         edges = list(constraint_graph.edges)
#         left, right = edges[edge_index]
#         edge_data = constraint_graph.get_edge_data(left, right)
#         gap = edge_data.get("gap", 20)
#         return left, right, gap

#     def violation(edge_index: int):
#         left, right, gap = get_edge_data(edge_index)
#         return node_blocks.posn(left) + gap - node_blocks.posn(right)

#     def get_max_violation_edge_index():
#         violations = [violation(ci) for ci in range(edge_len)]
#         c_index = int(np.argmax(violations))
#         c_violation = violations[c_index]
#         return c_index, c_violation

#     def merge_blocks(L: int, R: int, edge_index: int):
#         left, right, gap = get_edge_data(edge_index)

#         d = offset[left] + gap - offset[right]

#         B[L].posn = (
#             (B[L].posn * B[L].nvars + (B[R].posn - d) * B[R].nvars)
#             / (B[L].nvars + B[R].nvars)
#             if B[L].nvars + B[R].nvars != 0
#             else 0
#         )

#         B[L].active = B[L].active.union(B[R].active)
#         B[L].active.add(edge_index)

#         for i in B[R].vars:
#             blocks[i] = L
#             offset[i] += d

#         B[L].vars = B[L].vars.union(B[R].vars)
#         B[L].nvars = B[L].nvars + B[R].nvars
#         B[R].nvars = 0

#     def connected(graph: nx.DiGraph, node: int):
#         v = set()
#         v.add(node)
#         que = deque()
#         que.append(node)
#         while que:
#             frm = que.popleft()
#             for _, to in graph.out_edges(frm):
#                 if to in v:
#                     continue
#                 v.add(to)
#                 que.append(to)

#         return list(v)

#     def expand_block(block: int, edge_index: int):
#         _, c_tilde_right, _ = get_edge_data(edge_index)

#         AC: set = B[block].active
#         AC_grpah = nx.Graph()
#         AC_grpah.add_nodes_from(constraint_graph.nodes)
#         AC_grpah.add_edges_from([edge for edge in constraint_graph.edges if edge in AC])
#         v = shortest_simple_paths()

#         ps = set()
#         for c in AC:
#             c_left, c_right, gap = get_edge_data(c)
#             for j in range(len(v) - 1):
#                 if c_left == v[j] and c_right == v[j + 1]:
#                     ps.add(c)
#                     break

#         AC_grpah.to_directed()

#         edge_violation = violation(edge_index)
#         for v in connected(AC_grpah, c_tilde_right):
#             offset[v] += max(0.0001, edge_violation)
#         AC.add(edge_index)
#         # B[block].active = AC
#         B[block].posn = (
#             sum([positions1D[j] - offset[j] for j in B[block].vars]) / B[block].nvars
#             if B[block].nvars != 0
#             else 0
#         )

#     for _ in range(edge_len):
#         edge_ci, violate = get_max_violation_edge_index()
#         print(edge_ci, violate)
#         if violate <= 1e-6:
#             break
#         left, right, _ = get_edge_data(edge_ci)
#         if blocks[left] != blocks[right]:
#             merge_blocks(blocks[left], blocks[right], edge_ci)
#         else:
#             expand_block(blocks[left], edge_ci)

#     x = [B[blocks[i]].posn + offset[i] for i in range(node_len)]
#     x = np.array(x).reshape(-1, 1)
#     return x


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


def plot_sgd(file, save_dir, edge_length, gap):
    base_name = os.path.splitext(os.path.basename(file))[0]
    with open(file) as f:
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
    dist *= edge_length

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
    Z, stresses, times = sgd_ipsepcola(Z, weight=weights, dist=dist, gap=gap, data=data)

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

        plt.title(f"SGD (seed 0) {edge_length=} {gap=}")
        nx.draw(
            G,
            pos=position,
            node_size=300,
            labels={i + 1: i for i in range(n)},
            edge_color=edge_colors,
            ax=ax,
        )
        plt.savefig(f"{save_dir}/{base_name}_{edge_length=}_{gap=}.png")
        plt.close()

    view()

    return stresses, times


import glob

if __name__ == "__main__":
    print(glob.glob("src/data/*.json"))

    gaps = np.arange(10, 51, 10)
    edge_lengths = np.arange(10.0, 51.0, 10.0)
    today = datetime.date.today()
    now = datetime.datetime.now()
    save_dir = f"result/SGD/edge_gap/{today}/{now}"
    os.makedirs(save_dir, exist_ok=True)

    for gap in gaps:
        for edge_length in edge_lengths:
            plot_sgd("./src/data/no_cycle_tree.json", save_dir, gap, edge_length)
    # print(edge_length, gap, "done")

    # for file in glob.glob("src/data/*_100.json"):
    #     print(file)
    #     today = datetime.date.today()
    #     now = datetime.datetime.now().time()
    #     save_dir = f"result/SGD/n50/{today}"
    #     os.makedirs(save_dir, exist_ok=True)

    #     edge_legth = 20
    #     gap = 20

    #     plot_sgd(file, save_dir, edge_legth, gap)
    #     print(file, "done")
