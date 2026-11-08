"""Dział 4: Pierwiastki kwadratowe i sześcienne oraz szacowanie."""

from __future__ import annotations

import math

from ..math_text import pl_num, shuffle_abcd
from ..models import DiagramSpec
from .base import register_template


@register_template(
    template_id="pierwiastki_dzialania_ab_cd",
    topic_id="pierwiastki",
    subtype="ab_cd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2023 zad. 5",
)
def gen_pierwiastki_ab_cd(rng):
    # Zdanie 1: sqrt(a^2) - sqrt(b^2) vs sqrt(a^2 - b^2)
    a, b = rng.choice([(9, 7), (11, 6), (12, 8), (13, 9), (15, 7)])
    sq_a, sq_b = a * a, b * b
    corr1 = f"${a - b}$"
    wrong1 = rf"$\sqrt{{{sq_a - sq_b}}}$"

    if rng.choice([True, False]):
        opts1 = {"A": corr1, "B": wrong1}
        c1 = "A"
    else:
        opts1 = {"A": wrong1, "B": corr1}
        c1 = "B"

    # Zdanie 2: wyłączanie czynnika przed pierwiastek np. sqrt(75) = 5 sqrt(3)
    k, rad = rng.choice([(4, 3), (5, 3), (6, 2), (5, 2), (4, 5), (3, 6)])
    inside = k * k * rad
    corr2 = rf"${k}\sqrt{{{rad}}}$"
    wrong2 = rf"${rad}\sqrt{{{k}}}$"

    if rng.choice([True, False]):
        opts2 = {"C": corr2, "D": wrong2}
        c2 = "C"
    else:
        opts2 = {"C": wrong2, "D": corr2}
        c2 = "D"

    stem = "Dane są dwa wyrażenia zawierające pierwiastki kwadratowe."
    command = "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D."

    parts = [
        {
            "prefix": rf"Wartość wyrażenia $\sqrt{{{sq_a}}} - \sqrt{{{sq_b}}}$ jest równa",
            "suffix": ".",
            "options": opts1,
        },
        {
            "prefix": rf"Liczba $\sqrt{{{inside}}}$ zapisana w najprostszej postaci jest równa",
            "suffix": ".",
            "options": opts2,
        },
    ]

    return {
        "stem": stem,
        "command": command,
        "ab_cd_parts": parts,
        "correct_answer": c1 + c2,
        "solution_steps": [
            rf"Obliczamy każdy pierwiastek osobno: $\sqrt{{{sq_a}}} - \sqrt{{{sq_b}}} = {a} - {b} = {a - b}$ (wybór **{c1}**).",
            rf"Wyłączamy czynnik przed znak pierwiastka: $\sqrt{{{inside}}} = \sqrt{{{k * k} \cdot {rad}}} = {k}\sqrt{{{rad}}}$ (wybór **{c2}**).",
        ],
    }


