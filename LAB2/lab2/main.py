"""Простое веб-приложение для лабораторной работы №2 (вариант 10)."""
import base64
from io import BytesIO
from pathlib import Path

import numpy as np
from flask import Flask, render_template, request
from PIL import Image, ImageOps, UnidentifiedImageError

from processing import binary_image, iterative_threshold, order_filters, otsu_threshold

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
FOLDER = Path(__file__).resolve().parent
SAMPLES = sorted(p.name for p in (FOLDER / "images").glob("*.png"))


def to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    error = ""
    sample = request.form.get("sample", SAMPLES[0] if SAMPLES else "")
    size = int(request.form.get("size", 3)) if request.form.get("size", "3") in ("3", "5") else 3

    if request.method == "POST":
        try:
            uploaded = request.files.get("image")
            if uploaded and uploaded.filename:
                image = Image.open(uploaded.stream)
            elif sample in SAMPLES:
                image = Image.open(FOLDER / "images" / sample)
            else:
                raise ValueError("Выберите изображение")

            image = ImageOps.exif_transpose(image).convert("L")
            # Ограничение размера ради быстрой обработки в браузере.
            image.thumbnail((1000, 1000))
            pixels = np.array(image)
            results = [("Исходное изображение", to_base64(image))]

            if request.form.get("mode") == "filters":
                for name, filtered in order_filters(pixels, size).items():
                    results.append((name, to_base64(filtered)))
            else:
                t_otsu = otsu_threshold(pixels)
                t_iter = iterative_threshold(pixels)
                results += [
                    (f"Метод Отсу (порог {t_otsu})", to_base64(binary_image(pixels, t_otsu))),
                    (f"Итеративный метод (порог {t_iter})", to_base64(binary_image(pixels, t_iter))),
                ]
        except (UnidentifiedImageError, OSError, ValueError):
            error = "Не удалось открыть изображение. Выберите JPG или PNG."

    return render_template("index.html", samples=SAMPLES, sample=sample,
                           results=results, error=error, size=size)


if __name__ == "__main__":
    app.run(debug=True)
