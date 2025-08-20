import math
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


def sgd(nx_graph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=2):
    parameter = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    dist_list = nx_graph.graph["distance"]
    diameter = nx.diameter(nx_graph)
    print(diameter)

    eggraph, indices = nxgraph_to_eggraph(nx_graph)
    distance = nx.floyd_warshall_numpy(nx_graph, weight=None)
    print(distance)
    dist = eg.DistanceMatrix(eggraph)
    for i, u in enumerate(nx_graph.nodes):
        for j, v in enumerate(nx_graph.nodes):
            dist.set(
                indices[u],
                indices[v],
                min(math.pi, math.log(distance[i][j]) if distance[i][j] != 0 else 0),
            )

    drawing = eg.DrawingHyperbolic2d.initial_placement(eggraph)
    sgd = eg.FullSgd.new_with_distance_matrix(dist)
    rng = eg.Rng.seed_from(parameter.seed)

    # size = []
    if overlap_removal:
        overlap = eg.OverwrapRemoval(eggraph, lambda node_index: 0.3)
        overlap.iterations = 5

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

    # pos = {u: [drawing.x(indices[u]), drawing.y(indices[u])] for u in nx_graph.nodes}

    positions = []
    circle_centers = []
    circle_radii = []

    for i in range(parameter.iter):
        print(f"iter:{i}")
        sgd_scheduler.step(step)

    # current_centers, current_radii = project_circle_constraints_hyper(
    #     drawing, circle_constraints, indices
    # )

    # circle_centers.append(current_centers)
    # circle_radii.append(current_radii)
    # pos = {
    #     u: [drawing.x(indices[u]), drawing.y(indices[u])] for u in nx_graph.nodes
    # }
    # positions.append(pos)

    pos = {
        u: [
            drawing.x(indices[u]),
            drawing.y(indices[u]),
        ]
        for u in nx_graph.nodes
    }
    return pos