@register_template(
    template_id="pierwiastki_szacowanie_os_abcd",
    topic_id="pierwiastki",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2022 zad. 6",
    has_diagram=True,
)
def gen_szacowanie_pierwiastka_abcd(rng):
    # Punkt P leży między n a n+1 na osi liczbowej; pytamy która liczba z pierwiastkiem odpowiada P
    n = rng.randint(5, 9)
    # Wybierz liczbę podpierwiastkową m między n^2 + 2 a (n+1)^2 - 2
    low, high = n * n + 2, (n + 1) * (n + 1) - 2
    m = rng.randint(low, high)
    approx_x = math.sqrt(m)

    corr = rf"$\sqrt{{{m}}}$"
    d1 = rf"$\sqrt{{{max(2, (n - 1) ** 2 - 3)}}}$"
    d2 = rf"$\sqrt{{{(n - 1) ** 2 + 2}}}$"
    d3 = rf"$\sqrt{{{(n + 1) ** 2 + 4}}}$"

    choices, ans = shuffle_abcd(rng, corr, [d1, d2, d3])

    ticks = list(range(n - 2, n + 4))
    labeled = {t: str(t) for t in ticks}
    diag = DiagramSpec(
        kind="number_line",
        params={
            "ticks": ticks,
            "labeled_ticks": labeled,
            "points": [{"x": round(approx_x, 2), "label": "P"}],
        },
        width_mm=96.0,
    )

    stem = f"Na osi liczbowej zaznaczono punkt $P$, który znajduje się między liczbami ${n}$ oraz ${n + 1}$."
    command = "Która z podanych liczb może być współrzędną punktu $P$? Wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            rf"Zapisujemy liczby całkowite ${n}$ i ${n + 1}$ w postaci pierwiastków kwadratowych: "
            rf"${n} = \sqrt{{{n * n}}}$ oraz ${n + 1} = \sqrt{{{(n + 1) ** 2}}}$.",
            rf"Szukamy liczby podpierwiastkowej większej od ${n * n}$ i mniejszej od ${(n + 1) ** 2}$.",
            rf"Warunek $\sqrt{{{n * n}}} < \sqrt{{{m}}} < \sqrt{{{(n + 1) ** 2}}}$ spełnia liczba {corr} (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="pierwiastki_szescienne_pf",
    topic_id="pierwiastki",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2022 zad. 5",
)
def gen_pierwiastki_pf(rng):
    # Pierwiastek sześcienny z liczby ujemnej i iloczyn pierwiastków
    c = rng.choice([2, 3, 4, 5])
    cube = c ** 3
    s1_true = rng.choice([True, False])
    shown_c = -c if s1_true else c

    a, b = rng.choice([(2, 8), (3, 12), (2, 18), (3, 27), (5, 20)])
    prod_root = int(round(math.sqrt(a * b)))
    s2_true = rng.choice([True, False])
    shown_prod = prod_root if s2_true else (a + b) // 2

    st1 = rf"Wartość pierwiastka sześciennego $\sqrt[3]{{-{cube}}}$ jest równa ${pl_num(shown_c)}$."
    st2 = rf"Iloczyn $\sqrt{{{a}}} \cdot \sqrt{{{b}}}$ jest równy ${shown_prod}$."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    return {
        "stem": "Przeanalizuj poniższe własności pierwiastków kwadratowych i sześciennych.",
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": [
            rf"Ponieważ $(-{c})^3 = -{cube}$, mamy $\sqrt[3]{{-{cube}}} = -{c}$ -> zdanie pierwsze: **{p1}**.",
            rf"Korzystamy ze wzoru na iloczyn pierwiastków: $\sqrt{{{a}}} \cdot \sqrt{{{b}}} = \sqrt{{{a * b}}} = {prod_root}$ -> zdanie drugie: **{p2}**.",
        ],
    }


