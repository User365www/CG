from pathlib import Path
from flask import Flask, render_template, request, jsonify
from .algorithms import step_line, dda_line, bresenham_line, bresenham_circle
from .timing import measure_algorithms

# Шаблоны лежат в корневой папке проекта: lab03/templates.
# Явный абсолютный путь не зависит от того, откуда запущен main.py.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "templates"
app = Flask(__name__, template_folder=str(TEMPLATE_DIR))

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/draw")
def draw():
    try:
        data = request.get_json(force=True)
        algorithm = data.get("algorithm")
        x0, y0 = int(data["x0"]), int(data["y0"])
        if algorithm == "circle":
            r = int(data["r"])
            points = bresenham_circle(x0, y0, r)
            ideal = {"type":"circle", "cx":x0, "cy":y0, "r":r}
        else:
            x1, y1 = int(data["x1"]), int(data["y1"])
            funcs = {
                "step": step_line,
                "dda": dda_line,
                "bresenham": bresenham_line,
            }
            if algorithm not in funcs:
                return jsonify(error="Неизвестный алгоритм."), 400
            points = funcs[algorithm](x0,y0,x1,y1)
            ideal = {"type":"line","x0":x0,"y0":y0,"x1":x1,"y1":y1}
        return jsonify(points=points, ideal=ideal, count=len(points))
    except (KeyError, TypeError, ValueError) as e:
        return jsonify(error=str(e) or "Проверьте введённые координаты."), 400

@app.get("/timing")
def timing():
    return jsonify(results=measure_algorithms(100))
