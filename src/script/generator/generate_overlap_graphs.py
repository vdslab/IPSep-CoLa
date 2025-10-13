import csv
import json
import os

import networkx as nx


def main():
    csvpath = 'data/graph/overlap.csv'
    os.makedirs(os.path.dirname(csvpath), exist_ok=True)
    writer = csv.writer(open('data/graph/overlap.csv', 'w'))
    writer.writerow(['name', 'type', 'n', 'path'])

    for n in range(100, 2001, 100):
        for i in range(20):
            graph = nx.connected_watts_strogatz_graph(n, 5, 0.2, seed=i)
            distance = nx.floyd_warshall_numpy(graph, weight=None) * 100
            graph.graph['distance'] = distance.tolist()
            graph.graph['constraints'] = []
            for u in graph.nodes:
                graph.nodes[u]['shape'] = {
                    'type': 'rect',
                    'width': 20,
                    'height': 20,
                }

            name = f'node_n={n:04}_{i:02}.json'
            graphpath = f'data/graph/overlap/{n:04}/{name}'
            data = nx.node_link_data(graph)
            for node in data['nodes']:
                node['id'] = str(node['id'])
            for link in data['links']:
                link['source'] = str(link['source'])
                link['target'] = str(link['target'])
            os.makedirs(os.path.dirname(graphpath), exist_ok=True)
            json.dump(data, open(graphpath, 'w'))
            writer.writerow([name, 'overlap', n, f'overlap/{n:04}/{name}'])


if __name__ == '__main__':
    main()
