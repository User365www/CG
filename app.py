from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='.')

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

# RGB-CMYK
def rgb_to_cmyk(r, g, b):
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    k = 1.0 - max(r_n, g_n, b_n)
    if k == 1.0:
        return 0.0, 0.0, 0.0, 100.0
    c = (1.0 - r_n - k) / (1.0 - k)
    m = (1.0 - g_n - k) / (1.0 - k)
    y = (1.0 - b_n - k) / (1.0 - k)
    return round(c * 100, 1), round(m * 100, 1), round(y * 100, 1), round(k * 100, 1)

def cmyk_to_rgb(c, m, y, k):
    c_n, m_n, y_n, k_n = c / 100.0, m / 100.0, y / 100.0, k / 100.0
    r = 255.0 * (1.0 - c_n) * (1.0 - k_n)
    g = 255.0 * (1.0 - m_n) * (1.0 - k_n)
    b = 255.0 * (1.0 - y_n) * (1.0 - k_n)
    return int(round(clamp(r, 0, 255))), int(round(clamp(g, 0, 255))), int(round(clamp(b, 0, 255)))

# RGB-HSV
def rgb_to_hsv(r, g, b):
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    c_max = max(r_n, g_n, b_n)
    c_min = min(r_n, g_n, b_n)
    delta = c_max - c_min

    if delta == 0:
        h = 0.0
    elif c_max == r_n:
        h = 60.0 * (((g_n - b_n) / delta) % 6)
    elif c_max == g_n:
        h = 60.0 * (((b_n - r_n) / delta) + 2)
    else:
        h = 60.0 * (((r_n - g_n) / delta) + 4)

    s = 0.0 if c_max == 0 else (delta / c_max)
    v = c_max
    return round(h, 1), round(s * 100, 1), round(v * 100, 1)

def hsv_to_rgb(h, s, v):
    h = h % 360
    s_n, v_n = s / 100.0, v / 100.0
    c = v_n * s_n
    x = c * (1.0 - abs(((h / 60.0) % 2) - 1.0))
    m = v_n - c

    if 0 <= h < 60:
        rp, gp, bp = c, x, 0
    elif 60 <= h < 120:
        rp, gp, bp = x, c, 0
    elif 120 <= h < 180:
        rp, gp, bp = 0, c, x
    elif 180 <= h < 240:
        rp, gp, bp = 0, x, c
    elif 240 <= h < 300:
        rp, gp, bp = x, 0, c
    else:
        rp, gp, bp = c, 0, x

    r = (rp + m) * 255.0
    g = (gp + m) * 255.0
    b = (bp + m) * 255.0
    return int(round(clamp(r, 0, 255))), int(round(clamp(g, 0, 255))), int(round(clamp(b, 0, 255)))

# Routs
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    req = request.get_json()
    model = req.get('model')
    vals = req.get('values', [])

    # 1. Приводим входящую модель к RGB
    if model == 'rgb':
        r, g, b = [int(clamp(float(v), 0, 255)) for v in vals]
    elif model == 'cmyk':
        c, m, y, k = [clamp(float(v), 0, 100) for v in vals]
        r, g, b = cmyk_to_rgb(c, m, y, k)
    elif model == 'hsv':
        h = clamp(float(vals[0]), 0, 360)
        s = clamp(float(vals[1]), 0, 100)
        v = clamp(float(vals[2]), 0, 100)
        r, g, b = hsv_to_rgb(h, s, v)
    else:
        r, g, b = 0, 0, 0

    # 2. Пересчитываем RGB в остальные модели
    c, m, y, k = rgb_to_cmyk(r, g, b)
    h, s, v = rgb_to_hsv(r, g, b)

    return jsonify({
        'rgb': [r, g, b],
        'cmyk': [c, m, y, k],
        'hsv': [h, s, v]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
