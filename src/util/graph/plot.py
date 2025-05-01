import matplotlib
import matplotlib.pyplot as plt
import networkx as nx


def plot_graph(G: nx.Graph, pos, file_name="graph.png", aspect="equal"):
    matplotlib.use('agg')
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect(aspect)
    nx.draw(
        G,
        with_labels=False,
        pos=pos,
        node_shape="o",
        node_size=50,
        ax=ax,
    )
    plt.gca().invert_yaxis()
    plt.savefig(file_name)
    plt.close()
