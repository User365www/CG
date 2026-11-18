from time import perf_counter
from .algorithms import step_line, dda_line, bresenham_line, bresenham_circle

def measure_algorithms(repeats=100):
    cases = [
        ("Пошаговый алгоритм", lambda: step_line(0,0,1000,600)),
        ("ЦДА (DDA)", lambda: dda_line(0,0,1000,600)),
        ("Брезенхем (отрезок)", lambda: bresenham_line(0,0,1000,600)),
        ("Брезенхем (окружность)", lambda: bresenham_circle(0,0,500)),
    ]
    result = []
    for name, fn in cases:
        points = fn()
        start = perf_counter()
        for _ in range(repeats):
            fn()
        avg_us = (perf_counter()-start)*1_000_000/repeats
        result.append({"name":name, "points":len(points), "microseconds":round(avg_us,2)})
    return result
