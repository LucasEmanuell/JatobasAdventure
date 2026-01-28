import math 
from core import Vertice

def pseudo_rand(seed, a=12.9898, b=78.233):
    return abs(math.sin(seed * a) * b) % 1.0


def draw_line(renderer, v0: Vertice, v1: Vertice, color):
    x1, y1 = int(v0.x), int(v0.y)
    x2, y2 = int(v1.x), int(v1.y)
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        renderer.put_pixel(x1, y1, color)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def draw_ellipse(renderer, center: Vertice, rx, ry, color):
    xc, yc = int(center.x), int(center.y)
    rx, ry = int(rx), int(ry)

    x, y = 0, ry
    d1 = (ry**2) - (rx**2 * ry) + (0.25 * rx**2)
    dx = 2 * ry**2 * x
    dy = 2 * rx**2 * y

    while dx < dy:
        renderer.put_pixel(xc + x, yc + y, color)
        renderer.put_pixel(xc - x, yc + y, color)
        renderer.put_pixel(xc + x, yc - y, color)
        renderer.put_pixel(xc - x, yc - y, color)

        if d1 < 0:
            x += 1
            dx += 2 * ry**2
            d1 += dx + ry**2
        else:
            x += 1
            y -= 1
            dx += 2 * ry**2
            dy -= 2 * rx**2
            d1 += dx - dy + ry**2

    d2 = ((ry**2) * ((x + 0.5)**2)) + ((rx**2) * ((y - 1)**2)) - (rx**2 * ry**2)

    while y >= 0:
        renderer.put_pixel(xc + x, yc + y, color)
        renderer.put_pixel(xc - x, yc + y, color)
        renderer.put_pixel(xc + x, yc - y, color)
        renderer.put_pixel(xc - x, yc - y, color)

        if d2 > 0:
            y -= 1
            dy -= 2 * rx**2
            d2 += rx**2 - dy
        else:
            y -= 1
            x += 1
            dx += 2 * ry**2
            dy -= 2 * rx**2
            d2 += dx - dy + rx**2


def flood_fill(renderer, seed: Vertice, fill_color):
    x, y = int(seed.x), int(seed.y)

    if x < 0 or x >= renderer.width or y < 0 or y >= renderer.height:
        return

    target_color = renderer.get_pixel(x, y)
    fill_color = tuple(fill_color)

    if target_color == fill_color:
        return

    stack = [(x, y)]

    while stack:
        cx, cy = stack.pop()

        if 0 <= cx < renderer.width and 0 <= cy < renderer.height:
            if renderer.get_pixel(cx, cy) == target_color:
                renderer.put_pixel(cx, cy, fill_color)
                stack.append((cx + 1, cy))
                stack.append((cx - 1, cy))
                stack.append((cx, cy + 1))
                stack.append((cx, cy - 1))
