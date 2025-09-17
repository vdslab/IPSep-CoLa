import argparse
import cmath
import json
import os

import networkx as nx

from util.graph.plot import plot_graph


def poincare_transform(z: complex, z0: complex) -> complex:
    """
    ポアンカレディスク上の点zを、z0が中心に来るように変換します。

    Args:
        z (complex): 変換したい点。
        z0 (complex): 新しい中心となる点。abs(z0) < 1 である必要があります。

    Returns:
        complex: 変換後の点の位置。
    """
    # z0は必ずディスクの内側の点でなければならない
    assert abs(z0) < 1, "The new center z0 must be inside the unit disk."

    # 複素共役を計算
    z0_conjugate = z0.conjugate()

    # 画像で示された数式を計算
    numerator = z - z0
    denominator = 1 - z0_conjugate * z

    # ゼロ除算を避ける
    if denominator == 0:
        # このケースはzとz0がディスク内部にある限り通常発生しません
        return float("inf")

    return numerator / denominator


def change_center(pos: dict, new_center: tuple) -> dict:
    """
    ポアンカレディスク上の描画位置を、新しい中心に基づいて変換します。

    Args:
        pos (dict): ノードIDをキー、(x, y)のタプルを値とする辞書。
        new_center (tuple): 新しい中心の座標 (x0, y0)。abs(x0 + iy0) < 1 である必要があります。

    Returns:
        dict: 変換後のノード位置の辞書。
    """
    x0, y0 = new_center
    z0 = complex(x0, y0)
    assert abs(z0) < 1, "The new center must be inside the unit disk."

    new_pos = {}
    xmin = float("inf")
    ymin = float("inf")
    for node, (x, y) in pos.items():
        z = complex(x, y)
        z_transformed = poincare_transform(z, z0)
        new_pos[node] = (z_transformed.real, z_transformed.imag)
        xmin = min(xmin, z_transformed.real)
        ymin = min(ymin, z_transformed.imag)

    new_pos = {node: (x - xmin, y - ymin) for node, (x, y) in new_pos.items()}
    return new_pos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph_file")
    parser.add_argument("drawing_file")
    parser.add_argument("output")
    parser.add_argument("--center", type=int, default=0)

    args = parser.parse_args()

    graph = nx.node_link_graph(json.load(open(args.graph_file)))
    pos = json.load(open(args.drawing_file))
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    # n = graph.graph["egos"][0]
    # print(n, graph.graph["egos"])
    # pos = change_center(pos, pos[n])
    print(args.center, list(graph.nodes)[args.center], graph.graph["egos"])
    pos = change_center(pos, pos[list(graph.nodes)[args.center]])
    plot_graph(graph, pos, args.output)


if __name__ == "__main__":
    main()
