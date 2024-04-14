import datetime
import json
import os

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from majorization.main import (
    stress,
    weight_laplacian,
    weights_of_normalization_constant,
    z_laplacian,
)
from networkx import floyd_warshall_numpy
from scipy.sparse.linalg import cg

from .block import Block
from .constraint import Constraints

lm = dict()
blocks = [i for i in range(1)]
offset = [0 for _ in range(1)]
x = [[0] for _ in range(1)]
B = [Block(i, x[i][0]) for i in range(1)]


def left(ci):
    return C[ci][0] - 1


def right(ci):
    return C[ci][1] - 1


def gap(ci):
    return C[ci][2]


def posn(vi):
    global blocks
    global offset
    global B

    return B[blocks[vi]].posn + offset[vi]


def violation(ci):
    return posn(left(ci)) + gap(ci) - posn(right(ci))


def solve_QPSC(A, b, C, constraints: Constraints):
    global x
    global B
    global offset
    global blocks

    print("solve_QPSC")

    while True:
        g = A @ x + b
        s = (g.T @ g) / (g.T @ A @ g)
        x_hat = np.copy(x)
        x = x_hat - s[0][0] * g
        no_split = split_blocks()
        x_bar = project(C, constraints)
        d = x_bar - x_hat
        alpha = max(g.T @ d / (d.T @ A @ d), 1)
        x = x_hat + alpha * d

        norm = np.linalg.norm(x - x_hat, ord=2)
        if norm < 1e-6 and no_split:
            break

    return x


def project(C, constraints: Constraints):
    global x
    global blocks
    global offset
    global B
    block = blocks

    if len(C) == 0:
        return x

    c = np.argmax([violation(ci) for ci in range(len(C))])

    while violation(c) > 0:
        if block[left(c)] != block[right(c)]:
            merge_blocks(block[left(c)], block[right(c)], c)
        else:
            expand_block(block[left(c)], c, constraints)
        c = np.argmax([violation(ci) for ci in range(len(C))])

    n = len(block)
    for i in range(n):
        x[i] = B[block[i]].posn + offset[i]

    return x


def merge_blocks(L, R, c):
    global blocks
    global offset
    global B

    block = blocks
    d = offset[L] + gap(c) - offset[R]
    B[L].posn = (B[L].posn * B[L].nvars + (B[R].posn - d) * B[R].nvars) / (
        B[L].nvars + B[R].nvars
    )
    B[L].active = B[L].active.union(B[R].active)
    B[L].active.add(c)

    for i in B[R].vars:
        block[i] = L
        offset[i] += d
    B[L].vars = B[L].vars.union(B[R].vars)
    B[L].nvars = B[L].nvars + B[R].nvars
    B[R].nvars = 0


def expand_block(b, c_tilde, constraints: Constraints):
    global lm
    global x
    global offset
    global B

    for c in B[b].active:
        lm[c] = 0
    AC: set = B[b].active

    c_tilde_left = constraints.left_index(c_tilde)
    c_tilde_right = constraints.right_index(c_tilde)
    comp_dfdv(c_tilde_left, AC, None)
    v = comp_path(c_tilde_left, c_tilde_right, AC)
    ps = set()
    for c in AC:
        for j in range(len(v) - 1):
            c_left = constraints.left_index(c)
            c_right = constraints.right_index(c)
            if c_left == v[j] and c_right == v[j + 1]:
                ps.add(c)
                break

    if len(ps) != 0:
        ps = list(ps)
        sc = ps[np.argmin([lm[c] for c in ps])]
        AC.discard(sc)

    # for v in connected(right(c_tilde), AC):
    for v in B[c_tilde_right].vars:
        offset[v] += violation(c_tilde)
    AC.add(c_tilde)
    B[b].active = AC
    B[b].posn = sum([x[j][0] - offset[j] for j in B[b].vars]) / B[b].nvars


def comp_dfdv(v, AC, u):
    global x
    global lm

    dfdv = posn(v) - x[v][0]
    if v == u:
        return dfdv

    for c in AC:
        if not (v == left(c) and u != right(c)):
            continue
        lm[c] = comp_dfdv(right(c), AC, v)
        dfdv += lm[c]
    for c in AC:
        if not (v == right(c) and u != left(c)):
            continue
        lm[c] = -comp_dfdv(left(c), AC, v)
        dfdv -= lm[c]

    return dfdv


