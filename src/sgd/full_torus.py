import traceback

import egraph as eg
import networkx as nx

from util.graph import nxgraph_to_eggraph
from util.parameter import SGDParameter

from .torus_util import torus_position_to_euclid


def sgd(nx_graph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=0):
    parameter = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    dist_list = nx_graph.graph["distance"]
    diameter = nx.diameter(nx_graph)
    cell_size = 1
    div = diameter * cell_size

    eggraph, indices = nxgraph_to_eggraph(nx_graph)
    dist = eg.DistanceMatrix(eggraph)
    for i, u in enumerate(nx_graph.nodes):
        for j, v in enumerate(nx_graph.nodes):
            dist.set(indices[u], indices[v], dist_list[j][i] / diameter)

    drawing = eg.DrawingTorus2d.initial_placement(eggraph)
    sgd = eg.FullSgd.new_with_distance_matrix(dist)
    rng = eg.Rng.seed_from(parameter.seed)

    # size = []
    if overlap_removal:
        overlap = eg.OverwrapRemoval(eggraph, lambda node_index: 0.3 / diameter)
        overlap.iterations = 5

    x_constraints = [
        eg.Constraint(indices[c["left"]], indices[c["right"]], c["gap"] / diameter)
        for c in nx_graph.graph["constraints"]
        if c.get("axis", "") == "x"
    ]
    y_constraints = [
        eg.Constraint(indices[c["left"]], indices[c["right"]], c["gap"] / diameter)
        for c in nx_graph.graph["constraints"]
        if c.get("axis", "") == "y"
    ]
    print(
        [
            c["gap"] / div
            for c in nx_graph.graph["constraints"]
            if c.get("axis", "") == "y"
        ]
    )

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

        xs, ys = torus_position_to_euclid(drawing, nx_graph, indices)
        drawingEuc = eg.DrawingEuclidean2d.initial_placement(eggraph)

        for i in range(drawing.len()):
            drawingEuc.set_x(i, xs[i])
            drawingEuc.set_y(i, ys[i])
        if overlap_removal:
            overlap.apply_with_drawing_euclidean_2d(drawingEuc)
        eg.project_1d(drawingEuc, 0, x_constraints)
        eg.project_1d(drawingEuc, 1, y_constraints)
        for i in range(drawing.len()):
            drawing.set_x(i, drawingEuc.x(i))
            drawing.set_y(i, drawingEuc.y(i))

    # import math
    pos = {
        u: [
            drawingEuc.x(indices[u]),
            drawingEuc.y(indices[u]),
        ]
        for u in nx_graph.nodes
    }
    return pos
