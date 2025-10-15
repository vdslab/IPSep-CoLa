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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--node-size", type=int, default=100)
    parser.add_argument("--edge-length", type=int, default=20)
    args = parser.parse_args(namespace=Arg)

    graph = nx.scale_free_graph(args.node_size)
    assert nx.is_connected(graph)
    graph = nx.relabel_nodes(graph, lambda x: str(x))

    distance = nx.floyd_warshall_numpy(graph, weight=None)
    graph.graph["distance"] = distance.tolist()
    graph.graph["constraints"] = []
    data = nx.node_link_data(graph)
    json.dump(data, open(args.output, "w"))


if __name__ == "__main__":
    main()
