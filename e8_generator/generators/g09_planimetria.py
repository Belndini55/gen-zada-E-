"""Dział 9: Geometria płaska – kąty, trójkąty, czworokąty, okrąg i twierdzenie Pitagorasa."""

from __future__ import annotations

import math

from ..math_text import pl_num, shuffle_abcd
from ..models import DiagramSpec
from .base import register_template


@register_template(
    template_id="planimetria_katy_rownolegle_abcd",
    topic_id="geometria_plaska",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2021 zad. 12",
    has_diagram=True,
)
def gen_katy_rownolegle_abcd(rng):
    obtuse = rng.randint(112, 146)
    alpha = 180 - obtuse

    corr = f"${alpha}^\\circ$"
    distractors = [
        f"${obtuse}^\\circ$",
        f"${90 - (alpha // 2)}^\\circ$",
        f"${alpha + 10}^\\circ$",
    ]
    choices, ans = shuffle_abcd(rng, corr, distractors)

    diag = DiagramSpec(
        kind="parallel_angles",
        params={"top_label": f"{obtuse}°", "bottom_label": "α", "mode": "alternate"},
        caption="Rysunek pomocniczy",
        width_mm=72.0,
    )

    stem = (
        f"Na rysunku proste $k$ oraz $l$ są równoległe i przecięte trzecią prostą. "
        f"Jeden z utworzonych kątów rozwartych ma miarę ${obtuse}^\\circ$."
    )
    command = "Miara kąta ostrego $\\alpha$ zaznaczonego na rysunku jest równa – wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Kąt przyległy do kąta o mierze ${obtuse}^\\circ$ ma miarę $180^\\circ - {obtuse}^\\circ = {alpha}^\\circ$.",
            f"Z własności kątów odpowiadających (i naprzemianległych) przy prostych równoległych $k \\parallel l$ "
            f"wynika, że $\\alpha = {alpha}^\\circ$ (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="planimetria_okrag_cieciwa_abcd",
    topic_id="geometria_plaska",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Grudzień 2024 zad. 15",
    has_diagram=True,
)
def gen_okrag_cieciwa_abcd(rng):
    # Średnica 2R, cięciwa AB = 2*half_c -> odległość d od środka S: d^2 + half_c^2 = R^2
    half_c, d_dist, R = rng.choice([
        (6, 8, 10),
        (8, 6, 10),
        (5, 12, 13),
        (12, 5, 13),
        (9, 12, 15),
        (12, 16, 20),
    ])
    diam = 2 * R
    chord = 2 * half_c

    corr = f"${d_dist}$ cm"
    distractors = [
        f"${R}$ cm",
        f"${abs(diam - chord)}$ cm",
        f"${half_c}$ cm" if half_c != d_dist else f"${d_dist + 2}$ cm",
    ]
    choices, ans = shuffle_abcd(rng, corr, distractors)

    diag = DiagramSpec(
        kind="circle_chord",
        params={"chord_label": f"{chord} cm", "show_dist": True},
        caption="Rysunek pomocniczy",
        width_mm=58.0,
    )

    stem = (
        f"Dany jest okrąg o środku $S$, którego **średnica** ma długość ${diam}$ cm. "
        f"Odcinek $AB$ o długości ${chord}$ cm jest cięciwą tego okręgu (zobacz rysunek)."
    )
    command = "Odległość środka $S$ tego okręgu od cięciwy $AB$ jest równa – wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Promień okręgu jest równy połowie średnicy: $r = {diam} : 2 = {R}$ cm.",
            f"Rzut prostokątny środka $S$ na cięciwę $AB$ dzieli tę cięciwę na połowy o długości ${chord} : 2 = {half_c}$ cm.",
            f"Z twierdzenia Pitagorasa dla trójkąta prostokątnego: $d = \\sqrt{{{R}^2 - {half_c}^2}} = \\sqrt{{{R*R - half_c*half_c}}} = {d_dist}$ cm (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="planimetria_kwadrat_z_prostokatow_uzasadnienie",
    topic_id="geometria_plaska",
    subtype="uzasadnienie",
    points=1,
    difficulty=3,
    cke_ref="Wzorzec: CKE Maj 2023 zad. 13",
)
def gen_kwadrat_z_figur_uzasadnienie(rng):
    # Mamy trzy prostokąty o łącznym polu równym polu kwadratu a^2 (np. 49 lub 64 cm^2),
    # ale czasami jeden z prostokątów ma bok dłuższy od a (więc NIE da się bez rozcinania!), a czasami da się ułożyć!
    side = rng.choice([7, 8, 9])
    sq_area = side * side
    possible = rng.choice([True, False])

    if possible:
        # Prostokąt F1: side x 3, F2: 4 x (side-3), F3: (side-4) x (side-3) -> idealny rozkład kwadratu side x side!
        h1 = 3
        h2 = side - h1
        w2 = 4
        w3 = side - w2
        dims = [(side, h1), (w2, h2), (w3, h2)]
        ans_ab = "A"
        r_corr = (
            f"suma pól tych trzech prostokątów jest równa ${sq_area}\\text{{ cm}}^2$, a z prostokątów "
            f"${w2}\\text{{ cm}} \\times {h2}\\text{{ cm}}$ oraz ${w3}\\text{{ cm}} \\times {h2}\\text{{ cm}}$ można złożyć prostokąt "
            f"${side}\\text{{ cm}} \\times {h2}\\text{{ cm}}$, który wraz z $F_1$ tworzy kwadrat o boku ${side}$ cm."
        )
    else:
        # Suma pól też równa side^2, ale jeden bok > side! Np. side=7 (pole 49): F1 ma 9 x 3 = 27, F2 ma 5 x 2 = 10, F3 ma 6 x 2 = 12 (razem 49!)
        big_len = side + 2
        f1_area = big_len * 3
        rem = sq_area - f1_area  # dla side=7: 49-27=22; dla side=8: 64-30=34; dla side=9: 81-33=48 (wszystkie parzyste!)
        half_rem = rem // 2
        w_a = half_rem // 2
        w_b = half_rem - w_a
        dims = [(big_len, 3), (w_a, 2), (w_b, 2)]
        ans_ab = "B"
        r_corr = (
            f"kwadrat o polu ${sq_area}\\text{{ cm}}^2$ ma bok długości ${side}$ cm, natomiast prostokąt $F_1$ "
            f"ma bok długości ${big_len}$ cm, który jest dłuższy od boku (a nawet nie mieści się wzdłuż boku) tego kwadratu."
        )

    r_w1 = f"suma obwodów figur $F_1$, $F_2$, $F_3$ różni się od obwodu kwadratu o boku ${side}$ cm."
    r_w2 = (
        f"suma pól figur $F_1$, $F_2$, $F_3$ jest {'różna od' if possible else 'równa'} ${sq_area}\\text{{ cm}}^2$, "
        f"co zawsze wystarcza do ułożenia kwadratu bez rozcinania."
    )

    r_list = [r_corr, r_w1, r_w2]
    rng.shuffle(r_list)
    r_dict = {str(i + 1): r_list[i] for i in range(3)}
    c_num = next(k for k, v in r_dict.items() if v == r_corr)

    stem = (
        f"Dane są trzy prostokąty o następujących wymiarach:\n"
        f"• $F_1$: ${dims[0][0]}\\text{{ cm}} \\times {dims[0][1]}\\text{{ cm}}$,\n"
        f"• $F_2$: ${dims[1][0]}\\text{{ cm}} \\times {dims[1][1]}\\text{{ cm}}$,\n"
        f"• $F_3$: ${dims[2][0]}\\text{{ cm}} \\times {dims[2][1]}\\text{{ cm}}$.\n"
        f"Wszystkie trzy prostokąty należy wykorzystać w całości (bez rozcinania i bez nakładania na siebie)."
    )
    command = (
        f"Czy z prostokątów $F_1$, $F_2$, $F_3$ można ułożyć kwadrat o polu ${sq_area}\\text{{ cm}}^2$? "
        f"Wybierz odpowiedź A albo B i jej uzasadnienie spośród 1., 2. albo 3."
    )

    return {
        "stem": stem,
        "command": command,
        "justification_data": {
            "choices_ab": {"A": "Tak,", "B": "Nie,"},
            "connector": "ponieważ",
            "reasons": r_dict,
        },
        "correct_answer": f"{ans_ab}{c_num}",
        "solution_steps": [
            f"Kwadrat o polu ${sq_area}\\text{{ cm}}^2$ ma bok długości $\\sqrt{{{sq_area}}} = {side}$ cm.",
            f"Suma pól prostokątów wynosi ${dims[0][0]*dims[0][1]} + {dims[1][0]*dims[1][1]} + {dims[2][0]*dims[2][1]} = {sq_area}\\text{{ cm}}^2$, "
            f"jednak musimy jeszcze sprawdzić wymiary boków poszczególnych prostokątów.",
            f"Poprawna odpowiedź z uzasadnieniem to **{ans_ab}{c_num}**.",
        ],
    }


