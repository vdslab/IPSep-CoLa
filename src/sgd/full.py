import traceback

import egraph as eg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from ipsep_cola import NodeBlocks, project, split_blocks
from ipsep_cola.constraint import Constraints, get_constraints_dict
from util.graph import nxgraph_to_eggraph
from util.parameter import SGDParameter


def sgd(nxgraph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=0):
    C = get_constraints_dict(nxgraph.graph["constraints"], default_gap=20)
    sgd_param = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    const_dist = {"x": None, "y": None, "sq": {"x": None, "y": None}}
    node_num = nxgraph.number_of_nodes()
    if C.get("y") is not None and len(C["y"]) > 0:
        const_dist["y"] = Constraints(C["y"], node_num)
    if C.get("x") is not None and len(C["x"]) > 0:
        const_dist["x"] = Constraints(C["x"], node_num)

    return __sgd(
        nxgraph,
        nxgraph.graph['distance'],
        const_dist,
        sgd_param,
    )


def __sgd(
    nx_graph: nx.Graph,
    dist_list,
    constraints: dict[str, Constraints],
    parameter: SGDParameter,
):
    eggraph, indices = nxgraph_to_eggraph(nx_graph)
    drawing = eg.DrawingEuclidean2d.initial_placement(eggraph)
    dist = eg.DistanceMatrix(eggraph)
    for i, u in enumerate(eggraph.node_indices()):
        for j, v in enumerate(eggraph.node_indices()):
            dist.set(u, v, dist_list[i][j])
    sgd = eg.FullSgd.new_with_distance_matrix(dist)
    rng = eg.Rng.seed_from(parameter.seed)

    def step(eta):
        try:
            sgd.shuffle(rng)
            sgd.apply(drawing, eta)
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
