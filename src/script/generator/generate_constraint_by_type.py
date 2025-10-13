import json
from collections import deque

import egraph as eg
import networkx as nx
import scipy.io

from util.graph import nxgraph_to_egDiGraph

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

    eggraph, indices = nxgraph_to_egDiGraph(graph, [deg_max_node])
    vi = {v: k for k, v in indices.items()}

    eg.remove_cycle(eggraph)
    longest = eg.LongestPath()
    nodeidx_layer = longest.assign_layers(eggraph)
    max_layer = max(nodeidx_layer.values())
    layer_nodeidx = dict()
    for k, v in nodeidx_layer.items():
        layer_nodeidx.setdefault(v, []).append(k)
    constraint = []
    for u, v in graph.edges:
        ul = nodeidx_layer[indices[u]]
        vl = nodeidx_layer[indices[v]]
        left, right = (u, v) if ul < vl else (v, u)
        constraint.append(
            {"axis": "y", "left": left, "right": right, "gap": abs(ul - vl)}
        )
    graph.graph["constraints"] = constraint
    # graph.graph["layer_constraints"] = constraint
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
