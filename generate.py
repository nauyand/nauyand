#!/usr/bin/env python3
"""
README profil GitHub yang "dibangun live" oleh ratusan kursor AI
(Claude, ChatGPT, Gemini, Grok, Copilot, ...).

Cara pakai
  1. Ubah bagian KONFIGURASI di bawah (nama, peran, skill, proyek, kontak).
  2. Jalankan:   python3 generate.py
  3. Upload README.md + folder assets/ ke repo yang namanya SAMA dengan
     username GitHub kamu (contoh: github.com/budi/budi).

Tanpa dependensi, cukup Python 3.8+.

Kenapa SVG? README GitHub tidak menjalankan JavaScript, tapi file SVG yang
ditampilkan sebagai gambar tetap boleh punya animasi (SMIL). Jadi tiap bagian
README = satu SVG yang "merakit dirinya sendiri" saat dibuka.
"""
import base64
import colorsys
import hashlib
import html
import json
import math
import os
import random

# ═══════════════════════════ KONFIGURASI: UBAH DI SINI ═══════════════════════════
PROFILE = {
    "github_user": "nauyand",
    "greeting": "// halo, perkenalkan saya",
    "name": "YUAN ANDRATA",
    "tagline": "IoT Engineer · Mobile Developer · Prompt Engineer",
    "about_comment": "// kenalan dulu, yuk!",
    "about": [  # (kunci, nilai): nilai boleh string atau list
        ("nama", "Yuan Andrata"),
        ("peran", ["IoT Engineer", "Mobile Dev"]),
        ("lokasi", "Cimahi, Jawa Barat"),
        ("status", "Fokus bekerja"),
        ("fokus", ["IoT", "Embedded", "Android"]),
        ("hobi", "Bikin alat yang bisa ngobrol"),
    ],
    "skills_comment": "// tech stack andalan (dari proyek-proyek saya)",
    "skills": ["C/C++", "Python", "Kotlin", "JavaScript", "HTML/CSS", "Arduino",
               "ESP8266", "ESP32", "Raspberry Pi", "PlatformIO", "MQTT", "Mosquitto",
               "Modbus TCP", "RabbitMQ", "OpenCV", "Android Studio", "Linux VPS",
               "Teltonika FMB125", "Prompt Engineering"],
    "projects_comment": "// proyek pilihan",
    "projects": [  # "url" kosong = tanpa link (dan tanpa awalan nauyand/)
        {"name": "SMARTMT-V3.0", "url": "https://github.com/nauyand/SMARTMT-V3.0",
         "desc": "Sistem pintar mobil tangki BBM: suhu & tekanan ban, 12 sensor jarak, kontrol penseal, plus aplikasi Android & desktop teknisi.",
         "tags": ["Arduino Mega", "ESP8266", "Kotlin"]},
        {"name": "GPS-MQTT-VPS-MOBILEAPPS", "url": "https://github.com/nauyand/GPS-MQTT-VPS-MOBILEAPPS",
         "desc": "GPS + TPMS dari Teltonika FMB125 diteruskan server Python di VPS ke MQTT, dipantau lewat aplikasi Android.",
         "tags": ["Python", "MQTT", "Kotlin"]},
        {"name": "iot-data-dashboard", "url": "",
         "desc": "Dashboard web real-time untuk memantau dan mengontrol data sensor dari perangkat apa pun.",
         "tags": ["ESP32", "Web"]},
        {"name": "modbus-tcp", "url": "",
         "desc": "Server Modbus TCP di ESP8266 dan Arduino untuk berkomunikasi dengan perangkat industri.",
         "tags": ["Modbus TCP", "ESP8266"]},
    ],
    "contact": {  # kosongkan ("") yang tidak dipakai
        "instagram": "https://www.instagram.com/yuan.and/",
        "facebook": "https://www.facebook.com/yuanandrata",
        "email": "yuanandrata@gmail.com",
        "whatsapp": "https://wa.me/6281220947936",
        "linkedin": "",
        "website": "",
    },
}

# Animasi
LOOP = False        # True = bangun -> tahan LOOP_HOLD detik -> diulang terus
LOOP_HOLD = 14      # detik hasil jadi ditahan sebelum diulang (kalau LOOP=True)
# README GitHub tidak bisa mendeteksi scroll, jadi tiap bagian mulai dibangun
# X detik setelah halaman dibuka: urutannya dari atas ke bawah, kira-kira
# mengikuti kecepatan orang membaca sambil scroll.
SECTION_DELAY = {"hero": 0.0, "about": 2.5, "skills": 5.0, "projects": 7.0, "footer": 11.0}
SEED = 7            # ganti angka ini untuk susunan gerakan kursor yang berbeda

# Versi web (GitHub Pages) yang BENAR-BENAR dibangun ulang tiap bagian di-scroll.
# Kosongkan ("") kalau tidak dipakai; link ini muncul di README.
SITE_URL = "https://nauyand.github.io/nauyand/"

# (nama label, warna kursor, warna teks label)
AGENTS = [
    ("Claude", "#D97757", "#ffffff"),
    ("ChatGPT", "#10A37F", "#ffffff"),
    ("Gemini", "#4C8DF6", "#ffffff"),
    ("Grok", "#E7E9EA", "#0d1117"),
    ("Copilot", "#A371F7", "#ffffff"),
    ("Llama", "#1877F2", "#ffffff"),
    ("Mistral", "#FF7000", "#ffffff"),
    ("DeepSeek", "#4D6BFE", "#ffffff"),
    ("Perplexity", "#20B8CD", "#0d1117"),
    ("Qwen", "#7C6CF2", "#ffffff"),
    ("Kimi", "#F7C843", "#0d1117"),
    ("Devin", "#2EA043", "#ffffff"),
]
# ══════════════════════════════════════════════════════════════════════════════════

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
_DELAYS = dict(SECTION_DELAY)

W = 900
TOP = 40
FADE = 0.8
C = dict(bg="#0d1117", panel="#161b22", border="#30363d", dot="#262c36", muted="#8b949e",
         text="#e6edf3", kw="#ff7b72", fn="#d2a8ff", key="#79c0ff", str="#a5d6ff",
         green="#7ee787", orange="#ffa657", yellow="#f2cc60")
