import numpy as np


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
