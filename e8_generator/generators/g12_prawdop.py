"""Dział 12: Prawdopodobieństwo klasyczne i elementy kombinatoryki."""

from __future__ import annotations

from math import gcd

from ..math_text import frac_tex, pl_num, shuffle_abcd
from .base import register_template


@register_template(
    template_id="prawdop_liczby_trzycyfrowe_abcd",
    topic_id="prawdopodobienstwo",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2022 zad. 3",
)
def gen_liczby_trzycyfrowe_suma_cyfr_abcd(rng):
    # Spośród wszystkich liczb trzycyfrowych o sumie cyfr równej S (gdzie 4 <= S <= 9) wybrano największą i najmniejszą
    S = rng.randint(5, 9)
    max_num = S * 100                 # np. dla S=6: 600
    min_num = 100 + (S - 1)           # np. dla S=6: 105! (bo cyfra setek >= 1, dziesiątek = 0, jedności = S-1)
    ask_diff = rng.choice([True, False])

    if ask_diff:
        res = max_num - min_num
        q_word = "Różnica"
        op_sign = "-"
        # Typowe błędy: najmniejsza jako 00S, albo 1(S-1)0, albo brak zer (np. 11(S-2) i (S-2)11)
        d1 = f"${max_num - (100 + (S - 1) * 10)}$"
        d2 = f"${(S - 2) * 100 + 11 - (110 + (S - 2))}$"
        d3 = f"${max_num + min_num}$"
    else:
        res = max_num + min_num
        q_word = "Suma"
        op_sign = "+"
        d1 = f"${max_num + (100 + (S - 1) * 10)}$"
        d2 = f"${max_num + S}$"
        d3 = f"${max_num - min_num}$"

    corr = f"${res}$"
    choices, ans = shuffle_abcd(rng, corr, [d1, d2, d3])

    stem = f"Spośród wszystkich liczb naturalnych trzycyfrowych, których suma cyfr jest równa ${S}$, wybrano liczbę największą oraz liczbę najmniejszą."
    command = f"{q_word} tych dwóch wybranych liczb jest równa – wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Aby liczba trzycyfrowa o sumie cyfr ${S}$ była największa, cyfra setek musi być jak największa: jest to liczba ${max_num}$.",
            f"Aby liczba trzycyfrowa była najmniejsza, cyfra setek musi być równa $1$, cyfra dziesiątek $0$, a cyfra jedności ${S - 1}$: jest to liczba ${min_num}$.",
            f"{q_word} wybranych liczb wynosi: ${max_num} {op_sign} {min_num} = {res}$ (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="prawdop_kostka_pf",
    topic_id="prawdopodobienstwo",
    subtype="pf",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2021 zad. 15",
)
def gen_kostka_pf(rng):
    # Rzut standardową sześcienną kostką
    # Zdanie 1: prawdopodobieństwo wyrzucenia liczby pierwszej ({2, 3, 5} -> 3/6 = 1/2; częsty błąd: zaliczenie 1!)
    s1_true = rng.choice([True, False])
    shown_f1 = frac_tex("1", "2") if s1_true else frac_tex("2", "3")

    # Zdanie 2: wyrzucenie dzielnika liczby 6 ({1, 2, 3, 6} -> 4/6 = 2/3)
    s2_true = rng.choice([True, False])
    shown_f2 = frac_tex("2", "3") if s2_true else frac_tex("1", "2")

    stem = "Rzucamy jeden raz symetryczną sześcienną kostką do gry o ściankach oznaczonych liczbami oczek od $1$ do $6$."
    command = "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe."

    st1 = f"Prawdopodobieństwo wyrzucenia liczby oczek będącej liczbą pierwszą jest równe {shown_f1}."
    st2 = f"Prawdopodobieństwo wyrzucenia liczby oczek będącej dzielnikiem liczby $6$ jest równe {shown_f2}."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    return {
        "stem": stem,
        "command": command,
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": [
            "Wśród liczb $\\{1, 2, 3, 4, 5, 6\\}$ liczbami pierwszymi są wyłącznie $2$, $3$ oraz $5$ (liczba $1$ nie jest pierwsza!), "
            f"zatem prawdopodobieństwo wynosi {frac_tex('3', '6')} $=$ {frac_tex('1', '2')} -> zdanie pierwsze: **{p1}**.",
            "Dzielnikami liczby $6$ na kostce są $1, 2, 3, 6$ ($4$ wyniki sprzyjające), więc prawdopodobieństwo wynosi "
            f"{frac_tex('4', '6')} $=$ {frac_tex('2', '3')} -> zdanie drugie: **{p2}**.",
        ],
    }


