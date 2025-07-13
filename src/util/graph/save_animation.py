import matplotlib.animation as animation
import matplotlib.pyplot as plt
import networkx as nx


def save_animation(
    output_path,
    nx_graph,
    positions,
    circle_centers,
    circle_radii,
):
    fig, ax = plt.subplots(figsize=(10, 10))

    def update(i):
        ax.clear()
        nx.draw(
            nx_graph,
            with_labels=True,
            pos=positions[i],
            node_shape="o",
            node_size=50,
            ax=ax,
        )
        if i < len(circle_centers) and i < len(circle_radii):
            for (cx, cy), r in zip(circle_centers[i], circle_radii[i]):
                ax.plot(cx, cy, "ro")  # Plot the center
                circle = plt.Circle(
                    (cx, cy), r, color="r", fill=False, linestyle="--"
                )
                ax.add_artist(circle)
        ax.set_title(f"Iteration {i}")
        plt.gca().invert_yaxis()

    ani = animation.FuncAnimation(fig, update, frames=len(positions), interval=200)
    ani.save(output_path, writer="imagemagick")
    plt.close()
