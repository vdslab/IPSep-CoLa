# nodes = set()
# edges = set()

# for i in range(1, 10):
#     edges.add((0, i))

# for i in range(50, 50 + 10):
#     edges.add((i, i + 1))

# print(edges)

# edges.add((0, 100))
# edges.add((50, 100))

# for i, j in edges:
#     nodes.add(i)
#     nodes.add(j)

# graph_edges = set()
# d = dict()
# index = 0
# for i, j in edges:
#     if i not in d:
#         d[i] = index
#         index += 1
#     if j not in d:
#         d[j] = index
#         index += 1

#     graph_edges.add((d[i], d[j]))

# graph_nodes = [i for i in range(index)]


# import networkx as nx

# G = nx.DiGraph()
# for node in graph_nodes:
#     G.add_node(node)

# for edge in graph_edges:
#     G.add_edge(*edge)

# print(G.nodes)
# print(G.edges)

# import matplotlib.pyplot as plt

# fig, ax = plt.subplots(figsize=(10, 10))
# ax.set_aspect("equal")


# nx.draw(G, node_size=300, ax=ax)
# plt.savefig("test.png")
# plt.close()

# #   {
# #       "axis": "y",
# #       "left": 0,
# #       "right": 1,
# #       "gap": 25
# #     },

# data = {
#     "nodes": [{"id": i} for i in graph_nodes],
#     "links": [{"source": i, "target": j} for i, j in graph_edges],
#     "constraints": [
#         {"axis": "y", "left": i, "right": j, "gap": 25} for i, j in graph_edges
#     ],
# }
# import json

# json.dump(data, open("src/data/tree_line.json", "w"), indent=2)

from collections import deque

import networkx as nx


def tree_graph_parent(n, edges):
    link_graph = [[] for _ in range(n)]
    for i, j in edges:
        link_graph[i].append(j)
        link_graph[j].append(i)
    dist = [float("inf") for _ in range(n)]
    dist[0] = 0
    parent = [-1 for _ in range(n)]
    q = deque([0])
    while q:
        i = q.popleft()
        for j in link_graph[i]:
            if dist[j] > dist[i] + 1:
                dist[j] = dist[i] + 1
                parent[j] = i
                q.append(j)

    return parent


ns = list(range(50, 501, 50))
ns = [10] + ns
# graphs: list[nx.Graph] = [nx.random_tree(n) for n in ns]
# graphs: list[nx.Graph] = [nx.gnp_random_graph(n, 0.2) for n in ns]

connected_seed = []
for n in ns:
    for i in range(1000000):
        graph = nx.gnp_random_graph(n, 0.2, seed=i)
        if nx.is_connected(graph):
            connected_seed.append((n, i))
            break

graphs = []
for n, seed in connected_seed:
    graph = nx.gnp_random_graph(n, 0.2, seed=seed)
    graphs.append(graph)


for graph, n in zip(graphs, ns):
    print(f"random_tree_{n}")
    nodes = [{"id": i, "name": i} for i in graph.nodes]
    links = [{"source": i, "target": j} for i, j in graph.edges]

    edges = list(graph.edges)
    parent = tree_graph_parent(n, edges)
    constraint_edges = []
    for i in range(1, n):
        if parent[i] != -1:
            constraint_edges.append((parent[i], i))

    constraints = [{"axis": "y", "left": i, "right": j, "gap": 20} for i, j in edges]

    data = {
        "nodes": nodes,
        "links": links,
        "constraints": constraints,
    }
    import json

    json.dump(
        data, open(f"src/data/gnp_random_all_constraints_{n}.json", "w"), indent=2
    )
