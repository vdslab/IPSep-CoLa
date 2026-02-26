import traceback

import egraph as eg

from util.graph import nxgraph_to_eggraph
from util.parameter import SGDParameter

from .projection.circle_constraints import (
    project_circle_constraints,
    project_circle_constraints_hyper,
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
    drawing = eg.DrawingEuclidean2d.initial_placement(eggraph)
    # drawing = eg.DrawingHyperbolic2d.initial_placement(eggraph)
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
    circle_constraints = [
        [
            [indices[v] for v in c["nodes"]],
            c["r"],
            indices[c["center"]] if c.get("center") is not None else None,
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

    for i in range(parameter.iter):
        print(f"iter:{i}")
        sgd_scheduler.step(step)
        # if overlap_removal:
        #     overlap.apply_with_drawing_euclidean_2d(drawing)
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
        project_circle_constraints(drawing, circle_constraints, indices)
        # project_circle_constraints_hyper(drawing, circle_constraints, indices)

        # eg.project_1d(drawing, 0, x_constraints)
        # eg.project_1d(drawing, 1, y_constraints)

    pos = {
        u: [
            drawing.x(indices[u]),
            drawing.y(indices[u]),
        ]
        for u in nx_graph.nodes
    }
    return pos
