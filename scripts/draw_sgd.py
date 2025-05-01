import argparse
import json
import os

import networkx as nx

from sgd.full import sgd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', default='.')
    parser.add_argument('--iterations', type=int, default=30)
    parser.add_argument('--overlap-removal',
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('--cluster-overlap-removal',
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('input', nargs='+')
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    for filepath in args.input:
        basename = os.path.basename(filepath)
        graph = nx.node_link_graph(json.load(open(filepath)))
        clusters = None
        if args.cluster_overlap_removal:
            clusters = [graph.nodes[u]['group'] for u in graph.nodes]
        pos = sgd(graph, iterations=args.iterations,
                  overlap_removal=args.overlap_removal,
                  clusters=clusters)
        json.dump(pos,
                  open(os.path.join(args.dest, basename), 'w'),
                  ensure_ascii=False)


if __name__ == '__main__':
    main()
