import itertools


def overlap1d(x00, x01, x10, x11):
    return (x00 < x11 and x10 < x01) or (x10 < x01 and x00 < x11)


def overlap(x00, y00, x01, y01, x10, y10, x11, y11):
    return overlap1d(x00, x01, x10, x11) and overlap1d(y00, y01, y10, y11)


def generate_overlap_removal_constraints(drawing, size, axis='y'):
    for i, j in itertools.combinations(range(drawing.len()), 2):
        x1 = drawing.x(i)
        y1 = drawing.y(i)
        w1, h1 = size[i]
        x2 = drawing.x(j)
        y2 = drawing.y(j)
        w2, h2 = size[j]
        if axis == 'x':
            if overlap1d(y1 - h1 / 2, y1 + h1 / 2, y2 - h2 / 2, y2 + h2 / 2):
                if x1 < x2:
                    yield ('x', [i, j, (w1 + w2) / 2])
                else:
                    yield ('x', [j, i, (w1 + w2) / 2])
        else:
            if overlap1d(x1 - w1 / 2, x1 + w1 / 2, x2 - w2 / 2, x2 + w2 / 2):
                if y1 < y2:
                    yield ('y', [i, j, (h1 + h2) / 2])
                else:
                    yield ('y', [j, i, (h1 + h2) / 2])
