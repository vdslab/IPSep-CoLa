"""NetworkXの無向グラフに対して、ノード順序に基づいて辺に向きを付けるモジュール"""

import argparse
import json
import random
from typing import Optional

import networkx as nx


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

    args = parser.parse_args()

    # グラフを読み込み
    with open(args.input) as f:
        data = json.load(f)

    graph = nx.node_link_graph(data)

    # 無向グラフであることを確認
    if isinstance(graph, nx.DiGraph):
        print("警告: 入力グラフは既に有向グラフです。無向グラフに変換します。")
        graph = graph.to_undirected()

    # 辺に向きを付ける
    directed_graph = orient_edges_by_random_order(graph, seed=args.seed)

    # 結果を保存
    output_data = nx.node_link_data(directed_graph)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"処理完了:")
    print(f"  入力ノード数: {graph.number_of_nodes()}")
    print(f"  入力辺数: {graph.number_of_edges()}")
    print(f"  出力ノード数: {directed_graph.number_of_nodes()}")
    print(f"  出力辺数: {directed_graph.number_of_edges()}")
    print(f"  出力ファイル: {args.output}")


if __name__ == "__main__":
    main()
