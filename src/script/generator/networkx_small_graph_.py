import argparse
import json

import networkx as nx


class Arg(argparse.Namespace):
    dest: str
    edge_length: int


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", required=True, help="directory to save graphs")
    parser.add_argument("--edge-length", type=int, default=100)
    args: Arg = parser.parse_args()

    import os

    os.makedirs(args.dest, exist_ok=True)

    graph_generators = [
        nx.bull_graph,
        nx.chvatal_graph,
        nx.cubical_graph,
        nx.desargues_graph,
        nx.diamond_graph,
        nx.dodecahedral_graph,
        nx.frucht_graph,
        nx.heawood_graph,
        nx.hoffman_singleton_graph,
        nx.house_graph,
        nx.house_x_graph,
        nx.icosahedral_graph,
        nx.krackhardt_kite_graph,
        nx.moebius_kantor_graph,
        nx.octahedral_graph,
        nx.pappus_graph,
        nx.petersen_graph,
        nx.sedgewick_maze_graph,
        nx.tetrahedral_graph,
        nx.truncated_cube_graph,
        nx.truncated_tetrahedron_graph,
        nx.tutte_graph,
    ]

    for generator in graph_generators:
        name = generator.__name__
        output = os.path.join(args.dest, f"{name}.json")
        print(f"Generating graph: {name}")
        graph: nx.Graph = generator()
        graph = nx.relabel_nodes(graph, lambda x: str(x))

        distance = nx.floyd_warshall_numpy(graph, weight=None)
        distance *= args.edge_length
        graph.graph["distance"] = distance.tolist()
        graph.graph["constraints"] = []

        data = nx.node_link_data(graph)
        json.dump(data, open(output, "w"))


if __name__ == "__main__":
    main()
