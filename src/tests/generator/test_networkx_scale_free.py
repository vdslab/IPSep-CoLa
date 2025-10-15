import json
import os
import tempfile
import unittest

import networkx as nx

from script.generator.networkx_scale_free import main


class TestNetworkxScaleFree(unittest.TestCase):
    def setUp(self):
        """各テストの前処理"""
        print("setUp", self._testMethodName)
        # 一時ディレクトリを作成
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """各テストの後処理"""
        # 一時ディレクトリとその中身を削除
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_generate_creates_valid_graph(self):
        """generate関数が正しくグラフを生成することを確認"""
        output_path = os.path.join(self.test_dir, "test_graph.json")
        n = 50
        m = 3

        # グラフを生成
        generate(output_path, n, m)

        # ファイルが作成されたことを確認
        self.assertTrue(os.path.exists(output_path))

        # JSONファイルを読み込み
        with open(output_path, "r") as f:
            data = json.load(f)

        # 基本的な構造を確認
        self.assertIn("nodes", data)
        self.assertIn("links", data)
        self.assertIn("graph", data)

        # ノード数を確認
        self.assertEqual(len(data["nodes"]), n)

        # グラフメタデータを確認
        self.assertIn("distance", data["graph"])
        self.assertIn("constraints", data["graph"])

    def test_generate_graph_properties(self):
        """生成されたグラフの性質を確認"""
        output_path = os.path.join(self.test_dir, "test_graph.json")
        n = 100
        m = 5

        # グラフを生成
        generate(output_path, n, m)

        # JSONファイルを読み込み
        with open(output_path, "r") as f:
            data = json.load(f)

        # NetworkXグラフに変換
        graph = nx.node_link_graph(data)

        # 連結グラフであることを確認
        self.assertTrue(nx.is_connected(graph))

        # ノード数を確認
        self.assertEqual(graph.number_of_nodes(), n)

    def test_generate_distance_matrix(self):
        """距離行列が正しく計算されていることを確認"""
        output_path = os.path.join(self.test_dir, "test_graph.json")
        n = 20
        m = 2

        # グラフを生成
        generate(output_path, n, m)

        # JSONファイルを読み込み
        with open(output_path, "r") as f:
            data = json.load(f)

        # 距離行列を確認
        distance = data["graph"]["distance"]
        self.assertEqual(len(distance), n)
        self.assertEqual(len(distance[0]), n)

        # 対角成分が0であることを確認
        for i in range(n):
            self.assertEqual(distance[i][i], 0)

        # 対称行列であることを確認
        for i in range(n):
            for j in range(n):
                self.assertEqual(distance[i][j], distance[j][i])

    def test_generate_multiple_graphs(self):
        """複数のグラフを生成できることを確認（test_create関数と同様）"""
        for n in [50, 100]:
            for m in [3, 5]:
                output_path = os.path.join(self.test_dir, f"graph_n{n}_m{m}.json")
                generate(output_path, n, m)

                # ファイルが作成されたことを確認
                self.assertTrue(os.path.exists(output_path))

                # JSONファイルを読み込み
                with open(output_path, "r") as f:
                    data = json.load(f)

                # ノード数を確認
                self.assertEqual(len(data["nodes"]), n)

    def test_generate_node_labels_are_strings(self):
        """ノードラベルが文字列であることを確認"""
        output_path = os.path.join(self.test_dir, "test_graph.json")
        n = 30
        m = 2

        # グラフを生成
        generate(output_path, n, m)

        # JSONファイルを読み込み
        with open(output_path, "r") as f:
            data = json.load(f)

        # すべてのノードIDが文字列であることを確認
        for node in data["nodes"]:
            self.assertIsInstance(node["id"], str)

        # すべてのエッジのsource/targetが文字列であることを確認
        for link in data["links"]:
            self.assertIsInstance(link["source"], str)
            self.assertIsInstance(link["target"], str)


def generate(output: str, n: int):
    def trim_graph(graph: nx.DiGraph) -> nx.Graph:
        """多重辺、自己ループを削除する"""
        simple_graph = nx.Graph()
        simple_graph.add_nodes_from(graph.nodes(data=True))
        edges = [
            (u, v, d)
            for u, v, d in graph.edges(data=True)
            if u != v and not simple_graph.has_edge(u, v)
        ]
        simple_graph.add_edges_from(edges)
        return simple_graph

    def create_graph(n):
        graph = nx.scale_free_graph(n)
        graph = trim_graph(graph)
        if not nx.is_connected(graph):
            raise ValueError("生成されたグラフが連結ではありません")
        print(
            "nodes:",
            graph.number_of_nodes(),
            "edges:",
            graph.number_of_edges(),
            "avg_deg:",
            2 * graph.number_of_edges() / graph.number_of_nodes(),
        )
        print("is connected:", nx.is_connected(graph))
        graph = nx.relabel_nodes(graph, lambda x: str(x))

        distance = nx.floyd_warshall_numpy(graph, weight=None)
        graph.graph["distance"] = distance.tolist()
        graph.graph["constraints"] = []
        return graph

    for i in range(10):
        try:
            graph = create_graph(n)
            break
        except ValueError:
            if i == 9:
                raise
            print("再試行", i + 1)
    data = nx.node_link_data(graph)
    with open(output, "w") as f:
        json.dump(data, f)


def check_graph(output: str):
    import os
    import subprocess

    dirname = os.path.dirname(output)
    basename = os.path.basename(output)
    command = [
        "python",
        "/home/iharuki/school/itohal/IPSep-CoLa/scripts/draw.py",
        output,
        "--dest",
        os.path.join(dirname, "drawing"),
    ]
    subprocess.run(command)
    command = [
        "python",
        "/home/iharuki/school/itohal/IPSep-CoLa/scripts/plot.py",
        output,
        os.path.join(dirname, "drawing", basename),
        os.path.join(dirname, "plot.png"),
    ]
    subprocess.run(command)


def test_create():
    import os

    for n in range(100, 2001, 100):
        tmpdir = os.path.join("data", "graph", "scale_free")
        output = os.path.join(tmpdir, f"node_{n:0>4}.json")
        os.makedirs(tmpdir, exist_ok=True)
        generate(output, n)
        # check_graph(output)


if __name__ == "__main__":
    # unittest.main()
    test_create()
