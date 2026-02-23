import matplotlib as mpl

mpl.use("Agg")

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib_fontja
import pandas as pd
import seaborn as sns


def set_paper_style(font_scale=1.5, save_dpi=300):
    sns.set_theme(style="whitegrid", context="paper", font_scale=font_scale)
    matplotlib_fontja.japanize()
    mpl.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": save_dpi,
            "font.size": 27,
            "axes.titlesize": 27,
            "axes.labelsize": 27,
            "xtick.labelsize": 27,
            "ytick.labelsize": 27,
            "legend.fontsize": 24,
            "legend.title_fontsize": 24,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def load_csv_files(runtime_dir, suffix):
    """指定されたsuffixのCSVファイルを全て読み込む"""
    methods = ["fullsgd", "inline", "post", "unicon", "webcola"]
    data_dict = {}

    for method in methods:
        filepath = runtime_dir / f"{method}_{suffix}.csv"
        if filepath.exists():
            df = pd.read_csv(filepath)
            data_dict[method] = df

    return data_dict


def plot_stacked_area(data_dict, suffix, output_path):
    """積み上げ面グラフを作成"""
    set_paper_style()

    n_methods = len(data_dict)
    fig, axes = plt.subplots(
        n_methods, 1, figsize=(14, 4 * n_methods), layout="constrained"
    )

    if n_methods == 1:
        axes = [axes]

    method_names = {
        "fullsgd": "Full SGD",
        "inline": "Inline",
        "post": "Post",
        "unicon": "Unicon",
        "webcola": "WebCoLa",
    }

    for idx, (method, df) in enumerate(data_dict.items()):
        ax = axes[idx]

        # データの準備
        x = df["NodeSize"]

        # webcolaの場合はカラム名が異なる
        if method == "webcola" and "initialLayout_total_median" in df.columns:
            # webcolaの特殊なカラム名に対応
            sgd = df["initialLayout_total_median"]
            x_median = df["initialUserConstraint_total_median"]
            y_median = (
                df["initialAllConstraints_total_median"]
                + df["updateNodePositions_total_median"]
            )
            labels = ["InitLayout", "UserConstraint", "AllConstraints+Update"]
        else:
            sgd = df["SGD_total_median"]
            x_median = df["X_total_median"]
            y_median = df["Y_total_median"]
            labels = ["SGD", "X", "Y"]

        # 積み上げ面グラフ
        ax.fill_between(x, 0, sgd, alpha=0.7, label=labels[0], color="#8dd3c7")
        ax.fill_between(
            x, sgd, sgd + x_median, alpha=0.7, label=labels[1], color="#ffffb3"
        )
        ax.fill_between(
            x,
            sgd + x_median,
            sgd + x_median + y_median,
            alpha=0.7,
            label=labels[2],
            color="#bebada",
        )

        # Iter_total_medianの折れ線
        ax.plot(x, df["Iter_total_median"], "k-", linewidth=2, label="Iter合計")

        ax.set_xlabel("ノードサイズ")
        ax.set_ylabel("実行時間（秒）")
        ax.set_title(f"{method_names.get(method, method)} - {suffix}")
        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"✓ 積み上げ面グラフを保存: {output_path}")


def plot_subplot_with_ratio(df, method, suffix, output_path):
    """サブプロット形式（上段: 折れ線、下段: 割合）"""
    set_paper_style(font_scale=1.3)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), layout="constrained")

    method_names = {
        "fullsgd": "Full SGD",
        "inline": "Inline",
        "post": "Post",
        "unicon": "Unicon",
        "webcola": "WebCoLa",
    }

    x = df["NodeSize"]

    # webcolaの場合はカラム名が異なる
    if method == "webcola" and "initialLayout_total_median" in df.columns:
        comp1 = df["initialLayout_total_median"]
        comp2 = df["initialUserConstraint_total_median"]
        comp3 = (
            df["initialAllConstraints_total_median"]
            + df["updateNodePositions_total_median"]
        )
        labels = ["InitLayout", "UserConstraint", "AllConstraints+Update"]
    else:
        comp1 = df["SGD_total_median"]
        comp2 = df["X_total_median"]
        comp3 = df["Y_total_median"]
        labels = ["SGD", "X", "Y"]

    # 上段: 各成分の折れ線グラフ
    ax1.plot(
        x,
        df["Iter_total_median"],
        "o-",
        linewidth=2,
        markersize=6,
        label="Iter合計",
        color="#1f77b4",
    )
    ax1.plot(
        x, comp1, "s-", linewidth=2, markersize=6, label=labels[0], color="#ff7f0e"
    )
    ax1.plot(
        x, comp3, "^-", linewidth=2, markersize=6, label=labels[2], color="#2ca02c"
    )
    ax1.plot(
        x, comp2, "d-", linewidth=2, markersize=6, label=labels[1], color="#d62728"
    )

    ax1.set_xlabel("ノードサイズ")
    ax1.set_ylabel("実行時間（秒）")
    ax1.set_title(f"{method_names.get(method, method)} - {suffix} (実行時間)")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # 下段: 割合のグラフ
    comp1_ratio = (comp1 / df["Iter_total_median"]) * 100
    comp2_ratio = (comp2 / df["Iter_total_median"]) * 100
    comp3_ratio = (comp3 / df["Iter_total_median"]) * 100

    ax2.plot(
        x,
        comp1_ratio,
        "s-",
        linewidth=2,
        markersize=6,
        label=f"{labels[0]}割合",
        color="#ff7f0e",
    )
    ax2.plot(
        x,
        comp3_ratio,
        "^-",
        linewidth=2,
        markersize=6,
        label=f"{labels[2]}割合",
        color="#2ca02c",
    )
    ax2.plot(
        x,
        comp2_ratio,
        "d-",
        linewidth=2,
        markersize=6,
        label=f"{labels[1]}割合",
        color="#d62728",
    )

    ax2.set_xlabel("ノードサイズ")
    ax2.set_ylabel("割合（%）")
    ax2.set_title(f"{method_names.get(method, method)} - {suffix} (成分割合)")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 105)

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"✓ サブプロットを保存: {output_path}")


