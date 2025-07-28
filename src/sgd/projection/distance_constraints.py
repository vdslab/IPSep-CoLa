import numpy as np


def euclidean_to_hyperbolic(coords: np.ndarray) -> np.ndarray:
    """
    ユークリッド空間の2次元座標を双曲空間（ポアンカレ円板）の座標に変換します。

    この実装では、ユークリッド空間での原点からの距離を、そのまま双曲空間での
    距離として扱い、ポアンカレ円板モデル上の座標に変換します。

    Args:
        coords: ユークリッド座標の配列 (shape: [N, 2])

    Returns:
        双曲座標（ポアンカレ円板）の配列 (shape: [N, 2])
    """
    # ユークリッド空間での原点からの距離を計算
    norm = np.linalg.norm(coords, axis=1, keepdims=True)

    # ゼロ除算を避けるためのマスク
    mask = norm > 1e-9

    # ポアンカレ円板上の座標を計算
    # 双曲半径 r_h = tanh(r_e / 2) を用いてスケーリング
    # u = tanh(norm/2) * (x / norm)
    # v = tanh(norm/2) * (y / norm)
    # 係数 scale = tanh(norm / 2) / norm
    scale = np.zeros_like(norm)
    scale[mask] = np.tanh(norm[mask] / 2.0) / norm[mask]

    hyperbolic_coords = coords * scale

    return hyperbolic_coords


import numpy as np


def hyperbolic_to_euclidean(coords: np.ndarray) -> np.ndarray:
    """
    双曲空間（ポアンカレ円板）の座標をユークリッド空間の2次元座標に変換します。

    Args:
        coords: 双曲座標（ポアンカレ円板）の配列 (shape: [N, 2])

    Returns:
        ユークリッド座標の配列 (shape: [N, 2])
    """
    coords = np.array(coords)
    # print(coords)
    # ポアンカレ円板上での原点からの距離を計算
    norm = np.linalg.norm(coords, axis=1, keepdims=True)

    # ゼロ除算と定義域外エラー(|z|>=1)を避けるためのマスク
    # ポアンカレ円板の点は |z|<1 の範囲にある
    mask = (norm > 1e-9) & (norm < 1.0)

    # ユークリッド空間の座標を計算
    # ユークリッド距離 r_e = 2 * arctanh(r_h) を用いてスケーリング
    # x = (2 * arctanh(norm)) * (u / norm)
    # y = (2 * arctanh(norm)) * (v / norm)
    # 係数 scale = 2 * arctanh(norm) / norm
    scale = np.zeros_like(norm)
    scale[mask] = (2.0 * np.arctanh(norm[mask])) / norm[mask]

    euclidean_coords = coords * scale

    return euclidean_coords


def hyperbolic_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """
    ポアンカレ円板モデルにおける2点間の双曲距離を計算します。

    Args:
        p1: 1点目の座標 (shape: [2,])
        p2: 2点目の座標 (shape: [2,])

    Returns:
        2点間の双曲距離
    """
    norm_p1_sq = np.sum(p1**2)
    norm_p2_sq = np.sum(p2**2)
    norm_diff_sq = np.sum((p1 - p2) ** 2)

    # 浮動小数点数エラーを避けるために分母が0に近づかないようにクリップ
    denominator = (1.0 - norm_p1_sq) * (1.0 - norm_p2_sq)
    if denominator <= 1e-9:
        # 一方または両方の点が円板の境界上または外側にある場合、距離は無限大として扱います。
        return np.inf

    # arccosh の引数は1以上でなければなりません。
    argument = 1.0 + 2.0 * norm_diff_sq / denominator
    if argument < 1.0:
        # 浮動小数点数エラーにより引数が1未満になる場合があるため対処します。
        argument = 1.0

    return np.arccosh(argument)


def translate_hyperbolic_space(
    coords: np.ndarray, center_node_coords: np.ndarray
) -> np.ndarray:
    """
    特定のノードが中心(0,0)に来るように、双曲空間全体を移動（変換）します。

    この処理は以下の手順で行われます：
    1. 全ての双曲座標と中心ノードの座標をユークリッド座標に変換します。
    2. ユークリッド空間で、中心ノードが原点(0,0)に移動するように、全ての点を平行移動します。
    3. 平行移動後の全ユークリッド座標を、再び双曲座標に変換します。

    これにより、双曲的な距離関係を保ったまま、視点の中心を移動させる効果が得られます。

    Args:
        coords (np.ndarray): 移動対象となる双曲座標の配列 (shape: [N, 2])
        center_node_coords (np.ndarray): 新しい中心としたいノードの現在の双曲座標 (shape: [2,])

    Returns:
        np.ndarray: 移動後の新しい双曲座標の配列 (shape: [N, 2])
    """
    # 1. 中心ノードの双曲座標をユークリッド座標に変換します。
    #    関数が (N, 2) の入力を期待するため、reshape/flatten を使用します。
    center_euclidean = hyperbolic_to_euclidean(
        center_node_coords.reshape(1, 2)
    ).flatten()

    # 2. 移動対象の全ノードの双曲座標をユークリッド座標に変換します。
    all_euclidean = hyperbolic_to_euclidean(coords)

    # 3. 全ての点をユークリッド空間で平行移動します。
    translated_euclidean = all_euclidean - center_euclidean

    # 4. 平行移動後のユークリッド座標を双曲座標に変換して返します。
    new_hyperbolic_coords = euclidean_to_hyperbolic(translated_euclidean)

    return new_hyperbolic_coords


