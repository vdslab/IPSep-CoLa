import datetime
import json
import os
import time
from logging import DEBUG, StreamHandler, getLogger, handlers

import egraph as eg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from ipsep_cola import NodeBlocks, project, split_blocks
from majorization.main import weight_laplacian, weights_of_normalization_constant
from util.constraint import Constraints, get_constraints_dict
from util.graph import get_graph_and_constraints, nxgraph_to_eggraph, plot_graph

logger = getLogger(__name__)
handler = handlers.RotatingFileHandler("log1.log", maxBytes=100000)
handler.setLevel(DEBUG)

logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

logger.debug("hello")

dtoday = datetime.date.today()
now = datetime.datetime.now().time()
save_dir = f"./result/SGD/sparse/{dtoday}/{now}"
fullsgd_save_dir = f"./src/data/SGD/full/{dtoday}/{now}"
os.makedirs(save_dir, exist_ok=True)
os.makedirs(fullsgd_save_dir, exist_ok=True)


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
    name: str = "graph",
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
    ds = np.array([[d.get(i, j) for j in range(n)] for i in range(n)])
    ds = ds.flatten()
    ds = ds[ds != 0]
    d_min = np.min(ds)
    d_max = np.max(ds)
    # dist = np.array([[d.get(i,j) for j in range(n)] for i in range(n)])
    # w = weights_of_normalization_constant(alpha=2, dist=dist)
    # Lw = weight_laplacian(w)
    # _b = np.ones(n)
    # _b = _b.reshape(-1, 1)
    sgd = eg.FullSgd.new_with_distance_matrix(d)

    stresses: dict[list] = {}
    for _ in range(50):
        for it in range(10, 61, 5):
            iitt = 10
            scheduler = sgd.scheduler(
                iitt,  # number of iterations
                eps,  # eps: eta_min = eps * min d[i, j] ^ 2
            )

            def step(eta):
                sgd.shuffle(rng)
                sgd.apply(drawing, eta)

            for _ in range(iitt):
                scheduler.step(step)

            eta_max = 1 / (d_max**2)
            eta_min = eps / (d_min**2)
            b = 1 / (it - 1) * np.log(eta_min / eta_max)

            def apply_project(j):
                nonlocal it
                _y = np.array([drawing.y(i) for i in range(n)])
                # y_hat = _y.copy()
                # y_hat = y_hat.reshape(-1, 1)
                # g = Lw @ y_hat + _b

                blocks = NodeBlocks(_y)
                y = project(constraints, blocks)
                # d = y - y_hat
                # divede = d.T @ Lw @ d
                # alpha = max(g.T @ d / divede, 1) if divede > 1e-6 else 1
                # y = y_hat + alpha * d
                y = y.flatten()

                eta = eta_max * np.exp(b * j)
                # print((eta-eta_min)/(eta_max-eta_min))
                d = y - _y
                y = _y + d * (1 + (eta - eta_min) / (eta_max - eta_min))

                for i in range(n):
                    drawing.set_y(i, y[i])

            scheduler = sgd.scheduler(
                it,  # number of iterations
                eps,  # eps: eta_min = eps * min d[i, j] ^ 2
            )
            for j in range(it):
                scheduler.step(step)
                apply_project(j)

            stresses.setdefault((iitt, it), []).append(eg.stress(drawing, d))

    fig = plt.figure(figsize=(20, 15), facecolor="lightblue")
    boxitem_st = []
    boxitem_la = []
    for ij, st in stresses.items():
        if 0 in ij:
            continue
        boxitem_st.append(st)
        boxitem_la.append(f"SGD{ij[0]}_project{ij[1]}")

    with open("src/data/cola/stress/no_cycle_tree.json") as f:
        s = json.load(f)
        boxitem_st.append(s)
        boxitem_la.append("webcola stress")

    plt.boxplot(boxitem_st, labels=boxitem_la)
    plt.title("SGD_project_stress")
    plt.ylabel("stress")
    plt.legend()
    # plt.xlim(right=150)
    # plt.ylim(270, 300)
    # plt.axvline(i - 1, 0, 1, color="g", alpha=0.5, label="finish SGD", linestyle=":")
    plt.savefig(f"{save_dir}/SGD_project_{name}.png")
    plt.close()
    # pos = {u: (drawing.x(i), drawing.y(i)) for u, i in indices.items()}
    pos = [(drawing.x(i), drawing.y(i)) for u, i in indices.items()]
    # print(eg.stress(drawing, d))
    return pos, drawing


