import math
import random
import traceback

import egraph as eg
import networkx as nx
from networkx import all_pairs_dijkstra_path_length

from util.graph import nxgraph_to_eggraph
from util.graph.save_animation import save_animation
from util.parameter import SGDParameter

from .projection.circle_constraints import (
    project_circle_constraints,
    project_circle_constraints_hyper,
)


def sgd(nx_graph, overlap_removal=False, clusters=None, iterations=30, eps=0.1, seed=5):
    parameter = SGDParameter(iterator=iterations, eps=eps, seed=seed)
    dist_list = nx_graph.graph["distance"]
    diameter = nx.diameter(nx_graph)
    print(diameter)

    eggraph, indices = nxgraph_to_eggraph(nx_graph)
    distance = nx.floyd_warshall_numpy(nx_graph, weight=None)
    print(distance)
    dist = eg.DistanceMatrix(eggraph)
    for i, u in enumerate(nx_graph.nodes):
        for j, v in enumerate(nx_graph.nodes):
            dist.set(
                indices[u], indices[v], min(math.pi, distance[i][j] * (math.pi / 3))
            )

    # 初期配置ランダム、直線だとその直線上にしか動かない
    # 接平面から射影してるだけ
    drawing = eg.DrawingSpherical2d.initial_placement(eggraph)
    # for i in range(drawing.len()):
    #     drawing.set_lat(i, random.random() * math.pi - math.pi / 2)
    #     drawing.set_lon(i, random.random() * 2 * math.pi - math.pi)

    drawing.set_lat(0, math.radians(45))
    drawing.set_lon(0, math.radians(45))
    drawing.set_lat(4, math.radians(-45))
    drawing.set_lon(4, math.radians(45))

    drawing.set_lat(1, math.radians(45))
    drawing.set_lon(1, math.radians(135))
    drawing.set_lat(7, math.radians(-45))
    drawing.set_lon(7, math.radians(135))

    drawing.set_lat(3, math.radians(45))
    drawing.set_lon(3, math.radians(-45))
    drawing.set_lat(5, math.radians(-45))
    drawing.set_lon(5, math.radians(-45))

    drawing.set_lat(2, math.radians(45))
    drawing.set_lon(2, math.radians(-135))
    drawing.set_lat(6, math.radians(-45))
    drawing.set_lon(6, math.radians(-135))

    lat_x, lon_x = drawing.lat(0), drawing.lon(0)
    lat_y, lon_y = drawing.lat(7), drawing.lon(7)
    # delta_lat = abs(lat1 - lat0)
    # delta_lon = abs(lon1 - lon0)
    sin_lon_x, cos_lon_x = math.sin(lon_x), math.cos(lon_x)
    sin_lat_x, cos_lat_x = math.sin(lat_x), math.cos(lat_x)
    sin_lon_y, cos_lon_y = math.sin(lon_y), math.cos(lon_y)
    sin_lat_y, cos_lat_y = math.sin(lat_y), math.cos(lat_y)

    # 点xと点yのデカルト座標ベクトルの内積を計算
    dot_product = (
        sin_lat_x * sin_lat_y * math.cos(lon_y - lon_x) + cos_lat_x * cos_lat_y
    )

    # acosの定義域 [-1, 1] に値をクリップして、計算エラーを防ぐ
    d01 = math.acos(max(-1.0, min(1.0, dot_product)))
    print(d01, math.pi / 3)
    # print(d06)
    # assert abs(d06 - math.pi) < 1e-4
    sgd = eg.FullSgd.new_with_distance_matrix(dist)
    sgd.update_weight(lambda i, j, dij, wij: 1 / dij)
    rng = eg.Rng.seed_from(parameter.seed)

    # size = []
    if overlap_removal:
        overlap = eg.OverwrapRemoval(eggraph, lambda node_index: 0.3)
        overlap.iterations = 5

    circle_constraints = [
        [
            [indices[v] for v in c["nodes"]],
            c["r"],
            indices[c["center"]] if c.get("center") is not None else None,
        ]
        for c in nx_graph.graph["constraints"]
        if c.get("type", "") == "circle"
    ]

    def step(eta):
        try:
            sgd.shuffle(rng)
            sgd.apply(drawing, eta)
        except Exception:
            traceback.print_exc()

    sgd_scheduler = sgd.scheduler(
        parameter.iter,  # number of iterations
        parameter.eps,  # eps: eta_min = eps * min d[i, j] ^ 2
    )

    # pos = {u: [drawing.x(indices[u]), drawing.y(indices[u])] for u in nx_graph.nodes}

    positions = []
    circle_centers = []
    circle_radii = []

    for i in range(parameter.iter):
        print(f"iter:{i}")
        sgd_scheduler.step(step)

    # current_centers, current_radii = project_circle_constraints_hyper(
    #     drawing, circle_constraints, indices
    # )

    # circle_centers.append(current_centers)
    # circle_radii.append(current_radii)
    # pos = {
    #     u: [drawing.x(indices[u]), drawing.y(indices[u])] for u in nx_graph.nodes
    # }
    # positions.append(pos)

    pos = {}
    for i in nx_graph.nodes:
        # 2. 現在の緯度を取得
        lat = drawing.lat(indices[i])
        lon = drawing.lon(indices[i])
        pos[i] = [
            math.cos(lat) * math.cos(lon),
            math.cos(lat) * math.sin(lon),
            math.sin(lat),
        ]
    print(pos)
    return pos
