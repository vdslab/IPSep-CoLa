import argparse
import glob
import json
import os

import matplotlib
import matplotlib.pyplot as plt

from boxplot_2item import boxplot_2item_plot_only


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", required=True)
    parser.add_argument("--data_directories", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--iterations", type=int, default=30)
    args = parser.parse_args()

    categories = []
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    stresses: dict[dict[str, list]] = dict()
    violations = dict()
    for data_directory in args.data_directories:
        dirname = os.path.dirname(data_directory).split("/")[-1]
        categories.append(dirname)
        stresses.setdefault(dirname, dict())
        violations.setdefault(dirname, dict())
        print(data_directory, dirname)
        for data_path in glob.glob(os.path.join(data_directory, "*.json")):
            data = json.load(open(data_path))
            for method in ["unicon", "constrained_sgd"]:
                stresses[dirname].setdefault(method, []).append(data[method]["stress"])
                violations[dirname].setdefault(method, []).append(
                    data[method]["violation"]
                )

    # print(stresses)
    # print(violations)
    matplotlib.use("agg")
    boxplot_2item_plot_only(
        [stresses[category]["constrained_sgd"] for category in categories],
        [stresses[category]["unicon"] for category in categories],
        categories,
        ["Constrained SGD", "UNICON"],
    )
    plt.savefig(
        os.path.join(
            os.path.dirname(args.out), f"compare-stress-{os.path.basename(args.out)}."
        )
    )
    boxplot_2item_plot_only(
        [violations[category]["constrained_sgd"] for category in categories],
        [violations[category]["unicon"] for category in categories],
        categories,
        ["Constrained SGD", "UNICON"],
    )
    plt.savefig(
        os.path.join(
            os.path.dirname(args.out),
            f"compare-violation-{os.path.basename(args.out)}.png",
        ),
    )


if __name__ == "__main__":
    main()
