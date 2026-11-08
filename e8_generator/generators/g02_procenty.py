"""Dział 2: Procenty, obniżki i podwyżki cen oraz proporcje."""

from __future__ import annotations

from fractions import Fraction

from ..math_text import frac_tex, pl_num, shuffle_abcd
from .base import register_template


@register_template(
    template_id="procenty_przepis_pf",
    topic_id="procenty_proporcje",
    subtype="pf",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2023 zad. 1",
)
def gen_przepis_kulinarny_pf(rng):
    # Składniki na N gofrów (np. 8 lub 12)
    base_n = rng.choice([8, 12])
    mult_num = rng.choice([3, 5])  # np. na 20 lub 30 gofrów (gdy base_n=8 -> 20 to *2.5; gdy base_n=12 -> 30 to *2.5)
    target_n = int(base_n * 2.5) if mult_num == 5 else int(base_n * 1.5)
    ratio = Fraction(target_n, base_n)

    flour_g = rng.choice([240, 280, 320])
    milk_ml = rng.choice([300, 360, 400])
    eggs = 2 if base_n == 8 else 4

    req_flour = int(flour_g * ratio)
    req_eggs = int(eggs * ratio)

    s1_true = rng.choice([True, False])
    shown_flour = req_flour if s1_true else req_flour - 40

    s2_true = rng.choice([True, False])
    # Jaki procent masy mąki stanowi coś lub liczba jajek na target_n
    shown_eggs = req_eggs if s2_true else req_eggs + 1

    table = [
        [f"Składniki na {base_n} gofrów", "Ilość"],
        ["Mąka pszenna", f"{flour_g} g"],
        ["Mleko", f"{milk_ml} ml"],
        ["Jajka", f"{eggs} sztuki"],
    ]

    stem = (
        f"W tabeli podano ilości składników potrzebnych do przygotowania ciasta na ${base_n}$ gofrów. "
        f"Zosia chce przygotować według tego samego przepisu ciasto na ${target_n}$ takich samych gofrów."
    )
    command = "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe."

    st1 = f"Do przygotowania ciasta na ${target_n}$ gofrów Zosia potrzebuje dokładnie ${shown_flour}$ g mąki pszennej."
    st2 = f"Do przygotowania ciasta na ${target_n}$ gofrów Zosia powinna użyć ${shown_eggs}$ jajek."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    return {
        "stem": stem,
        "command": command,
        "table_data": table,
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": [
            f"Stosunek liczby gofrów wynosi ${target_n} : {base_n} = {pl_num(float(ratio))}$.",
            f"Potrzebna ilość mąki: ${flour_g}\\text{{ g}} \\cdot {pl_num(float(ratio))} = {req_flour}\\text{{ g}}$ -> zdanie pierwsze: **{p1}**.",
            f"Potrzebna liczba jajek: ${eggs} \\cdot {pl_num(float(ratio))} = {req_eggs}$ -> zdanie drugie: **{p2}**.",
        ],
    }


@register_template(
    template_id="procenty_trzy_sklepy_abcd",
    topic_id="procenty_proporcje",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2021 zad. 3",
)
def gen_trzy_sklepy_abcd(rng):
    item, item_gen = rng.choice([
        ("łyżwy figurowe", "łyżew"),
        ("hulajnogę miejską", "hulajnogi"),
        ("rakietę tenisową", "rakiety"),
        ("plecak szkolny", "plecaka"),
    ])
    price0 = rng.choice([200, 240, 300, 360])
    pct_alfa = rng.choice([15, 20, 25, 30])
    disc_alfa = price0 * pct_alfa // 100
    p_alfa = price0 - disc_alfa

    # Beta: kwotowa obniżka
    disc_beta = disc_alfa + rng.choice([-12, -8, 8, 12])
    p_beta = price0 - disc_beta

    # Gamma: ułamek ceny (dobierz ułamek różny od pct_alfa/100)
    frac_candidates = [(n, d) for (n, d) in [(1, 4), (1, 5), (3, 10), (2, 5)] if n * 100 != pct_alfa * d]
    f_num, f_den = rng.choice(frac_candidates)
    p_gamma = price0 - (price0 * f_num // f_den)

    # Upewnij się, że wszystkie trzy ceny są parami różne
    while p_beta in (p_alfa, p_gamma):
        disc_beta += 4
        p_beta = price0 - disc_beta

    prices = {"Alfa": p_alfa, "Beta": p_beta, "Gamma": p_gamma}

    best_shop = min(prices, key=prices.get)
    worst_shop = max(prices, key=prices.get)

    correct = f"Najniższa cena po obniżce była w sklepie {best_shop}, a najwyższa – w sklepie {worst_shop}."
    others = [
        f"Najniższa cena po obniżce była w sklepie {worst_shop}, a najwyższa – w sklepie {best_shop}.",
        f"We wszystkich trzech sklepach cena po obniżce była jednakowa.",
        f"Najniższa cena po obniżce była w sklepie {[s for s in ('Alfa', 'Beta', 'Gamma') if s not in (best_shop, worst_shop)][0]}, a najwyższa – w sklepie {best_shop}.",
    ]
    choices, ans = shuffle_abcd(rng, correct, others)

    stem = (
        f"Przed świętami w trzech sklepach sportowych: Alfa, Beta i Gamma, sprzedawano {item} w tej samej cenie "
        f"równej ${price0}$ zł. W styczniu każdy sklep ogłosił promocję:\n"
        f"• w sklepie **Alfa** cenę obniżono o ${pct_alfa}\\%$,\n"
        f"• w sklepie **Beta** cenę obniżono o ${disc_beta}$ zł,\n"
        f"• w sklepie **Gamma** cenę obniżono o {frac_tex(f_num, f_den)} dotychczasowej ceny."
    )
    command = f"Które zdanie prawdziwie opisuje ceny {item_gen} po obniżce? Wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Sklep Alfa: obniżka o ${pct_alfa}\\%$ z ${price0}$ zł to ${disc_alfa}$ zł, więc nowa cena wynosi ${price0} - {disc_alfa} = {p_alfa}$ zł.",
            f"Sklep Beta: nowa cena wynosi ${price0} - {disc_beta} = {p_beta}$ zł.",
            f"Sklep Gamma: obniżka o {frac_tex(f_num, f_den)} z ${price0}$ zł to ${price0 * f_num // f_den}$ zł, więc nowa cena wynosi ${p_gamma}$ zł.",
            f"Najtaniej jest w sklepie **{best_shop}** (${prices[best_shop]}$ zł), a najdrożej w sklepie **{worst_shop}** (${prices[worst_shop]}$ zł). Odpowiedź **{ans}**.",
        ],
    }


