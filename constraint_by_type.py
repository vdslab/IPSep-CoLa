import json
from collections import deque

import networkx as nx
import scipy.io

# 1. Matrix Marketファイル（.mtx）を読み込む
# 'your_graph.mtx' の部分はダウンロードしたファイル名に置き換えてください
try:
    sparse_matrix = scipy.io.mmread("data/graph/1138_bus.mtx")

    # 2. SciPyのスパース行列からNetworkXのグラフオブジェクトを作成
    G: nx.Graph = nx.from_scipy_sparse_array(sparse_matrix)
    graph = nx.Graph()
    for node in G.nodes:
        graph.add_node(str(node))
    for s, t in G.edges:
        if s == t:
            continue
        graph.add_edge(str(s), str(t), **G.get_edge_data(s, t, default=dict()))
    dist = dict(nx.all_pairs_shortest_path_length(graph))
    n = graph.number_of_nodes()
    dist_matrix = [[0] * n for _ in range(n)]
    for i, v in enumerate(list(graph.nodes)):
        for j, u in enumerate(list(graph.nodes)):
            dist_matrix[i][j] = dist[v][u]
    graph.graph["distance"] = dist_matrix

    degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes]
    deg_max = max([m[1] for m in degree])
    deg_index = [m[1] for m in degree].index(deg_max)
    deg_max_node = list(graph.nodes)[deg_index]
    que = deque([deg_max_node])
    visit = set([deg_max_node])
    layer_constraint = []
    while que:
        v = que.popleft()
        for u in graph.neighbors(v):
            if u not in visit:
                visit.add(u)
                que.append(u)
                layer_constraint.append({"axis": "y", "left": v, "right": u, "gap": 2})
    graph.graph["layer_constraints"] = layer_constraint

    distance_constraints = []
    nodes = list(graph.nodes)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if i != j:
                distance_constraints.append(
                    {
                        "type": "distance",
                        "left": nodes[i],
                        "right": nodes[j],
                        "gap": 0.5,
                    }
                )
    graph.graph["distance_constraints"] = distance_constraints

    graph.graph["constraints"] = layer_constraint + distance_constraints
    # 3. NetworkXグラフをJSON形式に適した辞書に変換
    # ノードとリンクのデータ（最も一般的な形式）
    data_for_json = nx.node_link_data(graph)
    # 4. 辞書をJSONファイルとして保存
    with open("1138_bus.json", "w") as f:
        json.dump(data_for_json, f, ensure_ascii=False)

    print("グラフを '1138_bus.json' として正常に保存しました。")
    print(f"ノード数: {graph.number_of_nodes()}, エッジ数: {graph.number_of_edges()}")


except FileNotFoundError:
    print(
        "エラー: 'your_graph.mtx' が見つかりません。ファイル名を正しく指定してください。"
    )
except Exception as e:
    print(f"エラーが発生しました: {e}")