GRAD = ["#7ee787", "#79c0ff", "#d2a8ff"]
CHIP_COLORS = ["#79c0ff", "#7ee787", "#d2a8ff", "#ffa657", "#ff7b72", "#f2cc60", "#56d4dd", "#ff9bce"]
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
CWR = 0.6  # perkiraan lebar 1 karakter monospace = 0.6 x ukuran font
CURSOR = "M0 0V17.2L4.7 12.9L7.7 19.7L10.6 18.5L7.6 11.8H13.4Z"

EASE_MOVE = ".42 0 .2 1"
EASE_OUT = ".2 .6 .35 1"
POP = ".3 0 .3 1"
LIN = "0 0 1 1"

FONT = {  # font piksel 5x7 (lebar boleh berbeda)
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#", "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.", "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####", "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.###.", "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": "###|.#.|.#.|.#.|.#.|.#.|###", "J": "..###|...#.|...#.|...#.|...#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#", "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#", "N": "#...#|#...#|##..#|#.#.#|#..##|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.", "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#", "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.", "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.", "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|#.#.#|.#.#.", "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..", "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.", "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####", "3": "#####|...#.|..#..|...#.|....#|#...#|.###.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.", "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.", "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.", "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    " ": "...|...|...|...|...|...|...", ".": "..|..|..|..|..|##|##", ",": "..|..|..|..|##|.#|#.",
    "!": "#|#|#|#|#|.|#", "?": ".###.|#...#|....#|...#.|..#..|.....|..#..", "-": "....|....|....|####|....|....|....",
    "'": "#|#|.|.|.|.|.", "&": ".##..|#..#.|#.#..|.#...|#.#.#|#..#.|.##.#", "_": ".....|.....|.....|.....|.....|.....|#####",
}


# ───────────────────────────── utilitas ─────────────────────────────
def num(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def esc(s):
    return html.escape(str(s), quote=True)


def clamp(v, a, b):
    return max(a, min(b, v))


def lerp_color(stops, t):
    t = clamp(t, 0, 1) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    f = t - i
    a, b = stops[i], stops[i + 1]
    ca = [int(a[k:k + 2], 16) for k in (1, 3, 5)]
    cb = [int(b[k:k + 2], 16) for k in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * f):02x}" for x, y in zip(ca, cb))


def kt(pts, T, eases=None):
    """Titik-titik (waktu_absolut, nilai) -> atribut values/keyTimes(/keySplines) SMIL."""
    pts = [(clamp(t, 0, T), v) for t, v in pts]
    eases = list(eases) if eases else [LIN] * (len(pts) - 1)
    if pts[0][0] > 0:
        pts.insert(0, (0.0, pts[0][1]))
        eases.insert(0, LIN)
    if pts[-1][0] < T:
        pts.append((T, pts[-1][1]))
        eases.append(LIN)
    ks, last = [], 0.0
    for t, _ in pts:
        k = max(last, round(t / T, 4))
        ks.append(k)
        last = k
    ks[0], ks[-1] = 0.0, 1.0
    s = f'values="{";".join(v for _, v in pts)}" keyTimes="{";".join(num4(k) for k in ks)}"'
    if any(e != LIN for e in eases):
        s += f' calcMode="spline" keySplines="{";".join(eases)}"'
    return s


def num4(k):
    s = f"{k:.4f}".rstrip("0").rstrip(".")
    return s or "0"


def rep():
    return 'repeatCount="indefinite"' if LOOP else 'fill="freeze"'


def A(attr, pts, T, eases=None, tag="animate", typ=None):
    t = f' type="{typ}"' if typ else ""
    return f'<{tag} attributeName="{attr}"{t} {kt(pts, T, eases)} dur="{num(T)}s" {rep()}/>'


def loopfade(T, hi="1"):
    return [(T - FADE, hi), (T, "0")] if LOOP else []


def window(T, t_on, t_off=None, eps=0.02):
    pts = [(t_on, "0"), (t_on + eps, "1")]
    if t_off is None:
        pts += loopfade(T)
    else:
        pts += [(t_off, "1"), (t_off + eps, "0")]
    return pts


_recent = []


def pick_agent():
    keep = min(3, len(AGENTS) - 1)
    while True:
        i = random.randrange(len(AGENTS))
        if keep == 0 or i not in _recent[-keep:]:
            break
    _recent.append(i)
    return i


# ───────────────────────────── scene ─────────────────────────────
class Scene:
    def __init__(self, key, h, label):
        self.key, self.h, self.label = key, h, label
        self.delay = _DELAYS.get(key, 0.0)
        self.layers = {"bg": [], "pieces": [], "chrome": [], "cursors": []}
        self.drops, self.agent_ids = [], set()
        self.cursors, self.end = 0, self.delay

    def add(self, layer, item):
        self.layers[layer].append(item)

    def register(self, ai, t_drop, t_end):
        self.drops.append(t_drop)
        self.agent_ids.add(ai)
        self.cursors += 1
        self.end = max(self.end, t_end)

    @property
    def T(self):
        return self.end + 0.3 + ((LOOP_HOLD + FADE) if LOOP else 0)

    def render(self):
        T, H = self.T, self.h
        defs = [
            "<style>.m{font-family:" + MONO + "}.b{font-weight:700}</style>",
            f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="12"/></clipPath>',
            f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="11" cy="11" r="1.1" fill="{C["dot"]}"/></pattern>',
            f'<linearGradient id="prog" gradientUnits="userSpaceOnUse" x1="0" x2="{W}" y1="0" y2="0">'
            + "".join(f'<stop offset="{i / (len(GRAD) - 1)}" stop-color="{c}"/>' for i, c in enumerate(GRAD))
            + "</linearGradient>",
        ]
        for i in sorted(self.agent_ids):
            name, col, fg = AGENTS[i]
            lw = len(name) * 6.5 + 12
            defs.append(
                f'<g id="a{i}"><path d="{CURSOR}" fill="{col}" stroke="#fff" stroke-width="1.2" stroke-linejoin="round"/>'
                f'<rect x="12" y="17" width="{num(lw)}" height="17" rx="5" fill="{col}"/>'
                f'<text x="18" y="29" font-size="10.5" font-weight="600" fill="{fg}">{esc(name)}</text></g>')
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
               f'font-family="{SANS}" role="img">',
               f"<title>{esc(self.label)}</title>",
               "<defs>" + "".join(defs) + "</defs>",
               '<g clip-path="url(#clip)">',
               f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>',
               f'<rect y="{TOP}" width="{W}" height="{H - TOP}" fill="url(#dots)"/>']
        for layer in ("bg", "pieces", "chrome", "cursors"):
            for item in self.layers[layer]:
                out.append(item(T) if callable(item) else item)
        out.append("</g>")
        out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{C["border"]}"/>')
        out.append("</svg>")
        return "\n".join(out)


