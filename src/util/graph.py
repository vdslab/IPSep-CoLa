import json
import networkx as nx
import numpy as np

import os
import matplotlib.pyplot as plt


def get_graph_and_constraints(file):
    with open(file) as f:
        data = json.load(f)

    # links = [[d["source"], d["target"]] for d in data["links"]]
    # constraints = data["constraints"]
    # G = nx.Graph(links)
    nodes = [i for i in range(len(data["nodes"]))]

    links = [[d["source"], d["target"]] for d in data["links"]]
    constraints = data["constraints"]

    G = nx.Graph()
    for node in nodes:
        G.add_node(node)
    for link in links:
        G.add_edge(*link)

    return G, constraints


def init_positions(G: nx.Graph, dim, seed):
    n = G.number_of_nodes()
    np.random.seed(seed)
    Z = np.random.rand(n, dim)
    Z[0] = [0 for _ in range(dim)]
    return Z


def plot_graph(G: nx.Graph, Z, save_dir, file_name="graph.png"):
    n = G.number_of_nodes()
    position = {i: Z[i] for i in range(n)}

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")
    nx.draw(G, with_labels=True, pos=position)
    plt.savefig(os.path.join(save_dir, file_name))
    plt.close()
