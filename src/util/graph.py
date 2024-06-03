import json
import networkx as nx
import numpy as np


def get_graph_and_constraints(file):
    with open(file) as f:
        data = json.load(f)

    links = [[d["source"] + 1, d["target"] + 1] for d in data["links"]]
    constraints = data["constraints"]
    G = nx.Graph(links)

    return G, constraints


def init_positions(G: nx.Graph, dim, seed):
    n = G.number_of_nodes()
    np.random.seed(seed)
    Z = np.random.rand(n, dim)
    Z[0] = [0 for _ in range(dim)]
    return Z
