from math import floor, ceil, atan2

def round_pixel(v):
    return int(floor(v + 0.5)) if v >= 0 else int(ceil(v - 0.5))

def step_line(x0, y0, x1, y1):
    dx, dy = x1-x0, y1-y0
    if dx == 0 and dy == 0:
        return [(x0, y0)]
    pts = []
    if abs(dx) >= abs(dy):
        direction = 1 if dx > 0 else -1
        k = dy / dx
        for x in range(x0, x1 + direction, direction):
            pts.append((x, round_pixel(y0 + k*(x-x0))))
    else:
        direction = 1 if dy > 0 else -1
        k = dx / dy
        for y in range(y0, y1 + direction, direction):
            pts.append((round_pixel(x0 + k*(y-y0)), y))
    return pts

def dda_line(x0, y0, x1, y1):
    dx, dy = x1-x0, y1-y0
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x0, y0)]
    x, y = float(x0), float(y0)
    x_inc, y_inc = dx/steps, dy/steps
    pts = []
    for _ in range(steps+1):
        pts.append((round_pixel(x), round_pixel(y)))
        x += x_inc
        y += y_inc
    pts[-1] = (x1, y1)
    return pts

def bresenham_line(x0, y0, x1, y1):
    dx, sx = abs(x1-x0), 1 if x0 < x1 else -1
    dy, sy = -abs(y1-y0), 1 if y0 < y1 else -1
    err = dx + dy
    x, y, pts = x0, y0, []
    while True:
        pts.append((x,y))
        if x == x1 and y == y1:
            break
        e2 = 2*err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    return pts

def bresenham_circle(cx, cy, r):
    if r < 0:
        raise ValueError("Радиус не может быть отрицательным.")
    if r == 0:
        return [(cx,cy)]
    x, y = 0, r
    d = 3 - 2*r
    pts = set()
    while x <= y:
        pts.update({
            (cx+x,cy+y),(cx-x,cy+y),(cx+x,cy-y),(cx-x,cy-y),
            (cx+y,cy+x),(cx-y,cy+x),(cx+y,cy-x),(cx-y,cy-x)
        })
        if d < 0:
            d += 4*x + 6
        else:
            d += 4*(x-y) + 10
            y -= 1
        x += 1
    return sorted(pts, key=lambda p: atan2(p[1]-cy,p[0]-cx))
