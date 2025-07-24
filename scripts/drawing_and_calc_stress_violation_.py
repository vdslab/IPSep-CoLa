import argparse
import glob
import itertools
import json
import math
import os

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx

from boxplot_2item import boxplot_2item_plot_only
from sgd.full import sgd as constrained_sgd
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
    for constraint in graph.graph["layer_constraints"]:
        u = constraint["left"]
        v = constraint["right"]
        gap = constraint["gap"]
        if constraint["axis"] == "x":
            ls += max(0, gap - (drawing[v][0] - drawing[u][0]))
        else:
            ls += max(0, gap - (drawing[v][1] - drawing[u][1]))
    ls /= len(graph.graph["layer_constraints"])
    ovs = 0
    for constraint in graph.graph["distance_constraints"]:
        v, u, gap = constraint["left"], constraint["right"], constraint["gap"]
        dx = drawing[v][0] - drawing[u][0]
        dy = drawing[v][1] - drawing[u][1]
        dist = math.hypot(dx, dy)
        ovs += max(0, gap - dist)
    ovs /= len(graph.graph["distance_constraints"])
    return ls + ovs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file")
    parser.add_argument("out_json")
    parser.add_argument("--iterations", type=int, default=30)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    graph = nx.node_link_graph(json.load(open(args.graph_file)))
    constrained_sgd_stresses = []
    constrained_sgd_violations = []
    uniocon_sgd_stresses = []
    uniocon_sgd_violations = []
    for i in range(args.iterations):
        poscs = constrained_sgd(graph, seed=i)
        scs = calc_stress(graph, poscs)
        vcs = calc_violation(graph, poscs)
        constrained_sgd_stresses.append(scs)
        constrained_sgd_violations.append(vcs)

        posu = uniocon_sgd(graph, seed=i)
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
            open(f"dest/compare/y-layer/compare_seed{i}.json", "w"),
        )
        print(f"{scs=} {vcs=} {su=} {vu=}")

if __name__ == "__main__":
    main()
