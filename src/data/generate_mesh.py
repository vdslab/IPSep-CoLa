import json

import networkx as nx


def create_toroidal_grid_graph_data(width, height):
    """
    各行の端がつながったメッシュ状のグラフを生成し、
    node_link_data形式で返す関数。

    Args:
        width (int): グリッドの幅
        height (int): グリッドの高さ

    Returns:
        dict: node_link_data形式のグラフデータ
    """
    # 1. 行方向(第一次元)が周期的なグリッドグラフを生成
    # periodic=(True, False)は、第一次元(幅)を周期的、第二次元(高さ)を非周期的と設定
    # デフォルトのノード名は (x, y) のようなタプルになります
    G: nx.Graph = nx.grid_graph(dim=[width, height], periodic=(False, False))

    # 2. ノード名を文字列に変換
    # 例: (0, 1) -> "0-1"
    # relabel_nodes関数で一括変換します
    mapping = {node: f"{node[0]}-{node[1]}" for node in G.nodes()}
    G_relabeled = nx.relabel_nodes(G, mapping)
    G_relabeled.add_edge(f"0-{width - 1}", "0-0")
    dist = dict(nx.all_pairs_shortest_path_length(G_relabeled))
    n = G_relabeled.number_of_nodes()
    dist_matrix = [[0] * n for _ in range(n)]
    for i, v in enumerate(list(G_relabeled.nodes)):
        for j, u in enumerate(list(G_relabeled.nodes)):
            dist_matrix[i][j] = dist[v][u]
    G_relabeled.graph["distance"] = dist_matrix
    G_relabeled.graph["constraints"] = []
    # 3. node_link_data形式に変換して返す
    return nx.node_link_data(G_relabeled)


# --- ここから実行 ---

# グラフのサイズを設定 (4x3のグリッド)
grid_width = 12
grid_height = 6

# グラフデータを生成
graph_data = create_toroidal_grid_graph_data(grid_width, grid_height)

# 結果を整形して表示
print(
    json.dump(
        graph_data, open(f"data/graph/mesh_w{grid_width}_h{grid_height}.json", "w")
    )
)