@register_template(
    template_id="pierwiastki_obwod_uzasadnij_2pkt",
    topic_id="pierwiastki",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2024 zad. 16",
)
def gen_pierwiastki_obwod_2pkt(rng):
    # Prostokąt ma boki sqrt(k1^2 * r) oraz sqrt(k2^2 * r). Uzasadnij, że obwód jest większy od T cm.
    r, r_low_num = rng.choice([
        (2, 1.4),   # sqrt(2) > 1,4
        (3, 1.7),   # sqrt(3) > 1,7
        (5, 2.2),   # sqrt(5) > 2,2
    ])
    k1, k2 = rng.choice([(2, 3), (3, 4), (2, 5), (3, 5)])
    n1 = k1 * k1 * r
    n2 = k2 * k2 * r
    coef_perim = 2 * (k1 + k2)
    # coef_perim * sqrt(r): np. 2*(2+3)=10; dla r=3: 10*sqrt(3) = sqrt(300) > 17
    sq_perim = (coef_perim ** 2) * r
    threshold = int(math.isqrt(sq_perim - 1))  # największa całkowita mniejsza od sqrt(sq_perim)

    stem = (
        rf"Dany jest prostokąt o sąsiednich bokach długości $a = \sqrt{{{n1}}}\text{{ cm}}$ "
        rf"oraz $b = \sqrt{{{n2}}}\text{{ cm}}$."
    )
    command = f"Uzasadnij, że obwód tego prostokąta jest większy od ${threshold}$ cm. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"Obwód wynosi {coef_perim}√{r} = √{sq_perim} cm > √{threshold**2} cm = {threshold} cm.",
        "solution_steps": [
            rf"Wyłączamy czynnik przed znak pierwiastka w długościach boków: "
            rf"$a = \sqrt{{{k1 * k1} \cdot {r}}} = {k1}\sqrt{{{r}}}\text{{ cm}}$ oraz "
            rf"$b = \sqrt{{{k2 * k2} \cdot {r}}} = {k2}\sqrt{{{r}}}\text{{ cm}}$.",
            rf"Obliczamy obwód prostokąta: $Obw = 2a + 2b = 2 \cdot {k1}\sqrt{{{r}}} + 2 \cdot {k2}\sqrt{{{r}}} = {coef_perim}\sqrt{{{r}}}\text{{ cm}}$.",
            rf"Włączamy czynnik pod znak pierwiastka: ${coef_perim}\sqrt{{{r}}} = \sqrt{{{coef_perim ** 2} \cdot {r}}} = \sqrt{{{sq_perim}}}$.",
            rf"Ponieważ ${threshold} = \sqrt{{{threshold ** 2}}}$ oraz $\sqrt{{{sq_perim}}} > \sqrt{{{threshold ** 2}}}$, obwód jest większy od ${threshold}$ cm.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyłączenie czynnika przed znak pierwiastka i zapisanie obwodu w postaci {coef_perim}√{r} cm.",
            f"2 pkt – poprawne porównanie liczby {coef_perim}√{r} z liczbą {threshold} (np. przez włączenie pod pierwiastek: √{sq_perim} > √{threshold**2}) i wniosek.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="pierwiastki_kwadraty_3pkt",
    topic_id="pierwiastki",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Wzorzec: CKE Czerwiec 2021 zad. 18",
)
def gen_pierwiastki_kwadraty_3pkt(rng):
    # Dwa kwadraty K1 o polu P1 = m1^2 * r i K2 o polu P2 = m2^2 * r, zbudowano z nich prostokąt lub porównano obwody i przekątne
    m1, m2 = rng.choice([(2, 5), (3, 5), (2, 6), (3, 7)])
    r = rng.choice([2, 3])
    P1 = (m1 ** 2) * r
    P2 = (m2 ** 2) * r
    # Z drutu o długości równej sumie obwodów K1 i K2 uformowano trójkąt równoboczny. Oblicz bok i pole (lub wysokość) tego trójkąta!
    # Dobierzmy m1 + m2 podzielne przez 3, żeby bok trójkąta równobocznego wyszedł całkowity*sqrt(r)!
    m1, m2 = rng.choice([(2, 4), (2, 7), (4, 5), (3, 6)])
    P1 = (m1 ** 2) * r
    P2 = (m2 ** 2) * r
    sum_perim_coef = 4 * (m1 + m2)  # podzielne przez 3, bo m1+m2 in {6, 9, 9, 9}
    tri_side_coef = sum_perim_coef // 3
    # Dla r=3 wysokość trójkąta równobocznego h = a*sqrt(3)/2 = tri_side_coef * sqrt(3) * sqrt(3) / 2 = tri_side_coef * 3 / 2!
    r = 3
    P1 = (m1 ** 2) * r
    P2 = (m2 ** 2) * r
    # Ponieważ sum_perim_coef = 4*(m1+m2) jest parzyste, tri_side_coef jest parzyste! Więc h jest całkowite!
    h_val = (tri_side_coef * 3) // 2

    stem = (
        f"Dane są dwa kwadraty: kwadrat $K_1$ o polu ${P1}\\text{{ cm}}^2$ oraz kwadrat $K_2$ o polu ${P2}\\text{{ cm}}^2$. "
        f"Z drutu o długości równej sumie obwodów obu tych kwadratów zbudowano ramkę w kształcie trójkąta równobocznego."
    )
    command = "Oblicz wysokość zbudowanego trójkąta równobocznego. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"{h_val} cm",
        "solution_steps": [
            rf"Obliczamy długości boków kwadratów: $a_1 = \sqrt{{{P1}}} = {m1}\sqrt{{3}}\text{{ cm}}$ oraz "
            rf"$a_2 = \sqrt{{{P2}}} = {m2}\sqrt{{3}}\text{{ cm}}$.",
            rf"Suma obwodów obu kwadratów wynosi: $4a_1 + 4a_2 = 4 \cdot {m1}\sqrt{{3}} + 4 \cdot {m2}\sqrt{{3}} = {sum_perim_coef}\sqrt{{3}}\text{{ cm}}$.",
            rf"Długość boku trójkąta równobocznego wynosi: $a = {sum_perim_coef}\sqrt{{3}} : 3 = {tri_side_coef}\sqrt{{3}}\text{{ cm}}$.",
            rf"Obliczamy wysokość trójkąta równobocznego ze wzoru $h = \frac{{a\sqrt{{3}}}}{{2}}$: "
            rf"$h = \frac{{{tri_side_coef}\sqrt{{3}} \cdot \sqrt{{3}}}}{{2}} = \frac{{{tri_side_coef} \cdot 3}}{{2}} = {h_val}\text{{ cm}}$.",
            f"**Odpowiedź:** Wysokość zbudowanego trójkąta równobocznego jest równa ${h_val}$ cm.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyznaczenie długości boków obu kwadratów ({m1}√3 cm oraz {m2}√3 cm).",
            f"2 pkt – obliczenie sumy obwodów ({sum_perim_coef}√3 cm) oraz boku trójkąta równobocznego ({tri_side_coef}√3 cm).",
            f"3 pkt – zastosowanie wzoru na wysokość trójkąta równobocznego i podanie wyniku {h_val} cm.",
        ],
        "grid_height_mm": 62.0,
    }
