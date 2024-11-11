import glob
import json

import networkx as nx


class Constraint:
    def __init__(
        self, left: "Variable", right: "Variable", gap=5, equality=False
    ) -> None:
        self.left = left
        self.right = right
        self.gap = gap
        self.active = False
        self.lm = 0
        self.satisfiable = True
        self.equality = equality

    def violation(self) -> float:
        if self.satisfiable:
            violation = self.left.posn() + self.gap - self.right.posn()
            return violation
        return 0


class Variable:
    def __init__(self, desired_position, weight=1) -> None:
        self.desired_position = desired_position
        self.weight = weight
        self.offset = 0
        self.set_block = None
        self.vid = id(self)
        self.constraints_start: list[Constraint] = []
        self.constraints_end: list[Constraint] = []

    @property
    def block(self) -> "Block":
        return self.__block

    @block.setter
    def set_block(self, block: "Block"):
        self.__block = block

    def posn(self):
        return self.block.posn + self.offset

    def right_variables(self, cur: "Variable" = None) -> list["Variable"]:
        rvars = []
        for c in self.constraints_start:
            if c.right == cur:
                continue
            if not c.active:
                continue
            rvars.append(c.right)
            rvars += c.right.right_variables()
        return rvars

    def dfdv(self) -> float:
        return self.weight * (self.posn() - self.desired_position)

    def __str__(self) -> str:
        dps = f"desired_position={self.desired_position}"
        ws = f"weight={self.weight}"
        os = f"offset={self.offset}"
        s = f"Variable( {dps},\t{ws},\t{os} )"
        if self.set_block is not None:
            posn = self.posn()
            s = f"Variable( {dps}, {posn=} \t{ws},\t{os} )"
        return s

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, v: "Variable") -> bool:
        if v is None:
            return False
        return self.vid == v.vid

    def __hash__(self) -> int:
        return self.vid


class Block:
    def __init__(self, v: Variable) -> None:
        self.posn = v.desired_position
        self.ac = set()
        self.vars: set[Variable] = set()
        self.add_variable(v)
        self.__block_id = id(self)

    @property
    def block_id(self):
        return self.__block_id

    @block_id.setter
    def set_block_id(self, block_id):
        self.__block_id = block_id

    @block_id.getter
    def get_block_id(self):
        return self.__block_id

    def add_variable(self, v: Variable):
        self.vars.add(v)
        v.set_block = self
        self.update_posn()

    def update_posn(self):
        w_pos_sum = sum([v.desired_position * v.weight for v in self.vars])
        w_offset_sum = sum([v.offset * v.weight for v in self.vars])
        w_nvars = sum([v.weight for v in self.vars])
        self.posn = (w_pos_sum - w_offset_sum) / w_nvars

    def compute_dfdv(self, v: Variable, prev: Variable, f) -> float:
        print(f"{v.vid=}")
        dfdv = v.dfdv()
        for c in v.constraints_start:
            if not c.active:
                continue
            if c.right == prev:
                continue
            c.lm = self.compute_dfdv(c.right, v, f)
            f(c)
            dfdv += c.lm

        for c in v.constraints_end:
            if not c.active:
                continue
            if c.left == prev:
                continue
            c.lm = -self.compute_dfdv(c.left, v, f)
            f(c)
            dfdv -= c.lm
        return dfdv

    @staticmethod
    def split(c: Constraint):
        c.active = False
        left_block = Block(c.left)
        right_block = Block(c.right)

        return [
            Block.create_splited_block(c.left, left_block),
            Block.create_splited_block(c.right, right_block),
        ]

    @staticmethod
    def create_splited_block(start_v: Variable, block: "Block" = None) -> "Block":
        for c in start_v.constraints_start:
            if not c.active:
                continue
            c.right.offset = c.left.offset + c.gap
            block.add_variable(c.right)

        for c in start_v.constraints_end:
            if not c.active:
                continue
            c.left.offset = c.right.offset - c.gap
            block.add_variable(c.left)
        return block

    def min_lm(self) -> Constraint | None:
        m: Constraint = None

        def f(c: Constraint):
            nonlocal m
            if c.equality:
                return
            if m is None or c.lm < m.lm:
                m = c

        self.compute_dfdv(next(iter(self.vars)), None, f)
        return m

    def merge(self, b: "Block", c: Constraint, d: float):
        c.active = True
        for v in b.vars:
            v.offset += d
            self.add_variable(v)
        self.update_posn()

    def haveActivePath(self, start: Variable, end: Variable):
        if start == end:
            return True
        for c in start.constraints_start:
            if not c.active:
                continue
            if self.haveActivePath(c.right, end):
                return True
        return False

    def visit_path(self, start: Variable, prev: Variable, end: Variable, visit_func):
        to_end = False
        for c in start.constraints_start:
            if not c.active:
                continue
            if to_end:
                continue
            if c.right == prev:
                continue
            print(f"{c.right.vid=}")
            if c.right == end or self.visit_path(c.right, c.left, end, visit_func):
                to_end = True
                visit_func(c)
        return to_end

    def min_lm_between(self, left: Variable, right: Variable) -> Constraint | None:
        self.compute_dfdv(next(iter(self.vars)), None, lambda _: None)
        m: Constraint = None

        def f(c: Constraint):
            nonlocal m
            if c.equality:
                return
            if m is None or c.lm < m.lm:
                m = c

        self.visit_path(left, None, right, f)
        return m

    def split_between(self, left: Variable, right: Variable):
        c = self.min_lm_between(left, right)
        if c is None:
            return None

        bs = Block.split(c)
        return (c, bs)

    def cost(self):
        sm = 0
        for v in self.vars:
            d = v.posn() - v.desired_position
            sm += d * d * v.weight
        return sm


