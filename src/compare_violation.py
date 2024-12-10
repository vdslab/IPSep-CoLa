import datetime
import glob
import json
import os
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np

from boxplot_2item import boxplot_2item_plot_only


def get_data(file):
    with open(file) as f:
        data = json.load(f)
    # print(data)
    data = [[float(d) for d in dd] for dd in data]
    return data


def main():
    save_dir = "src/data/square/violation"
    os.makedirs(save_dir, exist_ok=True)
    webcola_violations = []
    fullSGD_violations = []
    labels = []
    for node_n in range(100, 501, 100):
        webcola_violation = get_data(f"src/data/square/violation/webcola_{node_n}.json")
        wvs = [sum([v if v > 0 else 0 for v in wv]) for wv in webcola_violation]

        fullSGD_violation = get_data(f"src/data/square/violation/fullsgd_{node_n}.json")
        fsvs = [sum([v if v > 0 else 0 for v in fsv]) for fsv in fullSGD_violation]
        webcola_violations.append(wvs)
        fullSGD_violations.append(fsvs)
        labels.append(node_n)

    for i in range(0, len(fullSGD_violation), 5):
        print(i, i + 5)
        boxplot_2item_plot_only(
            webcola_violations[i : i + 5],
            fullSGD_violations[i : i + 5],
            labels[i : i + 5],
            ["webcola", "FullSGD"],
        )
        plt.title("Webcola violation vs FullSGD violation ")
        plt.savefig(f"{save_dir}/violation_sum_full_webcola_{i}-{i+5}.png")
        plt.close()


if __name__ == "__main__":
    main()
