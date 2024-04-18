import numpy as np
from block import NodeBlocks
from constraint import Constraints


def solve_QPSC(A, b, constraints: Constraints, node_blocks: NodeBlocks):
    x = node_blocks.positions

    print("solve_QPSC")

    while True:
        g = A @ x + b
        s = (g.T @ g) / (g.T @ A @ g)
        x_hat = np.copy(x)
        x = x_hat - s[0][0] * g
        node_blocks.positions = x
        no_split = split_blocks(constraints, node_blocks)
        x_bar = project(constraints, node_blocks)
        d = x_bar - x_hat
        # print(len(d), len(d[0]))
        divede = d.T @ A @ d
        alpha = max(g.T @ d / divede, 1) if divede > 1e-6 else 1
        x = x_hat + alpha * d
        node_blocks.positions = x.flatten()

        norm = np.linalg.norm(x - x_hat, ord=2)
        if norm < 1e-6 and no_split:
            break

    return x


def split_blocks(constraints: Constraints, node_blocks: NodeBlocks):
    no_split = True
    return no_split


def project(constraints: Constraints, node_blocks: NodeBlocks):
    n = len(node_blocks.positions)
    block = node_blocks.blocks
    offset = node_blocks.offset
    B = node_blocks.B
    x = [B[block[i]].posn + offset[i] for i in range(n)]
    x = np.array(x).reshape(-1, 1)
    return x


# def violation(ci, constraints: Constraints, node_blocks: NodeBlocks):
#     ci_left = constraints.left(ci)
#     ci_right = constraints.right(ci)
#     return node_blocks.posn(ci_left) + constraints.gap(ci) - node_blocks.posn(ci_right)


# def solve_QPSC(A, b, constraints: Constraints, node_blocks: NodeBlocks):
#     x = node_blocks.positions

#     print("solve_QPSC")

#     while True:
#         g = A @ x + b
#         s = (g.T @ g) / (g.T @ A @ g)
#         x_hat = np.copy(x)
#         x = x_hat - s[0][0] * g
#         node_blocks.positions = x
#         no_split = split_blocks(constraints, node_blocks)
#         x_bar = project(constraints, node_blocks)
#         d = x_bar - x_hat
#         divede = d.T @ A @ d
#         alpha = max(g.T @ d / (d.T @ A @ d), 1) if divede != 0 else 1
#         x = x_hat + alpha * d
#         node_blocks.positions = x

#         norm = np.linalg.norm(x - x_hat, ord=2)
#         if norm < 1e-6 and no_split:
#             break

#     return x


# def project(constraints: Constraints, node_blocks: NodeBlocks):
#     x = node_blocks.positions
#     B = node_blocks.B
#     offset = node_blocks.offset
#     block = node_blocks.blocks
#     C = constraints.constraints

#     if len(C) == 0:
#         return x

#     c = np.argmax([violation(ci, constraints, node_blocks) for ci in range(len(C))])

#     while violation(c, constraints, node_blocks) > 1e-6:
#         c_left = constraints.left(c)
#         c_right = constraints.right(c)
#         if block[c_left] != block[c_right]:
#             merge_blocks(block[c_left], block[c_right], c, constraints, node_blocks)
#         else:
#             expand_block(block[c_left], c, constraints, node_blocks)
#         c = np.argmax([violation(ci, constraints, node_blocks) for ci in range(len(C))])
#         print(f"{c=} {violation(c, constraints, node_blocks)=}")
#         print(f"{violation(c, constraints, node_blocks)>1e-6=}")

#     n = len(block)
#     for i in range(n):
#         x[i][0] = B[block[i]].posn + offset[i]

#     node_blocks.positions = x
#     return x


# def merge_blocks(L, R, c, constraints: Constraints, node_blocks: NodeBlocks):
#     block = node_blocks.blocks
#     offset = node_blocks.offset
#     B = node_blocks.B

#     d = offset[L] + constraints.gap(c) - offset[R]
#     B[L].posn = (B[L].posn * B[L].nvars + (B[R].posn - d) * B[R].nvars) / (
#         B[L].nvars + B[R].nvars
#     )
#     B[L].active = B[L].active.union(B[R].active)
#     B[L].active.add(c)

#     for i in B[R].vars:
#         block[i] = L
#         offset[i] += d
#     B[L].vars = B[L].vars.union(B[R].vars)
#     B[L].nvars = B[L].nvars + B[R].nvars
#     B[R].nvars = 0

#     node_blocks.blocks = block
#     node_blocks.offset = offset
#     node_blocks.B = B


