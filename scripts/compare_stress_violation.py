import argparse
import glob
import json
import os

import matplotlib
import matplotlib.pyplot as plt

from boxplot_2item import boxplot_2item_plot_only


def plot_comparison(results_dir, output_file="comparison_boxplot.png"):
    """
    実験結果のJSONファイルを読み込み、stressとviolationの比較を箱ひげ図でプロットします。

    Args:
        results_dir (str): 'compare_seed*.json'ファイルが含まれるディレクトリのパス。
        output_file (str): 出力する画像ファイル名。
    """
    json_files = glob.glob(os.path.join(results_dir, "compare_seed*.json"))

    if not json_files:
        print(
            f"エラー: ディレクトリ '{results_dir}' に 'compare_seed*.json' ファイルが見つかりません。"
        )
        return

    # データを格納するためのリストを初期化
    constrained_sgd_stresses = []
    constrained_sgd_violations = []
    uniocon_sgd_stresses = []
    uniocon_sgd_violations = []

    # 各JSONファイルからデータを読み込む
    for file_path in json_files:
        with open(file_path, "r") as f:
            data = json.load(f)
            # Constrained SGDのデータを追加
            constrained_sgd_stresses.append(data["constrained_sgd"]["stress"])
            constrained_sgd_violations.append(data["constrained_sgd"]["violation"])
            # UniConのデータを追加
            uniocon_sgd_stresses.append(data["unicon"]["stress"])
            uniocon_sgd_violations.append(data["unicon"]["violation"])
    matplotlib.use("agg")
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 6))
    labels = ["UNICON", "FullSGD"]
    colors = ["lime", "lightblue"]  # 🎨 色のリストを定義

    # 1. Stressの箱ひげ図を描画
    bplot1 = ax1.boxplot(
        [uniocon_sgd_stresses, constrained_sgd_stresses],
        labels=labels,
        patch_artist=True,  # 色付けのためにTrue
        medianprops={"color": "black"},
    )
    ax1.set_title("Stress Comparison", fontsize=14)
    ax1.set_ylabel("Stress")
    ax1.grid(True, linestyle="--", alpha=0.6)

    # 2. Violationの箱ひげ図を描画
    bplot2 = ax2.boxplot(
        [uniocon_sgd_violations, constrained_sgd_violations],
        labels=labels,
        patch_artist=True,
        medianprops={"color": "black"},
    )
    ax2.set_title("Violation Comparison", fontsize=14)
    ax2.set_ylabel("Violation")
    ax2.grid(True, linestyle="--", alpha=0.6)

    # --- ここからが色付けの追記部分です ---
    # Stressプロットの色を設定
    for patch, color in zip(bplot1["boxes"], colors):
        patch.set_facecolor(color)

    # Violationプロットの色を設定
    for patch, color in zip(bplot2["boxes"], colors):
        patch.set_facecolor(color)

    # 画像の保存
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()

    print(f"比較グラフを '{output_file}' として保存しました。")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir")
    parser.add_argument(
        "-o",
        "--output",
        default="comparison_boxplot.png",
    )
    args = parser.parse_args()

    plot_comparison(args.results_dir, args.output)


if __name__ == "__main__":
    main()