def full_sgd_with_constraints(
    graph: eg.Graph,
    indices: dict,
    constraints: Constraints,
    *,
    edge_length: int,
    sgd_iter: int,
    project_iter: int,
    eps: float,
    seed: int = None,
    name: str = "graph",
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
    ds = np.array([[d.get(i, j) for j in range(n)] for i in range(n)])
    ds = ds.flatten()
    ds = ds[ds != 0]
    d_min = np.min(ds)
    d_max = np.max(ds)
    sgd = eg.FullSgd.new_with_distance_matrix(d)
    dist = np.array([[d.get(i, j) for j in range(n)] for i in range(n)])
    w = weights_of_normalization_constant(alpha=2, dist=dist)
    Lw = weight_laplacian(w)
    _b = np.ones(n)
    _b = _b.reshape(-1, 1)

    def step(eta):
        sgd.shuffle(rng)
        sgd.apply(drawing, eta)

    eta_max = 1 / (d_max**2)
    eta_min = eps / (d_min**2)
    b = 1 / (project_iter - 1) * np.log(eta_min / eta_max)

    def apply_project(j):
        _y = np.array([drawing.y(i) for i in range(n)])
        y = _y.copy()
        # y = y.reshape(-1,1)
        # g = Lw @ y + _b

        blocks = NodeBlocks(_y)
        y_bar = project(constraints, blocks)
        y_bar = y_bar.flatten()

        d = y_bar - y
        # divede = d.T @ Lw @ d
        # alpha = max(((g.T @ d)[0][0] / divede[0][0]), 1) if divede[0][0] > 1e-6 else 0
        # y = y_hat + alpha * d
        eta = eta_max * np.exp(b * j)
        # d = y - _y
        y = _y + d * (1 + (eta - eta_min) / (eta_max - eta_min))

        y = y.flatten()

        for i in range(n):
            drawing.set_y(i, y[i])

    schedulers = [
        ["exp", sgd.scheduler],
        # ["linear", sgd.scheduler_linear],
        # ["constant", sgd.scheduler_constant],
        # ["quadratic", sgd.scheduler_quadratic],
        # ["reciprocal", sgd.scheduler_reciprocal],
    ]
    stresses: dict[list] = {}
    for scheduler_name, scheduler in schedulers:
        for _ in range(50):
            for it in range(10, 31, 10):
                sgd_iter = 100 - it
                project_iter = it

                sgd_scheduler = scheduler(
                    sgd_iter,  # number of iterations
                    eps,  # eps: eta_min = eps * min d[i, j] ^ 2
                )
                project_scheduler = scheduler(
                    project_iter,  # number of iterations
                    eps,  # eps: eta_min = eps * min d[i, j] ^ 2
                )
                sgd_scheduler.run(step)

                # _y = np.array([drawing.y(i) for i in range(n)])
                # blocks = NodeBlocks(_y)
                for j in range(project_iter):
                    project_scheduler.step(step)
                    apply_project(j)

                stresses.setdefault((sgd_iter, project_iter), []).append(
                    eg.stress(drawing, d)
                )

        fig = plt.figure(figsize=(20, 15), facecolor="lightblue")
        boxitem_st = []
        boxitem_la = []
        for ij, st in stresses.items():
            if 0 in ij:
                continue
            boxitem_st.append(st)
            boxitem_la.append(f"SGD{ij[0]}_project{ij[1]}")

        with open("src/data/cola/stress/qh882.json") as f:
            s = json.load(f)
            boxitem_st.append(s)
            boxitem_la.append("webcola stress")

        plt.boxplot(boxitem_st, labels=boxitem_la)
        plt.title(f"SGD_project_stress {scheduler_name}")
        plt.ylabel("stress")
        plt.legend()
        # plt.xlim(right=150)
        # plt.ylim(270, 300)
        # plt.axvline(i - 1, 0, 1, color="g", alpha=0.5, label="finish SGD", linestyle=":")
        plt.savefig(f"{save_dir}/{scheduler_name}_SGD_project_{name}.png")
        plt.close()
    pos = [(drawing.x(i), drawing.y(i)) for u, i in indices.items()]
    # print(eg.stress(drawing, d))
    return pos, drawing


def full_sgd_check_constraints():
    file = "./src/data/json/download/no_cycle_tree.json"
    basename = os.path.basename(file)
    title = os.path.splitext(basename)[0]

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

    boxitem = []
    for i in range(20):
        each_constraint_violation = []
        print("\t", i)
        pos, drawing = full_sgd_with_constraints(
            eggraph,
            indices,
            constraints,
            edge_length=length,
            sgd_iter=10,
            project_iter=10,
            eps=0.1,
        )
        for l, r, gap in C["y"]:
            ly = drawing.y(l)
            ry = drawing.y(r)
            ydist = ry - ly
            if ydist < gap:
                each_constraint_violation.append((ydist - gap))
        boxitem.append(each_constraint_violation)

    boxitem.append(sum(boxitem, []))
    label = list(range(20))
    label.append("all")
    fig = plt.figure(figsize=(10, 8), facecolor="lightblue")
    plt.boxplot(boxitem, labels=label)
    plt.title("SGD:10 project:10 violation")
    plt.ylabel("violation")
    plt.legend()
    # plt.xlim(right=150)
    # plt.ylim(270, 300)
    # plt.axvline(i - 1, 0, 1, color="g", alpha=0.5, label="finish SGD", linestyle=":")
    plt.savefig(f"{save_dir}/SGD_project_violation.png")
    plt.close()


def full_sgd_main():
    files = [
        # "./src/data/json/download/no_cycle_tree.json",
        "./src/data/json/download/qh882.json",
        # "./src/data/json/download/dwt_1005.json",
        # "./src/data/json/download/1138_bus.json",
        # "./src/data/json/download/USpowerGrid.json",
        # "./src/data/json/download/dwt_2680.json",
        # "./src/data/json/download/3elt.json",
    ]
    for file in files:
        basename = os.path.basename(file)
        print(basename)
        title = os.path.splitext(basename)[0]

        stresses = []
        stressfilepath = os.path.join(fullsgd_save_dir, basename)
        imagepath = os.path.join(save_dir, title)
        # try:
        #     with open(stressfilepath, "r") as f:
        #         stresses = json.load(f)
        # except Exception as e:
        #     print(e)
        #     print(file)

        # if len(stresses) >= 20:
        #     continue

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

        for i in range(1):
            # if len(stresses) >= 20:
            #     break

            print("\t", i)
            pos, drawing = full_sgd_with_constraints(
                eggraph,
                indices,
                constraints,
                edge_length=length,
                sgd_iter=30,
                project_iter=30,
                eps=0.1,
                name=title,
            )

            stresses.append(eg.stress(drawing, d))
            os.makedirs(imagepath, exist_ok=True)
            plot_graph(nx_graph, pos, imagepath, f"{i}.png")
            # with open(stressfilepath, "w") as f:
            #     json.dump(stresses, f, indent=2)
        print(stresses)


def main():
    files = [
        "./src/data/json/download/no_cycle_tree.json",
        "./src/data/json/download/qh882.json",
        "./src/data/json/download/dwt_1005.json",
        "./src/data/json/download/1138_bus.json",
        "./src/data/json/download/USpowerGrid.json",
        "./src/data/json/download/dwt_2680.json",
        "./src/data/json/download/3elt.json",
    ]

    for file in files:
        basename = os.path.basename(file)
        print(basename)
        title = os.path.splitext(basename)[0]

        stresses = []
        # try:
        #     with open(f"./src/data/SGD/sparse/{basename}", "r") as f:
        #         stresses = json.load(f)
        # except Exception as e:
        #     print(e)
        #     print(file)

        # if len(stresses) >= 20:
        #     continue

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

        for i in range(1):
            # if len(stresses) >= 20:
            #     break

            print("\t", i)
            pos, drawing = sparse_sgd_with_constraints(
                eggraph,
                indices,
                constraints,
                edge_length=length,
                povot_count=50,
                iter_count=100,
                eps=0.1,
                name=title,
            )

            stresses.append(eg.stress(drawing, d))
            plot_graph(nx_graph, pos, save_dir, f"{basename}_{i}.png")
            with open(f"./src/data/SGD/sparse/{basename}", "w") as f:
                json.dump(stresses, f, indent=2)
        print(stresses)


if __name__ == "__main__":
    # main()
    full_sgd_main()
    # full_sgd_check_constraints()
