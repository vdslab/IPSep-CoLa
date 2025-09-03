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
    args = parser.parse_args()

    data = [row for row in csv.DictReader(open(args.csv_file))]
    data.sort(key=lambda row: (row["method"], int(row["n"])))
    labels = sorted({int(row["n"]) for row in data})
    values = {
        method: [
            [float(row["value"]) for row in list(rows)]
            for _, rows in itertools.groupby(method_rows, lambda row: int(row["n"]))
        ]
        for method, method_rows in itertools.groupby(data, lambda row: row["method"])
    }

    matplotlib.use("agg")
    boxplot_2item_plot_only(
        values["webcola"],
        values["sgd"],
        labels,
        ["Webcola", "FullSGD"],
    )
    plt.title(args.title)
    plt.savefig(args.out)


if __name__ == "__main__":
    main()
