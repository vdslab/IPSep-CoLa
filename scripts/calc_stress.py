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


def calculate_stress_for_run(args):
    """単一runのストレス計算を行う"""
    graph, drawing_filepath, nodes = args
    drawing = json.load(open(drawing_filepath))
    s = 0
    for i, j in itertools.combinations(range(len(nodes)), 2):
        d1 = graph.graph["distance"][i][j]
        pos_i = drawing[nodes[i]]
        pos_j = drawing[nodes[j]]
        d2 = math.hypot(pos_i[0] - pos_j[0], pos_i[1] - pos_j[1])
        s += ((d2 - d1) / d1) ** 2
    s /= len(nodes) * (len(nodes) - 1) // 2
    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("out")
    parser.add_argument("--methods", nargs="+", default=["webcola", "sgd"])
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    writer = csv.writer(open(args.out, "w"))
    writer.writerow(["name", "method", "type", "n", "value"])
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
            with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                stress_values = list(executor.map(calculate_stress_for_run, tasks))
            
            # 中央値を計算
            median_stress = np.median(stress_values)
            writer.writerow([row["name"], method, row["type"], row["n"], median_stress])


if __name__ == "__main__":
    main()
