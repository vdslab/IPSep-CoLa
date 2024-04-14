class Block:
    def __init__(self, node_id, posn):
        self.posn = posn
        self.nvars = 1
        self.active = set()
        self.vars = set()
        self.vars.add(node_id)

    def __str__(self) -> str:
        return f"Block(posn={self.posn}, nvars={self.nvars}, active={self.active}, vars={self.vars})"


class NodeBlocks:
    def __init__(self, node_len, axis_positions):
        n = len(axis_positions)
        self.blocks = [i for i in range(n)]
        self.offset = [0 for _ in range(n)]
        self.B = [Block(i, axis_positions[i]) for i in range(n)]