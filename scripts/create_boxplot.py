import argparse
import csv
import itertools

import matplotlib

matplotlib.use("agg")


import matplotlib.pyplot as plt

from boxplot_2item import boxplot_2item_plot_only, boxplot_seaborn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("out")
    parser.add_argument("--title", default="")
    parser.add_argument("--xlabel", default="")
    parser.add_argument("--ylabel", default="")
    parser.add_argument("--methods", nargs=2, required=True)
    parser.add_argument("--legend", nargs=2, required=True)
    args = parser.parse_args()

    data = [row for row in csv.DictReader(open(args.csv_file))]
    data.sort(key=lambda row: (row["method"], int(row["n"])))
    labels = sorted({int(row["n"]) for row in data})
    values = {method: [] for method in args.methods}
    for method, method_rows in itertools.groupby(data, lambda row: row["method"]):
        if method not in args.methods:
            continue
        for _, rows in itertools.groupby(method_rows, lambda row: int(row["n"])):
            values[method].append([float(row["value"]) for row in list(rows)])

    boxplot_seaborn(
        {
            args.legend[0]: {"data": values[args.methods[0]], "baseline": []},
            args.legend[1]: {"data": values[args.methods[1]], "baseline": []},
        },
        labels,
        show_legend=True,
    )
    
    plt.xlabel(args.xlabel)
    plt.ylabel(args.ylabel)
    plt.title(args.title)
    plt.savefig(args.out, bbox_inches="tight", pad_inches=0.02)


if __name__ == "__main__":
    main()
