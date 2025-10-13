import argparse
import json

import networkx as nx
import numpy as np


class Arg(argparse.Namespace):
    output: str
    node_size: int
    link_size: int
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


def calc_m(n1: int, m1: int, n2: int) -> int:
    """
    n_1/((n_1 - m_1) m_1) = n_2/((n_2 - m_2) m_2)

    m_2 = (n_1 n_2 - sqrt(n_1) sqrt(n_2) sqrt(-4 n_1 m_1 + n_1 n_2 + 4 m_1^2))/(2 n_1)

    return max(2, min(n2 - 1, round(m_2)))
    """
    import math

    n1n2 = n1 * n2
    b4ab = -4 * n1 * m1 + n1n2 + 4 * m1 * m1
    if b4ab < 0:
        b4ab = 1
    sqrt_b4ab = math.sqrt(b4ab)
    m2_minus = (n1n2 - math.sqrt(n1) * math.sqrt(n2) * sqrt_b4ab) / (2 * n1)
    m2_minus = max(2, min(n2 - 1, round(m2_minus)))
    return m2_minus


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("--node-size", type=int, default=100)
    parser.add_argument("--link-size", type=int, default=2)
    parser.add_argument("--edge-length", type=int, default=20)
    args = parser.parse_args(namespace=Arg)

    graph = nx.barabasi_albert_graph(args.node_size, args.link_size)
    assert nx.is_connected(graph)
    graph = nx.relabel_nodes(graph, lambda x: str(x))

    distance = nx.floyd_warshall_numpy(graph, weight=None)
    graph.graph["distance"] = distance.tolist()
    graph.graph["constraints"] = []
    data = nx.node_link_data(graph)
    json.dump(data, open(args.output, "w"))


def test_create():
    import os

    for n in range(100, 2001, 100):
        tmpdir = os.path.join("baharabi", f"fix_m_{5}")
        output = os.path.join(tmpdir, f"node_{n}.json")
        os.makedirs(tmpdir, exist_ok=True)
        generate(output, n, 5)


def test_gamma():
    import csv
    import os

    with open("baharabi/gamma.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["m", "is_connected", "nodes", "edges", "avg_deg", "gamma"])
    for n in range(100, 1001, 100):
        for m in range(1, 50):
            print("m:", m)
            graph = nx.barabasi_albert_graph(n, m)
            print("is connected:", nx.is_connected(graph))
            print("nodes:", graph.number_of_nodes())
            print("edges:", graph.number_of_edges())
            print("avg_deg:", 2 * graph.number_of_edges() / graph.number_of_nodes())
            gamma = estimate_power_law_exponent(graph)
            print("gamma:", gamma)
            print()
            os.makedirs("baharabi", exist_ok=True)
            # append data
            with open("baharabi/gamma.csv", "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [
                        m,
                        nx.is_connected(graph),
                        graph.number_of_nodes(),
                        graph.number_of_edges(),
                        2 * graph.number_of_edges() / graph.number_of_nodes(),
                        gamma,
                    ]
                )


def generate(output: str, n: int, m: int):
    def create_graph(n, m):
        graph = nx.barabasi_albert_graph(n, m)
        assert nx.is_connected(graph)
        print(
            "m:",
            m,
            "edges:",
            graph.number_of_edges(),
            "avg_deg:",
            2 * graph.number_of_edges() / graph.number_of_nodes(),
        )
        print("is connected:", nx.is_connected(graph))
        graph = nx.relabel_nodes(graph, lambda x: str(x))

        distance = nx.floyd_warshall_numpy(graph, weight=None)
        graph.graph["distance"] = distance.tolist()
        graph.graph["constraints"] = []
        return graph

    graph = create_graph(n, m)
    data = nx.node_link_data(graph)
    json.dump(data, open(output, "w"))


def check_graph(output: str, m: int):
    import os
    import subprocess

    dirname = os.path.dirname(output)
    command = [
        "python",
        "/home/iharuki/school/itohal/IPSep-CoLa/scripts/draw.py",
        output,
        "--dest",
        os.path.join(dirname, "drawing"),
    ]
    subprocess.run(command)
    command = [
        "python",
        "/home/iharuki/school/itohal/IPSep-CoLa/scripts/plot.py",
        output,
        os.path.join(dirname, "drawing", f"graph_{m}.json"),
        os.path.join(dirname, f"plot_{m}.png"),
    ]
    subprocess.run(command)


if __name__ == "__main__":
    # main()
    test_create()
    # test_power_law_generation()
    # test_gamma()
