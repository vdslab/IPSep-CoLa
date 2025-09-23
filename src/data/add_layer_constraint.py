import argparse
import json

import egraph as eg
import networkx as nx

from util.graph import nxgraph_to_egDiGraph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    graph: nx.Graph = nx.node_link_graph(json.load(open(args.input)), link="links")

    degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes]
    deg_max = max([m[1] for m in degree])
    deg_index = [m[1] for m in degree].index(deg_max)
    deg_max_node = list(graph.nodes)[deg_index]

    eggraph, indices = nxgraph_to_egDiGraph(graph, [deg_max_node])

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
            {"axis": "y", "left": left, "right": right, "gap": abs(ul - vl)}
        )
    graph.graph["constraints"] = constraint
    # graph.graph["layer_constraints"] = constraint
    # 3. NetworkXグラフをJSON形式に適した辞書に変換
    # ノードとリンクのデータ（最も一般的な形式）
    data_for_json = nx.node_link_data(graph)
    # 4. 辞書をJSONファイルとして保存
    with open(args.output, "w") as f:
        json.dump(data_for_json, f, ensure_ascii=False)

    print(f"グラフを '{args.output}' として正常に保存しました。")


if __name__ == "__main__":
    main()
