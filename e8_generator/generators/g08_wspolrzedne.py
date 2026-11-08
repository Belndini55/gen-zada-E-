"""Dział 8: Układ współrzędnych – odcinki, symetria i pola wielokątów."""

from __future__ import annotations

import math

from ..math_text import pl_num, shuffle_abcd
from ..models import DiagramSpec
from .base import register_template


@register_template(
    template_id="wspolrzedne_srodek_odcinka_abcd",
    topic_id="uklad_wspolrzednych",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – CKE Maj 2022 zad. 12",
)
def gen_srodek_odcinka_abcd(rng):
    ax = rng.randint(-7, 2)
    ay = rng.randint(-5, 6)
    sx = rng.randint(-1, 5)
    sy = rng.randint(-3, 4)
    if ax == sx and ay == sy:
        sx += 2

    bx = 2 * sx - ax
    by = 2 * sy - ay

    corr = f"$B = ({pl_num(bx)},\\; {pl_num(by)})$"
    # Typowy błąd ucznia: policzenie środka między A i S zamiast drugiego końca albo odjęcie odwrotne!
    mx_str = pl_num((ax + sx) / 2)
    my_str = pl_num((ay + sy) / 2)
    d1 = f"$B = ({mx_str},\\; {my_str})$"
    d2 = f"$B = ({pl_num(2 * ax - sx)},\\; {pl_num(2 * ay - sy)})$"
    d3 = f"$B = ({pl_num(bx)},\\; {pl_num(-by if by != 0 else by + 2)})$"

    choices, ans = shuffle_abcd(rng, corr, [d1, d2, d3])

    stem = (
        f"W układzie współrzędnych dany jest odcinek $AB$, którego jednym końcem jest punkt "
        f"$A = ({pl_num(ax)},\\; {pl_num(ay)})$, natomiast środkiem tego odcinka jest punkt "
        f"$S = ({pl_num(sx)},\\; {pl_num(sy)})$."
    )
    command = "Jakie współrzędne ma punkt $B$? Wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Ze wzoru na współrzędne środka odcinka mamy: $\\frac{{{ax} + x_B}}{{2}} = {sx}$ oraz $\\frac{{{ay} + y_B}}{{2}} = {sy}$.",
            f"Stąd $x_B = 2 \\cdot ({pl_num(sx)}) - ({pl_num(ax)}) = {pl_num(bx)}$ oraz "
            f"$y_B = 2 \\cdot ({pl_num(sy)}) - ({pl_num(ay)}) = {pl_num(by)}$.",
            f"Zatem {corr} (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="wspolrzedne_rownoleglobok_pf",
    topic_id="uklad_wspolrzednych",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – CKE Maj 2023 zad. 11",
    has_diagram=True,
)
def gen_rownoleglobok_pf(rng):
    # Równoległobok ABCD z podstawą poziomą AB: A=(-3,-2), B=(2,-2), D=(-1,2) -> C=(4,2)
    ax_v = rng.choice([-4, -3])
    ay_v = rng.choice([-3, -2])
    base_len = rng.choice([4, 5])
    bx_v, by_v = ax_v + base_len, ay_v
    shift_x = rng.choice([1, 2])
    h_val = rng.choice([3, 4])
    dx_v, dy_v = ax_v + shift_x, ay_v + h_val
    cx_v, cy_v = bx_v + shift_x, by_v + h_val
    area = base_len * h_val

    s1_true = rng.choice([True, False])
    shown_cx = cx_v if s1_true else (bx_v - shift_x)

    s2_true = rng.choice([True, False])
    shown_area = area if s2_true else (area // 2)

    diag = DiagramSpec(
        kind="coord_plane",
        params={
            "limit": 6,
            "segments": [[[ax_v, ay_v], [bx_v, by_v]], [[ax_v, ay_v], [dx_v, dy_v]]],
            "points": [
                {"x": ax_v, "y": ay_v, "label": "A", "dx": -0.35, "dy": -0.38},
                {"x": bx_v, "y": by_v, "label": "B", "dx": 0.35, "dy": -0.38},
                {"x": dx_v, "y": dy_v, "label": "D", "dx": -0.35, "dy": 0.38},
            ],
        },
        caption="Rysunek pomocniczy",
        width_mm=68.0,
    )

    stem = (
        f"W układzie współrzędnych zaznaczono trzy kolejne wierzchołki równoległoboku $ABCD$: "
        f"$A = ({pl_num(ax_v)},\\; {pl_num(ay_v)})$, $B = ({pl_num(bx_v)},\\; {pl_num(by_v)})$ oraz "
        f"$D = ({pl_num(dx_v)},\\; {pl_num(dy_v)})$ (zobacz rysunek)."
    )
    command = "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe."

    st1 = f"Wierzchołek $C$ tego równoległoboku ma współrzędne $({pl_num(shown_cx)},\\; {pl_num(cy_v)})$."
    st2 = f"Pole równoległoboku $ABCD$ jest równe ${shown_area}$."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": [
            f"Przesunięcie z punktu $A$ do $D$ to o ${shift_x}$ w prawo i o ${h_val}$ w górę. Takie samo przesunięcie z punktu $B$ daje "
            f"$C = ({pl_num(bx_v)} + {shift_x},\\; {pl_num(by_v)} + {h_val}) = ({pl_num(cx_v)},\\; {pl_num(cy_v)})$ -> zdanie pierwsze: **{p1}**.",
            f"Podstawa $|AB| = {base_len}$, a wysokość opuszczona na prostą $AB$ wynosi $h = {h_val}$, więc pole $P = {base_len} \\cdot {h_val} = {area}$ -> zdanie drugie: **{p2}**.",
        ],
    }