def start_point(sc, cx, cy):
    m = 45
    if random.random() < 0.45:
        x = clamp(cx + random.gauss(0, W * 0.3), -m, W + m)
        y = -m if random.random() < 0.5 else sc.h + m
    else:
        y = clamp(cy + random.gauss(0, sc.h * 0.4), -m, sc.h + m)
        x = -m - 30 if random.random() < (1 - cx / W) else W + m
    return x, y


def selection(w, h, col, t0, t_drop, T):
    x, y, ww, hh = -w / 2 - 5, -h / 2 - 4, w + 10, h + 8
    handles = "".join(
        f'<rect x="{num(px - 2.5)}" y="{num(py - 2.5)}" width="5" height="5" fill="#fff" stroke="{col}"/>'
        for px, py in ((x, y), (x + ww, y), (x, y + hh), (x + ww, y + hh)))
    op = A("opacity", [(t0, "0"), (t0 + .1, "1"), (t_drop + .2, "1"), (t_drop + .6, "0")], T)
    return (f'<g opacity="0">{op}<rect x="{num(x)}" y="{num(y)}" width="{num(ww)}" height="{num(hh)}" '
            f'fill="none" stroke="{col}" stroke-width="1.5"/>{handles}</g>')


def drag(sc, content, w, h, cx, cy, t_drop, select=True, agent=None):
    """Satu kursor AI menyeret satu potongan dari luar kanvas ke posisinya."""
    ai = pick_agent() if agent is None else agent
    _, col, _ = AGENTS[ai]
    sx, sy = start_point(sc, cx, cy)
    travel = clamp(0.35 + math.hypot(cx - sx, cy - sy) / 700, 0.55, 1.5)
    t0 = max(sc.delay + 0.05, t_drop - travel)
    t_drop = max(t_drop, t0 + 0.4)
    ox, oy = w / 2 - min(6, w / 4), h / 2 - min(4, h / 4)
    a, r = random.uniform(0, 2 * math.pi), random.uniform(70, 150)
    ex, ey = cx + ox + math.cos(a) * r, cy + oy + math.sin(a) * r
    t_p = t_drop + random.uniform(0.08, 0.2)
    t_x = t_p + random.uniform(0.45, 0.7)
    sc.register(ai, t_drop, t_x)

    def piece(T):
        body = content(T, col, t_drop) if callable(content) else content
        tr = A("transform", [(t0, f"{num(sx)} {num(sy)}"), (t_drop, f"{num(cx)} {num(cy)}")], T,
               [EASE_MOVE], "animateTransform", "translate")
        op = A("opacity", [(t0, "0"), (t0 + .08, ".92"), (t_drop, ".92"), (t_drop + .12, "1")] + loopfade(T), T)
        sca = A("transform", [(t0, "1.07"), (t_drop, "1.07"), (t_drop + .09, ".93"), (t_drop + .26, "1")], T,
                [LIN, POP, POP], "animateTransform", "scale")
        sel = selection(w, h, col, t0, t_drop, T) if select else ""
        return (f'<g opacity="0" transform="translate({num(sx)} {num(sy)})">{tr}{op}'
                f"<g>{sca}{body}</g>{sel}</g>")

    def cursor(T):
        tr = A("transform", [(t0, f"{num(sx + ox)} {num(sy + oy)}"), (t_drop, f"{num(cx + ox)} {num(cy + oy)}"),
                             (t_p, f"{num(cx + ox)} {num(cy + oy)}"), (t_x, f"{num(ex)} {num(ey)}")], T,
               [EASE_MOVE, LIN, EASE_OUT], "animateTransform", "translate")
        op = A("opacity", [(t0, "0"), (t0 + .1, "1"), (t_x - .3, "1"), (t_x, "0")], T)
        return f'<g opacity="0">{tr}{op}<use href="#a{ai}"/></g>'

    sc.add("pieces", piece)
    sc.add("cursors", cursor)


def word(text, fs, color, bold=False, italic=False):
    cls = "m b" if bold else "m"
    st = ' font-style="italic"' if italic else ""
    return (f'<text class="{cls}" text-anchor="middle" y="{num(fs * .35)}" font-size="{num(fs)}" '
            f'fill="{color}"{st}>{esc(text)}</text>')


def block(size, final):
    rx = size * 0.22

    def f(T, carry, t_drop):
        return (f'<rect x="{num(-size / 2)}" y="{num(-size / 2)}" width="{num(size)}" height="{num(size)}" '
                f'rx="{num(rx)}" fill="{final}">{A("fill", [(t_drop, carry), (t_drop + .35, final)], T)}</rect>')
    return f


def chip(text, fs, w, h, col, dot=True):
    dot_svg = f'<circle cx="{num(-w / 2 + 16)}" cy="0" r="4" fill="{col}"/>' if dot else ""
    tx = -w / 2 + (28 if dot else 9)
    return (f'<rect x="{num(-w / 2)}" y="{num(-h / 2)}" width="{num(w)}" height="{num(h)}" rx="{num(h / 2)}" '
            f'fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".55"/>{dot_svg}'
            f'<text class="m" x="{num(tx)}" y="{num(fs * .35)}" font-size="{num(fs)}" fill="{C["text"]}">{esc(text)}</text>')


def tokens_line(text, x_left, y, fs):
    cw, out, col = fs * CWR, [], 0
    for wd in text.split(" "):
        if wd:
            w = len(wd) * cw
            out.append((wd, x_left + col * cw + w / 2, y, w, fs * 1.3))
        col += len(wd) + 1
    return out


