"""Rozszerzony pakiet 24 wzorców zadań bezpośrednio z archiwum CKE (2019–2026).

Dodaje po 2 nowe archetypy zadań CKE do każdego z 12 działów E8 (łącznie 84 szablony w bazie):
cyfry rzymskie, NWD/NWW, skala mapy, sprzedaż w opakowaniach, potęgi dużych liczb,
porównywanie potęg z 10^k, rozdzielność pierwiastków, sześciany z klocków, przekształcanie
wzorów, wzór na sumę S = 1/2 n(n+1), puszki karmy, origami w 4 kolorach, wykres drogi s(t),
uzasadnienie czasu przejazdu > 1 h, przesunięcie punktu na kratce, czworokąt na układzie,
trójkąt równoboczny (P/F), romb z przekątnymi, słupek ze sześcianów, wieże ze sześcianów
i ostrosłupa, diagram kołowy z procentami, tabela Dnia Sportu (CKE 2026), losowanie bez
zwracania oraz kule 1..2n+1 z parzystością sumy.
"""

from __future__ import annotations

import math
from fractions import Fraction

from ..math_text import frac_tex, pl_num, shuffle_abcd
from ..models import DiagramSpec
from .base import register_template


def _to_roman(n: int) -> str:
    pairs = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    out = []
    val = n
    for arabic, rom in pairs:
        while val >= arabic:
            out.append(rom)
            val -= arabic
    return "".join(out)


