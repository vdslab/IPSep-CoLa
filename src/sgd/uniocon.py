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


def print_progress_bar(iteration, total, bar_length=40):
    progress = (iteration + 1) / total
    block = int(round(bar_length * progress))
    text = "\rProgress: [{0}] {1}%".format(
        "#" * block + "-" * (bar_length - block), int(progress * 100)
    )
    print(text, end="")


def sgd(nx_graph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=0):
    parameter = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    dist_list = nx_graph.graph["distance"]
    # print(nx_graph)

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
        shape = nx_graph.nodes[list(nx_graph.nodes)[0]]["shape"]
        overlap = eg.OverwrapRemoval(eggraph, lambda node_index: 50)
        overlap.iterations = 1
        overlap.strength = 2

        for i, u in enumerate(nx_graph.nodes):
            shape = nx_graph.nodes[u]["shape"]
            size.append([shape["width"], shape["height"]])

    # 制約の種類ごとに分割
    x_constraints: list = [
        eg.Constraint(indices[str(c["left"])], indices[str(c["right"])], c["gap"])
        for c in nx_graph.graph["constraints"]
        if c.get("axis", "") == "x"
    ]
    y_constraints: list = [
        eg.Constraint(indices[str(c["left"])], indices[str(c["right"])], c["gap"])
        for c in nx_graph.graph["constraints"]
        if c.get("axis", "") == "y"
    ]

    # distance_constraints = [
    #     (indices[c["left"]], indices[c["right"]], c["gap"])
    #     for c in nx_graph.graph["distance_constraints"]
    #     if c.get("type", "") == "distance"
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
        print_progress_bar(i, parameter.iter)
        sgd_scheduler.step(step)
        if overlap_removal:
            # overlap.apply_with_drawing_euclidean_2d(drawing)
            eg.project_rectangle_no_overlap_constraints_2d(
                drawing, lambda u, d: size[u][d]
            )
        for constraint in x_constraints:
            eg.project_1d(drawing, 0, [constraint])
        for constraint in y_constraints:
            eg.project_1d(drawing, 1, [constraint])

    pos = {u: [drawing.x(indices[u]), drawing.y(indices[u])] for u in nx_graph.nodes}
    return pos
