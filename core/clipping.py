INSIDE = 0
LEFT   = 1
RIGHT  = 2
BOTTOM = 4
TOP    = 8

from core import Vertice

def get_outcode(v, xmin, ymin, xmax, ymax):
    code = INSIDE

    if v.x < xmin:
        code |= LEFT
    elif v.x > xmax:
        code |= RIGHT

    if v.y < ymin:
        code |= BOTTOM
    elif v.y > ymax:
        code |= TOP

    return code


def cohen_sutherland_clip(v1, v2, xmin, ymin, xmax, ymax):

    code1 = get_outcode(v1, xmin, ymin, xmax, ymax)
    code2 = get_outcode(v2, xmin, ymin, xmax, ymax)

    while True:
        # Trivially accept
        if not (code1 | code2):
            return v1, v2

        # Trivially reject
        if code1 & code2:
            return None

        # Choose one endpoint outside
        code_out = code1 if code1 else code2

        if code_out & TOP:
            t = (ymax - v1.y) / (v2.y - v1.y)
            x = v1.x + t * (v2.x - v1.x)
            y = ymax

        elif code_out & BOTTOM:
            t = (ymin - v1.y) / (v2.y - v1.y)
            x = v1.x + t * (v2.x - v1.x)
            y = ymin

        elif code_out & RIGHT:
            t = (xmax - v1.x) / (v2.x - v1.x)
            y = v1.y + t * (v2.y - v1.y)
            x = xmax

        elif code_out & LEFT:
            t = (xmin - v1.x) / (v2.x - v1.x)
            y = v1.y + t * (v2.y - v1.y)
            x = xmin

        new_v = Vertice(x, y, 
                        v1.u if code_out == code1 else v2.u,
                        v1.v if code_out == code1 else v2.v)

        if code_out == code1:
            v1 = new_v
            code1 = get_outcode(v1, xmin, ymin, xmax, ymax)
        else:
            v2 = new_v
            code2 = get_outcode(v2, xmin, ymin, xmax, ymax)
