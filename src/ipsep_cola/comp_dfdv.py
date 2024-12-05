import networkx as nx

from ipsep_cola.constraint.constraint import Constraints

from .block import NodeBlocks


def make_ditree(root, graph: nx.Graph):
    digraph = nx.DiGraph()
    stack = [root]
    checked = set()
    checked.add(root)
    while stack:
        child = stack.pop()
        for c in graph.edges(child):
            if c[1] in checked:
                continue
            checked.add(c[1])
            stack.append(c[1])
            digraph.add_edge(*c)
    return digraph


def comp_dfdv(
    child: int, AC: set, parent: int, constraints: Constraints, node_blocks: NodeBlocks
) -> dict[int, int]:
    # print(child)
    edges = dict()
    edge_set = set()
    nodes = set()
    for c in AC:
        left = constraints.left(c)
        right = constraints.right(c)
        edges[(left, right)] = c
        edges[(right, left)] = c
        edge_set.add((left, right))
        nodes.add(left)
        nodes.add(right)

    if child not in nodes:
        return dict()

    ac_graph = nx.Graph(edges.keys())
    ac_digraph = make_ditree(child, ac_graph)

    x = node_blocks.desired_position
    dfdv = {
        node: node_blocks.weight[node] * (node_blocks.posn(node) - x[node])
        for node in nodes
    }
    for c in reversed(list(nx.topological_sort(ac_digraph))):
        for p in ac_digraph.predecessors(c):
            dfdv[p] += dfdv[c]

    lm = dict()
    for edge in ac_digraph.edges:
        c = edges.get(edge)
        if (c := edges.get(edge)) is not None:
            lm[c] = dfdv[edge[1]]
        else:
            raise ValueError(f"no edge {edge} in {edges}")

    return lm
