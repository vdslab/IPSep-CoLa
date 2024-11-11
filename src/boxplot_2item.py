import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np


def boxplot_2item_plot_only(data1, data2, labels, legend=["Data1", "Data2"]):
    plt.figure(figsize=(8, 6))

    width = 0.6
    gap = 0.1
    positions1 = np.arange(1, len(data1) + 1) * 2.0 - width / 2 - gap
    positions2 = np.arange(1, len(data2) + 1) * 2.0 + width / 2 + gap

    plt.boxplot(
        data1,
        positions=positions1,
        widths=0.6,
        patch_artist=True,
        boxprops=dict(facecolor="lightblue"),
    )
    plt.boxplot(
        data2,
        positions=positions2,
        widths=0.6,
        patch_artist=True,
        boxprops=dict(facecolor="lightgreen"),
    )

    blue_patch = mpatches.Patch(color="lightblue", label=legend[0])
    green_patch = mpatches.Patch(color="lightgreen", label=legend[1])
    plt.legend(handles=[blue_patch, green_patch])
    plt.xticks(np.arange(1, len(data1) + 1) * 2.0, labels)
    plt.grid(True)


if __name__ == "__main__":
    np.random.seed(0)
    data1 = [np.random.normal(0, std, 100) for std in range(1, 3)]
    data2 = [np.random.normal(1, std, 100) for std in range(1, 3)]

    boxplot_2item_plot_only(data1, data2, ["Group 1", "Group 2"], list(range(1, 3)))
    plt.title("Boxplots for Two Sets of Data per Group")
    plt.savefig("boxplot_grouped.png")
