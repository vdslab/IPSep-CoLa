import argparse
import json
import os
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def main():
    parser = argparse.ArgumentParser(
        description="Plot degree distribution of a graph to check scale-free property"
    )
    parser.add_argument("graph_file", help="Path to the graph JSON file")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: <graph_file>_degree_distribution.png)",
    )
    args = parser.parse_args()

    # グラフの読み込み
    graph: nx.Graph = nx.node_link_graph(json.load(open(args.graph_file)))

    # 次数の計算
    degrees = [degree for node, degree in graph.degree()]

    # 統計情報の表示
    print(f"グラフ統計情報:")
    print(f"  ノード数: {graph.number_of_nodes()}")
    print(f"  エッジ数: {graph.number_of_edges()}")
    print(f"  平均次数: {np.mean(degrees):.2f}")
    print(f"  次数の最小値: {np.min(degrees)}")
    print(f"  次数の最大値: {np.max(degrees)}")
    print(f"  次数の中央値: {np.median(degrees):.2f}")
    print(f"  次数の標準偏差: {np.std(degrees):.2f}")

    # 次数分布の計算
    degree_count = Counter(degrees)
    degrees_unique = sorted(degree_count.keys())
    counts = [degree_count[d] for d in degrees_unique]

    # 出力ファイル名の決定
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(args.graph_file)[0]
        output_file = f"{base_name}_degree_distribution.png"

    # プロットの作成
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # 1. 線形スケールのヒストグラム
    ax1.hist(degrees, bins=30, edgecolor="black", alpha=0.7)
    ax1.set_xlabel("Degree", fontsize=12)
    ax1.set_ylabel("Frequency", fontsize=12)
    ax1.set_title("Degree Distribution (Linear Scale)", fontsize=14)
    ax1.grid(True, alpha=0.3)

    # 2. 両対数プロット
    # ゼロを除外してプロット
    degrees_nonzero = [d for d in degrees_unique if d > 0]
    counts_nonzero = [degree_count[d] for d in degrees_nonzero]

    ax2.scatter(degrees_nonzero, counts_nonzero, alpha=0.6, s=50)
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("Degree [log]", fontsize=12)
    ax2.set_ylabel("Frequency [log]", fontsize=12)
    ax2.set_title("Degree Distribution (Log-Log Scale)", fontsize=14)
    ax2.grid(True, alpha=0.3, which="both")

    # べき乗則の参考線を追加(オプション)
    if len(degrees_nonzero) > 1:
        # 簡易的なべき乗則のフィッティング
        log_degrees = np.log10(degrees_nonzero)
        log_counts = np.log10(counts_nonzero)
        coeffs = np.polyfit(log_degrees, log_counts, 1)
        gamma = -coeffs[0]  # べき指数

        # フィット線の描画
        fit_line = 10 ** (coeffs[0] * log_degrees + coeffs[1])
        ax2.plot(
            degrees_nonzero,
            fit_line,
            "r--",
            alpha=0.7,
            label=f"power law fitting (γ ≈ {gamma:.2f})",
        )
        ax2.legend()

        print(f"\nべき乗則フィッティング:")
        print(f"  推定されたべき指数 γ: {gamma:.2f}")
        print(
            f"  (Scale-freeネットワークでは通常 2 < γ < 3 の範囲になります)"
        )

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"\n次数分布のプロットを保存しました: {output_file}")

    # Scale-free性質の判定
    print("\nScale-free性質の評価:")
    if len(degrees_nonzero) > 1:
        # 両対数プロットでの線形性を簡易的に評価
        correlation = np.corrcoef(log_degrees, log_counts)[0, 1]
        print(f"  両対数プロットの相関係数: {correlation:.3f}")
        if abs(correlation) > 0.8:
            print("  → 両対数プロットで強い線形関係が見られます")
            print("  → Scale-free性質を持つ可能性が高いです")
        elif abs(correlation) > 0.6:
            print("  → 両対数プロットで中程度の線形関係が見られます")
            print("  → Scale-free性質を部分的に持つ可能性があります")
        else:
            print("  → 両対数プロットで線形関係が弱いです")
            print("  → Scale-free性質を持たない可能性が高いです")


if __name__ == "__main__":
    main()
