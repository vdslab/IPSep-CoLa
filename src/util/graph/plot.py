import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.colors import ListedColormap, Normalize


def plot_graph(
    G: nx.Graph, pos, file_name="graph.png", aspect="equal", show_violation=False
):
    matplotlib.use("agg")
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect(aspect)

    edge_color = ["black"] * len(G.edges)
    if show_violation:
        constraints = G.graph["constraints"]
        #   { "axis": "y", "left": 72, "right": 1, "gap": 20 },
        gap = constraints[0]["gap"]
        y_violations = {
            tuple(sorted([str(c["left"]), str(c["right"])])): c["gap"]
            - (pos[str(c["right"])][1] - pos[str(c["left"])][1])
            for c in constraints
            if c.get("axis", "") == "y"
            and (pos[str(c["right"])][1] - pos[str(c["left"])][1] < c["gap"])
        }
        norm = Normalize(vmin=0, vmax=gap)
        original_cmap = cm.get_cmap("Reds")
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "truncated_reds", original_cmap(np.linspace(0.2, 1.0, 256))
        )

        print(y_violations)
        edge_color = []
        for e in G.edges:
            # 辺 e が違反辞書に存在するかチェック
            violation_amount = y_violations.get(tuple(sorted(e)))
            if violation_amount is not None:
                # 違反量(violation_amount)を正規化(norm)し、カラーマップ(cmap)から色を取得
                edge_color.append(cmap(norm(min(gap, violation_amount))))
            else:
                # 違反していなければ黒
                edge_color.append("lightgray")
    nx.draw(
        G,
        with_labels=False,
        pos=pos,
        node_shape="o",
        node_size=10,
        edge_color=edge_color,
        width=[0.5] * G.number_of_edges(),
        ax=ax,
    )
    plt.gca().invert_yaxis()
    plt.savefig(file_name, dpi=150, bbox_inches="tight", pad_inches=0)
    plt.close()
