import argparse
import json

import egraph as eg
import networkx as nx

from util.graph import nxgraph_to_egDiGraph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--edge-length", default=100, type=int)
    args = parser.parse_args()

    graph: nx.Graph = nx.node_link_graph(json.load(open(args.input)), link="links")

    # 制約データから入次数0のノードを抽出
    constraints = graph.graph.get("constraints", [])
    all_nodes = set(graph.nodes)

    # rightに現れるノード（入次数が1以上）を収集
    nodes_with_incoming = set()
    for constraint in constraints:
        if constraint.get("axis") == "y":
            nodes_with_incoming.add(constraint["right"])

    # 入次数0のノード = 全ノード - rightに現れるノード
    zero_indegree_nodes = list(all_nodes - nodes_with_incoming)

    # 入次数0のノードが存在しない場合は、従来通り次数最大のノードを使用
    if not zero_indegree_nodes:
        degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes]
        deg_max = max([m[1] for m in degree])
        deg_index = [m[1] for m in degree].index(deg_max)
        deg_max_node = list(graph.nodes)[deg_index]
        zero_indegree_nodes = [deg_max_node]

    eggraph, indices = nxgraph_to_egDiGraph(graph, zero_indegree_nodes)

    eg.remove_cycle(eggraph)
    longest = eg.LongestPath()
    nodeidx_layer = longest.assign_layers(eggraph)
    layer_nodeidx = dict()
    for k, v in nodeidx_layer.items():
        layer_nodeidx.setdefault(v, []).append(k)
    constraint = []
    for u, v in graph.edges:
        ul = nodeidx_layer[indices[u]]
        vl = nodeidx_layer[indices[v]]
        left, right = (u, v) if ul < vl else (v, u)
        constraint.append(
            {"axis": "y", "left": left, "right": right, "gap": abs(ul - vl)*args.edge_length}
        )
    graph.graph["constraints"] = constraint
    # graph.graph["layer_constraints"] = constraint
    # 3. NetworkXグラフをJSON形式に適した辞書に変換
    # ノードとリンクのデータ（最も一般的な形式）
    data_for_json = nx.node_link_data(graph)
    # 4. 辞書をJSONファイルとして保存
    import os

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(data_for_json, f, ensure_ascii=False)

    print(f"グラフを '{args.output}' として正常に保存しました。")


if __name__ == "__main__":
    main()
