import glob
import json

import networkx as nx

from sgd.github_commit_tree import github_commit_tree
from util.constraint import Constraints, get_constraints_dict
from util.parameter import SGDParameter


def tree():
    print("create align")
    graph_base_dir = "src/data/json/random_tree/2024-10-27/07:07:06.283826"
    # d_today = datetime.date.today()
    # t_now = datetime.datetime.now().time()
    # savedir = f"src/data/json/{d_today}/random_tree/05:44:55.186990"
    # "src/data/json/2024-10-21/random_tree/05:44:55.186990"
    # os.makedirs(savedir, exist_ok=True)

    for node_n in range(100, 2001, 100):
        print(f"{node_n=}")
        graphdir = f"{graph_base_dir}/{node_n}"
        files = glob.glob(f"{graphdir}/*.json")
        files.sort()
        for file in files:
            with open(file) as f:
                json_data = json.load(f)
                graph_data = json_data["graph"]

            nxgraph = nx.Graph()
            # print(graph_data["nodes"])
            for node in graph_data["nodes"]:
                nxgraph.add_node(node["id"])
            for link in graph_data["links"]:
                nxgraph.add_edge(link["source"], link["target"])
            gt = github_commit_tree(nxgraph, 0)
            gt.sort(key=lambda x: len(x), reverse=True)
            # print(gt)
            align_constraints = []
            for t in gt:
                for i in range(1, len(t)):
                    align_constraints.append(
                        {
                            "axis": "x",
                            "left": t[i - 1],
                            "right": t[i],
                            "gap": 0,
                        }
                    )
                    align_constraints.append(
                        {
                            "axis": "x",
                            "left": t[i],
                            "right": t[i - 1],
                            "gap": 0,
                        }
                    )
            json_data["graph"]["alignment"] = align_constraints
            with open(file, "w") as f:
                json.dump(
                    json_data,
                    f,
                    indent=2,
                )


tree()