@register_template(
    template_id="prawdop_regula_mnozenia_ab_cd",
    topic_id="prawdopodobienstwo",
    subtype="ab_cd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2024 zad. 14",
)
def gen_kombinatoryka_ab_cd(rng):
    # Zbiór k cyfr niezerowych, np. {1, 2, 3, 4, 5} (k=5 lub k=4 lub k=6)
    k = rng.choice([4, 5, 6])
    digits = list(range(1, k + 1))
    digits_str = ", ".join(str(d) for d in digits)

    # Kody trzycyfrowe o niepowtarzających się cyfrach: k * (k-1) * (k-2)
    no_rep = k * (k - 1) * (k - 2)
    with_rep = k ** 3

    if rng.choice([True, False]):
        opts1 = {"A": f"${no_rep}$", "B": f"${with_rep}$"}
        c1 = "A"
    else:
        opts1 = {"A": f"${with_rep}$", "B": f"${no_rep}$"}
        c1 = "B"

    # Ile wśród nich jest parzystych (gdy cyfry mogą się powtarzać): k * k * n_even
    n_even = len([d for d in digits if d % 2 == 0])
    even_rep = k * k * n_even
    wrong_even = k * (k - 1) * n_even

    if rng.choice([True, False]):
        opts2 = {"C": f"${even_rep}$", "D": f"${wrong_even}$"}
        c2 = "C"
    else:
        opts2 = {"C": f"${wrong_even}$", "D": f"${even_rep}$"}
        c2 = "D"

    stem = f"Tworzymy kody trzycyfrowe wyłącznie z cyfr ze zbioru $\\{{{digits_str}\\}}$."
    command = "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D."

    parts = [
        {"prefix": "Wszystkich takich kodów trzycyfrowych o **różnych** (niepowtarzających się) cyfrach jest", "suffix": ".", "options": opts1},
        {"prefix": "Wszystkich parzystych liczb trzycyfrowych, w których cyfry ze zbioru mogą się powtarzać, jest", "suffix": ".", "options": opts2},
    ]

    return {
        "stem": stem,
        "command": command,
        "ab_cd_parts": parts,
        "correct_answer": c1 + c2,
        "solution_steps": [
            f"Pierwszą cyfrę wybieramy na ${k}$ sposobów, drugą na ${k - 1}$, a trzecią na ${k - 2}$ sposobów: "
            f"${k} \\cdot {k - 1} \\cdot {k - 2} = {no_rep}$ (wybór **{c1}**).",
            f"W podanym zbiorze cyfr parzystych jest ${n_even}$. Przy powtarzających się cyfrach mamy "
            f"${k} \\cdot {k} \\cdot {n_even} = {even_rep}$ takich liczb parzystych (wybór **{c2}**).",
        ],
    }


@register_template(
    template_id="prawdop_tabela_zawodnicy_2pkt",
    topic_id="prawdopodobienstwo",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2024 zad. 16",
)
def gen_prawdop_tabela_2pkt(rng):
    scores = [10, 15, 20, 25, 30]
    counts = [rng.randint(3, 7) for _ in range(5)]
    # Ustawmy sumę ładną (np. 24, 25, 30 lub 32)
    total = sum(counts)
    fav = counts[3] + counts[4]  # więcej niż 20 pkt -> 25 lub 30 pkt!
    g = gcd(fav, total)
    num_s, den_s = fav // g, total // g

    table = [
        ["Liczba zdobytych punktów", *[str(s) for s in scores]],
        ["Liczba zawodników", *[str(c) for c in counts]],
    ]

    stem = (
        "W szkolnym turnieju szachowym wzięła udział grupa uczniów. Każdy uczestnik zdobył jedną z pięciu "
        "możliwych liczb punktów. Zbiorcze wyniki wszystkich uczestników przedstawiono w tabeli."
    )
    command = (
        "Spośród wszystkich uczestników turnieju losujemy jedną osobę. Oblicz prawdopodobieństwo zdarzenia "
        "polegającego na tym, że wylosowany uczestnik zdobył **więcej niż 20 punktów**. Zapisz obliczenia."
    )

    ans_str = f"{num_s}/{den_s}"
    return {
        "stem": stem,
        "command": command,
        "table_data": table,
        "correct_answer": ans_str,
        "solution_steps": [
            f"Obliczamy łączną liczbę wszystkich uczestników turnieju: ${' + '.join(str(c) for c in counts)} = {total}$.",
            f"Więcej niż $20$ punktów (czyli $25$ lub $30$ punktów) zdobyło: ${counts[3]} + {counts[4]} = {fav}$ uczestników.",
            f"Prawdopodobieństwo wynosi: $P =$ {frac_tex(str(fav), str(total))}"
            + (f" $=$ {frac_tex(str(num_s), str(den_s))}." if g > 1 else "."),
            f"**Odpowiedź:** Szukane prawdopodobieństwo jest równe {frac_tex(str(num_s), str(den_s))}.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie łącznej liczby uczestników ({total}) oraz liczby wyników sprzyjających ({fav}).",
            f"2 pkt – poprawne zapisanie prawdopodobieństwa zdarzenia: {num_s}/{den_s} (lub {fav}/{total}).",
        ],
        "grid_height_mm": 48.0,
    }


