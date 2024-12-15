import random
import traceback

import egraph as eg
import numpy as np

from ipsep_cola import NodeBlocks, project, split_blocks
from ipsep_cola.constraint import Constraints, get_constraints_dict
from ipsep_cola.constraint.overlap_removal import \
    generate_overlap_removal_constraints
from util.graph import nxgraph_to_eggraph
from util.parameter import SGDParameter


def sgd(nx_graph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=0):
    parameter = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    node_num = nx_graph.number_of_nodes()
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
            size.append([shape['width'] + 10, shape['height'] + 10])

    def step(eta):
        try:
            sgd.shuffle(rng)
            sgd.apply(drawing, eta)

            C = get_constraints_dict(nx_graph.graph["constraints"],
                                     default_gap=20)
            if overlap_removal:
                for axis, item in generate_overlap_removal_constraints(drawing, size,
                                                                       'y' if random.random() < 0.5 else 'x'):
                    C[axis].append(item)

            constraints = {"x": None, "y": None,
                           "sq": {"x": None, "y": None}}
            if C.get("y") is not None and len(C["y"]) > 0:
                constraints["y"] = Constraints(C["y"], node_num)
            if C.get("x") is not None and len(C["x"]) > 0:
                constraints["x"] = Constraints(C["x"], node_num)

            project_each_axis(drawing, constraints)
        except Exception:
            traceback.print_exc()

    sgd_scheduler = sgd.scheduler(
        parameter.iter,  # number of iterations
        parameter.eps,  # eps: eta_min = eps * min d[i, j] ^ 2
    )
    sgd_scheduler.run(step)

    pos = {u: [drawing.x(indices[u]), drawing.y(indices[u])]
           for u in nx_graph.nodes}
    return pos


def project_each_axis(drawing, constraints):
    n = drawing.len()
    for key in ['x', 'y']:
        if constraints[key] is None or len(constraints[key].constraints) == 0:
            continue
        x = np.array([drawing.x(i) if key == 'x' else drawing.y(i)
                     for i in range(n)])
        block = NodeBlocks(x, x)
        while not split_blocks(x, constraints[key], block):
            pass
        new_x = project(constraints[key], block)
        for i in range(n):
            if key == 'x':
                drawing.set_x(i, new_x[i])
            else:
                drawing.set_y(i, new_x[i])
