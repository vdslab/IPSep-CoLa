from collections import deque

import networkx as nx


def _depth(tree: nx.Graph, start: int, visited: set, d: int, dpth: dict) -> int:
    go_cnt = 0
    dmx = 0
    for u in tree.neighbors(start):
        if u in visited:
            continue
        visited.add(u)
        dd = _depth(tree, u, visited, d, dpth)
        dmx = max(dmx, dd)
        go_cnt += 1

    dpth[start] = dmx
    return dmx + 1


def depth(tree: nx.Graph, start: int):
    visited = set()
    dpth = {start: 0}
    visited.add(start)
    _depth(tree, start, visited, 0, dpth)
    return dpth


def dfs_path(
    tree: nx.Graph, start: int, path: list, visited: set, commit_tree: list, dpth: dict
):
    go_cnt = 0
    neighbors = list(tree.neighbors(start))
    neighbors.sort(key=lambda x: (dpth[x], -x), reverse=True)
    for u in neighbors:
        if u in visited:
            continue
        go_cnt += 1
        visited.add(u)
        path.append(u)
        path = dfs_path(tree, u, path, visited, commit_tree, dpth)
    if go_cnt == 0:
        commit_tree.append(path[::])
        path = []
    return path


def github_commit_tree(tree: nx.Graph, start: int):
    visited = set()
    path = [start]
    commit_tree = []
    visited.add(start)
    dpth = depth(tree, start)
    dfs_path(tree, start, path, visited, commit_tree, dpth)
    return [t for t in commit_tree if len(t) > 1]


def get_max_depth(nodes: list[int], dpth: dict) -> int:
    mxkey = 0
    mxval = 0
    for node in nodes:
        if dpth[node] > mxval:
            mxval = dpth[node]
            mxkey = node
    return mxkey


def test_github_commit_tree():
    graph = nx.Graph()
    graph.add_edges_from(
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (1, 4),
            (3, 5),
            (5, 6),
            (5, 7),
            (4, 9),
            (9, 8),
            (8, 10),
        ]
    )
    t = github_commit_tree(graph, 0)
    print(t)
    assert t == [[0, 1, 4, 9, 8, 10], [3, 5, 6]]


def test_depth():
    graph = nx.Graph()
    graph.add_edges_from(
        [
            (0, 1),
            (0, 2),
            (1, 3),
            (1, 4),
            (3, 5),
            (5, 6),
            (5, 7),
            (4, 9),
            (9, 8),
            (8, 10),
        ]
    )
    d = depth(graph, 0)
    assert d == {6: 0, 7: 0, 5: 1, 3: 2, 1: 4, 4: 3, 9: 2, 8: 1, 10: 0, 2: 0, 0: 5}


def test_get_max_depth():
    d = {6: 0, 7: 0, 5: 1, 3: 2, 1: 4, 4: 3, 9: 2, 8: 1, 10: 0, 2: 0, 0: 5}
    nodes = [1, 2]
    assert get_max_depth(nodes, d) == 1


if __name__ == "__main__":
    test_github_commit_tree()
    # test_depth()
    # test_get_max_depth()