@register_template(
    template_id="planimetria_trapez_prostokatny_2pkt",
    topic_id="geometria_plaska",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2022 zad. 18",
    has_diagram=True,
)
def gen_trapez_prostokatny_2pkt(rng):
    # Trapez prostokątny o podstawach a > b i wysokości h -> ramię pochyłe c z Pitagorasa!
    diff_ab, h, c = rng.choice([
        (6, 8, 10),
        (8, 6, 10),
        (5, 12, 13),
        (9, 12, 15),
    ])
    b = rng.randint(6, 14)
    a = b + diff_ab
    perim = a + b + h + c
    area = (a + b) * h // 2

    diag = DiagramSpec(
        kind="trapezoid",
        params={
            "trap_kind": "right",
            "a_label": f"{a} cm",
            "b_label": f"{b} cm",
            "h_label": "",
            "c_label": f"{c} cm",
        },
        caption="Rysunek pomocniczy",
        width_mm=68.0,
    )

    stem = (
        f"Dany jest trapez prostokątny $ABCD$ o podstawach $|AB| = {a}$ cm oraz $|DC| = {b}$ cm. "
        f"Dłuższe ramię $BC$ tego trapezu ma długość ${c}$ cm (zobacz rysunek)."
    )
    command = "Oblicz pole tego trapezu. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "correct_answer": f"{area} cm^2",
        "solution_steps": [
            f"Opuszczamy wysokość z wierzchołka $C$ na podstawę $AB$. Odcięty odcinek przy wierzchołku $B$ ma długość "
            f"${a} - {b} = {diff_ab}$ cm.",
            f"Z twierdzenia Pitagorasa obliczamy wysokość $h$ trapezu: "
            f"$h = \\sqrt{{{c}^2 - {diff_ab}^2}} = \\sqrt{{{c*c - diff_ab*diff_ab}}} = {h}$ cm.",
            f"Obliczamy pole trapezu: $P = \\frac{{({a} + {b}) \\cdot {h}}}{{2}} = \\frac{{{a + b} \\cdot {h}}}{{2}} = {area}\\text{{ cm}}^2$.",
            f"**Odpowiedź:** Pole trapezu jest równe ${area}\\text{{ cm}}^2$.",
        ],
        "scoring_scheme": [
            f"1 pkt – zastosowanie twierdzenia Pitagorasa i poprawne obliczenie wysokości trapezu (h = {h} cm).",
            f"2 pkt – poprawne obliczenie pola trapezu ({area} cm^2).",
        ],
        "grid_height_mm": 52.0,
    }


