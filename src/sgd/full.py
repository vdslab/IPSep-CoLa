import random
import traceback

import egraph as eg
import networkx as nx
from networkx import all_pairs_dijkstra_path_length

from util.graph import nxgraph_to_eggraph
from util.graph.save_animation import save_animation
from util.parameter import SGDParameter

from .projection.circle_constraints import (
    project_circle_constraints,
    project_circle_constraints_hyper,
)
from .projection.distance_constraints import (
    place_node_below_in_hyperbolic,
    project_distance_constraints,
    project_distance_constraints_hyperbolic,
    translate_hyperbolic_space,
)


def sgd(nx_graph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=0):
    parameter = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    dist_list = nx_graph.graph["distance"]

    eggraph, indices = nxgraph_to_eggraph(nx_graph)
    dist = eg.DistanceMatrix(eggraph)
    for i, u in enumerate(nx_graph.nodes):
        for j, v in enumerate(nx_graph.nodes):
            dist.set(indices[u], indices[v], dist_list[j][i])

    # drawing = eg.ClassicalMds.new_with_distance_matrix(dist).run_2d()
    # drawing = eg.DrawingEuclidean2d.initial_placement(eggraph)
    drawing = eg.DrawingHyperbolic2d.initial_placement(eggraph)
    sgd = eg.FullSgd.new_with_distance_matrix(dist)
    rng = eg.Rng.seed_from(parameter.seed)

    # size = []
    if overlap_removal:
        overlap = eg.OverwrapRemoval(eggraph, lambda node_index: 0.3)
        overlap.iterations = 5
        # for i, u in enumerate(nx_graph.nodes):
        #     shape = nx_graph.nodes[u]["shape"]
        #     size.append([shape["width"] + 5, shape["height"] + 5])
        #     shape = nx_graph.nodes[u]["shape"]
        #     size.append([shape["width"] + 5, shape["height"] + 5])

    x_constraints = [
        eg.Constraint(indices[c["left"]], indices[c["right"]], c["gap"])
        for c in nx_graph.graph["constraints"]
        if c.get("axis", "") == "x"
    ]
    y_constraints = [
        eg.Constraint(indices[c["left"]], indices[c["right"]], c["gap"])
        for c in nx_graph.graph["constraints"]
        if c.get("axis", "") == "y"
    ]

    # distance_constraints = [
    #     (indices[c["left"]], indices[c["right"]], c["gap"])
    #     for c in nx_graph.graph["distance_constraints"]
    # ]
    distance_constraints = [
        (indices[c["left"]], indices[c["right"]], c["gap"])
        for c in nx_graph.graph["constraints"]
        if c.get("axis", "") == "y"
    ]
    print(len(distance_constraints))
    circle_constraints = [
        [
            [indices[v] for v in c["nodes"]],
            c["r"],
            indices[c["center"]] if c["center"] is not None else None,
        ]
        for c in nx_graph.graph["constraints"]
        if c.get("type", "") == "circle"
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

    # pos = {u: [drawing.x(indices[u]), drawing.y(indices[u])] for u in nx_graph.nodes}

    positions = []
    circle_centers = []
    circle_radii = []
    degree = [(node, len(list(nx_graph.neighbors(node)))) for node in nx_graph.nodes]
    deg_max = max([m[1] for m in degree])
    deg_index = [m[1] for m in degree].index(deg_max)
    deg_max_node = list(nx_graph.nodes)[deg_index]
    deg_max_idx = indices[deg_max_node]
    for i in range(parameter.iter):
        print(f"iter:{i}")
        sgd_scheduler.step(step)
        if overlap_removal:
            overlap.apply_with_drawing_euclidean_2d(drawing)
            # eg.project_rectangle_no_overlap_constraints_2d(
            #     drawing, lambda u, d: size[u][d]
            # )
            # if clusters is not None:
            #     eg.project_clustered_rectangle_no_overlap_constraints(
            #         eggraph,
            #         drawing,
            #         lambda u: clusters[u],
            #         lambda u, d: size[u][d],
            #     )

        import numpy as np

        all_coods = np.array(
            [[drawing.x(i), drawing.y(i)] for i in range(drawing.len())]
        )

        coods = translate_hyperbolic_space(
            all_coods, np.array([drawing.x(deg_max_idx), drawing.y(deg_max_idx)])
        )
        for i in range(drawing.len()):
            drawing.set_x(i, coods[i][0])
            drawing.set_y(i, coods[i][1])

        # project_distance_constraints_hyperbolic(drawing, distance_constraints, indices)
        # place_node_below_in_hyperbolic(
        #     drawing,
        #     distance_constraints,
        # )
        # eg.project_1d(drawing, 0, x_constraints)
        # eg.project_1d(drawing, 1, y_constraints)

        project_circle_constraints_hyper(drawing, circle_constraints, indices)
        # circle_centers.append(current_centers)
        # circle_radii.append(current_radii)

        # pos = {
        #     u: [drawing.x(indices[u]), drawing.y(indices[u])] for u in nx_graph.nodes
        # }
        # positions.append(pos)
    # save_animation(
    #     "sgd_animation.gif", nx_graph, positions, circle_centers, circle_radii
    # )

    # import math

    pos = {
        u: [
            drawing.x(indices[u]),
            drawing.y(indices[u]),
        ]
        for u in nx_graph.nodes
    }
    return pos
