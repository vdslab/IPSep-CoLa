import random
import traceback

import egraph as eg

from util.graph import nxgraph_to_eggraph
from util.parameter import SGDParameter


def sgd(nx_graph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=0):
    parameter = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    dist_list = nx_graph.graph['distance']

    eggraph, indices = nxgraph_to_eggraph(nx_graph)
    dist = eg.DistanceMatrix(eggraph)
    for i, u in enumerate(nx_graph.nodes):
        for j, v in enumerate(nx_graph.nodes):
            dist.set(indices[u], indices[v], dist_list[j][i])

    drawing = eg.ClassicalMds.new_with_distance_matrix(dist).run_2d()
    sgd = eg.FullSgd.new_with_distance_matrix(dist)
    rng = eg.Rng.seed_from(parameter.seed)

    size = []
    if overlap_removal:
        for i, u in enumerate(nx_graph.nodes):
            shape = nx_graph.nodes[u]['shape']
            size.append([shape['width'] + 5, shape['height'] + 5])

    x_constraints = [eg.Constraint(c['left'], c['right'], c['gap'])
                     for c in nx_graph.graph['constraints']
                     if c['axis'] == 'x']
    y_constraints = [eg.Constraint(c['left'], c['right'], c['gap'])
                     for c in nx_graph.graph['constraints']
                     if c['axis'] == 'y']

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
        sgd_scheduler.step(step)
        eg.project_1d(drawing, 0, x_constraints)
        eg.project_1d(drawing, 1, y_constraints)
        if overlap_removal:
            eg.project_rectangle_no_overlap_constraints_2d(
                drawing, lambda u, d: size[u][d])
        if clusters is not None:
            eg.project_clustered_rectangle_no_overlap_constraints(
                eggraph,
                drawing,
                lambda u: clusters[u],
                lambda u, d: size[u][d],
            )

    pos = {u: [drawing.x(indices[u]), drawing.y(indices[u])]
           for u in nx_graph.nodes}
    return pos
