from collections import deque

import numpy as np
from block import NodeBlocks
from constraint import Constraints
from numpy import ndarray
from comp_dfdv import comp_dfdv

lm = dict()


def solve_QPSC(
    A: ndarray,
    b: ndarray,
    constraints: Constraints,
    node_blocks: NodeBlocks,
):
    global lm
    # print("solve_QPSC")
    lm = dict()
    x = np.copy(node_blocks.positions)
    x = x.reshape(-1, 1)

    iter = 30

    for i in range(iter):
        g = A @ x + b
        s = (g.T @ g) / (g.T @ A @ g)
        x_hat = np.copy(x)
        x = x_hat - s[0][0] * g

        no_split = split_blocks(x.flatten(), constraints, node_blocks)
        x_bar = project(constraints, node_blocks)

        d = x_bar - x_hat
        divede = d.T @ A @ d
        alpha = max(g.T @ d / divede, 1) if divede > 1e-6 else 1
        x = x_hat + alpha * d
        node_blocks.positions = x.flatten()

        try:
            norm = np.linalg.norm(x - x_hat, ord=2)
            if norm < 1e-4 and no_split:
                break
        except np.linalg.LinAlgError as e:
            print(e)

    return x


def split_blocks(position: ndarray, constraints: Constraints, node_blocks: NodeBlocks):
    if position.ndim != 1:
        raise ValueError("positions must be a 1D array")

    no_split = True

    for b in node_blocks.B:
        if b.nvars == 0:
            continue
        AC: set = b.active
        if len(AC) == 0:
            continue

        b.posn = sum([position[j] - node_blocks.offset[j] for j in b.vars]) / float(
            b.nvars
        )

        for c in AC:
            lm[c] = 0

        v = b.vars.pop()
        b.vars.add(v)
        sub_lm = comp_dfdv(v, AC, None, constraints, node_blocks)
        for key, value in sub_lm.items():
            lm.setdefault(key, 0)
            lm[key] = value

        AC_list = list(AC)
        sc = AC_list[np.argmin([lm[c] for c in AC_list])]
        if lm[sc] >= 0:
            break
        no_split = False
        AC.discard(sc)

        s = node_blocks.blocks[constraints.right(sc)]

        node_blocks.B[s].vars = connected(s, AC, constraints)

        for v in node_blocks.B[s].vars:
            node_blocks.blocks[v] = s

        b.vars = b.vars.difference(node_blocks.B[s].vars)
        node_blocks.B[s].nvars = len(node_blocks.B[s].vars)
        b.nvars = len(b.vars)
        node_blocks.B[s].posn = (
            (
                sum(
                    [position[j] - node_blocks.offset[j] for j in node_blocks.B[s].vars]
                )
                / float(node_blocks.B[s].nvars)
            )
            if node_blocks.B[s].nvars != 0
            else 0
        )
        b.posn = (
            sum([position[j] - node_blocks.offset[j] for j in b.vars]) / float(b.nvars)
            if b.nvars != 0
            else 0
        )
        b.active = {
            c
            for c in AC
            if constraints.left(c) in node_blocks.B[s].vars
            and constraints.right(c) in node_blocks.B[s].vars
        }
        node_blocks.B[s].active = AC.difference(b.active)

    return no_split


def connected(s, AC, constraints: Constraints):
    c_graph = constraints.graph

    AC_edges = set()
    for c in AC:
        c_left = constraints.left(c)
        c_right = constraints.right(c)
        AC_edges.add((c_left, c_right))

    v = set()
    v.add(s)
    # left to right path nodes
    stack = [s]
    while len(stack) > 0:
        u = stack.pop()
        for vv, cost in c_graph[u]:
            if vv in v:
                continue
            if (u, vv) not in AC_edges:
                continue
            v.add(vv)
            stack.append(vv)

    return v


