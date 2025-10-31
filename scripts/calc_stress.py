import argparse
import csv
import itertools
import json
import math
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor

import networkx as nx
import numpy as np

from util.scale_normalized_stress import _pairwise_euclidean, scale_normalized_stress


def calculate_stress_for_run(args):
    """単一runのSNS計算を行う"""
    graph, drawing_filepath, nodes = args
    drawing = json.load(open(drawing_filepath))

    # 高次元距離行列（グラフの最短路距離）
    D_high = np.array(graph.graph["distance"], dtype=np.float64)

    # 低次元距離行列（描画座標から計算）
    P_low = np.array([drawing[node] for node in nodes], dtype=np.float64)
    D_low = _pairwise_euclidean(P_low)

    # SNS と α* を計算
    sns, alpha_star = scale_normalized_stress(D_high, D_low)

    return sns, alpha_star


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("out")
    parser.add_argument("--methods", nargs="+", default=["webcola", "sgd"])
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    writer = csv.writer(open(args.out, "w"))
    writer.writerow(["name", "method", "type", "n", "value", "alpha_star"])
    data = [row for row in csv.DictReader(open(args.csv_file))]
    methods = args.methods
    for method in methods:
        for row in data:
            graph_filepath = os.path.join(os.path.dirname(args.csv_file), row["path"])
            print("\r", method, graph_filepath, f"{int(row['n']):0>4}")
            graph = nx.node_link_graph(json.load(open(graph_filepath)))
            nodes = list(graph.nodes)

            # 10回の実行結果からストレスを計算（並列実行）
            tasks = []
            for run in range(10):
                # ファイル名から.jsonを除去してrun番号を追加
                name_without_ext = row["name"].replace(".json", "")
                drawing_filepath = (
                    f"data/drawing/{method}/{row['type']}/{int(row['n']):0>4}/"
                    f"{name_without_ext}_run_{run}.json"
                )
                tasks.append((graph, drawing_filepath, nodes))

            # 並列実行
            with ProcessPoolExecutor(
                max_workers=multiprocessing.cpu_count()
            ) as executor:
                results = list(executor.map(calculate_stress_for_run, tasks))

            # SNS と α* をそれぞれ分離
            sns_values = [r[0] for r in results]
            alpha_values = [r[1] for r in results]

            # 中央値を計算
            median_sns = np.median(sns_values)
            median_alpha = np.median(alpha_values)
            writer.writerow(
                [row["name"], method, row["type"], row["n"], median_sns, median_alpha]
            )


if __name__ == "__main__":
    main()
