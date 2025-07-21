import random
import traceback

import egraph as eg
import networkx as nx
from networkx import all_pairs_dijkstra_path_length

from util.graph import nxgraph_to_eggraph
from util.graph.save_animation import save_animation
from util.parameter import SGDParameter

from .projection.circle_constraints import project_circle_constraints
from .projection.distance_constraints import project_distance_constraints


def sgd(nx_graph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=0):
    parameter = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    dist_list = nx_graph.graph["distance"]
    print(nx_graph)

    eggraph, indices = nxgraph_to_eggraph(nx_graph)
    dist = eg.DistanceMatrix(eggraph)
    for i, u in enumerate(nx_graph.nodes):
        for j, v in enumerate(nx_graph.nodes):
            dist.set(indices[u], indices[v], dist_list[j][i])

    drawing = eg.ClassicalMds.new_with_distance_matrix(dist).run_2d()
    drawing = eg.DrawingEuclidean2d.initial_placement(eggraph)
    sgd = eg.FullSgd.new_with_distance_matrix(dist)
    rng = eg.Rng.seed_from(parameter.seed)

    size = []
    if overlap_removal:
        for i, u in enumerate(nx_graph.nodes):
            shape = nx_graph.nodes[u]["shape"]
            size.append([shape["width"] + 5, shape["height"] + 5])

    # 制約の種類ごとに分割
    x_constraints: list = [
        eg.Constraint(indices[c["left"]], indices[c["right"]], c["gap"])
        for c in nx_graph.graph["layer_constraints"]
        if c.get("axis", "") == "x"
    ]
    y_constraints: list = [
        eg.Constraint(indices[c["left"]], indices[c["right"]], c["gap"])
        for c in nx_graph.graph["layer_constraints"]
        if c.get("axis", "") == "y"
    ]

    overlap_constraints = [
        (indices[c["left"]], indices[c["right"]], c["gap"])
        for c in nx_graph.graph["overlap_constraints"]
        if c.get("type", "") == "overlap"
    ]

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
        print(f"iter:{i}")
        sgd_scheduler.step(step)
        # for constraint in x_constraints:
        #     eg.project_1d(drawing, 0, [constraint])
        # for constraint in y_constraints:
        #     eg.project_1d(drawing, 1, [constraint])
        for constraint in overlap_constraints:
            project_distance_constraints(drawing, [constraint], indices)

    pos = {u: [drawing.x(indices[u]), drawing.y(indices[u])] for u in nx_graph.nodes}
    return pos
