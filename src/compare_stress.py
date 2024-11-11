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
    # today = datetime.date.today()
    # now = datetime.datetime.now().time()
    save_dir = "src/data/align"
    # os.makedirs(save_dir, exist_ok=True)

    dir = "src/data/align/sgd"
    files = list(
        glob.glob(f"{dir}/stress_po*.json"),
    )
    files.sort(key=lambda x: int(os.path.basename(x).split(".")[0].split("_")[-1]))
    # pprint(files)
    # # base_names = ["no_cycle_tree.json", "qh882.json"]

    webcolas = []
    fullSGDs = []
    labels = []
    for file in files:
        base_file = os.path.basename(file)
        base_name = os.path.splitext(base_file)[0]
        node_n = int(base_name.split("_")[-1])
        print(base_name, node_n)
        webcola_stress = get_data(f"src/data/align/cola/stress{node_n}.json")
        fullSGD_stress = []
        with open(file) as f:
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
