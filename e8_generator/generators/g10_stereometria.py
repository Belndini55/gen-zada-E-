"""Dział 10: Geometria przestrzenna – graniastosłupy, ostrosłupy, siatki i objętość."""

from __future__ import annotations

from ..math_text import frac_tex, pl_num, shuffle_abcd
from ..models import DiagramSpec
from .base import register_template


@register_template(
    template_id="stereometria_wierzcholki_krawedzie_abcd",
    topic_id="geometria_przestrzenna",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2023 zad. 9",
)
def gen_ostroslup_graniastoslup_abcd(rng):
    n = rng.randint(6, 15)  # n-kąt w podstawie
    mode = rng.choice(["vertices_to_vertices", "edges_to_edges"])

    if mode == "vertices_to_vertices":
        pyr_v = n + 1
        prism_v = 2 * n
        stem = f"Pewien ostrosłup ma dokładnie ${pyr_v}$ wierzchołków."
        command = "Ile wierzchołków ma graniastosłup o takiej samej podstawie, jaką ma ten ostrosłup? Wybierz właściwą odpowiedź spośród podanych."
        corr = f"${prism_v}$"
        distractors = [f"${2 * pyr_v}$", f"${3 * n}$", f"${n + 2}$"]
        steps = [
            f"Ostrosłup o podstawie $n$-kąta ma $n + 1$ wierzchołków. Z równania $n + 1 = {pyr_v}$ otrzymujemy $n = {n}$.",
            f"Graniastosłup o podstawie ${n}$-kąta ma $2n = 2 \\cdot {n} = {prism_v}$ wierzchołków (odpowiedź **{ '{ans}' }**).",
        ]
    else:
        pyr_e = 2 * n
        prism_e = 3 * n
        stem = f"Pewien ostrosłup ma dokładnie ${pyr_e}$ krawędzi."
        command = "Ile wszystkich krawędzi ma graniastosłup o takiej samej podstawie, jaką ma ten ostrosłup? Wybierz właściwą odpowiedź spośród podanych."
        corr = f"${prism_e}$"
        distractors = [f"${2 * pyr_e}$", f"${2 * n + 1}$", f"${prism_e + 3}$"]
        steps = [
            f"Ostrosłup o podstawie $n$-kąta ma $2n$ krawędzi. Zatem $2n = {pyr_e}$, skąd $n = {n}$.",
            f"Graniastosłup o podstawie ${n}$-kąta ma $3n = 3 \\cdot {n} = {prism_e}$ krawędzi (odpowiedź **{ '{ans}' }**).",
        ]

    choices, ans = shuffle_abcd(rng, corr, distractors)
    steps[-1] = steps[-1].replace("{ans}", ans)

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": steps,
    }


@register_template(
    template_id="stereometria_graniastoslup_pf",
    topic_id="geometria_przestrzenna",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Grudzień 2024 zad. 13",
)
def gen_graniastoslup_pf(rng):
    a = rng.randint(4, 9)
    mult = rng.choice([2, 3])
    H = mult * a
    vol = a * a * H
    edges_sum = 8 * a + 4 * H

    s1_true = rng.choice([True, False])
    shown_vol = vol if s1_true else (4 * a * H)

    s2_true = rng.choice([True, False])
    shown_edges = edges_sum if s2_true else (4 * a + 4 * H)

    word_mult = "dwa razy dłuższa" if mult == 2 else "trzy razy dłuższa"
    stem = (
        f"Dany jest graniastosłup prawidłowy czworokątny, w którym krawędź podstawy ma długość ${a}$ cm, "
        f"a krawędź boczna jest {word_mult} od krawędzi podstawy."
    )
    command = "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe."

    st1 = f"Objętość tego graniastosłupa jest równa ${shown_vol}\\text{{ cm}}^3$."
    st2 = f"Suma długości wszystkich krawędzi tego graniastosłupa jest równa ${shown_edges}$ cm."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    return {
        "stem": stem,
        "command": command,
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": [
            f"Wysokość graniastosłupa wynosi $H = {mult} \\cdot {a} = {H}$ cm, a podstawa jest kwadratem o boku ${a}$ cm.",
            f"Objętość: $V = a^2 \\cdot H = {a}^2 \\cdot {H} = {vol}\\text{{ cm}}^3$ -> zdanie pierwsze: **{p1}**.",
            f"Graniastosłup czworokątny ma $8$ krawędzi podstaw i $4$ krawędzie boczne: $8 \\cdot {a} + 4 \\cdot {H} = {edges_sum}$ cm -> zdanie drugie: **{p2}**.",
        ],
    }


