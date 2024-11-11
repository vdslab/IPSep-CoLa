import json

import egraph as eg
import networkx as nx
import numpy as np


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


def init_positions(G: nx.Graph, dim, seed=None):
    n = G.number_of_nodes()
    if seed is not None:
        np.random.seed(seed)
    Z = np.random.rand(n, dim)
    Z[0] = [0 for _ in range(dim)]
    return Z


def nxgraph_to_eggraph(graph: nx.Graph) -> tuple[eg.Graph, dict]:
    eggraph = eg.Graph()
    indices = {}
    for u in graph.nodes:
        indices[u] = eggraph.add_node(u)
    for u, v in graph.edges:
        eggraph.add_edge(indices[u], indices[v], (u, v))
    return eggraph, indices
