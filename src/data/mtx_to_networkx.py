import argparse
import json
import os

import networkx as nx
import scipy.io


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="+")
    args = parser.parse_args()

    for file_path in args.input:
        # 1. Matrix Marketファイル（.mtx）を読み込む
        # 'your_graph.mtx' の部分はダウンロードしたファイル名に置き換えてください
        try:
            sparse_matrix = scipy.io.mmread(file_path)

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
            graph.graph["constraints"] = []
            # graph.graph["layer_constraints"] = constraint
            # 3. NetworkXグラフをJSON形式に適した辞書に変換
            # ノードとリンクのデータ（最も一般的な形式）
            data_for_json = nx.node_link_data(graph)
            # 4. 辞書をJSONファイルとして保存

            basename = os.path.splitext(os.path.basename(file_path))[0]
            dirname = os.path.dirname(file_path)
            outfile = os.path.join(dirname, f"{basename}.json")
            with open(outfile, "w") as f:
                json.dump(data_for_json, f, ensure_ascii=False)

            print(f"グラフを '{outfile}' として正常に保存しました。")
            print(
                f"ノード数: {graph.number_of_nodes()}, エッジ数: {graph.number_of_edges()}"
            )
        except Exception as e:
            print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
