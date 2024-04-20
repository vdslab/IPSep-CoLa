import datetime
import json
import os

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from block import NodeBlocks
from constraint import Constraints
from majorization.main import (
    stress,
    weight_laplacian,
    weights_of_normalization_constant,
    z_laplacian,
)
from networkx import floyd_warshall_numpy
from QPSC import solve_QPSC
from scipy.sparse.linalg import cg

lm = dict()


def IPSep_CoLa(graph: nx.Graph, constraints: Constraints, edge_length: float = 20.0):
    """
    graph: networkx.Graph
    graph.edges: [(i, j), ...] node index
    """

    n = len(graph.nodes)
    sigmas = [[0] * n] * n
    for i, j in graph.edges:
        sigmas[i][j] = 1

    dist = floyd_warshall_numpy(graph)
    dist *= edge_length

    Z = np.random.rand(n, 2)
    Z[0] = [0, 0]

    weight = weights_of_normalization_constant(2, dist)

    Lw = weight_laplacian(weight)

    # 実行
    eps = 0.0001
    now_stress = stress(Z, dist, weight)
    new_stress = 0.5 * now_stress

    def delta_stress(now, new):
        return abs(now - new) / now

    y_blocks = NodeBlocks(Z[:, 1].flatten())

    iter = 100
    while delta_stress(now_stress, new_stress) > eps and iter > 0:
        iter -= 1
        Lz = z_laplacian(weight, dist, Z)
        for a in range(2):
            Z[1:, a] = cg(Lw[1:, 1:], (Lz @ Z[:, a])[1:])[0]
        # Z[1:, 0] = cg(Lw[1:, 1:], (Lz @ Z[:, 0])[1:])[0]

        y_blocks = NodeBlocks(Z[:, 1].flatten())
        b = (Lz @ Z[:, 1]).reshape(-1, 1)
        A = Lw
        delta_x = solve_QPSC(A, b, constraints, y_blocks)
        # print(delta_x)
        Z[:, 1:2] = delta_x.flatten()[:, None]
        for i in range(n - 1, -1, -1):
            Z[i] -= Z[0]

        now_stress = new_stress
        new_stress = stress(Z, dist, weight)
        print("stress", now_stress, "->", new_stress)

    # json.dump(y_blocks.__dict__(), open("result.json", "w"))
    # print(y_blocks.__dict__())

    return Z


if __name__ == "__main__":
    with open("./src/data/no_cycle_tree.json") as f:
        data = json.load(f)

    nodes = [i for i in range(len(data["nodes"]))]
    n = len(nodes)

    links = [[d["source"], d["target"]] for d in data["links"]]
    constraints = data["constraints"]

    G = nx.Graph()
    for node in nodes:
        G.add_node(node)
    for link in links:
        G.add_edge(*link)

    np.random.seed(0)
    today = datetime.date.today()
    now = datetime.datetime.now().time()
    dir = f"result/IPSep_Cola/{today}/{now.hour}-{now.minute}-{now.second}"

    def view(position, file_name):
        DG = nx.DiGraph()
        for node in nodes:
            DG.add_node(node)
        for link in links:
            DG.add_edge(*link)

        position = {i: position[i] for i in range(n)}

        os.makedirs(dir, exist_ok=True)

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect("equal")

        plt.title(file_name)
        nx.draw(G, pos=position, node_size=300, labels={i: i for i in range(n)}, ax=ax)
        plt.savefig(f"{dir}/{file_name}.png")

    # C = []
    # for c in constraints:
    #     C.append([c["left"], c["right"], 30])
    # const = Constraints(C, n)
    # Z = IPSep_CoLa(G, const, edge_length=20.0)
    # view(Z, "IPSep_Cola (seed 0) gap=30, edge_length=20.0.png")

    gaps = np.arange(10, 51, 10)
    edge_lengths = np.arange(10.0, 51.0, 10.0)
    for gap in gaps:
        for edge_length in edge_lengths:
            C = []
            for c in constraints:
                C.append([c["left"], c["right"], gap])
            const = Constraints(C, n)
            Z = IPSep_CoLa(G, const, edge_length=edge_length)
            view(Z, f"IPSep_Cola (seed 0) {gap=}, {edge_length=}.png")