def project_distance_constraints(drawing, constraints, indices):
    for _ in range(5):
        for v, u, gap in constraints:
            posv = np.array([drawing.x(v), drawing.y(v)])
            posu = np.array([drawing.x(u), drawing.y(u)])
            dist = max(0.01, np.linalg.norm(posu - posv))
            if dist < gap:
                unit = (posu - posv) / dist
                r = (dist - gap) / 2 * unit
                posv += r
                posu -= r
                drawing.set_x(v, posv[0])
                drawing.set_y(v, posv[1])
                drawing.set_x(u, posu[0])
                drawing.set_y(u, posu[1])


def project_distance_constraints_hyperbolic(
    drawing, constraints, indices, iterations=5
):
    """
    双曲空間（ポアンカレ円板）上で距離制約を適用します。

    この関数は、指定されたノードペア間の双曲距離が、
    目標のギャップ(`gap`)より小さい場合に、それらのノードを反発させます。
    移動はユークリッド空間での近似的な勾配降下法によって行い、
    円板の縁に近い点ほど動きにくくなるようにスケーリングします。

    Args:
        drawing: グラフの描画情報を持つオブジェクト。
                 `x(node)`, `y(node)`, `set_x(node, val)`, `set_y(node, val)`
                 メソッドを持つことを想定。
        constraints: (v, u, gap) のタプルのリスト。
                     v, u: ノードID
                     gap: 目標とする最小双曲距離
        indices: (未使用の引数、互換性のために維持)
        learning_rate: 移動量を調整する学習率。
        iterations: 制約を適用する反復回数。
    """
    for _ in range(iterations):
        for v, u, gap in constraints:
            posv = np.array([drawing.x(v), drawing.y(v)])
            posu = np.array([drawing.x(u), drawing.y(u)])

            # 2点間の双曲距離を計算
            dist_h = hyperbolic_distance(posv, posu)

            # 距離が目標より小さい場合のみ処理
            if dist_h < gap:
                # ユークリッド空間での差分ベクトルと距離
                diff_e = posu - posv
                dist_e = np.linalg.norm(diff_e)
                if dist_e < 1e-9:
                    # 点が重なっている場合はランダムに少し動かす
                    diff_e = np.random.rand(2) * 1e-6
                    dist_e = np.linalg.norm(diff_e)

                unit_vec = diff_e / dist_e

                # 移動量の計算：双曲距離の差に比例
                move_dist = (gap - dist_h) / 2.0

                # 移動ベクトルを計算
                # 円板の縁に近いほど動きにくくするスケーリングを適用
                # (1 - |pos|^2) は縁で0になるため、移動量が0になる
                r_v = move_dist * unit_vec * (1 - np.sum(posv**2))
                r_u = move_dist * unit_vec * (1 - np.sum(posu**2))

                # 新しい座標を計算
                new_posv = posv - r_v
                new_posu = posu + r_u

                # 新しい座標が円板からはみ出さないようにクリッピング
                # ノルムが1以上になった場合、ノルムを1未満に補正
                norm_v = np.linalg.norm(new_posv)
                if norm_v >= 1.0:
                    new_posv /= norm_v + 1e-6

                norm_u = np.linalg.norm(new_posu)
                if norm_u >= 1.0:
                    new_posu /= norm_u + 1e-6

                # 座標を更新
                drawing.set_x(v, new_posv[0])
                drawing.set_y(v, new_posv[1])
                drawing.set_x(u, new_posu[0])
                drawing.set_y(u, new_posu[1])


def place_node_below_in_hyperbolic(drawing, constraints):
    """
    指定されたノードvに対し、ユークリッド空間でy軸の負の方向に
    gap分離れた点にノードuを配置し、その結果を双曲空間に反映します。

    この関数は、元の project_distance_constraints_hyperbolic を置き換えるものです。

    Args:
        drawing: グラフの描画情報を持つオブジェクト。
                 x(node), y(node), set_x(node, val), set_y(node, val)
                 メソッドを持つことを想定。
        constraints: (v, u, gap) のタプルのリスト。
                     v: 基準となるノードID
                     u: 配置するノードID
                     gap: ユークリッド空間でのy軸方向の目標距離
    """
    for _ in range(5):
        for v, u, gap in constraints:
            # 1. 基準ノードvの現在の双曲座標を取得
            pos_v_h = np.array([drawing.x(v), drawing.y(v)])
            pos_u_h = np.array([drawing.x(u), drawing.y(u)])

            # 2. ノードvの双曲座標をユークリッド座標に変換
            #    入力は (N, 2) の形式を要求するため、reshape と flatten を使用
            pos_v_e = hyperbolic_to_euclidean(pos_v_h.reshape(1, 2)).flatten()
            pos_u_e = hyperbolic_to_euclidean(pos_u_h.reshape(1, 2)).flatten()

            # 3. ユークリッド空間で、vの真下(y軸負方向)にgapだけ離れたuの目標座標を計算
            dist = max(0.01, np.linalg.norm(pos_u_e - pos_v_e))
            if dist < gap:
                unit = (pos_u_e - pos_v_e) / dist
                r = (dist - gap) * unit
                pos_u_e -= r

            # 4. uの目標ユークリッド座標を双曲座標に変換
            pos_u_h_target = euclidean_to_hyperbolic(pos_u_e.reshape(1, 2)).flatten()

            # 5. ノードuの座標を更新
            drawing.set_x(u, pos_u_h_target[0])
            drawing.set_y(u, pos_u_h_target[1])