@register_template(
    template_id="wspolrzedne_odleglosc_ab_cd",
    topic_id="uklad_wspolrzednych",
    subtype="ab_cd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – CKE Czerwiec 2022 zad. 11",
)
def gen_wspolrzedne_ab_cd(rng):
    # Odległość między dwoma punktami z Pitagorasa (trójka pitagorejska 3-4-5 lub 6-8-10 lub 5-12-13)
    dx, dy, hyp = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13)])
    x1, y1 = rng.randint(-4, 1), rng.randint(-3, 2)
    x2, y2 = x1 + dx, y1 - dy

    corr1 = f"${hyp}$"
    wrong1 = f"${dx + dy}$"
    if rng.choice([True, False]):
        opts1 = {"A": corr1, "B": wrong1}
        c1 = "A"
    else:
        opts1 = {"A": wrong1, "B": corr1}
        c1 = "B"

    # Odległość punktu P=(x2, y2) od osi Ox to |y2|
    if abs(x2) == abs(y2):
        x2 += 1
        corr1 = rf"$\sqrt{{{(x2 - x1) ** 2 + (y2 - y1) ** 2}}}$"
        opts1[c1] = corr1

    corr2 = f"${abs(y2)}$"
    wrong2 = f"${abs(x2)}$"
    if rng.choice([True, False]):
        opts2 = {"C": corr2, "D": wrong2}
        c2 = "C"
    else:
        opts2 = {"C": wrong2, "D": corr2}
        c2 = "D"

    stem = f"W układzie współrzędnych dane są punkty $K = ({pl_num(x1)},\\; {pl_num(y1)})$ oraz $L = ({pl_num(x2)},\\; {pl_num(y2)})$."
    command = "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D."

    parts = [
        {"prefix": "Długość odcinka $KL$ jest równa", "suffix": ".", "options": opts1},
        {"prefix": "Odległość punktu $L$ od osi $Ox$ jest równa", "suffix": ".", "options": opts2},
    ]

    return {
        "stem": stem,
        "command": command,
        "ab_cd_parts": parts,
        "correct_answer": c1 + c2,
        "solution_steps": [
            f"Różnice współrzędnych wynoszą $|x_L - x_K| = {abs(x2 - x1)}$ oraz $|y_L - y_K| = {abs(y2 - y1)}$. "
            f"Z twierdzenia Pitagorasa $|KL| = {corr1}$ (wybór **{c1}**).",
            f"Odległość punktu $L = ({pl_num(x2)},\\; {pl_num(y2)})$ od osi $Ox$ jest równa wartości bezwzględnej rzędnej: $|{pl_num(y2)}| = {abs(y2)}$ (wybór **{c2}**).",
        ],
    }


