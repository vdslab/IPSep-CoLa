import argparse
import csv
import itertools

import matplotlib
import matplotlib.pyplot as plt

from boxplot_2item import boxplot_2item_plot_only


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("out")
    parser.add_argument("--methods", nargs=2, required=True)
    args = parser.parse_args()

    data = [row for row in csv.DictReader(open(args.csv_file))]
    print(data)
    data.sort(key=lambda row: (row["method"], int(row["n"])))
    labels = sorted({int(row["n"]) for row in data})
    values = {method: [] for method in args.methods}
    for method, method_rows in itertools.groupby(data, lambda row: row["method"]):
        if method not in args.methods:
            continue
        for _, rows in itertools.groupby(method_rows, lambda row: int(row["n"])):
            values[method].append([float(row["value"]) for row in list(rows)])
    # Compute stress ratios
    print(values)
    stress_ratios = []
    stress_diffs = []
    for i in range(len(labels)):
        method1_values = values[args.methods[0]][i]
        method2_values = values[args.methods[1]][i]
        ratios = []
        diffs = []
        for v1, v2 in zip(method1_values, method2_values):
            ratios.append(v1 / v2)
            diffs.append(v1 - v2)

        stress_ratios.append(ratios)
        stress_diffs.append(diffs)

    # write csv file with stress ratios
    import os

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "n",
                "stress_ratio_values_avg",
                f"{args.methods[0]}-{args.methods[1]}_stress_diff_avg",
            ]
        )
        for n, ratios in zip(labels, stress_ratios):
            stress_ratio_values_avg = sum(ratios) / len(ratios)
            stress_diff_values_avg = sum(stress_diffs[labels.index(n)]) / len(
                stress_diffs[labels.index(n)]
            )
            writer.writerow([n, stress_ratio_values_avg, stress_diff_values_avg])
    print(args.methods, labels, stress_ratios)


if __name__ == "__main__":
    main()
