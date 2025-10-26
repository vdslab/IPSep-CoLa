from collections import deque

import networkx as nx
import numpy as np

from ipsep_cola import NodeBlocks, project, split_blocks


def project_torus(drawing, constraints, graph: nx.Graph, indices, cell_size):
    n = drawing.len()
    x, y = torus_position_to_euclid(drawing, graph, indices, cell_size)
    for key in ["x", "y"]:
        if constraints[key] is None or len(constraints[key].constraints) == 0:
            continue

        x = np.array(x if key == "x" else y)
        block = NodeBlocks(x, x)
        while not split_blocks(x, constraints[key], block):
            pass
        new_x = project(constraints[key], block)
        for i in range(n):
            if key == "x":
                drawing.set_x(i, float(new_x[i]) / cell_size % 1)
            else:
                drawing.set_y(i, float(new_x[i]) / cell_size % 1)


def torus_position_to_euclid(drawing, graph: nx.Graph, indices):
    # 必ず9*9マスで完結するので+-1or0座標を取得
    n = drawing.len()
    xy = {
        u: [
            float(drawing.x(indices[u])),
            float(drawing.y(indices[u])),
        ]
        for u in graph.nodes
    }
    start = list(graph.nodes)[0]
    que = deque()
    que.append(start)
    new_xy = dict()
    new_xy[start] = [xy[start][0], xy[start][1]]

    while que:
        v = que.popleft()
        for u in graph.neighbors(v):
            nx, ny = nearest_xy_torus2d(xy[v], xy[u])
            if new_xy.get(u, None) is None:
                new_xy[u] = [nx, ny]
                que.append(u)

    position = sorted([(indices[u], new_xy[u]) for u in graph.nodes])

    x, y = zip(*[position[i][1] for i in range(n)])
    return x, y


def nearest_xy_torus2d(center, other):
    x = other[0]
    y = other[1]
    d = float("inf")
    near = [other[0], other[1]]
    for dy in [-1, 0, 1]:
        y0 = y + dy
        for dx in [-1, 0, 1]:
            x0 = x + dx
            dist = (center[0] - x0) ** 2 + (center[1] - y0) ** 2
            if dist < d:
                d = dist
                near = [x0, y0]

    return near


def draw_torus(
    graph, pos, cell_size=1, output="./test.png", node_size=30, show_violation=False
):
    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.use("agg")

    fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
    ax.set_aspect("equal")

    # 1. BFS to unwrap coordinates into a single Euclidean representation
    start_node = list(graph.nodes)[0]
    unwrapped_pos = {start_node: np.array(pos[start_node])}
    queue = deque([start_node])

    while queue:
        v = queue.popleft()
        for u in graph.neighbors(v):
            if u not in unwrapped_pos:
                # Find the nearest image of u relative to v
                unwrapped_pos[u] = np.array(
                    nearest_xy_torus2d(unwrapped_pos[v], pos[u])
                )
                queue.append(u)

    # Define the grid for tiling
    offsets = [-1, 0, 1]

    # 2. Draw nodes for each tile
    for i in offsets:
        for j in offsets:
            offset_vector = np.array([i, j])
            # Create positions for the current tile
            tile_pos = {
                node: (xy - offset_vector) * cell_size
                for node, xy in unwrapped_pos.items()
            }
            node_colors = ["#1f78b4"] * len(graph.nodes)
            if show_violation:
                # highlight nodes that nodepair is overlapped
                for u in graph.nodes:
                    for v in graph.nodes:
                        if u == v:
                            continue
                        dist = np.linalg.norm(unwrapped_pos[u] - unwrapped_pos[v])
                        print(dist)
                        if dist < 0.10:  # threshold for overlap
                            node_colors[list(graph.nodes).index(u)] = "red"
                            node_colors[list(graph.nodes).index(v)] = "red"

            # if i == 0 and j == 0:
            nx.draw_networkx_nodes(
                graph,
                pos=tile_pos,
                ax=ax,
                node_shape="o",
                node_size=node_size,
                node_color=node_colors,
            )
            # nx.draw_networkx_labels(graph, pos=tile_pos, ax=ax)

    # 3. Draw edges manually for each tile
    for u, v in graph.edges():

        def make_edge(start, posv):
            end_point = nearest_xy_torus2d(start, posv)
            for i in offsets:
                for j in offsets:
                    offset_vector = np.array([i, j])
                    vv = np.array(start) - offset_vector
                    uu = np.array(end_point) - offset_vector
                    line = plt.Line2D(
                        [vv[0] * cell_size, uu[0] * cell_size],
                        [vv[1] * cell_size, uu[1] * cell_size],
                        color="gray",
                        zorder=0,  # Draw edges behind nodes
                        linewidth=6,
                    )
                    ax.add_line(line)

        make_edge(pos[u], pos[v])
        make_edge(pos[v], pos[u])

    # mn = -0.05
    # mx = 1.05

    # gp = dict()
    # for j in [-1, 0, 1]:
    #     for i in [-1, 0, 1]:
    #         p = {k: [v[0] - i, v[1] - j] for k, v in new_xy.items()}
    #         for k, v in new_xy.items():
    #             gp[f"{k}{i}{j}"] = [v[0] - i, v[1] - j]
    #         nx.draw(
    #             graph,
    #             pos=p,
    #             ax=ax,
    #             node_shape="o",
    #             node_color="lightgreen",
    #             node_size=50,
    #             with_labels=False,
    #         )
    # G = nx.Graph()
    # # G.add_edge("300", "10-10")
    # nx.draw(
    #     G,
    #     pos=gp,
    #     ax=ax,
    #     node_shape="o",
    #     node_color="lightgreen",
    #     node_size=400,
    #     # with_labels=True,
    # )

    view_margin = 0.2 * cell_size
    ax.set_xlim(-view_margin, cell_size + view_margin)
    ax.set_ylim(-view_margin, cell_size + view_margin)

    # Draw central cell boundaries
    ax.axvline(0, color="k", linestyle=":")
    ax.axvline(cell_size, color="k", linestyle=":")
    ax.axhline(0, color="k", linestyle=":")
    ax.axhline(cell_size, color="k", linestyle=":")
    print("save_fig")
    plt.axis("off")
    plt.margins(0)
    plt.gca().invert_yaxis()
    plt.savefig(output, bbox_inches="tight", pad_inches=0.01)
