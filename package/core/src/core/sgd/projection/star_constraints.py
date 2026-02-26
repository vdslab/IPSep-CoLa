import math
import random
from collections import deque

import networkx as nx


def cartesianBarycenterHeuristic(root, graph: nx.Graph, drawing, indices, layer_gap=1):
    digraph = to_digraph(root, graph, indices)
    initialize_node_attributes(digraph, drawing)
    num_layers = assign_radial_layers(digraph, start=root)
    cartesian_barycenter_ordering(digraph, num_layers)
    assign_final_coordinates(digraph, num_layers, layer_gap=layer_gap)


def to_digraph(root, graph: nx.Graph, indices):
    queue = deque([root])
    visited = set([root])
    digraph = nx.DiGraph()
    digraph.add_nodes_from([indices[v] for v in graph.nodes])

    while queue:
        v = queue.popleft()
        for u in graph.neighbors(v):
            if u not in visited:
                digraph.add_edge(indices[v], indices[u])
                visited.add(u)
    return digraph


def initialize_node_attributes(G: nx.DiGraph, drawing):
    """ノード属性を初期化する"""
    for node in G.nodes():
        G.nodes[node]["layer"] = -1
        G.nodes[node]["order"] = 0
        G.nodes[node]["pos"] = (drawing.x(node), drawing.y(node))


def assign_radial_layers(G: nx.DiGraph, start: int | None = None):
    """
    シンクノードからの最長経路に基づいて、各ノードに放射状の階層を割り当てる。
    シンクは階層0に配置され、階層番号は中心に向かって増加する。
    """
    # シンクノード（出次数が0のノード）を見つける
    sinks = [node for node, out_degree in G.out_degree if out_degree == 0]
    if start is not None:
        sinks.append(start)

    if not sinks:
        # シンクがない場合（例：サイクルのみのグラフ）、ランダムなノードを開始点とする
        sinks = [list(G.nodes())]

    # シンクノードを階層0に設定
    for node in sinks:
        G.nodes[node]["layer"] = 0

    queue = deque(sinks)
    visited = set(sinks)
    max_layer = 0

    # 辺を逆向きにたどるグラフを作成
    G_rev = G.reverse(copy=True)

    head = 0
    while queue:
        u = queue.popleft()
        head += 1

        # G_revでの近傍は、元のグラフGでの先行ノード
        for v in G_rev.neighbors(u):
            if v not in visited:
                # 先行ノードの階層を、現在のノードの階層+1に設定
                G.nodes[v]["layer"] = G.nodes[u]["layer"] + 1
                max_layer = max(max_layer, G.nodes[v]["layer"])
                visited.add(v)
                queue.append(v)

    # 未訪問のノード（到達不可能なコンポーネント）があれば、それらも処理
    unvisited_nodes = set(G.nodes()) - visited
    if unvisited_nodes:
        # 簡単な処理として、残りのノードを最も内側の階層に配置
        for node in unvisited_nodes:
            G.nodes[node]["layer"] = max_layer + 1
        max_layer += 1

    # # 階層を反転させる（中心が0、外側が大きくなるように）
    num_layers = max_layer + 1
    # for node in G.nodes():
    #     G.nodes[node]["layer"] = max_layer - G.nodes[node]["layer"]

    return num_layers


def cartesian_barycenter_ordering(G: nx.DiGraph, num_layers, iterations=20):
    """
    カーテシアン重心ヒューリスティックを用いて、各階層のノード順序を決定し、
    辺の交差を削減する。
    """
    # 各階層のノードをリストとして保持
    layers = [[] for _ in range(num_layers)]
    for node in G.nodes():
        layers[G.nodes[node]["layer"]].append(node)

    # 各階層のノードをランダムに初期順序付け
    for i in range(num_layers):
        random.shuffle(layers[i])
        for order, node in enumerate(layers[i]):
            G.nodes[node]["order"] = order

    # 反復スイープによる交差削減
    for _ in range(iterations):
        # Downward sweep (中心から外側へ)
        for i in range(1, num_layers):
            reorder_layer(G, layers, layer_index=i, neighbor_layer_index=i - 1)

        # Upward sweep (外側から中心へ)
        for i in range(num_layers - 2, -1, -1):
            reorder_layer(G, layers, layer_index=i, neighbor_layer_index=i + 1)


def reorder_layer(G: nx.DiGraph, layers, layer_index, neighbor_layer_index):
    """指定された階層を、隣接階層に基づいて再順序付けする。"""
    nodes_to_order = layers[layer_index]
    neighbor_nodes = layers[neighbor_layer_index]

    if not nodes_to_order or not neighbor_nodes:
        return

    barycenter_angles = {}
    neighbor_radius = (
        neighbor_layer_index + 1
    )  # 簡単のため半径を階層インデックス+1とする
    num_neighbors_in_layer = len(neighbor_nodes)

    for v in nodes_to_order:
        # vの隣接ノードで、neighbor_layerに属するものを見つける
        v_neighbors = [
            u for u in G.predecessors(v) if G.nodes[u]["layer"] == neighbor_layer_index
        ]
        v_neighbors.extend(
            [u for u in G.successors(v) if G.nodes[u]["layer"] == neighbor_layer_index]
        )

        if not v_neighbors:
            barycenter_angles[v] = random.uniform(
                0, 2 * math.pi
            )  # 孤立ノードはランダムな角度
            continue

        sum_x, sum_y = 0.0, 0.0
        for u in v_neighbors:
            u_order = G.nodes[u]["order"]
            angle = (2 * math.pi * u_order) / num_neighbors_in_layer
            sum_x += neighbor_radius * math.cos(angle)
            sum_y += neighbor_radius * math.sin(angle)

        avg_x = sum_x / len(v_neighbors)
        avg_y = sum_y / len(v_neighbors)

        barycenter_angles[v] = math.atan2(avg_y, avg_x)

    # 計算された重心の角度に基づいてノードをソート
    sorted_nodes = sorted(nodes_to_order, key=lambda n: barycenter_angles.get(n, 0))

    # 新しい順序をノード属性に反映
    for order, node in enumerate(sorted_nodes):
        G.nodes[node]["order"] = order

    # layersリストも更新
    layers[layer_index] = sorted_nodes


def assign_final_coordinates(
    G: nx.DiGraph, num_layers, layer_gap=50, node_gap_factor=1.2
):
    """
    各ノードの(layer, order)に基づいて、最終的な(x, y)座標を割り当てる。
    """
    layers = [[] for _ in range(num_layers)]
    for node in G.nodes():
        layers[G.nodes[node]["layer"]].append(node)

    for i in range(num_layers):
        layer_nodes = layers[i]
        num_nodes_in_layer = len(layer_nodes)
        if num_nodes_in_layer == 0:
            continue

        # 階層の半径を計算
        # 外側の階層ほど多くのノードを配置するため、円周を考慮する
        radius = (i + 1) * layer_gap

        for node in layer_nodes:
            order = G.nodes[node]["order"]
            # 角度を計算
            angle = (2 * math.pi * order) / num_nodes_in_layer

            # 座標を計算して保存
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            G.nodes[node]["pos"] = (x, y)
