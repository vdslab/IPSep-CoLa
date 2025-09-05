import argparse
import csv
import itertools
import json
import math
import os

import networkx as nx


def constraint_violation(graph, drawing):
    if len(graph.graph["constraints"]) == 0:
        return 0
    nodes = list(graph.nodes)
    s = 0
    for constraint in graph.graph["constraints"]:
        u = nodes[constraint["left"]]
        v = nodes[constraint["right"]]
        gap = constraint["gap"]
        if constraint["axis"] == "x":
            s += max(0, gap - (drawing[v][0] - drawing[u][0]))
        else:
            s += max(0, gap - (drawing[v][1] - drawing[u][1]))
    s /= len(graph.graph["constraints"])
    return s


def overlap_violation(graph, drawing):
    nodes = list(graph.nodes)
    r = graph.nodes[nodes[0]]["shape"]["width"] + 5
    s = 0
    node_pairs = list(itertools.combinations(nodes, 2))

    for u, v in node_pairs:
        pos_u = drawing[u]
        pos_v = drawing[v]

        # 2点間のユークリッド距離を計算
        dist = math.hypot(pos_v[0] - pos_u[0], pos_v[1] - pos_u[1])

        # 違反量を計算: 本来あるべき距離 (2 * r) よりどれだけ近いか
        violation = max(0, 2 * r - dist)
        s += violation

    # 違反量の合計をペアの総数で割り、平均値を返す
    return s / len(node_pairs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("out")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    writer = csv.writer(open(args.out, "w"))
    writer.writerow(["name", "method", "type", "n", "value"])
    data = [row for row in csv.DictReader(open(args.csv_file))]
    methods = ["sgd", "unicon"]
    for method in methods:
        for row in data:
            graph_filepath = os.path.join(os.path.dirname(args.csv_file), row["path"])
            graph = nx.node_link_graph(json.load(open(graph_filepath)))
            print(method, graph_filepath)
            drawing_filepath = (
                f"data/drawing/{method}/{row['type']}/{row['n']}/{row['name']}"
            )
            drawing = json.load(open(drawing_filepath))
            # s = constraint_violation(graph, drawing)
            s = overlap_violation(graph, drawing)
            writer.writerow([row["name"], method, row["type"], row["n"], s])


def test_overlap_violation():
    """
    overlap_violation 関数の動作をテストする。
    """
    # --- テスト用のグラフと描画データを作成 ---
    G = nx.Graph()
    # shape["width"]が10のノードを3つ追加
    # この場合、r = 10 + 5 = 15 となり、ノードが接するためには 2 * r = 30 の距離が必要
    G.add_node("A", shape={"width": 10})
    G.add_node("B", shape={"width": 10})
    G.add_node("C", shape={"width": 10})

    print("--- overlap_violationのテストを開始 ---")

    # ケース1: 重なりが全くない場合 -> 違反量は0
    drawing1 = {"A": [0, 0], "B": [30, 0], "C": [0, 30]}
    # A-B dist=30, A-C dist=30, B-C dist>30 -> 全ペアの違反量0
    # 合計違反量 0 / 3ペア = 0
    d1s = overlap_violation(G, drawing1)
    assert math.isclose(d1s, 0.0), f"ケース1に失敗 {d1s}"
    print("✅ ケース1（重なりなし）: パス")

    # ケース2: 2つのノードが完全に重なっている場合
    drawing2 = {"A": [0, 0], "B": [0, 0], "C": [100, 100]}
    # A-B dist=0 -> 違反量30
    # A-C, B-C dist>30 -> 違反量0
    # 合計違反量 30 / 3ペア = 10
    assert math.isclose(overlap_violation(G, drawing2), 10.0), "ケース2に失敗"
    print("✅ ケース2（完全な重なり）: パス")

    # ケース3: 2つのノードが部分的に重なっている場合
    drawing3 = {"A": [0, 0], "B": [15, 0], "C": [100, 100]}
    # A-B dist=15 -> 違反量 (30-15) = 15
    # A-C, B-C dist>30 -> 違反量0
    # 合計違反量 15 / 3ペア = 5
    assert math.isclose(overlap_violation(G, drawing3), 5.0), "ケース3に失敗"
    print("✅ ケース3（部分的な重なり）: パス")

    # ケース4: 複数のペアで重なりがある場合
    drawing4 = {"A": [0, 0], "B": [15, 0], "C": [0, 15]}
    # A-B dist=15 -> 違反量15
    # A-C dist=15 -> 違反量15
    # B-C dist=sqrt(15^2+15^2) ~= 21.21 -> 違反量 (30 - 21.21) ~= 8.78
    # 合計違反量 (15 + 15 + (30 - 15 * math.sqrt(2))) / 3ペア
    expected_value = (60 - 15 * math.sqrt(2)) / 3
    assert math.isclose(overlap_violation(G, drawing4), expected_value), "ケース4に失敗"
    print("✅ ケース4（複数の重なり）: パス")

    print("--- 全てのテストに成功しました！ ---")


if __name__ == "__main__":
    # test_overlap_violation()
    main()
