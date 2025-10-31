import networkx as nx
import numpy as np
from networkx.readwrite import json_graph


def _pairwise_euclidean(X: np.ndarray) -> np.ndarray:
    """行列 X (N×d) からユークリッド距離行列 (N×N) を返す。"""
    X = np.asarray(X, dtype=np.float64)
    G = X @ X.T
    sq = np.clip(np.diag(G)[:, None] + np.diag(G)[None, :] - 2 * G, 0.0, None)
    return np.sqrt(sq, dtype=np.float64)


def _upper_triangle_vector(D: np.ndarray) -> np.ndarray:
    """距離行列 D の上三角 (i<j) をベクトル化。NaN/inf は自動で弾く。"""
    D = np.asarray(D, dtype=np.float64)
    i, j = np.triu_indices_from(D, k=1)
    v = D[i, j]
    # 有効値のみ
    m = np.isfinite(v)
    return v[m]


def normalized_stress(
    D_high: np.ndarray, D_low: np.ndarray, alpha: float = 1.0
) -> float:
    """
    NS(D_high, alpha * D_low) = sqrt( sum_{i<j} (Δ_ij - alpha*δ_ij)^2 / sum_{i<j} Δ_ij^2 )
    """
    a = _upper_triangle_vector(D_high)
    b = _upper_triangle_vector(D_low)
    # 長さ揃え（念のため）
    n = min(a.size, b.size)
    a, b = a[:n], b[:n]

    denom = np.dot(a, a)
    if denom == 0.0:
        return 0.0  # 全ての高次元距離が0なら誤差は0とする

    resid_sq = np.sum((a - alpha * b) ** 2, dtype=np.float64)
    return np.sqrt(resid_sq / denom, dtype=np.float64)


def scale_normalized_stress(D_high: np.ndarray, D_low: np.ndarray):
    """
    SNS = min_{alpha>0} NS(D_high, alpha * D_low)
    解析解: alpha* = (a·b) / (b·b)  （a=高次元距離ベクトル, b=低次元距離ベクトル）
    返り値: (sns, alpha_star)
    """
    a = _upper_triangle_vector(D_high)
    b = _upper_triangle_vector(D_low)
    n = min(a.size, b.size)
    a, b = a[:n], b[:n]

    aa = np.dot(a, a)  # ||a||^2
    bb = np.dot(b, b)  # ||b||^2
    ab = np.dot(a, b)  # a·b

    if aa == 0.0:
        return 0.0, 0.0  # 退化ケース: 高次元距離が全0
    if bb == 0.0:
        # 低次元距離が全0なら NS(α=0)=1、NSはαで単調増 → 最小はα*=0, SNS=1
        return 1.0, 0.0

    alpha_star = max(ab / bb, 0.0)  # α>0 制約（必要なら max を外す）
    # 最小残差 ||a - α*b||^2 = ||a||^2 - (a·b)^2 / ||b||^2
    min_resid_sq = aa - (ab * ab) / bb
    min_resid_sq = max(min_resid_sq, 0.0)  # 数値誤差で負になるのを防止

    sns = np.sqrt(min_resid_sq / aa, dtype=np.float64)
    return sns, alpha_star


def sns_from_embeddings(X_high: np.ndarray, P_low: np.ndarray):
    """
    高次元点列 X_high (N×n) と 低次元埋め込み P_low (N×d) から SNS を計算。
    """
    D_high = _pairwise_euclidean(X_high)
    D_low = _pairwise_euclidean(P_low)
    return scale_normalized_stress(D_high, D_low)


# ---------- node_link_data の例（JSON相当の辞書） ----------
# 5ノードのサイクル。各ノードに2次元座標を持たせています（pos: [x, y]）
node_link = {
    "directed": False,
    "multigraph": False,
    "graph": {},
    "nodes": [
        {"id": 0, "pos": [0.0, 0.0]},
        {"id": 1, "pos": [1.0, 0.0]},
        {"id": 2, "pos": [1.5, 0.866]},  # 60度回転っぽい位置
        {"id": 3, "pos": [0.5, 1.366]},
        {"id": 4, "pos": [-0.5, 0.866]},
    ],
    "links": [
        {"source": 0, "target": 1, "weight": 1.0},
        {"source": 1, "target": 2, "weight": 1.0},
        {"source": 2, "target": 3, "weight": 1.0},
        {"source": 3, "target": 4, "weight": 1.0},
        {"source": 4, "target": 0, "weight": 1.0},
    ],
}


def main():
    # 1) JSON -> Graph 復元
    G = json_graph.node_link_graph(node_link, directed=node_link.get("directed", False))
    # node_link_data のノード順（安定な順序）を確保
    nodelist = [n["id"] for n in node_link["nodes"]]

    # 2) 高次元距離（ここでは「グラフ最短路距離」）を行列化
    #    無向グラフ＋weight 属性があれば重み付き最短路
    D_high = nx.floyd_warshall_numpy(G, nodelist=nodelist, weight="weight").astype(
        np.float64
    )

    # 3) 低次元埋め込み（pos 属性）からユークリッド距離行列
    #    pos が無い場合は spring_layout などで生成する
    if all("pos" in G.nodes[n] for n in nodelist):
        P_low = np.array([G.nodes[n]["pos"] for n in nodelist], dtype=np.float64)
    else:
        pos = nx.spring_layout(G, seed=0, weight="weight", dim=2)
        P_low = np.array([pos[n] for n in nodelist], dtype=np.float64)

    D_low = _pairwise_euclidean(P_low)

    # 4) SNS と α* を計算
    sns, alpha_star = scale_normalized_stress(D_high, D_low)

    # 5) ちょいテスト
    assert 0.0 <= sns <= 1.0 + 1e-12
    ns_at_alpha_star = normalized_stress(D_high, D_low, alpha_star)
    # 数値誤差の範囲で一致
    assert abs(ns_at_alpha_star - sns) < 1e-9

    print(f"SNS = {sns:.6f}")
    print(f"alpha* = {alpha_star:.6f}")
    print(f"NS(alpha*) = {ns_at_alpha_star:.6f}")


if __name__ == "__main__":
    main()