# ===========================================================================
# 1. LICZBY I DZIAŁANIA (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="liczby_rzymskie_os_abcd",
    topic_id="liczby_dzialania",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: Informator CKE 2025 zad. 2",
)
def gen_liczby_rzymskie_os(rng):
    target = rng.choice([200, 300, 400, 500, 1500, 2000])
    # Cztery różne odległości od targetu, najmniejsza jest jednoznaczna
    d_best = rng.choice([8, 9, 10, 11, 12])
    d2, d3, d4 = d_best + rng.choice([8, 12]), d_best + rng.choice([22, 28]), d_best + rng.choice([38, 45])
    signs = [rng.choice([-1, 1]) for _ in range(4)]
    vals = [target + s * d for s, d in zip(signs, [d_best, d2, d3, d4])]
    romans = [_to_roman(v) for v in vals]

    shown = list(romans)
    rng.shuffle(shown)
    choices, ans = shuffle_abcd(rng, romans[0], romans[1:])

    dec_parts = ", ".join(f"{r} $= {pl_num(v)}$ (odległość od ${pl_num(target)}$: ${abs(v - target)}$)" for r, v in zip(romans, vals))
    return {
        "stem": (
            f"Marta zapisała w systemie rzymskim cztery liczby: "
            f"**{shown[0]}**, **{shown[1]}**, **{shown[2]}** oraz **{shown[3]}**."
        ),
        "command": f"Która z tych liczb leży na osi liczbowej najbliżej liczby ${pl_num(target)}$? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Zamieniamy zapis rzymski na system dziesiętny i obliczamy odległość od ${pl_num(target)}$: {dec_parts}.",
            f"Najmniejszą odległość (${d_best}$) ma liczba **{romans[0]}** ($= {pl_num(vals[0])}$). Poprawna odpowiedź: **{ans}**.",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="liczby_nwd_nww_kod_abcd",
    topic_id="liczby_dzialania",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2026 zad. 2 / Maj 2023 zad. 2",
)
def gen_liczby_nwd_nww(rng):
    pairs_nwd = [(18, 27), (24, 36), (28, 42), (32, 48), (36, 54), (45, 60)]
    a1, b1 = rng.choice(pairs_nwd)
    g = math.gcd(a1, b1)

    pairs_nww = [(6, 8), (8, 12), (9, 12), (10, 15), (12, 18), (15, 20)]
    a2, b2 = rng.choice(pairs_nww)
    l = math.lcm(a2, b2)

    sep = rng.choice(["K", "T", "M"])
    correct = f"{g}{sep}{l}"
    w1 = f"{math.lcm(a1, b1)}{sep}{l}"
    w2 = f"{g}{sep}{a2 * b2}"
    w3 = f"{math.gcd(a2, b2)}{sep}{l}"
    choices, ans = shuffle_abcd(rng, correct, [w1, w2, w3])

    return {
        "stem": (
            f"Dostęp do szkolnego archiwum jest chroniony hasłem złożonym z dwóch liczb naturalnych "
            f"rozdzielonych literą **{sep}**. Pierwsza liczba hasła to największy wspólny dzielnik ($\\text{{NWD}}$) "
            f"liczb ${a1}$ i ${b1}$, a druga to najmniejsza wspólna wielokrotność ($\\text{{NWW}}$) liczb ${a2}$ i ${b2}$."
        ),
        "command": "Jakie jest hasło do archiwum? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Wyznaczamy $\\text{{NWD}}({a1}, {b1}) = {g}$.",
            f"Wyznaczamy $\\text{{NWW}}({a2}, {b2}) = {l}$ (ponieważ ${a2} \\cdot {b2} : {math.gcd(a2, b2)} = {l}$).",
            f"Hasło ma postać **{correct}** (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


# ===========================================================================
# 2. PROCENTY I PROPORCJE (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="procenty_skala_planu_abcd",
    topic_id="procenty_proporcje",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2023 zad. 10 / Czerwiec 2024 zad. 12",
)
def gen_skala_planu(rng):
    cm_plan = rng.choice([6, 8, 12, 15])
    scale = rng.choice([4000, 5000, 10000, 25000])
    real_m = (cm_plan * scale) // 100
    correct = f"${pl_num(real_m)}$ m"
    w1 = f"${pl_num(real_m * 10)}$ m"
    w2 = f"${pl_num(max(10, real_m // 10))}$ m"
    w3 = f"${pl_num((scale // 100) * 2)}$ m"
    choices, ans = shuffle_abcd(rng, correct, [w1, w2, w3])

    return {
        "stem": (
            f"Na planie miasta wykonanym w skali $1 : {pl_num(scale)}$ odległość w linii prostej "
            f"między przystankiem *Dworzec* a przystankiem *Park* jest równa ${cm_plan}$ cm."
        ),
        "command": "Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\nOdległość w linii prostej w terenie między tymi przystankami jest równa",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Skala $1 : {pl_num(scale)}$ oznacza, że $1\\text{{ cm}}$ na planie odpowiada ${pl_num(scale)}\\text{{ cm}} = {pl_num(scale // 100)}\\text{{ m}}$ w terenie.",
            f"Obliczamy odległość rzeczywistą: ${cm_plan} \\cdot {pl_num(scale // 100)}\\text{{ m}} = {pl_num(real_m)}\\text{{ m}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="procenty_truskawki_opakowania_3pkt",
    topic_id="procenty_proporcje",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2024 zad. 18",
)
def gen_truskawki_opakowania(rng):
    total_kg = rng.choice([80, 100, 120, 160])
    pct_mid = rng.choice([10, 15, 20, 25])
    # Upewnij się, że masy dzielą się na pełne opakowania 1 kg, 0.5 kg i 0.25 kg
    kg_big = total_kg // 2
    kg_mid = (total_kg * pct_mid) // 100
    kg_small = total_kg - kg_big - kg_mid

    p_big = rng.choice([16, 18, 20])
    p_mid = rng.choice([9, 10, 11])
    p_small = rng.choice([5, 6, 7])

    n_big = kg_big
    n_mid = kg_mid * 2
    n_small = kg_small * 4
    revenue = n_big * p_big + n_mid * p_mid + n_small * p_small

    return {
        "stem": (
            f"Pan Jan sprzedał w swoim sklepie ${total_kg}$ kg truskawek. Połowę masy tych truskawek sprzedał "
            f"w dużych opakowaniach, ${pct_mid}\\%$ masy truskawek – w średnich, a pozostałe truskawki – "
            f"w małych opakowaniach. W tabeli podano informacje o opakowaniach i ich cenach."
        ),
        "table_data": [
            ["Rodzaj opakowania", "Masa w opakowaniu", "Cena jednego opakowania"],
            ["duże", "$1$ kg", f"${p_big}$ zł"],
            ["średnie", "$0,5$ kg", f"${p_mid}$ zł"],
            ["małe", "$0,25$ kg", f"${p_small}$ zł"],
        ],
        "command": "Oblicz, jaką łączną kwotę otrzymał pan Jan ze sprzedaży wszystkich truskawek. Zapisz obliczenia.",
        "correct_answer": f"{pl_num(revenue)} zł",
        "solution_steps": [
            f"Obliczamy masy truskawek w poszczególnych rodzajach opakowań: duże: $\\frac{{1}}{{2}} \\cdot {total_kg} = {kg_big}\\text{{ kg}}$, "
            f"średnie: ${pct_mid}\\% \\cdot {total_kg} = {kg_mid}\\text{{ kg}}$, małe: ${total_kg} - ({kg_big} + {kg_mid}) = {kg_small}\\text{{ kg}}$.",
            f"Wyznaczamy liczby sprzedanych opakowań: dużych: ${kg_big} : 1 = {n_big}$, "
            f"średnich: ${kg_mid} : 0,5 = {n_mid}$, małych: ${kg_small} : 0,25 = {n_small}$.",
            f"Obliczamy łączny przychód: ${n_big} \\cdot {p_big} + {n_mid} \\cdot {p_mid} + {n_small} \\cdot {p_small} = "
            f"{n_big * p_big} + {n_mid * p_mid} + {n_small * p_small} = {pl_num(revenue)}\\text{{ zł}}$.",
        ],
        "scoring_scheme": [
            "1 pkt – poprawne obliczenie masy truskawek w każdym z trzech rodzajów opakowań.",
            "2 pkt – poprawne wyznaczenie liczby opakowań każdego rodzaju.",
            f"3 pkt – pełne rozwiązanie i poprawna kwota końcowa: {pl_num(revenue)} zł.",
        ],
        "grid_height_mm": 60.0,
    }


# ===========================================================================
# 3. POTĘGI I NOTACJA WYKŁADNICZA (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="potegi_duza_liczba_z_zerami_abcd",
    topic_id="potegi_notacja",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2021 zad. 4",
)
def gen_potegi_duza_liczba(rng):
    digit = rng.choice([3, 4, 6, 7, 8])
    zeros = rng.choice([5, 6, 7])
    exp = rng.choice([3, 4])
    big_num_str = f"{digit}" + "0" * zeros
    big_fmt = pl_num(int(big_num_str))

    correct = f"${digit}^{{{exp}}} \\cdot 10^{{{zeros * exp}}}$"
    w1 = f"${digit} \\cdot 10^{{{zeros * exp}}}$"
    w2 = f"${digit}^{{{exp}}} \\cdot 10^{{{zeros + exp}}}$"
    w3 = f"${digit} \\cdot 10^{{{zeros + exp}}}$"
    choices, ans = shuffle_abcd(rng, correct, [w1, w2, w3])

    return {
        "stem": (
            "Z reguł działań na potęgach wynika, że:\n"
            "$(200\\,000)^3 = (2 \\cdot 10^5)^3 = 2^3 \\cdot 10^{15}$."
        ),
        "command": f"Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\nZ tych samych reguł wynika, że liczba $({big_fmt})^{exp}$ jest równa",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Zapisujemy liczbę w nawiasie jako iloczyn: ${big_fmt} = {digit} \\cdot 10^{{{zeros}}}$.",
            f"Podnosimy iloczyn do potęgi ${exp}$: $({digit} \\cdot 10^{{{zeros}}})^{{{exp}}} = {digit}^{{{exp}}} \\cdot (10^{{{zeros}}})^{{{exp}}} = {digit}^{{{exp}}} \\cdot 10^{{{zeros * exp}}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="potegi_porownanie_10_do_k_abcd",
    topic_id="potegi_notacja",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2022 zad. 5",
)
def gen_potegi_porownanie_100(rng):
    target_exp = rng.choice([60, 80, 100])
    a1 = target_exp // 2 - 10
    a2 = target_exp - a1  # a1 + a2 - 1 = target_exp - 1 < target_exp
    b_in = 3
    b_out = 10
    b_rest = target_exp + 5 - b_in * b_out  # > target_exp
    c1 = target_exp // 2
    c2 = target_exp - c1 + 20

    fx = rf"\frac{{10^{{{a1}}} \cdot 10^{{{a2}}}}}{{10}}"
    fy = rf"(10^{{{b_in}}})^{{{b_out}}} \cdot 10^{{{b_rest}}}"
    fz = rf"10^{{{c1}}} \cdot \frac{{10^{{{c2}}}}}{{10^{{15}}}}"

    choices, ans = shuffle_abcd(
        rng,
        "Tylko $x$.",
        ["Tylko $y$.", "Tylko $z$.", "Każda z liczb $x, y, z$."],
    )
    return {
        "stem": (
            f"Dane są trzy liczby:\n"
            f"$x = {fx}$,   $y = {fy}$,   $z = {fz}$."
        ),
        "command": f"Która z tych liczb jest mniejsza od liczby $10^{{{target_exp}}}$? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Upraszczamy każdą liczbę: $x = 10^{{{a1} + {a2} - 1}} = 10^{{{target_exp - 1}}}$, "
            f"$y = 10^{{{b_in * b_out} + {b_rest}}} = 10^{{{target_exp + 5}}}$, "
            f"$z = 10^{{{c1} + {c2} - 15}} = 10^{{{target_exp + 5}}}$.",
            f"Mniejsza od $10^{{{target_exp}}}$ jest wyłącznie liczba $x = 10^{{{target_exp - 1}}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


# ===========================================================================
# 4. PIERWIASTKI (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="pierwiastki_nawias_rozdzielnosc_abcd",
    topic_id="pierwiastki",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2020 zad. 6",
)
def gen_pierwiastki_nawias(rng):
    base_p = rng.choice([2, 3, 5])
    k1, k2 = rng.choice([(3, 2), (4, 2), (5, 3), (4, 1)])
    n1 = base_p * (k1 ** 2)
    n2 = base_p * (k2 ** 2)
    val = base_p * (k1 - k2)

    s_out = rf"\sqrt{{{base_p}}}"
    s_in = rf"\sqrt{{{n1}}} - \sqrt{{{n2}}}"
    w1 = rf"$\sqrt{{{val}}}$"
    w2 = rf"$\sqrt{{{base_p * (n1 - n2)}}}$"
    w3 = f"${k1 - k2}$"
    choices, ans = shuffle_abcd(rng, f"${val}$", [w1, w2, w3])

    return {
        "stem": f"Dane jest wyrażenie arytmetyczne ${s_out}({s_in})$.",
        "command": "Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\nWartość tego wyrażenia jest równa",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Mnożymy jednomian przez każdy wyraz w nawiasie: ${s_out} \\cdot \\sqrt{{{n1}}} - {s_out} \\cdot \\sqrt{{{n2}}} = \\sqrt{{{base_p * n1}}} - \\sqrt{{{base_p * n2}}}$.",
            f"Obliczamy pierwiastki: ${base_p * k1} - {base_p * k2} = {val}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="pierwiastki_szescian_z_klockow_abcd",
    topic_id="pierwiastki",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Kwiecień 2019 zad. 14",
)
def gen_klocki_szescian(rng):
    k = rng.choice([4, 5, 6])
    cube = k ** 3
    next_cube = (k + 1) ** 3
    rem = rng.randint(18, next_cube - cube - 12)
    total = cube + rem

    w1 = total - (k - 1) ** 3
    w2 = next_cube - total
    w3 = cube
    choices, ans = shuffle_abcd(rng, f"${rem}$", [f"${w1}$", f"${w2}$", f"${w3}$"])

    return {
        "stem": (
            f"W pudełku było ${total}$ jednakowych sześciennych klocków. Zbudowano z nich możliwie największy "
            f"pełny sześcian, a pozostałe klocki odłożono z powrotem do pudełka."
        ),
        "command": "Ile klocków odłożono do pudełka? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Kolejne sześciany liczb naturalnych to: $4^3 = 64$, $5^3 = 125$, $6^3 = 216$, $7^3 = 343$.",
            f"Największy sześcian mniejszy lub równy ${total}$ to ${k}^3 = {cube}$.",
            f"Liczba odłożonych klocków wynosi: ${total} - {cube} = {rem}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


# ===========================================================================
# 5. WYRAŻENIA ALGEBRAICZNE (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="wyrazenia_przeksztalcanie_wzoru_abcd",
    topic_id="wyrazenia_algebraiczne",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2020 zad. 10 / Maj 2025 zad. 5",
)
def gen_przeksztalcanie_wzoru(rng):
    variant = rng.choice(["trapez", "energia"])
    if variant == "trapez":
        f_main = r"P = \frac{(x + y) \cdot h}{2}"
        correct = r"$x = \frac{2P}{h} - y$"
        wrongs = [r"$x = \frac{P}{2h} - y$", r"$x = 2P - hy$", r"$x = \frac{2P - y}{h}$"]
        steps = [
            r"Mnożymy obie strony wzoru $P = \frac{(x+y)h}{2}$ przez $2$: $2P = (x + y) \cdot h$.",
            r"Dzielimy obie strony przez $h$: $\frac{2P}{h} = x + y$, stąd $x = \frac{2P}{h} - y$.",
        ]
        var_ask = "x"
        desc = "pole trapezu o podstawach $x, y$ oraz wysokości $h$"
    else:
        k = rng.choice([2, 3, 5])
        f_main = rf"E = {k}m \cdot h + w"
        correct = rf"$m = \frac{{E - w}}{{{k}h}}$"
        wrongs = [rf"$m = \frac{{E}}{{{k}h}} - w$", rf"$m = \frac{{E + w}}{{{k}h}}$", rf"$m = {k}h(E - w)$"]
        steps = [
            rf"Odejmujemy $w$ od obu stron równania $E = {k}mh + w$: $E - w = {k}mh$.",
            rf"Dzielimy obie strony przez ${k}h$: $m = \frac{{E - w}}{{{k}h}}$.",
        ]
        var_ask = "m"
        desc = "zależność między wielkościami dodatnimi"

    choices, ans = shuffle_abcd(rng, correct, wrongs)
    return {
        "stem": f"Dany jest wzór opisujący {desc}:\n${f_main}$.",
        "command": f"Którym równaniem opisano wielkość ${var_ask}$ wyznaczoną poprawnie z tego wzoru? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": steps + [f"Poprawna odpowiedź: **{ans}**."],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="wyrazenia_suma_kolejnych_ab_cd",
    topic_id="wyrazenia_algebraiczne",
    subtype="ab_cd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2026 zad. 8",
)
def gen_wzor_suma_kolejnych(rng):
    n_val = rng.choice([40, 50, 60, 80, 100])
    s_val = n_val * (n_val + 1) // 2
    s_wrong = (n_val * n_val) // 2 + 1

    if rng.random() < 0.5:
        opts1 = {"A": f"${pl_num(s_wrong)}$", "B": f"${pl_num(s_val)}$"}
        a1 = "B"
    else:
        opts1 = {"A": f"${pl_num(s_val)}$", "B": f"${pl_num(s_wrong)}$"}
        a1 = "A"

    f_good = r"$S = \frac{1}{2}n^2 + \frac{1}{2}n$"
    f_bad = r"$S = \frac{1}{2}n^2 + 1$"
    if rng.random() < 0.5:
        opts2 = {"C": f_bad, "D": f_good}
        a2 = "D"
    else:
        opts2 = {"C": f_good, "D": f_bad}
        a2 = "C"

    f_stem = r"S = \frac{1}{2}n(n + 1)"
    return {
        "stem": (
            f"Sumę $S = 1 + 2 + 3 + \\dots + n$ kolejnych liczb naturalnych od $1$ do $n$ można obliczyć ze wzoru:\n"
            f"${f_stem}$."
        ),
        "command": "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D.",
        "ab_cd_parts": [
            {
                "prefix": f"Suma kolejnych liczb naturalnych od $1$ do ${n_val}$ jest równa",
                "suffix": ".",
                "options": opts1,
            },
            {
                "prefix": "Wzór na sumę $S$ po poprawnym wymnożeniu nawiasu ma postać",
                "suffix": ".",
                "options": opts2,
            },
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Dla $n = {n_val}$ obliczamy $S = \\frac{{1}}{{2}} \\cdot {n_val} \\cdot {n_val + 1} = {n_val // 2} \\cdot {n_val + 1} = {pl_num(s_val)}$ (**{a1}**).",
            f"Po wymnożeniu jednomianu przez nawias otrzymujemy $\\frac{{1}}{{2}}n(n + 1) = \\frac{{1}}{{2}}n^2 + \\frac{{1}}{{2}}n$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna para odpowiedzi.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


# ===========================================================================
# 6. RÓWNANIA I ZADANIA TEKSTOWE (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="rownania_puszki_zabraklo_zostalo_2pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2021 zad. 18",
)
def gen_puszki_zabraklo(rng):
    n_more, n_less = rng.choice([(10, 6), (12, 7), (9, 5), (8, 5)])
    price_gr = rng.choice([360, 420, 450, 550, 640, 750])
    have_gr = n_less * price_gr + rng.choice([240, 340, 460])
    lack_gr = n_more * price_gr - have_gr
    rem_gr = have_gr - n_less * price_gr

    price_zl = price_gr / 100
    lack_zl = lack_gr / 100
    rem_zl = rem_gr / 100

    return {
        "stem": (
            f"Ania chciała kupić ${n_more}$ jednakowych puszek karmy dla psa, ale zabrakło jej ${pl_num(lack_zl)}$ zł. "
            f"Kupiła więc ${n_less}$ takich samych puszek karmy i zostało jej ${pl_num(rem_zl)}$ zł."
        ),
        "command": "Oblicz, ile kosztuje jedna puszka tej karmy. Zapisz obliczenia.",
        "correct_answer": f"{pl_num(price_zl)} zł",
        "solution_steps": [
            f"Oznaczmy przez $x$ cenę jednej puszki karmy (w zł). Kwota, którą miała Ania, to z jednej strony ${n_more}x - {pl_num(lack_zl)}$, a z drugiej ${n_less}x + {pl_num(rem_zl)}$.",
            f"Układamy równanie: ${n_more}x - {pl_num(lack_zl)} = {n_less}x + {pl_num(rem_zl)}$, skąd ${n_more - n_less}x = {pl_num(lack_zl + rem_zl)}$, czyli $x = {pl_num(price_zl)}$ zł.",
        ],
        "scoring_scheme": [
            "1 pkt – zapisanie poprawnego równania lub zauważenie, że różnica liczby puszek odpowiada sumie brakującej i pozostałej kwoty.",
            f"2 pkt – pełne rozwiązanie i podanie ceny puszki: {pl_num(price_zl)} zł.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="rownania_origami_cztery_kolory_2pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2026 zad. 15",
)
def gen_origami_kolory(rng):
    x_red = rng.choice([24, 28, 32, 36, 40])  # parzyste, żeby 1,5x było całkowite
    blue = int(1.5 * x_red)
    offset = rng.choice([8, 10, 12, 14])
    green = x_red - offset
    white = rng.choice([25, 31, 37, 43])
    total = white + blue + x_red + green

    return {
        "stem": (
            f"Do wykonania modeli origami Ela przygotowała łącznie ${total}$ kartek papieru w czterech kolorach: "
            f"białym, niebieskim, czerwonym oraz zielonym. Kartek białych było ${white}$. "
            f"Kartek niebieskich było $1,5$ raza więcej niż czerwonych, a kartek zielonych – o ${offset}$ mniej niż czerwonych."
        ),
        "command": "Oblicz, ile kartek w kolorze niebieskim przygotowała Ela. Zapisz obliczenia.",
        "correct_answer": f"{blue}",
        "solution_steps": [
            f"Oznaczmy przez $x$ liczbę kartek czerwonych. Wówczas niebieskich było $1,5x$, zielonych $x - {offset}$, a białych ${white}$.",
            f"Zapisujemy równanie: ${white} + 1,5x + x + (x - {offset}) = {total} \\Rightarrow 3,5x + {white - offset} = {total} \\Rightarrow 3,5x = {total - white + offset} \\Rightarrow x = {x_red}$.",
            f"Liczba kartek niebieskich wynosi: $1,5 \\cdot {x_red} = {blue}$.",
        ],
        "scoring_scheme": [
            "1 pkt – poprawne ułożenie równania opisującego łączną liczbę kartek.",
            f"2 pkt – wyznaczenie liczby kartek czerwonych ({x_red}) oraz podanie liczby kartek niebieskich ({blue}).",
        ],
        "grid_height_mm": 54.0,
    }


# ===========================================================================
# 7. PRĘDKOŚĆ, DROGA, CZAS (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="predkosc_wykres_drogi_pf",
    topic_id="predkosc_droga_czas",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: Informator CKE 2025 zad. 15",
    has_diagram=True,
)
def gen_wykres_drogi(rng):
    v1 = rng.choice([12, 15, 18, 20])
    t1 = 2
    d1 = v1 * t1
    t_stop = 1
    v2 = rng.choice([10, 15, 20])
    t2 = 2
    d2 = d1 + v2 * t2

    s1_true = rng.choice([True, False])
    v_claim = v1 if s1_true else (d1 // (t1 + 1))

    s2_true = rng.choice([True, False])
    stop_min = 60 if s2_true else 30

    p1_ans = "P" if s1_true else "F"
    p2_ans = "P" if s2_true else "F"

    return {
        "stem": (
            "Rowerzysta wyruszył z domu na wycieczkę. Na wykresie przedstawiono zależność jego odległości "
            "od domu od czasu trwania wycieczki."
        ),
        "diagram": DiagramSpec(
            kind="travel_graph",
            params={
                "times": [0, t1, t1 + t_stop, t1 + t_stop + t2],
                "dists": [0, d1, d1, d2],
                "xlabel": "Czas [h]",
                "ylabel": "Odległość od domu [km]",
                "x_step": 1,
                "y_step": 10,
            },
            width_mm=88.0,
        ),
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Przez pierwsze dwie godziny rowerzysta jechał ze średnią prędkością ${v_claim}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$.", p1_ans),
            (f"Postój rowerzysty podczas tej wycieczki trwał ${stop_min}$ minut.", p2_ans),
        ],
        "correct_answer": f"{p1_ans}{p2_ans}",
        "solution_steps": [
            f"Z wykresu odczytujemy, że w ciągu pierwszych $2\\text{{ h}}$ rowerzysta pokonał ${d1}\\text{{ km}}$, czyli jechał z prędkością ${d1} : 2 = {v1}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$ (zdanie 1.: **{p1_ans}**).",
            f"Odcinek poziomy na wykresie między $2\\text{{ h}}$ a $3\\text{{ h}}$ oznacza postój trwający $1\\text{{ h}} = 60\\text{{ min}}$ (zdanie 2.: **{p2_ans}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="predkosc_uzasadnij_dluzej_niz_godzina_3pkt",
    topic_id="predkosc_droga_czas",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2026 zad. 16",
)
def gen_uzasadnij_czas_przejazdu(rng):
    # v w km/h podzielne przez 3, czas 1. odcinka = 40 min = 2/3 h
    v = rng.choice([60, 66, 72, 78, 84])
    d1 = (v * 2) // 3
    extra_km = rng.choice([3, 6, 9, 12])
    d2 = v + extra_km  # d2 > v, więc przy prędkości v czas > 1 h!
    d_total = d1 + d2

    return {
        "stem": (
            f"Z Polanki do Dębiny prowadzi jedna droga przez Jodłowo i ma łączną długość ${d_total}$ km. "
            f"Droga z Polanki do Jodłowa ma długość ${d1}$ km i samochód przejechał ją w czasie $40$ minut. "
            f"Drogę z Jodłowa do Dębiny ten samochód pokonał z taką samą średnią prędkością, jak drogę z Polanki do Jodłowa."
        ),
        "command": "Uzasadnij, że przejazd tego samochodu z Jodłowa do Dębiny trwał dłużej niż godzinę. Zapisz obliczenia.",
        "correct_answer": f"v = {v} km/h, s2 = {d2} km > {v} km (czas > 1 h)",
        "solution_steps": [
            f"Zamieniamy czas pierwszego etapu na godziny: $40\\text{{ min}} = \\frac{{40}}{{60}}\\text{{ h}} = \\frac{{2}}{{3}}\\text{{ h}}$.",
            f"Obliczamy prędkość samochodu: $v = \\frac{{{d1}}}{{\\frac{{2}}{{3}}}} = {d1} \\cdot \\frac{{3}}{{2}} = {v}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$.",
            f"Długość drugiego odcinka (z Jodłowa do Dębiny) wynosi: ${d_total} - {d1} = {d2}\\text{{ km}}$.",
            f"W ciągu $1$ godziny samochód jadący z prędkością ${v}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$ przejeżdża ${v}\\text{{ km}}$. Ponieważ ${d2}\\text{{ km}} > {v}\\text{{ km}}$, przejazd trwał dłużej niż godzinę, co należało uzasadnić.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne obliczenie długości drugiego odcinka ({d2} km) lub zamiana 40 minut na 2/3 h.",
            f"2 pkt – poprawne obliczenie prędkości samochodu ({v} km/h).",
            "3 pkt – pełne obliczenia wraz z poprawnym wnioskiem porównującym drogę lub czas z 1 godziną.",
        ],
        "grid_height_mm": 58.0,
    }


# ===========================================================================
# 8. UKŁAD WSPÓŁRZĘDNYCH (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="wspolrzedne_przesuniecie_punktu_abcd",
    topic_id="uklad_wspolrzednych",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2024 zad. 12",
    has_diagram=True,
)
def gen_przesuniecie_punktu(rng):
    x1, y1 = rng.choice([(-3, -2), (-2, -3), (-3, -1), (-1, -2)])
    dx = rng.choice([4, 5])
    dy = rng.choice([3, 4])
    target = (x1 + dx, y1 + dy)
    w_pts = [
        (x1 + dy, y1 + dx),
        (x1 + dx, y1 - dy),
        (x1 - 2, y1 + dy + 1),
    ]
    labels = ["P_2", "P_3", "P_4", "P_5"]
    coords_4 = [target] + w_pts
    rng.shuffle(coords_4)
    correct_idx = coords_4.index(target)
    correct_lbl = f"${labels[correct_idx]}$"

    pts_diag = [{"x": x1, "y": y1, "label": "P1"}]
    for idx, (px, py) in enumerate(coords_4):
        pts_diag.append({"x": px, "y": py, "label": f"P{idx + 2}"})

    choices = {L: f"${labels[i]}$" for i, L in enumerate(["A", "B", "C", "D"])}
    ans = ["A", "B", "C", "D"][correct_idx]

    return {
        "stem": (
            f"W układzie współrzędnych $(x, y)$ zaznaczono pięć punktów: $P_1, P_2, P_3, P_4$ oraz $P_5$ "
            f"(zobacz rysunek). Punkt $P_1$ ma współrzędne $({pl_num(x1)}, {pl_num(y1)})$."
        ),
        "diagram": DiagramSpec(kind="coord_plane", params={"limit": 6, "points": pts_diag}, width_mm=72.0),
        "command": (
            f"Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\n"
            f"Jeżeli współrzędną $x$ punktu $P_1$ zwiększymy o ${dx}$, a współrzędną $y$ tego punktu zwiększymy o ${dy}$, "
            f"to otrzymamy współrzędne punktu"
        ),
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Obliczamy nowe współrzędne: $x = {pl_num(x1)} + {dx} = {pl_num(target[0])}$ oraz $y = {pl_num(y1)} + {dy} = {pl_num(target[1])}$.",
            f"Punkt o współrzędnych $({pl_num(target[0])}, {pl_num(target[1])})$ to na rysunku punkt {correct_lbl} (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="wspolrzedne_pole_trapezu_2pkt",
    topic_id="uklad_wspolrzednych",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2025 zad. 14",
    has_diagram=True,
)
def gen_pole_trapezu_uklad(rng):
    y_bot = rng.choice([-3, -2])
    h = rng.choice([4, 6])
    y_top = y_bot + h
    a = rng.choice([6, 8])
    b = rng.choice([2, 4])
    x_a = -a // 2
    x_b = x_a + a
    x_d = -b // 2
    x_c = x_d + b
    area = (a + b) * h // 2

    poly = [[x_a, y_bot], [x_b, y_bot], [x_c, y_top], [x_d, y_top]]
    pts = [
        {"x": x_a, "y": y_bot, "label": "A", "dx": -0.4, "dy": -0.4},
        {"x": x_b, "y": y_bot, "label": "B", "dx": 0.4, "dy": -0.4},
        {"x": x_c, "y": y_top, "label": "C", "dx": 0.4, "dy": 0.4},
        {"x": x_d, "y": y_top, "label": "D", "dx": -0.4, "dy": 0.4},
    ]

    return {
        "stem": (
            f"W układzie współrzędnych $(x, y)$ narysowano trapez $ABCD$ o wierzchołkach: "
            f"$A = ({pl_num(x_a)}, {pl_num(y_bot)})$, $B = ({pl_num(x_b)}, {pl_num(y_bot)})$, "
            f"$C = ({pl_num(x_c)}, {pl_num(y_top)})$ oraz $D = ({pl_num(x_d)}, {pl_num(y_top)})$."
        ),
        "diagram": DiagramSpec(kind="coord_plane", params={"limit": 6, "polygon": poly, "points": pts}, width_mm=74.0),
        "command": "Oblicz pole trapezu $ABCD$. Zapisz obliczenia.",
        "correct_answer": f"{area}",
        "solution_steps": [
            f"Podstawy trapezu są równoległe do osi $Ox$: $|AB| = {x_b} - ({pl_num(x_a)}) = {a}$ oraz $|CD| = {x_c} - ({pl_num(x_d)}) = {b}$.",
            f"Wysokość trapezu jest równa różnicy rzędnych podstaw: $h = {pl_num(y_top)} - ({pl_num(y_bot)}) = {h}$.",
            f"Pole trapezu wynosi: $P = \\frac{{({a} + {b}) \\cdot {h}}}{{2}} = {area}$.",
        ],
        "scoring_scheme": [
            "1 pkt – poprawne wyznaczenie długości obu podstaw i wysokości trapezu z układu współrzędnych.",
            f"2 pkt – poprawne obliczenie pola trapezu: {area}.",
        ],
        "grid_height_mm": 50.0,
    }


# ===========================================================================
# 9. GEOMETRIA PŁASKA (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="planimetria_trojkat_rownoboczny_pf",
    topic_id="geometria_plaska",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2026 zad. 10",
)
def gen_trojkat_rownoboczny_pf(rng):
    a = rng.choice([2, 4, 6, 8, 10])
    h_coeff = a // 2
    area_coeff = (a * a) // 4

    s1_true = rng.choice([True, False])
    h_str = rf"\sqrt{{3}}" if (h_coeff == 1 and s1_true) else (
        rf"{h_coeff}\sqrt{{3}}" if s1_true else rf"{a}\sqrt{{3}}"
    )

    s2_true = rng.choice([True, False])
    p_str = rf"\sqrt{{3}}" if (area_coeff == 1 and s2_true) else (
        rf"{area_coeff}\sqrt{{3}}" if s2_true else rf"{(a * a) // 2}\sqrt{{3}}"
    )

    a1 = "P" if s1_true else "F"
    a2 = "P" if s2_true else "F"
    h_good = rf"\sqrt{{3}}" if h_coeff == 1 else rf"{h_coeff}\sqrt{{3}}"
    p_good = rf"\sqrt{{3}}" if area_coeff == 1 else rf"{area_coeff}\sqrt{{3}}"

    return {
        "stem": f"Dany jest trójkąt równoboczny o boku długości ${a}$ cm.",
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Wysokość tego trójkąta jest równa ${h_str}$ cm.", a1),
            (f"Pole tego trójkąta jest równe ${p_str}\\text{{ cm}}^2$.", a2),
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Wysokość trójkąta równobocznego o boku $a = {a}\\text{{ cm}}$ wynosi $h = \\frac{{a\\sqrt{{3}}}}{{2}} = {h_good}\\text{{ cm}}$ (zdanie 1.: **{a1}**).",
            f"Pole tego trójkąta wynosi $P = \\frac{{a^2\\sqrt{{3}}}}{{4}} = \\frac{{{a * a}\\sqrt{{3}}}}{{4}} = {p_good}\\text{{ cm}}^2$ (zdanie 2.: **{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="planimetria_romb_przekatne_3pkt",
    topic_id="geometria_plaska",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2022 zad. 18",
    has_diagram=True,
)
def gen_romb_przekatne(rng):
    # Trójka pitagorejska dla połówek przekątnych (e/2, f/2, a)
    half_e, half_f, side = rng.choice([(12, 5, 13), (8, 6, 10), (15, 8, 17), (12, 9, 15), (16, 12, 20)])
    obw = 4 * side
    diag_ac = 2 * half_e
    diag_bd = 2 * half_f
    area = (diag_ac * diag_bd) // 2
    ask_area = rng.choice([True, False])

    cmd = (
        "Oblicz pole rombu $ABCD$. Zapisz obliczenia."
        if ask_area
        else "Oblicz długość drugiej przekątnej $BD$ rombu $ABCD$. Zapisz obliczenia."
    )
    ans_str = f"{area} cm^2" if ask_area else f"{diag_bd} cm"

    steps = [
        f"Bok rombu ma długość $a = {obw} : 4 = {side}\\text{{ cm}}$. Przekątne rombu przecinają się w połowie pod kątem prostym, więc $|AS| = {diag_ac} : 2 = {half_e}\\text{{ cm}}$.",
        f"Z twierdzenia Pitagorasa w trójkącie prostokątnym $ABS$: $|BS|^2 + {half_e}^2 = {side}^2 \\Rightarrow |BS|^2 = {side**2} - {half_e**2} = {half_f**2}$, stąd $|BS| = {half_f}\\text{{ cm}}$.",
        f"Druga przekątna ma długość $|BD| = 2 \\cdot {half_f} = {diag_bd}\\text{{ cm}}$"
        + (f", zatem pole rombu wynosi $P = \\frac{{{diag_ac} \\cdot {diag_bd}}}{{2}} = {area}\\text{{ cm}}^2$." if ask_area else "."),
    ]

    return {
        "stem": (
            f"Dany jest romb $ABCD$ o obwodzie równym ${obw}$ cm. Przekątna $AC$ tego rombu ma długość ${diag_ac}$ cm "
            f"(zobacz rysunek)."
        ),
        "diagram": DiagramSpec(
            kind="rhombus_diagonals",
            params={"side_label": f"{side} cm" if False else "", "ac_label": ""},
            width_mm=72.0,
        ),
        "command": cmd,
        "correct_answer": ans_str,
        "solution_steps": steps,
        "scoring_scheme": [
            f"1 pkt – obliczenie długości boku rombu ({side} cm) oraz połowy przekątnej AC ({half_e} cm).",
            f"2 pkt – zastosowanie twierdzenia Pitagorasa i wyznaczenie połowy przekątnej BD ({half_f} cm).",
            f"3 pkt – pełne rozwiązanie i podanie poprawnego wyniku: {ans_str}.",
        ],
        "grid_height_mm": 58.0,
    }


# ===========================================================================
# 10. GEOMETRIA PRZESTRZENNA – BRYŁY (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="stereometria_slupek_szescianow_abcd",
    topic_id="geometria_przestrzenna",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2026 zad. 14",
)
def gen_slupek_szescianow(rng):
    k = rng.choice([3, 4, 5])
    a = rng.choice([3, 4, 5, 6])
    faces_exposed = 4 * k + 2
    area = faces_exposed * (a * a)

    w1 = 6 * k * (a * a)  # błąd: suma pól wszystkich sześcianów bez odjęcia sklejonych ścian!
    w2 = (4 * k) * (a * a)  # błąd: pominięcie dwóch podstaw
    w3 = k * (a ** 3)  # błąd: objętość zamiast pola
    choices, ans = shuffle_abcd(
        rng,
        f"${pl_num(area)}\\text{{ cm}}^2$",
        [f"${pl_num(w1)}\\text{{ cm}}^2$", f"${pl_num(w2)}\\text{{ cm}}^2$", f"${pl_num(w3)}\\text{{ cm}}^2$"],
    )
    k_word = {3: "trzech", 4: "czterech", 5: "pięciu"}[k]

    return {
        "stem": (
            f"Z {k_word} jednakowych drewnianych sześcianów, z których każdy ma krawędź długości ${a}$ cm, "
            f"sklejono wysoki prostopadłościenny słupek (ustawiając sześciany jeden dokładnie na drugim)."
        ),
        "command": "Jakie jest pole powierzchni całkowitej tak zbudowanego słupka? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Słupek jest prostopadłościanem o wymiarach ${a}\\text{{ cm}} \\times {a}\\text{{ cm}} \\times {k * a}\\text{{ cm}}$ (składa się z $4 \\cdot {k} + 2 = {faces_exposed}$ kwadratowych ścianek o boku ${a}\\text{{ cm}}$).",
            f"Pole jednej kwadratowej ścianki wynosi ${a}^2 = {a * a}\\text{{ cm}}^2$, więc pole całkowite słupka jest równe ${faces_exposed} \\cdot {a * a} = {pl_num(area)}\\text{{ cm}}^2$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="stereometria_wieze_szescian_ostroslup_2pkt",
    topic_id="geometria_przestrzenna",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2024 zad. 19",
)
def gen_wieze_ostroslup(rng):
    a_cube = rng.choice([8, 10, 12])
    a_pyr = rng.choice([6, 9, 12])
    # Dobieramy wysokość ostrosłupa tak, aby różnica wysokości wież (2 sześciany vs 1 sześcian + ostrosłup) była niezerowa
    h_pyr = a_cube + rng.choice([-3, -2, 2, 3, 4])
    vol_pyr = (a_pyr * a_pyr * h_pyr) // 3
    h_tower1 = 2 * a_cube
    h_tower2 = a_cube + h_pyr
    diff = abs(h_tower1 - h_tower2)

    return {
        "stem": (
            f"Z trzech jednakowych klocków w kształcie sześcianu o krawędzi ${a_cube}$ cm oraz jednego klocka "
            f"w kształcie ostrosłupa prawidłowego czworokątnego zbudowano dwie wieże: pierwszą z dwóch sześcianów "
            f"ustawionych jeden na drugim, a drugą – z jednego sześcianu i postawionego na nim ostrosłupa. "
            f"Krawędź podstawy ostrosłupa ma długość ${a_pyr}$ cm, a jego objętość jest równa ${pl_num(vol_pyr)}\\text{{ cm}}^3$."
        ),
        "command": "Oblicz różnicę wysokości obu zbudowanych wież. Zapisz obliczenia.",
        "correct_answer": f"{diff} cm",
        "solution_steps": [
            f"Pole podstawy ostrosłupa wynosi $P_p = {a_pyr}^2 = {a_pyr * a_pyr}\\text{{ cm}}^2$. Z wzoru $V = \\frac{{1}}{{3}} P_p \\cdot H$ wyznaczamy wysokość ostrosłupa: "
            f"${pl_num(vol_pyr)} = \\frac{{1}}{{3}} \\cdot {a_pyr * a_pyr} \\cdot H \\Rightarrow H = {h_pyr}\\text{{ cm}}$.",
            f"Wysokość pierwszej wieży to $2 \\cdot {a_cube} = {h_tower1}\\text{{ cm}}$, a drugiej: ${a_cube} + {h_pyr} = {h_tower2}\\text{{ cm}}$.",
            f"Różnica wysokości wież wynosi $|{h_tower1} - {h_tower2}| = {diff}\\text{{ cm}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne obliczenie wysokości ostrosłupa ({h_pyr} cm).",
            f"2 pkt – obliczenie wysokości obu wież i podanie różnicy: {diff} cm.",
        ],
        "grid_height_mm": 52.0,
    }


# ===========================================================================
# 11. STATYSTYKA, TABELE I DIAGRAMY (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="statystyka_diagram_kolowy_abcd",
    topic_id="statystyka_diagramy",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2026 zad. 1 / Grudzień 2024 zad. 7",
    has_diagram=True,
)
def gen_diagram_kolowy(rng):
    total = rng.choice([40, 80, 120, 200])
    p1, p2, p3 = rng.choice([(35, 25, 15), (40, 25, 20), (30, 35, 15), (45, 20, 10)])
    p4 = 100 - (p1 + p2 + p3)
    cats = ["algebra", "geometria", "arytmetyka", "statystyka"]
    val4 = (total * p4) // 100

    w1 = p4
    w2 = (total * p3) // 100
    w3 = total - p1 - p2 - p3 if (total - p1 - p2 - p3 > 0 and total != 100) else val4 + 6
    choices, ans = shuffle_abcd(rng, f"${val4}$", [f"${w1}$", f"${w2}$", f"${w3}$"])

    return {
        "stem": (
            f"Zestaw powtórkowy z matematyki składa się z ${total}$ zadań podzielonych na cztery działy. "
            f"Na diagramie kołowym przedstawiono procentowy podział tych zadań."
        ),
        "diagram": DiagramSpec(
            kind="pie_chart",
            params={"labels": cats, "percents": [p1, p2, p3, p4], "hide_percent_index": 3},
            width_mm=84.0,
        ),
        "command": "Ile zadań ze statystyki znajduje się w tym zestawie? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Obliczamy procentowy udział zadań ze statystyki: $100\\% - ({p1}\\% + {p2}\\% + {p3}\\%) = {p4}\\%$.",
            f"Obliczamy liczbę zadań: ${p4}\\% \\cdot {total} = \\frac{{{p4}}}{{100}} \\cdot {total} = {val4}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="statystyka_dzien_sportu_tabela_3pkt",
    topic_id="statystyka_diagramy",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2026 zad. 17",
)
def gen_dzien_sportu_tabela(rng):
    # Dokładnie archetyp CKE Maj 2026 zad. 17: suma wszystkich uczestników = 200 lub 250 dla czystego procentu!
    total = rng.choice([200, 250])
    diff_gb = rng.choice([8, 10, 12, 16]) if total == 200 else rng.choice([10, 20, 30])
    # girls + boys = total, girls - boys = diff_gb
    girls_tot = (total + diff_gb) // 2
    boys_tot = total - girls_tot

    b1 = rng.randint(32, 48)
    b2 = rng.randint(14, 24)
    b3 = boys_tot - b1 - b2

    g1 = rng.randint(12, 22)
    g2 = rng.randint(52, 68)
    g3 = girls_tot - g1 - g2  # szukana liczba dziewcząt w tenisie stołowym

    tennis_tot = g3 + b3
    pct_tennis = Fraction(tennis_tot * 100, total)

    return {
        "stem": (
            f"Podczas szkolnego Dnia Sportu rozegrano trzy turnieje. Każdy uczestnik wziął udział w dokładnie jednym "
            f"turnieju. W tabeli podano liczby dzieci startujących w poszczególnych dyscyplinach. Wiadomo, że łączna "
            f"liczba dziewcząt była o ${diff_gb}$ większa od łącznej liczby chłopców uczestniczących w Dniu Sportu."
        ),
        "table_data": [
            ["", "Turniej piłki nożnej", "Turniej tańca", "Turniej tenisa stołowego"],
            ["Liczba dziewcząt", f"${g1}$", f"${g2}$", "$?$"],
            ["Liczba chłopców", f"${b1}$", f"${b2}$", f"${b3}$"],
        ],
        "command": (
            "Oblicz, ile procent liczby wszystkich uczestników Dnia Sportu stanowi liczba dzieci, "
            "które brały udział w turnieju tenisa stołowego. Zapisz obliczenia."
        ),
        "correct_answer": f"{pl_num(pct_tennis)}%",
        "solution_steps": [
            f"Łączna liczba chłopców wynosi: ${b1} + {b2} + {b3} = {boys_tot}$. Ponieważ dziewcząt było o ${diff_gb}$ więcej, łączna liczba dziewcząt to ${boys_tot} + {diff_gb} = {girls_tot}$.",
            f"Liczba dziewcząt w turnieju tenisa stołowego: ${girls_tot} - ({g1} + {g2}) = {g3}$. Wszystkich uczestników Dnia Sportu było ${girls_tot} + {boys_tot} = {total}$.",
            f"W turnieju tenisa stołowego startowało łącznie ${g3} + {b3} = {tennis_tot}$ dzieci, co stanowi $\\frac{{{tennis_tot}}}{{{total}}} \\cdot 100\\% = {pl_num(pct_tennis)}\\%$ wszystkich uczestników.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie łącznej liczby chłopców ({boys_tot}) i łącznej liczby dziewcząt ({girls_tot}).",
            f"2 pkt – wyznaczenie brakującej liczby dziewcząt ({g3}) oraz łącznej liczby uczestników ({total}).",
            f"3 pkt – poprawne obliczenie procentowego udziału: {pl_num(pct_tennis)}%.",
        ],
        "grid_height_mm": 60.0,
    }


