import json
import os
from argparse import ArgumentParser
from collections import deque
from typing import Protocol

import egraph as eg
import networkx as nx
import scipy.io

from util.graph import nxgraph_to_egDiGraph


class Arg(Protocol):
    dest: str
    data_path: str


def main():
    parser = ArgumentParser()
    parser.add_argument("data_path")
    parser.add_argument("--dest", default=".")
    args: Arg = parser.parse_args()
    # 1. Matrix Marketファイル（.mtx）を読み込む
    # 'your_graph.mtx' の部分はダウンロードしたファイル名に置き換えてください
    try:
        print("load scipy")
        sparse_matrix = scipy.io.mmread(args.data_path)

        # 2. SciPyのスパース行列からNetworkXのグラフオブジェクトを作成
        print("load from networkx")
        G: nx.Graph = nx.from_scipy_sparse_array(sparse_matrix)

        print("remove_loop_and_multi")
        graph = remove_loop_and_multi(G)

        dist = dict(nx.all_pairs_shortest_path_length(graph))
        n = graph.number_of_nodes()
        dist_matrix = [[0] * n for _ in range(n)]
        for i, v in enumerate(list(graph.nodes)):
            for j, u in enumerate(list(graph.nodes)):
                dist_matrix[i][j] = dist[v][u]
        graph.graph["distance"] = dist_matrix

        layer_constraint = manual(graph)
        graph.graph["layer_constraints"] = layer_constraint

        # distance_constraints = get_distance_constraint(graph)
        # graph.graph["distance_constraints"] = distance_constraints

        graph.graph["constraints"] = layer_constraint  # + distance_constraints
        # graph.graph["constraints"] = []
        # 3. NetworkXグラフをJSON形式に適した辞書に変換
        # ノードとリンクのデータ（最も一般的な形式）
        print(" to node link data")
        data_for_json = nx.node_link_data(graph)
        # 4. 辞書をJSONファイルとして保存
        base_name_no_ext = os.path.splitext(os.path.basename(args.data_path))[0]
        file_name = f"{base_name_no_ext}.json"
        print("save")
        with open(os.path.join(args.dest, file_name), "w") as f:
            json.dump(data_for_json, f, ensure_ascii=False)

        print(f"グラフを '{file_name}' として正常に保存しました。")
        print(
            f"ノード数: {graph.number_of_nodes()}, エッジ数: {graph.number_of_edges()}"
        )

    except FileNotFoundError:
        print(
            "エラー: 'your_graph.mtx' が見つかりません。ファイル名を正しく指定してください。"
        )
    except Exception as e:
        print(f"エラーが発生しました: {e}")


def manual(graph: nx.Graph):
    mesh = [
        [301, 302, 303, 304, 305, 306, 283, 284, 285, 286, 287, 288],
        [277, 278, 279, 280, 281, 282, 259, 260, 261, 262, 263, 264],
        [253, 254, 255, 256, 257, 258, 235, 236, 237, 238, 239, 240],
        [229, 230, 231, 232, 233, 234, 211, 212, 213, 214, 215, 216],
        [205, 206, 207, 208, 209, 210, 187, 188, 189, 190, 191, 192],
        [181, 182, 183, 184, 185, 186, 163, 164, 165, 166, 167, 168],
    ]
    mesh = [list(map(str, v)) for v in mesh]
    layer_constraint = []
    for vx in mesh:
        layer_constraint.append({"type": "alignment", "axis": "x", "nodes": vx})
    mesh = list(zip(*mesh))
    for vy in mesh:
        layer_constraint.append({"type": "alignment", "axis": "y", "nodes": vy})
    return layer_constraint


def alignment_vector(graph: nx.Graph):
    mesh = [
        [301, 302, 303, 304, 305, 306, 283, 284, 285, 286, 287, 288],
        [277, 278, 279, 280, 281, 282, 259, 260, 261, 262, 263, 264],
        [253, 254, 255, 256, 257, 258, 235, 236, 237, 238, 239, 240],
        [229, 230, 231, 232, 233, 234, 211, 212, 213, 214, 215, 216],
        [205, 206, 207, 208, 209, 210, 187, 188, 189, 190, 191, 192],
        [181, 182, 183, 184, 185, 186, 163, 164, 165, 166, 167, 168],
    ]
    mesh = [list(map(str, v)) for v in mesh]
    layer_constraint = []
    for vx in mesh:
        layer_constraint.append({"type": "alignment", "nodes": vx})
    mesh = list(zip(*mesh))
    for vy in mesh:
        layer_constraint.append({"type": "alignment", "nodes": vy})
    return layer_constraint


def get_layer_eg(graph: nx.Graph):
    egos = [str(267)]
    eggraph, indices = nxgraph_to_egDiGraph(graph, egos)
    vi = {v: k for k, v in indices.items()}
    eg.remove_cycle(eggraph)
    longest = eg.LongestPath()
    nodeidx_layer = longest.assign_layers(eggraph)
    max_layer = max(nodeidx_layer.values())
    layer_nodeidx = dict()
    for k, v in nodeidx_layer.items():
        layer_nodeidx.setdefault(v, []).append(k)

    dist = dict(nx.all_pairs_shortest_path_length(graph))
    circle_constraint = []
    for i in range(1, max_layer + 1):
        layer_nodeidx[i].sort(key=lambda x: dist[x])
        circle_constraint.append(
            # {
            #     "type": "circle",
            #     "nodes": [vi[j] for j in layer_nodeidx[i]],
            #     "r": i + (1 if len(egos) != 1 else 0),
            #     "center": str(267),
            # }
            # {"axis": "y", "left": v, "right": u, "gap": 2}
        )
    return circle_constraint


def get_layer_constraint(graph: nx.Graph):
    degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes]
    deg_max = max([m[1] for m in degree])
    deg_index = [m[1] for m in degree].index(deg_max)
    deg_max_node = list(graph.nodes)[deg_index]
    layer_constraint = []

    visit = set()
    indices = {node: i for i, node in enumerate(graph.nodes)}
    dist = [-1] * graph.number_of_nodes()
    for node in graph.nodes:
        if node in visit:
            continue
        visit.add(node)
        if graph.degree[node] != 5:
            continue
        dist[indices[node]] = 0
        que = deque([node])
        while que:
            v = que.popleft()
            for u in graph.neighbors(v):
                if u not in visit and dist[indices[u]] < 5 and graph.degree[node] == 5:
                    visit.add(u)
                    que.append(u)
                    layer_constraint.append(
                        {"axis": "y", "left": v, "right": u, "gap": 2}
                    )
                    dist[indices[u]] = dist[indices[v]] + 1

    return layer_constraint


def get_distance_constraint(graph: nx.Graph):
    distance_constraints = []
    nodes = list(graph.nodes)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if i != j:
                distance_constraints.append(
                    {
                        "type": "distance",
                        "left": nodes[i],
                        "left_weight": 0.5,
                        "right": nodes[j],
                        "right_weight": 0.5,
                        "gap": 0.5,
                    }
                )
    return distance_constraints


def remove_loop_and_multi(G: nx.Graph):
    graph = nx.Graph()
    for node in G.nodes:
        graph.add_node(str(node))
    for s, t in G.edges:
        if s == t:
            continue
        graph.add_edge(str(s), str(t), **G.get_edge_data(s, t, default=dict()))
    return graph


if __name__ == "__main__":
    main()
