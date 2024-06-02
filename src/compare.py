import datetime
import os
from sgd.main import plot_sgd

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import json
from majorization.main import stress, weights_of_normalization_constant
from networkx import floyd_warshall_numpy
from ipsep_cola.main import IPSep_CoLa
import time

today = datetime.date.today()
now = datetime.datetime.now()
save_dir = f"result/SGD/edge_gap/{today}/{now}"
os.makedirs(save_dir, exist_ok=True)

# for gap in gaps:
#     for edge_length in edge_lengths:
filename = "les_miserables_graph.json"
filename = "./src/data/no_cycle_tree.json"


start = time.time()
sgd_stresses, sgd_times = plot_sgd(filename, save_dir, 20, 30)
sgd_times = [s - start for s in sgd_times]

with open(filename) as f:
    data = json.load(f)

nodes = [i for i in range(len(data["nodes"]))]
n = len(nodes)

links = [[d["source"], d["target"]] for d in data["links"]]
constraints = data["constraints"]

G = nx.Graph()
for node in nodes:
    G.add_node(node)
for link in links:
    G.add_edge(*link)

np.random.seed(0)
today = datetime.date.today()
now = datetime.datetime.now().time()
dir = f"result/IPSep_Cola/{today}/{now.hour}-{now.minute}-{now.second}"


def view(position, file_name):
    DG = nx.DiGraph()
    for node in nodes:
        DG.add_node(node)
    for link in links:
        DG.add_edge(*link)

    position = {i: position[i] for i in range(n)}

    os.makedirs(dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")

    plt.title(file_name)
    nx.draw(G, pos=position, node_size=300, labels={i: i for i in range(n)}, ax=ax)
    plt.savefig(f"{save_dir}/{file_name}.png")
    plt.close()


dist = floyd_warshall_numpy(G)
# Tips: gapは実際のノードサイズ以上にしてくれとのこと.


C: dict[str, list] = dict()
C["y"] = []
C["x"] = []
for c in constraints:
    left = c["left"]
    right = c["right"]
    axis = c["axis"]
    gap = c["gap"]
    C[axis].append([left, right, gap])
start = time.time()
Z, stresses, times = IPSep_CoLa(G, C, edge_length=20.0)
times = [s - start for s in times]
weight = weights_of_normalization_constant(2, dist)
stress(Z, dist, weight)
print(stresses)

view(Z, "IPSep_Cola (seed 0) edge_length=20.0")

fig, ax = plt.subplots()
ax.plot(times, stresses)
ax.plot(sgd_times, sgd_stresses)
ax.set_yscale("log")
ax.set_xlabel("time (second)")
ax.set_ylabel("stress")
ax.legend(["IPSep_CoLa", "use SGD"])
plt.savefig(f"{save_dir}/stress_time.png")
plt.close()
print(sgd_times)
print(times)
print(time.time())