def project(constraints: Constraints, node_blocks: NodeBlocks):
    n = len(node_blocks.positions)
    block = node_blocks.blocks
    offset = node_blocks.offset
    B = node_blocks.B

    if len(constraints.constraints) != 0:

        def get_max_violation_c():
            violations = [
                violation(ci, constraints, node_blocks)
                for ci in range(len(constraints.constraints))
            ]
            c_index = np.argmax(violations)
            return c_index

        c = get_max_violation_c()
        iter = len(constraints.constraints)
        while violation(c, constraints, node_blocks) > 1e-6 and iter > 0:
            iter -= 1
            c_left = constraints.left(c)
            c_right = constraints.right(c)
            if block[c_left] != block[c_right]:
                merge_blocks(block[c_left], block[c_right], c, constraints, node_blocks)
            else:
                expand_block(block[c_left], c, constraints, node_blocks)
            c = get_max_violation_c()

    x = [B[block[i]].posn + offset[i] for i in range(n)]
    x = np.array(x).reshape(-1, 1)
    return x


def violation(ci, constraints: Constraints, node_blocks: NodeBlocks):
    ci_left = constraints.left(ci)
    ci_right = constraints.right(ci)
    return node_blocks.posn(ci_left) + constraints.gap(ci) - node_blocks.posn(ci_right)


def merge_blocks(L, R, c, constraints: Constraints, node_blocks: NodeBlocks):
    block = node_blocks.blocks
    offset = node_blocks.offset
    B = node_blocks.B

    # Tips: LとRを合体させてしまってた
    c_left = constraints.left(c)
    c_right = constraints.right(c)
    # 同じブロックのとき，制約をみたすためにrightに必要な距離
    d = offset[c_left] + constraints.gap(c) - offset[c_right]

    B[L].posn = (
        (B[L].posn * B[L].nvars + (B[R].posn - d) * B[R].nvars)
        / (B[L].nvars + B[R].nvars)
        if B[L].nvars + B[R].nvars != 0
        else 0
    )

    B[L].active = B[L].active.union(B[R].active)
    B[L].active.add(c)

    for i in B[R].vars:
        block[i] = L
        offset[i] += d

    B[L].vars = B[L].vars.union(B[R].vars)
    B[L].nvars = B[L].nvars + B[R].nvars
    B[R].nvars = 0


def expand_block(b, c_tilde, constraints: Constraints, node_blocks: NodeBlocks):
    global lm
    x = node_blocks.positions
    B = node_blocks.B
    offset = node_blocks.offset

    for c in B[b].active:
        lm[c] = 0

    AC: set = B[b].active

    c_tilde_left = constraints.left(c_tilde)

    sub_lm: dict = comp_dfdv(c_tilde_left, AC, None, constraints, node_blocks)
    for key, value in sub_lm.items():
        lm.setdefault(key, 0)
        lm[key] = value

    c_tilde_right = constraints.right(c_tilde)
    v = comp_path(c_tilde_left, c_tilde_right, AC, constraints)

    ps = set()
    for c in AC:
        c_left = constraints.left(c)
        c_right = constraints.right(c)
        for j in range(len(v) - 1):
            if c_left == v[j] and c_right == v[j + 1]:
                ps.add(c)
                break

    if len(ps) != 0:
        ps = list(ps)
        sc = ps[np.argmin([lm[c] for c in ps])]
        AC.discard(sc)

    for v in connected(c_tilde_right, AC, constraints):
        offset[v] += max(0.0001, violation(c_tilde, constraints, node_blocks))
    AC.add(c_tilde)
    B[b].active = AC
    B[b].posn = (
        sum([x[j] - offset[j] for j in B[b].vars]) / B[b].nvars
        if B[b].nvars != 0
        else 0
    )


def comp_path(left, right, AC, constraints: Constraints):
    c_graph = constraints.graph

    AC_vars = set()
    AC_edges = set()
    for c in AC:
        c_left = constraints.left(c)
        c_right = constraints.right(c)
        AC_vars.add(c_left)
        AC_vars.add(c_right)
        AC_edges.add((c_left, c_right))
        # AC_edges.add((c_right, c_left))

    if left not in AC_vars or right not in AC_vars:
        return []

    parent = {v: v for v in AC_vars}
    v = set()
    v.add(left)
    que = deque()
    que.append(left)
    while len(que) > 0:
        u = que.popleft()
        for vv, cost in c_graph[u]:
            if vv in v:
                continue
            if (u, vv) not in AC_edges:
                continue

            v.add(vv)
            parent[vv] = u
            que.append(vv)
            if vv == right:
                break

    if right == parent[right]:
        return []
    path = []
    u = right
    while u != left:
        path.append(u)
        u = parent[u]
    path.append(left)
    path.reverse()
    return path
