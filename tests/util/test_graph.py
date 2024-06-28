import unittest

import numpy as np
from networkx import Graph
from util.graph import distance_matrix, stress


class TestGraph(unittest.TestCase):
    def test_graph_stress(self):
        X = np.array([[1, 2], [3, 4]])
        Xdist = [[0, 1], [1, 0]]
        Xweight = [[0, 1], [1, 0]]
        Xstress = stress(X, Xdist, Xweight)
        exact = 18 - 8 * pow(2, 0.5)
        self.assertLess(Xstress - exact, 1e-4)

    def test_digraph_stress(self):
        Y = np.array([[1, 4], [6, 4], [3, 2], [5, 1]])
        Ydist = np.array([[0, 2, 2, 4], [0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 0, 0]])
        Yweight = [[0, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
        Ystress = stress(Y, Ydist, Yweight)
        exact = 31 - 8 * pow(2, 0.5) - 4 * pow(5, 0.5)
        self.assertLess(Ystress - exact, 1e-4)

    def test_distance_matrix(self):
        graph = Graph()
        graph.add_edge(1, 2)
        graph.add_edge(2, 3)
        matrix = distance_matrix(graph)
        exact = [[0, 1, 2], [1, 0, 1], [2, 1, 0]]
        self.assertEqual(len(matrix), len(exact))
        for i in range(len(matrix)):
            self.assertEqual(len(matrix[i]), len(exact[i]))
            for j in range(len(matrix[i])):
                self.assertAlmostEqual(matrix[i][j], exact[i][j], 1e-4)


if __name__ == "__main__":
    unittest.main()
