"""Dział 3: Potęgi o wykładnikach całkowitych i notacja wykładnicza."""

from __future__ import annotations

from ..math_text import frac_tex, pl_num, shuffle_abcd
from .base import register_template


@register_template(
    template_id="potegi_iloraz_iloczyn_ab_cd",
    topic_id="potegi_notacja",
    subtype="ab_cd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2023 zad. 7",
)
def gen_potegi_ab_cd(rng):
    # Część 1: iloraz (a*b)^n / b^n = a^n
    a, b = rng.choice([(2, 5), (3, 4), (2, 7), (3, 5), (4, 3)])
    ab = a * b
    n = rng.randint(6, 11)
    corr1 = f"${a}^{{{n}}}$"
    wrong1 = f"${ab - b}^{{{n}}}$" if (ab - b) != a else f"${a}^{{1}}$"

    if rng.choice([True, False]):
        opts1 = {"A": corr1, "B": wrong1}
        c1 = "A"
    else:
        opts1 = {"A": wrong1, "B": corr1}
        c1 = "B"

    # Część 2: iloczyn 2^(2k) * 5^(2k) zapisany jako 2^(2k) * 25^k = 10^(2k) albo 4^k * 5^(2k)
    k = rng.choice([3, 4, 5])
    exp2 = 2 * k
    corr2 = f"$10^{{{exp2}}}$"
    wrong2 = f"$50^{{{exp2 + k}}}$"

    if rng.choice([True, False]):
        opts2 = {"C": corr2, "D": wrong2}
        c2 = "C"
    else:
        opts2 = {"C": wrong2, "D": corr2}
        c2 = "D"

    stem = "Dane są dwa wyrażenia zapisane w postaci potęg."
    command = "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D."

    parts = [
        {
            "prefix": f"Iloraz {frac_tex(f'{ab}^{{{n}}}', f'{b}^{{{n}}}')} jest równy",
            "suffix": ".",
            "options": opts1,
        },
        {
            "prefix": f"Iloczyn $2^{{{exp2}}} \\cdot 25^{{{k}}}$ jest równy",
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
            f"Korzystamy ze wzoru na iloraz potęg o tym samym wykładniku: "
            f"{frac_tex(f'{ab}^{{{n}}}', f'{b}^{{{n}}}')} $= ({ab} : {b})^{{{n}}} = {a}^{{{n}}}$ (wybór **{c1}**).",
            f"Zapisujemy $25^{{{k}}} = (5^2)^{{{k}}} = 5^{{{exp2}}}$. Wówczas $2^{{{exp2}}} \\cdot 5^{{{exp2}}} = (2 \\cdot 5)^{{{exp2}}} = 10^{{{exp2}}}$ (wybór **{c2}**).",
        ],
    }


