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
    # today = datetime.date.today()
    # now = datetime.datetime.now().time()
    save_dir = "src/data/align/violation"
    os.makedirs(save_dir, exist_ok=True)

    dir = "src/data/json/violation/2024-10-21/07:15:58.244138"
    files = list(
        filter(
            lambda x: os.path.basename(x).split(".")[0] != "stress",
            glob.glob(f"{dir}/*.json"),
        )
    )
    files.sort(key=lambda x: int(os.path.basename(x).split("_")[1].split(".")[0]))
    # pprint(files)
    # # base_names = ["no_cycle_tree.json", "qh882.json"]

    webcola_violation = []
    fullSGD_violation = []
    labels = []
    for node_n in range(100, 101, 100):
        webcola_violation = get_data(f"src/data/align/violation/webcola_{node_n}.json")
        wvs = [max([v for v in wv if v > 0]) for wv in webcola_violation]

        # fullSGD_violation = get_data(f"src/data/align/violation/fullsgd_{node_n}.json")
        # fsvs = [max([v for v in fsv if v > 0]) for fsv in fullSGD_violation]
        fsvs = [sum(fsv) / len(fsv) if len(fsv) > 0 else 0 for fsv in fullSGD_violation]

        # wv_mean = max(wvs)
        # fsv_mean = max(fsvs)
        webcola_violation.append(wvs)
        # fullSGD_violation.append(fsvs)
        labels.append(node_n)
        #     base_file = os.path.basename(file)
        #     base_name = os.path.splitext(base_file)[0]
        #     node_n = int(base_name.split("_")[1])
        #     print(base_name, node_n)
        #     webcola_violation =
        #     fullSGD_violation =
        #     webcolas.append(webcola_violation)
        #     fullSGDs.append(fullSGD_violation)
        #     labels.append(node_n)
    plt.boxplot(
        webcola_violation[0],
        widths=0.6,
        patch_artist=True,
        boxprops=dict(facecolor="lightblue"),
    )
    # for i in range(0, len(webcola_violation), 5):
    #     print(i, i + 5)
    #     boxplot_2item_plot_only(
    #         webcola_violation[i : i + 1],
    #         fullSGD_violation[i : i + 1],
    #         labels[i : i + 5],
    #         ["webcola", "FullSGD"],
    #     )
    #     plt.title("Webcola min violation mean vs FullSGD min violation mean")
    plt.savefig(f"{save_dir}/violation_t.png")


if __name__ == "__main__":
    main()
