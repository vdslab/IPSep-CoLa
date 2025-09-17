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
    parser.add_argument("--title", default="")
    parser.add_argument("--xlabel", default="")
    parser.add_argument("--ylabel", default="")
    parser.add_argument("--methods", nargs=2, required=True)
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
    print(args.methods, labels, values)
    matplotlib.use("agg")
    boxplot_2item_plot_only(
        values[args.methods[0]],
        values[args.methods[1]],
        labels,
        args.methods,
    )
    plt.xlabel(args.xlabel)
    plt.ylabel(args.ylabel)
    plt.title(args.title)
    plt.savefig(args.out)


if __name__ == "__main__":
    main()
