"""Generator rysunków pomocniczych w stylu arkuszy CKE (Matplotlib -> PNG 260 DPI)."""

from __future__ import annotations

import hashlib
import json
import math
import tempfile
from pathlib import Path
from typing import Dict, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from .models import DiagramSpec

_DIAG_CACHE_DIR = Path(tempfile.gettempdir()) / "e8_generator_diag_cache"
_DIAG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_DIAG_CACHE: Dict[str, Tuple[str, int, int]] = {}

# Kolorystyka techniczna CKE (świetna zarówno na ekranie, jak i w czarno-białym druku)
INK = "#111827"
MUTED = "#4B5563"
GRID_COL = "#CBD5E1"
FILL_LIGHT = "#E2E8F0"
FILL_WATER = "#DBEAFE"
BAR_FILL = "#64748B"


def render_diagram(spec: DiagramSpec) -> Tuple[str, int, int]:
    """Renderuje DiagramSpec do pliku PNG i zwraca (posix_path, width_px, height_px)."""
    payload = json.dumps({"kind": spec.kind, "params": spec.params, "caption": spec.caption}, sort_keys=True, ensure_ascii=False)
    digest = hashlib.md5(payload.encode("utf-8")).hexdigest()[:16]
    if digest in _DIAG_CACHE:
        p_str, w_px, h_px = _DIAG_CACHE[digest]
        if Path(p_str).exists():
            return p_str, w_px, h_px

    out_path = _DIAG_CACHE_DIR / f"diag_{spec.kind}_{digest}.png"

    dispatch = {
        "number_line": _draw_number_line,
        "coord_plane": _draw_coord_plane,
        "right_triangle": _draw_right_triangle,
        "isosceles_triangle": _draw_isosceles_triangle,
        "parallel_angles": _draw_parallel_angles,
        "trapezoid": _draw_trapezoid,
        "circle_chord": _draw_circle_chord,
        "prism_net": _draw_prism_net,
        "cuboid_water": _draw_cuboid_water,
        "bar_chart": _draw_bar_chart,
    }
    fn = dispatch.get(spec.kind, _draw_number_line)
    fig = fn(spec.params)

    if spec.caption:
        fig.text(0.98, 0.02, spec.caption, ha="right", va="bottom", fontsize=7.5, style="italic", color=MUTED)

    dpi = 260
    fig.savefig(str(out_path), dpi=dpi, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    plt.close(fig)

    with Image.open(out_path) as im:
        w_px, h_px = im.size

    posix_path = out_path.as_posix()
    _DIAG_CACHE[digest] = (posix_path, w_px, h_px)
    return posix_path, w_px, h_px


def _fmt_pl(v: float | int) -> str:
    if isinstance(v, float) and abs(v - round(v)) < 1e-9:
        v = int(round(v))
    s = str(v).replace(".", ",")
    if s.startswith("-"):
        s = "−" + s[1:]
    return s


def _draw_number_line(p: dict) -> plt.Figure:
    """Oś liczbowa z równymi odstępami i zaznaczonymi punktami."""
    ticks = p.get("ticks", list(range(-4, 7)))
    labeled_ticks = p.get("labeled_ticks", {0: "0", 1: "1"})
    # json konwertuje klucze na str lub mogą być int
    labeled_map = {float(k): str(v) for k, v in labeled_ticks.items()}
    points = p.get("points", [])  # lista {"x": float, "label": "P"}

    xmin, xmax = min(ticks) - 0.8, max(ticks) + 1.0
    fig, ax = plt.subplots(figsize=(5.2, 1.15))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.65, 0.75)
    ax.axis("off")

    # Główna oś ze strzałką
    ax.annotate(
        "",
        xy=(xmax, 0),
        xytext=(xmin, 0),
        arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.45", lw=1.35, color=INK),
    )

    for t in ticks:
        ax.plot([t, t], [-0.12, 0.12], color=INK, lw=1.1)
        for lk, lv in labeled_map.items():
            if abs(t - lk) < 1e-6:
                ax.text(t, -0.36, lv, ha="center", va="center", fontsize=9.5, color=INK)

    for pt in points:
        px = float(pt["x"])
        lbl = pt.get("label", "")
        ax.plot([px], [0], marker="o", markersize=5.5, color=INK)
        if lbl:
            ax.text(px, 0.34, lbl, ha="center", va="center", fontsize=10, fontweight="bold", style="italic", color=INK)

    return fig