@register_template(
    template_id="prawdop_dokladanie_kul_3pkt",
    topic_id="prawdopodobienstwo",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Wzorzec: CKE Maj 2020 zad. 20",
)
def gen_dokladanie_kul_3pkt(rng):
    # W pudełku jest W kul białych i B kul czarnych. Ile kul białych (x) należy dołożyć, aby P(biała) = p/q?
    # (W + x) / (W + B + x) = p / q -> q(W + x) = p(W + B + x) -> (q - p)x = p(W + B) - qW = pB - (q - p)W
    # Aby x wyszło całkowite dodatnie: niech q - p = 1 (np. 2/3, 3/4, 4/5): wtedy x = p*B - W!
    p, q = rng.choice([(2, 3), (3, 4), (4, 5)])
    B = rng.randint(8, 16)
    W = rng.randint(3, p * B - 4)
    x_add = p * B - W
    total_before = W + B
    total_after = total_before + x_add

    stem = (
        f"W pudełku znajdują się wyłącznie kule białe i czarne: jest w nim ${W}$ kul białych oraz ${B}$ kul czarnych. "
        f"Do tego pudełka zamierzamy dołożyć pewną liczbę kul białych (nie zmieniając liczby kul czarnych)."
    )
    command = (
        f"Oblicz, ile kul białych należy dołożyć do pudełka, aby po dołożeniu prawdopodobieństwo wylosowania "
        f"kuli białej było równe {frac_tex(str(p), str(q))}. Zapisz obliczenia."
    )

    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"{x_add} kul białych",
        "solution_steps": [
            f"Oznaczmy przez $x$ liczbę dokładanych kul białych. Początkowo w pudełku jest ${W} + {B} = {total_before}$ kul.",
            f"Po dołożeniu $x$ kul białych w pudełku będzie ${W} + x$ kul białych spośród wszystkich ${total_before} + x$ kul.",
            f"Zapisujemy równanie na prawdopodobieństwo: {frac_tex(f'{W} + x', f'{total_before} + x')} $=$ {frac_tex(str(p), str(q))}.",
            f"Mnożymy na krzyż: ${q}({W} + x) = {p}({total_before} + x)$, czyli ${q * W} + {q}x = {p * total_before} + {p}x$, "
            f"skąd $x = {x_add}$.",
            f"Sprawdzenie: po dołożeniu mamy ${W + x_add}$ kul białych na ${total_after}$ wszystkich kul, "
            f"a {frac_tex(str(W + x_add), str(total_after))} $=$ {frac_tex(str(p), str(q))}.",
            f"**Odpowiedź:** Należy dołożyć ${x_add}$ kul białych.",
        ],
        "scoring_scheme": [
            f"1 pkt – wyrażenie liczby kul białych ({W} + x) oraz wszystkich kul ({total_before} + x) po dołożeniu.",
            f"2 pkt – ułożenie poprawnego równania ({W} + x)/({total_before} + x) = {p}/{q} i sprowadzenie go do równania liniowego.",
            f"3 pkt – poprawne rozwiązanie równania i podanie odpowiedzi ({x_add}).",
        ],
        "grid_height_mm": 62.0,
    }
