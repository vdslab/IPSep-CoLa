import datetime
import os

import matplotlib.pyplot as plt
from ipsep_cola.main import run_IPSep_CoLa
from majorization.main import weights_of_normalization_constant
from networkx import floyd_warshall_numpy
from sgd.main import sgd_with_project
from util.graph import get_graph_and_constraints, plot_graph, stress


def main():
    today = datetime.date.today()
    now = datetime.datetime.now().time()
    save_dir = f"result/compare/{today}/{now}"
    os.makedirs(save_dir, exist_ok=True)

    # for gap in gaps:
    #     for edge_length in edge_lengths:
    filenames = [
        "1138_bus.json",
        # "3elt.json",
        # "dwt_1005.json",
        # "dwt_2680.json",
        # "poli.json",
        # "USpowerGrid.json",
        # "qh882.json",
    ]
    # filenames = [
    #     "les_miserables_graph.json",
    #     "karate_club.json",
    #     "florentine_familes_graph.json",
    #     "davis_southern_women_graph.json",
    # ]
    for filename in filenames:
        graph, _ = get_graph_and_constraints(
            "src/data/json/download/no_cycle_tree.json"
        )

        print("do sgd with project")
        Z, sgd_stresses, sgd_times = sgd_with_project(
            file_path="src/data/json/download/no_cycle_tree.json",
            edge_length=20,
            gap=25,
            iter_count=15,
            eps=0.01,
        )

        graph, _ = get_graph_and_constraints(
            "src/data/json/download/no_cycle_tree.json"
        )
        plot_graph(graph, Z, save_dir, f"{"no_cycle_tree"}_sgd_with_project.png")
        dist = floyd_warshall_numpy(graph)
        print(dist)
        dist *= 20
        alpha = 2
        weights = weights_of_normalization_constant(alpha, dist)
        print(stress(Z, dist, weights))

        # print("do IPSep CoLa")
        # Z, stresses, times = run_IPSep_CoLa(
        #     file_path=filename,
        #     edge_length=20,
        #     gap=30,
        #     unconstrainedIter=5,
        #     allIter=10,
        # )

        # plot_graph(graph, Z, save_dir, f"{filename}_IPSep_CoLa.png")

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

        # save_fig(
        #     xy=[(times, stresses), (sgd_times, sgd_stresses)],
        #     xlabel="time (second)",
        #     ylabel="stress",
        #     title="stress-time",
        #     legend=["IPSep_CoLa", "use SGD"],
        #     filename=f"{filename}_tress_time.png",
        #     save_dir=save_dir,
        # )
        # save_fig(
        #     xy=[(sgd_times, sgd_stresses)],
        #     xlabel="time (second)",
        #     ylabel="stress",
        #     title="stress-time",
        #     legend=["use SGD"],
        #     filename=f"{filename}_tress_time.png",
        #     save_dir=save_dir,
        # )

        # save_fig(
        #     xy=[
        #         (list(range(len(stresses))), stresses),
        #         (list(range(len(sgd_stresses))), sgd_stresses),
        #     ],
        #     xlabel="iteration",
        #     ylabel="stress",
        #     title="stress-iteration",
        #     legend=["IPsep", "use SGD"],
        #     filename=f"{filename}_stress.png",
        #     save_dir=save_dir,
        # )
        # save_fig(
        #     xy=[
        #         (list(range(len(sgd_stresses))), sgd_stresses),
        #     ],
        #     xlabel="iteration",
        #     ylabel="stress",
        #     title="stress-iteration",
        #     legend=["use SGD"],
        #     filename=f"{filename}_stress.png",
        #     save_dir=save_dir,
        # )


# import cProfile

if __name__ == "__main__":
    # cProfile.run("main()", sort="cumtime", filename="compare.prof")
    main()