def chrome(sc, label):
    """Bilah atas ala jendela editor + avatar kolaborator + progress bar."""
    s = [f'<rect width="{W}" height="{TOP}" fill="{C["panel"]}"/>',
         f'<line x1="0" y1="{TOP - .5}" x2="{W}" y2="{TOP - .5}" stroke="{C["border"]}"/>']
    for k, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        s.append(f'<circle cx="{22 + k * 18}" cy="{TOP / 2}" r="5.5" fill="{col}"/>')
    s.append(f'<text class="m" x="{W / 2}" y="{TOP / 2 + 4}" text-anchor="middle" font-size="12" '
             f'fill="{C["muted"]}">{esc(label)}</text>')
    sc.add("chrome", "".join(s))

    def right(T):
        txt = f"{sc.cursors} kursor AI"
        x = W - 18
        parts = [f'<text class="m" x="{x}" y="{TOP / 2 + 4}" text-anchor="end" font-size="11.5" '
                 f'fill="{C["muted"]}">{txt}</text>']
        cx = x - len(txt) * 6.9 - 16
        for i in list(sorted(sc.agent_ids))[:6][::-1]:
            parts.append(f'<circle cx="{num(cx)}" cy="{TOP / 2}" r="8" fill="{AGENTS[i][1]}" '
                         f'stroke="{C["panel"]}" stroke-width="2"/>')
            cx -= 11
        drops = sorted(sc.drops)
        n = len(drops)
        pts = [(sc.delay, "0")]
        for q in range(1, 11):
            pts.append((drops[max(0, math.ceil(q / 10 * n) - 1)], num(W * q / 10)))
        pts += loopfade(T, num(W))
        parts.append(f'<rect y="{TOP - 2}" height="2" width="0" fill="url(#prog)">{A("width", pts, T)}</rect>')
        return "".join(parts)
    sc.add("chrome", right)


def status(sc, y):
    """Teks status di bawah: menunggu -> membangun k/n -> selesai."""
    def f(T):
        drops = sorted(sc.drops)
        n = len(drops)
        x, fs, parts = 24, 12.5, []

        def line(content, pts):
            parts.append(f'<text class="m" x="{x}" y="{num(y)}" font-size="{fs}" fill="{C["muted"]}" '
                         f'opacity="0">{A("opacity", pts, T)}{content}</text>')
        if sc.delay > 0.05:
            line(f'<tspan fill="{C["muted"]}">○</tspan> menunggu giliran…', window(T, 0, sc.delay))
        steps = 12
        taus = [sc.delay] + [drops[max(0, math.ceil(q / steps * n) - 1)] for q in range(1, steps)] + [drops[-1]]
        for q in range(steps):
            if taus[q + 1] - taus[q] < 0.05:
                continue
            k = 0 if q == 0 else math.ceil(q / steps * n)
            line(f'<tspan fill="{C["yellow"]}">●</tspan> membangun… {k}/{n} potongan',
                 window(T, taus[q], taus[q + 1]))
        line(f'<tspan fill="{C["green"]}">✓</tspan> selesai · {n} potongan dipasang oleh '
             f'{len(sc.agent_ids)} model AI', window(T, drops[-1] + 0.1))
        return "".join(parts)
    sc.add("chrome", f)


# ───────────────────────────── bagian-bagian README ─────────────────────────────
def build_hero(P):
    name = " ".join(P["name"].upper().split())
    name = "".join(ch if ch in FONT else "?" for ch in name)
    gw = lambda ch: len(FONT[ch].split("|")[0])
    bw = lambda txt: sum(gw(c) for c in txt) + max(0, len(txt) - 1)
    avail = W - 100
    lines = [name]
    p = min(14.0, avail / bw(name))
    words = name.split(" ")
    if p < 9 and len(words) > 1:
        best = min(([" ".join(words[:i]), " ".join(words[i:])] for i in range(1, len(words))),
                   key=lambda ls: max(bw(l) for l in ls))
        lines = best
        p = min(14.0, avail / max(bw(l) for l in lines))
    p = max(p, 4.0)
    bs = p * 0.84

    greet_y = TOP + 40
    name_top = greet_y + 28
    name_h = 7 * p * len(lines) + (len(lines) - 1) * p * 2.2
    tag_fs = min(17.0, (W - 80) / (len(P["tagline"]) * CWR))
    tag_y = name_top + name_h + 40
    status_y = tag_y + 52
    sc = Scene("hero", int(status_y + 20), f"{P['name']} — {P['tagline']}")
    chrome(sc, "README.md — sedang diedit live")
    d = sc.delay

    # sapaan
    g_fs = 16
    g_left = (W - len(P["greeting"]) * g_fs * CWR) / 2
    for i, (wd, cx, cy, w, h) in enumerate(tokens_line(P["greeting"], g_left, greet_y, g_fs)):
        drag(sc, word(wd, g_fs, C["muted"]), w, h, cx, cy, d + 0.75 + i * 0.2)

    # nama: tiap piksel diantar satu kursor
    cells = []
    for li, ln in enumerate(lines):
        lw = bw(ln) * p
        x = (W - lw) / 2
        top = name_top + li * p * 9.2
        for ch in ln:
            rows = FONT[ch].split("|")
            for r, row in enumerate(rows):
                for c, v in enumerate(row):
                    if v == "#":
                        cells.append((x + c * p + p / 2, top + r * p + p / 2))
            x += (gw(ch) + 1) * p
    n = len(cells)
    span = clamp(n * 0.024, 2.4, 4.6)
    order = sorted(range(n), key=lambda i: cells[i][0] + random.gauss(0, 70))
    t_blocks_end = d
    for rank, i in enumerate(order):
        cx, cy = cells[i]
        t = d + 1.1 + rank / max(1, n - 1) * span + random.uniform(-0.15, 0.15)
        t_blocks_end = max(t_blocks_end, t)
        drag(sc, block(bs, lerp_color(GRAD, cx / W)), bs, bs, cx, cy, t, select=False)

    # tagline
    t_left = (W - len(P["tagline"]) * tag_fs * CWR) / 2
    for i, (wd, cx, cy, w, h) in enumerate(tokens_line(P["tagline"], t_left, tag_y, tag_fs)):
        col = C["muted"] if wd in ("·", "|", "/", "-", "•") else C["text"]
        drag(sc, word(wd, tag_fs, col), w, h, cx, cy, t_blocks_end - 0.5 + i * 0.16)
    status(sc, status_y)
    return sc


