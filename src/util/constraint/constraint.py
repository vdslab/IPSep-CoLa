class Constraints:
    def __init__(self, C: list[list] = None, node_len: int = 0) -> None:
        self.constraints = C
        self.graph = [[] for _ in range(node_len)]
        self.in_graph = [[] for _ in range(node_len)]
        for l, r, g in C:
            self.graph[l - 1].append((r - 1, g))
            self.in_graph[r - 1].append((l - 1, g))

    def left(self, index) -> int:
        return self.constraints[index][0]

    def right(self, index) -> int:
        return self.constraints[index][1]

    def gap(self, index) -> int:
        return self.constraints[index][2]