@register_template(
    template_id="wspolrzedne_pole_trojkata_2pkt",
    topic_id="uklad_wspolrzednych",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – CKE Maj 2020 zad. 17",
    has_diagram=True,
)
def gen_pole_trojkata_uklad_2pkt(rng):
    # Trójkąt ukośny wpisany w prostokąt w układzie współrzędnych (klasyczna metoda prostokąta CKE!)
    ax_v, ay_v = -3, -2
    bx_v, by_v = rng.choice([(4, -1), (3, -1), (4, 0)])
    cx_v, cy_v = rng.choice([(-1, 4), (0, 4), (-2, 3)])

    # Pole z wyznacznika / prostokąta otaczającego (zawsze wielokrotność 0.5)
    xmin, xmax = min(ax_v, bx_v, cx_v), max(ax_v, bx_v, cx_v)
    ymin, ymax = min(ay_v, by_v, cy_v), max(ay_v, by_v, cy_v)
    rect_area = (xmax - xmin) * (ymax - ymin)

    # Pola trzech trójkątów prostokątnych narożnych lub dokładny wzór:
    area2 = abs(ax_v * (by_v - cy_v) + bx_v * (cy_v - ay_v) + cx_v * (ay_v - by_v))
    area = area2 / 2.0

    diag = DiagramSpec(
        kind="coord_plane",
        params={
            "limit": 5,
            "polygon": [[ax_v, ay_v], [bx_v, by_v], [cx_v, cy_v]],
            "points": [
                {"x": ax_v, "y": ay_v, "label": "A", "dx": -0.38, "dy": -0.35},
                {"x": bx_v, "y": by_v, "label": "B", "dx": 0.38, "dy": -0.25},
                {"x": cx_v, "y": cy_v, "label": "C", "dx": 0.0, "dy": 0.42},
            ],
        },
        width_mm=68.0,
    )

    stem = (
        f"W układzie współrzędnych na płaszczyźnie narysowano trójkąt $ABC$ o wierzchołkach "
        f"$A = ({pl_num(ax_v)},\\; {pl_num(ay_v)})$, $B = ({pl_num(bx_v)},\\; {pl_num(by_v)})$ oraz "
        f"$C = ({pl_num(cx_v)},\\; {pl_num(cy_v)})$."
    )
    command = "Oblicz pole trójkąta $ABC$. Zapisz obliczenia."

    t1 = abs((bx_v - ax_v) * (by_v - ay_v)) / 2.0
    t2 = abs((xmax - cx_v) * (cy_v - by_v)) / 2.0
    t3 = abs((cx_v - ax_v) * (cy_v - ay_v)) / 2.0

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "correct_answer": pl_num(area),
        "solution_steps": [
            f"Wpisujemy trójkąt $ABC$ w prostokąt o bokach równoległych do osi układu współrzędnych, "
            f"o wymiarach ${xmax - xmin} \\times {ymax - ymin}$ i polu $P_{{\\text{{prost}}}} = {xmax - xmin} \\cdot {ymax - ymin} = {rect_area}$.",
            f"Obliczamy pola trzech trójkątów prostokątnych dopełniających trójkąt $ABC$ do tego prostokąta: "
            f"$P_1 = {pl_num(t1)}$, $P_2 = {pl_num(t2)}$, $P_3 = {pl_num(t3)}$.",
            f"Odejmujemy ich pola od pola prostokąta: $P_{{ABC}} = {rect_area} - ({pl_num(t1)} + {pl_num(t2)} + {pl_num(t3)}) = {pl_num(area)}$.",
            f"**Odpowiedź:** Pole trójkąta $ABC$ jest równe ${pl_num(area)}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – zastosowanie poprawnej metody (np. obliczenie pola prostokąta otaczającego = {rect_area} oraz pól trójkątów prostokątnych).",
            f"2 pkt – bezbłędne dokończenie rachunków i podanie wyniku: {pl_num(area)}.",
        ],
        "grid_height_mm": 54.0,
    }


