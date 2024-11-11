from abc import ABC, abstractmethod
from enum import Enum, auto


class ConstraintType(Enum):
    SEPARATE = 0
    ALIGNMENT = auto()
    BOUNDING_BOX = auto()


class ConstraintABC(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass


class VariableABC(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass


class Constraint(ConstraintABC):
    def __init__(self, left: VariableABC, right: VariableABC, gap: int) -> None:
        self.left = left
        self.right = right
        self.gap = gap
        self.active = False
        self.lm = 0
        self.satisfiable = True


class Variable(VariableABC):
    def __init__(
        self,
        desired_position,
    ) -> None:
        self.desired_position = desired_position


class Block:
    def __init__(self, vars: set, nvars: int, posn: float) -> None:
        self.vars = vars
        self.nvars = nvars
        self.posn = posn
        self.active = set()
