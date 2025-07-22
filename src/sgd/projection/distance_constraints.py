import numpy as np


def project_distance_constraints(drawing, constraints, indices):
    for v, u, gap in constraints:
        posv = np.array([drawing.x(v), drawing.y(v)])
        posu = np.array([drawing.x(u), drawing.y(u)])
        dist = max(0.01, np.linalg.norm(posu - posv))
        if dist < gap:
            unit = (posu - posv) / dist
            r = (dist - gap) / 2 * unit
            posv += r
            posu -= r
            drawing.set_x(v, posv[0])
            drawing.set_y(v, posv[1])
            drawing.set_x(u, posu[0])
            drawing.set_y(u, posu[1])
