import matplotlib as mpl

mpl.use("Agg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib_fontja
import numpy as np
import pandas as pd
import seaborn as sns


def set_paper_style(font_scale: float = 1.5, save_dpi: int = 300) -> None:
    sns.set_theme(style="whitegrid", context="paper", font_scale=font_scale)
    matplotlib_fontja.japanize()
    mpl.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": save_dpi,
            "font.size": 27,
            "axes.titlesize": 27,
            "axes.labelsize": 27,
            "xtick.labelsize": 27,
            "ytick.labelsize": 27,
            "legend.fontsize": 27,
            "legend.title_fontsize": 27,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def boxplot_seaborn(data_dict, x_labels, show_legend: bool = True) -> None:
    records = []
    for hue_label, data in data_dict.items():
        data_list = data["data"]
        baseline = data.get("baseline", [])

        if len(data_list) != len(x_labels):
            print(f"Warning: {hue_label} のデータ数とラベル数が一致していません。")
            continue

        for i, group_label in enumerate(x_labels):
            group_data = data_list[i]
            baseline_data = baseline[i] if baseline else [None] * len(group_data)
            if len(group_data) > 0:
                for val, bval in zip(group_data, baseline_data):
                    records.append(
                        {
                            "Value": val,
                            "Group": group_label,
                            "Type": hue_label,
                            "Baseline": bval,
                        }
                    )

    df = pd.DataFrame(records)
    plt.figure(figsize=(14, 10), layout="constrained")

    set_paper_style()
    sns.boxplot(
        x="Group",
        y="Value",
        hue="Type",
        data=df,
        width=0.6,
        palette="gist_ncar",
        legend=show_legend,
    )
    ax = plt.gca()

    for i, lab in enumerate(ax.get_xticklabels()):
        lab.set_visible(i in [0, 4, 9, 14, 19])

    plt.grid(True, axis="y", linestyle="--", alpha=0.7)


def boxplot_2item_plot_only(
    data1, data2, labels, legend: tuple[str, str] = ("Data1", "Data2")
) -> None:
    plt.figure(figsize=(12, 6))

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