class Blocks:
    def __init__(self, vs: list[Variable]) -> None:
        self.blocks: list[Block] = []
        for v in vs:
            self.add_block(Block(v))

    def add_block(self, block: Block):
        block.set_block_id = len(self.blocks)
        self.blocks.append(block)

    def update_block_positions(self):
        for block in self.blocks:
            block.update_posn()

    def update_block_id(self):
        for i, block in enumerate(self.blocks):
            block.set_block_id = i
            for v in block.vars:
                v.set_block = block

    def split(self, inactive: list[Constraint]):
        self.update_block_positions()
        for block in self.blocks:
            c = block.min_lm()
            if c is None or c.lm >= 0:
                continue
            bs = Block.split(c)
            for b in bs:
                self.add_block(b)
            self.blocks.remove(block)
            inactive.append(c)

    def remove(self, b: Block):
        last_id = len(self.blocks) - 1
        swap_id = b.block_id
        (
            self.blocks[swap_id],
            self.blocks[last_id],
        ) = (
            self.blocks[last_id],
            self.blocks[swap_id],
        )
        self.blocks.pop()
        self.update_block_id()

    def merge(self, c: Constraint):
        lblock = c.left.block
        rblock = c.right.block
        d = c.left.offset + c.gap - c.right.offset
        for v in rblock.vars:
            v.set_block = lblock
        lblock.merge(rblock, c, d)
        self.update_block_id()
        self.remove(rblock)

    def cost(self):
        sm = 0
        for b in self.blocks:
            sm += b.cost()
        return sm


