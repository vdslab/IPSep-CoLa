import argparse
import json

import networkx as nx
import numpy as np


class Arg(argparse.Namespace):
    output: str
    node_size: int
    edge_length: int


def estimate_power_law_exponent(graph):
    """グラフの次数分布からpower law指数を推定

    Args:
        graph: NetworkXグラフ

    Returns:
        float: 推定されたpower law指数γ
    """
    degrees = [d for n, d in graph.degree()]
    degree_count = {}
    for d in degrees:
        degree_count[d] = degree_count.get(d, 0) + 1

    # 対数-対数プロットで線形回帰
    k_values = sorted(degree_count.keys())
    p_values = [degree_count[k] / len(degrees) for k in k_values]

    # k >= 2 のデータのみ使用(ノイズ除去)
    valid_indices = [i for i, k in enumerate(k_values) if k >= 2]
    if len(valid_indices) < 2:
        # データが不足している場合はデフォルト値を返す
        return 3.0

    log_k = np.log([k_values[i] for i in valid_indices])
    log_p = np.log([p_values[i] for i in valid_indices])

    # 線形回帰で傾きを求める
    slope, _ = np.polyfit(log_k, log_p, 1)
    gamma = -slope
    return gamma


def generate(output: str, n: int):
    def trim_graph(graph: nx.DiGraph) -> nx.Graph:
        """多重辺、自己ループを削除する"""
        simple_graph = nx.Graph()
        simple_graph.add_nodes_from(graph.nodes(data=True))
        edges = [
            (u, v, d)
            for u, v, d in graph.edges(data=True)
            if u != v and not simple_graph.has_edge(u, v)
        ]
        simple_graph.add_edges_from(edges)
        return simple_graph

    def create_graph(n):
        graph = nx.scale_free_graph(n, alpha=0.20, beta=0.75, gamma=0.05, seed=None)
        graph = trim_graph(graph)
        if not nx.is_connected(graph):
            raise ValueError("生成されたグラフが連結ではありません")
        print(
            "nodes:",
            graph.number_of_nodes(),
            "edges:",
            graph.number_of_edges(),
            "avg_deg:",
            2 * graph.number_of_edges() / graph.number_of_nodes(),
        )
        graph = nx.relabel_nodes(graph, lambda x: str(x))

        distance = nx.floyd_warshall_numpy(graph, weight=None)
        graph.graph["distance"] = distance.tolist()
        graph.graph["constraints"] = []
        return graph

    for i in range(10):
        try:
            graph = create_graph(n)
            break
        except ValueError:
            if i == 9:
                raise
            print("再試行", i + 1)
    return graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--node-size", type=int, default=100)
    parser.add_argument("--edge-length", type=int, default=100)
    args = parser.parse_args(namespace=Arg)

    graph = generate(args.output, args.node_size)

    data = nx.node_link_data(graph)
    import os

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    json.dump(data, open(args.output, "w"))


if __name__ == "__main__":
    main()