class CodeLine:
    def __init__(self, indent=0):
        self.col, self.toks = indent, []

    def add(self, text, color, gap=0, italic=False):
        self.col += gap
        for j, wd in enumerate(text.split(" ")):
            if j:
                self.col += 1
            if wd:
                self.toks.append((wd, color, self.col, italic))
                self.col += len(wd)
        return self


def identicon(user):
    h = hashlib.md5(user.encode()).digest()
    grid = [[False] * 5 for _ in range(5)]
    for c in range(3):
        for r in range(5):
            grid[r][c] = grid[r][4 - c] = h[c * 5 + r] % 2 == 0
    hue = (h[15] * 256 + h[14]) / 65535
    r_, g_, b_ = colorsys.hls_to_rgb(hue, 0.62, 0.6)
    return grid, "#{:02x}{:02x}{:02x}".format(int(r_ * 255), int(g_ * 255), int(b_ * 255))


def build_about(P):
    keyw = max(len(k) for k, _ in P["about"])
    lines = [CodeLine().add(P["about_comment"], C["muted"], italic=True),
             CodeLine().add("const", C["kw"]).add("tentangSaya", C["fn"], 1).add("=", C["text"], 1).add("{", C["text"], 1)]
    for k, v in P["about"]:
        ln = CodeLine(2).add(k + ":", C["key"])
        ln.col = 2 + keyw + 2
        if isinstance(v, (list, tuple)):
            ln.add("[" + ", ".join(f'"{x}"' for x in v) + "]", C["str"])
        else:
            ln.add(f'"{v}"', C["str"])
        ln.add(",", C["text"])
        lines.append(ln)
    lines.append(CodeLine().add("};", C["text"]))

    x0, right_w = 76, 230
    maxcol = max(l.col for l in lines)
    fs = min(16.0, (W - x0 - right_w) / (maxcol * CWR))
    cw, lh = fs * CWR, fs * 1.9
    y0 = TOP + 38
    status_y = y0 + len(lines) * lh + 18
    sc = Scene("about", int(status_y + 20), "Tentang saya")
    chrome(sc, "tentang-saya.ts")
    d = sc.delay

    gutter = "".join(f'<text class="m" x="{x0 - 22}" y="{num(y0 + i * lh + fs * .35)}" text-anchor="end" '
                     f'font-size="{num(fs - 2)}" fill="{C["muted"]}" opacity=".45">{i + 1}</text>'
                     for i in range(len(lines)))
    sc.add("bg", gutter + f'<line x1="{x0 - 12}" y1="{TOP}" x2="{x0 - 12}" y2="{sc.h}" stroke="{C["border"]}" opacity=".6"/>')

    t, idx = d + 0.9, 0
    for li, ln in enumerate(lines):
        cy = y0 + li * lh
        for wd, col, c0, it in ln.toks:
            w = len(wd) * cw
            drag(sc, word(wd, fs, col, italic=it), w, fs * 1.3, x0 + c0 * cw + w / 2, cy,
                 t + idx * 0.085 + random.uniform(-.05, .05))
            idx += 1

    # identicon ala GitHub, dirakit kotak demi kotak
    grid, icol = identicon(P["github_user"])
    cell, gap = 24, 4
    size = 5 * cell + 4 * gap
    icx = W - right_w / 2 - 10
    top = y0 - 8 + (len(lines) * lh - size - 40) / 2
    left = icx - size / 2
    sc.add("bg", f'<rect x="{num(left - 14)}" y="{num(top - 14)}" width="{size + 28}" height="{size + 28}" rx="10" '
                 f'fill="none" stroke="{C["border"]}" stroke-dasharray="5 5"/>')
    cells = [(r, c) for r in range(5) for c in range(5) if grid[r][c]]
    random.shuffle(cells)
    for k, (r, c) in enumerate(cells):
        drag(sc, block(cell, icol), cell, cell, left + c * (cell + gap) + cell / 2,
             top + r * (cell + gap) + cell / 2, d + 1.2 + k * 0.17, select=False)
    handle = "@" + P["github_user"]
    drag(sc, word(handle, 13, C["muted"]), len(handle) * 7.8, 17, icx, top + size + 34,
         d + 1.4 + len(cells) * 0.17)
    status(sc, status_y)
    return sc


def flow(items, avail, gap):
    rows, cur, cw = [], [], 0
    for it in items:
        w = it[1]
        if cur and cw + gap + w > avail:
            rows.append(cur)
            cur, cw = [], 0
        cw += (gap if cur else 0) + w
        cur.append(it)
    if cur:
        rows.append(cur)
    return rows


def build_skills(P):
    fs, ch, gap, rgap = 14, 34, 12, 14
    items = [(s, 30 + len(s) * fs * CWR + 16, CHIP_COLORS[i % len(CHIP_COLORS)]) for i, s in enumerate(P["skills"])]
    rows = flow(items, W - 80, gap)
    y_c = TOP + 34
    y_rows = y_c + 44
    status_y = y_rows + len(rows) * (ch + rgap) - rgap + 34
    sc = Scene("skills", int(status_y + 20), "Tech stack: " + ", ".join(P["skills"]))
    chrome(sc, "tech-stack.json")
    d = sc.delay
    for i, (wd, cx, cy, w, h) in enumerate(tokens_line(P["skills_comment"], 24, y_c, 15)):
        drag(sc, word(wd, 15, C["muted"], italic=True), w, h, cx, cy, d + 0.8 + i * 0.15)
    k = 0
    for ri, row in enumerate(rows):
        total = sum(w for _, w, _ in row) + gap * (len(row) - 1)
        x = (W - total) / 2
        cy = y_rows + ri * (ch + rgap) + ch / 2
        for s, w, col in row:
            drag(sc, chip(s, fs, w, ch, col), w, ch, x + w / 2, cy, d + 1.1 + k * 0.17 + random.uniform(-.06, .06))
            x += w + gap
            k += 1
    status(sc, status_y)
    return sc


def rrect_path(x, y, w, h, r):
    return (f"M{num(x + r)} {num(y)}H{num(x + w - r)}A{r} {r} 0 0 1 {num(x + w)} {num(y + r)}"
            f"V{num(y + h - r)}A{r} {r} 0 0 1 {num(x + w - r)} {num(y + h)}H{num(x + r)}"
            f"A{r} {r} 0 0 1 {num(x)} {num(y + h - r)}V{num(y + r)}A{r} {r} 0 0 1 {num(x + r)} {num(y)}Z")


