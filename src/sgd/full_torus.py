import sys
import traceback

import egraph as eg
import networkx as nx

from util.graph import nxgraph_to_eggraph
from util.parameter import SGDParameter

from .projection.circle_constraints import (
    project_circle_constraints,
    project_circle_constraints_hyper,
)
from .torus_util import torus_position_to_euclid

# TODO：道路


def sgd(nx_graph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=0):
    parameter = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    dist_list = nx_graph.graph["distance"]
    diameter = nx.diameter(nx_graph)
    print(diameter)

    eggraph, indices = nxgraph_to_eggraph(nx_graph)
    dist = eg.DistanceMatrix(eggraph)
    for i, u in enumerate(nx_graph.nodes):
        for j, v in enumerate(nx_graph.nodes):
            dist.set(indices[u], indices[v], float(dist_list[j][i]) / diameter / 100.0)

    drawing = eg.DrawingTorus2d.initial_placement(eggraph)
    sgd = eg.FullSgd.new_with_distance_matrix(dist)
    rng = eg.Rng.seed_from(parameter.seed)

    # size = []
    if overlap_removal:
        overlap = eg.OverwrapRemoval(eggraph, lambda node_index: 0.06)
        overlap.iterations = 5

    # x_constraints = [
    #     eg.Constraint(indices[c["left"]], indices[c["right"]], c["gap"] / diameter)
    #     for c in nx_graph.graph["constraints"]
    #     if c.get("axis", "") == "x"
    # ]
    # y_constraints = [
    #     eg.Constraint(indices[c["left"]], indices[c["right"]], c["gap"] / diameter)
    #     for c in nx_graph.graph["constraints"]
    #     if c.get("axis", "") == "y"
    # ]
    # circle_constraints = [
    #     [
    #         [indices[v] for v in c["nodes"]],
    #         c["r"] / diameter,
    #         indices[c["center"]] if c.get("center") is not None else None,
    #     ]
    #     for c in nx_graph.graph["constraints"]
    #     if c.get("type", "") == "circle"
    # ]
    # print(circle_constraints)
    # alignment_x_constraint = [
    #     list(sorted([indices[v] for v in c["nodes"]], key=lambda x: x))
    #     for c in nx_graph.graph["constraints"]
    #     if c.get("type", "") == "alignment" and c.get("axis", "") == "x"
    # ]
    # alignment_y_constraint = [
    #     list(sorted([indices[v] for v in c["nodes"]], key=lambda x: x))
    #     for c in nx_graph.graph["constraints"]
    #     if c.get("type", "") == "alignment" and c.get("axis", "") == "y"
    # ]

    def step(eta):
        try:
            sgd.shuffle(rng)
            sgd.apply(drawing, eta)
        except Exception:
            traceback.print_exc()

    sgd_scheduler = sgd.scheduler(
        parameter.iter,  # number of iterations
        parameter.eps,  # eps: eta_min = eps * min d[i, j] ^ 2
    )

    for i in range(parameter.iter):
        sys.stdout.flush()
        sys.stdout.write(f"\r\033[2Kiter:{i} / {parameter.iter}")
        # sgd
        sgd_scheduler.step(step)
        if overlap_removal:
            overlap.apply_with_drawing_torus_2d(drawing)
        # project
        # xs, ys = torus_position_to_euclid(drawing, nx_graph, indices)
        # for j in range(drawing.len()):
        #     drawingEuc.set_x(j, xs[j])
        #     drawingEuc.set_y(j, ys[j])

        # for nodes in alignment_x_constraint:
        #     for v in nodes[1:]:
        #         drawingEuc.set_y(v, ys[nodes[0]])
        # for nodes in alignment_y_constraint:
        #     for v in nodes[1:]:
        #         drawingEuc.set_x(v, xs[nodes[0]])

        # project_circle_constraints(drawingEuc, circle_constraints, indices)
        # # eg.project_1d(drawingEuc, 0, x_constraints)
        # # eg.project_1d(drawingEuc, 1, y_constraints)

        # for j in range(drawing.len()):
        #     drawing.set_x(j, drawingEuc.x(j))
        #     drawing.set_y(j, drawingEuc.y(j))

    # import math
    pos = {
        u: [
            drawing.x(indices[u]),
            drawing.y(indices[u]),
        ]
        for u in nx_graph.nodes
    }
    return pos
