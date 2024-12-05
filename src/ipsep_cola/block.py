from numpy import ndarray


class Block:
    def __init__(self, node_id, posn):
        self.posn = posn
        self.nvars = 1
        self.active = set()
        self.vars = set()
        self.vars.add(node_id)
        self.node_id = node_id
        self.init_posn = posn

    def __str__(self) -> str:
        return f"Block(\n\tposn={self.posn},\n\tnvars={self.nvars},\n\tactive={self.active},\n\tvars={self.vars})"

    def __dict__(self) -> dict:
        return {
            "posn": int(self.posn),
            "nvars": int(self.nvars),
            "active": list(self.active),
            "vars": list(self.vars),
        }


class NodeBlocks:
    def __init__(self, axis_positions: ndarray, desired_positions: ndarray):
        if axis_positions.ndim != 1:
            raise ValueError("axis_positions must be a 1D array")

        n = len(axis_positions)
        self.n = n
        self.blocks = [i for i in range(n)]
        self.offset = [0 for _ in range(n)]
        self.weight = [1 for _ in range(n)]
        self.B: list[Block] = [Block(i, axis_positions[i]) for i in range(n)]
        self.__positions = axis_positions[:]
        self.desired_position = desired_positions[:]

    def fixedWeight(self, i: int, w: float = 1000):
        self.weight[i] = w

    def __str__(self) -> str:
        return f"NodeBlocks(positions={self.__positions}, B={self.B}, blocks={self.blocks}, offset={self.offset})"

    def __dict__(self) -> dict:
        return {
            "positions": [float(p) for p in self.__positions],
            "B": [b.__dict__() for b in self.B if b.nvars > 0],
            "blocks": [int(b) for b in self.blocks],
            "offset": [float(o) for o in self.offset],
        }

    def posn(self, vi):
        # if vi in [100, 101]:
        #     return self.desired_position[vi]
        return self.B[self.blocks[vi]].posn + self.offset[vi]

    @property
    def positions(self):
        return self.__positions

    @positions.setter
    def positions(self, positions: ndarray):
        if positions.ndim != 1:
            raise ValueError("positions must be a 1D array")
        self.__positions = positions

    # def positions(self, i: int, x: float):
    #     if i < self.n - 2:
    #         self.__positions[i] = x
