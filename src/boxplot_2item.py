import matplotlib as mpl

mpl.use("Agg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib_fontja
import numpy as np
import pandas as pd
import seaborn as sns


def set_paper_style(font_scale=1.5, save_dpi=300):
    sns.set_theme(style="whitegrid", context="paper", font_scale=font_scale)
    matplotlib_fontja.japanize()
    mpl.rcParams.update(
        {
            # 画面表示用dpi（重要度低い）
            "figure.dpi": 150,
            # 保存dpi（これが本命）
            "savefig.dpi": save_dpi,
            # 文字サイズ（デフォルトだと小さすぎる）
            "font.size": 27,
            "axes.titlesize": 27,
            "axes.labelsize": 27,
            "xtick.labelsize": 27,
            "ytick.labelsize": 27,
            "legend.fontsize": 27,
            "legend.title_fontsize": 27,
            # PDF埋め込み文字の互換性（投稿で詰まりがち）
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def boxplot_seaborn(data_dict, x_labels, show_legend=True, l="v"):
    """
    data_dict: { "凡例名1": {data: [[...], [...]], baaseline: []}, "凡例名2": [[...], [...]], ... }
    という形式の辞書を受け取ることで、いくつでも比較可能にする。
    """
    # 1. データ整形（辞書 -> DataFrame）
    records = []
    labels = set()
    for hue_label, data in data_dict.items():
        data_list = data["data"]
        baseline = data.get("baseline", [])
        labels.add(hue_label)
        # データ長の整合性チェック（推奨）
        if len(data_list) != len(x_labels):
            print(f"Warning: {hue_label} のデータ数とラベル数が一致していません。")
            continue

        for i, group_label in enumerate(x_labels):
            group_data = data_list[i]
            baseline_data = baseline[i] if baseline else [None] * len(group_data)
            # データが空でないかチェック
            if len(group_data) > 0:
                for val, bval in zip(group_data, baseline_data):
                    records.append(
                        {
                            "Value": val,
                            "Group": group_label,
                            "Type": hue_label,
                            "Baseline": bval,
                        }
                    )

    df = pd.DataFrame(records)
    # 2. 描画
    plt.figure(figsize=(14, 10), layout="constrained")

    # データの種類数に応じてパレットを自動調整
    set_paper_style()
    sns.boxplot(
        x="Group",
        y="Value",
        hue="Type",
        data=df,
        width=0.6,  # 全体の幅
        palette="gist_ncar",  # 色の自動生成
        legend=show_legend,
    )
    ax = plt.gca()

    for i, lab in enumerate(ax.get_xticklabels()):
        if i in [0, 4, 9, 14, 19]:
            lab.set_visible(True)
        else:
            lab.set_visible(False)

    plt.grid(True, axis="y", linestyle="--", alpha=0.7)


def boxplot_2item_plot_only(data1, data2, labels, legend=["Data1", "Data2"]):
    plt.figure(figsize=(12, 6))

    width = 0.6
    gap = 0.1
    positions1 = np.arange(1, len(data1) + 1) * 2.0 - width / 2 - gap
    positions2 = np.arange(1, len(data2) + 1) * 2.0 + width / 2 + gap

    plt.boxplot(
        data1,
        positions=positions1,
        widths=0.6,
        patch_artist=True,
        boxprops=dict(facecolor="lightblue"),
    )
    plt.boxplot(
        data2,
        positions=positions2,
        widths=0.6,
        patch_artist=True,
        boxprops=dict(facecolor="lightgreen"),
    )

    blue_patch = mpatches.Patch(color="lightblue", label=legend[0])
    green_patch = mpatches.Patch(color="lightgreen", label=legend[1])
    plt.legend(handles=[blue_patch, green_patch])
    plt.xticks(np.arange(1, len(data1) + 1) * 2.0, labels)
    plt.grid(True)


if __name__ == "__main__":
    np.random.seed(0)
    data1 = [np.random.normal(0, std, 100) for std in range(1, 3)]
    data2 = [np.random.normal(1, std, 100) for std in range(1, 3)]

    boxplot_2item_plot_only(data1, data2, ["Group 1", "Group 2"], list(range(1, 3)))
    plt.title("Boxplots for Two Sets of Data per Group")
    plt.savefig("boxplot_grouped.png")
