def get_constraints_dict(constraints, *, default_gap=20):
    C: dict[str, list] = dict()
    C["y"] = []
    C["x"] = []
    for c in constraints:
        left = c["left"]
        right = c["right"]
        axis = c["axis"]
        gap = c["gap"]
        C[axis].append([left, right, gap])
    return C
