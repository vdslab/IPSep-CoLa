import datetime
import glob
import json
import os

import matplotlib.pyplot as plt


def get_data(file):
    with open(file) as f:
        data = json.load(f)
    return data


def main():
    today = datetime.date.today()
    now = datetime.datetime.now().time()
    save_dir = f"result/compare/webcola_fullSGD/{today}/{now}"
    os.makedirs(save_dir, exist_ok=True)

    dir = "src/data/SGD/sparse"
    files = glob.glob(f"{dir}/*.json")
    # base_names = ["no_cycle_tree.json", "qh882.json"]

    for file in files:
        base_file = os.path.basename(file)
        base_name = os.path.splitext(base_file)[0]
        print(base_name)
        try:
            webcola_stress = get_data(f"src/data/cola/stress/{base_file}")
            sparseSGD_stress = get_data(
                f"src/data/SGD/full/2024-07-22/10:13:42.987355/{base_file}"
            )
            sparseSGD_stress = [s for s in sparseSGD_stress]

            fig, ax = plt.subplots()
            ax.boxplot(
                [webcola_stress, sparseSGD_stress], labels=["WebCola", "full SGD"]
            )
            # ax.set_yscale("log")

            plt.title(base_name)
            plt.grid()

            plt.savefig(f"{save_dir}/{base_name}_stress_box.png")
            plt.close()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
