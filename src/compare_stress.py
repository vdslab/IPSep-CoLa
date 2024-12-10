import datetime
import glob
import json
import os
from pprint import pprint

import matplotlib.pyplot as plt

from boxplot_2item import boxplot_2item_plot_only


def get_data(file):
    with open(file) as f:
        data = json.load(f)
    print(data)
    data = [float(d) for d in data]
    return data


def main():
    save_dir = "result"
    webcola_dir = "result"
    sgd_dir = "result"
    webcolas = []
    fullSGDs = []
    labels = []
    for node_n in range(100, 2001, 100):
        webcola_stress = get_data(f"{webcola_dir}/stress{node_n}.json")
        fullSGD_stress = []
        with open(f"{sgd_dir}/stress_potition_{node_n}.json") as f:
            data = json.load(f)["stresses"]
            data = [float(d) for d in data]
            fullSGD_stress = data
        webcolas.append(webcola_stress)
        fullSGDs.append(fullSGD_stress)
        labels.append(node_n)
    for i in range(0, len(webcolas), 5):
        print(i, i + 5)
        boxplot_2item_plot_only(
            webcolas[i : i + 5],
            fullSGDs[i : i + 5],
            labels[i : i + 5],
            ["Webcola", "FullSGD"],
        )
        plt.title("Webcola stress vs FullSGD stress")
        plt.savefig(f"{save_dir}/stress_{i}-{i+5}.png")


if __name__ == "__main__":
    main()
