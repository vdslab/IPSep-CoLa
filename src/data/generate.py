nodes = set()
edges = set()

for i in range(1, 10):
    edges.add((0, i))

for i in range(50, 50 + 10):
    edges.add((i, i + 1))

print(edges)

edges.add((0, 100))
edges.add((50, 100))

for i, j in edges:
    nodes.add(i)
    nodes.add(j)

graph_edges = set()
d = dict()
index = 0
for i, j in edges:
    if i not in d:
        d[i] = index
        index += 1
    if j not in d:
        d[j] = index
        index += 1

    graph_edges.add((d[i], d[j]))

graph_nodes = [i for i in range(index)]


import networkx as nx

G = nx.DiGraph()
for node in graph_nodes:
    G.add_node(node)

for edge in graph_edges:
    G.add_edge(*edge)

print(G.nodes)
print(G.edges)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 10))
ax.set_aspect("equal")


nx.draw(G, node_size=300, ax=ax)
plt.savefig("test.png")
plt.close()

#   {
#       "axis": "y",
#       "left": 0,
#       "right": 1,
#       "gap": 25
#     },

data = {
    "nodes": [{"id": i} for i in graph_nodes],
    "links": [{"source": i, "target": j} for i, j in graph_edges],
    "constraints": [
        {"axis": "y", "left": i, "right": j, "gap": 25} for i, j in graph_edges
    ],
}
import json

json.dump(data, open("src/data/tree_line.json", "w"), indent=2)
