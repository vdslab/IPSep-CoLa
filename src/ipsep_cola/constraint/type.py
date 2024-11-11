from enum import Enum, auto


class ConstraintType(Enum):
    SEPARATE = 0
    ALIGNMENT = auto()
    BOUNDING_BOX = auto()
