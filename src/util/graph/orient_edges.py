"""NetworkXの無向グラフに対して、ノード順序に基づいて辺に向きを付けるモジュール"""

import argparse
import json
import random
from typing import Optional

import networkx as nx


def generate_y_gap_constraints(
    graph: nx.Graph, gap: int = 1, seed: Optional[int] = None
) -> dict:
    """
    無向グラフの辺にランダムなノード順序に基づいて向きを付け、y軸のギャップ制約を生成する
    Args:
        graph: NetworkXの無向グラフ
        gap: y軸のギャップ(デフォルトは1)
        seed: 乱数シード(再現性のため、オプション)
    Returns:
        dict: y軸のギャップ制約のリスト
    Example:
        >>> import networkx as nx
        >>> G = nx.Graph()
        >>> G.add_edges_from([(0, 1), (1, 2), (2, 0)])
        >>> constraints = generate_y_gap_constraints(G, gap=2, seed=42)
        >>> isinstance(constraints, list)
        True
    """
    digraph = orient_edges_by_random_order(graph, seed=seed)
    constraints = []
    for u, v in digraph.edges():
        constraints.append({"axis": "y", "left": u, "right": v, "gap": gap})
    return constraints


def orient_edges_by_random_order(
    graph: nx.Graph, seed: Optional[int] = None
) -> nx.DiGraph:
    """
    無向グラフの辺にランダムなノード順序に基づいて向きを付ける

    Args:
        graph: NetworkXの無向グラフ
        seed: 乱数シード(再現性のため、オプション)

    Returns:
        nx.DiGraph: 向き付けされた有向グラフ

    Example:
        >>> import networkx as nx
        >>> G = nx.Graph()
        >>> G.add_edges_from([(0, 1), (1, 2), (2, 0)])
        >>> directed_G = orient_edges_by_random_order(G, seed=42)
        >>> isinstance(directed_G, nx.DiGraph)
        True
    """
    # ノードのリストを取得
    nodes = list(graph.nodes())

    # ランダムにシャッフル
    if seed is not None:
        random.seed(seed)
    random.shuffle(nodes)

    # 各ノードに順序番号を割り当て
    node_order = {node: i for i, node in enumerate(nodes)}

    # 新しい有向グラフを作成
    directed_graph = nx.DiGraph()

    # ノードを追加(属性も保持)
    for node in graph.nodes():
        directed_graph.add_node(node, **graph.nodes[node])

    # 辺を追加(順序が小さい方から大きい方へ)
    for u, v in graph.edges():
        edge_data = graph.get_edge_data(u, v)
        if node_order[u] < node_order[v]:
            directed_graph.add_edge(u, v, **edge_data)
        else:
            directed_graph.add_edge(v, u, **edge_data)

    # グラフ属性も保持
    directed_graph.graph.update(graph.graph)

    return directed_graph


def main():
    """コマンドラインインターフェース"""
    parser = argparse.ArgumentParser(
        description="NetworkXの無向グラフに対して、ランダムなノード順序に基づいて辺に向きを付ける"
    )
    parser.add_argument("input", help="入力JSONファイル(NetworkXのnode-link形式)")
    parser.add_argument("output", help="出力JSONファイル")
    parser.add_argument(
        "--seed", type=int, default=None, help="乱数シード(再現性のため)"
    )

    import os

    args = parser.parse_args()
    dirname = os.path.dirname(args.output)
    os.makedirs(dirname, exist_ok=True)

    # グラフを読み込み
    with open(args.input) as f:
        data = json.load(f)

    graph = nx.node_link_graph(data)

    constraint = generate_y_gap_constraints(graph, gap=1, seed=args.seed)
    if "constraints" not in graph.graph:
        graph.graph["constraints"] = []
    graph.graph["constraints"] += constraint

    # 結果を保存
    with open(args.output, "w") as f:
        json.dump(nx.node_link_data(graph), f)

    print("処理完了:")
    print(f"  入力ファイル: {args.input}")
    print(f"  出力ファイル: {args.output}")


if __name__ == "__main__":
    main()
