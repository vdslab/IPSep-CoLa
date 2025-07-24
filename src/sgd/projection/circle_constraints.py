"""
このモジュールは、グラフ描画に円制約を適用します。
"""


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
    import math

    n = drawing.len()
    x = [drawing.x(j) for j in range(n)]
    y = [drawing.y(j) for j in range(n)]
    if centric:
        centerX = (max(x) + min(x)) / 2
        centerY = (max(y) + min(y)) / 2
        x = [centerX - xx for xx in x]
        y = [centerY - yy for yy in y]
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
