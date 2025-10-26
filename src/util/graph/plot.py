import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.colors import ListedColormap, Normalize


def plot_graph(
    G: nx.Graph,
    pos,
    file_name="graph.png",
    aspect="equal",
    show_violation=False,
    node_size=30,
    labeled=False,
):
    matplotlib.use("agg")
    fig, ax = plt.subplots(figsize=(10, 10), dpi=150)

    edge_color = ["black"] * len(G.edges)
    if show_violation:
        constraints = G.graph["constraints"]
        #   { "axis": "y", "left": 72, "right": 1, "gap": 20 },
        # gap = constraints[0]["gap"]
        y_violations = {
            tuple(sorted([str(c["right"]), str(c["left"])])): max(
                0, c["gap"] - (pos[str(c["right"])][1] - pos[str(c["left"])][1])
            )
            > 1e-1
            for c in constraints
            if c.get("axis", "") == "y"
        }
        # norm = Normalize(vmin=0, vmax=gap)
        # original_cmap = cm.get_cmap("Reds")
        # cmap = mcolors.LinearSegmentedColormap.from_list(
        #     "truncated_reds", original_cmap(np.linspace(0.2, 1.0, 256))
        # )

        print(y_violations)
        edge_color = [
            "red" if y_violations.get(tuple(sorted(e)), False) else "gray"
            for e in G.edges
        ]
        edge_width = [
            2 if y_violations.get(tuple(sorted(e)), False) else 1 for e in G.edges
        ]

    ax.set_aspect("equal")

    nx.draw(
        G,
        with_labels=labeled,
        pos=pos,
        node_shape="s",
        node_size=node_size,
        edge_color=edge_color,
        width=edge_width if show_violation else 0.5,
        ax=ax,
    )

    plt.axis("off")
    plt.margins(0)
    plt.gca().invert_yaxis()

    plt.savefig(file_name, bbox_inches="tight", pad_inches=0.01)
    plt.close()
