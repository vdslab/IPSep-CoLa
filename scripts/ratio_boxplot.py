import argparse
import csv
import itertools

import matplotlib
import matplotlib.pyplot as plt

from boxplot_2item import boxplot_2item_plot_only, boxplot_seaborn

matplotlib.use("agg")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("out")
    parser.add_argument("--title", default="")
    parser.add_argument("--xlabel", default="")
    args = parser.parse_args()

    data = [row for row in csv.DictReader(open(args.csv_file))]
    data.sort(key=lambda row: (int(row["graph_size_n"])))
    labels = sorted({int(row["graph_size_n"]) for row in data})

    rates = []
    amounts = []
    finals = []
    baselines = []

    for _, rows_iter in itertools.groupby(data, lambda row: int(row["graph_size_n"])):
        rows_list = list(rows_iter)

        # 1. 必要な生の値を抽出
        # baseline_stress と proposed_stress がCSVにあるので直接取得
        b_raw = [float(row["baseline_stress"]) for row in rows_list]
        p_raw = [float(row["proposed_stress"]) for row in rows_list]
        r_raw = [float(row["reduction_rate"]) for row in rows_list]

        # 診断用Baselineリストに追加
        baselines.append(b_raw)

        # 2. Reduction Rate (CSVの値をそのまま使用)
        rates.append(r_raw)

        # 3. Final Value (CSVの proposed_stress をそのまま使用)
        finals.append(p_raw)

        # 4. Reduction Amount (単純な差分: Baseline - Proposed)
        # 逆算 (Baseline * Rate) をやめ、実測値間の差を使うことで整合性を担保
        diffs = [b - p for b, p in zip(b_raw, p_raw)]
        amounts.append(diffs)

    import os

    def save_metric_plot(metric_name, metric_data, ylabel, filename_suffix):
        boxplot_seaborn(
            {metric_name: {"data": metric_data, "baseline": baselines}},
            labels,
            show_legend=False,
        )
        plt.xlabel(args.xlabel)
        plt.ylabel(ylabel)

        base_name, ext = os.path.splitext(os.path.basename(args.out))
        dir_name = os.path.dirname(args.out)
        save_path = os.path.join(
            dir_name, f"{base_name}_{filename_suffix}.{ext.lstrip('.')}"
        )
        plt.savefig(save_path, bbox_inches="tight", pad_inches=0.02)
        plt.close()

    save_metric_plot("Reduction Rate", rates, "Reduction Rate", "rate")
    save_metric_plot("Reduction Amount", amounts, "Reduction Amount (Absolute)", "abs")
    save_metric_plot("Final Value", finals, "Final Stress Value", "final")

    print(f"Saved 3 plots with prefix: {args.out}")


if __name__ == "__main__":
    main()