def draw_card(sc, x, y, w, h, t0, dur):
    """Satu kursor 'menggambar' garis tepi kartu, lalu kartunya terisi."""
    ai = pick_agent()
    col = AGENTS[ai][1]
    r = 10
    d_ = rrect_path(x, y, w, h, r)
    L = 2 * (w - 2 * r) + 2 * (h - 2 * r) + 2 * math.pi * r
    t1 = t0 + dur
    sc.register(ai, t1, t1 + 0.5)

    def card(T):
        dash = A("stroke-dashoffset", [(t0, num(L)), (t1, "0")], T)
        stroke = A("stroke", [(t1, col), (t1 + .6, C["border"])], T)
        fill = A("fill-opacity", [(t1, "0"), (t1 + .4, "1")], T)
        op = A("opacity", [(t0, "0"), (t0 + .02, "1")] + loopfade(T), T)
        return (f'<g opacity="0">{op}<path d="{d_}" fill="{C["panel"]}" fill-opacity="0" stroke="{C["border"]}" '
                f'stroke-width="1.5" stroke-dasharray="{num(L)}" stroke-dashoffset="{num(L)}">{dash}{stroke}{fill}</path></g>')

    def cursor(T):
        a, b = num4(t0 / T), num4(t1 / T)
        mo = (f'<animateMotion path="{d_}" keyPoints="0;0;1;1" keyTimes="0;{a};{b};1" calcMode="linear" '
              f'dur="{num(T)}s" {rep()}/>')
        op = A("opacity", [(t0, "0"), (t0 + .1, "1"), (t1 + .1, "1"), (t1 + .5, "0")], T)
        return f'<g opacity="0">{mo}{op}<use href="#a{ai}"/></g>'
    sc.add("bg", card)
    sc.add("cursors", cursor)
    return t1


def wrap(text, maxc):
    lines, cur = [], ""
    for wd in text.split():
        if cur and len(cur) + 1 + len(wd) > maxc:
            lines.append(cur)
            cur = wd
        else:
            cur = f"{cur} {wd}" if cur else wd
    if cur:
        lines.append(cur)
    return lines


def build_projects(P):
    projs = P["projects"]
    cols = 2 if len(projs) > 1 else 1
    pad, gap = 28, 18
    cw_card = (W - 2 * pad - gap * (cols - 1)) / cols
    fs_t, fs_d, fs_g = 15, 13, 11.5
    maxc = int((cw_card - 40) / (fs_d * CWR))
    descs = [wrap(p["desc"], maxc) for p in projs]
    heights = [24 + 18 + 18 + len(ds) * 21 + 16 + 24 + 20 for ds in descs]
    row_h = [max(heights[i:i + cols]) for i in range(0, len(projs), cols)]
    y_c = TOP + 34
    y_cards = y_c + 30
    status_y = y_cards + sum(row_h) + gap * (len(row_h) - 1) + 30
    sc = Scene("projects", int(status_y + 20), "Proyek pilihan")
    chrome(sc, "proyek/")
    d = sc.delay
    for i, (wd, cx, cy, w, h) in enumerate(tokens_line(P["projects_comment"], 24, y_c, 15)):
        drag(sc, word(wd, 15, C["muted"], italic=True), w, h, cx, cy, d + 0.8 + i * 0.15)

    user = P["github_user"]
    y = y_cards
    for ri in range(len(row_h)):
        for ci in range(cols):
            i = ri * cols + ci
            if i >= len(projs):
                break
            pr, x = projs[i], pad + ci * (cw_card + gap)
            t1 = draw_card(sc, x, y, cw_card, row_h[ri], d + 0.9 + i * 0.55, 1.15)
            # judul: "user/" + "nama-proyek"
            tx, ty = x + 20, y + 30
            pre = user + "/" if pr.get("url") else ""
            wpre, wname = len(pre) * fs_t * CWR, len(pr["name"]) * fs_t * CWR
            if len(pre) + len(pr["name"]) > maxc * fs_d / fs_t:
                pre, wpre = "", 0
            if pre:
                drag(sc, word(pre, fs_t, C["muted"]), wpre, 20, tx + wpre / 2, ty, t1 + .1)
            drag(sc, word(pr["name"], fs_t, C["key"], bold=True), wname, 20, tx + wpre + wname / 2, ty, t1 + .3)
            # deskripsi kata demi kata
            k = 0
            for li, ln in enumerate(descs[i]):
                for wd, cx, cy, w, h in tokens_line(ln, tx, ty + 32 + li * 21, fs_d):
                    drag(sc, word(wd, fs_d, "#9198a1"), w, h, cx, cy, t1 + .45 + k * 0.07)
                    k += 1
            # tag
            gx = tx
            gy = y + row_h[ri] - 30
            for j, tg in enumerate(pr.get("tags", [])):
                w = len(tg) * fs_g * CWR + 20
                drag(sc, chip(tg, fs_g, w, 22, CHIP_COLORS[(i * 2 + j) % len(CHIP_COLORS)], dot=False),
                     w, 22, gx + w / 2, gy, t1 + .6 + k * 0.07 + j * 0.15)
                gx += w + 8
        y += row_h[ri] + gap
    status(sc, status_y)
    return sc