class SolveQPSC:
    def __init__(self, vs: list[Variable], cs: list[Constraint]) -> None:
        self.vs = vs
        self.cs = cs
        self.inactive: list[Constraint] = []
        for c in cs:
            c.left.constraints_start.append(c)
            c.right.constraints_end.append(c)
            c.active = False
            self.inactive.append(c)
        self.bs = None

    def set_start_positions(self, positions):
        self.inactive = []
        for c in self.cs:
            c.active = False
            self.inactive.append(c)
        self.bs = Blocks(self.vs)
        for i in range(len(positions)):
            self.bs.blocks[i].posn = positions[i]

    def set_desired_positions(self, positions):
        for i in range(len(positions)):
            self.vs[i].desired_position = positions[i]

    def max_violation(self) -> Constraint | None:
        max_violation_ci = None
        for i, c in enumerate(self.inactive):
            if not c.satisfiable:
                continue
            if max_violation_ci is None:
                max_violation_ci = i
            if (
                c.equality
                or c.violation() > self.inactive[max_violation_ci].violation()
            ):
                max_violation_ci = i
                if c.equality:
                    break

        max_violation_c = (
            self.inactive[max_violation_ci] if max_violation_ci is not None else None
        )
        if max_violation_ci is not None:
            c = self.inactive[max_violation_ci]
            if not c.active or c.equality:
                self.inactive[max_violation_ci] = self.inactive[-1]
                self.inactive.pop()
        return max_violation_c

    def solve(self):
        if self.bs is None:
            self.bs = Blocks(self.vs)

        self.bs.split(self.inactive)
        while c := self.max_violation():
            if c.active and (not c.equality):
                break
            if c.left.weight != 1:
                c.right.offset += c.violation()
            if c.right.weight != 1:
                c.left.offset += c.violation()
            lblock = c.left.block
            rblock = c.right.block
            if lblock.block_id != rblock.block_id:
                self.bs.merge(c)
                continue

            if lblock.haveActivePath(c.right, c.left):
                c.satisfiable = False
                continue
            split = lblock.split_between(c.left, c.right)
            if split is None:
                c.satisfiable = False
                continue

            c, bs = split
            for b in bs:
                self.bs.add_block(b)
            self.bs.remove(lblock)
            for v in lblock.vars:
                print(v.posn())
            if c.violation() > 0:
                self.inactive.append(c)
            else:
                self.bs.merge(c)

    def solveQPSC(self):
        self.solve()
        cnt = 0
        cost = self.bs.cost()
        prev_cost = cost * 2 + 1000
        while abs(prev_cost - cost) > 1e-6:
            self.solve()
            prev_cost = cost
            cost = self.bs.cost()
            cnt += 1
            print(self.vs)

        print(f"cost={cost}")


def get_initial_variable(
    graph: nx.Graph, indices: dict, desired_position: list[list[float]]
) -> dict[int, Variable]:
    nodes = graph.nodes
    variables = dict()
    for node in nodes:
        idx = indices[node]
        weight = 10000 if nodes[node].get("fixed") else 1
        variables[idx] = Variable(desired_position[idx], weight)
    vs = variables.items()
    vs = sorted(vs, key=lambda x: x[0])
    vs = [v for _, v in vs]
    return vs


from pprint import pprint

graph = nx.Graph()
graph.add_nodes_from([1, 2, 3])
graph.add_node(0, fixed=True)
graph.add_node(4, fixed=True)
indices = {node: i for i, node in enumerate(graph.nodes)}
vs = get_initial_variable(graph, indices, [10, 20, 30, 10, 35])

pprint(vs)
cs = [
    Constraint(vs[3], vs[0], 10),
    Constraint(vs[3], vs[1], 10),
    Constraint(vs[3], vs[2], 10),
    Constraint(vs[0], vs[4], 10),
    Constraint(vs[1], vs[4], 10),
    Constraint(vs[2], vs[4], 10),
    Constraint(vs[0], vs[1], 50),
    # Constraint(vs[1], vs[2], 20),
]
#
# for i in range(len(vs) - 2):
#     for j in range(i + 1, len(vs) - 2):
#         cs.append(Constraint(vs[i], vs[j], 5))
print(cs)
solver = SolveQPSC(vs, cs)
solver.set_start_positions([10, 20, 30, 10, 30])
solver.solveQPSC()


pprint(vs)
