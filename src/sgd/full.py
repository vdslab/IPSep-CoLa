import datetime
import glob
import json
import os
import time
from logging import DEBUG, StreamHandler, getLogger, handlers

import egraph as eg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from ipsep_cola import NodeBlocks, project, split_blocks
from ipsep_cola.constraint import Constraints, get_constraints_dict
from majorization.main import weight_laplacian, weights_of_normalization_constant
from sgd.github_commit_tree import github_commit_tree
from util.graph import get_graph_and_constraints, nxgraph_to_eggraph, plot_graph
from util.parameter import SGDParameter

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


def main():
    basedir = "src/data/json/random_tree/2024-10-20/14:50:33.276929"
    for node_n in range(100, 101, 100):
        graphdir = f"{basedir}/{node_n}"
        files = glob.glob(f"{graphdir}/*.json")
        files.sort()
        stresses = []
        for file in files:
            basename = os.path.basename(file)
            print(basename)
            title = os.path.splitext(basename)[0]

            stresses = []
            with open(file) as f:
                json_data = json.load(f)
                graph_data = json_data["graph"]
                dist_list = json_data["dist"]
                length = json_data["length"]

            nxgraph = nx.Graph()
            # print(graph_data["nodes"])
            for node in graph_data["nodes"]:
                nxgraph.add_node(node["id"])
            for link in graph_data["links"]:
                nxgraph.add_edge(*link)
            print(nxgraph)
            C = get_constraints_dict(graph_data["constraints"], default_gap=20)

            constraints = Constraints(C["y"], nxgraph.number_of_nodes())
            eggraph, indices = nxgraph_to_eggraph(nxgraph)
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
                # os.makedirs(imagepath, exist_ok=True)
                # plot_graph(nx_graph, pos, imagepath, f"{i}.png")
                # with open(stressfilepath, "w") as f:
                #     json.dump(stresses, f, indent=2)
            print(stresses)


def tree():
    graph_base_dir = "src/data/json/random_tree/2024-10-27/07:07:06.283826"
    # d_today = datetime.date.today()
    # t_now = datetime.datetime.now().time()
    # savedir = f"src/data/json/{d_today}/random_tree/05:44:55.186990"
    # "src/data/json/2024-10-21/random_tree/05:44:55.186990"
    # os.makedirs(savedir, exist_ok=True)
    savedir = "src/data/align/sgd"
    data = []
    for node_n in range(100, 101, 100):
        graphdir = f"{graph_base_dir}/{node_n}"
        files = glob.glob(f"{graphdir}/*.json")
        files.sort()
        stresses = []
        positions = []
        for file in files:
            with open(file) as f:
                json_data = json.load(f)
                graph_data = json_data["graph"]
                dist_list = json_data["dist"]
                length = json_data["length"]

            nxgraph = nx.Graph()
            for node in graph_data["nodes"]:
                nxgraph.add_node(node["id"])
            for link in graph_data["links"]:
                nxgraph.add_edge(link["source"], link["target"])
            C = {"y": [], "x": []}
            C = get_constraints_dict(graph_data["constraints"], default_gap=20)
            # C_align = get_constraints_dict(graph_data["alignment"], default_gap=20)
            # C["y"] += C_align["y"]
            # C["x"] += C_align["x"]
            # nxgraph = nx.random_tree(3)

            # C = {"y": [[0, 1, 0], [1, 0, 0]], "x": [[0, 1, 0], [1, 0, 0]]}
            real_node_n = nxgraph.number_of_nodes()
            fixed_nodes = [
                {"index": real_node_n, "x": 0, "y": 0},
                {"index": real_node_n + 1, "x": 25, "y": 25},
            ]
            # dist_list = nx.floyd_warshall_numpy(nxgraph)
            node_num = real_node_n + len(fixed_nodes)

            for i in range(real_node_n):
                for j in range(i + 1, real_node_n):
                    C["y"].append([i, j, 10])
                    C["x"].append([i, j, 10])
                    C["y"].append([j, i, 10])
                    C["x"].append([j, i, 10])

            for i in range(real_node_n):
                C["y"].append([real_node_n, i, 30])
                C["x"].append([real_node_n, i, 30])
                C["y"].append([i, real_node_n + 1, 30])
                C["x"].append([i, real_node_n + 1, 30])

            sgd_param = SGDParameter(iterator=10, eps=0.1, seed=None)
            const_dist = dict()
            if C.get("y") is not None and len(C["y"]) > 0:
                const_dist["y"] = Constraints(C["y"], node_num)
            if C.get("x") is not None and len(C["x"]) > 0:
                const_dist["x"] = Constraints(C["x"], node_num)
            print(f"{C=}")
            x_graph = nx.Graph()
            for l, r, g in C["x"]:
                x_graph.add_edge(l, r)
            y_graph = nx.Graph()
            for l, r, g in C["y"]:
                y_graph.add_edge(l, r)

            position, stress = __sgd(
                nxgraph,
                const_dist,
                edge_length=length,
                sgd_parameter=sgd_param,
                dist_list=dist_list,
                fixed_nodes=fixed_nodes,
            )
            # nxgraph.remove_node(real_node_n)
            # nxgraph.remove_node(real_node_n + 1)
            # position = position[:real_node_n]
            plot_graph(nxgraph, position, savedir, f"{node_n}.png", aspect="equal")
            stresses.append(stress)
            positions.append(position)
            # break
            with open(f"{savedir}/stress_potition_{node_n}.json", "w") as f:
                json.dump(
                    {
                        "stresses": stresses,
                        "positions": positions,
                    },
                    f,
                    indent=2,
                )
            break

        data.append(
            {
                "node_n": node_n,
                "stresses": stresses,
            }
        )
        break

        with open(f"{savedir}/stress.json", "w") as f:
            json.dump(
                data,
                f,
                indent=2,
            )


