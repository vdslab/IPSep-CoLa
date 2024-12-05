import random
import unittest

import networkx as nx
import numpy as np

from ipsep_cola.block import NodeBlocks
from ipsep_cola.comp_dfdv import comp_dfdv
from ipsep_cola.constraint.constraint import Constraints


def calc_dfdv_dfs(
    child: int,
    AC: set,
    parent: int,
    constraints: Constraints,
    node_blocks: NodeBlocks,
    lm: dict,
):
    dfdv = (
        node_blocks.weight[child] * node_blocks.posn(child)
        - node_blocks.desired_position[child]
    )
    for c in AC:
        left = constraints.left(c)
        right = constraints.right(c)
        if child == left and parent != right:
            lm[c] = calc_dfdv_dfs(right, AC, child, constraints, node_blocks, lm)
            dfdv += lm[c]
        elif child == right and parent != left:
            lm[c] -= calc_dfdv_dfs(left, AC, child, constraints, node_blocks, lm)
            dfdv -= lm[c]
    return dfdv


class TestDFDV(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def setUp(self):
        print("setUp", self._testMethodName)
        graph: nx.Graph = nx.path_graph(5)
        nodes = graph.nodes
        n = graph.number_of_nodes()
        const = [[node, node + 1, 20] for node in nodes if node + 1 < n]
        self.constraints = Constraints(const, n)
        self.AC = set(range(len(const)))
        self.node_blocks = NodeBlocks(
            np.array([i * 20 * random.random() for i in range(n)]),
            np.array([i * 20 for i in range(n)]),
        )

        # TODO: 理想が現在の場所と間違えられてる

    def test_dfdv3(self):
        lm = comp_dfdv(0, self.AC, None, self.constraints, self.node_blocks)
        sub_lm = dict()
        calc_dfdv_dfs(0, self.AC, None, self.constraints, self.node_blocks, sub_lm)
        print(lm)
        print(sub_lm)
        self.assertEqual(lm, sub_lm)


if __name__ == "__main__":
    unittest.main()
