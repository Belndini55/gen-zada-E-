"""Pakiet 32 autorskich generatorów proceduralnych (działy 1–7: liczby, procenty, potęgi, pierwiastki, algebra, równania, ruch).

Każdy generator losuje niezależnie kontekst sytuacyjny, strukturę pytania oraz parametry liczbowe,
dzięki czemu każdy wygenerowany arkusz zawiera świeże, niepowtarzalne zadania w standardzie CKE E8.
"""

from __future__ import annotations

import math
from fractions import Fraction

from ..math_text import frac_tex, mixed_frac_tex, pl_num, shuffle_abcd
from .base import register_template


# ===========================================================================
# 1. LICZBY I DZIAŁANIA (6 nowych generatorów: zamknięte + 2 pkt + 3 pkt)
# ===========================================================================

@register_template(
    template_id="proc_liczby_cyfra_podzielnosci_abcd",
    topic_id="liczby_dzialania",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – cechy podzielności liczby czterocyfrowej",
)
def gen_proc_cyfra_podzielnosci(rng):
    div = rng.choice([4, 6, 9, 15, 18])
    d1 = rng.randint(2, 8)
    d2 = rng.randint(0, 9)
    if div == 9:
        # 4-cyfrowa d1 d2 * d4 podzielna przez 9
        d4 = rng.randint(1, 8)
        rem = (d1 + d2 + d4) % 9
        star = (9 - rem) % 9
        num_pat = f"${d1}{d2}\\text{{*}}{d4}$"
        rule_expl = f"Suma cyfr ${d1} + {d2} + \\text{{*}} + {d4} = {d1 + d2 + d4} + \\text{{*}}$ musi dzielić się przez $9$, skąd $\\text{{*}} = {star}$."
    elif div == 6:
        d4 = rng.choice([2, 4, 6, 8])
        # d1 + d2 + * + d4 podzielne przez 3, pytamy o NAJWIĘKSZĄ cyfrę *
        valid = [c for c in range(10) if (d1 + d2 + c + d4) % 3 == 0]
        star = max(valid)
        num_pat = f"${d1}{d2}\\text{{*}}{d4}$"
        rule_expl = f"Liczba jest parzysta (kończy się cyfrą ${d4}$), więc musi być jeszcze podzielna przez $3$. Największą cyfrą $\\text{{*}}$ spełniającą $({d1 + d2 + d4} + \\text{{*}}) \\vdots 3$ jest ${star}$."
    elif div == 4:
        # d1 d2 d3 *, pytamy o najmniejszą niezerową lub największą cyfrę jedności
        d3 = rng.choice([1, 3, 5, 7])
        valid = [c for c in range(10) if (10 * d3 + c) % 4 == 0]
        star = max(valid)  # dla nieparzystej dziesiątki są to 2 oraz 6 -> max = 6
        num_pat = f"${d1}{d2}{d3}\\text{{*}}$"
        rule_expl = f"Liczba dzieli się przez $4$, gdy jej dwie ostatnie cyfry tworzą liczbę podzielną przez $4$: spośród ${d3}2$ i ${d3}6$ większą cyfrą jedności jest ${star}$."
    elif div == 15:
        # d1 d2 * 5 podzielna przez 15 -> podzielna przez 5 (jest) i przez 3, największa cyfra *
        valid = [c for c in range(10) if (d1 + d2 + c + 5) % 3 == 0]
        star = max(valid)
        num_pat = f"${d1}{d2}\\text{{*}}5$"
        rule_expl = f"Liczba kończy się cyfrą $5$, więc dzieli się przez $5$; aby dzieliła się przez $15$, suma cyfr ${d1 + d2 + 5} + \\text{{*}}$ musi dzielić się przez $3$. Największą taką cyfrą jest ${star}$."
    else:
        # div == 18: parzysta i podzielna przez 9 -> d1 d2 * d4
        d4 = rng.choice([0, 2, 4, 6])
        rem = (d1 + d2 + d4) % 9
        star = 9 if rem == 0 else (9 - rem)
        num_pat = f"${d1}{d2}\\text{{*}}{d4}$"
        rule_expl = f"Liczba jest parzysta, więc dzieli się przez $18$ wtedy, gdy dzieli się przez $9$. Suma cyfr ${d1 + d2 + d4} + \\text{{*}}$ daje największą cyfrę $\\text{{*}} = {star}$."

    wrongs = [f"${c}$" for c in range(9, -1, -1) if c != star]
    rng.shuffle(wrongs)
    choices, ans = shuffle_abcd(rng, f"${star}$", wrongs[:3])
    ask_max = "największą cyfrę" if div in (4, 6, 15, 18) and star >= 6 else "cyfrę"
    if div == 9 and star == 0:
        # uniknij niejednoznaczności 0 vs 9: wymuś rem != 0
        star = 9
        choices, ans = shuffle_abcd(rng, "$9$", ["$3$", "$6$", "$1$"])
        rule_expl = f"Największą cyfrą uzupełniającą sumę cyfr do wielokrotności $9$ jest $9$."
        ask_max = "największą cyfrę"

    return {
        "stem": f"W zapisie liczby czterocyfrowej {num_pat} znak $\\text{{*}}$ zastępuje jedną nieznaną cyfrę. Wiadomo, że ta liczba jest podzielna przez ${div}$.",
        "command": f"Wskaż {ask_max}, którą można wpisać w miejsce znaku $\\text{{*}}$. Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [rule_expl, f"Poprawna odpowiedź: **{ans}**."],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_liczby_dzialania_mieszane_ab_cd",
    topic_id="liczby_dzialania",
    subtype="ab_cd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – działania na ułamkach zwykłych i dziesiętnych",
)
def gen_proc_dzialania_mieszane(rng):
    # W1: (a/b - c/d) * m, W2: p : 0,25 - q * 0,5
    f1, f2, mult = rng.choice([
        (Fraction(3, 4), Fraction(1, 6), 12),
        (Fraction(5, 6), Fraction(3, 8), 24),
        (Fraction(7, 8), Fraction(1, 4), 16),
        (Fraction(4, 5), Fraction(3, 10), 14),
        (Fraction(2, 3), Fraction(1, 4), 12),
    ])
    val1 = int((f1 - f2) * mult)
    bad1 = int((f1 + f2) * mult)

    p = rng.choice([3, 5, 7, 9])
    q = rng.choice([6, 8, 10, 14])
    val2 = p * 4 - q // 2
    bad2 = p // 4 + q * 2 if p % 4 == 0 else p * 4 + q // 2

    if rng.random() < 0.5:
        opts1, a1 = {"A": f"${val1}$", "B": f"${bad1}$"}, "A"
    else:
        opts1, a1 = {"A": f"${bad1}$", "B": f"${val1}$"}, "B"

    if rng.random() < 0.5:
        opts2, a2 = {"C": f"${val2}$", "D": f"${bad2}$"}, "C"
    else:
        opts2, a2 = {"C": f"${bad2}$", "D": f"${val2}$"}, "D"

    t_f1 = frac_tex(f1.numerator, f1.denominator)
    t_f2 = frac_tex(f2.numerator, f2.denominator)
    return {
        "stem": (
            f"Dane są dwa wyrażenia arytmetyczne:\n"
            f"$M = \\left(\\frac{{{f1.numerator}}}{{{f1.denominator}}} - \\frac{{{f2.numerator}}}{{{f2.denominator}}}\\right) \\cdot {mult}$   oraz   "
            f"$N = {p} : 0,25 - {q} \\cdot 0,5$."
        ),
        "command": "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D.",
        "ab_cd_parts": [
            {"prefix": "Wartość wyrażenia $M$ jest równa", "suffix": ".", "options": opts1},
            {"prefix": "Wartość wyrażenia $N$ jest równa", "suffix": ".", "options": opts2},
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Obliczamy $M$: $({t_f1} - {t_f2}) \\cdot {mult} = {f1.numerator * (mult // f1.denominator)} - {f2.numerator * (mult // f2.denominator)} = {val1}$ (**{a1}**).",
            f"Obliczamy $N$: ${p} : \\frac{{1}}{{4}} - {q} \\cdot \\frac{{1}}{{2}} = {p * 4} - {q // 2} = {val2}$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna para odpowiedzi.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_liczby_rozwiniecie_okresowe_pf",
    topic_id="liczby_dzialania",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – rozwinięcia dziesiętne i zaokrąglenia",
)
def gen_proc_okresowe_pf(rng):
    # Ułamek k/9 lub k/11 lub okres (ab)
    a, b = rng.choice([(2, 7), (3, 8), (4, 1), (5, 9), (6, 2), (1, 8)])
    # liczba 0,(ab): cyfra na n-tym miejscu po przecinku: nieparzyste -> a, parzyste -> b
    pos = rng.choice([15, 18, 21, 24, 30, 33])
    true_digit = a if pos % 2 == 1 else b
    s1_true = rng.choice([True, False])
    shown_digit = true_digit if s1_true else (b if pos % 2 == 1 else a)

    # Porównanie 0,(ab) z ułamkiem 0,ab
    # 0,abab... > 0,ab00... zawsze gdy ab > 0!
    s2_true = rng.choice([True, False])
    cmp_word = "większa" if s2_true else "mniejsza"

    a1, a2 = ("P" if s1_true else "F"), ("P" if s2_true else "F")
    return {
        "stem": f"Dana jest liczba o rozwinięciu dziesiętnym nieskończonym okresowym $u = 0,({a}{b}) = 0,{a}{b}{a}{b}{a}{b}\\dots$",
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Na ${pos}$. miejscu po przecinku w rozwinięciu dziesiętnym liczby $u$ stoi cyfra ${shown_digit}$.", a1),
            (f"Liczba $u$ jest {cmp_word} od ułamka dziesiętnego skończonego $0,{a}{b}$.", a2),
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Okres jest dwucyfrowy: na miejscach nieparzystych stoi cyfra ${a}$, a na parzystych cyfra ${b}$. Ponieważ liczba ${pos}$ jest {'nieparzysta' if pos % 2 == 1 else 'parzysta'}, stoi tam cyfra ${true_digit}$ (**{a1}**).",
            f"Porównujemy cyfry na trzecim miejscu po przecinku: $0,{a}{b}{a}\\dots > 0,{a}{b}0$, więc liczba $u$ jest większa od $0,{a}{b}$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_liczby_czas_zegar_jednostki_2pkt",
    topic_id="liczby_dzialania",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – obliczenia zegarowe i ułamki czasu",
)
def gen_proc_obliczenia_czasowe_2pkt(rng):
    ctx = rng.choice([
        ("Projekcja filmu dokumentalnego i dyskusja w klubie filmowym", "Sam film trwał", "a przerwa techniczna zajęła", "Ile minut trwała dyskusja po filmie"),
        ("Warsztaty laboratoryjne z chemii", "Część teoretyczna zajęła", "a przygotowanie stanowisk trwało", "Ile minut trwała część doświadczalna"),
        ("Trening lekkoatletyczny na stadionie", "Bieg ciągły zajął", "a rozgrzewka trwała", "Ile minut pozostało na ćwiczenia rozciągające"),
    ])
    title, p1_lbl, p2_lbl, q_lbl = ctx
    tot_h_frac_num, tot_h_frac_den, tot_min = rng.choice([
        (2, 1, 120),
        (5, 2, 150),
        (9, 4, 135),
        (7, 3, 140),
    ])
    f1 = rng.choice([Fraction(2, 5), Fraction(3, 5), Fraction(1, 3), Fraction(4, 9)])
    while (tot_min * f1.numerator) % f1.denominator != 0:
        f1 = Fraction(2, 5) if tot_min % 5 == 0 else Fraction(1, 3)
    m1 = int(tot_min * f1)
    m2 = rng.choice([15, 18, 20, 25])
    m3 = tot_min - m1 - m2

    tot_desc = f"${tot_h_frac_num}$ godziny" if tot_h_frac_den == 1 else mixed_frac_tex(tot_h_frac_num // tot_h_frac_den, tot_h_frac_num % tot_h_frac_den, tot_h_frac_den) + " godziny"
    t_f1 = frac_tex(f1.numerator, f1.denominator)
    return {
        "stem": (
            f"{title} trwały łącznie {tot_desc}. {p1_lbl} {t_f1} całego tego czasu, "
            f"{p2_lbl} ${m2}$ minut, natomiast resztę czasu przeznaczono na ostatnią część."
        ),
        "command": f"{q_lbl}? Zapisz obliczenia.",
        "correct_answer": f"{m3} min",
        "solution_steps": [
            f"Zamieniamy łączny czas na minuty: {tot_desc} $= {tot_min}\\text{{ min}}$.",
            f"Pierwsza część trwała {t_f1} $\\cdot {tot_min}\\text{{ min}} = {m1}\\text{{ min}}$.",
            f"Ostatnia część trwała: ${tot_min} - ({m1} + {m2}) = {m3}\\text{{ min}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – zamiana czasu całkowitego na minuty ({tot_min} min) i obliczenie trwania pierwszej części ({m1} min).",
            f"2 pkt – poprawne obliczenie szukanego czasu: {m3} min.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_liczby_trzy_etapy_ulamki_3pkt",
    topic_id="liczby_dzialania",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – ułamek całości i ułamek pozostałej części",
)
def gen_proc_trzy_etapy_ulamki_3pkt(rng):
    ctx = rng.choice([
        ("Szkoła zamówiła partię nowych podręczników do biblioteki", "W poniedziałek ostemplowano", "we wtorek", "a w środę pozostałe", "podręczników"),
        ("Gospodarstwo sadownicze zebrało skrzynki jabłek", "Pierwszego dnia wysłano do tłoczni", "drugiego dnia do sklepów", "a trzeciego dnia ostatnie", "skrzynek"),
        ("Drukarnia realizowała zamówienie na plakaty koncertowe", "Rano wydrukowano", "po południu", "a wieczorem ostatnie", "plakatów"),
    ])
    intro, d1_txt, d2_txt, d3_txt, noun_gen = ctx
    f1_num, f1_den = rng.choice([(1, 3), (2, 5), (1, 4), (3, 8)])
    f2_num, f2_den = rng.choice([(1, 2), (2, 3), (3, 5)])
    # Ułamek po 1. etapie: rem1 = 1 - f1; po 2. etapie (ułamek RESZTY!): rem2 = rem1 * (1 - f2)
    f1 = Fraction(f1_num, f1_den)
    f2 = Fraction(f2_num, f2_den)
    rem_frac = (1 - f1) * (1 - f2)
    mult = rng.randint(4, 12)
    last_cnt = rem_frac.numerator * mult
    total = rem_frac.denominator * mult
    c1 = int(total * f1)
    c2 = int((total - c1) * f2)

    t_f1 = frac_tex(f1.numerator, f1.denominator)
    t_f2 = frac_tex(f2.numerator, f2.denominator)
    t_rem = frac_tex(rem_frac.numerator, rem_frac.denominator)

    return {
        "stem": (
            f"{intro}. {d1_txt} {t_f1} wszystkich {noun_gen}, {d2_txt} – {t_f2} **pozostałej** części, "
            f"{d3_txt} ${last_cnt}$ {noun_gen}."
        ),
        "command": f"Oblicz łączną liczbę wszystkich {noun_gen} w całym zamówieniu. Zapisz obliczenia.",
        "correct_answer": f"{total}",
        "solution_steps": [
            f"Po pierwszym etapie pozostało $1 - \\frac{{{f1.numerator}}}{{{f1.denominator}}} = \\frac{{{f1.denominator - f1.numerator}}}{{{f1.denominator}}}$ wszystkich {noun_gen}.",
            f"W drugim etapie wykonano {t_f2} tej reszty, więc na trzeci etap została część równa $\\frac{{{f1.denominator - f1.numerator}}}{{{f1.denominator}}} \\cdot \\left(1 - \\frac{{{f2.numerator}}}{{{f2.denominator}}}\\right) = \\frac{{{rem_frac.numerator}}}{{{rem_frac.denominator}}}$ całości.",
            f"Skoro {t_rem} całości to ${last_cnt}$, to całość liczy ${last_cnt} : \\frac{{{rem_frac.numerator}}}{{{rem_frac.denominator}}} = {total}$ ({c1} + {c2} + {last_cnt} = {total}).",
        ],
        "scoring_scheme": [
            "1 pkt – poprawne wyznaczenie ułamka pozostałego po pierwszym etapie.",
            f"2 pkt – poprawne wyznaczenie ułamka całości przypadającego na trzeci etap ({rem_frac.numerator}/{rem_frac.denominator}).",
            f"3 pkt – pełne obliczenia i podanie łącznej liczby: {total}.",
        ],
        "grid_height_mm": 60.0,
    }


@register_template(
    template_id="proc_liczby_cyfry_dwucyfrowa_2pkt",
    topic_id="liczby_dzialania",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – dziesiątkowy system pozycyjny i przestawianie cyfr",
)
def gen_proc_przestawianie_cyfr(rng):
    # Liczba dwucyfrowa o sumie cyfr S; po przestawieniu cyfr liczba rośnie/maleje o 9*(b-a)
    a = rng.randint(2, 6)
    diff_d = rng.choice([2, 3, 4, 5])
    if a + diff_d > 9:
        a = 9 - diff_d
    b = a + diff_d
    s_digits = a + b
    orig = 10 * a + b
    swapped = 10 * b + a
    delta = swapped - orig  # 9 * diff_d

    return {
        "stem": (
            f"Suma cyfr pewnej liczby naturalnej dwucyfrowej jest równa ${s_digits}$. "
            f"Jeżeli przestawimy cyfry tej liczby, to otrzymamy liczbę dwucyfrową o ${delta}$ większą od liczby początkowej."
        ),
        "command": "Wyznacz tę liczbę początkową. Zapisz obliczenia.",
        "correct_answer": f"{orig}",
        "solution_steps": [
            f"Oznaczmy cyfrę dziesiątek liczby początkowej przez $x$, a cyfrę jedności przez ${s_digits} - x$. Liczba początkowa ma wartość $10x + ({s_digits} - x) = 9x + {s_digits}$.",
            f"Liczba po przestawieniu cyfr ma wartość $10({s_digits} - x) + x = {10 * s_digits} - 9x$. Z warunku $({10 * s_digits} - 9x) - (9x + {s_digits}) = {delta}$ mamy ${9 * s_digits} - 18x = {delta}$, skąd $x = {a}$ oraz druga cyfra to ${b}$. Szukana liczba: **${orig}$**.",
        ],
        "scoring_scheme": [
            "1 pkt – poprawne zapisanie zależności między cyframi lub sprawdzenie systematyczne kandydatów o danej sumie cyfr.",
            f"2 pkt – wyznaczenie poprawnej liczby początkowej: {orig}.",
        ],
        "grid_height_mm": 52.0,
    }


# ===========================================================================
# 2. PROCENTY I PROPORCJE (5 nowych generatorów)
# ===========================================================================

@register_template(
    template_id="proc_procenty_podatek_brutto_abcd",
    topic_id="procenty_proporcje",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – kwota netto, podatek i kwota brutto",
)
def gen_proc_netto_brutto(rng):
    net = rng.choice([150, 200, 250, 300, 400, 500, 800])
    vat_pct = rng.choice([8, 23])
    while (net * vat_pct) % 100 != 0:
        net = 200
    tax = (net * vat_pct) // 100
    gross = net + tax

    ask_net = rng.choice([True, False])
    item = rng.choice(["usługi serwisowej", "biletu okresowego", "zestawu narzędzi", "oprawy oświetleniowej"])
    if ask_net:
        corr = f"${pl_num(net)}$ zł"
        w1 = f"${pl_num(gross - vat_pct)}$ zł"
        w2 = f"${pl_num(round(gross * (100 - vat_pct) / 100, 2))}$ zł"
        w3 = f"${pl_num(tax)}$ zł"
        choices, ans = shuffle_abcd(rng, corr, [w1, w2, w3])
        return {
            "stem": f"Cena brutto {item} (czyli cena netto powiększona o podatek VAT w wysokości ${vat_pct}\\%$ ceny netto) wynosi ${pl_num(gross)}$ zł.",
            "command": f"Ile wynosi cena netto {item}? Wybierz właściwą odpowiedź spośród podanych.",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Cena brutto stanowi $100\\% + {vat_pct}\\% = {100 + vat_pct}\\%$ ceny netto.",
                f"Cena netto wynosi $\\frac{{{gross}}}{{{(100 + vat_pct) / 100}}} = {pl_num(net)}$ zł (odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    corr = f"${pl_num(gross)}$ zł"
    choices, ans = shuffle_abcd(rng, corr, [f"${pl_num(net + vat_pct)}$ zł", f"${pl_num(tax)}$ zł", f"${pl_num(net * 2)}$ zł"])
    return {
        "stem": f"Cena netto {item} jest równa ${pl_num(net)}$ zł. Do tej kwoty dolicza się podatek VAT równy ${vat_pct}\\%$ ceny netto.",
        "command": f"Jaka jest cena brutto {item}? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Kwota podatku VAT: ${vat_pct}\\% \\cdot {net} = {tax}$ zł.",
            f"Cena brutto: ${net} + {tax} = {gross}$ zł (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_procenty_roztwor_stezenie_2pkt",
    topic_id="procenty_proporcje",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – stężenie procentowe roztworu / zawartość składnika",
)
def gen_proc_roztwor_2pkt(rng):
    ctx = rng.choice([
        ("W dzbanku przygotowano", "napoju cytrynowego", "soku z cytryny", "czystej wody"),
        ("W naczyniu wymieszano", "zalewy do kiszenia", "soli kamiennej", "wody źródlanej"),
        ("W kuchni przygotowano", "syropu owocowego", "cukru trzcinowego", "wody"),
    ])
    intro, mix_gen, sub_gen, water_gen = ctx
    m_init = rng.choice([200, 250, 300, 400])
    pct_init = rng.choice([10, 15, 20, 25])
    m_sub = (m_init * pct_init) // 100
    m_added_water = rng.choice([100, 150, 200, 250, 300])
    # Dobierz m_added_water tak, aby m_sub * 100 dzieliło się przez (m_init + m_added_water)
    valid_add = [w for w in (50, 100, 150, 200, 250, 300, 400, 600) if (m_sub * 100) % (m_init + w) == 0]
    m_added_water = rng.choice(valid_add) if valid_add else m_init
    m_final = m_init + m_added_water
    pct_final = (m_sub * 100) // m_final

    return {
        "stem": (
            f"{intro} ${m_init}$ g {mix_gen}, w którym masa {sub_gen} stanowiła ${pct_init}\\%$ masy całości. "
            f"Następnie dolano jeszcze ${m_added_water}$ g {water_gen} i dokładnie wymieszano."
        ),
        "command": f"Oblicz, ile procent masy nowego {mix_gen} stanowi masa {sub_gen}. Zapisz obliczenia.",
        "correct_answer": f"{pct_final}%",
        "solution_steps": [
            f"Masa {sub_gen} przed dolaniem wody wynosiła ${pct_init}\\% \\cdot {m_init}\\text{{ g}} = {m_sub}\\text{{ g}}$ i nie uległa zmianie.",
            f"Po dolaniu wody łączna masa wzrosła do ${m_init} + {m_added_water} = {m_final}\\text{{ g}}$, więc nowy udział procentowy wynosi $\\frac{{{m_sub}}}{{{m_final}}} \\cdot 100\\% = {pct_final}\\%$.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie masy czystego składnika ({m_sub} g) lub nowej masy całkowitej ({m_final} g).",
            f"2 pkt – poprawne obliczenie nowego stężenia procentowego: {pct_final}%.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_procenty_proporcja_praca_abcd",
    topic_id="procenty_proporcje",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – wielkości wprost i odwrotnie proporcjonalne",
)
def gen_proc_proporcja_praca(rng):
    is_inverse = rng.choice([True, False])
    if is_inverse:
        n1, t1, n2 = rng.choice([(3, 8, 4), (4, 9, 6), (6, 10, 15), (5, 12, 10), (4, 15, 12)])
        t2 = (n1 * t1) // n2
        w1 = Fraction(n2 * t1, n1)
        w1_s = f"${pl_num(float(w1))}$ h" if w1.denominator in (1, 2, 4, 5) else f"${t2 + 3}$ h"
        choices, ans = shuffle_abcd(rng, f"${t2}$ h", [w1_s, f"${t1 - (n2 - n1) if t1 > (n2 - n1) else t2 + 2}$ h", f"${n1 * t1}$ h"])
        job = rng.choice([
            ("jednakowych drukarek 3D realizuje serię modeli", "takich samych drukarek"),
            ("identycznych pomp opróżnia zbiornik retencyjny", "takich samych pomp"),
            ("kosiarek kosi trawę na boiskach treningowych", "takich samych kosiarek"),
        ])
        return {
            "stem": f"Zespół ${n1}$ {job[0]} ze stałą wydajnością w czasie ${t1}$ godzin.",
            "command": f"W jakim czasie tę samą pracę wykona równocześnie ${n2}$ {job[1]} pracujących z taką samą wydajnością? Wybierz właściwą odpowiedź spośród podanych.",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Liczba urządzeń i czas wykonania tej samej pracy są odwrotnie proporcjonalne: ${n1} \\cdot {t1}\\text{{ h}} = {n1 * t1}$ roboczogodzin.",
                f"Czas dla ${n2}$ urządzeń: ${n1 * t1} : {n2} = {t2}\\text{{ h}}$ (odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    # Wprost proporcjonalne (zużycie paliwa / farby na powierzchnię)
    s1, l1, s2 = rng.choice([(15, 3, 40), (24, 4, 54), (35, 5, 63), (40, 6, 100)])
    l2 = Fraction(s2 * l1, s1)
    corr = f"${pl_num(float(l2))}$ l"
    choices, ans = shuffle_abcd(rng, corr, [f"${pl_num(float(l2) + 2)}$ l", f"${pl_num(s2 / l1 if s2 % l1 == 0 else float(l2) * 2)}$ l", f"${l1 + 3}$ l"])
    return {
        "stem": f"Na pomalowanie ogrodzenia o powierzchni ${s1}\\text{{ m}}^2$ zużyto dokładnie ${l1}$ l impregnatu.",
        "command": f"Ile litrów tego samego impregnatu potrzeba na pomalowanie (taką samą warstwą) ogrodzenia o powierzchni ${s2}\\text{{ m}}^2$? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Z proporcji wprost proporcjonalnej: $\\frac{{{l1}\\text{{ l}}}}{{{s1}\\text{{ m}}^2}} = \\frac{{x}}{{{s2}\\text{{ m}}^2}}$.",
            f"Obliczamy $x = \\frac{{{s2} \\cdot {l1}}}{{{s1}}} = {pl_num(float(l2))}\\text{{ l}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_procenty_lokata_lub_marza_3pkt",
    topic_id="procenty_proporcje",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – wieloetapowe obliczenia procentowe i porównanie ofert",
)
def gen_proc_porownanie_ofert_3pkt(rng):
    item, base_price = rng.choice([
        ("roweru górskiego", 2400),
        ("laptopa edukacyjnego", 3000),
        ("mikroskopu optycznego", 1600),
        ("pianina cyfrowego", 3200),
    ])
    d_a1, d_a2 = rng.choice([(10, 10), (20, 5), (15, 10)])
    # Sklep Hurt-Max: dwie kolejne obniżki o d_a1% i d_a2%
    # Sklep Dom-Tech: jednorazowy rabat kwotowy lub procentowy
    p_after_1 = Fraction(base_price * (100 - d_a1), 100)
    p_a = Fraction(p_after_1 * (100 - d_a2), 100)
    flat_pct = d_a1 + d_a2 - 1
    p_b = Fraction(base_price * (100 - flat_pct), 100)
    diff_val = abs(p_a - p_b)
    cheaper = "pierwszej" if p_a < p_b else "drugiej"

    return {
        "stem": (
            f"Cena katalogowa tego samego modelu {item} w dwóch hurtowniach wynosiła ${pl_num(base_price)}$ zł.\n"
            f"• W *pierwszej* hurtowni cenę obniżono najpierw o ${d_a1}\\%$, a tydzień później nową cenę obniżono jeszcze o ${d_a2}\\%$.\n"
            f"• W *drugiej* hurtowni cenę katalogową obniżono jednorazowo o ${flat_pct}\\%$."
        ),
        "command": "W której hurtowni końcowa cena jest niższa i o ile złotych? Zapisz obliczenia.",
        "correct_answer": f"W {cheaper} hurtowni, o {pl_num(float(diff_val))} zł",
        "solution_steps": [
            f"Pierwsza hurtownia: po pierwszej obniżce cena wynosi ${base_price} \\cdot {pl_num((100 - d_a1)/100)} = {pl_num(float(p_after_1))}$ zł, a po drugiej: ${pl_num(float(p_after_1))} \\cdot {pl_num((100 - d_a2)/100)} = {pl_num(float(p_a))}$ zł.",
            f"Druga hurtownia: po obniżce o ${flat_pct}\\%$ cena wynosi ${base_price} \\cdot {pl_num((100 - flat_pct)/100)} = {pl_num(float(p_b))}$ zł.",
            f"Niższa jest cena w **{cheaper}** hurtowni o $|{pl_num(float(p_a))} - {pl_num(float(p_b))}| = {pl_num(float(diff_val))}$ zł.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne obliczenie końcowej ceny w pierwszej hurtowni ({pl_num(float(p_a))} zł).",
            f"2 pkt – poprawne obliczenie ceny w drugiej hurtowni ({pl_num(float(p_b))} zł).",
            f"3 pkt – wskazanie tańszej hurtowni ({cheaper}) oraz obliczenie różnicy: {pl_num(float(diff_val))} zł.",
        ],
        "grid_height_mm": 58.0,
    }


@register_template(
    template_id="proc_procenty_ankieta_uzasadnienie",
    topic_id="procenty_proporcje",
    subtype="uzasadnienie",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – uzasadnienie przekroczenia progu procentowego",
)
def gen_proc_procenty_uzasadnienie(rng):
    total = rng.choice([160, 240, 320])
    thresh_pct = rng.choice([60, 75])
    needed = (total * thresh_pct) // 100
    is_yes = rng.choice([True, False])
    actual = needed + rng.randint(4, 15) if is_yes else needed - rng.randint(4, 15)
    ans_ab = "A" if is_yes else "B"

    r_good = f"${thresh_pct}\\%$ z liczby ${total}$ jest równe ${needed}$."
    r_bad1 = f"różnica ${total} - {actual}$ jest mniejsza od ${thresh_pct}$."
    r_bad2 = f"ułamek $\\frac{{{thresh_pct}}}{{{total}}}$ jest mniejszy od $\\frac{{1}}{{2}}$."
    reasons_list = [(r_good, True), (r_bad1, False), (r_bad2, False)]
    rng.shuffle(reasons_list)
    reasons_dict = {str(i + 1): txt for i, (txt, _) in enumerate(reasons_list)}
    good_num = next(str(i + 1) for i, (_, ok) in enumerate(reasons_list) if ok)

    return {
        "stem": (
            f"Aby projekt budżetu uczniowskiego przeszedł do kolejnego etapu, musi go poprzeć więcej niż ${thresh_pct}\\%$ "
            f"spośród ${total}$ głosujących uczniów. Za projektem oddano dokładnie ${actual}$ ważnych głosów."
        ),
        "command": (
            "Czy ten projekt przeszedł do kolejnego etapu? Wybierz odpowiedź A (Tak) albo B (Nie) "
            "i jej uzasadnienie spośród 1., 2. albo 3."
        ),
        "justification_data": {
            "prefix_a": "Tak,",
            "prefix_b": "Nie,",
            "conjunction": "ponieważ",
            "reasons": reasons_dict,
        },
        "correct_answer": f"{ans_ab}{good_num}",
        "solution_steps": [
            f"Obliczamy próg ${thresh_pct}\\%$ z ${total}$: $\\frac{{{thresh_pct}}}{{100}} \\cdot {total} = {needed}$ głosów.",
            f"Liczba oddanych głosów (${actual}$) jest {'większa' if is_yes else 'mniejsza'} niż ${needed}$, więc poprawny wybór to **{ans_ab}{good_num}**.",
        ],
        "scoring_scheme": ["1 pkt – poprawny wybór odpowiedzi i uzasadnienia.", "0 pkt – pozostałe przypadki."],
    }


# ===========================================================================
# 3. POTĘGI I NOTACJA WYKŁADNICZA (4 nowe generatory)
# ===========================================================================

@register_template(
    template_id="proc_potegi_ostatnia_cyfra_pf",
    topic_id="potegi_notacja",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – własności potęg o wykładniku całkowitym i znak potęgi",
)
def gen_proc_potegi_znak_pf(rng):
    # Zdanie 1: (-a)^parzysta vs -a^parzysta; Zdanie 2: (1/b)^(-2) = b^2
    a = rng.choice([2, 3, 4, 5])
    exp_even = rng.choice([4, 6, 8])
    s1_true = rng.choice([True, False])
    rel = "większa od" if s1_true else "równa"
    # (-a)^exp_even > 0, natomiast -a^exp_even < 0, więc (-a)^exp > -a^exp!

    b = rng.choice([2, 3, 5, 6])
    k = rng.choice([2, 3])
    s2_true = rng.choice([True, False])
    val_true = b ** k
    val_shown = f"${val_true}$" if s2_true else f"$−{val_true}$"

    a1, a2 = ("P" if s1_true else "F"), ("P" if s2_true else "F")
    return {
        "stem": (
            f"Rozważmy liczby zapisane za pomocą potęg:\n"
            f"$x = (−{a})^{{{exp_even}}}$,   $y = −{a}^{{{exp_even}}}$   oraz   $z = \\left(\\frac{{1}}{{{b}}}\\right)^{{−{k}}}$."
        ),
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Liczba $x$ jest {rel} liczby $y$.", a1),
            (f"Liczba $z$ jest równa {val_shown}.", a2),
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Liczba $x = (-{a})^{{{exp_even}}} > 0$ (parzysty wykładnik obejmuje minus), natomiast $y = -({a}^{{{exp_even}}}) < 0$, więc $x > y$ (**{a1}**).",
            f"Z definicji potęgi o wykładniku ujemnym: $z = {b}^{{{k}}} = {val_true}$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_potegi_polowa_lub_trzecia_czesc_abcd",
    topic_id="potegi_notacja",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – połowa, ćwiartka lub wielokrotność potęgi",
)
def gen_proc_polowa_potegi(rng):
    base, word, div_exp = rng.choice([
        (2, "Połowa", 1),
        (4, "Połowa", 1),
        (8, "Ćwiartka", 2),
        (3, "Trzecia część", 1),
        (9, "Trzecia część", 1),
        (5, "Piąta część", 1),
    ])
    n = rng.choice([12, 16, 20, 24, 30])
    if base in (2, 3, 5):
        p = base
        tot_exp = n - div_exp
    elif base == 4:
        p = 2
        tot_exp = 2 * n - 1
    elif base == 8:
        p = 2
        tot_exp = 3 * n - 2
    else:  # base == 9
        p = 3
        tot_exp = 2 * n - 1

    corr = f"${p}^{{{tot_exp}}}$"
    wrongs = [
        f"${p}^{{{n // 2}}}$",
        f"${base // 2 if base % 2 == 0 else base}^{{{n}}}$" if base != 2 else f"$1^{{{n}}}$",
        f"${p}^{{{tot_exp + 2}}}$",
    ]
    choices, ans = shuffle_abcd(rng, corr, wrongs)
    return {
        "stem": f"Dana jest potęga ${base}^{{{n}}}$.",
        "command": f"Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\n{word} liczby ${base}^{{{n}}}$ jest równa",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Zapisujemy wyrażenie w postaci potęgi liczby ${p}$: ${base}^{{{n}}} = {p}^{{{tot_exp + div_exp}}}$.",
            f"Dzieląc przez ${p}^{{{div_exp}}}$, odejmujemy wykładniki i otrzymujemy ${p}^{{{tot_exp}}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_potegi_wyrazenie_iloraz_2pkt",
    topic_id="potegi_notacja",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – upraszczanie wyrażenia z potęgami o różnych podstawach",
)
def gen_proc_potegi_iloraz_2pkt(rng):
    p = rng.choice([2, 3, 5])
    # Licznik: (p^2)^a * p^b, mianownik: (p^3)^c -> wynik p^k dla k in {2, 3, 4}
    k = rng.choice([2, 3, 4])
    c = rng.randint(3, 5)
    denom_exp = 3 * c
    num_exp = denom_exp + k
    a = rng.randint(3, 6)
    b = num_exp - 2 * a
    while b <= 1:
        a -= 1
        b = num_exp - 2 * a

    p2 = p ** 2
    p3 = p ** 3
    res = p ** k
    expr = rf"\frac{{{p2}^{{{a}}} \cdot {p}^{{{b}}}}}{{{p3}^{{{c}}}}}"

    return {
        "stem": f"Dane jest wyrażenie arytmetyczne:\n${expr}$.",
        "command": "Oblicz wartość tego wyrażenia i zapisz wynik w postaci liczby całkowitej. Zapisz obliczenia.",
        "correct_answer": f"{res}",
        "solution_steps": [
            f"Zamieniamy podstawy potęg na liczbę ${p}$: ${p2}^{{{a}}} = ({p}^2)^{{{a}}} = {p}^{{{2 * a}}}$ oraz ${p3}^{{{c}}} = ({p}^3)^{{{c}}} = {p}^{{{3 * c}}}$.",
            f"Obliczamy wartość ułamka: $\\frac{{{p}^{{{2 * a}}} \\cdot {p}^{{{b}}}}}{{{p}^{{{3 * c}}}}} = \\frac{{{p}^{{{num_exp}}}}}{{{p}^{{{denom_exp}}}}} = {p}^{{{k}}} = {res}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – sprowadzenie potęg do wspólnej podstawy {p}.",
            f"2 pkt – poprawne zastosowanie praw działań na potęgach i obliczenie wartości: {res}.",
        ],
        "grid_height_mm": 48.0,
    }


@register_template(
    template_id="proc_potegi_notacja_astronomia_3pkt",
    topic_id="potegi_notacja",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – obliczenia praktyczne w notacji wykładniczej",
)
def gen_proc_notacja_praktyczna_3pkt(rng):
    ctx = rng.choice([
        ("Sonda badawcza porusza się w przestrzeni kosmicznej ze stałą prędkością", "km/s", "Jaką drogę (w kilometrach) pokona ta sonda w ciągu", "godzin"),
        ("Laser przemysłowy emituje w ciągu jednej sekundy", "impulsów świetlnych", "Ile łącznie impulsów wyemituje ten laser w czasie nieprzerwanej pracy przez", "godzin"),
    ])
    intro, rate_unit, q_pref, time_unit = ctx
    m_rate = rng.choice([1.5, 2.5, 4.0, 5.0])
    e_rate = rng.choice([4, 5, 6])
    hours = rng.choice([5, 10, 20, 25])
    secs = hours * 3600  # np. 5*3600 = 18000 = 1,8 * 10^4
    raw_val = m_rate * (10 ** e_rate) * secs
    # Wyznacz postać a * 10^k gdzie 1 <= a < 10
    exp_ans = int(math.floor(math.log10(raw_val)))
    mant_ans = round(raw_val / (10 ** exp_ans), 4)

    return {
        "stem": f"{intro} równą ${pl_num(m_rate)} \\cdot 10^{{{e_rate}}}$ {rate_unit}.",
        "command": (
            f"{q_pref} ${hours}$ {time_unit}? Wynik zapisz w notacji wykładniczej, czyli w postaci "
            f"$a \\cdot 10^k$, gdzie $1 \\le a < 10$ oraz $k$ jest liczbą całkowitą. Zapisz obliczenia."
        ),
        "correct_answer": f"{pl_num(mant_ans)} * 10^{exp_ans}",
        "solution_steps": [
            f"Zamieniamy czas ${hours}$ godzin na sekundy: ${hours} \\cdot 3600\\text{{ s}} = {pl_num(secs)}\\text{{ s}} = {pl_num(secs / 10000)} \\cdot 10^4\\text{{ s}}$.",
            f"Mnożymy wartość na sekundę przez czas: $({pl_num(m_rate)} \\cdot 10^{{{e_rate}}}) \\cdot ({pl_num(secs / 10000)} \\cdot 10^4) = {pl_num(round(m_rate * secs / 10000, 4))} \\cdot 10^{{{e_rate + 4}}}$.",
            f"Zapisujemy wynik w notacji wykładniczej ($1 \\le a < 10$): ${pl_num(mant_ans)} \\cdot 10^{{{exp_ans}}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – przeliczenie {hours} h na sekundy ({pl_num(secs)} s).",
            "2 pkt – poprawne pomnożenie wielkości z użyciem potęg liczby 10.",
            f"3 pkt – zapisanie poprawnego wyniku w notacji wykładniczej: {pl_num(mant_ans)} · 10^{exp_ans}.",
        ],
        "grid_height_mm": 56.0,
    }


# ===========================================================================
# 4. PIERWIASTKI (4 nowe generatory)
# ===========================================================================

@register_template(
    template_id="proc_pierwiastki_iloraz_i_suma_abcd",
    topic_id="pierwiastki",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – iloraz pierwiastków i pierwiastek z liczby mieszanej",
)
def gen_proc_pierwiastki_mieszana(rng):
    variant = rng.choice(["mixed", "quotient_cube"])
    if variant == "mixed":
        whole, num, den, r_num, r_den = rng.choice([
            (1, 9, 16, 5, 4),
            (2, 1, 4, 3, 2),
            (2, 7, 9, 5, 3),
            (3, 1, 16, 7, 4),
            (5, 4, 9, 7, 3),
            (6, 1, 4, 5, 2),
        ])
        corr = frac_tex(r_num, r_den)
        w1 = mixed_frac_tex(int(math.isqrt(whole)), int(math.isqrt(num)), int(math.isqrt(den)))
        w2 = frac_tex(whole * den + num, den)
        w3 = frac_tex(r_den, r_num)
        choices, ans = shuffle_abcd(rng, corr, [w1, w2, w3])
        m_str = rf"\sqrt{{{whole}\frac{{{num}}}{{{den}}}}}"
        return {
            "stem": f"Dane jest wyrażenie ${m_str}$.",
            "command": "Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\nWartość tego wyrażenia jest równa",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Zamieniamy liczbę mieszaną pod pierwiastkiem na ułamek niewłaściwy: ${whole}\\frac{{{num}}}{{{den}}} = \\frac{{{whole * den + num}}}{{{den}}}$.",
                f"Obliczamy pierwiastek: $\\sqrt{{\\frac{{{r_num**2}}}{{{r_den**2}}}}} = \\frac{{{r_num}}}{{{r_den}}}$ (odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    # Pierwiastek sześcienny ilorazu
    base_b = rng.choice([2, 3, 5])
    k = rng.choice([2, 3, 4])
    n_top = base_b * (k ** 3)
    corr = f"${k}$"
    w1 = f"${k ** 3}$"
    w2 = rf"$\sqrt[3]{{{k}}}$"
    w3 = f"${k * base_b}$"
    choices, ans = shuffle_abcd(rng, corr, [w1, w2, w3])
    expr = rf"\frac{{\sqrt[3]{{{n_top}}}}}{{\sqrt[3]{{{base_b}}}}}"
    return {
        "stem": f"Dane jest wyrażenie ${expr}$.",
        "command": "Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\nWartość tego wyrażenia jest równa",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Zapisujemy iloraz pierwiastków jako jeden pierwiastek sześcienny: $\\sqrt[3]{{\\frac{{{n_top}}}{{{base_b}}}}} = \\sqrt[3]{{{k ** 3}}} = {k}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_pierwiastki_liczby_calkowite_pomiedzy_abcd",
    topic_id="pierwiastki",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – szacowanie pierwiastków na osi liczbowej",
)
def gen_proc_pierwiastki_przedzial(rng):
    a_int = rng.choice([3, 4, 5, 6])
    b_int = a_int + rng.choice([3, 4, 5])
    low_rad = a_int * a_int - rng.randint(2, 2 * a_int - 2)  # między (a_int-1) a a_int -> pierwsza całkowita >= sqrt to a_int
    high_rad = b_int * b_int + rng.randint(2, 2 * b_int - 1)  # między b_int a (b_int+1) -> ostatnia całkowita <= sqrt to b_int
    count = b_int - a_int + 1

    choices, ans = shuffle_abcd(rng, f"${count}$", [f"${count - 1}$", f"${count + 1}$", f"${high_rad - low_rad}$"])
    s_low = rf"\sqrt{{{low_rad}}}"
    s_high = rf"\sqrt{{{high_rad}}}"
    return {
        "stem": f"Rozważmy wszystkie liczby całkowite większe od ${s_low}$ i jednocześnie mniejsze od ${s_high}$.",
        "command": "Ile jest wszystkich takich liczb całkowitych? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Szacujemy pierwiastki: ${a_int - 1} < {s_low} < {a_int}$ oraz ${b_int} < {s_high} < {b_int + 1}$.",
            f"Szukane liczby całkowite to ${a_int}, {a_int + 1}, \\dots, {b_int}$, których jest ${b_int} - {a_int} + 1 = {count}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_pierwiastki_suma_wyrazow_2pkt",
    topic_id="pierwiastki",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – upraszczanie sumy pierwiastków kwadratowych",
)
def gen_proc_suma_pierwiastkow_2pkt(rng):
    p = rng.choice([2, 3, 5, 7])
    c1, c2, c3 = rng.choice([(5, 3, 2), (6, 2, 3), (7, 4, 2), (5, 4, 3)])
    n1, n2, n3 = p * c1 * c1, p * c2 * c2, p * c3 * c3
    k_res = c1 + c2 - c3
    expr = rf"\sqrt{{{n1}}} + \sqrt{{{n2}}} - \sqrt{{{n3}}}"
    ans_tex = f"{k_res}*sqrt({p})"

    return {
        "stem": f"Dane jest wyrażenie $W = {expr}$.",
        "command": f"Zapisz wyrażenie $W$ w najprostszej postaci $k\\sqrt{{{p}}}$, gdzie $k$ jest liczbą całkowitą, i podaj wartość liczby $k$. Zapisz obliczenia.",
        "correct_answer": f"W = {k_res}√{p} (k = {k_res})",
        "solution_steps": [
            f"Wyłączamy czynniki przed znak pierwiastka: $\\sqrt{{{n1}}} = {c1}\\sqrt{{{p}}}$, $\\sqrt{{{n2}}} = {c2}\\sqrt{{{p}}}$ oraz $\\sqrt{{{n3}}} = {c3}\\sqrt{{{p}}}$.",
            f"Obliczamy: $W = {c1}\\sqrt{{{p}}} + {c2}\\sqrt{{{p}}} - {c3}\\sqrt{{{p}}} = {k_res}\\sqrt{{{p}}}$, więc $k = {k_res}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne wyłączenie czynnika przed znak pierwiastka w co najmniej dwóch składnikach.",
            f"2 pkt – otrzymanie postaci {k_res}√{p} i wskazanie k = {k_res}.",
        ],
        "grid_height_mm": 48.0,
    }


@register_template(
    template_id="proc_pierwiastki_prostokat_przekatna_3pkt",
    topic_id="pierwiastki",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – obliczenia geometryczne z pierwiastkami i twierdzeniem Pitagorasa",
)
def gen_proc_prostokat_pierwiastki_3pkt(rng):
    # Prostokąt o bokach k1*sqrt(p) i k2*sqrt(p) tak, że p*(k1^2 + k2^2) jest pełnym kwadratem!
    # Np. p=5, k1=1, k2=2 -> 5*(1+4)=25 -> przekątna = 5! Albo p=2, k1=1, k2=7 -> 2*50=100 -> d=10! Albo p=3, k1=2, k2=4 -> nie; p=5, k1=2, k2=4 -> 5*20=100 -> d=10! Albo p=10, k1=1, k2=3 -> 10*10=100 -> d=10! Albo p=2, k1=3, k2=3 -> 2*18=36 -> d=6!
    p, k1, k2, diag = rng.choice([
        (5, 2, 4, 10),
        (5, 3, 6, 15),
        (10, 1, 3, 10),
        (13, 2, 3, 13),
        (17, 1, 4, 17),
        (2, 1, 7, 10),
    ])
    area = p * k1 * k2
    s_a = rf"\sqrt{{{p}}}" if k1 == 1 else rf"{k1}\sqrt{{{p}}}"
    s_b = rf"{k2}\sqrt{{{p}}}"

    return {
        "stem": f"Sąsiednie boki prostokąta $ABCD$ mają długości $|AB| = {s_b}$ cm oraz $|BC| = {s_a}$ cm.",
        "command": "Oblicz pole tego prostokąta oraz długość jego przekątnej $AC$. Zapisz obliczenia.",
        "correct_answer": f"P = {area} cm^2, |AC| = {diag} cm",
        "solution_steps": [
            f"Pole prostokąta: $P = |AB| \\cdot |BC| = {s_b} \\cdot {s_a} = {k1 * k2} \\cdot {p} = {area}\\text{{ cm}}^2$.",
            f"Z twierdzenia Pitagorasa dla trójkąta $ABC$: $|AC|^2 = ({s_b})^2 + ({s_a})^2 = {k2*k2*p} + {k1*k1*p} = {diag*diag}$.",
            f"Stąd długość przekątnej wynosi $|AC| = \\sqrt{{{diag*diag}}} = {diag}\\text{{ cm}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne obliczenie pola prostokąta ({area} cm^2).",
            f"2 pkt – poprawne zapisanie i obliczenie kwadratu przekątnej ({diag*diag}).",
            f"3 pkt – pełne rozwiązanie z podaniem pola ({area} cm^2) i przekątnej ({diag} cm).",
        ],
        "grid_height_mm": 56.0,
    }


# ===========================================================================
# 5. WYRAŻENIA ALGEBRAICZNE (4 nowe generatory)
# ===========================================================================

@register_template(
    template_id="proc_wyrazenia_pole_figury_abcd",
    topic_id="wyrazenia_algebraiczne",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – zapisywanie pola i obwodu za pomocą wyrażeń algebraicznych",
)
def gen_proc_wyrazenia_pole_abcd(rng):
    c1 = rng.randint(2, 6)
    c2 = rng.randint(1, 5)
    # Prostokąt o bokach (2x + c1) oraz (x - c2) albo (x + c1) i (3x + c2)
    m = rng.choice([2, 3])
    op2 = rng.choice(["+", "-"])
    b_const = c2 if op2 == "+" else -c2
    # (m*x + c1)*(x + b_const) = m*x^2 + (m*b_const + c1)*x + c1*b_const
    mid = m * b_const + c1
    last = c1 * b_const

    def _fmt_quad(a2: int, a1: int, a0: int) -> str:
        s = f"{a2}x^2"
        if a1 > 0:
            s += f" + {a1}x" if a1 != 1 else " + x"
        elif a1 < 0:
            s += f" - {abs(a1)}x" if a1 != -1 else " - x"
        if a0 > 0:
            s += f" + {a0}"
        elif a0 < 0:
            s += f" - {abs(a0)}"
        return f"${s}$"

    corr = _fmt_quad(m, mid, last)
    w1 = _fmt_quad(m, 0, last)
    w2 = _fmt_quad(m, c1 + b_const, last)
    w3 = f"${2 * (m + 1)}x {'+' if c1 + b_const >= 0 else '-'} {abs(2 * (c1 + b_const))}$"
    choices, ans = shuffle_abcd(rng, corr, [w1, w2, w3])

    side2_str = f"x + {c2}" if op2 == "+" else f"x - {c2}"
    cond = "" if op2 == "+" else f" (gdzie $x > {c2}$)"
    return {
        "stem": f"Boki prostokąta mają długości $({m}x + {c1})$ oraz $({side2_str})${cond}.",
        "command": "Które wyrażenie algebraiczne opisuje pole tego prostokąta po redukcji wyrazów podobnych? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Mnożymy długości sąsiednich boków: $({m}x + {c1})({side2_str}) = {m}x^2 {'+' if m*b_const >= 0 else '-'} {abs(m*b_const)}x + {c1}x {'+' if last >= 0 else '-'} {abs(last)}$.",
            f"Po redukcji wyrazów podobnych otrzymujemy {corr} (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_wyrazenia_wartosc_dla_ujemnej_abcd",
    topic_id="wyrazenia_algebraiczne",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – wartość liczbowa wyrażenia dla argumentów ujemnych",
)
def gen_proc_wartosc_ujemna(rng):
    x_val = rng.choice([-4, -3, -2])
    y_val = rng.choice([2, 3, 5])
    a = rng.choice([2, 3])
    # W = a * x^2 - x * y
    res = a * (x_val ** 2) - x_val * y_val
    w1 = a * (x_val ** 2) + x_val * y_val  # błąd ze znakiem przy -xy
    w2 = -a * (x_val ** 2) - x_val * y_val  # błąd ze znakiem przy x^2
    w3 = (a * x_val) ** 2 - x_val * y_val
    choices, ans = shuffle_abcd(rng, f"${res}$", [f"${w1}$", f"${w2}$", f"${w3}$"])

    return {
        "stem": f"Dane jest wyrażenie algebraiczne $W = {a}a^2 - ab$.",
        "command": f"Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\nWartość wyrażenia $W$ dla $a = {pl_num(x_val)}$ oraz $b = {y_val}$ jest równa",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Podstawiamy $a = {pl_num(x_val)}$ oraz $b = {y_val}$: $W = {a} \\cdot ({pl_num(x_val)})^2 - ({pl_num(x_val)}) \\cdot {y_val}$.",
            f"Obliczamy: $W = {a} \\cdot {x_val**2} + {abs(x_val) * y_val} = {a * x_val**2} + {abs(x_val) * y_val} = {res}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_wyrazenia_roznica_obwodow_2pkt",
    topic_id="wyrazenia_algebraiczne",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – przekształcanie wyrażeń opisujących obwody figur",
)
def gen_proc_roznica_obwodow_2pkt(rng):
    k = rng.choice([2, 3, 4])
    d1 = rng.randint(3, 8)
    d2 = rng.randint(2, 7)
    # Kwadrat o boku (k*x + d1) -> obwód 4kx + 4d1
    # Trójkąt równoboczny o boku ((k+1)*x - d2) lub prostokąt o bokach (2kx - d2) i d1
    # Zróbmy tak, aby x SIĘ SKRÓCIŁO i różnica obwodów była stałą liczbą niezależną od x!
    # Kwadrat o boku (3x + d1) -> obwód 12x + 4d1; Trójkąt równoboczny o boku (4x - d2) -> obwód 12x - 3d2!
    mult_sq, mult_tri = rng.choice([(3, 4), (6, 8), (3, 4)])
    diff_const = 4 * d1 + 3 * d2

    return {
        "stem": (
            f"Rozważmy kwadrat o boku długości $({mult_sq}x + {d1})$ cm oraz trójkąt równoboczny o boku "
            f"długości $({mult_tri}x - {d2})$ cm, gdzie $x > {math.ceil(d2 / mult_tri) + 1}$."
        ),
        "command": "Wykaż, że różnica obwodów tego kwadratu i tego trójkąta nie zależy od wartości $x$, i oblicz tę różnicę. Zapisz obliczenia.",
        "correct_answer": f"{diff_const} cm",
        "solution_steps": [
            f"Obwód kwadratu wynosi $O_1 = 4({mult_sq}x + {d1}) = {4 * mult_sq}x + {4 * d1}$ (cm), a obwód trójkąta równobocznego $O_2 = 3({mult_tri}x - {d2}) = {3 * mult_tri}x - {3 * d2}$ (cm).",
            f"Różnica obwodów: $O_1 - O_2 = ({4 * mult_sq}x + {4 * d1}) - ({3 * mult_tri}x - {3 * d2}) = {diff_const}$ cm – wynik jest stałą liczbą i nie zależy od $x$.",
        ],
        "scoring_scheme": [
            "1 pkt – poprawne zapisanie obwodów obu figur za pomocą wyrażeń algebraicznych.",
            f"2 pkt – poprawne odjęcie wyrażeń z uwzględnieniem znaków w nawiasie i otrzymanie stałej {diff_const} cm.",
        ],
        "grid_height_mm": 52.0,
    }


@register_template(
    template_id="proc_wyrazenia_podzielnosc_sumy_3pkt",
    topic_id="wyrazenia_algebraiczne",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – dowód algebraiczny podzielności liczb kolejnych",
)
def gen_proc_dowod_kolejne_3pkt(rng):
    variant = rng.choice(["four_even", "three_odd_plus", "five_consec"])
    if variant == "four_even":
        # Suma czterech kolejnych liczb parzystych + 4 jest podzielna przez 8:
        # 2n + (2n+2) + (2n+4) + (2n+6) + 4 = 8n + 16 = 8(n + 2)
        c_add = rng.choice([4, 12, 20])
        sum_c = 12 + c_add
        q = sum_c // 8
        return {
            "stem": f"Rozważmy dowolne cztery kolejne liczby naturalne parzyste.",
            "command": f"Uzasadnij, że suma tych czterech liczb powiększona o ${c_add}$ jest zawsze liczbą podzielną przez $8$. Zapisz przekształcenia algebraiczne.",
            "correct_answer": f"8n + {sum_c} = 8(n + {q})",
            "solution_steps": [
                "Oznaczmy cztery kolejne liczby naturalne parzyste jako: $2n$, $2n + 2$, $2n + 4$ oraz $2n + 6$, gdzie $n$ jest liczbą naturalną.",
                f"Dodajemy te liczby i powiększamy wynik o ${c_add}$: $2n + (2n + 2) + (2n + 4) + (2n + 6) + {c_add} = 8n + {sum_c}$.",
                f"Wyłączamy czynnik $8$ przed nawias: $8(n + {q})$. Ponieważ $n + {q}$ jest liczbą całkowitą, wyrażenie dzieli się przez $8$.",
            ],
            "scoring_scheme": [
                "1 pkt – poprawne zapisanie czterech kolejnych liczb parzystych za pomocą jednej zmiennej.",
                f"2 pkt – zredukowanie sumy do postaci 8n + {sum_c}.",
                f"3 pkt – wyłączenie 8 przed nawias i sformułowanie poprawnego wniosku.",
            ],
            "grid_height_mm": 56.0,
        }

    if variant == "three_odd_plus":
        # Suma trzech kolejnych liczb nieparzystych: (2n+1) + (2n+3) + (2n+5) = 6n + 9 -> + 3 daje 6n + 12 = 6(n+2) podzielne przez 6!
        c_add = rng.choice([3, 9, 15])
        sum_c = 9 + c_add
        q = sum_c // 6
        return {
            "stem": "Rozważmy dowolne trzy kolejne liczby naturalne nieparzyste.",
            "command": f"Uzasadnij, że suma tych trzech liczb powiększona o ${c_add}$ jest podzielna przez $6$. Zapisz przekształcenia algebraiczne.",
            "correct_answer": f"6n + {sum_c} = 6(n + {q})",
            "solution_steps": [
                "Trzy kolejne liczby nieparzyste możemy zapisać jako $2n + 1$, $2n + 3$ oraz $2n + 5$ ($n \\in \\mathbb{N}$).",
                f"Ich suma powiększona o ${c_add}$ wynosi: $(2n + 1) + (2n + 3) + (2n + 5) + {c_add} = 6n + {sum_c}$.",
                f"Zapisujemy wynik jako $6(n + {q})$, co przy całkowitym $n + {q}$ dowodzi podzielności przez $6$.",
            ],
            "scoring_scheme": [
                "1 pkt – algebraiczny zapis trzech kolejnych liczb nieparzystych.",
                f"2 pkt – poprawne dodanie wyrażeń i otrzymanie 6n + {sum_c}.",
                "3 pkt – wyłączenie 6 przed nawias wraz z komentarzem uzasadniającym podzielność.",
            ],
            "grid_height_mm": 56.0,
        }

    # Suma pięciu kolejnych liczb całkowitych jest podzielna przez 5
    return {
        "stem": "Rozważmy pięć kolejnych liczb całkowitych.",
        "command": "Uzasadnij, że suma dowolnych pięciu kolejnych liczb całkowitych jest podzielna przez $5$. Zapisz przekształcenia algebraiczne.",
        "correct_answer": "5k + 10 = 5(k + 2)",
        "solution_steps": [
            "Oznaczmy najmniejszą z tych pięciu liczb przez $k$ ($k \\in \\mathbb{Z}$). Kolejne liczby to $k+1, k+2, k+3, k+4$.",
            "Obliczamy sumę: $k + (k+1) + (k+2) + (k+3) + (k+4) = 5k + 10$.",
            "Wyłączamy $5$ przed nawias: $5(k + 2)$. Ponieważ $k + 2$ jest liczbą całkowitą, suma jest podzielna przez $5$.",
        ],
        "scoring_scheme": [
            "1 pkt – zapisanie pięciu kolejnych liczb całkowitych za pomocą zmiennej.",
            "2 pkt – poprawne obliczenie sumy 5k + 10.",
            "3 pkt – zapisanie iloczynu 5(k + 2) i wniosek o podzielności przez 5.",
        ],
        "grid_height_mm": 56.0,
    }


# ===========================================================================
# 6. RÓWNANIA I ZADANIA TEKSTOWE (5 nowych generatorów)
# ===========================================================================

@register_template(
    template_id="proc_rownania_wiek_rodzenstwa_2pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – zadanie tekstowe o wieku teraz i za kilka lat",
)
def gen_proc_wiek_2pkt(rng):
    pair = rng.choice([
        ("Tata", "syna", "taty", "syn"),
        ("Mama", "córki", "mamy", "córka"),
        ("Babcia", "wnuczki", "babci", "wnuczka"),
    ])
    p_nom, c_gen, p_gen, c_nom = pair
    child_now = rng.randint(8, 15)
    mult_now = rng.choice([3, 4]) if p_nom != "Babcia" else rng.choice([5, 6])
    parent_now = mult_now * child_now
    years_ahead = rng.choice([4, 5, 6, 8])
    sum_future = (child_now + years_ahead) + (parent_now + years_ahead)

    return {
        "stem": (
            f"Obecnie {p_nom.lower()} ma ${mult_now}$ razy więcej lat niż {c_nom}. "
            f"Za ${years_ahead}$ {'lata' if years_ahead <= 4 else 'lat'} będą mieli łącznie ${sum_future}$ lat."
        ),
        "command": f"Oblicz, ile lat ma obecnie {c_nom}, a ile lat ma obecnie {p_nom.lower()}. Zapisz obliczenia.",
        "correct_answer": f"{c_nom}: {child_now} lat, {p_nom.lower()}: {parent_now} lat",
        "solution_steps": [
            f"Oznaczmy obecny wiek ({c_nom}) przez $x$, a obecny wiek ({p_gen}) przez ${mult_now}x$.",
            f"Za ${years_ahead}$ {'lata' if years_ahead <= 4 else 'lat'} ich wiek wyniesie odpowiednio $x + {years_ahead}$ oraz ${mult_now}x + {years_ahead}$. Z równania $(x + {years_ahead}) + ({mult_now}x + {years_ahead}) = {sum_future}$ otrzymujemy ${mult_now + 1}x = {sum_future - 2 * years_ahead}$, skąd $x = {child_now}$ oraz ${mult_now}x = {parent_now}$.",
        ],
        "scoring_scheme": [
            "1 pkt – ułożenie poprawnego równania uwzględniającego przyrost wieku obu osób.",
            f"2 pkt – podanie obecnego wieku obu osób: {child_now} i {parent_now} lat.",
        ],
        "grid_height_mm": 52.0,
    }


@register_template(
    template_id="proc_rownania_monety_banknoty_3pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Styl CKE – zadanie o monetach / banknotach dwóch nominałów",
)
def gen_proc_banknoty_3pkt(rng):
    v_small, v_big, kind_pl = rng.choice([
        (2, 5, "monet"),
        (10, 20, "banknotów"),
        (20, 50, "banknotów"),
    ])
    cnt_big = rng.randint(7, 16)
    diff = rng.randint(4, 11)
    more_small = rng.choice([True, False])
    cnt_small = cnt_big + diff if more_small else max(3, cnt_big - diff)
    tot_cnt = cnt_big + cnt_small
    tot_val = cnt_small * v_small + cnt_big * v_big

    return {
        "stem": (
            f"W kasetce znajdują się wyłącznie nominały ${v_small}$ zł oraz ${v_big}$ zł – łącznie jest tam "
            f"dokładnie ${tot_cnt}$ {kind_pl} o sumarycznej wartości ${pl_num(tot_val)}$ zł."
        ),
        "command": f"Oblicz, ile sztuk nominału ${v_big}$ zł oraz ile sztuk nominału ${v_small}$ zł znajduje się w kasetce. Zapisz obliczenia.",
        "correct_answer": f"{cnt_big} szt. po {v_big} zł oraz {cnt_small} szt. po {v_small} zł",
        "solution_steps": [
            f"Oznaczmy przez $x$ liczbę sztuk po ${v_big}$ zł; wówczas sztuk po ${v_small}$ zł jest ${tot_cnt} - x$.",
            f"Układamy równanie wartości: ${v_big}x + {v_small}({tot_cnt} - x) = {tot_val}$, czyli ${v_big - v_small}x + {v_small * tot_cnt} = {tot_val}$.",
            f"Stąd ${v_big - v_small}x = {tot_val - v_small * tot_cnt}$, więc $x = {cnt_big}$ (nominał ${v_big}$ zł) oraz ${tot_cnt} - {cnt_big} = {cnt_small}$ (nominał ${v_small}$ zł).",
        ],
        "scoring_scheme": [
            "1 pkt – poprawne oznaczenie niewiadomej i wyrażenie liczby drugiego nominału.",
            "2 pkt – ułożenie i poprawne rozwiązanie równania wartości.",
            f"3 pkt – podanie liczby sztuk obu nominałów ({cnt_big} i {cnt_small}).",
        ],
        "grid_height_mm": 56.0,
    }


@register_template(
    template_id="proc_rownania_konkurs_punkty_ujemne_2pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – quiz z punktami dodatnimi i ujemnymi",
)
def gen_proc_konkurs_punkty(rng):
    n_q = rng.choice([20, 25, 30])
    pts_ok = rng.choice([4, 5])
    pts_bad = rng.choice([1, 2])
    n_good = rng.randint(n_q // 2 + 2, n_q - 3)
    n_wrong = n_q - n_good
    score = n_good * pts_ok - n_wrong * pts_bad

    who = rng.choice(["Uczestnik teleturnieju", "Uczennica w konkursie przyrodniczym", "Zawodnik ligi matematycznej"])
    return {
        "stem": (
            f"Test składał się z ${n_q}$ pytań. Za każdą poprawną odpowiedź przyznawano ${pts_ok}$ pkt, "
            f"natomiast za każdą błędną odpowiedź odejmowano ${pts_bad}$ pkt. {who} udzielił(a) odpowiedzi "
            f"na wszystkie pytania i uzyskał(a) łącznie ${score}$ pkt."
        ),
        "command": "Oblicz, na ile pytań udzielono poprawnej odpowiedzi. Zapisz obliczenia.",
        "correct_answer": f"{n_good}",
        "solution_steps": [
            f"Niech $x$ oznacza liczbę poprawnych odpowiedzi, a ${n_q} - x$ liczbę błędnych odpowiedzi.",
            f"Z równania ${pts_ok}x - {pts_bad}({n_q} - x) = {score}$ otrzymujemy ${pts_ok + pts_bad}x - {pts_bad * n_q} = {score} \\Rightarrow {pts_ok + pts_bad}x = {score + pts_bad * n_q} \\Rightarrow x = {n_good}$.",
        ],
        "scoring_scheme": [
            "1 pkt – zapisanie poprawnego równania z uwzględnieniem odejmowanych punktów.",
            f"2 pkt – poprawne wyznaczenie liczby poprawnych odpowiedzi: {n_good}.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_rownania_listwa_trzy_czesci_abcd",
    topic_id="rownania_tekstowe",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – podział odcinka / sznurka na części",
)
def gen_proc_listwa_abcd(rng):
    x = rng.randint(18, 35)
    m = rng.choice([2, 3])
    d = rng.randint(5, 16)
    total = x + m * x + (x + d)
    obj = rng.choice(["Drewnianą listwę", "Stalowy pręt", "Linę wspinaczkową", "Wstążkę dekoracyjną"])
    choices, ans = shuffle_abcd(rng, f"${x}$ cm", [f"${m * x}$ cm", f"${x + d}$ cm", f"${total // 3}$ cm"])

    return {
        "stem": (
            f"{obj} o długości ${total}$ cm rozcięto bez reszty na trzy części. Druga część jest ${m}$ razy dłuższa "
            f"od pierwszej, a trzecia część jest o ${d}$ cm dłuższa od pierwszej."
        ),
        "command": "Jaką długość ma najkrótsza (pierwsza) z otrzymanych części? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Oznaczmy długość pierwszej części przez $x$. Wówczas $x + {m}x + (x + {d}) = {total}$.",
            f"Stąd ${m + 2}x = {total - d}$, czyli $x = {x}\\text{{ cm}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_rownania_rzedy_krzesla_3pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – wieloetapowe zadanie tekstowe o miejscach i grupach",
)
def gen_proc_sala_miejsca_3pkt(rng):
    # W auli ustawiono r rzędów krzeseł po tyle samo w każdym rzędzie. Gdy dostawiono 2 rzędy, a z każdego rzędu zabrano po 3 krzesła... albo prostsze liniowe CKE:
    # Gdy w każdym rzędzie usiądzie po a osób, zabraknie miejsc dla b osób; gdy po c osób, zostanie d wolnych miejsc!
    n_rows = rng.randint(11, 18)
    a_per, c_per = rng.choice([(12, 15), (14, 16), (15, 18), (16, 20), (8, 10)])
    standing = rng.randint(5, 15)
    people = n_rows * a_per + standing
    free_seats = n_rows * c_per - people
    while free_seats <= 2:
        n_rows += 1
        free_seats = n_rows * c_per - people

    ctx = rng.choice([
        ("W sali konferencyjnej przygotowano pewną liczbę długich stołów", "przy każdym stole posadzono", "uczestników", "zabrakło miejsc dla", "wolnych miejsc"),
        ("Na wyjazd integracyjny zamówiono pewną liczbę busów", "do każdego busa przydzielono", "pasażerów", "bez miejsca pozostało", "wolnych foteli"),
    ])
    intro, verb, who_gen, lack_txt, free_txt = ctx

    return {
        "stem": (
            f"{intro}. Gdy {verb} po ${a_per}$ {who_gen}, to {lack_txt} ${standing}$ osób. "
            f"Gdy natomiast {verb} po ${c_per}$ {who_gen}, to pozostało dokładnie ${free_seats}$ {free_txt}."
        ),
        "command": f"Oblicz łączną liczbę wszystkich {who_gen}. Zapisz obliczenia.",
        "correct_answer": f"{people}",
        "solution_steps": [
            f"Oznaczmy przez $x$ liczbę grup/rzędów. Liczbę osób można zapisać na dwa sposoby: ${a_per}x + {standing}$ oraz ${c_per}x - {free_seats}$.",
            f"Z równania ${a_per}x + {standing} = {c_per}x - {free_seats}$ otrzymujemy ${c_per - a_per}x = {standing + free_seats}$, skąd $x = {n_rows}$.",
            f"Łączna liczba {who_gen}: ${a_per} \\cdot {n_rows} + {standing} = {people}$.",
        ],
        "scoring_scheme": [
            "1 pkt – ułożenie poprawnego równania wiążącego oba sposoby rozmieszczenia.",
            f"2 pkt – wyznaczenie $x = {n_rows}$.",
            f"3 pkt – obliczenie łącznej liczby osób: {people}.",
        ],
        "grid_height_mm": 58.0,
    }


# ===========================================================================
# 7. PRĘDKOŚĆ, DROGA, CZAS (4 nowe generatory)
# ===========================================================================

@register_template(
    template_id="proc_predkosc_spotkanie_naprzeciw_2pkt",
    topic_id="predkosc_droga_czas",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – ruch naprzeciw siebie dwóch obiektów",
)
def gen_proc_spotkanie_2pkt(rng):
    v1, v2 = rng.choice([(14, 16), (18, 22), (45, 55), (55, 65), (12, 18)])
    t_min = rng.choice([20, 30, 40, 45, 90])
    while ((v1 + v2) * t_min) % 60 != 0:
        t_min = 30
    dist = ((v1 + v2) * t_min) // 60
    start_h, start_m = rng.choice([(9, 15), (10, 20), (11, 10), (13, 30)])
    end_tot = start_h * 60 + start_m + t_min
    end_str = f"{end_tot // 60}:{end_tot % 60:02d}"

    actor = "rowerzystów" if v1 < 30 else "kierowców"
    return {
        "stem": (
            f"Z dwóch miejscowości odległych od siebie o ${dist}$ km wyruszyli jednocześnie naprzeciw siebie dwaj {actor} "
            f"o godzinie ${start_h}:{start_m:02d}$. Pierwszy poruszał się ze średnią prędkością ${v1}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$, "
            f"a drugi – ze średnią prędkością ${v2}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$...."
        ).replace("....", "."),
        "command": "O której godzinie nastąpiło ich spotkanie na trasie? Zapisz obliczenia.",
        "correct_answer": end_str,
        "solution_steps": [
            f"W ciągu godziny obaj zbliżają się do siebie o ${v1} + {v2} = {v1 + v2}\\text{{ km}}$.",
            f"Czas do spotkania wynosi $t = \\frac{{{dist}}}{{{v1 + v2}}}\\text{{ h}} = {t_min}\\text{{ min}}$. Dodając ${t_min}\\text{{ min}}$ do ${start_h}:{start_m:02d}$, otrzymujemy godzinę **{end_str}**.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie prędkości zbliżania się ({v1 + v2} km/h) i czasu jazdy ({t_min} min).",
            f"2 pkt – podanie poprawnej godziny spotkania: {end_str}.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="proc_predkosc_przeliczanie_ms_kmh_ab_cd",
    topic_id="predkosc_droga_czas",
    subtype="ab_cd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – zamiana jednostek prędkości m/s i km/h",
)
def gen_proc_ms_kmh_abcd(rng):
    v_ms = rng.choice([10, 15, 20, 25, 30])
    v_kmh = int(round(v_ms * 3.6))
    bad_kmh = v_ms * 60 // 10

    d_m = rng.choice([450, 600, 750, 900])
    while d_m % v_ms != 0:
        d_m = 600
    t_s = d_m // v_ms
    bad_t = t_s + 15

    if rng.random() < 0.5:
        opts1, a1 = {"A": f"${v_kmh}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$", "B": f"${bad_kmh}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$"}, "A"
    else:
        opts1, a1 = {"A": f"${bad_kmh}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$", "B": f"${v_kmh}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$"}, "B"

    if rng.random() < 0.5:
        opts2, a2 = {"C": f"${t_s}$ s", "D": f"${bad_t}$ s"}, "C"
    else:
        opts2, a2 = {"C": f"${bad_t}$ s", "D": f"${t_s}$ s"}, "D"

    obj = rng.choice(["Dron pomiarowy", "Pociąg podmiejski", "Motocyklista na torze"])
    return {
        "stem": f"{obj} porusza się ruchem jednostajnym ze stałą prędkością równą ${v_ms}\\;\\frac{{\\text{{m}}}}{{\\text{{s}}}}$.",
        "command": "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D.",
        "ab_cd_parts": [
            {"prefix": "Prędkość tego ruchu wyrażona w kilometrach na godzinę jest równa", "suffix": ".", "options": opts1},
            {"prefix": f"Drogę równą ${d_m}$ metrów obiekt ten pokonuje w czasie", "suffix": ".", "options": opts2},
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Przeliczamy jednostki: ${v_ms} \\cdot 3,6 = {v_kmh}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$ (**{a1}**).",
            f"Czas pokonania ${d_m}$ m wynosi ${d_m} : {v_ms} = {t_s}\\text{{ s}}$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna para odpowiedzi.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="proc_predkosc_srednia_cala_trasa_abcd",
    topic_id="predkosc_droga_czas",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – prędkość średnia na trasie dwuetapowej",
)
def gen_proc_srednia_predkosc_abcd(rng):
    # Etap 1: d1 km w t1 h, Etap 2: d2 km w t2 h -> v_sr = (d1+d2)/(t1+t2) != średniej arytmetycznej prędkości!
    d1, t1, d2, t2 = rng.choice([
        (60, 1, 120, 3),   # v1=60, v2=40 -> v_sr = 180/4 = 45 (dystraktor: 50!)
        (80, 1, 100, 2),   # v1=80, v2=50 -> v_sr = 180/3 = 60 (dystraktor: 65!)
        (30, 2, 12, 1),    # v1=15, v2=12 -> v_sr = 42/3 = 14 (dystraktor: 13,5!)
        (90, 1, 150, 3),   # v1=90, v2=50 -> v_sr = 240/4 = 60 (dystraktor: 70!)
    ])
    v_avg = (d1 + d2) // (t1 + t2)
    v1, v2 = d1 // t1, d2 // t2
    arith_bad = pl_num((v1 + v2) / 2)

    choices, ans = shuffle_abcd(
        rng,
        f"${v_avg}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$",
        [
            f"${arith_bad}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$",
            f"${v1 + v2}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$",
            f"${(d1 + d2) // 2}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$",
        ],
    )
    return {
        "stem": (
            f"Pojazd przejechał pierwszy odcinek trasy o długości ${d1}$ km w czasie ${t1}$ h, "
            f"a bezpośrednio potem drugi odcinek o długości ${d2}$ km w czasie ${t2}$ h."
        ),
        "command": "Ile wyniosła średnia prędkość tego pojazdu na całej trasie? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Całkowita droga wynosi ${d1} + {d2} = {d1 + d2}\\text{{ km}}$, a całkowity czas jazdy ${t1} + {t2} = {t1 + t2}\\text{{ h}}$.",
            f"Średnia prędkość na całej trasie: $v_{{\\text{{śr}}}} = \\frac{{{d1 + d2}}}{{{t1 + t2}}} = {v_avg}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="proc_predkosc_tunel_pociag_3pkt",
    topic_id="predkosc_droga_czas",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – przejazd pociągu przez most lub tunel",
)
def gen_proc_pociag_tunel_3pkt(rng):
    v_kmh = rng.choice([54, 72, 90])
    v_ms = v_kmh * 10 // 36  # 15, 20, 25 m/s
    len_train = rng.choice([120, 150, 180, 200, 250])
    t_sec = rng.choice([40, 50, 60, 75, 80])
    total_d = v_ms * t_sec
    while total_d <= len_train + 100:
        t_sec += 20
        total_d = v_ms * t_sec
    len_tunnel = total_d - len_train
    struct = rng.choice(["tunel górski", "wiadukt stalowy", "most kolejowy"])

    return {
        "stem": (
            f"Pociąg towarowy o długości ${len_train}$ m porusza się ze stałą prędkością ${v_kmh}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$. "
            f"Od chwili wjazdu czoła lokomotywy na {struct} do chwili całkowitego zjazdu ostatniego wagonu upłynęło dokładnie ${t_sec}$ sekund."
        ),
        "command": f"Oblicz długość (w metrach), jaką ma ten {struct}. Zapisz obliczenia.",
        "correct_answer": f"{len_tunnel} m",
        "solution_steps": [
            f"Zamieniamy prędkość pociągu na metry na sekundę: ${v_kmh}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}} = \\frac{{{v_kmh} \\cdot 1000\\text{{ m}}}}{{3600\\text{{ s}}}} = {v_ms}\\;\\frac{{\\text{{m}}}}{{\\text{{s}}}}$.",
            f"W ciągu ${t_sec}\\text{{ s}}$ czoło lokomotywy pokonało drogę równą sumie długości obiektu i długości pociągu: $s = {v_ms} \\cdot {t_sec} = {pl_num(total_d)}\\text{{ m}}$.",
            f"Długość obiektu wynosi: ${pl_num(total_d)} - {len_train} = {pl_num(len_tunnel)}\\text{{ m}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – zamiana prędkości {v_kmh} km/h na {v_ms} m/s.",
            f"2 pkt – obliczenie całkowitej drogi przebytej przez czoło pociągu ({pl_num(total_d)} m).",
            f"3 pkt – odjęcie długości pociągu i podanie poprawnego wyniku: {pl_num(len_tunnel)} m.",
        ],
        "grid_height_mm": 58.0,
    }
