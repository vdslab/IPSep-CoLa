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
    data = [row for row in csv.DictReader(open(args.csv_file))
            if row['type'] == 'random_tree']
    methods = ['sgd', 'webcola']
    for method in methods:
        for row in data:
            graph_filepath = os.path.join(os.path.dirname(args.csv_file),
                                          row['path'])
            graph = nx.node_link_graph(json.load(open(graph_filepath)))
            drawing_filepath = f'data/drawing/{method}/{
                row['type']}/{row['n']}/{row['name']}'
            drawing = json.load(open(drawing_filepath))
            nodes = list(graph.nodes)
            s = 0
            for constraint in graph.graph['constraints']:
                u = nodes[constraint['left']]
                v = nodes[constraint['right']]
                gap = constraint['gap']
                if constraint['axis'] == 'x':
                    s += max(0, gap - (drawing[v][0] - drawing[u][0]))
                else:
                    s += max(0, gap - (drawing[v][1] - drawing[u][1]))
            s /= len(graph.graph['constraints'])
            writer.writerow(
                [row['name'], method, row['type'], row['n'], s])


if __name__ == '__main__':
    main()