def tree():
    graph_base_dir = "src/data/json/random_tree/2024-10-27/07:07:06.283826"
    # d_today = datetime.date.today()
    # t_now = datetime.datetime.now().time()
    # savedir = f"src/data/json/{d_today}/random_tree/05:44:55.186990"
    # "src/data/json/2024-10-21/random_tree/05:44:55.186990"
    # os.makedirs(savedir, exist_ok=True)
    savedir = "src/data/align/sgd"
    data = []
    for node_n in range(200, 201, 100):
        graphdir = f"{graph_base_dir}/{node_n}"
        files = glob.glob(f"{graphdir}/*.json")
        files.sort()
        stresses = []
        positions = []
        for file in files:
            with open(file) as f:
                json_data = json.load(f)
                graph_data = json_data["graph"]
                dist_list = json_data["dist"]
                length = json_data["length"]

            nxgraph = nx.Graph()
            for node in graph_data["nodes"]:
                nxgraph.add_node(node["id"])
            for link in graph_data["links"]:
                nxgraph.add_edge(link["source"], link["target"])
            C = {"y": [], "x": []}
            C = get_constraints_dict(graph_data["constraints"], default_gap=20)
            # C_align = get_constraints_dict(graph_data["alignment"], default_gap=20)
            # C["y"] += C_align["y"]
            # C["x"] += C_align["x"]
            # nxgraph = nx.random_tree(3)

            # C = {"y": [[0, 1, 0], [1, 0, 0]], "x": [[0, 1, 0], [1, 0, 0]]}
            real_node_n = nxgraph.number_of_nodes()
            fixed_nodes = [
                # {"index": real_node_n, "x": 0, "y": 0},
                # {"index": real_node_n + 1, "x": 25, "y": 25},
            ]
            # dist_list = nx.floyd_warshall_numpy(nxgraph)
            node_num = real_node_n + len(fixed_nodes)

            # for i in range(real_node_n):
            #     for j in range(i + 1, real_node_n):
            #         C["y"].append([i, j, 10])
            #         C["x"].append([i, j, 10])
            #         C["y"].append([j, i, 10])
            #         C["x"].append([j, i, 10])

            # for i in range(real_node_n):
            #     C["y"].append([real_node_n, i, 30])
            #     C["x"].append([real_node_n, i, 30])
            #     C["y"].append([i, real_node_n + 1, 30])
            #     C["x"].append([i, real_node_n + 1, 30])

            sgd_param = SGDParameter(iterator=10, eps=0.1, seed=None)
            const_dist = dict()
            if C.get("y") is not None and len(C["y"]) > 0:
                const_dist["y"] = Constraints(C["y"], node_num)
            if C.get("x") is not None and len(C["x"]) > 0:
                const_dist["x"] = Constraints(C["x"], node_num)
            print(f"{C=}")
            x_graph = nx.Graph()
            for l, r, g in C["x"]:
                x_graph.add_edge(l, r)
            y_graph = nx.Graph()
            for l, r, g in C["y"]:
                y_graph.add_edge(l, r)
            # nx.spring_layout(x_graph)
            # nx.spring_layout(y_graph)
            # nx.draw(x_graph)
            # plt.savefig(f"x_graph_{node_n}.png")
            # plt.close()
            # nx.draw(y_graph)
            # plt.savefig(f"y_graph_{node_n}.png")
            # plt.close()
            # plt.show()
            # break

            position, stress = __sgd(
                nxgraph,
                const_dist,
                edge_length=length,
                sgd_parameter=sgd_param,
                dist_list=dist_list,
                fixed_nodes=fixed_nodes,
            )
            # nxgraph.remove_node(real_node_n)
            # nxgraph.remove_node(real_node_n + 1)
            # position = position[:real_node_n]
            plot_graph(nxgraph, position, savedir, f"{node_n}.png", aspect="equal")
            stresses.append(stress)
            positions.append(position)
            # break
            with open(f"{savedir}/stress_potition_{node_n}.json", "w") as f:
                json.dump(
                    {
                        "stresses": stresses,
                        "positions": positions,
                    },
                    f,
                    indent=2,
                )
            # break

        data.append(
            {
                "node_n": node_n,
                "stresses": stresses,
            }
        )
        # break

        with open(f"{savedir}/stress.json", "w") as f:
            json.dump(
                data,
                f,
                indent=2,
            )


