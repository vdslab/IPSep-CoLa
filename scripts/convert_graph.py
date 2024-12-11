import argparse
import json
import os

import networkx as nx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', default='.')
    parser.add_argument('input', nargs='+')
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    for filepath in args.input:
        basename = os.path.basename(filepath)
        print(basename)
        data = json.load(open(filepath))
        graph = nx.Graph()
        for node in data['graph']['nodes']:
            graph.add_node(str(node['id']))
        for link in data['graph']['links']:
            graph.add_edge(str(link['source']), str(link['target']))
        for i in range(graph.number_of_nodes()):
            for j in range(graph.number_of_nodes()):
                data['dist'][i][j] *= data['length']
        graph.graph['constraints'] = data['graph']['constraints']
        graph.graph['distance'] = data['dist']
        new_data = nx.node_link_data(graph)
        json.dump(new_data,
                  open(os.path.join(args.dest, basename), 'w'),
                  ensure_ascii=False)


if __name__ == '__main__':
    main()
