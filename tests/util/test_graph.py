import unittest

import egraph as eg
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
        self.assertLess(abs(Xstress - exact / 2), 1e-4)

    def test_digraph_stress(self):
        Y = np.array([[1, 4], [6, 4], [3, 2], [5, 1]])
        Ydist = np.array([[0, 2, 2, 4], [0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 0, 0]])
        Yweight = [[0, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
        Ystress = stress(Y, Ydist, Yweight)
        exact = 31 - 8 * pow(2, 0.5) - 4 * pow(5, 0.5)
        self.assertLess(abs(Ystress - exact / 2), 1e-4)

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
                self.assertLess(abs(matrix[i][j] - exact[i][j]), 1e-4)

    def test_stress_egraph(self):
        X = np.array([[1, 2], [3, 4]])
        Xdist = [[0, 1], [1, 0]]
        Xweight = [[0, 1], [1, 0]]
        Xstress = stress(X, Xdist, Xweight)

        graph = Graph()
        graph.add_edge(0, 1)
        graph.add_edge(1, 0)
        eggraph = eg.Graph()
        indices = {}
        for u in graph.nodes:
            indices[u] = eggraph.add_node(u)
        for u, v in graph.edges:
            eggraph.add_edge(indices[u], indices[v], (u, v))
        drawing = eg.DrawingEuclidean2d.initial_placement(eggraph)
        drawing.set_x(0, 1)
        drawing.set_y(0, 2)
        drawing.set_x(1, 3)
        drawing.set_y(1, 4)

        Y = [[drawing.x(i), drawing.y(i)] for i in range(2)]
        self.assertEqual(X.tolist(), Y)

        d = eg.all_sources_dijkstra(eggraph, lambda _: 1)
        Ydist = [[d.get(i, j) for j in range(2)] for i in range(2)]
        self.assertEqual(Ydist, Xdist)

        Ystress = eg.stress(drawing, d)

        s = 0
        for j in range(1, 2):
            for i in range(j):
                delta = X[i] - X[j]
                norm = np.linalg.norm(delta)
                e = (norm - Xdist[i][j]) / Xdist[i][j]
                s += e * e
        self.assertLess(abs(Ystress - s), 1e-4)

        exact = 18 - 8 * pow(2, 0.5)
        self.assertLess(abs(Ystress - exact / 2), 1e-4)
        self.assertLess(abs(Xstress - Ystress), 1e-4)


if __name__ == "__main__":
    unittest.main()
