from typing import overload


class Rect:
    def __init__(self, x: float, y: float, w: int, h: int):
        self.x: float = x
        self.y: float = y
        self.w: int = w
        self.h: int = h
        self.left_x: float = x
        self.right_x: float = x + w
        self.top_y: float = y
        self.bottom_y: float = y + h

    def __str__(self):
        return f"Rect(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.x, self.y, self.w, self.h))

    def union(self, other: "Rect") -> "Rect":
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.right_x, other.right_x) - x
        h = max(self.bottom_y, other.bottom_y) - y
        return Rect(x, y, w, h)

    # axis x
    @overload
    def is_overlap_x(self, x: float) -> bool:
        return self.left_x <= x <= self.right_x

    @overload
    def is_overlap_x(self, other: "Rect") -> bool:
        left_overlap = self.is_overlap_x(other.left_x)
        right_overlap = self.is_overlap_x(other.right_x)
        return left_overlap or right_overlap

    @overload
    def how_overlap_x(self, x: float) -> float:
        return self.right_x - x

    @overload
    def how_overlap_x(self, other: "Rect") -> float:
        return self.how_overlap_x(other.left_x)

    def move_x(self, dx: float):
        self.x += dx
        self.left_x += dx
        self.right_x += dx

    def set_center_x(self, x: float):
        self.x = x - self.w / 2
        self.left_x = x
        self.right_x = x + self.w

    # axis y
    @overload
    def is_overlap_y(self, y: float) -> bool:
        return self.top_y <= y <= self.bottom_y

    @overload
    def is_overlap_y(self, other: "Rect") -> bool:
        top_overlap = self.is_overlap_y(other.top_y)
        bottom_overlap = self.is_overlap_y(other.bottom_y)
        return top_overlap or bottom_overlap

    @overload
    def how_overlap_y(self, y: float) -> float:
        return self.bottom_y - y

    @overload
    def how_overlap_y(self, other: "Rect", other_is_top: bool = False) -> float:
        if other_is_top:
            return other.how_overlap_y(self.top_y)
        return self.how_overlap_y(other.top_y)

    def move_y(self, dy: float):
        self.y += dy
        self.top_y += dy
        self.bottom_y += dy

    def set_center_y(self, y: float):
        self.y = y - self.h / 2
        self.top_y = y
        self.bottom_y = y + self.h
