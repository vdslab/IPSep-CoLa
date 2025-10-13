import json

import networkx as nx
from networkx.readwrite import json_graph

G: nx.Graph = nx.cubical_graph()
graph = nx.Graph()
for node in G.nodes:
    graph.add_node(str(node))
for u, v in G.edges:
    graph.add_edge(str(u), str(v))


data = json_graph.node_link_data(graph)
distance = nx.floyd_warshall_numpy(graph, weight=None)
graph.graph["distance"] = distance.tolist()
graph.graph["constraints"] = []
print(json.dump(data, open("data/graph/cube.json", "w"), indent=2))
