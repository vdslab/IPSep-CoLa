import argparse
import glob
import itertools
import json
import math
import os

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from boxplot_2item import boxplot_2item_plot_only
from sgd.full import sgd as constrained_sgd
from sgd.projection.distance_constraints import hyperbolic_to_euclidean
from sgd.uniocon import sgd as uniocon_sgd


def calc_stress(graph, drawing):
    s = 0
    nodes = list(graph.nodes)
    for i, j in itertools.combinations(range(graph.number_of_nodes()), 2):
        d1 = graph.graph["distance"][i][j]
        pos_i = drawing[nodes[i]]
        pos_j = drawing[nodes[j]]
        d2 = math.hypot(pos_i[0] - pos_j[0], pos_i[1] - pos_j[1])
        s += ((d2 - d1) / d1) ** 2
    s /= len(nodes) * (len(nodes) - 1) // 2
    return s


def calc_violation(graph, drawing):
    ls = 0
    for constraint in graph.graph["constraints"]:
        u = constraint["left"]
        v = constraint["right"]
        gap = constraint["gap"]
        if constraint["axis"] == "x":
            ls += max(0, gap - (drawing[v][0] - drawing[u][0]))
        else:
            ls += max(0, gap - (drawing[v][1] - drawing[u][1]))
    ls /= len(graph.graph["constraints"])
    # ovs = 0
    # for constraint in graph.graph["distance_constraints"]:
    #     v, u, gap = constraint["left"], constraint["right"], constraint["gap"]
    #     dx = drawing[v][0] - drawing[u][0]
    #     dy = drawing[v][1] - drawing[u][1]
    #     dist = math.hypot(dx, dy)
    #     ovs += max(0, gap - dist)
    # ovs /= len(graph.graph["distance_constraints"])
    return ls  # + ovs


def poincare_distance(p1, p2):
    """
    ポアンカレ円板モデルにおける2点間の双曲距離を計算します。

    Args:
        p1 (tuple): 1点目の座標 (x, y)
        p2 (tuple): 2点目の座標 (x, y)

    Returns:
        float: 2点間の双曲距離
    """
    norm_p1_sq = p1[0] ** 2 + p1[1] ** 2
    norm_p2_sq = p2[0] ** 2 + p2[1] ** 2
    norm_diff_sq = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

    # ポアンカレ円板の境界上または外側にある場合のエラーハンドリング
    # 分母が0または負になるのを防ぎます
    denominator = (1 - norm_p1_sq) * (1 - norm_p2_sq)
    if denominator <= 1e-9:  # 浮動小数点誤差を考慮
        if norm_diff_sq < 1e-9:
            return 0.0
        # 実際には、drawingの結果が円盤内に収まっていることが期待されます
        return float("inf")

    # arccoshの引数が1未満にならないように補正します
    arg = 1 + 2 * norm_diff_sq / denominator
    if arg < 1:
        arg = 1

    return math.acosh(arg)


def calc_violation_hyperbolic(graph, drawing):
    """
    双曲空間の座標を前提としてviolationを計算します。
    """
    ls = 0
    # # layer_constraints は、ポアンカレ円板モデルの座標系でそのまま計算できると仮定します
    # if "layer_constraints" in graph.graph and graph.graph["layer_constraints"]:
    #     for constraint in graph.graph["layer_constraints"]:
    #         u = constraint["left"]
    #         v = constraint["right"]
    #         gap = constraint["gap"]
    #         if constraint["axis"] == "x":
    #             ls += max(0, gap - (drawing[v][0] - drawing[u][0]))
    #         else:
    #             ls += max(0, gap - (drawing[v][1] - drawing[u][1]))
    #     if len(graph.graph["layer_constraints"]) > 0:
    #         ls /= len(graph.graph["layer_constraints"])

    ovs = 0
    if "constraints" in graph.graph and graph.graph["constraints"]:
        for constraint in graph.graph["constraints"]:
            if constraint.get("axis", "") != "y":
                continue
            v, u, gap = constraint["left"], constraint["right"], constraint["gap"]
            pos_v = drawing[v]
            pos_u = drawing[u]
            # 双曲距離を計算
            dist = poincare_distance(pos_v, pos_u)
            ovs += max(0, gap - dist)
        if len(graph.graph["constraints"]) > 0:
            ovs /= len(graph.graph["constraints"])

    return ls + ovs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file")
    parser.add_argument("dest")
    parser.add_argument("--overlap-removal", action=argparse.BooleanOptionalAction)
    parser.add_argument("--iterations", type=int, default=30)
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    graph = nx.node_link_graph(json.load(open(args.graph_file)))
    constrained_sgd_stresses = []
    constrained_sgd_violations = []
    uniocon_sgd_stresses = []
    uniocon_sgd_violations = []
    for i in range(args.iterations):
        poscs = constrained_sgd(
            graph,
            seed=i,
            overlap_removal=args.overlap_removal,
        )
        scs = calc_stress(graph, poscs)
        vcs = calc_violation(graph, poscs)
        constrained_sgd_stresses.append(scs)
        constrained_sgd_violations.append(vcs)

        posu = uniocon_sgd(
            graph,
            seed=i,
            overlap_removal=args.overlap_removal,
        )
        su = calc_stress(graph, posu)
        vu = calc_violation(graph, posu)
        uniocon_sgd_stresses.append(su)
        uniocon_sgd_violations.append(vu)
        json.dump(
            {
                "seed": i,
                "iteration": args.iterations,
                "unicon": {"stress": su, "violation": vu, "drawing": posu},
                "constrained_sgd": {"stress": scs, "violation": vcs, "drawing": poscs},
            },
            open(f"{args.dest}/compare_seed{i}.json", "w"),
        )
        # print(f"{scs=} {vcs=} {su=} {vu=}")


if __name__ == "__main__":
    main()
