import argparse
import csv
import itertools
import json
import math
import os

import networkx as nx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file')
    parser.add_argument('out')
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    writer = csv.writer(open(args.out, 'w'))
    writer.writerow(['name', 'method', 'type', 'n', 'value'])
    data = [row for row in csv.DictReader(open(args.csv_file))]
    methods = ['sgd', 'webcola']
    for method in methods:
        for row in data:
            graph_filepath = os.path.join(os.path.dirname(args.csv_file),
                                          row['path'])
            print(method, graph_filepath)
            graph = nx.node_link_graph(json.load(open(graph_filepath)))
            drawing_filepath = f"data/drawing/{method}/{row['type']}/{int(row['n']):04}/{row['name']}"
            drawing = json.load(open(drawing_filepath))
            s = 0
            nodes = list(graph.nodes)
            for i, j in itertools.combinations(range(graph.number_of_nodes()), 2):
                d1 = graph.graph['distance'][i][j]
                pos_i = drawing[nodes[i]]
                pos_j = drawing[nodes[j]]
                d2 = math.hypot(pos_i[0] - pos_j[0], pos_i[1] - pos_j[1])
                s += ((d2 - d1) / d1) ** 2
            s /= len(nodes) * (len(nodes) - 1) // 2
            writer.writerow(
                [row['name'], method, row['type'], row['n'], s])


if __name__ == '__main__':
    main()