@register_template(
    template_id="procenty_ab_cd",
    topic_id="procenty_proporcje",
    subtype="ab_cd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2024 zad. 3",
)
def gen_procenty_ab_cd(rng):
    # Zdanie 1: Liczba X stanowi P% liczby Y
    pct = rng.choice([20, 25, 40, 75, 80])
    whole = rng.choice([60, 80, 120, 160, 200])
    part = whole * pct // 100
    wrong_part = whole * 100 // pct if (whole * 100) % pct == 0 else part + 15

    if rng.choice([True, False]):
        opts1 = {"A": f"${part}$", "B": f"${wrong_part}$"}
        c1 = "A"
    else:
        opts1 = {"A": f"${wrong_part}$", "B": f"${part}$"}
        c1 = "B"

    # Zdanie 2: Liczba o Q% większa od M
    q = rng.choice([15, 20, 30, 35])
    m_val = rng.choice([140, 180, 220, 260])
    inc_val = m_val + (m_val * q // 100)
    wrong_inc = m_val + q

    if rng.choice([True, False]):
        opts2 = {"C": f"${inc_val}$", "D": f"${wrong_inc}$"}
        c2 = "C"
    else:
        opts2 = {"C": f"${wrong_inc}$", "D": f"${inc_val}$"}
        c2 = "D"

    stem = "Rozważmy dwie zależności procentowe między liczbami dodatnimi."
    command = "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D."

    parts = [
        {
            "prefix": f"Liczba stanowiąca ${pct}\\%$ liczby ${whole}$ jest równa",
            "suffix": ".",
            "options": opts1,
        },
        {
            "prefix": f"Liczba o ${q}\\%$ większa od liczby ${m_val}$ jest równa",
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
            f"Pierwsze zdanie: ${pct}\\% \\cdot {whole} = {pl_num(pct / 100)} \\cdot {whole} = {part}$ (wybór **{c1}**).",
            f"Drugie zdanie: liczba o ${q}\\%$ większa od ${m_val}$ to ${m_val} + {q}\\% \\cdot {m_val} = {m_val} + {m_val * q // 100} = {inc_val}$ (wybór **{c2}**).",
        ],
    }


@register_template(
    template_id="procenty_uzasadnij_sklepy_2pkt",
    topic_id="procenty_proporcje",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2025 zad. 16",
)
def gen_uzasadnij_ceny_sklepy_2pkt(rng):
    # W sklepie B cena stanowi p1% ceny w A, a w sklepie C stanowi p2% ceny w B (np. 80% i 120% -> 0,96x < x)
    p1, p2 = rng.choice([(80, 120), (75, 130), (85, 115), (70, 140), (90, 110)])
    prod_pct = Fraction(p1 * p2, 100)  # w procentach ceny A, np. 96% lub 97,5%
    prod_dec = float(prod_pct) / 100.0

    item = rng.choice(["hulajnogi", "deskorolki", "kurtki zimowej", "roweru"])
    stem = (
        f"Takie same {item} są sprzedawane w trzech sklepach: A, B oraz C. "
        f"W sklepie B cena {item} stanowi ${p1}\\%$ ceny w sklepie A. "
        f"Natomiast w sklepie C cena tej {item} stanowi ${p2}\\%$ ceny w sklepie B."
    )
    command = f"Uzasadnij, że cena {item} w sklepie C jest niższa od ceny tej {item} w sklepie A. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"Cena w sklepie C stanowi {pl_num(float(prod_pct))}% ceny w sklepie A ({pl_num(float(prod_pct))}% < 100%).",
        "solution_steps": [
            f"Oznaczmy przez $x$ ($x > 0$) cenę {item} w sklepie A.",
            f"Wtedy cena w sklepie B wynosi ${pl_num(p1 / 100)}x$.",
            f"Cena w sklepie C stanowi ${p2}\\%$ ceny w sklepie B, czyli wynosi: "
            f"${pl_num(p2 / 100)} \\cdot {pl_num(p1 / 100)}x = {pl_num(prod_dec)}x = {pl_num(float(prod_pct))}\\% \\cdot x$.",
            f"Ponieważ ${pl_num(prod_dec)}x < x$ (dla każdego $x > 0$), cena w sklepie C jest niższa od ceny w sklepie A, co należało uzasadnić.",
        ],
        "scoring_scheme": [
            f"1 pkt – zapisanie ceny w sklepie B jako {pl_num(p1/100)}x oraz w sklepie C jako iloczynu {pl_num(p2/100)} · {pl_num(p1/100)}x (lub poprawne sprawdzenie na konkretnej cenie z komentarzem o proporcjonalności).",
            f"2 pkt – obliczenie {pl_num(prod_dec)}x ({pl_num(float(prod_pct))}% ceny w A) i sformułowanie pełnego wniosku porównującego z x.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="procenty_dwukrotna_zmiana_3pkt",
    topic_id="procenty_proporcje",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Wzorzec: CKE Maj 2020 zad. 18",
)
def gen_dwukrotna_zmiana_ceny_3pkt(rng):
    # Cena początkowa x -> podwyżka o p1% -> obniżka o p2% -> końcowa cena K zł. Oblicz x!
    p1, p2 = rng.choice([(20, 25), (25, 20), (10, 20), (20, 15), (30, 20)])
    # Współczynnik (100+p1)*(100-p2)/10000
    factor = Fraction((100 + p1) * (100 - p2), 10000)
    # Wybierzmy x tak, by po pierwszej i drugiej zmianie były liczby całkowite
    base_unit = factor.denominator
    x0 = base_unit * rng.randint(12, 30)
    if x0 < 200:
        x0 *= 10
    after_up = int(x0 * Fraction(100 + p1, 100))
    final_price = int(after_up * Fraction(100 - p2, 100))
    diff_zl = abs(x0 - final_price)

    prod_name = rng.choice(["konsoli do gier", "aparatu fotograficznego", "zegarka sportowego", "tabletu"])
    stem = (
        f"Cenę pewnego modelu {prod_name} najpierw podwyższono o ${p1}\\%$, a po miesiącu nową cenę obniżono o ${p2}\\%$. "
        f"Po obu tych zmianach {prod_name.split()[0]} kosztuje ${final_price}$ zł."
    )
    command = (
        f"Oblicz początkową cenę {prod_name} (przed podwyżką) oraz o ile złotych cena końcowa różni się "
        f"od ceny początkowej. Zapisz obliczenia."
    )

    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"Cena początkowa: {x0} zł, różnica: {diff_zl} zł",
        "solution_steps": [
            f"Oznaczmy cenę początkową przez $x$. Po podwyżce o ${p1}\\%$ cena wynosiła ${pl_num((100 + p1) / 100)}x$.",
            f"Po kolejnej obniżce o ${p2}\\%$ nowa cena stanowiła ${100 - p2}\\%$ poprzedniej ceny: "
            f"${pl_num((100 - p2) / 100)} \\cdot {pl_num((100 + p1) / 100)}x = {pl_num(float(factor))}x$.",
            f"Z warunków zadania otrzymujemy równanie: ${pl_num(float(factor))}x = {final_price}$, skąd $x = {final_price} : {pl_num(float(factor))} = {x0}$ (zł).",
            f"Różnica między ceną początkową a końcową wynosi: $|{x0} - {final_price}| = {diff_zl}$ zł.",
            f"**Odpowiedź:** Cena początkowa wynosiła ${x0}$ zł, a cena końcowa różni się od niej o ${diff_zl}$ zł.",
        ],
        "scoring_scheme": [
            "1 pkt – zapisanie ceny po pierwszej zmianie lub po obu zmianach za pomocą wyrażenia z niewiadomą x.",
            f"2 pkt – ułożenie i rozwiązanie równania, wyznaczenie ceny początkowej ({x0} zł).",
            f"3 pkt – obliczenie różnicy kwotowej ({diff_zl} zł) i zapisanie pełnej odpowiedzi.",
        ],
        "grid_height_mm": 62.0,
    }