def build_footer(P, total, n_agents, n_files):
    fs = 14
    cw = fs * CWR
    y1, y2 = TOP + 38, TOP + 70
    sc = Scene("footer", TOP + 96, "Build selesai")
    chrome(sc, "terminal — zsh")
    d = sc.delay
    user = P["github_user"]
    prompt = f"~/{user}"
    sc.add("bg", f'<text class="m" x="28" y="{y1}" font-size="{fs}" fill="{C["green"]}">{esc(prompt)} '
                 f'<tspan fill="{C["muted"]}">$</tspan></text>')
    cmd = f'git commit -m "feat: README dibangun {total} kursor AI"'
    c0 = len(prompt) + 3
    ai = 0  # agen pertama di daftar AGENTS yang mengetik
    name, col, fg = AGENTS[ai]
    times, t = [], d + 0.7
    for ch in cmd:
        t += random.uniform(0.03, 0.065) + (0.05 if ch == " " else 0)
        times.append(t)
    t_end = times[-1]
    sc.register(ai, t_end, t_end + 1.0)

    def typed(T):
        out = []
        for i, (ch, ti) in enumerate(zip(cmd, times)):
            if ch == " ":
                continue
            colr = C["str"] if i >= cmd.index('"') else C["text"]
            out.append(f'<text class="m" x="{num(28 + (c0 + i) * cw)}" y="{y1}" font-size="{fs}" fill="{colr}" '
                       f'opacity="0">{A("opacity", window(T, ti - .02), T)}{esc(ch)}</text>')
        h7 = hashlib.md5(P["name"].encode()).hexdigest()[:7]
        out.append(f'<text class="m" x="28" y="{y2}" font-size="{fs - 1}" fill="{C["muted"]}" opacity="0">'
                   f'{A("opacity", window(T, t_end + .5), T)}<tspan fill="{C["green"]}">✓</tspan> [main {h7}] '
                   f'{n_files} file berubah · {total} potongan · {n_agents} model AI · 0 konflik</text>')
        return "".join(out)

    def caret(T):
        xs = [28 + (c0 + i) * cw for i in range(len(cmd) + 1)]
        kts = ["0"] + [num4(ti / T) for ti in times]
        vals = [f"{num(x)} {y1}" for x in xs]
        mv = (f'<animateTransform attributeName="transform" type="translate" calcMode="discrete" '
              f'values="{";".join(vals)}" keyTimes="{";".join(kts)}" dur="{num(T)}s" {rep()}/>')
        lw = len(name) * 6.5 + 10
        blink = ("" if LOOP else f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1s" '
                                 f'begin="{num(t_end + .3)}s" repeatCount="indefinite"/>')
        return (f'<g transform="translate({num(xs[0])} {y1})">{mv}<g>{blink}'
                f'<rect x="0" y="{-fs}" width="2" height="{num(fs * 1.35)}" fill="{col}"/>'
                f'<rect x="0" y="{-fs - 17}" width="{num(lw)}" height="15" rx="3" fill="{col}"/>'
                f'<text x="5" y="{-fs - 6}" font-size="10" font-weight="600" fill="{fg}">{esc(name)}</text></g></g>')
    sc.add("pieces", typed)
    sc.add("cursors", caret)
    return sc


# ───────────────────────────── README + preview ─────────────────────────────
def badges(P):
    c, out = P["contact"], []
    spec = [("instagram", "Instagram", "E4405F", "instagram", lambda v: v),
            ("facebook", "Facebook", "1877F2", "facebook", lambda v: v),
            ("email", "Gmail", "D14836", "gmail", lambda v: "mailto:" + v),
            ("whatsapp", "WhatsApp", "25D366", "whatsapp", lambda v: v),
            ("linkedin", "LinkedIn", "0A66C2", "linkedin", lambda v: v),
            ("website", "Website", "111827", "googlechrome", lambda v: v)]
    for key, label, color, logo, href in spec:
        if c.get(key):
            out.append(f'<a href="{esc(href(c[key]))}"><img src="https://img.shields.io/badge/{label}-{color}'
                       f'?style=for-the-badge&logo={logo}&logoColor=white" alt="{label}" /></a>')
    u = P["github_user"]
    out.append(f'<a href="https://github.com/{esc(u)}"><img src="https://img.shields.io/github/followers/{esc(u)}'
               f'?style=for-the-badge&logo=github&label=Follow&color=24292f" alt="GitHub followers" /></a>')
    out.append(f'<br/><img src="https://visitor-badge.laobi.icu/badge?page_id={esc(u)}.{esc(u)}" alt="visitor badge" />')
    return "\n".join(out)


def build_readme(P, files):
    alt = {k: esc(sc.label) for k, sc in files.items()}
    links = " · ".join(f"[{p['name']}]({p['url']})" for p in P["projects"] if p.get("url"))
    parts = [
        "<!-- README ini \"dibangun live\" oleh ratusan kursor AI. Dibuat dengan generate.py — edit di sana, bukan di sini. -->",
        '<div align="center">', "",
        f'<img src="./assets/hero.svg" width="100%" alt="{alt["hero"]}" />', "",
    ]
    if SITE_URL:
        parts += [f'<sub>✨ <a href="{esc(SITE_URL)}"><b>Buka versi interaktif</b></a>: tiap bagian dibangun ulang '
                  f'setiap kali kamu scroll ke sana</sub>', ""]
    parts += [
        f'<img src="./assets/about.svg" width="100%" alt="{alt["about"]}" />', "",
        f'<img src="./assets/skills.svg" width="100%" alt="{alt["skills"]}" />', "",
        f'<img src="./assets/projects.svg" width="100%" alt="{alt["projects"]}" />', "",
    ]
    if links:
        parts += [f"**Lihat proyek →** {links}", ""]
    parts += [badges(P), "",
              f'<img src="https://streak-stats.demolab.com?user={esc(P["github_user"])}&theme=tokyonight&hide_border=true" alt="GitHub streak" />', "",
              f'<img src="./assets/footer.svg" width="100%" alt="{alt["footer"]}" />', "",
              "<sub>Animasi diputar saat halaman dibuka. Muat ulang halaman untuk menonton para kursor membangunnya lagi.</sub>",
              "", "</div>", ""]
    return "\n".join(parts)


def build_preview(svgs):
    data = json.dumps({k: v for k, v in svgs.items()})
    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pratinjau README</title>
