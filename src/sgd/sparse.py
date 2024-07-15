import json
import os
import time
from logging import DEBUG, StreamHandler, getLogger, handlers

import egraph as eg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from ipsep_cola import NodeBlocks, project
from majorization.main import weights_of_normalization_constant
from util.constraint import Constraints, get_constraints_dict
from util.graph import get_graph_and_constraints, plot_graph

logger = getLogger(__name__)
handler = handlers.RotatingFileHandler("log1.log", maxBytes=100000)
handler.setLevel(DEBUG)

logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

logger.debug("hello")


def nxgraph_to_eggraph(graph: nx.Graph) -> tuple[eg.Graph, dict]:
    eggraph = eg.Graph()
    indices = {}
    for u in graph.nodes:
        indices[u] = eggraph.add_node(u)
    for u, v in graph.edges:
        eggraph.add_edge(indices[u], indices[v], (u, v))
    return eggraph, indices


def sparse_sgd_with_constraints(
    graph: eg.Graph,
    indices: dict,
    constraints: Constraints,
    *,
    edge_length: int,
    povot_count: int,
    iter_count: int,
    eps: float,
    seed: int = None,
) -> tuple[list[tuple[int, int]], float]:
    """
    # Returns
    pos: list[tuple[int, int]]
        - x, y

    stress: float
    """
    n = len(indices)

    drawing = eg.DrawingEuclidean2d.initial_placement(graph)
    rng = eg.Rng.seed_from(seed) if seed is not None else eg.Rng()
    d = eg.all_sources_dijkstra(graph, lambda _: edge_length)
    sgd = eg.FullSgd.new_with_distance_matrix(d)
    scheduler = sgd.scheduler(
        100,  # number of iterations
        eps,  # eps: eta_min = eps * min d[i, j] ^ 2
    )

    def apply_project():
        y = np.array([drawing.y(i) for i in range(n)])
        blocks = NodeBlocks(y)
        y = project(constraints, blocks)
        y = y.flatten()
        for i in range(n):
            drawing.set_y(i, y[i])

    def step(eta):
        sgd.shuffle(rng)
        sgd.apply(drawing, eta)

    for i in range(0, 100, 10):
        j = 100 - i
        for i in range(30):
            scheduler.step(step)
        # for i in range(15):
        #     apply_project()
        for i in range(70):
            scheduler.step(step)
            apply_project()

    # pos = {u: (drawing.x(i), drawing.y(i)) for u, i in indices.items()}
    pos = [(drawing.x(i), drawing.y(i)) for u, i in indices.items()]
    # print(eg.stress(drawing, d))
    return pos, drawing


def main():
    files = [
        "./src/data/json/download/no_cycle_tree.json",
        "./src/data/json/download/qh882.json",
        "./src/data/json/download/dwt_1005.json",
        "./src/data/json/download/1138_bus.json",
        "./src/data/json/download/dwt_2680.json",
        "./src/data/json/download/USpowerGrid.json",
        "./src/data/json/download/3elt.json",
    ]
    for file in files:
        basename = os.path.basename(file)
        print(basename)

        stresses = []
        try:
            with open(f"./src/data/SGD/sparse/{basename}", "r") as f:
                stresses = json.load(f)
        except Exception as e:
            print(e)
            print(file)

        if len(stresses) >= 20:
            continue

        nx_graph, constraints_data = get_graph_and_constraints(file)
        length = None
        with open(f"./src/data/json/dist/{basename}") as f:
            json_data = json.load(f)
            length = json_data["length"]

        C = get_constraints_dict(constraints_data, default_gap=20)
        constraints = Constraints(C["y"], nx_graph.number_of_nodes())
        eggraph, indices = nxgraph_to_eggraph(nx_graph)
        print("\t start dijkstra")
        d = eg.all_sources_dijkstra(eggraph, lambda _: length)

        for i in range(20):
            if len(stresses) >= 20:
                break

            print("\t", i)
            pos, drawing = sparse_sgd_with_constraints(
                eggraph,
                indices,
                constraints,
                edge_length=length,
                povot_count=50,
                iter_count=100,
                eps=0.1,
            )

            stresses.append(eg.stress(drawing, d))
            plot_graph(nx_graph, pos, f"./src/data/SGD/sparse/{basename}_{i}.png")
            with open(f"./src/data/SGD/sparse/{basename}", "w") as f:
                json.dump(stresses, f, indent=2)
        print(stresses)


if __name__ == "__main__":
    main()