@register_template(
    template_id="planimetria_trojkat_rownoramienny_3pkt",
    topic_id="geometria_plaska",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Wzorzec: CKE Czerwiec 2025 zad. 19",
    has_diagram=True,
)
def gen_trojkat_rownoramienny_pole_3pkt(rng):
    # Trójkąt równoramienny o obwodzie Obw, w którym każde z ramion jest o d cm dłuższe (lub krótsze) od podstawy!
    # Dobierzmy tak, aby połowa podstawy, wysokość i ramię tworzyły trójkę pitagorejską!
    # Np. (half_a, h, b):
    # - (5, 12, 13): podstawa a=10, ramię b=13 -> b jest o 3 cm dłuższe od podstawy! Obwód = 36, pole = 60 (DOKŁADNIE jak CKE Czerwiec 2025!)
    # - (6, 8, 10): podstawa a=12, ramię b=10 -> ramię jest o 2 cm krótsze od podstawy! Obwód = 32, pole = 48
    # - (8, 15, 17): podstawa a=16, ramię b=17 -> ramię o 1 cm dłuższe! Obwód = 50, pole = 120
    # - (9, 12, 15): podstawa a=18, ramię b=15 -> ramię o 3 cm krótsze! Obwód = 48, pole = 108
    # - (10, 24, 26): podstawa a=20, ramię b=26 -> ramię o 6 cm dłuższe! Obwód = 72, pole = 240
    half_a, h, arm = rng.choice([
        (5, 12, 13),
        (6, 8, 10),
        (8, 15, 17),
        (9, 12, 15),
        (10, 24, 26),
    ])
    base = 2 * half_a
    perim = base + 2 * arm
    diff = arm - base
    area = half_a * h

    rel_phrase = (
        f"o ${diff}$ cm dłuższe od podstawy $AB$"
        if diff > 0
        else f"o ${abs(diff)}$ cm krótsze od podstawy $AB$"
    )
    eq_str = f"x + 2(x + {diff}) = {perim}" if diff > 0 else f"x + 2(x - {abs(diff)}) = {perim}"

    diag = DiagramSpec(
        kind="isosceles_triangle",
        params={"base_label": "x", "arm_label": "", "show_height": True, "height_label": "h"},
        caption="Rysunek pomocniczy",
        width_mm=65.0,
    )

    stem = (
        f"Dany jest trójkąt równoramienny $ABC$ o podstawie $AB$ i ramionach $AC$ oraz $BC$. "
        f"Obwód tego trójkąta jest równy ${perim}$ cm, a każde z jego ramion jest {rel_phrase}."
    )
    command = "Oblicz pole trójkąta $ABC$. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "correct_answer": f"{area} cm^2",
        "solution_steps": [
            f"Oznaczmy długość podstawy $|AB|$ przez $x$. Korzystając z obwodu trójkąta, zapisujemy równanie: "
            f"${eq_str}$, skąd $3x = {3 * base}$, czyli $x = {base}$ cm.",
            f"Zatem podstawa ma długość $|AB| = {base}$ cm, a ramię $|AC| = |BC| = {arm}$ cm.",
            f"Wysokość $h$ opuszczona na podstawę dzieli ją na dwie równe części po ${half_a}$ cm. "
            f"Z twierdzenia Pitagorasa: $h = \\sqrt{{{arm}^2 - {half_a}^2}} = \\sqrt{{{arm*arm - half_a*half_a}}} = {h}$ cm.",
            f"Obliczamy pole trójkąta: $P = \\frac{{1}}{{2}} \\cdot {base} \\cdot {h} = {area}\\text{{ cm}}^2$.",
            f"**Odpowiedź:** Pole trójkąta $ABC$ jest równe ${area}\\text{{ cm}}^2$.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyznaczenie długości podstawy ({base} cm) i ramienia ({arm} cm) trójkąta.",
            f"2 pkt – zastosowanie twierdzenia Pitagorasa i obliczenie wysokości opuszczonej na podstawę (h = {h} cm).",
            f"3 pkt – obliczenie pola trójkąta ({area} cm^2) i zapisanie odpowiedzi.",
        ],
        "grid_height_mm": 64.0,
    }
