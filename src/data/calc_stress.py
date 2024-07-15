import glob
import json

import numpy as np
from majorization.main import (
    stress,
    weight_laplacian,
    weights_of_normalization_constant,
)
from networkx import floyd_warshall_numpy
from util.graph import get_graph_and_constraints


def get_data(file):
    with open(file) as f:
        data = json.load(f)
    return data


def xy_dict_to_list(data):
    xy = [[0, 0] for _ in range(len(data))]
    for d in data:
        xy[d["index"]] = [
            d["x"],
            d["y"],
        ]
    # x, y = zip(*xy)
    # x = liner_scale(x, 0, 100)
    # y = liner_scale(y, 0, 100)
    # xy = [[x[i], y[i]] for i in range(len(x))]
    return np.array(xy)


import os

dirs = glob.glob("src/data/cola/**/")
print(dirs)
print([os.path.basename(os.path.dirname(d)) for d in dirs])

dirs = [
    "src/data/cola/no_cycle_tree/",
    "src/data/cola/qh882/",
    "src/data/cola/1138_bus/",
    "src/data/cola/dwt_1005/",
    "src/data/cola/dwt_2680/",
    "src/data/cola/USpowerGrid/",
    "src/data/cola/3elt/",
]
for dir in dirs:
    dirname = os.path.basename(os.path.dirname(dir))
    if dirname == "stress":
        continue
    print(dirname)
    files = glob.glob(os.path.join(dir, "*.json"))
    stresses = []
    for file in files:
        print("\t", file)
        data = get_data(file)
        nodes = data["nodes"]
        xy = xy_dict_to_list(nodes)
        dist = data["distanceMatrix"]
        weights = weights_of_normalization_constant(2, dist)
        stresses.append(stress(xy, dist, weights))
        with open(f"src/data/cola/stress/{dirname}.json", "w") as f:
            json.dump(stresses, f, indent=2)
# for base_name in base_names:
#     files = glob.glob(f"src/data/cola/{base_name}*.json")
#     stresses = []
#     if base_name == "bus_1138":
#         base_name = "1138_bus"
#     graph, _ = get_graph_and_constraints(f"src/data/json/download/{base_name}.json")
#     dist = floyd_warshall_numpy(graph)
#     dist *= 20
#     weights = weights_of_normalization_constant(2, dist)
#     for file in files:
#         data = get_data(file)
#         xy = xy_dict_to_list(data)
#         xy = np.array(xy)
#         # print(stress(xy, dist, weights))
#         stresses.append(stress(xy, dist, weights))
#         # print(data[0])
#         # print(xy[0])
#         break
#     print(stresses)