# def __main():
#     nx_graph, constraints_data = get_graph_and_constraints("")
#     length = 20
#     C = get_constraints_dict(constraints_data, default_gap=20)
#     constraints = Constraints(C["y"], nx_graph.number_of_nodes())

#     sgd_param = SGDParameter(iterator=10, eps=0.1, seed=None)
#     for i in range(1):
#         pos, stress = __sgd(
#             nx_graph, constraints, edge_length=length, sgd_parameter=sgd_param
#         )


def __sgd(
    nx_graph: nx.Graph,
    constraints: dict[str, Constraints],
    edge_length,
    sgd_parameter: SGDParameter,
    dist_list,
    fixed_nodes: list[dict] = [],
):
    eggraph, indices = nxgraph_to_eggraph(nx_graph)
    drawing = eg.DrawingEuclidean2d.initial_placement(eggraph)
    dist = eg.all_sources_dijkstra(eggraph, lambda _: edge_length)
    sgd = eg.FullSgd.new_with_distance_matrix(dist)

    _pos = __do_sgd(
        drawing, constraints, dist, sgd, sgd_parameter, dist_list, fixed_nodes
    )
    for pj in _pos:
        for pp, jj in pj:
            print(jj)
            pp = [(pp["x"][i], pp["y"][i]) for i in range(len(indices))]
            plot_graph(nx_graph, pp, "src/data/align/sgd", f"{jj}.png")

    pos = [(drawing.x(i), drawing.y(i)) for u, i in indices.items()]
    stress = eg.stress(drawing, dist)
    return pos, stress


