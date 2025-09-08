import argparse
import json
import os

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib import animation

from sgd.full_spherical import sgd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=".")
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--overlap-removal", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--cluster-overlap-removal", action=argparse.BooleanOptionalAction
    )
    parser.add_argument("input", nargs="+")
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    for filepath in args.input:
        basename = os.path.basename(filepath)
        graph: nx.Graph = nx.node_link_graph(json.load(open(filepath)), link="links")
        clusters = None
        if args.cluster_overlap_removal:
            clusters = [graph.nodes[u]["group"] for u in graph.nodes]
        pos = sgd(
            graph,
            iterations=args.iterations,
            overlap_removal=args.overlap_removal,
            clusters=clusters,
        )

        nodes = np.array([pos[v] for v in graph])
        edges = np.array([(pos[u], pos[v]) for u, v in graph.edges])

        # theta = np.linspace(0, 2 * np.pi, 100)
        # phi = np.linspace(0, np.pi, 50)
        # theta, phi = np.meshgrid(theta, phi)
        # r = 1
        # x = r * np.sin(phi) * np.cos(theta)
        # y = r * np.sin(phi) * np.sin(theta)
        # z = r * np.cos(phi)

        def init():
            ax.clear()
            ax.set_aspect("equal")
            # ax.plot_surface(x, y, z, cmap="viridis", alpha=0.3)
            ax.scatter(*nodes.T, alpha=0.2, s=100, color="blue")
            for vizedge in edges:
                ax.plot(*vizedge.T, color="gray")
            ax.grid(False)
            ax.set_axis_off()

        def _frame_update(index):
            ax.view_init(index * 0.2, index * 0.5)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        fig.tight_layout()

        ani = animation.FuncAnimation(
            fig,
            _frame_update,
            init_func=init,
            interval=50,
            cache_frame_data=False,
            frames=100,
        )
        ani.save("test.gif", writer="imagemagick")
        plt.show()
        plt.close()
        json.dump(pos, open(os.path.join(args.dest, basename), "w"), ensure_ascii=False)


if __name__ == "__main__":
    # main()

    import cProfile

    cProfile.run("main()", filename="main.prof")