# def expand_block(b, c_tilde, constraints: Constraints, node_blocks: NodeBlocks):
#     global lm
#     x = node_blocks.positions
#     B = node_blocks.B
#     offset = node_blocks.offset

#     for c in B[b].active:
#         lm[c] = 0
#     AC: set = B[b].active

#     c_tilde_left = constraints.left(c_tilde)
#     c_tilde_right = constraints.right(c_tilde)
#     comp_dfdv(c_tilde_left, AC, None, constraints, node_blocks)
#     v = comp_path(c_tilde_left, c_tilde_right, AC, constraints)
#     ps = set()
#     for c in AC:
#         c_left = constraints.left(c)
#         c_right = constraints.right(c)
#         for j in range(len(v) - 1):
#             if c_left == v[j] and c_right == v[j + 1]:
#                 ps.add(c)
#                 break

#     if len(ps) != 0:
#         ps = list(ps)
#         sc = ps[np.argmin([lm[c] for c in ps])]
#         AC.discard(sc)

#     for v in connected(c_tilde_right, AC, constraints):
#         offset[v] += max(0.0001, violation(c_tilde, constraints, node_blocks))
#     AC.add(c_tilde)
#     B[b].active = AC
#     B[b].posn = sum([x[j][0] - offset[j] for j in B[b].vars]) / B[b].nvars

#     node_blocks.positions = x
#     node_blocks.B = B
#     node_blocks.offset = offset


# def comp_dfdv(v, AC, u, constraints: Constraints, node_blocks: NodeBlocks):
#     global lm
#     x = node_blocks.positions

#     dfdv = node_blocks.posn(v) - x[v][0]
#     if v == u:
#         return dfdv

#     for c in AC:
#         c_left = constraints.left(c)
#         c_right = constraints.right(c)
#         if not (v == c_left and u != c_right):
#             continue
#         lm[c] = comp_dfdv(c_right, AC, v, constraints, node_blocks)
#         dfdv += lm[c]
#     for c in AC:
#         if not (v == c_right and u != c_left):
#             continue
#         lm[c] = -comp_dfdv(c_left, AC, v, constraints, node_blocks)
#         dfdv -= lm[c]

#     return dfdv


# def split_blocks(constraints: Constraints, node_blocks: NodeBlocks):
#     global lm
#     block = node_blocks.blocks
#     offset = node_blocks.offset
#     B = node_blocks.B
#     x = node_blocks.positions

#     no_split = True
#     for i in range(len(B)):
#         if B[i].nvars == 0:
#             continue

#         B[i].posn = sum([x[j][0] - offset[j] for j in B[i].vars]) / B[i].nvars
#         AC: set = B[i].active
#         for c in AC:
#             lm[c] = 0
#         # random?
#         v = B[i].vars.pop()
#         B[i].vars.add(v)

#         comp_dfdv(v, AC, None, constraints, node_blocks)

#         if len(AC) == 0:
#             continue
#         sc = list(AC)[np.argmin([lm[c] for c in AC])]
#         if lm[sc] >= 0:
#             break
#         no_split = False
#         AC.remove(sc)
#         s = constraints.right(sc)
#         B[s].vars = connected(s, AC, constraints)
#         for v in B[s].vars:
#             block[v] = s

#         B[i].vars = B[i].vars.difference(B[s].vars)

#         B[s].nvars = len(B[s].vars)
#         B[i].nvars = len(B[i].vars)

#         if B[s].nvars == 0:
#             B[s].posn = 0
#         else:
#             B[s].posn = sum([x[j][0] - offset[j] for j in B[s].vars]) / B[s].nvars

#         if B[i].nvars == 0:
#             B[i].posn = 0
#         else:
#             B[i].posn = sum([x[j][0] - offset[j] for j in B[i].vars]) / B[i].nvars

#         B[i].active = {
#             c
#             for c in AC
#             if constraints.left(c) in B[s].vars and constraints.right(c) in B[s].vars
#         }
#         B[s].active = AC.difference(B[i].active)

#     node_blocks.blocks = block
#     node_blocks.B = B
#     return no_split


# def connected(s, AC, constraints: Constraints):
#     c_graph = constraints.graph

#     v = set()
#     v.add(s)
#     # left to right path nodes
#     stack = [s]
#     while len(stack) > 0:
#         u = stack.pop()
#         for vv, cost in c_graph[u]:
#             if u not in AC or v not in AC:
#                 continue
#             if vv in v:
#                 continue
#             v.add(vv)
#             stack.append(vv)

#     return v


# def comp_path(left, right, AC, constraints: Constraints):
#     global G
#     path = list(nx.all_simple_paths(G, left, right))[0]


#     return path