def __do_sgd(
    drawing,
    constraints: dict[str, Constraints],
    dist,
    sgd,
    parameter: SGDParameter,
    dist_list,
    fixed_nodes: list[dict] = [],
):
    def step(eta):
        sgd.shuffle(parameter.rng)
        sgd.apply(drawing, eta)

    sgd_scheduler = sgd.scheduler(
        parameter.iter,  # number of iterations
        parameter.eps,  # eps: eta_min = eps * min d[i, j] ^ 2
    )
    sgd_scheduler.run(step)

    # __do_project(
    #     constraints,
    #     dist=dist_list,
    #     drawing=drawing,
    #     sgd=sgd,
    #     parameter=parameter,
    #     fixed_nodes=fixed_nodes,
    # )
    yield __do_project(
        constraints,
        dist=dist_list,
        drawing=drawing,
        sgd=sgd,
        parameter=parameter,
        fixed_nodes=fixed_nodes,
        with_sgd=True,
    )


def __do_project(
    constraints: dict[str, Constraints],
    dist: list[list[int]],
    drawing,
    sgd,
    parameter: SGDParameter,
    fixed_nodes: list[dict] = [],
    with_sgd=False,
):
    def step(eta):
        sgd.shuffle(parameter.rng)
        sgd.apply(drawing, eta)

    ds = np.array(dist).flatten()
    ds = ds[ds != 0]
    d_min = np.min(ds)
    d_max = np.max(ds)

    eta_max = 1 / (d_max**2)
    eta_min = parameter.eps / (d_min**2)
    b = 1 / (parameter.iter - 1) * np.log(eta_min / eta_max)

    n = len(dist)
    sgd_scheduler = sgd.scheduler(
        parameter.iter,  # number of iterations
        parameter.eps,  # eps: eta_min = eps * min d[i, j] ^ 2
    )

    fixed_nodes.sort(key=lambda x: x["index"])
    # position = {
    #     "x": np.array([drawing.x(i) for i in range(n)] + [0] * len(fixed_nodes)),
    #     "y": np.array([drawing.y(i) for i in range(n)] + [0] * len(fixed_nodes)),
    # }
    # for node in fixed_nodes:
    #     position["y"][node["index"]] = node["y"]
    #     position["x"][node["index"]] = node["x"]

    # blocks = {
    #     "x": NodeBlocks(position["x"]),
    #     "y": NodeBlocks(position["y"]),
    # }
    for j in range(parameter.iter):
        if with_sgd:
            sgd_scheduler.step(step)
        eta = eta_max * np.exp(b * j)
        position = {
            "x": np.array([drawing.x(i) for i in range(n)] + [0] * len(fixed_nodes)),
            "y": np.array([drawing.y(i) for i in range(n)] + [0] * len(fixed_nodes)),
        }
        for node in fixed_nodes:
            position["y"][node["index"]] = node["y"]
            position["x"][node["index"]] = node["x"]
        blocks = {
            "x": NodeBlocks(position["x"]),
            "y": NodeBlocks(position["y"]),
        }
        for node in fixed_nodes:
            blocks["y"].fixedWeight(node["index"])
            blocks["x"].fixedWeight(node["index"])

        for key in constraints.keys():
            block = blocks[key]
            block.positions = position[key]
            block.desired_position = position[key]

        for key in constraints.keys():
            _pos = position[key]
            pos: np.ndarray = _pos.copy()

            block = blocks[key]
            split_blocks(_pos.flatten(), constraints[key], block)
            y_bar = project(constraints[key], block)
            y_bar = y_bar.flatten()
            print(y_bar)
            d = y_bar - pos
            eta = eta_max * np.exp(b * j)
            pos = _pos + d * (1 + (eta - eta_min) / (eta_max - eta_min))

            pos = pos.flatten()
            pos = list(pos[:n]) + [0] * len(fixed_nodes)
            for node in fixed_nodes:
                pos[node["index"]] = node[key]
            position[key] = np.array(pos)
        yield position, j
        for i in range(n):
            drawing.set_y(i, position["y"][i])
            drawing.set_x(i, position["x"][i])


if __name__ == "__main__":
    # main()
    # full_sgd_check_constraints()
    tree()
    # pass
