import os

import matplotlib.pyplot as plt
import networkx as nx


def plot_graph(G: nx.Graph, Z, save_dir, file_name="graph.png", aspect="equal"):
    n = G.number_of_nodes()
    print(n)
    position = {i: Z[i] for i in range(n)}

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect(aspect)
    nx.draw(
        G,
        with_labels=True,
        pos=position,
        node_shape="o",
        node_size=50,
        ax=ax,
    )
    plt.gca().invert_yaxis()
    plt.savefig(os.path.join(save_dir, file_name))
    plt.close()