def _draw_coord_plane(p: dict) -> plt.Figure:
    """Układ współrzędnych z kratką CKE, wielokątem/odcinkiem i punktami."""
    lim = int(p.get("limit", 6))
    points = p.get("points", [])  # [{"x": -2, "y": 3, "label": "A"}]
    polygon = p.get("polygon", [])  # [[x1,y1], [x2,y2], ...]
    segments = p.get("segments", [])  # [[[x1,y1],[x2,y2]], ...]

    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    ax.set_xlim(-lim - 0.6, lim + 0.8)
    ax.set_ylim(-lim - 0.6, lim + 0.8)
    ax.set_aspect("equal")
    ax.axis("off")

    # Kratka
    for i in range(-lim, lim + 1):
        ax.plot([i, i], [-lim, lim], color=GRID_COL, lw=0.65, zorder=1)
        ax.plot([-lim, lim], [i, i], color=GRID_COL, lw=0.65, zorder=1)

    # Osie x i y
    ax.annotate("", xy=(lim + 0.65, 0), xytext=(-lim - 0.35, 0),
                arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.35", lw=1.2, color=INK), zorder=3)
    ax.annotate("", xy=(0, lim + 0.65), xytext=(0, -lim - 0.35),
                arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.35", lw=1.2, color=INK), zorder=3)
    ax.text(lim + 0.55, -0.45, "x", fontsize=10, style="italic", ha="center", va="top", color=INK)
    ax.text(-0.45, lim + 0.55, "y", fontsize=10, style="italic", ha="right", va="center", color=INK)

    # Jednostki 1 na osiach (styl CKE)
    ax.plot([1, 1], [-0.14, 0.14], color=INK, lw=1.1, zorder=4)
    ax.plot([-0.14, 0.14], [1, 1], color=INK, lw=1.1, zorder=4)
    ax.text(1, -0.45, "1", fontsize=8.5, ha="center", va="top", color=INK)
    ax.text(-0.35, 1, "1", fontsize=8.5, ha="right", va="center", color=INK)
    ax.text(-0.3, -0.42, "0", fontsize=8.5, ha="right", va="top", color=INK)

    if polygon:
        poly_patch = patches.Polygon(polygon, closed=True, facecolor=FILL_LIGHT, edgecolor=INK, lw=1.5, alpha=0.65, zorder=2)
        ax.add_patch(poly_patch)

    for seg in segments:
        (x1, y1), (x2, y2) = seg
        ax.plot([x1, x2], [y1, y2], color=INK, lw=1.6, zorder=4)

    for pt in points:
        px, py = float(pt["x"]), float(pt["y"])
        lbl = pt.get("label", "")
        dx = float(pt.get("dx", 0.32 if px >= 0 else -0.38))
        dy = float(pt.get("dy", 0.32 if py >= 0 else -0.38))
        ax.plot([px], [py], marker="o", markersize=4.8, color=INK, zorder=5)
        if lbl:
            ax.text(px + dx, py + dy, lbl, fontsize=9.5, fontweight="bold", style="italic", ha="center", va="center", color=INK, zorder=6)

    return fig


def _draw_right_triangle(p: dict) -> plt.Figure:
    """Trójkąt prostokątny z polskim oznaczeniem kąta prostego (kwadracik z kropką)."""
    lbl_a = p.get("label_a", "")
    lbl_b = p.get("label_b", "")
    lbl_c = p.get("label_c", "")
    vertices = p.get("vertices", ["A", "B", "C"])  # kąt prosty przy pierwszym lub drugim: dajmy przy A=(0,0) lub C

    w, h = 4.0, 2.7
    fig, ax = plt.subplots(figsize=(3.4, 2.35))
    ax.set_xlim(-0.7, w + 0.8)
    ax.set_ylim(-0.65, h + 0.65)
    ax.set_aspect("equal")
    ax.axis("off")

    pts = [(0, 0), (w, 0), (0, h)]
    poly = patches.Polygon(pts, closed=True, facecolor=FILL_LIGHT, edgecolor=INK, lw=1.5, alpha=0.45)
    ax.add_patch(poly)

    # Kąt prosty z kropką przy (0,0)
    sq = 0.38
    ax.plot([sq, sq, 0], [0, sq, sq], color=INK, lw=1.0)
    ax.plot([sq * 0.48], [sq * 0.48], marker="o", markersize=2.2, color=INK)

    if len(vertices) == 3:
        ax.text(-0.26, -0.24, vertices[0], fontsize=10, style="italic", ha="center", va="center", color=INK)
        ax.text(w + 0.26, -0.24, vertices[1], fontsize=10, style="italic", ha="center", va="center", color=INK)
        ax.text(-0.26, h + 0.24, vertices[2], fontsize=10, style="italic", ha="center", va="center", color=INK)

    if lbl_a:
        ax.text(w / 2, -0.34, lbl_a, fontsize=9.5, ha="center", va="top", color=INK)
    if lbl_b:
        ax.text(-0.22, h / 2, lbl_b, fontsize=9.5, ha="right", va="center", color=INK)
    if lbl_c:
        ax.text(w / 2 + 0.25, h / 2 + 0.22, lbl_c, fontsize=9.5, ha="left", va="bottom", color=INK)

    return fig


def _draw_isosceles_triangle(p: dict) -> plt.Figure:
    """Trójkąt równoramienny ABC (|AC| = |BC|) z wysokością h lub kątem."""
    base_lbl = p.get("base_label", "")
    arm_lbl = p.get("arm_label", "")
    h_lbl = p.get("height_label", "")
    show_height = bool(p.get("show_height", True))
    top_angle = p.get("top_angle", "")
    base_angle = p.get("base_angle", "")

    w, h = 4.2, 3.0
    fig, ax = plt.subplots(figsize=(3.5, 2.55))
    ax.set_xlim(-0.7, w + 0.7)
    ax.set_ylim(-0.65, h + 0.65)
    ax.set_aspect("equal")
    ax.axis("off")

    A, B, C = (0.0, 0.0), (w, 0.0), (w / 2, h)
    poly = patches.Polygon([A, B, C], closed=True, facecolor=FILL_LIGHT, edgecolor=INK, lw=1.5, alpha=0.4)
    ax.add_patch(poly)

    ax.text(-0.24, -0.22, "A", fontsize=10, style="italic", ha="center", va="center", color=INK)
    ax.text(w + 0.24, -0.22, "B", fontsize=10, style="italic", ha="center", va="center", color=INK)
    ax.text(w / 2, h + 0.28, "C", fontsize=10, style="italic", ha="center", va="center", color=INK)

    if show_height:
        ax.plot([w / 2, w / 2], [0, h], color=INK, lw=1.1, ls="--")
        sq = 0.32
        ax.plot([w / 2, w / 2 + sq, w / 2 + sq], [sq, sq, 0], color=INK, lw=0.95)
        ax.plot([w / 2 + sq * 0.48], [sq * 0.48], marker="o", markersize=2.0, color=INK)
        ax.text(w / 2, -0.28, "D", fontsize=9.5, style="italic", ha="center", va="top", color=INK)
        if h_lbl:
            ax.text(w / 2 + 0.18, h * 0.45, h_lbl, fontsize=9.5, ha="left", va="center", color=INK)

    if base_lbl:
        ax.text(w / 2, -0.34 if not show_height else -0.52, base_lbl, fontsize=9.5, ha="center", va="top", color=INK)
    if arm_lbl:
        ax.text(w * 0.78 + 0.22, h * 0.55, arm_lbl, fontsize=9.5, ha="left", va="center", color=INK)
        ax.text(w * 0.22 - 0.22, h * 0.55, arm_lbl, fontsize=9.5, ha="right", va="center", color=INK)
    if base_angle:
        arc = patches.Arc(A, 1.1, 1.1, angle=0, theta1=0, theta2=math.degrees(math.atan2(h, w / 2)), color=INK, lw=1.1)
        ax.add_patch(arc)
        ax.text(0.75, 0.26, base_angle, fontsize=9, ha="left", va="center", color=INK)
    if top_angle:
        ang = math.degrees(math.atan2(w / 2, h))
        arc = patches.Arc(C, 1.1, 1.1, angle=0, theta1=270 - ang, theta2=270 + ang, color=INK, lw=1.1)
        ax.add_patch(arc)
        ax.text(w / 2, h - 0.82, top_angle, fontsize=9, ha="center", va="top", color=INK)

    return fig


def _draw_parallel_angles(p: dict) -> plt.Figure:
    """Dwie proste równoległe k || l przecięte sieczną z kątami."""
    top_lbl = p.get("top_label", "124°")
    bot_lbl = p.get("bottom_label", "α")
    mode = p.get("mode", "alternate")  # "alternate" lub "supplementary"

    fig, ax = plt.subplots(figsize=(3.8, 2.2))
    ax.set_xlim(-2.6, 2.8)
    ax.set_ylim(-1.35, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")

    # Proste równoległe k i l
    ax.plot([-2.4, 2.4], [0.7, 0.7], color=INK, lw=1.4)
    ax.plot([-2.4, 2.4], [-0.7, -0.7], color=INK, lw=1.4)
    ax.text(2.52, 0.7, "k", fontsize=10, style="italic", va="center", color=INK)
    ax.text(2.52, -0.7, "l", fontsize=10, style="italic", va="center", color=INK)

    # Sieczna pod kątem ~58 stopni
    dx = 0.85
    ax.plot([-dx, dx], [-1.25, 1.25], color=INK, lw=1.4)
    theta = math.degrees(math.atan2(1.25, dx))  # ok. 55.8°

    # Punkt przecięcia górny i dolny
    x_top = dx * (0.7 / 1.25)
    x_bot = -dx * (0.7 / 1.25)

    # Kąt rozwarty u góry po lewej (180 - theta)
    arc1 = patches.Arc((x_top, 0.7), 0.78, 0.78, angle=0, theta1=theta, theta2=180, color=INK, lw=1.1)
    ax.add_patch(arc1)
    ax.text(x_top - 0.35, 0.98, top_lbl, fontsize=9.5, ha="center", va="bottom", color=INK)

    if mode == "alternate":
        # Kąt ostry na dole po prawej
        arc2 = patches.Arc((x_bot, -0.7), 0.78, 0.78, angle=0, theta1=0, theta2=theta, color=INK, lw=1.1)
        ax.add_patch(arc2)
        ax.text(x_bot + 0.56, -0.5, bot_lbl, fontsize=10, style="italic", ha="left", va="center", color=INK)
    else:
        arc2 = patches.Arc((x_bot, -0.7), 0.78, 0.78, angle=0, theta1=theta, theta2=180, color=INK, lw=1.1)
        ax.add_patch(arc2)
        ax.text(x_bot - 0.35, -0.42, bot_lbl, fontsize=10, style="italic", ha="center", va="bottom", color=INK)

    return fig


def _draw_trapezoid(p: dict) -> plt.Figure:
    """Trapez prostokątny lub równoramienny z wymiarami."""
    kind = p.get("trap_kind", "right")  # "right" lub "isosceles"
    a_lbl = p.get("a_label", "")
    b_lbl = p.get("b_label", "")
    h_lbl = p.get("h_label", "")
    c_lbl = p.get("c_label", "")

    fig, ax = plt.subplots(figsize=(3.6, 2.35))
    ax.set_aspect("equal")
    ax.axis("off")

    if kind == "right":
        A, B, C, D = (0.0, 0.0), (4.2, 0.0), (2.7, 2.2), (0.0, 2.2)
        ax.set_xlim(-0.8, 4.9)
        ax.set_ylim(-0.65, 2.85)
        poly = patches.Polygon([A, B, C, D], closed=True, facecolor=FILL_LIGHT, edgecolor=INK, lw=1.5, alpha=0.45)
        ax.add_patch(poly)
        sq = 0.32
        ax.plot([sq, sq, 0], [0, sq, sq], color=INK, lw=0.95)
        ax.plot([sq * 0.48], [sq * 0.48], marker="o", markersize=2.0, color=INK)
        if h_lbl:
            ax.text(-0.22, 1.1, h_lbl, fontsize=9.5, ha="right", va="center", color=INK)
        if b_lbl:
            ax.text(1.35, 2.35, b_lbl, fontsize=9.5, ha="center", va="bottom", color=INK)
        if c_lbl:
            ax.text(3.58, 1.18, c_lbl, fontsize=9.5, ha="left", va="center", color=INK)
    else:
        A, B, C, D = (0.0, 0.0), (4.4, 0.0), (3.3, 2.2), (1.1, 2.2)
        ax.set_xlim(-0.7, 5.1)
        ax.set_ylim(-0.65, 2.85)
        poly = patches.Polygon([A, B, C, D], closed=True, facecolor=FILL_LIGHT, edgecolor=INK, lw=1.5, alpha=0.45)
        ax.add_patch(poly)
        ax.plot([1.1, 1.1], [0, 2.2], color=INK, lw=1.05, ls="--")
        sq = 0.3
        ax.plot([1.1, 1.1 + sq, 1.1 + sq], [sq, sq, 0], color=INK, lw=0.95)
        ax.plot([1.1 + sq * 0.48], [sq * 0.48], marker="o", markersize=2.0, color=INK)
        if h_lbl:
            ax.text(1.24, 1.05, h_lbl, fontsize=9.5, ha="left", va="center", color=INK)
        if b_lbl:
            ax.text(2.2, 2.35, b_lbl, fontsize=9.5, ha="center", va="bottom", color=INK)
        if c_lbl:
            ax.text(4.0, 1.18, c_lbl, fontsize=9.5, ha="left", va="center", color=INK)

    if a_lbl:
        ax.text(2.1, -0.34, a_lbl, fontsize=9.5, ha="center", va="top", color=INK)

    for (vx, vy), name, (ox, oy) in zip([A, B, C, D], ["A", "B", "C", "D"], [(-0.24, -0.24), (0.24, -0.24), (0.22, 0.22), (-0.24, 0.22)]):
        ax.text(vx + ox, vy + oy, name, fontsize=9.5, style="italic", ha="center", va="center", color=INK)

    return fig


def _draw_circle_chord(p: dict) -> plt.Figure:
    """Okrąg o środku S z cięciwą AB i odległością od środka (wzorzec CKE 2024)."""
    chord_lbl = p.get("chord_label", "AB")
    dist_show = bool(p.get("show_dist", True))

    fig, ax = plt.subplots(figsize=(2.9, 2.8))
    R = 1.8
    ax.set_xlim(-2.35, 2.35)
    ax.set_ylim(-2.25, 2.25)
    ax.set_aspect("equal")
    ax.axis("off")

    circ = patches.Circle((0, 0), R, facecolor="none", edgecolor=INK, lw=1.45)
    ax.add_patch(circ)
    ax.plot([0], [0], marker="o", markersize=4.5, color=INK)
    ax.text(-0.18, 0.2, "S", fontsize=10, style="italic", fontweight="bold", color=INK)

    # Cięciwa pozioma pod środkiem
    yc = -0.95
    xc = math.sqrt(R * R - yc * yc)
    ax.plot([-xc, xc], [yc, yc], color=INK, lw=1.5)
    ax.plot([-xc, xc], [yc, yc], "o", markersize=4.2, color=INK)
    ax.text(-xc - 0.24, yc - 0.12, "A", fontsize=10, style="italic", ha="center", va="center", color=INK)
    ax.text(xc + 0.24, yc - 0.12, "B", fontsize=10, style="italic", ha="center", va="center", color=INK)

    # Promień SA przerywany
    ax.plot([0, xc], [0, yc], color=MUTED, lw=1.05, ls="--")
    if dist_show:
        ax.plot([0, 0], [0, yc], color=INK, lw=1.05, ls=":")

    if chord_lbl and chord_lbl != "AB":
        ax.text(0, yc - 0.28, chord_lbl, fontsize=9, ha="center", va="top", color=INK)

    return fig


def _draw_prism_net(p: dict) -> plt.Figure:
    """Siatka graniastosłupa prawidłowego czworokątnego ze strzałką wymiarową (klasyk CKE 2022/2024)."""
    dim_mode = p.get("dim_mode", "three_walls")  # "three_walls" (3a) lub "height_plus_base" (H + a) lub "both"
    horiz_label = p.get("horiz_label", "48 cm")
    vert_label = p.get("vert_label", "41 cm")

    a = 1.0
    H = 2.0
    fig, ax = plt.subplots(figsize=(4.0, 3.3))
    ax.set_xlim(-0.6, 4 * a + 1.25)
    ax.set_ylim(-a - 0.75, H + a + 0.55)
    ax.set_aspect("equal")
    ax.axis("off")

    # 4 ściany boczne
    for i in range(4):
        rect = patches.Rectangle((i * a, 0), a, H, facecolor=FILL_LIGHT, edgecolor=INK, lw=1.35, alpha=0.45)
        ax.add_patch(rect)

    # Dwie podstawy kwadratowe (przy drugiej od lewej i trzeciej ścianie dla urozmaicenia jak w CKE)
    top_sq = patches.Rectangle((a, H), a, a, facecolor=FILL_LIGHT, edgecolor=INK, lw=1.35, alpha=0.65)
    bot_sq = patches.Rectangle((2 * a, -a), a, a, facecolor=FILL_LIGHT, edgecolor=INK, lw=1.35, alpha=0.65)
    ax.add_patch(top_sq)
    ax.add_patch(bot_sq)

    # Strzałka pozioma pod 3 ścianami lub pod 4 ścianami
    span_w = 3 * a if dim_mode == "three_walls" else 4 * a
    if horiz_label:
        y_arr = -a - 0.32 if dim_mode != "three_walls" else -0.32
        if dim_mode == "three_walls":
            y_arr = H + a + 0.26
            ax.plot([0, 0], [H, y_arr + 0.08], color=MUTED, lw=0.8, ls=":")
            ax.plot([3 * a, 3 * a], [H, y_arr + 0.08], color=MUTED, lw=0.8, ls=":")
        else:
            ax.plot([0, 0], [0, y_arr - 0.08], color=MUTED, lw=0.8, ls=":")
            ax.plot([span_w, span_w], [0, y_arr - 0.08], color=MUTED, lw=0.8, ls=":")

        ax.annotate(
            "",
            xy=(span_w, y_arr),
            xytext=(0, y_arr),
            arrowprops=dict(arrowstyle="<->", lw=1.1, color=INK),
        )
        ax.text(
            span_w / 2,
            y_arr + (0.14 if dim_mode == "three_walls" else -0.24),
            horiz_label,
            fontsize=9.5,
            ha="center",
            va="bottom" if dim_mode == "three_walls" else "top",
            color=INK,
        )

    # Strzałka pionowa (np. wysokość H + krawędź podstawy a po prawej stronie)
    if vert_label:
        x_arr = 4 * a + 0.35
        y_top = H + a
        y_bot = 0.0
        ax.plot([2 * a, x_arr + 0.08], [y_top, y_top], color=MUTED, lw=0.8, ls=":")
        ax.plot([4 * a, x_arr + 0.08], [y_bot, y_bot], color=MUTED, lw=0.8, ls=":")
        ax.annotate(
            "",
            xy=(x_arr, y_top),
            xytext=(x_arr, y_bot),
            arrowprops=dict(arrowstyle="<->", lw=1.1, color=INK),
        )
        ax.text(x_arr + 0.14, (y_top + y_bot) / 2, vert_label, fontsize=9.5, ha="left", va="center", color=INK)

    return fig


def _draw_cuboid_water(p: dict) -> plt.Figure:
    """Prostopadłościenne akwarium z wodą w rzucie ukośnym (styl CKE)."""
    a_lbl = p.get("a_label", "40 cm")
    b_lbl = p.get("b_label", "25 cm")
    H_lbl = p.get("H_label", "30 cm")
    fill_ratio = float(p.get("fill_ratio", 0.6))

    W, H = 3.4, 2.3
    dx, dy = 1.05, 0.72
    hw = H * fill_ratio

    fig, ax = plt.subplots(figsize=(3.8, 2.7))
    ax.set_xlim(-0.5, W + dx + 0.95)
    ax.set_ylim(-0.55, H + dy + 0.45)
    ax.set_aspect("equal")
    ax.axis("off")

    # Wypełnienie wodą (przód + góra wody + prawy bok wody)
    front_water = patches.Polygon([(0, 0), (W, 0), (W, hw), (0, hw)], closed=True, facecolor=FILL_WATER, edgecolor="none", alpha=0.85)
    side_water = patches.Polygon([(W, 0), (W + dx, dy), (W + dx, dy + hw), (W, hw)], closed=True, facecolor="#BFDBFE", edgecolor="none", alpha=0.85)
    top_water = patches.Polygon([(0, hw), (W, hw), (W + dx, dy + hw), (dx, dy + hw)], closed=True, facecolor="#93C5FD", edgecolor=MUTED, lw=0.85, alpha=0.65)
    ax.add_patch(front_water)
    ax.add_patch(side_water)
    ax.add_patch(top_water)

    # Krawędzie tylne przerywane
    ax.plot([0, dx], [0, dy], color=MUTED, lw=1.0, ls="--")
    ax.plot([dx, W + dx], [dy, dy], color=MUTED, lw=1.0, ls="--")
    ax.plot([dx, dx], [dy, H + dy], color=MUTED, lw=1.0, ls="--")

    # Krawędzie widoczne prostopadłościanu
    ax.plot([0, W, W, 0, 0], [0, 0, H, H, 0], color=INK, lw=1.45)
    ax.plot([W, W + dx], [0, dy], color=INK, lw=1.45)
    ax.plot([W + dx, W + dx], [dy, H + dy], color=INK, lw=1.45)
    ax.plot([0, dx, W + dx, W], [H, H + dy, H + dy, H], color=INK, lw=1.45)

    if a_lbl:
        ax.text(W / 2, -0.32, a_lbl, fontsize=9.5, ha="center", va="top", color=INK)
    if b_lbl:
        ax.text(W + dx * 0.62 + 0.18, dy * 0.42 - 0.12, b_lbl, fontsize=9.5, ha="left", va="top", color=INK)
    if H_lbl:
        ax.text(W + dx + 0.18, dy + H / 2, H_lbl, fontsize=9.5, ha="left", va="center", color=INK)

    return fig


def _draw_bar_chart(p: dict) -> plt.Figure:
    """Diagram słupkowy w stylu arkuszy CKE."""
    categories = p.get("categories", ["I", "II", "III", "IV"])
    values = p.get("values", [12, 18, 15, 21])
    ylabel = p.get("ylabel", "Liczba")
    y_step = int(p.get("y_step", 5))
    show_values = bool(p.get("show_values", False))

    fig, ax = plt.subplots(figsize=(4.4, 2.35))
    x = np.arange(len(categories))
    bars = ax.bar(x, values, width=0.52, color=BAR_FILL, edgecolor=INK, linewidth=1.0, zorder=3)

    ymax = max(values) + y_step
    ymax = int(math.ceil(ymax / y_step) * y_step)
    ax.set_ylim(0, ymax)
    ax.set_yticks(range(0, ymax + 1, y_step))
    if y_step >= 10 and y_step % 2 == 0:
        ax.set_yticks(range(0, ymax + 1, y_step // 2), minor=True)
        ax.grid(axis="y", which="minor", color="#E2E8F0", linestyle="--", linewidth=0.55, zorder=0)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9, color=INK)
    ax.tick_params(axis="y", labelsize=8.5, colors=INK)
    ax.grid(axis="y", color=GRID_COL, linestyle="-", linewidth=0.75, zorder=0)
    ax.set_ylabel(ylabel, fontsize=8.8, color=INK)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(INK)
    ax.spines["bottom"].set_color(INK)

    if show_values:
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + ymax * 0.025, _fmt_pl(val),
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=INK)

    fig.tight_layout()
    return fig
