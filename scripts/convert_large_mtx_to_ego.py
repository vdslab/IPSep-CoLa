# -*- coding: utf-8 -*-
"""
巨大な.mtx形式のグラフデータから、次数が上位の複数のノード（ハブ）を
中心とする指定半径のエゴグラフ（ego-centric graph）を統合し、
単一のJSONファイルとして保存するスクリプト。

統合後のグラフには、中心となったハブのIDリストが記録される。
メモリ効率を考慮し、scipy.sparse行列を活用して大規模データを扱う。
"""

import argparse
import itertools
import json
import os
from typing import Protocol

import networkx as nx
import numpy as np
from scipy.io import mmread, mmwrite
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import shortest_path


class Arg(Protocol):
    MTX_FILE_PATH: str = "data/road_central/road_central.mtx"
    JSON_OUTPUT_PATH: str = "data/graph/road_ego_graph.json"
    NUM_HUBS: int = 3
    EGO_GRAPH_RADIUS: int = 100


def main():
    """
    メイン処理を実行する関数。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("MTX_FILE_PATH")
    parser.add_argument("JSON_OUTPUT_PATH")
    parser.add_argument("NUM_HUBS", type=int)
    parser.add_argument("EGO_GRAPH_RADIUS", type=int)
    args: Arg = parser.parse_args()
    # --- ステップ0: 入力ファイルの確認 ---
    if not os.path.exists(args.MTX_FILE_PATH):
        create_dummy_mtx_file(args.MTX_FILE_PATH)
        print("-" * 30)

    # --- ステップ1: データ読み込み ---
    print(f"グラフデータ '{args.MTX_FILE_PATH}' を読み込んでいます...")
    adj_matrix = mmread(args.MTX_FILE_PATH).tocsr()
    num_nodes = adj_matrix.shape[0]

    if num_nodes != adj_matrix.shape[1]:
        print("エラー: 隣接行列が正方行列ではありません。処理を中断します。")
        return

    print(
        f"読み込み完了。グラフの形状: {adj_matrix.shape}, 非ゼロ要素数: {adj_matrix.nnz}"
    )
    print("-" * 30)

    # --- ステップ2: 次数上位ノードの特定 ---
    print(f"次数が上位 {args.NUM_HUBS} 個のノード（ハブ）を特定しています...")
    degrees = adj_matrix.getnnz(axis=1)

    # 次数に基づいてノードIDを降順にソートし、上位N個を取得
    hub_node_ids = np.argsort(degrees)[::-1][: args.NUM_HUBS]

    print("ハブを特定しました。")
    for i, hub_id in enumerate(hub_node_ids):
        print(f"  - 上位 {i + 1} 位: ノードID {hub_id} (次数: {degrees[hub_id]})")
    print("-" * 30)

    # --- ステップ3: 各エゴグラフを構築し、一つのグラフに統合 ---
    print("各ハブのエゴグラフを構築し、一つのグラフに統合しています...")
    combined_graph = nx.Graph()
    all_ego_nodes = set()

    for hub_node_id in hub_node_ids:
        # 半径内のノード群を取得
        ego_nodes = find_nodes_within_radius(
            adj_matrix, hub_node_id, args.EGO_GRAPH_RADIUS
        )
        all_ego_nodes.update(ego_nodes)

    # 統合後の全ノードをソート済みのリストに変換
    final_nodes = np.array(sorted(list(all_ego_nodes)), dtype=int)
    print(f"統合後の対象となる総ノード数: {len(final_nodes)}")

    # 全ノードを含む部分行列を一度に抽出
    sub_adj_matrix = adj_matrix[final_nodes, :][:, final_nodes]

    # 統合グラフを生成
    combined_graph = nx.from_scipy_sparse_array(sub_adj_matrix)

    # --- ★ここからが別アプローチの修正部分 ---
    if not nx.is_connected(combined_graph):
        print("警告: 統合グラフが非連結です。最大の連結成分のみを抽出します。")
        # 最大の連結成分を見つける
        largest_cc = max(nx.connected_components(combined_graph), key=len)
        # 最大連結成分のみを含むサブグラフを作成
        combined_graph = combined_graph.subgraph(largest_cc).copy()
    # --- ★修正部分ここまで ---

    # ノードIDを元のグラフのIDにマッピングし直す
    mapping = {i: str(original_id) for i, original_id in enumerate(final_nodes)}
    combined_graph = nx.relabel_nodes(combined_graph, mapping)

    # グラフの属性として、中心となったハブのIDリストを保存
    # 抽出後のノードに含まれるハブのみを記録する
    original_hubs = {str(hub_id) for hub_id in hub_node_ids}
    final_hubs = [hub for hub in original_hubs if hub in combined_graph.nodes()]
    combined_graph.graph["egos"] = final_hubs

    print("統合グラフの構築が完了しました。")
    print(f"  - 抽出後のノード数: {combined_graph.number_of_nodes()}")
    print(f"  - 抽出後のエッジ数: {combined_graph.number_of_edges()}")
    print(f"  - 中心ハブのIDリスト: {combined_graph.graph['egos']}")
    print("-" * 30)

    print("距離計算...")
    dist = dict(nx.all_pairs_shortest_path_length(combined_graph))
    n = combined_graph.number_of_nodes()
    dist_matrix = [[0] * n for _ in range(n)]
    for i, v in enumerate(list(combined_graph.nodes)):
        for j, u in enumerate(list(combined_graph.nodes)):
            dist_matrix[i][j] = dist[v][u]
    combined_graph.graph["distance"] = dist_matrix
    combined_graph.graph["constraints"] = []
    # --- ステップ4: 統合グラフをJSON形式で保存 ---
    print(f"統合したエゴグラフを '{args.JSON_OUTPUT_PATH}' に保存しています...")

    graph_data = nx.node_link_data(combined_graph)

    with open(
        os.path.join(args.JSON_OUTPUT_PATH),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(graph_data, f, indent=4, ensure_ascii=False)

    print("保存が完了しました。")
    print("-" * 30)
    print("全ての処理が正常に終了しました。")


def create_dummy_mtx_file(
    file_path, num_nodes=5000, density=0.0005, hub_id=10, hub_degree=500
):
    """
    テスト用のダミー.mtxファイルを生成する関数。
    意図的に次数が大きいハブノードを作成する。
    """
    print(f"'{file_path}' が見つかりません。テスト用のダミーデータを生成します。")

    # ランダムな疎行列を生成
    S = coo_matrix((num_nodes, num_nodes))

    # ハブノードにエッジを集中させる
    hub_neighbors = np.random.choice(np.arange(num_nodes), hub_degree, replace=False)

    # ハブと隣人ノード間のエッジを追加 (双方向)
    row = np.concatenate([np.full(hub_degree, hub_id), hub_neighbors])
    col = np.concatenate([hub_neighbors, np.full(hub_degree, hub_id)])
    data = np.ones(2 * hub_degree, dtype=np.int8)

    # ランダムなエッジも追加
    num_random_edges = int(num_nodes * num_nodes * density)
    random_rows = np.random.randint(0, num_nodes, size=num_random_edges)
    random_cols = np.random.randint(0, num_nodes, size=num_random_edges)
    random_data = np.ones(num_random_edges, dtype=np.int8)

    # 全てのエッジを結合
    S = coo_matrix(
        (
            np.concatenate([data, random_data]),
            (np.concatenate([row, random_rows]), np.concatenate([col, random_cols])),
        ),
        shape=(num_nodes, num_nodes),
    )

    # 対称性を確保し、重複を除去
    S = S.maximum(S.T).tocoo()

    # .mtx形式で保存
    mmwrite(file_path, S)
    print(
        f"ダミーデータ '{file_path}' を生成しました (ノード数: {num_nodes}, ハブ次数: 約{hub_degree})。"
    )


def find_nodes_within_radius(
    adj_matrix: csr_matrix, start_node: int, radius: int
) -> np.ndarray:
    """
    指定されたノードから指定された半径内のすべてのノードをBFSで探索する関数。

    Args:
        adj_matrix (scipy.sparse.csr_matrix): グラフの隣接行列。
        start_node (int): 探索を開始する中心ノードのID。
        radius (int): 探索の半径（ホップ数）。

    Returns:
        numpy.ndarray: 中心ノードと半径内のすべてのノードIDを含むソート済み配列。
    """
    if radius < 0:
        return np.array([], dtype=int)
    if radius == 0:
        return np.array([start_node])

    # 探索済みのノードと、現在の探索の最前線（フロンティア）を管理
    nodes_in_ego_net = {start_node}
    frontier = {start_node}

    for _ in range(radius):
        # 次のフロンティアを計算
        next_frontier = set()
        for node in frontier:
            # csr_matrixのindptrとindicesを使って高速に隣接ノードを取得
            start, end = adj_matrix.indptr[node], adj_matrix.indptr[node + 1]
            neighbors = adj_matrix.indices[start:end]
            next_frontier.update(neighbors)

        # 新しく発見したノードのみを次のフロンティアとする
        frontier = next_frontier - nodes_in_ego_net

        # 新しく見つかったノードをエゴネットに追加
        nodes_in_ego_net.update(frontier)

        # これ以上探索するノードがなければ終了
        if not frontier:
            break

    return np.array(sorted(list(nodes_in_ego_net)), dtype=int)


if __name__ == "__main__":
    main()