def plot_method_comparison(data_dict, suffix, output_path):
    """手法間でIter_total_medianを比較"""
    set_paper_style(font_scale=1.3)

    fig, ax = plt.subplots(1, 1, figsize=(14, 10), layout="constrained")

    method_names = {
        "fullsgd": "SGD",
        "inline": "反復内",
        "post": "後処理",
        "unicon": "UNICON",
        "webcola": "WebCoLa",
    }

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    markers = ["o", "s", "^", "d", "v"]

    for idx, (method, df) in enumerate(data_dict.items()):
        x = df["NodeSize"]
        y = df["Iter_total_median"]
        ax.plot(
            x,
            y,
            marker=markers[idx],
            linewidth=2,
            markersize=8,
            label=method_names.get(method, method),
            color=colors[idx],
        )

    # ax.set_xscale("log")
    # ax.set_yscale("log")
    ax.set_xlabel("ノードサイズ")
    ax.set_ylabel("実行時間（秒）")
    ax.set_title(f"手法間比較: Iter_total_median ({suffix})")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"✓ 手法間比較グラフを保存: {output_path}")


def plot_ratio_comparison(data_dict, suffix, output_path):
    """手法間でSGD割合とY割合を比較"""
    set_paper_style(font_scale=1.3)

    fig, (ax, ax1) = plt.subplots(
        2, 1, figsize=(14, 12), layout="constrained", gridspec_kw={"hspace": 0.1}
    )

    method_names = {
        "fullsgd": "同時射影",
        "inline": "反復内",
        "post": "後処理",
        "unicon": "UNICON",
        "webcola": "WebCoLa",
    }

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    markers = ["o", "s", "^", "d", "v"]

    for idx, (method, df) in enumerate(data_dict.items()):
        x = df["NodeSize"]
        y = df["Iter_total_median"]
        ax.plot(
            x,
            y,
            marker=markers[idx],
            linewidth=2,
            markersize=8,
            label=method_names.get(method, method),
            color=colors[idx],
        )

    # ax.set_xscale("log")
    # ax.set_yscale("log")
    ax.set_xlabel("ノードサイズ")
    ax.set_ylabel("合計実行時間（秒）")
    ax.set_title("合計実行時間の比較")
    ax.grid(True, alpha=0.3)

    # 上段: SGD割合の比較
    for idx, (method, df) in enumerate(data_dict.items()):
        x = df["NodeSize"]

        # webcolaの場合はカラム名が異なる
        if method == "webcola" and "initialLayout_total_median" in df.columns:
            sgd = df["initialLayout_total_median"]
        else:
            sgd = df["SGD_total_median"]

        sgd_ratio = (sgd / df["Iter_total_median"]) * 100
        ax1.plot(
            x,
            sgd_ratio,
            marker=markers[idx],
            linewidth=2,
            markersize=8,
            # label=method_names.get(method, method),
            color=colors[idx],
        )

    ax1.set_xlabel("ノードサイズ")
    ax1.set_ylabel("割合（%）")
    ax1.set_title("合計実行時間の内SGDが占める割合")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 105)

    # 図全体の上部に共有凡例を配置
    fig.legend(bbox_to_anchor=(0.5, 1.02), loc="lower center", ncol=5)

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"✓ 割合比較グラフを保存: {output_path}")


def main():
    # ディレクトリ設定
    runtime_dir = Path("result/runtime")

    # 各suffix（y_gap, y_fix）について処理
    for suffix in ["y_gap", "y_fix"]:
        print(f"\n{'=' * 60}")
        print(f"処理中: {suffix}")
        print("=" * 60)

        # CSVファイル読み込み
        data_dict = load_csv_files(runtime_dir, suffix)
        print(f"読み込んだファイル: {list(data_dict.keys())}")

        # # 1. 積み上げ面グラフ
        # stacked_output = runtime_dir / f"stacked_area_{suffix}.png"
        # plot_stacked_area(data_dict, suffix, stacked_output)

        # # 2. 各手法ごとのサブプロット
        # for method, df in data_dict.items():
        #     subplot_output = runtime_dir / f"subplot_{method}_{suffix}.png"
        #     plot_subplot_with_ratio(df, method, suffix, subplot_output)

        # 3. 手法間比較グラフ（Iter_total_median）
        comparison_output = runtime_dir / f"method_comparison_{suffix}.pdf"
        plot_method_comparison(data_dict, suffix, comparison_output)

        # 4. 手法間比較グラフ（SGD割合とY割合）
        ratio_comparison_output = runtime_dir / f"ratio_comparison_{suffix}.pdf"
        plot_ratio_comparison(data_dict, suffix, ratio_comparison_output)

    print(f"\n{'=' * 60}")
    print("✓ 全てのグラフ作成が完了しました！")
    print("=" * 60)


if __name__ == "__main__":
    main()