@register_template(
    template_id="stereometria_szescian_ab_cd",
    topic_id="geometria_przestrzenna",
    subtype="ab_cd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2021 zad. 14",
)
def gen_szescian_ab_cd(rng):
    a = rng.randint(4, 10)
    Pc = 6 * a * a
    vol = a ** 3
    diag_face = rf"${a}\sqrt{{2}}\text{{ cm}}$"
    wrong_diag = rf"${a}\sqrt{{3}}\text{{ cm}}$"

    corr1 = f"${vol}\\text{{ cm}}^3$"
    wrong1 = f"${6 * a * 4}\\text{{ cm}}^3$" if (6 * a * 4) != vol else f"${vol + 36}\\text{{ cm}}^3$"

    if rng.choice([True, False]):
        opts1 = {"A": corr1, "B": wrong1}
        c1 = "A"
    else:
        opts1 = {"A": wrong1, "B": corr1}
        c1 = "B"

    if rng.choice([True, False]):
        opts2 = {"C": diag_face, "D": wrong_diag}
        c2 = "C"
    else:
        opts2 = {"C": wrong_diag, "D": diag_face}
        c2 = "D"

    stem = f"Pole powierzchni całkowitej pewnego sześcianu jest równe ${Pc}\\text{{ cm}}^2$."
    command = "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D."

    parts = [
        {"prefix": "Objętość tego sześcianu jest równa", "suffix": ".", "options": opts1},
        {"prefix": "Przekątna jednej ściany tego sześcianu ma długość", "suffix": ".", "options": opts2},
    ]

    return {
        "stem": stem,
        "command": command,
        "ab_cd_parts": parts,
        "correct_answer": c1 + c2,
        "solution_steps": [
            f"Ze wzoru $P_c = 6a^2 = {Pc}$ otrzymujemy $a^2 = {a * a}$, czyli krawędź sześcianu ma długość $a = {a}$ cm.",
            f"Objętość sześcianu wynosi $V = a^3 = {a}^3 = {vol}\\text{{ cm}}^3$ (wybór **{c1}**).",
            rf"Ściana sześcianu jest kwadratem o boku ${a}$ cm, więc jej przekątna ma długość $a\sqrt{{2}} = {a}\sqrt{{2}}$ cm (wybór **{c2}**).",
        ],
    }


@register_template(
    template_id="stereometria_akwarium_woda_2pkt",
    topic_id="geometria_przestrzenna",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2021 zad. 19",
    has_diagram=True,
)
def gen_akwarium_2pkt(rng):
    # Akwarium o wymiarach podstawy a cm x b cm i wysokości H cm. Woda sięga do ułamka f1 wysokości.
    # Ile litrów wody trzeba dolać, aby lustro wody znajdowało się d cm poniżej górnej krawędzi?
    a_cm, b_cm = rng.choice([(40, 25), (50, 30), (60, 25), (50, 40)])
    H_cm = rng.choice([30, 36, 40])
    h1_cm = H_cm // 2
    gap_top = rng.choice([4, 5, 6])
    h2_cm = H_cm - gap_top
    dh_cm = h2_cm - h1_cm

    vol_cm3 = a_cm * b_cm * dh_cm
    liters = vol_cm3 / 1000.0

    diag = DiagramSpec(
        kind="cuboid_water",
        params={
            "a_label": f"{a_cm} cm",
            "b_label": f"{b_cm} cm",
            "H_label": f"{H_cm} cm",
            "fill_ratio": 0.5,
        },
        caption="Rysunek pomocniczy",
        width_mm=70.0,
    )

    stem = (
        f"Akwarium ma kształt prostopadłościanu o wymiarach podstawy ${a_cm}\\text{{ cm}} \\times {b_cm}\\text{{ cm}}$ "
        f"oraz wysokości ${H_cm}$ cm. Obecnie woda w tym akwarium sięga dokładnie do połowy jego wysokości."
    )
    command = (
        f"Oblicz, ile litrów wody należy dolać do tego akwarium, aby powierzchnia wody znajdowała się "
        f"${gap_top}$ cm poniżej górnej krawędzi akwarium ($1\\text{{ litr}} = 1\\text{{ dm}}^3 = 1000\\text{{ cm}}^3$). Zapisz obliczenia."
    )

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "correct_answer": f"{pl_num(liters)} l",
        "solution_steps": [
            f"Obecny poziom wody wynosi $h_1 = {H_cm} : 2 = {h1_cm}$ cm. Docelowy poziom wody to $h_2 = {H_cm} - {gap_top} = {h2_cm}$ cm.",
            f"Poziom wody musi wzrosnąć o $\\Delta h = {h2_cm} - {h1_cm} = {dh_cm}$ cm.",
            f"Objętość dolewanej wody wynosi: $V = {a_cm} \\cdot {b_cm} \\cdot {dh_cm} = {pl_num(vol_cm3)}\\text{{ cm}}^3 = {pl_num(liters)}\\text{{ dm}}^3 = {pl_num(liters)}$ l.",
            f"**Odpowiedź:** Do akwarium należy dolać ${pl_num(liters)}$ litrów wody.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyznaczenie różnicy poziomów wody ({dh_cm} cm) lub obliczenie obecnej i docelowej objętości wody.",
            f"2 pkt – obliczenie objętości dolewanej wody i poprawne wyrażenie wyniku w litrach ({pl_num(liters)} l).",
        ],
        "grid_height_mm": 54.0,
    }


