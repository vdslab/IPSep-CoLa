"""
このモジュールは、グラフ描画に円制約を適用します。
"""

import math

from .distance_constraints import euclidean_to_hyperbolic, hyperbolic_to_euclidean


def project_circle_constraints(drawing, circle_constraints, indices, centric=True):
    """
    描画に円制約を適用します。

    Args:
        drawing: 制約を適用する描画。
        circle_constraints: 円制約のリスト。各制約は、ノードのリストと円の半径を含むタプルです。
        indices: ノード名をその描画におけるインデックスにマッピングする辞書。

    Returns:
        円の中心のリストと円の半径のリストを含むタプル。
    """

    n = drawing.len()
    x = [drawing.x(j) for j in range(n)]
    y = [drawing.y(j) for j in range(n)]
    if centric:
        centerX = (max(x) + min(x)) / 2
        centerY = (max(y) + min(y)) / 2
        x = [xx - centerX for xx in x]
        y = [yy - centerY for yy in y]
    current_centers = []
    current_radii = []
    for circle_nodes, r, center in circle_constraints:
        if center is None:
            if centric:
                cx = centerX
                cy = centerY
            else:
                cx = sum([x[v] for v in circle_nodes]) / len(circle_nodes)
                cy = sum([y[v] for v in circle_nodes]) / len(circle_nodes)
        else:
            cx = x[center]
            cy = y[center]
        current_centers.append((cx, cy))
        current_radii.append(r)
        for v in circle_nodes:
            dx = x[v] - cx
            dy = y[v] - cy
            d = r - math.hypot(dx, dy)
            theta = math.atan2(dy, dx)
            x[v] += d * math.cos(theta)
            y[v] += d * math.sin(theta)
    for j in range(n):
        drawing.set_x(j, x[j])
        drawing.set_y(j, y[j])
    return current_centers, current_radii


def project_circle_constraints_hyper(
    drawing, circle_constraints, indices, centric=True
):
    import numpy as np

    pos = np.array([[drawing.x(i), drawing.y(i)] for i in range(drawing.len())])
    pos = hyperbolic_to_euclidean(pos)
    for i in range(drawing.len()):
        drawing.set_x(i, pos[i][0])
        drawing.set_y(i, pos[i][1])
    current_centers, current_radii = project_circle_constraints(
        drawing, circle_constraints, indices, centric
    )

    pos = np.array([[drawing.x(i), drawing.y(i)] for i in range(drawing.len())])
    pos = euclidean_to_hyperbolic(pos)
    for i in range(drawing.len()):
        drawing.set_x(i, pos[i][0])
        drawing.set_y(i, pos[i][1])
    return current_centers, current_radii


def project_spherical_constraints(drawing, circle_constraints):
    """
    描画に球面上の円制約を適用します。
    ノードを指定された中心点からの角距離が一定になるように配置します。

    Args:
        drawing: 制約を適用する描画オブジェクト。
                 lat(index), lon(index), set_lat(index, val), set_lon(index, val), len()
                 のメソッドを持つことを想定します。角度の単位はラジアンです。
        circle_constraints: 円制約のリスト。
                            各制約は (node_indices, radius, center_node_index) のタプルです。
                            - node_indices: 円周上に配置するノードのインデックスのリスト。
                            - radius: 円の半径（角距離、ラジアン単位）。
                            - center_node_index: 中心のノードのインデックス。Noneの場合は重心を計算します。

    Returns:
        (list, list): 円の中心座標（(緯度, 経度)のタプル）のリストと、円の半径のリスト。
    """

    # --- ヘルパー関数 ---

    def calculate_bearing(lat1, lon1, lat2, lon2):
        """2点間の最初の方位角を計算します。"""
        delta_lon = lon2 - lon1
        y = math.sin(delta_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
            lat2
        ) * math.cos(delta_lon)
        return math.atan2(y, x)

    def find_destination_point(lat, lon, bearing, distance):
        """始点、方位角、距離から目的地の座標を計算します。"""
        lat2 = math.asin(
            math.sin(lat) * math.cos(distance)
            + math.cos(lat) * math.sin(distance) * math.cos(bearing)
        )
        lon2 = lon + math.atan2(
            math.sin(bearing) * math.sin(distance) * math.cos(lat),
            math.cos(distance) - math.sin(lat) * math.sin(lat2),
        )
        return lat2, lon2

    # --- メイン処理 ---

    current_centers = []
    current_radii = []

    for node_indices, r, center_index in circle_constraints:
        # 1. 中心の緯度・経度を決定
        if center_index is not None:
            # 中心ノードが指定されている場合
            center_lat = drawing.lat(center_index)
            center_lon = drawing.lon(center_index)
        else:
            # 中心が指定されていない場合、ノード群の球面上の重心を計算
            if not node_indices:
                # 対象ノードがない場合は原点を中心とする
                center_lat, center_lon = 0.0, 0.0
            else:
                # 3Dデカルト座標に変換して平均ベクトルを求める
                avg_x, avg_y, avg_z = 0, 0, 0
                for v_idx in node_indices:
                    lat_v, lon_v = drawing.lat(v_idx), drawing.lon(v_idx)
                    avg_x += math.cos(lat_v) * math.cos(lon_v)
                    avg_y += math.cos(lat_v) * math.sin(lon_v)
                    avg_z += math.sin(lat_v)

                count = len(node_indices)
                avg_x /= count
                avg_y /= count
                avg_z /= count

                # 平均ベクトルを緯度・経度に戻す
                center_lon = math.atan2(avg_y, avg_x)
                hyp = math.sqrt(avg_x**2 + avg_y**2)
                center_lat = math.atan2(avg_z, hyp)

        current_centers.append((center_lat, center_lon))
        current_radii.append(r)

        # 2. 対象ノードを円周上に再配置
        for v_idx in node_indices:
            node_lat, node_lon = drawing.lat(v_idx), drawing.lon(v_idx)

            # 中心から見た現在の方位角を計算
            bearing = calculate_bearing(center_lat, center_lon, node_lat, node_lon)

            # 中から同じ方位角で、距離rの位置にある新しい座標を計算
            new_lat, new_lon = find_destination_point(
                center_lat, center_lon, bearing, r
            )

            # 新しい座標を一時的に保存
            drawing.set_lat(v_idx, new_lat)
            drawing.set_lon(v_idx, new_lon)

    return current_centers, current_radii
