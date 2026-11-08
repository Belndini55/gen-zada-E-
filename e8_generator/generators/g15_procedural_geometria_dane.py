"""Pakiet 32 autorskich generatorów proceduralnych (działy 8–12: układ współrzędnych, planimetria, bryły, statystyka, prawdopodobieństwo).

Zapewnia bogaty zasób różnorodnych zadań zamkniętych oraz otwartych (0–2 pkt i 0–3 pkt)
w działach o największej wadze na Egzaminie Ósmoklasisty (szczególnie geometrii płaskiej i przestrzennej).
"""

from __future__ import annotations

import math
from fractions import Fraction

from ..math_text import frac_tex, pl_num, shuffle_abcd
from ..models import DiagramSpec
from .base import register_template


# ===========================================================================
# 8. UKŁAD WSPÓŁRZĘDNYCH (5 nowych generatorów)
# ===========================================================================

@register_template(
    template_id="proc_wspolrzedne_symetria_osie_pf",
    topic_id="uklad_wspolrzednych",
    subtype="pf",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – ćwiartki układu i odbicie względem osi",
)
def gen_proc_symetria_osie_pf(rng):
    x0 = rng.choice([-7, -5, -4, 3, 6, 8])
    y0 = rng.choice([-6, -3, 2, 5, 9])
    # Symetria względem osi Ox zmienia znak y: (x0, -y0); względem początku układu: (-x0, -y0)
    s1_true = rng.choice([True, False])
    p_ox = (x0, -y0) if s1_true else (-x0, y0)

    s2_true = rng.choice([True, False])
    p_orig = (-x0, -y0) if s2_true else (-x0, y0)

    a1, a2 = ("P" if s1_true else "F"), ("P" if s2_true else "F")
    return {
        "stem": f"W układzie współrzędnych $(x, y)$ dany jest punkt $P = ({pl_num(x0)},\\; {pl_num(y0)})$.",
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Punktem symetrycznym do punktu $P$ względem osi $Ox$ jest punkt $({pl_num(p_ox[0])},\\; {pl_num(p_ox[1])})$.", a1),
            (f"Punktem symetrycznym do punktu $P$ względem początku układu współrzędnych $(0, 0)$ jest punkt $({pl_num(p_orig[0])},\\; {pl_num(p_orig[1])})$.", a2),
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Symetria względem osi $Ox$ zachowuje odciętą $x$ i zmienia znak rzędnej $y$: $({pl_num(x0)},\\; {pl_num(-y0)})$ (**{a1}**).",
            f"Symetria względem punktu $(0, 0)$ zmienia znaki obu współrzędnych: $({pl_num(-x0)},\\; {pl_num(-y0)})$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_wspolrzedne_drugi_koniec_ze_srodka_abcd",
    topic_id="uklad_wspolrzednych",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – wyznaczanie końca odcinka na podstawie środka",
)
def gen_proc_koniec_odcinka(rng):
    ax, ay = rng.randint(-6, 4), rng.randint(-5, 5)
    sx, sy = rng.randint(-2, 6), rng.randint(-3, 6)
    while (ax, ay) == (sx, sy):
        sx += 2
    bx, by = 2 * sx - ax, 2 * sy - ay

    corr = f"$({pl_num(bx)},\\; {pl_num(by)})$"
    w1 = f"$({pl_num((ax + sx) / 2)},\\; {pl_num((ay + sy) / 2)})$"
    w2 = f"$({pl_num(2 * ax - sx)},\\; {pl_num(2 * ay - sy)})$"
    w3 = f"$({pl_num(bx)},\\; {pl_num(-by if by != 0 else by + 2)})$"
    choices, ans = shuffle_abcd(rng, corr, [w1, w2, w3])

    return {
        "stem": (
            f"Punkt $S = ({pl_num(sx)},\\; {pl_num(sy)})$ jest środkiem odcinka $AB$, "
            f"którego początkiem jest punkt $A = ({pl_num(ax)},\\; {pl_num(ay)})$."
        ),
        "command": "Jakie współrzędne ma punkt $B$? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Ze wzoru na środek odcinka: $\\frac{{{ax} + x_B}}{{2}} = {sx} \\Rightarrow x_B = {2 * sx} - ({ax}) = {bx}$.",
            f"Analogicznie: $\\frac{{{ay} + y_B}}{{2}} = {sy} \\Rightarrow y_B = {2 * sy} - ({ay}) = {by}$, stąd $B = {corr}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_wspolrzedne_kwadrat_przekatna_2pkt",
    topic_id="uklad_wspolrzednych",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – pole kwadratu o wierzchołkach w układzie współrzędnych",
)
def gen_proc_kwadrat_uklad_2pkt(rng):
    # Przekątna AC lub bok AB kwadratu -> pole kwadratu P = |AB|^2 albo P = |AC|^2 / 2!
    use_diag = rng.choice([True, False])
    ax, ay = rng.randint(-4, 1), rng.randint(-4, 1)
    if not use_diag:
        dx, dy = rng.choice([(3, 4), (4, 3), (5, 2), (2, 6), (4, 5)])
        bx, by = ax + dx, ay + dy
        d_sq = dx * dx + dy * dy
        return {
            "stem": (
                f"Punkty $A = ({pl_num(ax)},\\; {pl_num(ay)})$ oraz $B = ({pl_num(bx)},\\; {pl_num(by)})$ "
                f"są sąsiednimi wierzchołkami kwadratu $ABCD$ w układzie współrzędnych."
            ),
            "command": "Oblicz pole kwadratu $ABCD$. Zapisz obliczenia.",
            "correct_answer": f"{d_sq}",
            "solution_steps": [
                f"Obliczamy kwadrat długości boku $AB$ z twierdzenia Pitagorasa: $|AB|^2 = ({bx} - ({ax}))^2 + ({by} - ({ay}))^2 = {dx}^2 + {dy}^2 = {d_sq}$.",
                f"Pole kwadratu o boku $|AB|$ jest równe $P = |AB|^2 = {d_sq}$.",
            ],
            "scoring_scheme": [
                f"1 pkt – poprawne zapisanie wyrażenia na długość lub kwadrat długości odcinka AB.",
                f"2 pkt – obliczenie pola kwadratu: {d_sq}.",
            ],
            "grid_height_mm": 48.0,
        }

    # Przekątna AC: wybieramy dx, dy tej samej parzystości, aby d_sq/2 było całkowite!
    dx, dy = rng.choice([(4, 2), (6, 2), (4, 6), (6, 4), (8, 2)])
    cx, cy = ax + dx, ay + dy
    d_sq = dx * dx + dy * dy
    area = d_sq // 2
    return {
        "stem": (
            f"Punkty $A = ({pl_num(ax)},\\; {pl_num(ay)})$ oraz $C = ({pl_num(cx)},\\; {pl_num(cy)})$ "
            f"są przeciwległymi wierzchołkami kwadratu $ABCD$ w układzie współrzędnych."
        ),
        "command": "Oblicz pole kwadratu $ABCD$. Zapisz obliczenia.",
        "correct_answer": f"{area}",
        "solution_steps": [
            f"Odcinek $AC$ jest przekątną kwadratu. Z twierdzenia Pitagorasa: $|AC|^2 = {dx}^2 + {dy}^2 = {d_sq}$.",
            f"Pole kwadratu wyrażone przez przekątną wynosi $P = \\frac{{|AC|^2}}{{2}} = \\frac{{{d_sq}}}{{2}} = {area}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyznaczenie długości lub kwadratu długości przekątnej AC ({d_sq}).",
            f"2 pkt – poprawne obliczenie pola kwadratu: {area}.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_wspolrzedne_trojkat_prostokatny_3pkt",
    topic_id="uklad_wspolrzednych",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – obwód i pole trójkąta w układzie współrzędnych",
    has_diagram=True,
)
def gen_proc_trojkat_obwod_uklad_3pkt(rng):
    # Trójkąt prostokątny o przyprostokątnych równoległych do osi i przeciwprostokątnej z trójki pitagorejskiej
    leg_x, leg_y, hyp = rng.choice([(3, 4, 5), (6, 8, 10), (8, 6, 10), (5, 12, 13)])
    lim = 6 if max(leg_x, leg_y) <= 8 else 8
    ax = -leg_x // 2
    ay = -leg_y // 2
    bx = ax + leg_x
    by = ay
    cx = ax
    cy = ay + leg_y
    obw = leg_x + leg_y + hyp
    area = (leg_x * leg_y) // 2

    poly = [[ax, ay], [bx, by], [cx, cy]]
    pts = [
        {"x": ax, "y": ay, "label": "A", "dx": -0.45, "dy": -0.45},
        {"x": bx, "y": by, "label": "B", "dx": 0.4, "dy": -0.45},
        {"x": cx, "y": cy, "label": "C", "dx": -0.45, "dy": 0.4},
    ]

    return {
        "stem": (
            f"W układzie współrzędnych $(x, y)$ narysowano trójkąt $ABC$ o wierzchołkach: "
            f"$A = ({pl_num(ax)},\\; {pl_num(ay)})$, $B = ({pl_num(bx)},\\; {pl_num(by)})$ oraz $C = ({pl_num(cx)},\\; {pl_num(cy)})$."
        ),
        "diagram": DiagramSpec(kind="coord_plane", params={"limit": lim, "polygon": poly, "points": pts}, width_mm=72.0),
        "command": "Oblicz obwód oraz pole trójkąta $ABC$. Zapisz obliczenia.",
        "correct_answer": f"Obwód = {obw}, Pole = {area}",
        "solution_steps": [
            f"Odcinki $AB$ i $AC$ są równoległe do osi układu, więc $\\angle BAC = 90^\\circ$, $|AB| = {leg_x}$ oraz $|AC| = {leg_y}$.",
            f"Z twierdzenia Pitagorasa: $|BC| = \\sqrt{{{leg_x}^2 + {leg_y}^2}} = \\sqrt{{{hyp**2}}} = {hyp}$.",
            f"Obwód wynosi ${leg_x} + {leg_y} + {hyp} = {obw}$, a pole $P = \\frac{{1}}{{2}} \\cdot {leg_x} \\cdot {leg_y} = {area}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyznaczenie długości przyprostokątnych ({leg_x} i {leg_y}).",
            f"2 pkt – obliczenie przeciwprostokątnej ({hyp}) lub pola trójkąta ({area}).",
            f"3 pkt – podanie poprawnego obwodu ({obw}) oraz pola ({area}).",
        ],
        "grid_height_mm": 58.0,
    }


@register_template(
    template_id="proc_wspolrzedne_wspoliniowosc_uzasadnienie",
    topic_id="uklad_wspolrzednych",
    subtype="uzasadnienie",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – położenie punktów na prostej w układzie współrzędnych",
)
def gen_proc_punkt_na_osiach_uzasadnienie(rng):
    # Czy trójkąt o wierzchołkach A=(-a,0), B=(a,0), C=(0,h) jest równoboczny? Nie, bo a != h/sqrt(3) (całkowite współrzędne kratowe!)
    # Albo: Czy punkt C należy do symetralnej odcinka AB / czy |PA| == |PB|!
    a = rng.choice([3, 4, 5])
    # P = (0, yP), A = (-a, 0), B = (a, 0) -> |PA| == |PB| (Tak), vs A = (-a, 0), B = (a+2, 0) -> |PA| != |PB| (Nie)
    is_equal = rng.choice([True, False])
    yp = rng.choice([4, 6, 8])
    bx = a if is_equal else a + 2
    pa_sq = a * a + yp * yp
    pb_sq = bx * bx + yp * yp

    ans_ab = "A" if is_equal else "B"
    r_good = (
        f"$|PA|^2 = {pa_sq}$ oraz $|PB|^2 = {pb_sq}$, czyli odcinki $PA$ i $PB$ {'mają równe długości' if is_equal else 'mają różne długości'}."
    )
    r_bad1 = f"punkt $P$ leży na osi $Oy$, więc zawsze tworzy z punktami na osi $Ox$ trójkąt równoboczny."
    r_bad2 = f"suma współrzędnych punktu $A$ i punktu $B$ jest liczbą parzystą."
    r_list = [(r_good, True), (r_bad1, False), (r_bad2, False)]
    rng.shuffle(r_list)
    reasons = {str(i + 1): t for i, (t, _) in enumerate(r_list)}
    good_idx = next(str(i + 1) for i, (_, ok) in enumerate(r_list) if ok)

    rel_sym = "=" if is_equal else r"\neq"
    return {
        "stem": (
            f"W układzie współrzędnych $(x, y)$ dane są trzy punkty: "
            f"$A = (−{a},\\; 0)$, $B = ({bx},\\; 0)$ oraz $P = (0,\\; {yp})$."
        ),
        "command": (
            "Czy trójkąt $ABP$ jest równoramienny o podstawie $AB$ (czyli $|PA| = |PB|$)? "
            "Wybierz odpowiedź A (Tak) albo B (Nie) i jej uzasadnienie spośród 1., 2. albo 3."
        ),
        "justification_data": {
            "prefix_a": "Tak,",
            "prefix_b": "Nie,",
            "conjunction": "ponieważ",
            "reasons": reasons,
        },
        "correct_answer": f"{ans_ab}{good_idx}",
        "solution_steps": [
            f"Z twierdzenia Pitagorasa: $|PA|^2 = {a}^2 + {yp}^2 = {pa_sq}$ oraz $|PB|^2 = {bx}^2 + {yp}^2 = {pb_sq}$.",
            f"Ponieważ $|PA|^2 {rel_sym} |PB|^2$, poprawna odpowiedź to **{ans_ab}{good_idx}**.",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź wraz z uzasadnieniem.", "0 pkt – pozostałe przypadki."],
    }


# ===========================================================================
# 9. GEOMETRIA PŁASKA (9 nowych generatorów!)
# ===========================================================================

@register_template(
    template_id="proc_planimetria_katy_trojkata_stosunek_abcd",
    topic_id="geometria_plaska",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – miary kątów wewnętrznych trójkąta i czworokąta",
)
def gen_proc_katy_stosunek(rng):
    r1, r2, r3 = rng.choice([
        (2, 3, 4),
        (1, 2, 3),
        (2, 5, 5),
        (3, 4, 5),
        (1, 3, 5),
        (3, 5, 10),
    ])
    unit = 180 // (r1 + r2 + r3)
    angles = [r1 * unit, r2 * unit, r3 * unit]
    ask_max = rng.choice([True, False])
    target = max(angles) if ask_max else min(angles)
    word = "największego" if ask_max else "najmniejszego"

    wrongs = [f"${a}^\\circ$" for a in angles if a != target]
    wrongs.extend([f"${unit}^\\circ$", f"${180 - target}^\\circ$", f"${target + 15}^\\circ$"])
    choices, ans = shuffle_abcd(rng, f"${target}^\\circ$", wrongs)

    return {
        "stem": f"Miary trzech kątów wewnętrznych pewnego trójkąta pozostają w stosunku ${r1} : {r2} : {r3}$.",
        "command": f"Jaka jest miara {word} kąta wewnętrznego tego trójkąta? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Suma kątów w trójkącie wynosi $180^\\circ$: ${r1}\\alpha + {r2}\\alpha + {r3}\\alpha = 180^\\circ \\Rightarrow {r1+r2+r3}\\alpha = 180^\\circ \\Rightarrow \\alpha = {unit}^\\circ$.",
            f"Kąty mają miary ${angles[0]}^\\circ, {angles[1]}^\\circ, {angles[2]}^\\circ$, więc miara {word} kąta to ${target}^\\circ$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_planimetria_rownoleglobok_katy_ab_cd",
    topic_id="geometria_plaska",
    subtype="ab_cd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – kąty i obwód równoległoboku",
)
def gen_proc_rownoleglobok_ab_cd(rng):
    diff_deg = rng.choice([24, 32, 40, 48, 56, 64])
    acute = (180 - diff_deg) // 2
    obtuse = acute + diff_deg
    side_a = rng.randint(7, 15)
    side_b = side_a + rng.randint(3, 8)
    obw = 2 * (side_a + side_b)

    if rng.random() < 0.5:
        opts1, a1 = {"A": f"${obtuse}^\\circ$", "B": f"${90 + diff_deg // 2}^\\circ$"}, "A"
    else:
        opts1, a1 = {"A": f"${90 + diff_deg // 2}^\\circ$", "B": f"${obtuse}^\\circ$"}, "B"

    if rng.random() < 0.5:
        opts2, a2 = {"C": f"${side_b}$ cm", "D": f"${obw - side_a}$ cm"}, "C"
    else:
        opts2, a2 = {"C": f"${obw - side_a}$ cm", "D": f"${side_b}$ cm"}, "D"

    return {
        "stem": (
            f"W równoległoboku $ABCD$ kąt rozwarty ma miarę o ${diff_deg}^\\circ$ większą od miary kąta ostrego. "
            f"Obwód tego równoległoboku jest równy ${obw}$ cm, a krótszy bok ma długość ${side_a}$ cm."
        ),
        "command": "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D.",
        "ab_cd_parts": [
            {"prefix": "Miara kąta rozwartego tego równoległoboku jest równa", "suffix": ".", "options": opts1},
            {"prefix": "Długość dłuższego boku tego równoległoboku wynosi", "suffix": ".", "options": opts2},
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Suma sąsiednich kątów w równoległoboku to $180^\\circ$: $\\alpha + (\\alpha + {diff_deg}^\\circ) = 180^\\circ \\Rightarrow \\alpha = {acute}^\\circ$, a kąt rozwarty ma ${obtuse}^\\circ$ (**{a1}**).",
            f"Z obwodu $2({side_a} + b) = {obw}$ wyznaczamy dłuższy bok $b = {obw // 2} - {side_a} = {side_b}\\text{{ cm}}$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna para odpowiedzi.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_planimetria_warunek_trojkata_pf",
    topic_id="geometria_plaska",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – nierówność trójkąta i twierdzenie odwrotne do Pitagorasa",
)
def gen_proc_warunek_trojkata_pf(rng):
    a, b = rng.choice([(5, 9), (6, 11), (7, 12), (8, 13)])
    s1_true = rng.choice([True, False])
    c_cand = (a + b - 2) if s1_true else (a + b + rng.choice([0, 2]))

    p1, p2, p3_true = rng.choice([(6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17)])
    s2_true = rng.choice([True, False])
    p3 = p3_true if s2_true else p3_true + 1

    a1, a2 = ("P" if s1_true else "F"), ("P" if s2_true else "F")
    return {
        "stem": "Przeanalizuj poniższe zdania dotyczące budowania trójkątów z danych odcinków.",
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Z trzech odcinków o długościach ${a}$ cm, ${b}$ cm oraz ${c_cand}$ cm można zbudować trójkąt.", a1),
            (f"Trójkąt o bokach długości ${p1}$ cm, ${p2}$ cm oraz ${p3}$ cm jest trójkątem prostokątnym.", a2),
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Suma dwóch krótszych boków wynosi ${a} + {b} = {a + b}$ cm, a trzeci bok ma ${c_cand}$ cm; warunek ${a} + {b} > {c_cand}$ jest {'spełniony' if s1_true else 'niespełniony'} (**{a1}**).",
            f"Sprawdzamy równanie Pitagorasa: ${p1}^2 + {p2}^2 = {p1**2 + p2**2}$, a ${p3}^2 = {p3**2}$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_planimetria_sciezka_wokol_trawnika_2pkt",
    topic_id="geometria_plaska",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – pole ramki / alejki wokół prostokątnego placu",
)
def gen_proc_ramka_sciezka_2pkt(rng):
    w_in = rng.randint(8, 16)
    l_in = w_in + rng.randint(4, 10)
    d = rng.choice([1, 2, 3])
    w_out = w_in + 2 * d
    l_out = l_in + 2 * d
    area_in = w_in * l_in
    area_out = w_out * l_out
    area_path = area_out - area_in

    place = rng.choice([
        ("prostokątnego basenu", "drewniany pomost", "pomostu"),
        ("prostokątnej rabaty kwiatowej", "wybrukowaną alejkę", "alejki"),
        ("prostokątnego boiska", "pas bezpieczeństwa ze sztucznej trawy", "pasa bezpieczeństwa"),
    ])
    return {
        "stem": (
            f"Wokół {place[0]} o wymiarach ${l_in}\\text{{ m}} \\times {w_in}\\text{{ m}}$ wykonano dookoła {place[1]} "
            f"o stałej szerokości równej ${d}$ m (z każdej strony)."
        ),
        "command": f"Oblicz pole powierzchni samego {place[2]}. Zapisz obliczenia.",
        "correct_answer": f"{area_path} m^2",
        "solution_steps": [
            f"Zewnętrzny prostokąt wraz z obramowaniem ma wymiary $({l_in} + 2 \\cdot {d})\\text{{ m}} \\times ({w_in} + 2 \\cdot {d})\\text{{ m}} = {l_out}\\text{{ m}} \\times {w_out}\\text{{ m}}$.",
            f"Pole samego {place[2]} jest różnicą pól: ${l_out} \\cdot {w_out} - {l_in} \\cdot {w_in} = {area_out} - {area_in} = {area_path}\\text{{ m}}^2$.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne wyznaczenie zewnętrznych wymiarów ({l_out} m i {w_out} m).",
            f"2 pkt – obliczenie pola samego obramowania: {area_path} m^2.",
        ],
        "grid_height_mm": 52.0,
    }


@register_template(
    template_id="proc_planimetria_drabina_pitagoras_2pkt",
    topic_id="geometria_plaska",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – praktyczne zastosowanie twierdzenia Pitagorasa",
)
def gen_proc_drabina_maszt_2pkt(rng):
    ctx = rng.choice(["ladder", "rope_mast", "tv_screen"])
    leg1, leg2, hyp = rng.choice([(6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17), (12, 16, 20)])
    if ctx == "ladder":
        # Drabina w decymetrach lub z ułamkiem dziesiętnym (np. 1,5 m; 2,0 m; 2,5 m lub w metrach)
        scale = rng.choice([0.5, 1])
        a, b, c = leg1 * scale, leg2 * scale, hyp * scale
        return {
            "stem": (
                f"Prosta drabina o długości ${pl_num(c)}$ m została oparta o pionową ścianę budynku na płaskim, "
                f"poziomym podłożu. Dolny koniec drabiny znajduje się w odległości ${pl_num(a)}$ m od podstawy ściany."
            ),
            "command": "Na jakiej wysokości nad podłożem górny koniec tej drabiny dotyka ściany? Zapisz obliczenia.",
            "correct_answer": f"{pl_num(b)} m",
            "solution_steps": [
                f"Ściana, podłoże i drabina tworzą trójkąt prostokątny o przeciwprostokątnej ${pl_num(c)}$ m i przyprostokątnej ${pl_num(a)}$ m.",
                f"Z twierdzenia Pitagorasa: $h^2 = ({pl_num(c)})^2 - ({pl_num(a)})^2 = {pl_num(c*c)} - {pl_num(a*a)} = {pl_num(b*b)}$, skąd $h = {pl_num(b)}$ m.",
            ],
            "scoring_scheme": [
                "1 pkt – poprawne zapisanie równania wynikającego z twierdzenia Pitagorasa.",
                f"2 pkt – obliczenie szukanej wysokości: {pl_num(b)} m.",
            ],
            "grid_height_mm": 50.0,
        }

    if ctx == "rope_mast":
        return {
            "stem": (
                f"Do wierzchołka pionowego masztu o wysokości ${leg2}$ m przymocowano prostą linę odciągową "
                f"i zakotwiczono ją w poziomym gruncie w odległości ${leg1}$ m od podstawy masztu."
            ),
            "command": "Oblicz długość napiętej liny (pomiń długość węzłów). Zapisz obliczenia.",
            "correct_answer": f"{hyp} m",
            "solution_steps": [
                f"Maszt i odcinek na ziemi są przyprostokątnymi trójkąta prostokątnego o długościach ${leg2}$ m i ${leg1}$ m.",
                f"Długość liny: $d = \\sqrt{{{leg1}^2 + {leg2}^2}} = \\sqrt{{{hyp*hyp}}} = {hyp}$ m.",
            ],
            "scoring_scheme": [
                "1 pkt – zastosowanie twierdzenia Pitagorasa do masztu i odległości kotwy.",
                f"2 pkt – wyznaczenie długości liny: {hyp} m.",
            ],
            "grid_height_mm": 48.0,
        }

    return {
        "stem": (
            f"Ekran monitora ma kształt prostokąta o szerokości ${leg2 * 4}$ cm oraz przekątnej równej ${hyp * 4}$ cm."
        ),
        "command": "Oblicz wysokość oraz obwód tego ekranu. Zapisz obliczenia.",
        "correct_answer": f"wysokość {leg1 * 4} cm, obwód {2 * (leg1 + leg2) * 4} cm",
        "solution_steps": [
            f"Z twierdzenia Pitagorasa: $h^2 = ({hyp * 4})^2 - ({leg2 * 4})^2 = {(leg1 * 4)**2}$, skąd $h = {leg1 * 4}$ cm.",
            f"Obwód ekranu wynosi $2 \\cdot ({leg2 * 4} + {leg1 * 4}) = {2 * (leg1 + leg2) * 4}$ cm.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyznaczenie wysokości ekranu ({leg1 * 4} cm).",
            f"2 pkt – obliczenie obwodu ekranu ({2 * (leg1 + leg2) * 4} cm).",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_planimetria_trapez_rownoramienny_3pkt",
    topic_id="geometria_plaska",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Styl CKE – obwód i pole trapezu równoramiennego z twierdzeniem Pitagorasa",
)
def gen_proc_trapez_rownoramienny_3pkt(rng):
    # Odcinek na dłuższej podstawie: (a - b)/2 = dx, wysokość h, ramię c -> trójka pitagorejska (dx, h, c)
    dx, h, leg = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 6, 10), (9, 12, 15)])
    b_top = rng.randint(6, 16)
    a_bot = b_top + 2 * dx
    obw = a_bot + b_top + 2 * leg
    area = (a_bot + b_top) * h // 2

    given_obw = rng.choice([True, False])
    if given_obw:
        return {
            "stem": (
                f"Podstawy trapezu równoramiennego $ABCD$ mają długości $|AB| = {a_bot}$ cm oraz $|CD| = {b_top}$ cm, "
                f"a obwód tego trapezu jest równy ${obw}$ cm."
            ),
            "command": "Oblicz pole trapezu $ABCD$. Zapisz obliczenia.",
            "correct_answer": f"{area} cm^2",
            "solution_steps": [
                f"Obliczamy długość ramienia trapezu: $c = \\frac{{{obw} - ({a_bot} + {b_top})}}{{2}} = {leg}\\text{{ cm}}$.",
                f"Wysokość opuszczona z wierzchołka $D$ odcina na podstawie $AB$ odcinek $x = \\frac{{{a_bot} - {b_top}}}{{2}} = {dx}\\text{{ cm}}$. Z twierdzenia Pitagorasa: $h = \\sqrt{{{leg}^2 - {dx}^2}} = {h}\\text{{ cm}}$.",
                f"Pole trapezu: $P = \\frac{{({a_bot} + {b_top}) \\cdot {h}}}{{2}} = {area}\\text{{ cm}}^2$.",
            ],
            "scoring_scheme": [
                f"1 pkt – obliczenie długości ramienia ({leg} cm) lub odcinka ({dx} cm) na dłuższej podstawie.",
                f"2 pkt – wyznaczenie wysokości trapezu ({h} cm) z twierdzenia Pitagorasa.",
                f"3 pkt – poprawne obliczenie pola trapezu: {area} cm^2.",
            ],
            "grid_height_mm": 58.0,
        }

    return {
        "stem": (
            f"Pole trapezu równoramiennego $ABCD$ jest równe ${area}\\text{{ cm}}^2$. Podstawy tego trapezu mają długości "
            f"$|AB| = {a_bot}$ cm oraz $|CD| = {b_top}$ cm."
        ),
        "command": "Oblicz obwód trapezu $ABCD$. Zapisz obliczenia.",
        "correct_answer": f"{obw} cm",
        "solution_steps": [
            f"Ze wzoru na pole trapezu $\\frac{{({a_bot} + {b_top}) \\cdot h}}{{2}} = {area}$ obliczamy wysokość: $h = {h}\\text{{ cm}}$.",
            f"Odcinek odcięty przez wysokość na dłuższej podstawie ma długość $\\frac{{{a_bot} - {b_top}}}{{2}} = {dx}\\text{{ cm}}$. Z twierdzenia Pitagorasa ramię ma długość $c = \\sqrt{{{dx}^2 + {h}^2}} = {leg}\\text{{ cm}}$.",
            f"Obwód trapezu wynosi ${a_bot} + {b_top} + 2 \\cdot {leg} = {obw}\\text{{ cm}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyznaczenie wysokości trapezu ({h} cm) ze wzoru na pole.",
            f"2 pkt – obliczenie długości ramienia ({leg} cm) z twierdzenia Pitagorasa.",
            f"3 pkt – obliczenie obwodu trapezu: {obw} cm.",
        ],
        "grid_height_mm": 58.0,
    }


@register_template(
    template_id="proc_planimetria_wysokosci_rownolegloboku_3pkt",
    topic_id="geometria_plaska",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – dwie wysokości równoległoboku i pole",
)
def gen_proc_dwie_wysokosci_rownolegloboku(rng):
    # a * h_a = b * h_b = P, obwód = 2(a + b)
    a, h_a, b, h_b = rng.choice([
        (15, 8, 10, 12),
        (18, 6, 12, 9),
        (20, 9, 15, 12),
        (16, 9, 12, 12),
        (24, 5, 15, 8),
    ])
    obw = 2 * (a + b)
    area = a * h_a

    return {
        "stem": (
            f"Obwód równoległoboku $ABCD$ wynosi ${obw}$ cm. Dłuższy bok tego równoległoboku ma długość ${a}$ cm, "
            f"a wysokość opuszczona na **krótszy** bok ma długość ${h_b}$ cm."
        ),
        "command": "Oblicz długość wysokości opuszczonej na dłuższy bok tego równoległoboku. Zapisz obliczenia.",
        "correct_answer": f"{h_a} cm",
        "solution_steps": [
            f"Z obwodu wyznaczamy długość krótszego boku: $b = \\frac{{{obw}}}{{2}} - {a} = {b}\\text{{ cm}}$.",
            f"Obliczamy pole równoległoboku, mnożąc krótszy bok przez opuszczoną na niego wysokość: $P = {b} \\cdot {h_b} = {area}\\text{{ cm}}^2$.",
            f"Wysokość opuszczona na dłuższy bok ma długość $h_a = \\frac{{P}}{{{a}}} = \\frac{{{area}}}{{{a}}} = {h_a}\\text{{ cm}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie długości krótszego boku równoległoboku ({b} cm).",
            f"2 pkt – obliczenie pola równoległoboku ({area} cm^2).",
            f"3 pkt – wyznaczenie szukanej wysokości: {h_a} cm.",
        ],
        "grid_height_mm": 56.0,
    }


@register_template(
    template_id="proc_planimetria_trojkat_katy_dwusieczna_abcd",
    topic_id="geometria_plaska",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – kąty przyległe, wierzchołkowe i dwusieczna kąta",
)
def gen_proc_dwusieczna_trojkat(rng):
    alpha = rng.choice([36, 42, 48, 54, 64, 72])
    beta = rng.choice([40, 50, 56, 62, 68])
    while alpha + beta >= 156:
        beta -= 20
    gamma = 180 - alpha - beta
    # Dwusieczna kąta gamma dzieli go na gamma/2 (upewnij się, że gamma parzyste - alpha i beta parzyste -> tak!)
    half_g = gamma // 2
    # Kąt rozwarty między dwusieczną CD a podstawą AB w trójkącie ADC to 180 - alpha - gamma/2
    adc_ang = 180 - alpha - half_g

    choices, ans = shuffle_abcd(
        rng,
        f"${adc_ang}^\\circ$",
        [f"${gamma}^\\circ$", f"${180 - adc_ang}^\\circ$", f"${90 + half_g // 2}^\\circ$"],
    )
    return {
        "stem": (
            f"W trójkącie $ABC$ miary kątów przy boku $AB$ wynoszą $|\\angle CAB| = {alpha}^\\circ$ oraz "
            f"$|\\angle ABC| = {beta}^\\circ$. Poprowadzono dwusieczną kąta $ACB$, która przecięła bok $AB$ w punkcie $D$."
        ),
        "command": "Jaka jest miara kąta $ADC$? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Obliczamy miarę kąta $ACB$: $180^\\circ - ({alpha}^\\circ + {beta}^\\circ) = {gamma}^\\circ$. Dwusieczna dzieli go na dwa kąty po ${half_g}^\\circ$.",
            f"W trójkącie $ADC$: $|\\angle ADC| = 180^\\circ - ({alpha}^\\circ + {half_g}^\\circ) = {adc_ang}^\\circ$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_planimetria_figura_L_pole_obwod_3pkt",
    topic_id="geometria_plaska",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Styl CKE – pole i obwód wielokąta o kątach prostych",
)
def gen_proc_wielokat_wyciety_3pkt(rng):
    # Z prostokąta W x H wycięto w narożniku prostokąt w x h -> obwód pozostaje 2(W+H), a pole maleje o w*h!
    W = rng.randint(12, 20)
    H = rng.randint(9, 15)
    w = rng.randint(3, W - 5)
    h = rng.randint(3, H - 4)
    area = W * H - w * h
    obw = 2 * (W + H)

    obj = rng.choice(["działki budowlanej", "tarasu ogrodowego", "blatu roboczego w pracowni"])
    unit = "m" if obj != "blatu roboczego w pracowni" else "dm"

    return {
        "stem": (
            f"Kształt {obj} powstał przez wycięcie w jednym z narożników prostokąta o wymiarach "
            f"${W}$ {unit} $\\times$ ${H}$ {unit} mniejszego prostokąta o wymiarach ${w}$ {unit} $\\times$ ${h}$ {unit} "
            f"(wszystkie kąty między sąsiednimi krawędziami są proste)."
        ),
        "command": f"Oblicz pole powierzchni oraz obwód tak ukształtowanego wielokąta. Zapisz obliczenia.",
        "correct_answer": f"Pole = {area} {unit}^2, Obwód = {obw} {unit}",
        "solution_steps": [
            f"Pole wielokąta jest różnicą pól dwóch prostokątów: $P = {W} \\cdot {H} - {w} \\cdot {h} = {W * H} - {w * h} = {area}\\text{{ {unit}}}^2$.",
            f"Dwie krawędzie powstałe w narożniku mają łączną długość równą wyciętym fragmentom boków (${w}$ {unit} oraz ${h}$ {unit}), więc obwód jest równy obwodowi pełnego prostokąta: $O = 2 \\cdot ({W} + {H}) = {obw}$ {unit}.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne obliczenie pola wielokąta ({area} {unit}^2).",
            "2 pkt – poprawne wyznaczenie brakujących odcinków krawędzi wielokąta.",
            f"3 pkt – podanie poprawnego pola ({area} {unit}^2) oraz obwodu ({obw} {unit}).",
        ],
        "grid_height_mm": 56.0,
    }


# ===========================================================================
# 10. GEOMETRIA PRZESTRZENNA (7 nowych generatorów!)
# ===========================================================================

@register_template(
    template_id="proc_stereometria_drut_szkielet_abcd",
    topic_id="geometria_przestrzenna",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – suma długości wszystkich krawędzi graniastosłupa i ostrosłupa",
)
def gen_proc_szkielet_drut(rng):
    solid = rng.choice(["prism_hex", "pyramid_sq", "prism_tri"])
    if solid == "prism_hex":
        a = rng.randint(4, 9)
        h = rng.randint(8, 16)
        # 12 krawędzi podstawy po a + 6 bocznych po h
        wire = 12 * a + 6 * h
        wrongs = [6 * a + 6 * h, 12 * a + h, 6 * (a + h)]
        desc = f"graniastosłupa prawidłowego sześciokątnego o krawędzi podstawy ${a}$ cm i wysokości ${h}$ cm"
        expl = f"Graniastosłup sześciokątny ma $12$ krawędzi podstawy i $6$ krawędzi bocznych: $12 \\cdot {a} + 6 \\cdot {h} = {wire}$ cm."
    elif solid == "pyramid_sq":
        a = rng.randint(5, 12)
        b = rng.randint(9, 18)
        wire = 4 * a + 4 * b
        wrongs = [4 * a + b, 8 * a + 4 * b, 2 * (a + b)]
        desc = f"ostrosłupa prawidłowego czworokątnego o krawędzi podstawy ${a}$ cm i krawędzi bocznej ${b}$ cm"
        expl = f"Ostrosłup czworokątny ma $4$ krawędzie podstawy i $4$ krawędzie boczne: $4 \\cdot {a} + 4 \\cdot {b} = {wire}$ cm."
    else:
        a = rng.randint(6, 13)
        h = rng.randint(10, 19)
        wire = 6 * a + 3 * h
        wrongs = [3 * a + 3 * h, 6 * a + 6 * h, 9 * (a + h)]
        desc = f"graniastosłupa prawidłowego trójkątnego o krawędzi podstawy ${a}$ cm i wysokości ${h}$ cm"
        expl = f"Bryła ma $6$ krawędzi podstaw i $3$ krawędzie boczne: $6 \\cdot {a} + 3 \\cdot {h} = {wire}$ cm."

    choices, ans = shuffle_abcd(rng, f"${wire}$ cm", [f"${w}$ cm" for w in wrongs])
    return {
        "stem": f" ze stalowego drutu zbudowano pełny szkielet krawędziowy {desc}.".strip().capitalize().replace("Ze ", "Ze ").replace("ze ", "Ze "),
        "command": "Jaka minimalna długość drutu była potrzebna na wykonanie wszystkich krawędzi tego modelu? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [expl, f"Poprawna odpowiedź: **{ans}**."],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_stereometria_pomalowany_szescian_abcd",
    topic_id="geometria_przestrzenna",
    subtype="abcd",
    points=1,
    difficulty=3,
    cke_ref="Styl CKE – rozcinanie pomalowanego sześcianu na mniejsze sześciany",
)
def gen_proc_pomalowany_szescian(rng):
    n = rng.choice([3, 4, 5])
    ask_type = rng.choice(["zero_faces", "two_faces", "one_face"])
    if ask_type == "zero_faces":
        val = (n - 2) ** 3
        q_txt = "nie ma **żadnej** pomalowanej ścianki"
        expl = f"Wewnątrz bryły, bez dostępu do powierzchni zewnętrznej, tworzy się sześcian o wymiarach $({n}-2) \\times ({n}-2) \\times ({n}-2)$, czyli $({n}-2)^3 = {val}$ kostek."
        wrongs = [n ** 3 - val, 6 * (n - 2) ** 2, 8]
    elif ask_type == "two_faces":
        val = 12 * (n - 2)
        q_txt = "ma pomalowane **dokładnie dwie** ścianki"
        expl = f"Dwie pomalowane ścianki mają kostki leżące wzdłuż $12$ krawędzi (bez $8$ narożników): $12 \\cdot ({n} - 2) = {val}$ kostek."
        wrongs = [8, 6 * (n - 2) ** 2, 12 * n]
    else:
        val = 6 * ((n - 2) ** 2)
        q_txt = "ma pomalowaną **dokładnie jedną** ściankę"
        expl = f"Na każdej z $6$ ścian zewnętrznych środkowe kostki tworzą kwadrat $({n}-2) \\times ({n}-2)$, więc jest ich $6 \\cdot ({n}-2)^2 = {val}$."
        wrongs = [6 * n * n, 12 * (n - 2), (n - 2) ** 3]

    choices, ans = shuffle_abcd(rng, f"${val}$", [f"${w}$" for w in wrongs])
    return {
        "stem": (
            f"Drewniany sześcian o krawędzi ${n}$ cm pomalowano z zewnątrz na zielono ze wszystkich stron, "
            f"a następnie rozcięto go na ${n ** 3}$ małych sześcianików o krawędzi $1$ cm."
        ),
        "command": f"Ile spośród otrzymanych małych sześcianików {q_txt}? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [expl, f"Poprawna odpowiedź: **{ans}**."],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_stereometria_przelewanie_wody_2pkt",
    topic_id="geometria_przestrzenna",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – przelewanie płynu między naczyniami prostopadłościennymi",
)
def gen_proc_przelewanie_wody_2pkt(rng):
    # Z pełnego naczynia A (a1 x b1 x h1) przelano całą wodę do większego naczynia B (a2 x b2) -> jaka wysokość słupa wody?
    a1, b1, h1, a2, b2 = rng.choice([
        (15, 20, 18, 30, 30),  # V = 5400, P2 = 900 -> h2 = 6 cm
        (20, 25, 16, 40, 25),  # V = 8000, P2 = 1000 -> h2 = 8 cm
        (12, 15, 20, 20, 18),  # V = 3600, P2 = 360 -> h2 = 10 cm
        (16, 20, 15, 24, 20),  # V = 4800, P2 = 480 -> h2 = 10 cm
    ])
    vol = a1 * b1 * h1
    base2 = a2 * b2
    h2 = vol // base2

    return {
        "stem": (
            f"Pierwsze naczynie w kształcie prostopadłościanu o wymiarach podstawy ${a1}\\text{{ cm}} \\times {b1}\\text{{ cm}}$ "
            f"napełniono wodą do wysokości ${h1}$ cm. Następnie całą tę wodę przelano (bez rozlewania) do pustego "
            f"drugiego prostopadłościennego naczynia o wymiarach podstawy ${a2}\\text{{ cm}} \\times {b2}\\text{{ cm}}$ (i wysokości $25$ cm)."
        ),
        "command": "Do jakiej wysokości sięga woda w drugim naczyniu po przelaniu? Zapisz obliczenia.",
        "correct_answer": f"{h2} cm",
        "solution_steps": [
            f"Objętość przelanej wody wynosi $V = {a1} \\cdot {b1} \\cdot {h1} = {pl_num(vol)}\\text{{ cm}}^3$.",
            f"Pole podstawy drugiego naczynia jest równe $P_2 = {a2} \\cdot {b2} = {base2}\\text{{ cm}}^2$, więc wysokość słupa wody wynosi $h_2 = \\frac{{{pl_num(vol)}}}{{{base2}}} = {h2}\\text{{ cm}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie objętości wody ({pl_num(vol)} cm^3).",
            f"2 pkt – wyznaczenie poziomu wody w drugim naczyniu: {h2} cm.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_stereometria_graniastoslup_trojkatny_3pkt",
    topic_id="geometria_przestrzenna",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Styl CKE – objętość i pole całkowite graniastosłupa prawidłowego trójkątnego",
)
def gen_proc_graniastoslup_trojkatny_3pkt(rng):
    a = rng.choice([4, 6, 8, 10])
    h = rng.choice([7, 9, 11, 12, 15])
    pb = 3 * a * h
    pp_coeff = (a * a) // 4  # P_p = pp_coeff * sqrt(3)
    vol_coeff = pp_coeff * h

    given_pb = rng.choice([True, False])
    if given_pb:
        return {
            "stem": (
                f"W graniastosłupie prawidłowym trójkątnym krawędź podstawy ma długość ${a}$ cm, "
                f"a pole powierzchni bocznej jest równe ${pb}\\text{{ cm}}^2$."
            ),
            "command": "Oblicz objętość tego graniastosłupa. Zapisz obliczenia.",
            "correct_answer": f"{vol_coeff}√3 cm^3",
            "solution_steps": [
                f"Pole powierzchni bocznej składa się z $3$ przystających prostokątów o boku ${a}$ cm: $3 \\cdot {a} \\cdot H = {pb} \\Rightarrow H = {h}\\text{{ cm}}$.",
                f"Pole podstawy (trójkąta równobocznego o boku ${a}$ cm) wynosi $P_p = \\frac{{{a}^2\\sqrt{{3}}}}{{4}} = {pp_coeff}\\sqrt{{3}}\\text{{ cm}}^2$.",
                f"Objętość bryły: $V = P_p \\cdot H = {pp_coeff}\\sqrt{{3}} \\cdot {h} = {vol_coeff}\\sqrt{{3}}\\text{{ cm}}^3$.",
            ],
            "scoring_scheme": [
                f"1 pkt – obliczenie wysokości graniastosłupa ({h} cm).",
                f"2 pkt – poprawne obliczenie pola podstawy ({pp_coeff}√3 cm^2).",
                f"3 pkt – podanie poprawnej objętości: {vol_coeff}√3 cm^3.",
            ],
            "grid_height_mm": 58.0,
        }

    return {
        "stem": (
            f"Objętość graniastosłupa prawidłowego trójkątnego jest równa ${vol_coeff}\\sqrt{{3}}\\text{{ cm}}^3$, "
            f"a krawędź jego podstawy ma długość ${a}$ cm."
        ),
        "command": "Oblicz pole powierzchni bocznej tego graniastosłupa. Zapisz obliczenia.",
        "correct_answer": f"{pb} cm^2",
        "solution_steps": [
            f"Pole podstawy (trójkąta równobocznego) wynosi $P_p = \\frac{{{a}^2\\sqrt{{3}}}}{{4}} = {pp_coeff}\\sqrt{{3}}\\text{{ cm}}^2$.",
            f"Ze wzoru $V = P_p \\cdot H$ mamy ${pp_coeff}\\sqrt{{3}} \\cdot H = {vol_coeff}\\sqrt{{3}}$, skąd $H = {h}\\text{{ cm}}$.",
            f"Pole powierzchni bocznej: $P_b = 3 \\cdot {a} \\cdot {h} = {pb}\\text{{ cm}}^2$.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyznaczenie pola podstawy ({pp_coeff}√3 cm^2).",
            f"2 pkt – obliczenie wysokości graniastosłupa ({h} cm).",
            f"3 pkt – obliczenie pola powierzchni bocznej: {pb} cm^2.",
        ],
        "grid_height_mm": 58.0,
    }


@register_template(
    template_id="proc_stereometria_ostroslup_pitagoras_3pkt",
    topic_id="geometria_przestrzenna",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – pole całkowite i objętość ostrosłupa prawidłowego czworokątnego",
)
def gen_proc_ostroslup_pitagoras_3pkt(rng):
    # Trójkąt prostokątny (a/2, H, h_boczna): (3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)
    # Dobierzmy H podzielne przez 3 lub a parzyste z a^2 podzielnym przez 3, aby objętość była całkowita!
    half_a, H_pyr, h_lat = rng.choice([
        (6, 8, 10),    # a = 12, a^2 = 144 (podzielne przez 3!), V = 384
        (3, 4, 5),     # a = 6, a^2 = 36 (podzielne przez 3!), V = 48
        (9, 12, 15),   # a = 18, V = 1296
        (5, 12, 13),   # a = 10, H = 12 (podzielne przez 3!), V = 400
        (8, 15, 17),   # a = 16, H = 15 (podzielne przez 3!), V = 1280
    ])
    a = 2 * half_a
    pp = a * a
    pb = 4 * (a * h_lat) // 2
    pc = pp + pb
    vol = (pp * H_pyr) // 3

    ask_vol = rng.choice([True, False])
    if ask_vol:
        return {
            "stem": (
                f"W ostrosłupie prawidłowym czworokątnym krawędź podstawy ma długość ${a}$ cm, "
                f"a wysokość ściany bocznej poprowadzona z wierzchołka ostrosłupa ma długość ${h_lat}$ cm."
            ),
            "command": "Oblicz objętość tego ostrosłupa. Zapisz obliczenia.",
            "correct_answer": f"{vol} cm^3",
            "solution_steps": [
                f"Wysokość $H$ ostrosłupa, wysokość ściany bocznej $h_b = {h_lat}\\text{{ cm}}$ oraz połowa krawędzi podstawy $\\frac{{a}}{{2}} = {half_a}\\text{{ cm}}$ tworzą trójkąt prostokątny.",
                f"Z twierdzenia Pitagorasa: $H = \\sqrt{{{h_lat}^2 - {half_a}^2}} = \\sqrt{{{H_pyr**2}}} = {H_pyr}\\text{{ cm}}$.",
                f"Objętość ostrosłupa: $V = \\frac{{1}}{{3}} \\cdot {a}^2 \\cdot {H_pyr} = {vol}\\text{{ cm}}^3$.",
            ],
            "scoring_scheme": [
                f"1 pkt – zauważenie trójkąta prostokątnego z odcinkiem a/2 = {half_a} cm.",
                f"2 pkt – wyznaczenie wysokości ostrosłupa H = {H_pyr} cm.",
                f"3 pkt – obliczenie objętości ostrosłupa: {vol} cm^3.",
            ],
            "grid_height_mm": 58.0,
        }

    return {
        "stem": (
            f"W ostrosłupie prawidłowym czworokątnym krawędź podstawy ma długość ${a}$ cm, "
            f"a wysokość tego ostrosłupa jest równa ${H_pyr}$ cm."
        ),
        "command": "Oblicz pole powierzchni całkowitej tego ostrosłupa. Zapisz obliczenia.",
        "correct_answer": f"{pc} cm^2",
        "solution_steps": [
            f"Z twierdzenia Pitagorasa dla wysokości ostrosłupa $H = {H_pyr}\\text{{ cm}}$ oraz połowy boku podstawy $\\frac{{a}}{{2}} = {half_a}\\text{{ cm}}$ obliczamy wysokość ściany bocznej: $h_b = \\sqrt{{{H_pyr}^2 + {half_a}^2}} = {h_lat}\\text{{ cm}}$.",
            f"Pole podstawy wynosi $P_p = {a}^2 = {pp}\\text{{ cm}}^2$, a pole boczne $P_b = 4 \\cdot \\frac{{1}}{{2}} \\cdot {a} \\cdot {h_lat} = {pb}\\text{{ cm}}^2$.",
            f"Pole powierzchni całkowitej: $P_c = {pp} + {pb} = {pc}\\text{{ cm}}^2$.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne zapisanie równania Pitagorasa na wysokość ściany bocznej.",
            f"2 pkt – obliczenie wysokości ściany bocznej ({h_lat} cm) oraz pola bocznego ({pb} cm^2).",
            f"3 pkt – podanie pola powierzchni całkowitej: {pc} cm^2.",
        ],
        "grid_height_mm": 58.0,
    }


@register_template(
    template_id="proc_stereometria_przekatna_prostopadloscianu_2pkt",
    topic_id="geometria_przestrzenna",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – przekątna podstawy i przekątna graniastosłupa",
)
def gen_proc_przekatna_prostopadloscianu(rng):
    # Czwórki pitagorejskie 3D: a^2 + b^2 = d_p^2 i d_p^2 + c^2 = D^2, np. (3, 4, 12 -> 13), (6, 8, 24 -> 26), (9, 12, 20 -> 25), (8, 15, 36 -> 39 - duże), (12, 16, 15 -> 25)
    a, b, dp, h, D = rng.choice([
        (3, 4, 5, 12, 13),
        (6, 8, 10, 24, 26),
        (9, 12, 15, 20, 25),
        (12, 16, 20, 15, 25),
    ])
    return {
        "stem": (
            f"Prostopadłościan ma podstawę o wymiarach ${a}\\text{{ cm}} \\times {b}\\text{{ cm}}$, "
            f"a jego wysokość (krawędź boczna) ma długość ${h}$ cm."
        ),
        "command": "Oblicz długość przekątnej tego prostopadłościanu. Zapisz obliczenia.",
        "correct_answer": f"{D} cm",
        "solution_steps": [
            f"Przekątna podstawy $d$ spełnia $d^2 = {a}^2 + {b}^2 = {dp**2}$ (czyli $d = {dp}\\text{{ cm}}$).",
            f"Przekątna prostopadłościanu $D$ z twierdzenia Pitagorasa: $D = \\sqrt{{d^2 + {h}^2}} = \\sqrt{{{dp**2} + {h**2}}} = \\sqrt{{{D**2}}} = {D}\\text{{ cm}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie długości (lub kwadratu długości) przekątnej podstawy ({dp} cm).",
            f"2 pkt – wyznaczenie długości przekątnej prostopadłościanu: {D} cm.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_stereometria_litry_objetosc_uzasadnienie",
    topic_id="geometria_przestrzenna",
    subtype="uzasadnienie",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – zamiana cm^3 na litry (1 l = 1 dm^3 = 1000 cm^3)",
)
def gen_proc_litry_pojemnik_uzasadnienie(rng):
    a_cm, b_cm, h_cm = rng.choice([(25, 20, 30), (40, 25, 18), (30, 20, 25), (20, 20, 35)])
    vol_cm3 = a_cm * b_cm * h_cm
    liters_cap = vol_cm3 / 1000  # 15, 18, 15, 14 l
    is_fit = rng.choice([True, False])
    pour_l = int(liters_cap) - rng.choice([2, 3]) if is_fit else int(liters_cap) + rng.choice([2, 4])

    ans_ab = "A" if is_fit else "B"
    r_good = f"$1\\text{{ litr}} = 1000\\text{{ cm}}^3$, więc pojemność skrzynki wynosi ${pl_num(liters_cap)}$ l."
    r_bad1 = f"suma krawędzi ${a_cm} + {b_cm} + {h_cm}$ jest większa od ${pour_l}$."
    r_bad2 = f"$1\\text{{ litr}} = 100\\text{{ cm}}^3$, więc pojemność skrzynki jest większa niż $100$ l."
    r_list = [(r_good, True), (r_bad1, False), (r_bad2, False)]
    rng.shuffle(r_list)
    reasons = {str(i + 1): txt for i, (txt, _) in enumerate(r_list)}
    good_idx = next(str(i + 1) for i, (_, ok) in enumerate(r_list) if ok)

    return {
        "stem": (
            f"Pojemnik ma wewnątrz kształt prostopadłościanu o wymiarach ${a_cm}\\text{{ cm}} \\times {b_cm}\\text{{ cm}} \\times {h_cm}\\text{{ cm}}$. "
            f"Ogrodnik chce wsypać do niego zawartość worka zawierającego ${pour_l}$ litrów ziemi ogrodniczej."
        ),
        "command": "Czy cała ziemia z worka zmieści się w tym pojemniku (bez usypywania górki)? Wybierz odpowiedź A (Tak) albo B (Nie) i jej uzasadnienie.",
        "justification_data": {
            "prefix_a": "Tak,",
            "prefix_b": "Nie,",
            "conjunction": "ponieważ",
            "reasons": reasons,
        },
        "correct_answer": f"{ans_ab}{good_idx}",
        "solution_steps": [
            f"Objętość wewnętrzna pojemnika wynosi ${a_cm} \\cdot {b_cm} \\cdot {h_cm} = {pl_num(vol_cm3)}\\text{{ cm}}^3 = {pl_num(liters_cap)}\\text{{ dm}}^3 = {pl_num(liters_cap)}\\text{{ l}}$.",
            f"Porównujemy ${pour_l}\\text{{ l}}$ z pojemnością ${pl_num(liters_cap)}\\text{{ l}}$ -> poprawna odpowiedź to **{ans_ab}{good_idx}**.",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź z uzasadnieniem.", "0 pkt – pozostałe przypadki."],
    }


# ===========================================================================
# 11. STATYSTYKA, TABELE I DIAGRAMY (6 nowych generatorów)
# ===========================================================================

@register_template(
    template_id="proc_statystyka_brakujaca_ocena_abcd",
    topic_id="statystyka_diagramy",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – wyznaczanie brakującej danej na podstawie średniej arytmetycznej",
)
def gen_proc_brakujaca_dana_abcd(rng):
    n = rng.choice([5, 6])
    target_mean = rng.choice([12, 14, 15, 16, 18])
    total_sum = n * target_mean
    known = [target_mean + rng.choice([-4, -2, -1, 1, 2, 3]) for _ in range(n - 1)]
    missing = total_sum - sum(known)
    while missing <= 0:
        known[0] -= 4
        missing = total_sum - sum(known)

    known_str = ", ".join(f"${v}$" for v in known)
    choices, ans = shuffle_abcd(
        rng,
        f"${missing}$",
        [f"${target_mean}$", f"${missing + n}$", f"${abs(missing - 3)}$"],
    )
    ctx = rng.choice([
        ("W kolejnych treningach pływackich zawodniczka przepłynęła następujące liczby długości basenu:", "ostatnim treningu"),
        ("Przez kolejne dni kiermaszu sprzedano następujące liczby zakładek:", "ostatniego dnia"),
        ("W kolejnych rundach turnieju drużyna zdobyła następujące liczby punktów:", "ostatniej rundzie"),
    ])

    return {
        "stem": (
            f"{ctx[0]} {known_str} oraz $x$ (w {ctx[1]}). "
            f"Średnia arytmetyczna wszystkich ${n}$ wyników jest równa ${target_mean}$."
        ),
        "command": "Ile wynosi wartość $x$? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Suma wszystkich ${n}$ wyników musi być równa ${n} \\cdot {target_mean} = {total_sum}$.",
            f"Suma znanych wyników wynosi ${sum(known)}$, więc $x = {total_sum} - {sum(known)} = {missing}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_statystyka_mediana_parzysta_pf",
    topic_id="statystyka_diagramy",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – mediana i rozstęp zestawu danych o parzystej liczebności",
)
def gen_proc_mediana_parzysta_pf(rng):
    # 8 liczb z medianą będącą ułamkiem .5 lub liczbą całkowitą
    base = rng.randint(4, 12)
    sorted_vals = [
        base,
        base + 1,
        base + 3,
        base + 4,
        base + 6,
        base + 7,
        base + 9,
        base + 11,
    ]
    shown = list(sorted_vals)
    rng.shuffle(shown)
    med_true = (sorted_vals[3] + sorted_vals[4]) // 2  # base + 5
    # Uwaga: dystraktor bez uporządkowania bierze shown[3] i shown[4]!
    s1_true = rng.choice([True, False])
    med_claim = med_true if s1_true else (med_true + 2)

    mean_val = Fraction(sum(sorted_vals), 8)
    s2_true = rng.choice([True, False])
    # Liczba wyników większych od mediany: 4 z 8 (czyli połowa!)
    cnt_above = sum(1 for v in sorted_vals if v > med_true)  # dokładnie 4
    claim_cnt = 4 if s2_true else 3

    a1, a2 = ("P" if s1_true else "F"), ("P" if s2_true else "F")
    vals_str = ",  ".join(f"${v}$" for v in shown)
    return {
        "stem": f"Ośmioro uczestników koła szachowego rozwiązało w ciągu tygodnia następujące liczby zadań taktycznych:\n{vals_str}.",
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Mediana liczby rozwiązanych zadań w tej grupie jest równa ${med_claim}$.", a1),
            (f"Dokładnie ${claim_cnt}$ uczestników rozwiązało więcej zadań niż wynosi mediana.", a2),
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Porządkujemy dane niemalejąco: {', '.join(str(v) for v in sorted_vals)}. Mediana to średnia czwartego i piątego wyrazu: $\\frac{{{sorted_vals[3]} + {sorted_vals[4]}}}{{2}} = {med_true}$ (**{a1}**).",
            f"Wyniki większe od ${med_true}$ to ${sorted_vals[4]}, {sorted_vals[5]}, {sorted_vals[6]}, {sorted_vals[7]}$ – jest ich dokładnie ${cnt_above}$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_statystyka_kat_wycinka_kolowego_ab_cd",
    topic_id="statystyka_diagramy",
    subtype="ab_cd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – miara kąta środkowego na diagramie kołowym",
)
def gen_proc_kat_diagramu_kolowego(rng):
    pct = rng.choice([15, 20, 25, 30, 35, 40])
    deg = (360 * pct) // 100
    bad_deg = pct * 3

    deg2 = rng.choice([72, 90, 108, 126, 144])
    pct2 = (deg2 * 100) // 360
    bad_pct2 = deg2 // 3

    if rng.random() < 0.5:
        opts1, a1 = {"A": f"${deg}^\\circ$", "B": f"${bad_deg}^\\circ$"}, "A"
    else:
        opts1, a1 = {"A": f"${bad_deg}^\\circ$", "B": f"${deg}^\\circ$"}, "B"

    if rng.random() < 0.5:
        opts2, a2 = {"C": f"${pct2}\\%$", "D": f"${bad_pct2}\\%$"}, "C"
    else:
        opts2, a2 = {"C": f"${bad_pct2}\\%$", "D": f"${pct2}\\%$"}, "D"

    return {
        "stem": "Wyniki ankiety szkolnej przedstawiono na diagramie kołowym, w którym całe koło ($360^\\circ$) odpowiada $100\\%$ ankietowanych.",
        "command": "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D.",
        "ab_cd_parts": [
            {"prefix": f"Kategorii wybranej przez ${pct}\\%$ ankietowanych odpowiada wycinek koła o kącie środkowym", "suffix": ".", "options": opts1},
            {"prefix": f"Wycinek koła o kącie środkowym równym ${deg2}^\\circ$ przedstawia wybór dokładnie", "suffix": " ankietowanych.", "options": opts2},
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Kąt środkowy dla ${pct}\\%$: $\\frac{{{pct}}}{{100}} \\cdot 360^\\circ = {deg}^\\circ$ (**{a1}**).",
            f"Procent dla kąta ${deg2}^\\circ$: $\\frac{{{deg2}^\\circ}}{{360^\\circ}} \\cdot 100\\% = {pct2}\\%$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna para odpowiedzi.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_statystyka_srednia_wazona_tabela_2pkt",
    topic_id="statystyka_diagramy",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – obliczanie średniej arytmetycznej z tabeli liczebności",
)
def gen_proc_srednia_z_tabeli_2pkt(rng):
    # Liczba książek przeczytanych w półroczu (0, 1, 2, 3, 4) i liczby uczniów w klasie (suma 20 lub 25)
    c0, c1, c2, c3, c4 = rng.choice([
        (2, 5, 7, 4, 2),   # n=20, suma = 0+5+14+12+8 = 39 -> 1,95
        (1, 4, 8, 5, 2),   # n=20, suma = 0+4+16+15+8 = 43 -> 2,15
        (3, 6, 8, 5, 3),   # n=25, suma = 0+6+16+15+12 = 49 -> 1,96
        (2, 5, 9, 6, 3),   # n=25, suma = 0+5+18+18+12 = 53 -> 2,12
        (2, 4, 6, 6, 2),   # n=20, suma = 0+4+12+18+8 = 42 -> 2,1
    ])
    n_students = c0 + c1 + c2 + c3 + c4
    tot_items = 0 * c0 + 1 * c1 + 2 * c2 + 3 * c3 + 4 * c4
    mean = tot_items / n_students

    topic_ctx = rng.choice([
        ("przeczytanych lektur dodatkowych", "Liczba książek", "Liczba uczniów"),
        ("zdobytych odznak turystycznych", "Liczba odznak", "Liczba harcerzy"),
        ("obejrzanych spektakli teatralnych", "Liczba spektakli", "Liczba osób"),
    ])

    return {
        "stem": f"W grupie badawczej przeprowadzono ankietę dotyczącą liczby {topic_ctx[0]} w minionym półroczu. Zebrane wyniki przedstawiono w tabeli.",
        "table_data": [
            [topic_ctx[1], "$0$", "$1$", "$2$", "$3$", "$4$"],
            [topic_ctx[2], f"${c0}$", f"${c1}$", f"${c2}$", f"${c3}$", f"${c4}$"],
        ],
        "command": f"Oblicz średnią liczbę {topic_ctx[0]} przypadającą na jedną osobę w tej grupie. Zapisz obliczenia.",
        "correct_answer": f"{pl_num(mean)}",
        "solution_steps": [
            f"Łączna liczba osób wynosi ${c0} + {c1} + {c2} + {c3} + {c4} = {n_students}$.",
            f"Suma wszystkich wskazań (z uwzględnieniem zer!): $0 \\cdot {c0} + 1 \\cdot {c1} + 2 \\cdot {c2} + 3 \\cdot {c3} + 4 \\cdot {c4} = {tot_items}$. Średnia wynosi $\\frac{{{tot_items}}}{{{n_students}}} = {pl_num(mean)}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne obliczenie łącznej liczby osób ({n_students}) lub sumy iloczynów ({tot_items}).",
            f"2 pkt – obliczenie poprawnej średniej arytmetycznej: {pl_num(mean)}.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_statystyka_wykres_dwuslupkowy_3pkt",
    topic_id="statystyka_diagramy",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Styl CKE – analiza diagramu słupkowego i zmiana procentowa",
    has_diagram=True,
)
def gen_proc_diagram_analiza_3pkt(rng):
    # Diagram słupkowy z 4 miesiącami (V, VI, VII, VIII), pytamy o ile procent sprzedaż w lipcu i sierpniu łącznie była większa od maja i czerwca łącznie
    m1, m2 = rng.choice([(30, 50), (45, 35), (60, 40), (50, 70)])  # suma = 80, 80, 100, 120
    s_first = m1 + m2
    pct_inc = rng.choice([25, 30, 40, 50])
    while (s_first * pct_inc) % 100 != 0:
        pct_inc = 25
    s_second = s_first + (s_first * pct_inc) // 100
    m3 = s_second // 2 + rng.choice([4, 6, 8])
    m4 = s_second - m3

    ctx = rng.choice([
        ("wypożyczonych kajaków w przystani wodnej", "Liczba wypożyczeń"),
        ("odwiedzających wieżę widokową (w dziesiątkach osób)", "Liczba wejść [×10]"),
        ("sprzedanych karnetów na korty tenisowe", "Liczba karnetów"),
    ])

    return {
        "stem": f"Na diagramie słupkowym przedstawiono statystykę {ctx[0]} w czterech kolejnych miesiącach: maju, czerwcu, lipcu oraz sierpniu.",
        "diagram": DiagramSpec(
            kind="bar_chart",
            params={
                "categories": ["maj", "czerwiec", "lipiec", "sierpień"],
                "values": [m1, m2, m3, m4],
                "ylabel": ctx[1],
                "y_step": 20,
            },
            width_mm=86.0,
        ),
        "command": "Oblicz, o ile procent łączny wynik z lipca i sierpnia był większy od łącznego wyniku z maja i czerwca. Zapisz obliczenia.",
        "correct_answer": f"{pct_inc}%",
        "solution_steps": [
            f"Odczytujemy wartości z diagramu: w maju i czerwcu łącznie było ${m1} + {m2} = {s_first}$, a w lipcu i sierpniu łącznie ${m3} + {m4} = {s_second}$.",
            f"Różnica wynosi ${s_second} - {s_first} = {s_second - s_first}$.",
            f"Obliczamy stosunek wzrostu do bazy z maja i czerwca: $\\frac{{{s_second - s_first}}}{{{s_first}}} \\cdot 100\\% = {pct_inc}\\%$.",
        ],
        "scoring_scheme": [
            f"1 pkt – odczytanie danych i obliczenie sum dla obu par miesięcy ({s_first} i {s_second}).",
            f"2 pkt – odniesienie różnicy ({s_second - s_first}) do sumy z maja i czerwca ({s_first}).",
            f"3 pkt – podanie poprawnego wyniku procentowego: {pct_inc}%.",
        ],
        "grid_height_mm": 56.0,
    }


@register_template(
    template_id="proc_statystyka_dwie_grupy_srednia_2pkt",
    topic_id="statystyka_diagramy",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – średnia połączonych grup o różnej liczebności",
)
def gen_proc_dwie_grupy_srednia(rng):
    n1, avg1, n2, avg2 = rng.choice([
        (12, 15, 8, 20),    # (180+160)/20 = 17
        (15, 18, 10, 23),   # (270+230)/25 = 20
        (9, 14, 6, 19),     # (126+114)/15 = 16
        (16, 22, 4, 27),    # (352+108)/20 = 23
    ])
    tot_pts = n1 * avg1 + n2 * avg2
    avg_all = tot_pts // (n1 + n2)

    return {
        "stem": (
            f"W konkursie geograficznym startowały dwie grupy uczniów. Pierwsza grupa liczyła ${n1}$ osób "
            f"i uzyskała średni wynik równy ${avg1}$ punktów, natomiast druga grupa liczyła ${n2}$ osób "
            f"i uzyskała średni wynik równy ${avg2}$ punktów."
        ),
        "command": f"Oblicz średnią liczbę punktów uzyskanych przez wszystkich ${n1 + n2}$ uczestników tego konkursu łącznie. Zapisz obliczenia.",
        "correct_answer": f"{avg_all} pkt",
        "solution_steps": [
            f"Suma punktów pierwszej grupy wynosi ${n1} \\cdot {avg1} = {n1 * avg1}$, a drugiej grupy: ${n2} \\cdot {avg2} = {n2 * avg2}$.",
            f"Średnia dla wszystkich ${n1 + n2}$ osób wynosi $\\frac{{{n1 * avg1} + {n2 * avg2}}}{{{n1 + n2}}} = \\frac{{{tot_pts}}}{{{n1 + n2}}} = {avg_all}$ pkt.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie łącznej sumy punktów zdobytych przez obie grupy ({tot_pts} pkt).",
            f"2 pkt – podzielenie przez łączną liczbę uczniów ({n1 + n2}) i podanie średniej: {avg_all} pkt.",
        ],
        "grid_height_mm": 50.0,
    }


# ===========================================================================
# 12. PRAWDOPODOBIEŃSTWO I KOMBINATORYKA (5 nowych generatorów)
# ===========================================================================

@register_template(
    template_id="proc_prawdop_dwie_kostki_suma_abcd",
    topic_id="prawdopodobienstwo",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – rzut dwiema kostkami sześciennymi",
)
def gen_proc_dwie_kostki_abcd(rng):
    cond_name, fav_count, pairs_desc = rng.choice([
        ("suma wyrzuconych oczek będzie równa $7$", 6, "(1,6), (2,5), (3,4), (4,3), (5,2), (6,1)"),
        ("suma wyrzuconych oczek będzie równa $10$", 3, "(4,6), (5,5), (6,4)"),
        ("suma wyrzuconych oczek będzie mniejsza od $5$", 6, "(1,1), (1,2), (2,1), (1,3), (2,2), (3,1)"),
        ("iloczyn wyrzuconych oczek będzie równy $12$", 4, "(2,6), (3,4), (4,3), (6,2)"),
        ("na obu kostkach wypadną jednakowe liczby oczek", 6, "(1,1), (2,2), (3,3), (4,4), (5,5), (6,6)"),
    ])
    p_corr = Fraction(fav_count, 36)
    cands = [
        Fraction(fav_count, 12),
        Fraction(max(1, fav_count - 1), 36),
        Fraction(fav_count + 2, 36),
        Fraction(1, 6) if p_corr != Fraction(1, 6) else Fraction(1, 9),
    ]
    wrongs = []
    for c in cands:
        if c != p_corr and c not in wrongs:
            wrongs.append(c)
        if len(wrongs) == 3:
            break

    choices, ans = shuffle_abcd(
        rng,
        frac_tex(p_corr.numerator, p_corr.denominator),
        [frac_tex(w.numerator, w.denominator) for w in wrongs],
    )

    return {
        "stem": "Rzucamy jednocześnie dwiema symetrycznymi sześciennymi kostkami do gry (na ściankach od $1$ do $6$ oczek).",
        "command": f"Jakie jest prawdopodobieństwo zdarzenia polegającego na tym, że {cond_name}? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            "Wszystkich równie prawdopodobnych wyników rzutu dwiema kostkami jest $6 \\cdot 6 = 36$.",
            f"Zdarzeniu sprzyja dokładnie ${fav_count}$ par wyników: {pairs_desc}, stąd $P = \\frac{{{fav_count}}}{{36}} = {frac_tex(p_corr.numerator, p_corr.denominator)}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_prawdop_liczby_dwucyfrowe_pf",
    topic_id="prawdopodobienstwo",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – zliczanie liczb dwucyfrowych spełniających warunki",
)
def gen_proc_liczby_dwucyfrowe_pf(rng):
    # Spośród wszystkich 90 liczb dwucyfrowych (10..99)
    div_k = rng.choice([9, 10, 15, 18])
    cnt_div = sum(1 for n in range(10, 100) if n % div_k == 0)
    p_true = Fraction(cnt_div, 90)
    s1_true = rng.choice([True, False])
    p_claim = p_true if s1_true else Fraction(cnt_div, 100)

    # Liczby dwucyfrowe o jednakowych cyfrach: 11, 22, ..., 99 -> jest ich 9 (prawdop. 9/90 = 1/10)
    s2_true = rng.choice([True, False])
    same_cnt_claim = 9 if s2_true else 10

    a1, a2 = ("P" if s1_true else "F"), ("P" if s2_true else "F")
    f_claim = frac_tex(p_claim.numerator, p_claim.denominator)
    f_good = frac_tex(p_true.numerator, p_true.denominator)
    return {
        "stem": "Ze zbioru wszystkich liczb naturalnych dwucyfrowych ($10, 11, 12, \\dots, 99$) losujemy jedną liczbę.",
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Prawdopodobieństwo wylosowania liczby podzielnej przez ${div_k}$ jest równe {f_claim}.", a1),
            (f"Wszystkich liczb dwucyfrowych mających jednakową cyfrę dziesiątek i jedności jest dokładnie ${same_cnt_claim}$.", a2),
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Wszystkich liczb dwucyfrowych jest $90$, a podzielnych przez ${div_k}$ jest ${cnt_div}$, więc prawdopodobieństwo wynosi $\\frac{{{cnt_div}}}{{90}} = {f_good}$ (**{a1}**).",
            f"Liczby o jednakowych cyfrach to $11, 22, \\dots, 99$ – jest ich dokładnie $9$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_prawdop_zestawy_menu_2pkt",
    topic_id="prawdopodobienstwo",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – reguła mnożenia i prawdopodobieństwo wyboru zestawu",
)
def gen_proc_menu_kombinatoryka_2pkt(rng):
    # Wybieramy losowo 1 zupę spośród A i 1 drugie danie spośród B i 1 napój spośród C
    n_a = rng.choice([3, 4])
    n_b = rng.choice([4, 5])
    n_c = rng.choice([2, 3])
    tot = n_a * n_b * n_c
    # Ile zestawów NIE zawiera określonej 1 zupy i określonego 1 drugiego dania? (n_a - 1)*(n_b - 1)*n_c
    fav = (n_a - 1) * (n_b - 1) * n_c
    prob = Fraction(fav, tot)

    return {
        "stem": (
            f"W szkolnej stołówce zestaw obiadowy składa się z jednej zupy wybranej spośród ${n_a}$ zup, "
            f"jednego drugiego dania wybranego spośród ${n_b}$ propozycji oraz jednego napoju spośród ${n_c}$ napojów. "
            f"Wśród zup jest pomidorowa, a wśród drugich dań – naleśniki."
        ),
        "command": (
            "Oblicz, ile wszystkich różnych zestawów obiadowych można utworzyć oraz ile z nich "
            "**nie zawiera** ani zupy pomidorowej, ani naleśników. Zapisz obliczenia."
        ),
        "correct_answer": f"Wszystkich: {tot}, bez pomidorowej i naleśników: {fav}",
        "solution_steps": [
            f"Z reguły mnożenia liczba wszystkich różnych zestawów wynosi ${n_a} \\cdot {n_b} \\cdot {n_c} = {tot}$.",
            f"Odrzucając zupę pomidorową (zostaje ${n_a - 1}$ zup) oraz naleśniki (zostaje ${n_b - 1}$ drugich dań), otrzymujemy ${n_a - 1} \\cdot {n_b - 1} \\cdot {n_c} = {fav}$ takich zestawów.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie liczby wszystkich możliwych zestawów ({tot}).",
            f"2 pkt – obliczenie liczby zestawów spełniających warunek ({fav}).",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_prawdop_losy_wygrywajace_2pkt",
    topic_id="prawdopodobienstwo",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – wyznaczanie liczby elementów ze znanego prawdopodobieństwa",
)
def gen_proc_losy_prawdop_2pkt(rng):
    # W urnie są losy pełne i puste. Prawdop. wylosowania pełnego to p/q. Pustych jest o D więcej niż pełnych -> ile jest wszystkich losów?
    p_num, p_den = rng.choice([(1, 4), (2, 7), (3, 8), (2, 9), (3, 10)])
    # Pełnych: p_num * k, Pustych: (p_den - p_num) * k -> różnica = (p_den - 2*p_num) * k
    k = rng.randint(5, 14)
    win = p_num * k
    empty = (p_den - p_num) * k
    diff = empty - win
    total = p_den * k
    t_fr = frac_tex(p_num, p_den)

    return {
        "stem": (
            f"W urnie na festynie szkolnym znajdują się wyłącznie losy wygrywające i losy puste. "
            f"Losów pustych jest o ${diff}$ więcej niż losów wygrywających. Prawdopodobieństwo wylosowania "
            f"jednego losu wygrywającego jest równe {t_fr}."
        ),
        "command": "Oblicz, ile łącznie wszystkich losów znajduje się w tej urnie. Zapisz obliczenia.",
        "correct_answer": f"{total}",
        "solution_steps": [
            f"Oznaczmy liczbę losów wygrywających przez $x$, a pustych przez $x + {diff}$. Wszystkich losów jest $2x + {diff}$.",
            f"Z równania $\\frac{{x}}{{2x + {diff}}} = \\frac{{{p_num}}}{{{p_den}}}$ mamy ${p_den}x = {2 * p_num}x + {p_num * diff}$, skąd ${p_den - 2 * p_num}x = {p_num * diff} \\Rightarrow x = {win}$.",
            f"Łączna liczba wszystkich losów: $2 \\cdot {win} + {diff} = {total}$.",
        ],
        "scoring_scheme": [
            "1 pkt – zapisanie poprawnej zależności lub równania na prawdopodobieństwo.",
            f"2 pkt – obliczenie liczby wszystkich losów w urnie: {total}.",
        ],
        "grid_height_mm": 52.0,
    }


@register_template(
    template_id="proc_prawdop_zabranie_kul_3pkt",
    topic_id="prawdopodobienstwo",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – zmiana zawartości pudełka a nowe prawdopodobieństwo",
)
def gen_proc_zmiana_pudelka_3pkt(rng):
    # W szkatułce są żetony złote, srebrne i miedziane. Złotych jest a, srebrnych 2a, miedzianych c.
    # Po dołożeniu d złotych prawdopodobieństwo wylosowania złotego stało się równe 1/3 (lub 2/5). Ile było żetonów na początku?
    a = rng.randint(6, 15)
    silver = 2 * a
    # Chcemy (a + added) / (3a + copper + added) = 1/3 -> 3a + 3*added = 3a + copper + added -> copper = 2*added!
    # Weźmy inny ułamek, żeby zależało od a! Np. p_new = 2/5:
    # 5(a + added) = 2(3a + c + added) -> 5a + 5*added = 6a + 2c + 2*added -> a = 3*added - 2c!
    c_fixed = rng.choice([6, 9, 12])
    added = rng.choice([8, 10, 12, 14])
    while 3 * added - 2 * c_fixed <= 4:
        added += 4
    a = 3 * added - 2 * c_fixed
    silver = 2 * a
    init_tot = 3 * a + c_fixed

    return {
        "stem": (
            f"W woreczku znajdowały się żetony w trzech kolorach: złotym, srebrnym oraz miedzianym. "
            f"Na początku żetonów srebrnych było $2$ razy więcej niż złotych, a żetonów miedzianych było dokładnie ${c_fixed}$. "
            f"Gdy do woreczka dołożono jeszcze ${added}$ żetonów złotych, prawdopodobieństwo wylosowania żetonu złotego stało się równe $\\frac{{2}}{{5}}$."
        ),
        "command": "Oblicz, ile wszystkich żetonów znajdowało się w woreczku na początku (przed dołożeniem). Zapisz obliczenia.",
        "correct_answer": f"{init_tot}",
        "solution_steps": [
            f"Oznaczmy początkową liczbę żetonów złotych przez $x$. Wówczas srebrnych było $2x$, miedzianych ${c_fixed}$, a łącznie na początku było $3x + {c_fixed}$ żetonów.",
            f"Po dołożeniu ${added}$ żetonów złotych mamy $x + {added}$ złotych spośród $3x + {c_fixed + added}$ wszystkich. Z warunku $\\frac{{x + {added}}}{{3x + {c_fixed + added}}} = \\frac{{2}}{{5}}$ dostajemy $5(x + {added}) = 2(3x + {c_fixed + added})$.",
            f"Stąd $5x + {5 * added} = 6x + {2 * (c_fixed + added)}$, czyli $x = {a}$. Na początku w woreczku było $3 \\cdot {a} + {c_fixed} = {init_tot}$ żetonów.",
        ],
        "scoring_scheme": [
            "1 pkt – wyrażenie liczby żetonów przed i po dołożeniu za pomocą jednej niewiadomej.",
            f"2 pkt – ułożenie równania z ułamkiem 2/5 i obliczenie x = {a}.",
            f"3 pkt – podanie początkowej łącznej liczby wszystkich żetonów: {init_tot}.",
        ],
        "grid_height_mm": 60.0,
    }
