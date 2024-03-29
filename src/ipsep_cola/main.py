import numpy as np

n = 19
x: list[list] = [[0, 0] for _ in range(n)]
# from, to, cost
C = [
    [3, 2, 1],
    [3, 4, 1],
    [5, 1, 1],
    [5, 3, 1],
    [5, 4, 1],
    [5, 7, 1],
    [5, 6, 1],
    [5, 9, 1],
    [7, 6, 1],
    [7, 10, 1],
    [9, 8, 1],
    [9, 6, 1],
    [9, 5, 1],
    [9, 7, 1],
    [9, 10, 1],
    [9, 11, 1],
    [10, 13, 1],
    [11, 12, 1],
    [12, 11, 1],
    [13, 10, 1],
    [13, 15, 1],
    [14, 12, 1],
    [14, 15, 1],
    [14, 16, 1],
    [15, 13, 1],
    [15, 16, 1],
    [16, 15, 1],
    [16, 17, 1],
    [17, 16, 1],
    [17, 18, 1],
    [17, 19, 1],
    [18, 19, 1],
    [19, 18, 1],
]

graph = [[] for _ in range(n)]
for l, r, c in C:
    graph[l - 1].append((r - 1, c))
    graph[r - 1].append((l - 1, c))


class Block:
    def __init__(self, posn, nvars):
        self.posn = posn
        self.nvars = nvars
        self.active = set()
        self.vars = set()


B = [Block(0, 0) for _ in range(n)]


def left(c):
    return C[c][0] - 1


def right(c):
    return C[c][1] - 1


def gap(c):
    return C[c][2]


def posn(vi):
    pass


def violation(c):
    return posn(left(c)) + gap(c) - posn(right(c))


lm = dict()


def solve_QPSC(A, b, C):
    global x
    while True:
        g = A @ x + b
        s = g.T @ g / (g.T @ A @ g)
        x_hat = np.copy(x)
        x = x_hat - s @ g
        no_split = split_blocks(x)
        x_bar = project(C)
        d = x_bar - x_hat
        alpha = max(g.T @ d / (d.T @ A @ d), 1)
        x = x_hat + alpha * d

        norm = np.linalg.norm(x - x_hat, ord=2)
        if norm < 1e-6 and no_split:
            break

    return x


def project(C, block, B: list[Block], offset):
    global x
    c = max([violation(c) for c in C])
    while violation(c) > 0:
        if block[left(c)] != block[right(c)]:
            merge_blocks(block[left(c)], block[right(c)], c)
        else:
            expand_block(block[left(c)], c)
        c = max([violation(c) for c in C])

    n = len(block)
    for i in range(n):
        x[i] = B[block[i]].posn + offset[i]

    return x


def merge_blocks(L, R, c, offset, block, B: list[Block]):
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


def expand_block(b, c_tilde, B: list[Block], offset):
    global lm
    global x

    for c in B[b].active:
        lm[c] = 0
    AC: set = B[b].active
    comp_dfdv(left(c_tilde), AC, None)
    v = comp_path(left(c_tilde), right(c_tilde), AC)
    ps = set()
    for c in AC:
        for j in range(len(v) - 1):
            if left(c) == v[j] and right(c) == v[j + 1]:
                ps.add(j)

    sc = min([lm[c] for c in ps])
    AC.remove(sc)

    for v in connected(right(c_tilde), AC):
        offset[v] += violation(c_tilde)
    B[b].active = AC.union(c_tilde)
    B[b].posn = sum([x[j] - offset[j] for j in B[b].vars]) / B[b].nvars


def comp_dfdv(v, AC, u):
    global x
    global lm

    dfdv = posn(v) - x[v]
    for c in AC:
        if not (v == left(c) and u != left(c)):
            continue
        lm[c] = -comp_dfdv(left(c), AC, v)
        dfdv -= lm[c]

    return dfdv


def split_blocks(x, B: list[Block], offset, block):
    global lm

    no_split = True
    for i in range(len(B)):
        if B[i].nvars == 0:
            continue

        B[i].posn = sum([x[j] - offset[j] for j in B[i].vars]) / B[i].nvars
        AC: set = B[i].active
        for c in AC:
            lm[c] = 0
        # random?
        v = B[i].vars.pop()
        B[i].vars.add(v)

        comp_dfdv(v, AC, None)
        sc = min([lm[c] for c in AC])
        if lm[sc] >= 0:
            break
        no_split = False
        AC.remove(sc)
        s = right(sc)
        B[s].vars = connected(s, AC)
        for v in B[s].vars:
            block[v] = s

        B[i].vars = B[i].vars.difference(B[s].vars)

        B[s].nvars = len(B[s].vars)
        B[i].nvars = len(B[i].vars)

        B[s].posn = sum([x[j] - offset[j] for j in B[s].vars]) / B[s].nvars
        B[i].posn = sum([x[j] - offset[j] for j in B[i].vars]) / B[i].nvars

        B[i].active = {c for c in AC if left(c) in B[s].vars and right(c) in B[s].vars}
        B[s].active = AC.difference(B[i].active)

    return no_split


def connected(s, AC):
    v = []
    for a, b, c in AC:
        if b == s:
            v.append(a)

    return v


def comp_path(left, right, AC):
    v = set()
    v.add(left)
    v.add(right)
    # left to right path nodes
    stack = [left]
    while len(stack) > 0:
        u = stack.pop()
        for vv, cost in graph[u]:
            if [u, vv, cost] not in AC:
                continue
            if vv in v:
                continue
            v.add(vv)
            stack.append(vv)

    return list(v)
