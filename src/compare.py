import datetime
import os
import matplotlib.pyplot as plt
from ipsep_cola.main import run_IPSep_CoLa

from sgd.main import sgd_with_project
from util.graph import get_graph_and_constraints, plot_graph


def main():
    today = datetime.date.today()
    now = datetime.datetime.now().time()
    save_dir = f"result/compare/{today}/{now}"
    os.makedirs(save_dir, exist_ok=True)

    # for gap in gaps:
    #     for edge_length in edge_lengths:
    filename = "les_miserables_graph.json"
    # filename = "./src/data/no_cycle_tree.json"

    graph, _ = get_graph_and_constraints(filename)

    print("do sgd with project")
    Z, sgd_stresses, sgd_times = sgd_with_project(
        file_path=filename,
        edge_length=20,
        gap=30,
        iter_count=300,
        eps=0.01,
    )

    graph, _ = get_graph_and_constraints(filename)
    plot_graph(graph, Z, save_dir, "sgd_with_project.png")

    print("do IPSep CoLa")
    Z, stresses, times = run_IPSep_CoLa(
        file_path=filename,
        edge_length=20,
        gap=30,
        unconstrainedIter=100,
        customConstrainedIter=100,
        allIter=100,
    )

    plot_graph(graph, Z, save_dir, "IPSep_CoLa.png")

    def save_fig(*, xy, xlabel, ylabel, title, legend, filename, save_dir=""):
        fig, ax = plt.subplots()
        for x, y in xy:
            ax.plot(x, y)
        ax.set_yscale("log")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(legend)
        plt.savefig(os.path.join(save_dir, filename))
        plt.close()

    save_fig(
        xy=[(times, stresses), (sgd_times, sgd_stresses)],
        xlabel="time (second)",
        ylabel="stress",
        title="stress-time",
        legend=["IPSep_CoLa", "use SGD"],
        filename="stress_time.png",
        save_dir=save_dir,
    )

    save_fig(
        xy=[
            (list(range(len(stresses))), stresses),
            (list(range(len(sgd_stresses))), sgd_stresses),
        ],
        xlabel="iteration",
        ylabel="stress",
        title="stress-iteration",
        legend=["IPSep_CoLa", "use SGD"],
        filename="stress.png",
        save_dir=save_dir,
    )


# import cProfile

if __name__ == "__main__":
    # cProfile.run("main()", sort="cumtime", filename="compare.prof")
    main()