@register_template(
    template_id="wspolrzedne_trapez_obwod_3pkt",
    topic_id="uklad_wspolrzednych",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – CKE Czerwiec 2024 zad. 18",
    has_diagram=True,
)
def gen_trapez_uklad_3pkt(rng):
    # Trapez równoramienny ABCD w układzie współrzędnych o podstawach poziomych i ramionach z trójki 3-4-5!
    # np. A=(-4,-2), B=(4,-2) (a=8), D=(-1,2), C=(1,2) (b=2): dx=3, h=4 -> ramię c=5!
    half_b = rng.choice([1, 2])
    dx, h, arm = (3, 4, 5)
    half_a = half_b + dx  # 4 lub 5
    y_bot = -2
    y_top = y_bot + h     # 2

    A = (-half_a, y_bot)
    B = (half_a, y_bot)
    C = (half_b, y_top)
    D = (-half_b, y_top)

    a_len = 2 * half_a
    b_len = 2 * half_b
    area = (a_len + b_len) * h // 2
    perim = a_len + b_len + 2 * arm

    diag = DiagramSpec(
        kind="coord_plane",
        params={
            "limit": 6,
            "polygon": [list(A), list(B), list(C), list(D)],
            "points": [
                {"x": A[0], "y": A[1], "label": "A", "dx": -0.35, "dy": -0.38},
                {"x": B[0], "y": B[1], "label": "B", "dx": 0.35, "dy": -0.38},
                {"x": C[0], "y": C[1], "label": "C", "dx": 0.35, "dy": 0.35},
                {"x": D[0], "y": D[1], "label": "D", "dx": -0.35, "dy": 0.35},
            ],
        },
        width_mm=68.0,
    )

    stem = (
        f"W układzie współrzędnych dany jest trapez $ABCD$ o wierzchołkach: "
        f"$A = ({pl_num(A[0])},\\; {pl_num(A[1])})$, $B = ({pl_num(B[0])},\\; {pl_num(B[1])})$, "
        f"$C = ({pl_num(C[0])},\\; {pl_num(C[1])})$ oraz $D = ({pl_num(D[0])},\\; {pl_num(D[1])})$."
    )
    command = "Oblicz pole oraz obwód trapezu $ABCD$. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "correct_answer": f"Pole = {area}, obwód = {perim}",
        "solution_steps": [
            f"Odcinki $AB$ i $DC$ są równoległe do osi $Ox$. Ich długości wynoszą: $|AB| = {B[0]} - ({pl_num(A[0])}) = {a_len}$ "
            f"oraz $|DC| = {C[0]} - ({pl_num(D[0])}) = {b_len}$. Wysokość trapezu wynosi $h = {y_top} - ({pl_num(y_bot)}) = {h}$.",
            f"Obliczamy pole trapezu: $P = \\frac{{({a_len} + {b_len}) \\cdot {h}}}{{2}} = {area}$.",
            f"Długość ramienia $AD$ (i równego mu ramienia $BC$) obliczamy z twierdzenia Pitagorasa: "
            f"$|AD| = \\sqrt{{{dx}^2 + {h}^2}} = \\sqrt{{9 + 16}} = {arm}$.",
            f"Obwód trapezu wynosi: $Obw = {a_len} + {b_len} + 2 \\cdot {arm} = {perim}$.",
            f"**Odpowiedź:** Pole trapezu jest równe ${area}$, a jego obwód wynosi ${perim}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyznaczenie długości podstaw ({a_len} i {b_len}), wysokości ({h}) oraz obliczenie pola trapezu ({area}).",
            f"2 pkt – zastosowanie twierdzenia Pitagorasa i wyznaczenie długości ramienia trapezu ({arm}).",
            f"3 pkt – obliczenie obwodu trapezu ({perim}) i podanie obu odpowiedzi.",
        ],
        "grid_height_mm": 64.0,
    }