@register_template(
    template_id="potegi_notacja_porzadkowanie_abcd",
    topic_id="potegi_notacja",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Styczeń 2026 (próbny) zad. 4",
)
def gen_notacja_porzadkowanie_abcd(rng):
    # Trzy liczby x, y, z rzędu 10^-3 .. 10^-2
    # np. x = 5,2 * 10^-3 = 0,0052; y = 0,0029; z = 140 * 10^-4 = 0,014
    m_x = rng.choice([4.3, 5.2, 6.4, 7.1])
    val_x = m_x * 1e-3  # 0.0043 .. 0.0071

    m_y = rng.choice([19, 23, 28, 34])
    val_y = m_y * 1e-4  # 0.0019 .. 0.0034

    m_z = rng.choice([120, 140, 160, 180])
    val_z = m_z * 1e-4  # 0.012 .. 0.018

    items = [("x", val_x), ("y", val_y), ("z", val_z)]
    items_sorted = sorted(items, key=lambda t: t[1])
    corr = f"${items_sorted[0][0]} < {items_sorted[1][0]} < {items_sorted[2][0]}$"

    perms = [
        "$x < y < z$",
        "$y < x < z$",
        "$z < x < y$",
        "$y < z < x$",
        "$x < z < y$",
        "$z < y < x$",
    ]
    distractors = [p for p in perms if p != corr][:3]
    choices, ans = shuffle_abcd(rng, corr, distractors)

    y_str = f"0,00{m_y}"
    stem = (
        f"Dane są trzy liczby:\n"
        f"$x = {pl_num(m_x)} \\cdot 10^{{-3}}$,    $y = {y_str}$,    $z = {m_z} \\cdot 10^{{-4}}$.\n"
        f"Liczby te uporządkowano w kolejności od najmniejszej do największej."
    )
    command = "Który zapis przedstawia poprawne uporządkowanie liczb $x$, $y$, $z$? Wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Zapisujemy wszystkie trzy liczby w postaci dziesiętnej:",
            f"$x = {pl_num(m_x)} \\cdot 0,001 = {pl_num(round(val_x, 5))}$,  $y = {y_str}$,  $z = {m_z} \\cdot 0,0001 = {pl_num(round(val_z, 5))}$.",
            f"Porównując części tysięczne i setne, otrzymujemy {corr} (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="potegi_suma_poteg_uzasadnienie",
    topic_id="potegi_notacja",
    subtype="uzasadnienie",
    points=1,
    difficulty=3,
    cke_ref="Wzorzec: CKE Czerwiec 2023 zad. 6",
)
def gen_suma_poteg_uzasadnienie(rng):
    # Czy liczba 2^n + 2^n + 2^n + 2^n jest równa 2^(n+2)?
    base = rng.choice([2, 3, 5])
    # Liczba składników równa base -> base * base^n = base^(n+1)
    n = rng.randint(10, 18)
    terms_str = " + ".join([f"{base}^{{{n}}}"] * base)
    ask_exp = n + 1 if rng.choice([True, False]) else n * base
    is_yes = (ask_exp == n + 1)

    ans_ab = "A" if is_yes else "B"
    r_corr = f"suma ${base}$ jednakowych składników postaci ${base}^{{{n}}}$ jest równa ${base} \\cdot {base}^{{{n}}} = {base}^{{{n + 1}}}$."
    r_w1 = f"przy dodawaniu potęg o tej samej podstawie dodajemy ich wykładniki, otrzymując ${base}^{{{n * base}}}$."
    r_w2 = f"przy dodawaniu potęg dodajemy podstawy i pozostawiamy wykładnik bez zmian, otrzymując ${base * base}^{{{n}}}$."

    r_list = [r_corr, r_w1, r_w2]
    rng.shuffle(r_list)
    r_dict = {str(i + 1): r_list[i] for i in range(3)}
    c_num = next(k for k, v in r_dict.items() if v == r_corr)

    stem = f"Dana jest suma potęg: $S = {terms_str}$."
    command = f"Czy liczba $S$ jest równa ${base}^{{{ask_exp}}}$? Wybierz odpowiedź A albo B i jej uzasadnienie spośród 1., 2. albo 3."

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
            f"Zapisujemy sumę ${base}$ równych składników jako iloczyn: $S = {base} \\cdot {base}^{{{n}}} = {base}^1 \\cdot {base}^{{{n}}} = {base}^{{{n + 1}}}$.",
            f"Zatem odpowiedź to **{ans_ab}{c_num}**.",
        ],
    }


@register_template(
    template_id="potegi_wspolna_podstawa_2pkt",
    topic_id="potegi_notacja",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2021 zad. 16",
)
def gen_potegi_oblicz_2pkt(rng):
    base = rng.choice([2, 3])
    b2 = base ** 2
    b3 = base ** 3
    # (b2^a * b3^b) / base^c = base^(2a + 3b - c)
    a = rng.randint(3, 5)
    b = rng.randint(2, 4)
    res_exp = rng.choice([2, 3, 4])
    c = 2 * a + 3 * b - res_exp
    val = base ** res_exp

    expr = frac_tex(f"{b2}^{{{a}}} \\cdot {b3}^{{{b}}}", f"{base}^{{{c}}}")
    stem = f"Dane jest wyrażenie arytmetyczne:\n{expr}."
    command = "Oblicz wartość tego wyrażenia i zapisz wynik w postaci liczby całkowitej. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "correct_answer": str(val),
        "solution_steps": [
            f"Zamieniamy wszystkie potęgi na potęgi o podstawie ${base}$: "
            f"${b2}^{{{a}}} = ({base}^2)^{{{a}}} = {base}^{{{2 * a}}}$ oraz ${b3}^{{{b}}} = ({base}^3)^{{{b}}} = {base}^{{{3 * b}}}$.",
            f"Licznik ułamka jest równy: ${base}^{{{2 * a}}} \\cdot {base}^{{{3 * b}}} = {base}^{{{2 * a + 3 * b}}}$.",
            f"Wykonujemy dzielenie potęg: ${base}^{{{2 * a + 3 * b}}} : {base}^{{{c}}} = {base}^{{{res_exp}}} = {val}$.",
            f"**Odpowiedź:** Wartość wyrażenia jest równa ${val}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – zapisanie liczb {b2}^{a} oraz {b3}^{b} jako potęg o podstawie {base}.",
            f"2 pkt – poprawne zastosowanie praw działań na potęgach i obliczenie wartości liczbowej ({val}).",
        ],
        "grid_height_mm": 48.0,
    }


