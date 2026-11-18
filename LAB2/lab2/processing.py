"""Алгоритмы лабораторной работы №2, вариант 10."""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image


def otsu_threshold(pixels):
    """Подбирает порог по максимуму межклассовой дисперсии."""
    hist = np.bincount(pixels.ravel(), minlength=256)
    total = pixels.size
    total_sum = sum(i * int(hist[i]) for i in range(256))
    count_dark = 0
    sum_dark = 0
    best_score = -1
    best_t = 0

    for t in range(256):
        count_dark += int(hist[t])
        sum_dark += t * int(hist[t])
        count_light = total - count_dark
        if count_dark == 0 or count_light == 0:
            continue
        mean_dark = sum_dark / count_dark
        mean_light = (total_sum - sum_dark) / count_light
        score = count_dark * count_light * (mean_dark - mean_light) ** 2
        if score > best_score:
            best_score = score
            best_t = t
    return best_t


def iterative_threshold(pixels):
    """Находит порог последовательным уточнением средних двух групп."""
    t = float(pixels.mean())
    for _ in range(100):
        dark = pixels[pixels <= t]
        light = pixels[pixels > t]
        if len(dark) == 0 or len(light) == 0:
            break
        new_t = (float(dark.mean()) + float(light.mean())) / 2
        if abs(new_t - t) < 0.5:
            t = new_t
            break
        t = new_t
    return int(round(t))


def binary_image(pixels, threshold):
    return Image.fromarray(np.where(pixels > threshold, 255, 0).astype(np.uint8))


def order_filters(pixels, size=3):
    """Нелинейные фильтры по окрестности size x size."""
    padded = np.pad(pixels, size // 2, mode="edge")
    windows = sliding_window_view(padded, (size, size))
    return {
        "Медианный фильтр": Image.fromarray(
            np.median(windows, axis=(-2, -1)).astype(np.uint8)
        ),
        "Фильтр минимума": Image.fromarray(windows.min(axis=(-2, -1))),
        "Фильтр максимума": Image.fromarray(windows.max(axis=(-2, -1))),
    }
