import networkx as nx
from numpy import argmax, argmin, ndarray

from .constraint import Constraints


def trim_group(
    group: list[dict[str, list[int]]],
) -> tuple[list[dict[str, list[int]]], list[dict[str]]]:
    gn = len(group)
    _group = [dict() for _ in range(gn)]
    for i in range(gn):
        # node contained group
        nodes = group[i].get("nodes", [])
        _group[i].setdefault("nodes", [dict() for _ in range(len(nodes))])
        for j, v in enumerate(nodes):
            _group[i]["nodes"][j] = dict()
            _group[i]["nodes"][j]["parent"] = group[i]
            _group[i]["nodes"][j]["node"] = v
        # group parent
        for childg in group[i].get("groups", []):
            _group[childg]["parent"] = group[i]

    root_group = {"nodes": [], "groups": []}
    for g in _group:
        for node in g.get("nodes", []):
            p = node.get("parent")
            if p is None:
                root_group["nodes"].append(node)

        gp = g.get("parent")
        if gp is None:
            root_group["groups"].append(gp)

    return group, root_group


def calc_group_min_max(group: dict[str], position1D: ndarray):
    node_index = []
    for node in group.get("nodes", []):
        v = node["node"]
        node_index.append(v)

    positions = list(enumerate(position1D))
    positions = list(filter(lambda x: x[0] in node_index, positions))
    mx_index = argmax(positions, axis=0)[1]
    mn_index = argmin(positions, axis=0)[1]
    return positions[mn_index], positions[mx_index]


def generate_group_constraints(
    cin_graph: list[list[tuple[int, int]]],
    axis: str,
    root_group: dict[str],
    position1D: ndarray,
    have_sub_group: bool = False,
    gap: int = 5,
) -> Constraints:
    """
    root_group: dict[str]
        - nodes: list[dict[str, dict]]
            - parent: parent group dict
            - node: node index
        - groups: list[dict]
            - list dict of sub group
        - parent?: int
            - parent group dict
    """
    group_constraints = []
    for g in root_group.get("group", []):
        group_constraints.extend(generate_group_constraints(g, position1D, True, gap))

    node_n = len(position1D)
    if have_sub_group:
        mn, mx = calc_group_min_max(root_group, position1D)
        group_constraints.append(
            {"axis": axis, "left": node_n, "right": mn[0], "gap": gap}
        )

        node_n += 1
        group_constraints.append(
            {"axis": axis, "left": mx[0], "right": node_n, "gap": gap}
        )
        node_n += 1

    for g in root_group.get("groups", []):
        pass