@register_template(
    template_id="potegi_notacja_masa_ziarna_3pkt",
    topic_id="potegi_notacja",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Wzorzec: Informator CKE 2025 (notacja wykładnicza)",
)
def gen_notacja_ziarna_3pkt(rng):
    # Masa jednego ziarenka np. 2,5 * 10^-5 kg; worek ma masę M kg, ile ziarenek mieści się w N workach?
    grain_m, bag_kg, n_bags = rng.choice([
        (2.5, 15, 4),   # 60 / 2.5 = 24 -> 2,4 * 10^6
        (4.0, 20, 6),   # 120 / 4 = 30 -> 3 * 10^6
        (5.0, 25, 3),   # 75 / 5 = 15 -> 1,5 * 10^6
        (2.0, 12, 5),   # 60 / 2 = 30 -> 3 * 10^6
    ])
    exp_neg = rng.choice([5, 6])
    total_kg = bag_kg * n_bags
    # total_kg / (grain_m * 10^-exp_neg) = (total_kg / grain_m) * 10^exp_neg
    q = total_kg / grain_m  # np. 24, 30, 15
    mantissa = q / 10.0     # np. 2.4, 3.0, 1.5
    final_exp = exp_neg + 1

    stem = (
        f"Przyjmuje się, że średnia masa jednego ziarenka pewnego gatunku zboża jest równa "
        f"${pl_num(grain_m)} \\cdot 10^{{-{exp_neg}}}$ kg. Gospodarz przygotował do siewu ${n_bags}$ worki tego zboża, "
        f"a w każdym worku znajduje się dokładnie ${bag_kg}$ kg ziaren."
    )
    command = (
        "Oblicz, ile ziarenek zboża znajduje się łącznie we wszystkich przygotowanych workach. "
        "Wynik zapisz w notacji wykładniczej (tj. w postaci $a \\cdot 10^k$, gdzie $1 \\le a < 10$ oraz $k$ jest liczbą całkowitą). "
        "Zapisz obliczenia."
    )

    ans_str = f"{pl_num(mantissa)} · 10^{final_exp}"
    den_grain = rf"{pl_num(grain_m)} \cdot 10^{{-{exp_neg}}}"
    return {
        "stem": stem,
        "command": command,
        "correct_answer": ans_str,
        "solution_steps": [
            f"Obliczamy łączną masę zboża we wszystkich workach: ${n_bags} \\cdot {bag_kg}\\text{{ kg}} = {total_kg}\\text{{ kg}}$.",
            f"Dzielimy łączną masę przez masę jednego ziarenka: "
            f"{frac_tex(str(total_kg), den_grain)} $= {pl_num(q)} \\cdot 10^{{{exp_neg}}}$.",
            f"Zapisujemy wynik w notacji wykładniczej ($1 \\le a < 10$): "
            f"${pl_num(q)} \\cdot 10^{{{exp_neg}}} = {pl_num(mantissa)} \\cdot 10^1 \\cdot 10^{{{exp_neg}}} = {pl_num(mantissa)} \\cdot 10^{{{final_exp}}}$.",
            f"**Odpowiedź:** We wszystkich workach znajduje się ${pl_num(mantissa)} \\cdot 10^{{{final_exp}}}$ ziarenek.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie łącznej masy zboża ({total_kg} kg) i zapisanie ilorazu masy całkowitej przez masę jednego ziarenka.",
            f"2 pkt – poprawne wykonanie dzielenia ({pl_num(q)} · 10^{exp_neg}).",
            f"3 pkt – przekształcenie wyniku do poprawnej postaci notacji wykładniczej: {pl_num(mantissa)} · 10^{final_exp}.",
        ],
        "grid_height_mm": 60.0,
    }