def split_blocks(constraints: Constraints):
    global lm
    global x
    global offset
    global blocks
    global B
    block = blocks

    no_split = True
    for i in range(len(B)):
        if B[i].nvars == 0:
            continue

        B[i].posn = sum([x[j][0] - offset[j] for j in B[i].vars]) / B[i].nvars

        AC: set = B[i].active
        for c in AC:
            lm[c] = 0
        # random?
        v = B[i].vars.pop()
        B[i].vars.add(v)

        comp_dfdv(v, AC, None)

        if len(AC) == 0:
            continue
        sc = list(AC)[np.argmin([lm[c] for c in AC])]
        if lm[sc] >= 0:
            break
        no_split = False
        AC.remove(sc)
        s = right(sc)
        B[s].vars = connected(s, AC, constraints)
        for v in B[s].vars:
            block[v] = s

        B[i].vars = B[i].vars.difference(B[s].vars)

        B[s].nvars = len(B[s].vars)
        B[i].nvars = len(B[i].vars)

        if B[s].nvars == 0:
            B[s].posn = 0
        else:
            B[s].posn = sum([x[j][0] - offset[j] for j in B[s].vars]) / B[s].nvars

        if B[i].nvars == 0:
            B[i].posn = 0
        else:
            B[i].posn = sum([x[j][0] - offset[j] for j in B[i].vars]) / B[i].nvars

        B[i].active = {c for c in AC if left(c) in B[s].vars and right(c) in B[s].vars}
        B[s].active = AC.difference(B[i].active)

    return no_split


def connected(s, AC, constraints: Constraints):
    c_graph = constraints.graph

    v = set()
    v.add(s)
    # left to right path nodes
    stack = [s]
    while len(stack) > 0:
        u = stack.pop()
        for vv, cost in c_graph[u]:
            if u not in AC or v not in AC:
                continue
            if vv in v:
                continue
            v.add(vv)
            stack.append(vv)

    return v


def comp_path(left, right, AC, constraints: Constraints):
    c_graph = constraints.graph
    v = set()
    v.add(left)
    v.add(right)
    # left to right path nodes
    stack = [left]
    while len(stack) > 0:
        u = stack.pop()
        for vv, cost in c_graph[u]:
            if u not in AC or v not in AC:
                continue
            if vv in v:
                continue
            v.add(vv)
            stack.append(vv)

    return list(v)


def stress_majorization(
    nodes, links, *, dim=2, initZ=None, constraints: Constraints = None
):
    global x
    global blocks
    global offset
    global B

    n = len(nodes)

    blocks = [i for i in range(n)]
    offset = [0 for _ in range(n)]

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
    np.random.seed(0)
    Z = np.random.rand(n, dim)
    if initZ is not None:
        Z = initZ
    dim = len(Z[0])
    Z[0] = [0 for _ in range(dim)]
    x = [[Z[i][1]] for i in range(n)]
    B = [Block(i, Z[i][1]) for i in range(n)]
    #
    alpha = 2
    weights = weights_of_normalization_constant(alpha, dist)

    Lw = weight_laplacian(weights)

    def update_ipset_cola():
        # ipsep_cola
        Lz = z_laplacian(weights, dist, Z)
        b = (Lz @ Z[:, 1]).reshape(-1, 1)
        A = Lw
        delta_x = solve_QPSC(A, b, C, constraints)
        Z[:, 1:2] = delta_x.flatten()[:, None]
        Z[0] = [0 for _ in range(dim)]

    update_ipset_cola()

    # 終了する閾値
    eps = 0.000_01
    now_stress = stress(Z, dist, weights)
    new_stress = 0.5 * now_stress

    def delta_stress(now, new):
        return (now - new) / now

    while True:
        Lz = z_laplacian(weights, dist, Z)

        # for a in range(dim):
        #     # Ax = b
        #     Z[1:, a] = cg(Lw[1:, 1:], (Lz @ Z[:, a])[1:])[0]
        Z[1:, 0] = cg(Lw[1:, 1:], (Lz @ Z[:, 0])[1:])[0]

        update_ipset_cola()

        new_stress = stress(Z, dist, weights)
        print(f"{now_stress=} -> {new_stress=}")
        print(delta_stress(now_stress, new_stress))

        if delta_stress(now_stress, new_stress) < eps:
            break
        now_stress = new_stress

    return Z


if __name__ == "__main__":
    with open("./src/majorization/data.json") as f:
        data = json.load(f)

    nodes = [i + 1 for i in range(len(data["nodes"]))]
    n = len(nodes)

    links = [[d["source"] + 1, d["target"] + 1] for d in data["links"]]
    constraints = data["constraints"]

    C = []
    # for c in constraints:
    #     C.append([c["right"], c["left"], 1])
    const = Constraints(C, n)

    Z = stress_majorization(nodes, links, constraints=const)

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
        nx.draw(G, pos=position, node_size=300, labels={i + 1: i for i in range(n)})
        plt.savefig(f"result/{today}/{now}.png")
        # plt.show()

    view()