@register_template(
    template_id="stereometria_siatka_graniastoslupa_3pkt",
    topic_id="geometria_przestrzenna",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Wzorzec: CKE Maj 2022 zad. 19 / Grudzień 2024 zad. 20",
    has_diagram=True,
)
def gen_siatka_graniastoslupa_3pkt(rng):
    # Siatka graniastosłupa prawidłowego czworokątnego:
    # Wymiar poziomy 3 ścian bocznych = 3a, wymiar pionowy (wysokość H + bok podstawy a) = H + a
    a = rng.randint(6, 15)
    H = rng.randint(a + 4, 26)
    three_a = 3 * a
    h_plus_a = H + a
    vol = a * a * H
    pc = 2 * a * a + 4 * a * H

    diag = DiagramSpec(
        kind="prism_net",
        params={
            "dim_mode": "three_walls",
            "horiz_label": f"{three_a} cm",
            "vert_label": f"{h_plus_a} cm",
        },
        caption="Rysunek pomocniczy",
        width_mm=76.0,
    )

    stem = (
        f"Na rysunku przedstawiono siatkę graniastosłupa prawidłowego czworokątnego oraz zapisano dwa wymiary tej siatki: "
        f"${three_a}$ cm oraz ${h_plus_a}$ cm."
    )
    command = "Oblicz objętość oraz pole powierzchni całkowitej tego graniastosłupa. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "correct_answer": f"V = {pl_num(vol)} cm^3, Pc = {pl_num(pc)} cm^2",
        "solution_steps": [
            f"Ponieważ graniastosłup jest prawidłowy czworokątny, jego podstawą jest kwadrat o boku $a$, a cztery ściany boczne są przystającymi prostokątami o wymiarach $a \\times H$.",
            f"Z poziomego wymiaru obejmującego trzy ściany boczne obliczamy krawędź podstawy: $3a = {three_a}\\text{{ cm}}$, stąd $a = {a}$ cm.",
            f"Z pionowego wymiaru $H + a = {h_plus_a}\\text{{ cm}}$ wyznaczamy wysokość graniastosłupa: $H = {h_plus_a} - {a} = {H}$ cm.",
            f"Objętość: $V = a^2 \\cdot H = {a}^2 \\cdot {H} = {pl_num(vol)}\\text{{ cm}}^3$.",
            f"Pole powierzchni całkowitej: $P_c = 2a^2 + 4aH = 2 \\cdot {a * a} + 4 \\cdot {a} \\cdot {H} = {pl_num(pc)}\\text{{ cm}}^2$.",
            f"**Odpowiedź:** $V = {pl_num(vol)}\\text{{ cm}}^3$ oraz $P_c = {pl_num(pc)}\\text{{ cm}}^2$.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne obliczenie długości krawędzi podstawy (a = {a} cm).",
            f"2 pkt – obliczenie wysokości graniastosłupa (H = {H} cm) oraz jednej z szukanych wielkości (V lub Pc).",
            f"3 pkt – poprawne obliczenie zarówno objętości ({pl_num(vol)} cm^3), jak i pola powierzchni całkowitej ({pl_num(pc)} cm^2).",
        ],
        "grid_height_mm": 64.0,
    }