<style>
:root{{--bg:#0d1117;--fg:#e6edf3;--muted:#8b949e;--line:#30363d}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}}
.wrap{{max-width:980px;margin:0 auto;padding:24px 16px 64px}}
.bar{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;
border:1px solid var(--line);border-radius:6px 6px 0 0;padding:10px 16px;background:#161b22;color:var(--muted);font-size:14px}}
.readme{{border:1px solid var(--line);border-top:0;border-radius:0 0 6px 6px;padding:24px}}
img{{display:block;width:100%;height:auto;margin:0 0 16px}}
button{{background:#238636;color:#fff;border:0;border-radius:6px;padding:6px 14px;font:inherit;font-weight:600;cursor:pointer}}
button:hover{{background:#2ea043}}
@media (max-width:600px){{.readme{{padding:12px}}}}
</style></head><body><div class="wrap">
<div class="bar"><span>README.md</span><button id="replay">↻ Putar ulang</button></div>
<div class="readme" id="readme"></div></div>
<script>
const SVGS = {data};
const order = ["hero","about","skills","projects","footer"];
function mount() {{
  const root = document.getElementById("readme");
  root.querySelectorAll("img").forEach(i => URL.revokeObjectURL(i.src));
  root.innerHTML = "";
  for (const k of order) {{
    const img = new Image();
    img.alt = k;
    img.src = URL.createObjectURL(new Blob([SVGS[k]], {{type: "image/svg+xml"}}));
    root.appendChild(img);
  }}
}}
document.getElementById("replay").onclick = mount;
mount();
</script></body></html>
"""


def build_site(P, svgs, scenes):
    """index.html untuk GitHub Pages: tiap bagian dibangun ulang saat di-scroll ke layar."""
    data = json.dumps(svgs)
    sizes = json.dumps({k: [W, sc.h] for k, sc in scenes.items()})
    alts = json.dumps({k: sc.label for k, sc in scenes.items()})
    plinks = "".join(f'<a href="{esc(p["url"])}">{esc(p["name"])} ↗</a>' for p in P["projects"] if p.get("url"))
    c = P["contact"]
    clinks = [("Instagram", c.get("instagram")) if c.get("instagram") else None,
              ("Facebook", c.get("facebook")) if c.get("facebook") else None,
              ("WhatsApp", c.get("whatsapp")) if c.get("whatsapp") else None,
              ("Email", "mailto:" + c["email"]) if c.get("email") else None,
              ("LinkedIn", c.get("linkedin")) if c.get("linkedin") else None,
              ("Website", c.get("website")) if c.get("website") else None,
              ("GitHub", f'https://github.com/{P["github_user"]}')]
    clinks = "".join(f'<a href="{esc(u)}">{esc(t)}</a>' for t, u in filter(None, clinks))
    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(P["name"].title())}</title>
<meta name="description" content="{esc(P["tagline"])}">
<style>
:root{{--bg:#0d1117;--fg:#e6edf3;--muted:#8b949e;--line:#30363d;--panel:#161b22}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif}}
main{{max-width:960px;margin:0 auto;padding:32px 16px 96px}}
.sec{{display:block;width:100%;height:auto;margin:0 0 40px;border-radius:12px;background:var(--bg);outline:1px solid var(--line);outline-offset:-1px}}
.links{{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:-16px 0 40px}}
.links a{{color:var(--fg);text-decoration:none;border:1px solid var(--line);background:var(--panel);border-radius:999px;padding:6px 14px;font-size:14px}}
.links a:hover{{border-color:#8b949e}}
.hint{{text-align:center;color:var(--muted);font-size:13px;margin:-24px 0 40px}}
</style></head><body><main id="page"></main>
<script>
const SVGS = {data};
const SIZE = {sizes};
const ALT = {alts};
const order = ["hero","about","skills","projects","footer"];
const page = document.getElementById("page");
function play(img) {{
  if (img.src.startsWith("blob:")) URL.revokeObjectURL(img.src);
  img.alt = ALT[img.dataset.k];
  img.src = URL.createObjectURL(new Blob([SVGS[img.dataset.k]], {{type: "image/svg+xml"}}));
}}
const io = new IntersectionObserver(entries => {{
  for (const e of entries) {{
    const img = e.target;
    if (e.intersectionRatio >= 0.3 && !img.dataset.on) {{ img.dataset.on = "1"; play(img); }}
    else if (!e.isIntersecting) delete img.dataset.on;  // keluar layar: siap dibangun ulang
  }}
}}, {{threshold: [0, 0.3]}});
for (const k of order) {{
  const img = document.createElement("img");
  img.className = "sec"; img.dataset.k = k; img.alt = "";
  img.width = SIZE[k][0]; img.height = SIZE[k][1];
  img.style.aspectRatio = SIZE[k][0] + " / " + SIZE[k][1];
  page.appendChild(img);
  io.observe(img);
  if (k === "hero") page.insertAdjacentHTML("beforeend", '<p class="hint">scroll pelan-pelan: tiap bagian dibangun ulang oleh para kursor AI ↓</p>');
  if (k === "projects") page.insertAdjacentHTML("beforeend", '<nav class="links">{plinks}</nav><nav class="links">{clinks}</nav>');
}}
</script></body></html>
"""


def build_all(P, delays):
    global _DELAYS
    _DELAYS = dict(delays)
    random.seed(SEED)
    _recent.clear()
    scenes = {"hero": build_hero(P), "about": build_about(P), "skills": build_skills(P),
              "projects": build_projects(P)}
    total = sum(s.cursors for s in scenes.values()) + 1
    used = set().union(*(s.agent_ids for s in scenes.values()))
    scenes["footer"] = build_footer(P, total, len(used), len(scenes) + 1)
    return scenes, {k: sc.render() for k, sc in scenes.items()}, total, used


def main():
    P = PROFILE
    os.makedirs(ASSETS, exist_ok=True)
    # 1) README: SVG dengan jeda per bagian (GitHub tidak bisa mendeteksi scroll)
    scenes, svgs, total, used = build_all(P, SECTION_DELAY)
    for k, sc in scenes.items():
        with open(os.path.join(ASSETS, f"{k}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svgs[k])
        print(f"assets/{k}.svg  {len(svgs[k]) / 1024:6.1f} KB  {sc.cursors:4d} kursor  {sc.T:5.1f} dtk")
    with open(os.path.join(HERE, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(build_readme(P, scenes))
    with open(os.path.join(HERE, "preview.html"), "w", encoding="utf-8") as fh:
        fh.write(build_preview(svgs))
    # 2) Situs GitHub Pages: tiap bagian langsung mulai begitu terlihat di layar
    site_scenes, site_svgs, _, _ = build_all(P, {k: 0.15 for k in SECTION_DELAY})
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_site(P, site_svgs, site_scenes))
    print(f"Total {total} kursor AI dari {len(used)} model. README.md, preview.html, index.html siap.")


if __name__ == "__main__":
    main()