# ===========================================================================
# 12. PRAWDOPODOBIEŃSTWO I KOMBINATORYKA (2 nowe wzorce CKE)
# ===========================================================================

@register_template(
    template_id="prawdop_balony_bez_zwracania_abcd",
    topic_id="prawdopodobienstwo",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2024 zad. 8",
)
def gen_balony_bez_zwracania(rng):
    c_red = rng.choice([10, 12, 14])
    c_blue = rng.choice([6, 8, 10])
    c_green = rng.choice([6, 8])
    c_yellow = rng.choice([6, 8])
    drawn = 2
    rem_red = c_red - drawn
    rem_tot = (c_red + c_blue + c_green + c_yellow) - drawn

    p_corr = Fraction(rem_red, rem_tot)
    p_w1 = Fraction(c_red, c_red + c_blue + c_green + c_yellow)
    p_w2 = Fraction(rem_red, c_red + c_blue + c_green + c_yellow)
    p_w3 = Fraction(c_red, rem_tot)

    def _f_str(fr: Fraction) -> str:
        return frac_tex(fr.numerator, fr.denominator)

    # Upewnij się, że ułamki dystraktorów są parami różne
    wrongs = []
    for cand in [p_w1, p_w2, p_w3, Fraction(rem_red - 1, rem_tot), Fraction(1, 4), Fraction(1, 3)]:
        if cand != p_corr and cand not in wrongs and cand > 0:
            wrongs.append(cand)
        if len(wrongs) == 3:
            break

    choices, ans = shuffle_abcd(rng, _f_str(p_corr), [_f_str(w) for w in wrongs])

    return {
        "stem": (
            "Karolina kupiła paczkę kolorowych balonów. W tabeli podano liczby balonów poszczególnych kolorów "
            "znajdujących się na początku w tej paczce.\n"
            f"Karolina wyjmowała losowo po jednym balonie bez zwracania. Pierwsze dwa wyjęte balony były czerwone."
        ),
        "table_data": [
            ["Kolor balonu", "czerwony", "niebieski", "zielony", "żółty"],
            ["Liczba balonów", f"${c_red}$", f"${c_blue}$", f"${c_green}$", f"${c_yellow}$"],
        ],
        "command": "Jakie jest prawdopodobieństwo, że trzeci losowo wyjęty balon również będzie czerwony? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Początkowo w paczce były ${c_red} + {c_blue} + {c_green} + {c_yellow} = {rem_tot + 2}$ balony.",
            f"Po wyjęciu dwóch czerwonych balonów w paczce zostało ${rem_tot}$ balonów, w tym ${c_red} - 2 = {rem_red}$ czerwonych.",
            f"Szukane prawdopodobieństwo wynosi $\\frac{{{rem_red}}}{{{rem_tot}}} = {_f_str(p_corr)}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="prawdop_kule_parzystosc_sumy_ab_cd",
    topic_id="prawdopodobienstwo",
    subtype="ab_cd",
    points=1,
    difficulty=3,
    cke_ref="Wzorzec: CKE Maj 2026 zad. 6",
)
def gen_kule_parzystosc_sumy(rng):
    # W pudełku kule 1..(2k+1), np. 1..11 (6 nieparzystych, 5 parzystych).
    # Wyjęto k kul. Suma dowolnych dwóch pozostałych jest parzysta => wszystkie pozostałe k+1 kul mają tę samą parzystość!
    # Ponieważ parzystych jest tylko k, a zostało k+1 kul, w pudełku MUSIAŁY zostać same nieparzyste, a wyjęto wszystkie k parzystych!
    k = rng.choice([4, 5, 6])  # 1..9 (wyjęto 4), 1..11 (wyjęto 5), 1..13 (wyjęto 6)
    max_n = 2 * k + 1
    sum_even = sum(2 * i for i in range(1, k + 1))  # k(k+1)
    sum_odd_k = sum(2 * i - 1 for i in range(1, k + 1))  # k^2 – dystraktor!

    opts1 = {"A": "nieparzystymi", "B": "parzystymi"}
    a1 = "A"
    if rng.random() < 0.5:
        opts1 = {"A": "parzystymi", "B": "nieparzystymi"}
        a1 = "B"

    if rng.random() < 0.5:
        opts2 = {"C": f"${sum_even}$", "D": f"${sum_odd_k}$"}
        a2 = "C"
    else:
        opts2 = {"C": f"${sum_odd_k}$", "D": f"${sum_even}$"}
        a2 = "D"

    return {
        "stem": (
            f"W pudełku było ${max_n}$ kul ponumerowanych kolejnymi liczbami naturalnymi od $1$ do ${max_n}$. "
            f"Z pudełka wyjęto ${k}$ kul. Okazało się, że suma liczb na dowolnych dwóch kulach, które pozostały "
            f"w pudełku, jest liczbą parzystą."
        ),
        "command": "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D.",
        "ab_cd_parts": [
            {
                "prefix": "Po wyjęciu kul w pudełku zostały wyłącznie kule ponumerowane liczbami",
                "suffix": ".",
                "options": opts1,
            },
            {
                "prefix": f"Suma liczb na ${k}$ wyjętych kulach jest równa",
                "suffix": ".",
                "options": opts2,
            },
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Suma dwóch liczb jest parzysta wtedy, gdy obie są parzyste albo obie są nieparzyste. W pudełku zostało ${max_n} - {k} = {k + 1}$ kul, więc wszystkie muszą mieć tę samą parzystość.",
            f"Wśród liczb $1..{max_n}$ jest tylko ${k}$ parzystych oraz ${k + 1}$ nieparzystych, zatem w pudełku musiały zostać wszystkie ${k + 1}$ kul **nieparzystych** (**{a1}**).",
            f"Wyjęto więc wszystkie ${k}$ kul parzystych, których suma wynosi: $" + " + ".join(str(2 * i) for i in range(1, k + 1)) + f" = {sum_even}$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna para odpowiedzi.", "0 pkt – odpowiedź niepełna lub błędna."],
    }
