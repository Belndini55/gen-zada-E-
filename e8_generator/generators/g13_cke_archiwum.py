"""Pakiet 24 wielowariantowych generatorów proceduralnych w standardzie CKE E8.

Każdy generator losuje zarówno wariant struktury matematycznej, jak i niezależny scenariusz
fabularny spośród wielu oryginalnych kontekstów, dzięki czemu kolejne generowania tworzą
zupełnie nowe zadania (bez powielania gotowych treści z archiwalnych arkuszy).
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
# 1. LICZBY I DZIAŁANIA
# ===========================================================================

@register_template(
    template_id="liczby_rzymskie_os_abcd",
    topic_id="liczby_dzialania",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – zapis rzymski i porównywanie liczb",
)
def gen_liczby_rzymskie_os(rng):
    mode = rng.choice(["closest", "diff", "between"])
    if mode == "closest":
        target = rng.choice([150, 250, 400, 600, 900, 1400, 1600, 1900])
        d_best = rng.choice([4, 6, 7, 9, 11, 13])
        d2 = d_best + rng.choice([7, 11, 14])
        d3 = d_best + rng.choice([21, 27, 32])
        d4 = d_best + rng.choice([39, 46, 54])
        vals = [target + rng.choice([-1, 1]) * d for d in (d_best, d2, d3, d4)]
        romans = [_to_roman(v) for v in vals]
        shown = list(romans)
        rng.shuffle(shown)
        choices, ans = shuffle_abcd(rng, romans[0], romans[1:])
        ctx = rng.choice([
            f"Na kartach gry historycznej zapisano cztery liczby w systemie rzymskim: **{shown[0]}**, **{shown[1]}**, **{shown[2]}** oraz **{shown[3]}**.",
            f"Cztery kamienie milowe oznaczono liczbami rzymskimi: **{shown[0]}**, **{shown[1]}**, **{shown[2]}** oraz **{shown[3]}**.",
            f"W katalogu monet numizmatycznych zanotowano cztery daty roczne: **{shown[0]}**, **{shown[1]}**, **{shown[2]}** oraz **{shown[3]}**.",
        ])
        dec_parts = ", ".join(f"{r} $= {pl_num(v)}$" for r, v in zip(romans, vals))
        return {
            "stem": ctx,
            "command": f"Która z podanych liczb różni się najmniej od liczby ${pl_num(target)}$? Wybierz właściwą odpowiedź spośród podanych.",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Zamieniamy liczby na system dziesiętny: {dec_parts}.",
                f"Obliczamy odległość każdej z nich od ${pl_num(target)}$ – najmniejszą różnicę (${d_best}$) ma **{romans[0]}** ($= {pl_num(vals[0])}$). Poprawna odpowiedź: **{ans}**.",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    if mode == "diff":
        a = rng.choice([1380, 1492, 1683, 1795, 1918, 1989, 2024])
        span = rng.choice([145, 185, 215, 260, 315, 370])
        b = a - span
        ra, rb = _to_roman(a), _to_roman(b)
        choices, ans = shuffle_abcd(
            rng,
            f"${span}$",
            [f"${span + 100}$", f"${abs(span - 50)}$", f"${span + 20}$"],
        )
        ctx = rng.choice([
            f"Na tablicy pamiątkowej widnieją dwie daty zapisane w systemie rzymskim: **{rb}** oraz **{ra}**.",
            f"Dwa zabytkowe rękopisy w bibliotece opatrzono numerami katalogowymi **{rb}** oraz **{ra}**.",
        ])
        return {
            "stem": ctx,
            "command": "Ile wynosi różnica między większą a mniejszą z tych dwóch liczb? Wybierz właściwą odpowiedź spośród podanych.",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Odczytujemy obie liczby: {rb} $= {pl_num(b)}$ oraz {ra} $= {pl_num(a)}$.",
                f"Obliczamy różnicę: ${pl_num(a)} - {pl_num(b)} = {span}$ (odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    # mode == "between"
    low = rng.choice([390, 440, 890, 1440, 1590])
    high = low + rng.choice([30, 40])
    v_in = rng.randint(low + 4, high - 4)
    v_w1 = low - rng.randint(8, 25)
    v_w2 = high + rng.randint(9, 28)
    v_w3 = high + rng.randint(45, 95)
    r_corr = _to_roman(v_in)
    r_wrongs = [_to_roman(v_w1), _to_roman(v_w2), _to_roman(v_w3)]
    choices, ans = shuffle_abcd(rng, r_corr, r_wrongs)
    return {
        "stem": f"Rozważmy przedział liczb naturalnych większych od ${pl_num(low)}$ i jednocześnie mniejszych od ${pl_num(high)}$.",
        "command": "Która z poniższych liczb zapisanych w systemie rzymskim należy do tego przedziału? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Zamieniamy podane zapisy rzymskie na dziesiętne: {r_corr} $= {pl_num(v_in)}$, {r_wrongs[0]} $= {pl_num(v_w1)}$, {r_wrongs[1]} $= {pl_num(v_w2)}$, {r_wrongs[2]} $= {pl_num(v_w3)}$.",
            f"Warunek ${pl_num(low)} < n < {pl_num(high)}$ spełnia liczba **{r_corr}** ($= {pl_num(v_in)}$), odpowiedź **{ans}**.",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="liczby_nwd_nww_kod_abcd",
    topic_id="liczby_dzialania",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – NWD i NWW w sytuacjach praktycznych",
)
def gen_liczby_nwd_nww(rng):
    variant = rng.choice(["intervals", "packs", "quotient"])
    if variant == "intervals":
        t1, t2 = rng.choice([(12, 18), (15, 20), (16, 24), (18, 24), (20, 30), (14, 21)])
        lcm_min = math.lcm(t1, t2)
        start_h = rng.choice([7, 8, 9, 10, 11])
        start_m = rng.choice([0, 10, 15, 20])
        tot_m = start_h * 60 + start_m + lcm_min
        end_str = f"${tot_m // 60}:{tot_m % 60:02d}$"
        w1_m = start_h * 60 + start_m + (t1 + t2)
        w2_m = start_h * 60 + start_m + (t1 * t2)
        w3_m = start_h * 60 + start_m + math.gcd(t1, t2) * 3
        wrongs = [f"${m // 60}:{m % 60:02d}$" for m in (w1_m, w2_m, w3_m)]
        choices, ans = shuffle_abcd(rng, end_str, wrongs)
        place = rng.choice([
            ("Dwa tramwaje różnych linii odjeżdżają z tej samej pętli", "odjechały jednocześnie"),
            ("Dwie fontanny multimedialne w parku uruchamiają pokaz", "uruchomiły się równocześnie"),
            ("Dwa autobusy podmiejskie ruszają z dworca głównego", "wyruszyły w tym samym momencie"),
        ])
        return {
            "stem": (
                f"{place[0]}: pierwszy dokładnie co ${t1}$ minut, a drugi dokładnie co ${t2}$ minut. "
                f"O godzinie ${start_h}:{start_m:02d}$ oba {place[1]}."
            ),
            "command": "O której godzinie po raz kolejny nastąpi to jednocześnie? Wybierz właściwą odpowiedź spośród podanych.",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Szukamy najmniejszej wspólnej wielokrotności okresów: $\\text{{NWW}}({t1}, {t2}) = {lcm_min}$ minut.",
                f"Dodajemy ${lcm_min}$ minut do godziny ${start_h}:{start_m:02d}$ i otrzymujemy {end_str} (odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    if variant == "packs":
        a, b = rng.choice([(36, 48), (42, 56), (45, 75), (48, 64), (54, 72), (60, 84)])
        g = math.gcd(a, b)
        per_pack = (a + b) // g
        ask_count = rng.choice([True, False])
        item_ctx = rng.choice([
            ("zeszytów w kratkę", "zeszytów w linię", "identycznych zestawów startowych"),
            ("sadzonek lawendy", "sadzonek rozmarynu", "jednakowych skrzynek ogrodowych"),
            ("batonów zbożowych", "jabłek", "równych pakietów regeneracyjnych na bieg"),
        ])
        if ask_count:
            corr = f"${g}$"
            wrongs = [f"${per_pack}$", f"${g // 2 if g % 2 == 0 else g + 3}$", f"${math.lcm(a, b)}$"]
            cmd = f"Jaka jest największa możliwa liczba {item_ctx[2]}, które można w ten sposób przygotować? Wybierz właściwą odpowiedź spośród podanych."
        else:
            corr = f"${per_pack}$"
            wrongs = [f"${g}$", f"${a // g}$", f"${b // g}$"]
            cmd = f"Ile łącznie sztuk obu produktów znajdzie się w jednym takim zestawie, jeśli liczba zestawów będzie największa możliwa? Wybierz właściwą odpowiedź spośród podanych."
        choices, ans = shuffle_abcd(rng, corr, wrongs)
        steps = [f"Obliczamy największą liczbę identycznych zestawów: $\\text{{NWD}}({a}, {b}) = {g}$."]
        if ask_count:
            steps.append(f"Można przygotować maksymalnie ${g}$ zestawów (odpowiedź **{ans}**).")
        else:
            steps.append(f"W każdym z ${g}$ zestawów będzie ${a} : {g} + {b} : {g} = {per_pack}$ sztuk (odpowiedź **{ans}**).")
        return {
            "stem": (
                f"Przygotowano ${a}$ {item_ctx[0]} oraz ${b}$ {item_ctx[1]}. Wszystkie te przedmioty trzeba rozdzielić "
                f"bez reszty do {item_ctx[2]} tak, aby w każdym zestawie skład ilościowy był identyczny."
            ),
            "command": cmd,
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": steps,
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    # variant == "quotient"
    a, b = rng.choice([(18, 30), (20, 28), (24, 40), (27, 36), (30, 45), (32, 48)])
    g = math.gcd(a, b)
    l = math.lcm(a, b)
    ratio = l // g
    choices, ans = shuffle_abcd(rng, f"${ratio}$", [f"${g}$", f"${l}$", f"${l - g}$"])
    return {
        "stem": f"Dane są dwie liczby naturalne: $a = {a}$ oraz $b = {b}$.",
        "command": (
            "Ile razy najmniejsza wspólna wielokrotność ($\\text{NWW}$) liczb $a$ i $b$ jest większa od ich "
            "największego wspólnego dzielnika ($\\text{NWD}$)? Wybierz właściwą odpowiedź spośród podanych."
        ),
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Wyznaczamy $\\text{{NWD}}({a}, {b}) = {g}$ oraz $\\text{{NWW}}({a}, {b}) = {l}$.",
            f"Obliczamy iloraz: ${l} : {g} = {ratio}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


# ===========================================================================
# 2. PROCENTY I PROPORCJE
# ===========================================================================

@register_template(
    template_id="procenty_skala_planu_abcd",
    topic_id="procenty_proporcje",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – skala mapy i planu",
)
def gen_skala_planu(rng):
    ask_map = rng.choice([True, False])
    if not ask_map:
        cm_plan = rng.choice([5, 7, 9, 12, 14, 16])
        scale = rng.choice([2000, 5000, 10000, 20000, 50000])
        real_m = (cm_plan * scale) // 100
        use_km = real_m >= 1000 and real_m % 100 == 0
        if use_km:
            val_km = real_m / 1000
            correct = f"${pl_num(val_km)}$ km"
            wrongs = [f"${pl_num(val_km * 10)}$ km", f"${pl_num(val_km / 10)}$ km", f"${pl_num(cm_plan * 2)}$ km"]
        else:
            correct = f"${pl_num(real_m)}$ m"
            wrongs = [f"${pl_num(real_m * 10)}$ m", f"${pl_num(max(5, real_m // 10))}$ m", f"${pl_num(scale // 100)}$ m"]
        choices, ans = shuffle_abcd(rng, correct, wrongs)
        obj = rng.choice([
            "ścieżka pieszo-rowerowa wokół zalewu ma na mapie długość",
            "odcinek nowej linii kolejowej zaznaczony na mapie ma długość",
            "długość prostoliniowego kanału żeglugowego na planie wynosi",
        ])
        return {
            "stem": f"Na mapie wykonanej w skali $1 : {pl_num(scale)}$ {obj} ${cm_plan}$ cm.",
            "command": "Jaka jest rzeczywista długość tego obiektu w terenie? Wybierz właściwą odpowiedź spośród podanych.",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Skala $1 : {pl_num(scale)}$ oznacza, że $1\\text{{ cm}}$ na mapie odpowiada ${pl_num(scale // 100)}\\text{{ m}}$ w terenie.",
                f"Rzeczywista długość wynosi ${cm_plan} \\cdot {pl_num(scale // 100)}\\text{{ m}} = {pl_num(real_m)}\\text{{ m}}$ ({correct}, odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    # Szukamy długości na planie znając długość w terenie
    scale = rng.choice([2500, 4000, 5000, 20000])
    cm_ans = rng.choice([6, 8, 11, 15])
    real_m = (cm_ans * scale) // 100
    choices, ans = shuffle_abcd(
        rng,
        f"${cm_ans}$ cm",
        [f"${cm_ans * 10}$ cm", f"${pl_num(cm_ans / 2)}$ cm", f"${cm_ans + 4}$ cm"],
    )
    obj = rng.choice(["mostu wiszącego", "alei parkowej", "pasa startowego dla szybowców"])
    return {
        "stem": f"Rzeczywista długość {obj} wynosi ${pl_num(real_m)}$ m. Obiekt ten narysowano na planie w skali $1 : {pl_num(scale)}$.",
        "command": "Jaką długość ma ten obiekt na planie? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"$1\\text{{ cm}}$ na planie odpowiada ${pl_num(scale)}\\text{{ cm}} = {pl_num(scale // 100)}\\text{{ m}}$ w terenie.",
            f"Długość na planie jest równa ${pl_num(real_m)} : {pl_num(scale // 100)} = {cm_ans}\\text{{ cm}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="procenty_truskawki_opakowania_3pkt",
    topic_id="procenty_proporcje",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Styl CKE – podział procentowy na porcje i cennik",
)
def gen_truskawki_opakowania(rng):
    scenario = rng.choice([
        ("Pasieka rozlała", "miodu lipowego", "słoikach", "Rodzaj słoika", "Masa miodu", "duży", "średni", "mały", "kg", 1, 0.5, 0.25, [28, 32, 36], [15, 17, 19], [8, 9, 11]),
        ("Palarnia kawy zapakowała", "ziaren kawy", "torebkach", "Wielkość torebki", "Masa kawy", "rodzinna", "standardowa", "degustacyjna", "kg", 1, 0.5, 0.25, [64, 72], [35, 38], [19, 21]),
        ("Wytwórnia soków rozlała", "świeżo tłoczonego soku", "butelkach", "Rodzaj butelki", "Pojemność", "duża", "średnia", "mała", "l", 2, 1, 0.5, [14, 16, 18], [8, 9, 10], [5, 6]),
    ])
    intro, prod_gen, cont_loc, col1, col2, n1, n2, n3, unit, s1, s2, s3, p1s, p2s, p3s = scenario

    total_amt = rng.choice([80, 120, 160, 200])
    pct1 = rng.choice([40, 50])
    pct2 = rng.choice([20, 25, 30])
    amt1 = (total_amt * pct1) // 100
    amt2 = (total_amt * pct2) // 100
    amt3 = total_amt - amt1 - amt2

    cnt1 = int(round(amt1 / s1))
    cnt2 = int(round(amt2 / s2))
    cnt3 = int(round(amt3 / s3))

    p1 = rng.choice(p1s)
    p2 = rng.choice(p2s)
    p3 = rng.choice(p3s)
    revenue = cnt1 * p1 + cnt2 * p2 + cnt3 * p3

    return {
        "stem": (
            f"{intro} łącznie ${total_amt}$ {unit} {prod_gen}. Dokładnie ${pct1}\\%$ tej ilości sprzedano w {cont_loc} "
            f"typu *{n1}*, ${pct2}\\%$ – w {cont_loc} typu *{n2}*, a całą resztę – w {cont_loc} typu *{n3}*. "
            f"Szczegóły dotyczące pojemności i cen zestawiono w tabeli."
        ),
        "table_data": [
            [col1, col2, "Cena za 1 sztukę"],
            [n1, f"${pl_num(s1)}$ {unit}", f"${p1}$ zł"],
            [n2, f"${pl_num(s2)}$ {unit}", f"${p2}$ zł"],
            [n3, f"${pl_num(s3)}$ {unit}", f"${p3}$ zł"],
        ],
        "command": f"Oblicz łączny przychód uzyskany ze sprzedaży wszystkich przygotowanych sztuk. Zapisz obliczenia.",
        "correct_answer": f"{pl_num(revenue)} zł",
        "solution_steps": [
            f"Ilości w poszczególnych wariantach: *{n1}*: ${pct1}\\% \\cdot {total_amt} = {amt1}$ {unit}, "
            f"*{n2}*: ${pct2}\\% \\cdot {total_amt} = {amt2}$ {unit}, *{n3}*: ${total_amt} - ({amt1} + {amt2}) = {amt3}$ {unit}.",
            f"Liczby sztuk: *{n1}*: ${amt1} : {pl_num(s1)} = {cnt1}$, *{n2}*: ${amt2} : {pl_num(s2)} = {cnt2}$, *{n3}*: ${amt3} : {pl_num(s3)} = {cnt3}$.",
            f"Łączny przychód: ${cnt1} \\cdot {p1} + {cnt2} \\cdot {p2} + {cnt3} \\cdot {p3} = {cnt1 * p1} + {cnt2 * p2} + {cnt3 * p3} = {pl_num(revenue)}$ zł.",
        ],
        "scoring_scheme": [
            f"1 pkt – poprawne wyznaczenie ilości ({amt1}, {amt2}, {amt3} {unit}) przypadających na każdy rodzaj opakowania.",
            f"2 pkt – poprawne obliczenie liczby sztuk każdego wariantu ({cnt1}, {cnt2}, {cnt3}).",
            f"3 pkt – pełne obliczenia i podanie łącznego przychodu: {pl_num(revenue)} zł.",
        ],
        "grid_height_mm": 60.0,
    }


# ===========================================================================
# 3. POTĘGI I NOTACJA WYKŁADNICZA
# ===========================================================================

@register_template(
    template_id="potegi_duza_liczba_z_zerami_abcd",
    topic_id="potegi_notacja",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – potęgowanie iloczynu i potęg liczby 10",
)
def gen_potegi_duza_liczba(rng):
    is_small = rng.choice([False, True])
    digit = rng.choice([2, 3, 4, 5, 6, 7])
    exp = rng.choice([2, 3, 4])
    if not is_small:
        zeros = rng.choice([4, 5, 6, 7])
        big_fmt = pl_num(int(f"{digit}" + "0" * zeros))
        correct = f"${digit}^{{{exp}}} \\cdot 10^{{{zeros * exp}}}$"
        wrongs = [
            f"${digit} \\cdot 10^{{{zeros * exp}}}$",
            f"${digit}^{{{exp}}} \\cdot 10^{{{zeros + exp}}}$",
            f"${digit * exp} \\cdot 10^{{{zeros * exp}}}$",
        ]
        choices, ans = shuffle_abcd(rng, correct, wrongs)
        return {
            "stem": f"Rozważmy potęgę dużej liczby naturalnej: $({big_fmt})^{{{exp}}}$.",
            "command": "Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\nPodana liczba zapisana w postaci iloczynu potęg jest równa",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Zapisujemy podstawę jako iloczyn: ${big_fmt} = {digit} \\cdot 10^{{{zeros}}}$.",
                f"Korzystamy ze wzoru $(a \\cdot b)^n = a^n \\cdot b^n$: $({digit} \\cdot 10^{{{zeros}}})^{{{exp}}} = {digit}^{{{exp}}} \\cdot 10^{{{zeros * exp}}}$ (odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    dec_places = rng.choice([3, 4, 5])
    dec_str = "0," + "0" * (dec_places - 1) + str(digit)
    correct = f"${digit}^{{{exp}}} \\cdot 10^{{−{dec_places * exp}}}$"
    wrongs = [
        f"${digit} \\cdot 10^{{−{dec_places * exp}}}$",
        f"${digit}^{{{exp}}} \\cdot 10^{{−{dec_places + exp}}}$",
        f"${digit}^{{{exp}}} \\cdot 10^{{{dec_places * exp}}}$",
    ]
    choices, ans = shuffle_abcd(rng, correct, wrongs)
    return {
        "stem": f"Dana jest potęga ułamka dziesiętnego: $({dec_str})^{{{exp}}}$.",
        "command": "Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\nWartość tego wyrażenia jest równa",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Zapisujemy ułamek w postaci iloczynu: ${dec_str} = {digit} \\cdot 10^{{-{dec_places}}}$.",
            f"Podnosząc do potęgi ${exp}$, otrzymujemy ${digit}^{{{exp}}} \\cdot 10^{{-{dec_places * exp}}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="potegi_porownanie_10_do_k_abcd",
    topic_id="potegi_notacja",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – porównywanie wyrażeń potęgowych",
)
def gen_potegi_porownanie_100(rng):
    base = rng.choice([2, 3, 5, 10])
    target_exp = rng.choice([30, 40, 50, 80])
    ask_greater = rng.choice([True, False])
    if ask_greater:
        e_x = target_exp + rng.randint(2, 6)
        e_y = target_exp - rng.randint(2, 5)
        e_z = target_exp
    else:
        e_x = target_exp - rng.randint(1, 4)
        e_y = target_exp + rng.randint(2, 6)
        e_z = target_exp + rng.randint(1, 5)

    p1 = e_x // 2 - 3
    p2 = e_x - p1 + 4
    fx = rf"\frac{{{base}^{{{p1}}} \cdot {base}^{{{p2}}}}}{{{base}^4}}"
    fy = rf"({base}^3)^{{{e_y // 3}}} \cdot {base}^{{{e_y - 3 * (e_y // 3)}}}"
    fz = rf"\frac{{({base}^2)^{{{e_z // 2 + 5}}}}}{{{base}^{{10}}}}"

    rel_word = "większa" if ask_greater else "mniejsza"
    choices, ans = shuffle_abcd(
        rng,
        "Tylko $a$.",
        ["Tylko $b$.", "Tylko $c$.", "Zarówno $a$, jak i $c$."],
    )
    return {
        "stem": f"Dane są trzy wyrażenia:\n$a = {fx}$,   $b = {fy}$,   $c = {fz}$.",
        "command": f"Która z podanych liczb jest {rel_word} od liczby ${base}^{{{target_exp}}}$? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Upraszczamy wykładniki przy podstawie ${base}$: $a = {base}^{{{p1}+{p2}-4}} = {base}^{{{e_x}}}$, $b = {base}^{{{e_y}}}$, $c = {base}^{{{2*(e_z//2+5)-10}}} = {base}^{{{e_z if e_z % 2 == 0 else e_z - 1}}}$.",
            f"Spośród nich {rel_word} od ${base}^{{{target_exp}}}$ jest wyłącznie liczba $a = {base}^{{{e_x}}}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


# ===========================================================================
# 4. PIERWIASTKI
# ===========================================================================

@register_template(
    template_id="pierwiastki_nawias_rozdzielnosc_abcd",
    topic_id="pierwiastki",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – wyłączanie czynnika i mnożenie pierwiastków",
)
def gen_pierwiastki_nawias(rng):
    op = rng.choice(["-", "+"])
    base_p = rng.choice([2, 3, 5, 6, 7])
    k1, k2 = rng.choice([(4, 1), (4, 2), (5, 2), (5, 3), (6, 2)])
    n1 = base_p * (k1 ** 2)
    n2 = base_p * (k2 ** 2)
    val = base_p * (k1 - k2) if op == "-" else base_p * (k1 + k2)

    s_out = rf"\sqrt{{{base_p}}}"
    s_in = rf"\sqrt{{{n1}}} {op} \sqrt{{{n2}}}"
    w1 = rf"$\sqrt{{{val}}}$"
    w2 = rf"${k1 - k2 if op == '-' else k1 + k2}$"
    w3 = rf"${val}\sqrt{{{base_p}}}$"
    choices, ans = shuffle_abcd(rng, f"${val}$", [w1, w2, w3])

    return {
        "stem": f"Rozważmy wyrażenie arytmetyczne $W = {s_out} \\cdot ({s_in})$.",
        "command": "Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\nPo wykonaniu działań wartość wyrażenia $W$ jest równa",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Korzystamy z rozdzielności mnożenia: ${s_out} \\cdot \\sqrt{{{n1}}} {op} {s_out} \\cdot \\sqrt{{{n2}}} = \\sqrt{{{base_p * n1}}} {op} \\sqrt{{{base_p * n2}}}$.",
            f"Wyciągamy pierwiastki kwadratowe: ${base_p * k1} {op} {base_p * k2} = {val}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="pierwiastki_szescian_z_klockow_abcd",
    topic_id="pierwiastki",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – kwadraty i sześciany liczb naturalnych",
)
def gen_klocki_szescian(rng):
    mode = rng.choice(["cube_leftover", "cube_missing", "square_tiles"])
    if mode == "cube_leftover":
        k = rng.choice([3, 4, 5, 6])
        cube = k ** 3
        next_cube = (k + 1) ** 3
        rem = rng.randint(11, next_cube - cube - 9)
        total = cube + rem
        choices, ans = shuffle_abcd(rng, f"${rem}$", [f"${next_cube - total}$", f"${total - (k - 1)**3}$", f"${cube}$"])
        return {
            "stem": (
                f"Z zestawu liczącego ${total}$ identycznych małych sześcianików ułożono największą możliwą bryłę "
                f"w kształcie pełnego sześcianu."
            ),
            "command": "Ile małych sześcianików nie zostało wykorzystanych do budowy tej bryły? Wybierz właściwą odpowiedź spośród podanych.",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Kolejne trzecie potęgi liczb naturalnych: $3^3=27, 4^3=64, 5^3=125, 6^3=216, 7^3=343$.",
                f"Największy pełny sześcian ma objętość ${k}^3 = {cube}$ klocków, więc zostało ${total} - {cube} = {rem}$ (odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    if mode == "cube_missing":
        k = rng.choice([4, 5, 6])
        next_cube = (k + 1) ** 3
        missing = rng.randint(14, 45)
        have = next_cube - missing
        choices, ans = shuffle_abcd(rng, f"${missing}$", [f"${have - k**3}$", f"${missing + k}$", f"${k + 1}$"])
        return {
            "stem": f"Modelarz ma ${have}$ jednakowych kostek o krawędzi $1$ cm i chce skleić z nich pełny sześcian o krawędzi ${k + 1}$ cm.",
            "command": "Ilu takich kostek mu brakuje? Wybierz właściwą odpowiedź spośród podanych.",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Pełny sześcian o krawędzi ${k + 1}$ cm składa się z $({k + 1})^3 = {next_cube}$ kostek.",
                f"Brakuje zatem ${next_cube} - {have} = {missing}$ kostek (odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    # square_tiles
    k = rng.choice([11, 12, 13, 14, 15])
    sq = k * k
    rem = rng.randint(7, 2 * k - 3)
    total = sq + rem
    choices, ans = shuffle_abcd(rng, f"${k}$", [f"${k + 1}$", f"${rem}$", f"${k - 1}$"])
    return {
        "stem": (
            f"Posadzkę kwadratowego tarasu wyłożono największą możliwą kwadratową mozaiką z jednakowych płytek. "
            f"Z kupionych ${total}$ płytek po ułożeniu mozaiki zostało niewykorzystanych mniej niż ${2 * k + 1}$ sztuk."
        ),
        "command": "Po ile płytek ułożono wzdłuż jednego boku tej kwadratowej mozaiki? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Szukamy największego kwadratu liczby naturalnej nieprzekraczającego ${total}$: ${k}^2 = {sq}$ (natomiast $({k+1})^2 = {(k+1)**2} > {total}$).",
            f"Wzdłuż jednego boku ułożono $\\sqrt{{{sq}}} = {k}$ płytek (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


# ===========================================================================
# 5. WYRAŻENIA ALGEBRAICZNE
# ===========================================================================

@register_template(
    template_id="wyrazenia_przeksztalcanie_wzoru_abcd",
    topic_id="wyrazenia_algebraiczne",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – wyznaczanie wielkości ze wzoru",
)
def gen_przeksztalcanie_wzoru(rng):
    variant = rng.choice(["trapez", "physics_force", "celsius", "harmonic_like"])
    if variant == "trapez":
        f_main = r"P = \frac{(a + b) \cdot h}{2}"
        correct = r"$b = \frac{2P}{h} - a$"
        wrongs = [r"$b = \frac{P}{2h} - a$", r"$b = 2Ph - a$", r"$b = \frac{2P - a}{h}$"]
        steps = [
            r"Mnożymy równanie $P = \frac{(a+b)h}{2}$ obustronnie przez $2$: $2P = (a + b)h$.",
            r"Dzielimy przez $h$ i odejmujemy $a$: $b = \frac{2P}{h} - a$.",
        ]
        var_ask, desc = "b", "pole trapezu o podstawach $a, b$ i wysokości $h$"
    elif variant == "physics_force":
        k = rng.choice([2, 3, 4])
        f_main = rf"W = {k}p \cdot t + q"
        correct = rf"$t = \frac{{W - q}}{{{k}p}}$"
        wrongs = [rf"$t = \frac{{W}}{{{k}p}} - q$", rf"$t = \frac{{W + q}}{{{k}p}}$", rf"$t = {k}p(W - q)$"]
        steps = [
            rf"Odejmujemy $q$ od obu stron wzoru $W = {k}pt + q$: $W - q = {k}pt$.",
            rf"Dzielimy obie strony przez ${k}p$: $t = \frac{{W - q}}{{{k}p}}$.",
        ]
        var_ask, desc = "t", "zależność między dodatnimi wielkościami $W, p, t, q$"
    elif variant == "celsius":
        c0 = rng.choice([25, 32, 40])
        m = rng.choice([2, 5])
        f_main = rf"T = {m}(x - {c0})"
        correct = rf"$x = \frac{{T}}{{{m}}} + {c0}$"
        wrongs = [rf"$x = \frac{{T + {c0}}}{{{m}}}$", rf"$x = \frac{{T}}{{{m}}} - {c0}$", rf"$x = {m}T + {c0}$"]
        steps = [
            rf"Dzielimy obie strony równania $T = {m}(x - {c0})$ przez ${m}$: $\frac{{T}}{{{m}}} = x - {c0}$.",
            rf"Dodajemy ${c0}$ do obu stron: $x = \frac{{T}}{{{m}}} + {c0}$.",
        ]
        var_ask, desc = "x", "przelicznik wskazań czujnika pomiarowego"
    else:
        k = rng.choice([3, 4, 6])
        f_main = rf"V = \frac{{S \cdot H}}{{{k}}}"
        correct = rf"$H = \frac{{{k}V}}{{S}}$"
        wrongs = [rf"$H = \frac{{V}}{{{k}S}}$", rf"$H = {k}VS$", rf"$H = \frac{{S}}{{{k}V}}$"]
        steps = [
            rf"Mnożymy obie strony wzoru przez ${k}$: ${k}V = S \cdot H$.",
            rf"Dzielimy przez $S$ ($S > 0$): $H = \frac{{{k}V}}{{S}}$.",
        ]
        var_ask, desc = "H", "objętość bryły o polu podstawy $S$ i wysokości $H$"

    choices, ans = shuffle_abcd(rng, correct, wrongs)
    return {
        "stem": f"Dany jest wzór opisujący {desc}:\n${f_main}$.",
        "command": f"Którym równaniem poprawnie wyznaczono wielkość ${var_ask}$ z tego wzoru? Wybierz właściwą odpowiedź spośród podanych.",
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
    cke_ref="Styl CKE – obliczanie wartości i przekształcanie wzoru z parametrem n",
)
def gen_wzor_suma_kolejnych(rng):
    variant = rng.choice(["diagonals", "handshakes", "tiles_border"])
    if variant == "diagonals":
        n_val = rng.choice([10, 12, 15, 20])
        d_val = n_val * (n_val - 3) // 2
        d_bad = n_val * (n_val - 1) // 2
        f_stem = r"d = \frac{n(n - 3)}{2}"
        stem = f"Liczbę $d$ wszystkich przekątnych $n$-kąta wypukłego ($n \\ge 4$) wyraża wzór:\n${f_stem}$."
        p1_pref = f"Liczba wszystkich przekątnych {n_val}-kąta wypukłego jest równa"
        f_good = r"$d = \frac{1}{2}n^2 - \frac{3}{2}n$"
        f_bad = r"$d = \frac{1}{2}n^2 - 3$"
        s1_expl = f"Dla $n={n_val}$: $d = \\frac{{{n_val} \\cdot ({n_val}-3)}}{{2}} = {d_val}$"
    elif variant == "handshakes":
        n_val = rng.choice([12, 16, 20, 25])
        d_val = n_val * (n_val - 1) // 2
        d_bad = n_val * (n_val + 1) // 2
        f_stem = r"M = \frac{1}{2}k(k - 1)"
        stem = f"W turnieju szachowym rozgrywanym systemem „każdy z każdym” przy $k$ uczestnikach łączna liczba partii wynosi:\n${f_stem}$."
        p1_pref = f"Przy udziale ${n_val}$ zawodników łączna liczba rozegranych partii wynosi"
        f_good = r"$M = \frac{1}{2}k^2 - \frac{1}{2}k$"
        f_bad = r"$M = \frac{1}{2}k^2 - 1$"
        s1_expl = f"Dla $k={n_val}$: $M = \\frac{{1}}{{2}} \\cdot {n_val} \\cdot {n_val - 1} = {d_val}$"
    else:
        n_val = rng.choice([15, 20, 30, 40])
        d_val = n_val * (n_val + 2)
        d_bad = n_val * n_val + 2
        f_stem = r"L = n(n + 2)"
        stem = f"Liczba $L$ elementów w $n$-tym etapie pewnej mozaiki geometrycznej jest opisana wzorem:\n${f_stem}$."
        p1_pref = f"W ${n_val}$-tym etapie mozaika składa się z liczby elementów równej"
        f_good = r"$L = n^2 + 2n$"
        f_bad = r"$L = n^2 + 2$"
        s1_expl = f"Dla $n={n_val}$: $L = {n_val} \\cdot ({n_val}+2) = {pl_num(d_val)}$"

    if rng.random() < 0.5:
        opts1, a1 = {"A": f"${pl_num(d_val)}$", "B": f"${pl_num(d_bad)}$"}, "A"
    else:
        opts1, a1 = {"A": f"${pl_num(d_bad)}$", "B": f"${pl_num(d_val)}$"}, "B"

    if rng.random() < 0.5:
        opts2, a2 = {"C": f_good, "D": f_bad}, "C"
    else:
        opts2, a2 = {"C": f_bad, "D": f_good}, "D"

    return {
        "stem": stem,
        "command": "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D.",
        "ab_cd_parts": [
            {"prefix": p1_pref, "suffix": ".", "options": opts1},
            {"prefix": "Podany wzór po poprawnym wymnożeniu nawiasu przyjmuje postać", "suffix": ".", "options": opts2},
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"{s1_expl} (**{a1}**).",
            f"Mnożymy każdy wyraz w nawiasie przez czynnik przed nawiasem, uzyskując {f_good} (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna para odpowiedzi.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


# ===========================================================================
# 6. RÓWNANIA I ZADANIA TEKSTOWE
# ===========================================================================

@register_template(
    template_id="rownania_puszki_zabraklo_zostalo_2pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – równanie z nadwyżką i niedoborem kwoty",
)
def gen_puszki_zabraklo(rng):
    ctx = rng.choice([
        ("Kamil", "biletów ulgowych do planetarium", "jeden taki bilet"),
        ("Pani Ewa", "sadzonek wrzosu na rabatę", "jedna sadzonka"),
        ("Wiktor", "zeszytów w twardej oprawie", "jeden taki zeszyt"),
        ("Koło teatralne", "identycznych rekwizytów scenicznych", "jeden rekwizyt"),
        ("Klub pływacki", "czepków silikonowych dla zawodników", "jeden czepek"),
    ])
    who, items_gen, item_nom = ctx
    n_more, n_less = rng.choice([(11, 7), (12, 8), (10, 6), (9, 5), (14, 9), (15, 10)])
    price_gr = rng.choice([450, 550, 650, 850, 1150, 1350, 1600])
    rem_gr = rng.choice([300, 450, 600, 750, 900])
    have_gr = n_less * price_gr + rem_gr
    lack_gr = n_more * price_gr - have_gr

    price_zl = price_gr / 100
    lack_zl = lack_gr / 100
    rem_zl = rem_gr / 100
    ask_budget = rng.choice([False, True])

    if not ask_budget:
        cmd = f"Oblicz, ile kosztuje {item_nom}. Zapisz obliczenia."
        ans = f"{pl_num(price_zl)} zł"
        final_step = f"Stąd ${n_more - n_less}x = {pl_num(lack_zl + rem_zl)}$, czyli cena wynosi $x = {pl_num(price_zl)}$ zł."
    else:
        budget_zl = have_gr / 100
        cmd = f"Oblicz, jaką kwotą dysponuje {who.lower() if who.startswith('Koło') or who.startswith('Klub') else who}. Zapisz obliczenia."
        ans = f"{pl_num(budget_zl)} zł"
        final_step = f"Stąd $x = {pl_num(price_zl)}$ zł, a posiadana kwota to ${n_less} \\cdot {pl_num(price_zl)} + {pl_num(rem_zl)} = {pl_num(budget_zl)}$ zł."

    return {
        "stem": (
            f"Przy zakupie ${n_more}$ jednakowych {items_gen} do zapłaty zabrakłoby kwoty ${pl_num(lack_zl)}$ zł. "
            f"Natomiast po zakupie ${n_less}$ takich samych sztuk w portfelu pozostaje jeszcze ${pl_num(rem_zl)}$ zł reszty."
        ),
        "command": cmd,
        "correct_answer": ans,
        "solution_steps": [
            f"Oznaczmy przez $x$ cenę jednostkową (w zł). Posiadana kwota to z jednej strony ${n_more}x - {pl_num(lack_zl)}$, a z drugiej ${n_less}x + {pl_num(rem_zl)}$.",
            f"Z równania ${n_more}x - {pl_num(lack_zl)} = {n_less}x + {pl_num(rem_zl)}$ mamy: {final_step}",
        ],
        "scoring_scheme": [
            "1 pkt – ułożenie poprawnego równania z jedną niewiadomą lub poprawne wyznaczenie ceny jednostkowej.",
            f"2 pkt – pełne obliczenia i podanie poprawnej odpowiedzi: {ans}.",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="rownania_origami_cztery_kolory_2pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – podział zbioru na cztery części z ułamkiem i różnicą",
)
def gen_origami_kolory(rng):
    ctx = rng.choice([
        ("W szkolnej wypożyczalni sprzętu zimowego przygotowano", "par nart", "dziecięcych", "młodzieżowych", "biegowych", "zjazdowych"),
        ("W magazynie sklepu muzycznego zinwentaryzowano", "instrumentów", "smyczkowych", "klawiszowych", "dętych", "perkusyjnych"),
        ("Na kiermasz charytatywny upieczono", "babeczek", "waniliowych", "czekoladowych", "malinowych", "cytrynowych"),
        ("W kolekcji geologicznej muzeum skatalogowano", "minerałów", "kwarcowych", "wapiennych", "krzemianowych", "rudnych"),
    ])
    intro, noun_gen, g_fixed, g_mult, g_base, g_off = ctx

    mult_choice = rng.choice([Fraction(3, 2), Fraction(5, 2), Fraction(2, 1)])
    x_base = rng.choice([18, 22, 26, 30, 34, 38])  # parzyste -> mult * x_base całkowite
    cnt_mult = int(mult_choice * x_base)
    offset = rng.choice([6, 9, 11, 14])
    is_more = rng.choice([True, False])
    cnt_off = x_base + offset if is_more else x_base - offset
    cnt_fixed = rng.choice([20, 27, 33, 41])
    total = cnt_fixed + cnt_mult + x_base + cnt_off

    mult_txt = "$2$ razy" if mult_choice == 2 else f"${pl_num(float(mult_choice))}$ raza"
    rel_txt = f"o ${offset}$ więcej" if is_more else f"o ${offset}$ mniej"
    op_sign = "+" if is_more else "-"

    return {
        "stem": (
            f"{intro} łącznie ${total}$ {noun_gen} podzielonych na cztery grupy: "
            f"{g_fixed}, {g_mult}, {g_base} oraz {g_off}. W grupie {g_fixed} jest dokładnie ${cnt_fixed}$ sztuk. "
            f"Sztuk {g_mult} jest {mult_txt} więcej niż {g_base}, a sztuk {g_off} – {rel_txt} niż {g_base}."
        ),
        "command": f"Oblicz, ile sztuk należy do grupy {g_mult}. Zapisz obliczenia.",
        "correct_answer": f"{cnt_mult}",
        "solution_steps": [
            f"Niech $x$ oznacza liczbę sztuk {g_base}. Wtedy sztuk {g_mult} jest ${pl_num(float(mult_choice))}x$, a sztuk {g_off}: $x {op_sign} {offset}$.",
            f"Równanie sumy: ${cnt_fixed} + {pl_num(float(mult_choice))}x + x + (x {op_sign} {offset}) = {total}$, skąd ${pl_num(float(mult_choice) + 2)}x = {total - cnt_fixed - (offset if is_more else -offset)}$, czyli $x = {x_base}$.",
            f"Liczba sztuk {g_mult}: ${pl_num(float(mult_choice))} \\cdot {x_base} = {cnt_mult}$.",
        ],
        "scoring_scheme": [
            "1 pkt – poprawne zapisanie równania opisującego łączną liczbę elementów.",
            f"2 pkt – wyznaczenie $x = {x_base}$ oraz obliczenie szukanej grupy: {cnt_mult}.",
        ],
        "grid_height_mm": 54.0,
    }


# ===========================================================================
# 7. PRĘDKOŚĆ, DROGA, CZAS
# ===========================================================================

@register_template(
    template_id="predkosc_wykres_drogi_pf",
    topic_id="predkosc_droga_czas",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – odczytywanie wykresu ruchu z postojem",
    has_diagram=True,
)
def gen_wykres_drogi(rng):
    who = rng.choice([
        ("Turysta na hulajnodze elektrycznej", "przystani"),
        ("Kajakarka płynąca w dół rzeki", "pomostu startowego"),
        ("Kurier rowerowy", "bazy przeładunkowej"),
    ])
    v1 = rng.choice([10, 12, 15, 18, 20])
    t1 = rng.choice([1, 2])
    d1 = v1 * t1
    t_stop = rng.choice([1, 2])
    v2 = rng.choice([10, 15, 20, 25])
    t2 = 2
    d2 = d1 + v2 * t2

    s1_true = rng.choice([True, False])
    v_claim = v1 if s1_true else v2 if v2 != v1 else v1 + 5

    s2_true = rng.choice([True, False])
    total_t = t1 + t_stop + t2
    avg_all_true = Fraction(d2, total_t)
    stop_min_true = t_stop * 60
    stop_claim = stop_min_true if s2_true else stop_min_true + 30

    p1_ans = "P" if s1_true else "F"
    p2_ans = "P" if s2_true else "F"

    return {
        "stem": (
            f"{who[0]} oddalał(a) się od {who[1]}. Na wykresie przedstawiono zależność przebytej odległości "
            f"od czasu liczonego od chwili startu."
        ),
        "diagram": DiagramSpec(
            kind="travel_graph",
            params={
                "times": [0, t1, t1 + t_stop, total_t],
                "dists": [0, d1, d1, d2],
                "xlabel": "Czas [h]",
                "ylabel": "Odległość [km]",
                "x_step": 1,
                "y_step": 10,
            },
            width_mm=88.0,
        ),
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Na pierwszym etapie przed postojem średnia prędkość wynosiła ${v_claim}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$.", p1_ans),
            (f"Przerwa w ruchu (postój) trwała dokładnie ${stop_claim}$ minut.", p2_ans),
        ],
        "correct_answer": f"{p1_ans}{p2_ans}",
        "solution_steps": [
            f"W ciągu pierwszych ${t1}\\text{{ h}}$ pokonano ${d1}\\text{{ km}}$, zatem prędkość wynosiła ${d1} : {t1} = {v1}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$ (zdanie 1.: **{p1_ans}**).",
            f"Poziomy odcinek wykresu trwa od ${t1}\\text{{ h}}$ do ${t1 + t_stop}\\text{{ h}}$, czyli ${t_stop}\\text{{ h}} = {stop_min_true}\\text{{ min}}$ (zdanie 2.: **{p2_ans}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="predkosc_uzasadnij_dluzej_niz_godzina_3pkt",
    topic_id="predkosc_droga_czas",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Styl CKE – uzasadnienie czasu przejazdu na trasie dwuetapowej",
)
def gen_uzasadnij_czas_przejazdu(rng):
    t1_min, frac_h = rng.choice([(20, Fraction(1, 3)), (30, Fraction(1, 2)), (40, Fraction(2, 3)), (45, Fraction(3, 4))])
    v = rng.choice([48, 60, 72, 84, 96])
    d1 = int(v * frac_h)
    threshold_h = rng.choice([1, 2])
    is_longer = rng.choice([True, False])
    delta = rng.choice([4, 6, 8, 10])
    d2 = threshold_h * v + delta if is_longer else threshold_h * v - delta
    d_total = d1 + d2

    route = rng.choice([
        ("pociąg regionalny", "stacji *Klonowo*", "stacji *Grotowice*", "stację węzłową *Bystra*"),
        ("autokar wycieczkowy", "miejscowości *Zalesie*", "przystani *Nadbrzeże*", "punkt widokowy *Skałka*"),
        ("samochód dostawczy", "magazynu w *Olszynie*", "hurtowni w *Kamieńcu*", "punkt odbioru w *Rudnikach*"),
    ])
    veh, p_start, p_end, p_mid = route
    cmp_word = "dłużej" if is_longer else "krócej"
    h_word = "jedną godzinę" if threshold_h == 1 else "dwie godziny"
    ineq = ">" if is_longer else "<"

    return {
        "stem": (
            f"Trasa z {p_start} do {p_end} prowadzi przez {p_mid} i liczy łącznie ${d_total}$ km. "
            f"Pierwszy odcinek (od {p_start} do punktu pośredniego) ma długość ${d1}$ km i {veh} pokonał go "
            f"w czasie ${t1_min}$ minut. Drugi odcinek trasy pojazd przejechał z taką samą średnią prędkością jak pierwszy."
        ),
        "command": f"Uzasadnij, że przejazd drugiego odcinka trasy trwał {cmp_word} niż {h_word}. Zapisz obliczenia.",
        "correct_answer": f"v = {v} km/h, drugi odcinek {d2} km {ineq} {threshold_h * v} km",
        "solution_steps": [
            f"Zamieniamy czas pierwszego odcinka na godziny: ${t1_min}\\text{{ min}} = \\frac{{{t1_min}}}{{60}}\\text{{ h}} = \\frac{{{frac_h.numerator}}}{{{frac_h.denominator}}}\\text{{ h}}$.",
            f"Obliczamy średnią prędkość pojazdu: $v = {d1} : \\frac{{{frac_h.numerator}}}{{{frac_h.denominator}}} = {v}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$.",
            f"Długość drugiego odcinka wynosi: ${d_total} - {d1} = {d2}\\text{{ km}}$.",
            f"W czasie ${threshold_h}\\text{{ h}}$ przy prędkości ${v}\\;\\frac{{\\text{{km}}}}{{\\text{{h}}}}$ pojazd pokonuje ${threshold_h * v}\\text{{ km}}$. Ponieważ ${d2}\\text{{ km}} {ineq} {threshold_h * v}\\text{{ km}}$, przejazd trwał {cmp_word} niż {h_word}.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie długości drugiego odcinka ({d2} km) lub wyrażenie {t1_min} min w godzinach.",
            f"2 pkt – poprawne wyznaczenie średniej prędkości pojazdu ({v} km/h).",
            "3 pkt – pełne obliczenia wraz z jednoznacznym porównaniem prowadzącym do tezy.",
        ],
        "grid_height_mm": 58.0,
    }


# ===========================================================================
# 8. UKŁAD WSPÓŁRZĘDNYCH
# ===========================================================================

@register_template(
    template_id="wspolrzedne_przesuniecie_punktu_abcd",
    topic_id="uklad_wspolrzednych",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – zmiana współrzędnych i symetria na kratce",
    has_diagram=True,
)
def gen_przesuniecie_punktu(rng):
    x1 = rng.choice([-4, -3, -2, 2, 3])
    y1 = rng.choice([-3, -2, 2, 3])
    dx = rng.choice([-4, -3, 3, 4]) if x1 > 0 else rng.choice([3, 4, 5])
    dy = rng.choice([-4, -3, 3, 4]) if y1 > 0 else rng.choice([3, 4, 5])
    if x1 + dx == x1 or abs(x1 + dx) > 5:
        dx = -x1 + rng.choice([-1, 2])
    if abs(y1 + dy) > 5:
        dy = -y1 + rng.choice([1, -2])

    target = (x1 + dx, y1 + dy)
    cands = [
        (x1 - dx if abs(x1 - dx) <= 5 else -target[0], target[1]),
        (target[1], target[0]),
        (target[0], -target[1] if target[1] != 0 else target[1] + 2),
        (-x1, -y1),
    ]
    w_pts = []
    for c in cands:
        if c != target and c != (x1, y1) and c not in w_pts and abs(c[0]) <= 5 and abs(c[1]) <= 5:
            w_pts.append(c)
    while len(w_pts) < 3:
        cand = (rng.randint(-5, 5), rng.randint(-5, 5))
        if cand not in w_pts and cand != target and cand != (x1, y1):
            w_pts.append(cand)
    w_pts = w_pts[:3]

    labels = ["K", "L", "M", "N"]
    coords_4 = [target] + w_pts
    rng.shuffle(coords_4)
    correct_idx = coords_4.index(target)
    correct_lbl = f"${labels[correct_idx]}$"

    pts_diag = [{"x": x1, "y": y1, "label": "S"}]
    for idx, (px, py) in enumerate(coords_4):
        pts_diag.append({"x": px, "y": py, "label": labels[idx]})

    choices = {L: f"${labels[i]}$" for i, L in enumerate(["A", "B", "C", "D"])}
    ans = ["A", "B", "C", "D"][correct_idx]

    x_act = f"zwiększymy o ${dx}$" if dx > 0 else f"zmniejszymy o ${abs(dx)}$"
    y_act = f"zwiększymy o ${dy}$" if dy > 0 else f"zmniejszymy o ${abs(dy)}$"

    return {
        "stem": (
            f"W układzie współrzędnych $(x, y)$ zaznaczono punkt początkowy $S = ({pl_num(x1)}, {pl_num(y1)})$ "
            f"oraz cztery punkty: $K, L, M$ i $N$ (zobacz rysunek)."
        ),
        "diagram": DiagramSpec(kind="coord_plane", params={"limit": 6, "points": pts_diag}, width_mm=72.0),
        "command": (
            f"Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\n"
            f"Jeżeli odciętą ($x$) punktu $S$ {x_act}, a rzędną ($y$) punktu $S$ {y_act}, to otrzymamy punkt"
        ),
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Nowa odcięta: $x = {pl_num(x1)} {'+' if dx > 0 else '-'} {abs(dx)} = {pl_num(target[0])}$. Nowa rzędna: $y = {pl_num(y1)} {'+' if dy > 0 else '-'} {abs(dy)} = {pl_num(target[1])}$.",
            f"Współrzędne $({pl_num(target[0])}, {pl_num(target[1])})$ ma na rysunku punkt {correct_lbl} (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="wspolrzedne_pole_trapezu_2pkt",
    topic_id="uklad_wspolrzednych",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – pole czworokąta w układzie współrzędnych",
    has_diagram=True,
)
def gen_pole_trapezu_uklad(rng):
    shape = rng.choice(["trapez", "rownoleglobok"])
    y_bot = rng.choice([-4, -3, -2])
    h = rng.choice([3, 4, 5, 6])
    y_top = y_bot + h

    if shape == "trapez":
        a = rng.choice([5, 6, 7, 8])
        b = rng.choice([2, 3, 4])
        if (a + b) * h % 2 != 0:
            b += 1
        x_a = rng.choice([-4, -3])
        x_b = x_a + a
        x_d = rng.choice([-2, -1, 0])
        x_c = x_d + b
        area = (a + b) * h // 2
        fig_name = "trapezu $ABCD$"
        steps = [
            f"Podstawy równoległe do osi $Ox$ mają długości: $|AB| = {x_b} - ({pl_num(x_a)}) = {a}$ oraz $|CD| = {x_c} - ({pl_num(x_d)}) = {b}$.",
            f"Wysokość wynosi $h = {pl_num(y_top)} - ({pl_num(y_bot)}) = {h}$, skąd $P = \\frac{{({a} + {b}) \\cdot {h}}}{{2}} = {area}$.",
        ]
    else:
        a = rng.choice([4, 5, 6, 7])
        shift = rng.choice([1, 2, -2])
        x_a = -3
        x_b = x_a + a
        x_d = x_a + shift
        x_c = x_b + shift
        area = a * h
        fig_name = "równoległoboku $ABCD$"
        steps = [
            f"Podstawa równoległa do osi $Ox$ ma długość $|AB| = {x_b} - ({pl_num(x_a)}) = {a}$.",
            f"Wysokość opuszczona na tę podstawę wynosi $h = {pl_num(y_top)} - ({pl_num(y_bot)}) = {h}$, zatem $P = {a} \\cdot {h} = {area}$.",
        ]

    poly = [[x_a, y_bot], [x_b, y_bot], [x_c, y_top], [x_d, y_top]]
    pts = [
        {"x": x_a, "y": y_bot, "label": "A", "dx": -0.4, "dy": -0.4},
        {"x": x_b, "y": y_bot, "label": "B", "dx": 0.4, "dy": -0.4},
        {"x": x_c, "y": y_top, "label": "C", "dx": 0.4, "dy": 0.4},
        {"x": x_d, "y": y_top, "label": "D", "dx": -0.4, "dy": 0.4},
    ]

    return {
        "stem": (
            f"W układzie współrzędnych $(x, y)$ zaznaczono wierzchołki {fig_name}: "
            f"$A = ({pl_num(x_a)}, {pl_num(y_bot)})$, $B = ({pl_num(x_b)}, {pl_num(y_bot)})$, "
            f"$C = ({pl_num(x_c)}, {pl_num(y_top)})$ oraz $D = ({pl_num(x_d)}, {pl_num(y_top)})$."
        ),
        "diagram": DiagramSpec(kind="coord_plane", params={"limit": 6, "polygon": poly, "points": pts}, width_mm=74.0),
        "command": f"Oblicz pole {fig_name}. Zapisz obliczenia.",
        "correct_answer": f"{area}",
        "solution_steps": steps,
        "scoring_scheme": [
            "1 pkt – poprawne odczytanie długości podstawy/podstaw i wysokości czworokąta.",
            f"2 pkt – poprawne obliczenie pola figury: {area}.",
        ],
        "grid_height_mm": 50.0,
    }


# ===========================================================================
# 9. GEOMETRIA PŁASKA
# ===========================================================================

@register_template(
    template_id="planimetria_trojkat_rownoboczny_pf",
    topic_id="geometria_plaska",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – własności trójkąta równobocznego i kwadratu",
)
def gen_trojkat_rownoboczny_pf(rng):
    fig = rng.choice(["equilateral", "hexagon", "square_diag"])
    if fig == "equilateral":
        a = rng.choice([4, 6, 8, 10, 12, 14])
        h_c = a // 2
        p_c = (a * a) // 4
        s1_true = rng.choice([True, False])
        s2_true = rng.choice([True, False])
        h_str = rf"{h_c}\sqrt{{3}}" if s1_true else rf"{a}\sqrt{{3}}"
        p_str = rf"{p_c}\sqrt{{3}}" if s2_true else rf"{(a * a) // 2}\sqrt{{3}}"
        a1, a2 = ("P" if s1_true else "F"), ("P" if s2_true else "F")
        return {
            "stem": f"Obwód pewnego trójkąta równobocznego jest równy ${3 * a}$ cm.",
            "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
            "pf_statements": [
                (f"Wysokość tego trójkąta ma długość ${h_str}$ cm.", a1),
                (f"Pole tego trójkąta jest równe ${p_str}\\text{{ cm}}^2$.", a2),
            ],
            "correct_answer": f"{a1}{a2}",
            "solution_steps": [
                f"Bok trójkąta wynosi $a = {3 * a} : 3 = {a}\\text{{ cm}}$, więc $h = \\frac{{{a}\\sqrt{{3}}}}{{2}} = {h_c}\\sqrt{{3}}\\text{{ cm}}$ (**{a1}**).",
                f"Pole trójkąta wynosi $P = \\frac{{{a}^2\\sqrt{{3}}}}{{4}} = {p_c}\\sqrt{{3}}\\text{{ cm}}^2$ (**{a2}**).",
            ],
            "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
        }

    if fig == "hexagon":
        a = rng.choice([4, 6, 8, 10])
        p_c = 6 * (a * a) // 4
        s1_true = rng.choice([True, False])
        s2_true = rng.choice([True, False])
        d_str = f"${2 * a}$" if s1_true else rf"${a}\sqrt{{3}}$"
        p_str = rf"${p_c}\sqrt{{3}}$" if s2_true else rf"${(a * a) // 4}\sqrt{{3}}$"
        a1, a2 = ("P" if s1_true else "F"), ("P" if s2_true else "F")
        return {
            "stem": f"Dany jest sześciokąt foremny o boku długości ${a}$ cm.",
            "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
            "pf_statements": [
                (f"Najdłuższa przekątna tego sześciokąta ma długość {d_str} cm.", a1),
                (f"Pole tego sześciokąta jest równe {p_str} $\\text{{cm}}^2$.", a2),
            ],
            "correct_answer": f"{a1}{a2}",
            "solution_steps": [
                f"Najdłuższa przekątna sześciokąta foremnego ma długość $2a = {2 * a}\\text{{ cm}}$ (**{a1}**).",
                f"Sześciokąt składa się z $6$ trójkątów równobocznych: $P = 6 \\cdot \\frac{{{a}^2\\sqrt{{3}}}}{{4}} = {p_c}\\sqrt{{3}}\\text{{ cm}}^2$ (**{a2}**).",
            ],
            "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
        }

    # square_diag
    a = rng.choice([5, 6, 7, 9, 11])
    s1_true = rng.choice([True, False])
    s2_true = rng.choice([True, False])
    obw_str = f"${4 * a}$" if s1_true else rf"${4 * a}\sqrt{{2}}$"
    area_str = f"${a * a}$" if s2_true else f"${2 * a * a}$"
    a1, a2 = ("P" if s1_true else "F"), ("P" if s2_true else "F")
    return {
        "stem": rf"Przekątna pewnego kwadratu ma długość ${a}\sqrt{{2}}$ cm.",
        "command": "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe.",
        "pf_statements": [
            (f"Obwód tego kwadratu jest równy {obw_str} cm.", a1),
            (f"Pole tego kwadratu jest równe {area_str} $\\text{{cm}}^2$.", a2),
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"Skoro $d = a\\sqrt{{2}} = {a}\\sqrt{{2}}\\text{{ cm}}$, to bok kwadratu ma długość $a = {a}\\text{{ cm}}$, a obwód $4a = {4 * a}\\text{{ cm}}$ (**{a1}**).",
            f"Pole kwadratu wynosi $a^2 = {a * a}\\text{{ cm}}^2$ (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – obie odpowiedzi poprawne.", "0 pkt – odpowiedź niepełna lub błędna."],
    }


@register_template(
    template_id="planimetria_romb_przekatne_3pkt",
    topic_id="geometria_plaska",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Styl CKE – przekątne, obwód i wysokość rombu",
    has_diagram=True,
)
def gen_romb_przekatne(rng):
    half_e, half_f, side = rng.choice([(12, 5, 13), (8, 6, 10), (15, 8, 17), (12, 9, 15), (16, 12, 20), (24, 7, 25)])
    obw = 4 * side
    diag_ac = 2 * half_e
    diag_bd = 2 * half_f
    area = (diag_ac * diag_bd) // 2

    given_diags = rng.choice([True, False])
    if given_diags:
        cmd = "Oblicz obwód rombu $ABCD$. Zapisz obliczenia."
        ans_str = f"{obw} cm"
        stem = f"Przekątne rombu $ABCD$ mają długości $|AC| = {diag_ac}$ cm oraz $|BD| = {diag_bd}$ cm (zobacz rysunek)."
        steps = [
            f"Przekątne rombu przecinają się pod kątem prostym i dzielą na połowy: $|AS| = {half_e}\\text{{ cm}}$ oraz $|BS| = {half_f}\\text{{ cm}}$.",
            f"Z twierdzenia Pitagorasa w trójkącie $ABS$: $|AB|^2 = {half_e}^2 + {half_f}^2 = {half_e**2} + {half_f**2} = {side**2}$, więc $|AB| = {side}\\text{{ cm}}$.",
            f"Obwód rombu wynosi $4 \\cdot {side} = {obw}\\text{{ cm}}$.",
        ]
    else:
        ask_area = rng.choice([True, False])
        stem = f"Obwód rombu $ABCD$ jest równy ${obw}$ cm, a przekątna $AC$ ma długość ${diag_ac}$ cm (zobacz rysunek)."
        cmd = "Oblicz pole rombu $ABCD$. Zapisz obliczenia." if ask_area else "Oblicz długość przekątnej $BD$ tego rombu. Zapisz obliczenia."
        ans_str = f"{area} cm^2" if ask_area else f"{diag_bd} cm"
        steps = [
            f"Bok rombu ma długość $a = {obw} : 4 = {side}\\text{{ cm}}$, a połowa znanej przekątnej $|AS| = {diag_ac} : 2 = {half_e}\\text{{ cm}}$.",
            f"Z twierdzenia Pitagorasa: $|BS|^2 = {side}^2 - {half_e}^2 = {half_f**2}$, skąd $|BS| = {half_f}\\text{{ cm}}$ oraz $|BD| = {diag_bd}\\text{{ cm}}$.",
        ]
        if ask_area:
            steps.append(f"Pole rombu: $P = \\frac{{{diag_ac} \\cdot {diag_bd}}}{{2}} = {area}\\text{{ cm}}^2$.")

    return {
        "stem": stem,
        "diagram": DiagramSpec(kind="rhombus_diagonals", params={"side_label": "", "ac_label": ""}, width_mm=72.0),
        "command": cmd,
        "correct_answer": ans_str,
        "solution_steps": steps,
        "scoring_scheme": [
            "1 pkt – wyznaczenie przyprostokątnych lub przeciwprostokątnej trójkąta prostokątnego utworzonego przez połowy przekątnych.",
            "2 pkt – poprawne zastosowanie twierdzenia Pitagorasa.",
            f"3 pkt – pełne rozwiązanie i poprawny wynik końcowy: {ans_str}.",
        ],
        "grid_height_mm": 58.0,
    }


# ===========================================================================
# 10. GEOMETRIA PRZESTRZENNA
# ===========================================================================

@register_template(
    template_id="stereometria_slupek_szescianow_abcd",
    topic_id="geometria_przestrzenna",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – pole powierzchni bryły sklejonej z sześcianów",
)
def gen_slupek_szescianow(rng):
    k = rng.choice([2, 3, 4, 5, 6])
    a = rng.choice([2, 3, 4, 5, 7])
    ask_diff = rng.choice([False, True])
    faces_exposed = 4 * k + 2
    area_glued = faces_exposed * (a * a)
    area_all = 6 * k * (a * a)
    diff_area = area_all - area_glued  # 2*(k-1)*a^2

    if not ask_diff:
        choices, ans = shuffle_abcd(
            rng,
            f"${pl_num(area_glued)}\\text{{ cm}}^2$",
            [f"${pl_num(area_all)}\\text{{ cm}}^2$", f"${pl_num(4 * k * a * a)}\\text{{ cm}}^2$", f"${pl_num(k * a**3)}\\text{{ cm}}^2$"],
        )
        return {
            "stem": (
                f"Ułożono obok siebie w jednym prostym rzędzie ${k}$ jednakowych kostek sześciennych o krawędzi ${a}$ cm "
                f"i sklejono je przystającymi ścianami w prostopadłościenną belkę."
            ),
            "command": "Jakie jest pole powierzchni całkowitej otrzymanej belki? Wybierz właściwą odpowiedź spośród podanych.",
            "choices": choices,
            "correct_answer": ans,
            "solution_steps": [
                f"Belka ma wymiary ${k * a}\\text{{ cm}} \\times {a}\\text{{ cm}} \\times {a}\\text{{ cm}}$ i składa się z $4 \\cdot {k} + 2 = {faces_exposed}$ kwadratowych pól o boku ${a}$ cm.",
                f"Pole całkowite wynosi ${faces_exposed} \\cdot {a}^2 = {pl_num(area_glued)}\\text{{ cm}}^2$ (odpowiedź **{ans}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
        }

    choices, ans = shuffle_abcd(
        rng,
        f"${pl_num(diff_area)}\\text{{ cm}}^2$",
        [f"${pl_num((k - 1) * a * a)}\\text{{ cm}}^2$", f"${pl_num(area_glued)}\\text{{ cm}}^2$", f"${pl_num(2 * k * a * a)}\\text{{ cm}}^2$"],
    )
    return {
        "stem": (
            f"Mamy ${k}$ jednakowych sześcianów o krawędzi ${a}$ cm. Sklejamy je w jeden prosty słupek, łącząc sąsiednie klocki "
            f"całymi ścianami."
        ),
        "command": (
            "O ile mniejsze jest pole powierzchni całkowitej sklejonego słupka od sumy pól powierzchni całkowitych "
            "wszystkich tych sześcianów przed sklejeniem? Wybierz właściwą odpowiedź spośród podanych."
        ),
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Przy ${k}$ klockach w rzędzie występuje ${k - 1}$ miejsc sklejenia, a każde sklejenie zakrywa $2$ kwadratowe ściany.",
            f"Ubywa więc $2 \\cdot {k - 1} = {2 * (k - 1)}$ ścian o polu ${a}^2 = {a * a}\\text{{ cm}}^2$, czyli ${pl_num(diff_area)}\\text{{ cm}}^2$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="stereometria_wieze_szescian_ostroslup_2pkt",
    topic_id="geometria_przestrzenna",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – porównywanie objętości i wysokości graniastosłupa oraz ostrosłupa",
)
def gen_wieze_ostroslup(rng):
    variant = rng.choice(["same_vol", "composite_monument"])
    if variant == "same_vol":
        a_prism = rng.choice([4, 6, 8])
        h_prism = rng.choice([5, 6, 9, 10])
        vol = a_prism * a_prism * h_prism
        a_pyr = rng.choice([6, 8, 12])
        while (3 * vol) % (a_pyr * a_pyr) != 0:
            a_pyr = a_prism
        h_pyr = (3 * vol) // (a_pyr * a_pyr)
        return {
            "stem": (
                f"Graniastosłup prawidłowy czworokątny o krawędzi podstawy ${a_prism}$ cm i wysokości ${h_prism}$ cm "
                f"ma dokładnie taką samą objętość jak pewien ostrosłup prawidłowy czworokątny o krawędzi podstawy ${a_pyr}$ cm."
            ),
            "command": "Oblicz wysokość tego ostrosłupa. Zapisz obliczenia.",
            "correct_answer": f"{h_pyr} cm",
            "solution_steps": [
                f"Objętość graniastosłupa: $V = {a_prism}^2 \\cdot {h_prism} = {pl_num(vol)}\\text{{ cm}}^3$.",
                f"Pole podstawy ostrosłupa to $P_p = {a_pyr}^2 = {a_pyr * a_pyr}\\text{{ cm}}^2$. Z równania $\\frac{{1}}{{3}} \\cdot {a_pyr * a_pyr} \\cdot H = {pl_num(vol)}$ otrzymujemy $H = {h_pyr}\\text{{ cm}}$.",
            ],
            "scoring_scheme": [
                f"1 pkt – poprawne obliczenie objętości graniastosłupa ({pl_num(vol)} cm^3).",
                f"2 pkt – wyznaczenie wysokości ostrosłupa: {h_pyr} cm.",
            ],
            "grid_height_mm": 50.0,
        }

    a_base = rng.choice([6, 9, 12])
    h_cube_part = rng.choice([8, 10, 14])
    h_pyr = rng.choice([6, 9, 12, 15])
    v_prism = a_base * a_base * h_cube_part
    v_pyr = (a_base * a_base * h_pyr) // 3
    v_tot = v_prism + v_pyr
    return {
        "stem": (
            f"Drewniany słupek ogrodowy składa się z graniastosłupa prawidłowego czworokątnego o krawędzi podstawy ${a_base}$ cm "
            f"i wysokości ${h_cube_part}$ cm oraz osadzonego na jego górnej podstawie ostrosłupa prawidłowego czworokątnego "
            f"o takiej samej podstawie. Całkowita objętość tego słupka wynosi ${pl_num(v_tot)}\\text{{ cm}}^3$."
        ),
        "command": "Oblicz całkowitą wysokość tego słupka ogrodowego. Zapisz obliczenia.",
        "correct_answer": f"{h_cube_part + h_pyr} cm",
        "solution_steps": [
            f"Objętość części graniastosłupowej: $V_1 = {a_base}^2 \\cdot {h_cube_part} = {pl_num(v_prism)}\\text{{ cm}}^3$, więc objętość części ostrosłupowej to $V_2 = {pl_num(v_tot)} - {pl_num(v_prism)} = {pl_num(v_pyr)}\\text{{ cm}}^3$.",
            f"Wysokość ostrosłupa z wzoru $\\frac{{1}}{{3}} \\cdot {a_base}^2 \\cdot h = {pl_num(v_pyr)}$ wynosi $h = {h_pyr}\\text{{ cm}}$, zatem wysokość całego słupka to ${h_cube_part} + {h_pyr} = {h_cube_part + h_pyr}\\text{{ cm}}$.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie objętości części ostrosłupowej ({pl_num(v_pyr)} cm^3).",
            f"2 pkt – wyznaczenie wysokości ostrosłupa ({h_pyr} cm) i wysokości całkowitej: {h_cube_part + h_pyr} cm.",
        ],
        "grid_height_mm": 52.0,
    }


# ===========================================================================
# 11. STATYSTYKA, TABELE I DIAGRAMY
# ===========================================================================

@register_template(
    template_id="statystyka_diagram_kolowy_abcd",
    topic_id="statystyka_diagramy",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – diagram kołowy z brakującym udziałem procentowym",
    has_diagram=True,
)
def gen_diagram_kolowy(rng):
    ctx = rng.choice([
        ("W ankiecie dotyczącej ulubionego gatunku filmowego wzięło udział", "uczniów", ["komedia", "przygodowy", "animacja", "fantastyka"]),
        ("W szkolnej bibliotece w ciągu miesiąca wypożyczono", "książek", ["powieści", "lektury", "popularnonauk.", "komiksy"]),
        ("Podczas zbiórki ekologicznej posegregowano", "kg surowców", ["makulatura", "szkło", "plastik", "metal"]),
        ("W sadzie posadzono łącznie", "drzewek owocowych", ["jabłonie", "grusze", "śliwy", "wiśnie"]),
    ])
    intro, unit_noun, cats = ctx
    total = rng.choice([60, 80, 120, 160, 200, 240])
    p1, p2, p3 = rng.choice([(35, 25, 15), (40, 20, 15), (30, 35, 20), (45, 25, 10), (30, 25, 20)])
    p4 = 100 - (p1 + p2 + p3)
    while (total * p4) % 100 != 0:
        total = 200
    val4 = (total * p4) // 100

    w1 = p4
    w2 = (total * p2) // 100
    w3 = val4 + rng.choice([6, 8, 12])
    choices, ans = shuffle_abcd(rng, f"${val4}$", [f"${w1}$", f"${w2}$", f"${w3}$"])

    return {
        "stem": (
            f"{intro} ${total}$ {unit_noun}. Na diagramie kołowym przedstawiono podział procentowy na cztery kategorie "
            f"(każda pozycja należy dokładnie do jednej kategorii)."
        ),
        "diagram": DiagramSpec(
            kind="pie_chart",
            params={"labels": cats, "percents": [p1, p2, p3, p4], "hide_percent_index": 3},
            width_mm=84.0,
        ),
        "command": f"Jaka wartość liczbowa odpowiada kategorii *{cats[3]}*? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Udział procentowy kategorii *{cats[3]}*: $100\\% - ({p1}\\% + {p2}\\% + {p3}\\%) = {p4}\\%$.",
            f"Szukana wartość: ${p4}\\% \\cdot {total} = \\frac{{{p4}}}{{100}} \\cdot {total} = {val4}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="statystyka_dzien_sportu_tabela_3pkt",
    topic_id="statystyka_diagramy",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Styl CKE – tabela dwudzielna z brakującą komórką i obliczeniem procentu",
)
def gen_dzien_sportu_tabela(rng):
    ctx = rng.choice([
        (
            "Uczniowie klas siódmych i ósmych zapisali się na dokładnie jedno koło zainteresowań",
            "Klasy ósme", "Klasy siódme",
            ["Koło robotyki", "Koło fotograficzne", "Koło astronomiczne"],
        ),
        (
            "Odwiedzający centrum nauki kupili bilety na dokładnie jeden z trzech pokazów specjalnych",
            "Bilety ulgowe", "Bilety normalne",
            ["Pokaz optyki", "Pokaz akustyki", "Pokaz magnetyzmu"],
        ),
        (
            "Uczestnicy obozu letniego wybrali dokładnie jedną sekcję warsztatową",
            "Grupa starsza", "Grupa młodsza",
            ["Żeglarstwo", "Łucznictwo", "Wspinaczka"],
        ),
    ])
    intro, row_a, row_b, cols = ctx
    total = rng.choice([160, 200, 250, 400])
    step_even = 10 if total in (250,) else 8
    diff_ab = rng.choice([step_even, 2 * step_even, 3 * step_even])
    tot_a = (total + diff_ab) // 2
    tot_b = total - tot_a

    b1 = rng.randint(tot_b // 4, tot_b // 3 + 6)
    b2 = rng.randint(tot_b // 5, tot_b // 3)
    b3 = tot_b - b1 - b2

    a1 = rng.randint(tot_a // 5, tot_a // 3)
    a2 = rng.randint(tot_a // 4, tot_a // 2 - 4)
    a3 = tot_a - a1 - a2

    col3_tot = a3 + b3
    pct_col3 = Fraction(col3_tot * 100, total)

    return {
        "stem": (
            f"{intro}. W tabeli zestawiono liczebności grup, przy czym jedna liczba uległa zamazaniu. "
            f"Wiadomo, że łączna liczebność wiersza *{row_a}* była o ${diff_ab}$ większa od łącznej liczebności wiersza *{row_b}*."
        ),
        "table_data": [
            ["Kategoria", cols[0], cols[1], cols[2]],
            [row_a, f"${a1}$", f"${a2}$", "$?$"],
            [row_b, f"${b1}$", f"${b2}$", f"${b3}$"],
        ],
        "command": (
            f"Oblicz, jaki procent wszystkich osób ujętych w zestawieniu wybrał kategorię *{cols[2]}*. "
            f"Zapisz obliczenia."
        ),
        "correct_answer": f"{pl_num(pct_col3)}%",
        "solution_steps": [
            f"Suma wiersza *{row_b}*: ${b1} + {b2} + {b3} = {tot_b}$. Zatem suma wiersza *{row_a}* wynosi ${tot_b} + {diff_ab} = {tot_a}$.",
            f"Brakująca liczba w kolumnie *{cols[2]}*: ${tot_a} - ({a1} + {a2}) = {a3}$, a wszystkich osób jest ${tot_a} + {tot_b} = {total}$.",
            f"Łącznie w kategorii *{cols[2]}* jest ${a3} + {b3} = {col3_tot}$ osób, co stanowi $\\frac{{{col3_tot}}}{{{total}}} \\cdot 100\\% = {pl_num(pct_col3)}\\%$.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie sumy wiersza „{row_b}” ({tot_b}) oraz wiersza „{row_a}” ({tot_a}).",
            f"2 pkt – wyznaczenie brakującej liczby ({a3}) oraz łącznej liczebności ({total}).",
            f"3 pkt – poprawne obliczenie szukanego udziału procentowego: {pl_num(pct_col3)}%.",
        ],
        "grid_height_mm": 60.0,
    }


# ===========================================================================
# 12. PRAWDOPODOBIEŃSTWO I KOMBINATORYKA
# ===========================================================================

@register_template(
    template_id="prawdop_balony_bez_zwracania_abcd",
    topic_id="prawdopodobienstwo",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – losowanie po uprzednim wyjęciu elementów",
)
def gen_balony_bez_zwracania(rng):
    ctx = rng.choice([
        ("W szufladzie znajdują się wymieszane długopisy w czterech kolorach obudowy", "Kolor", "Liczba sztuk", ["granatowy", "czarny", "zielony", "srebrny"], "długopis"),
        ("W koszyku przygotowano losy loterii szkolnej w czterech kolorach kopert", "Koperta", "Liczba losów", ["złota", "błękitna", "biała", "różowa"], "los"),
        ("W woreczku znajdują się drewniane pionki do gry planszowej", "Barwa pionka", "Liczba pionków", ["czerwona", "żółta", "fioletowa", "pomarańczowa"], "pionek"),
    ])
    intro, h1, h2, cols, item_acc = ctx
    c0 = rng.choice([9, 11, 13, 15])
    c1 = rng.choice([5, 7, 9])
    c2 = rng.choice([6, 8])
    c3 = rng.choice([6, 8])
    removed = rng.choice([2, 3])
    rem_target = c0 - removed
    init_tot = c0 + c1 + c2 + c3
    rem_tot = init_tot - removed

    p_corr = Fraction(rem_target, rem_tot)
    cands = [
        Fraction(c0, init_tot),
        Fraction(rem_target, init_tot),
        Fraction(c0, rem_tot),
        Fraction(rem_target - 1, rem_tot),
        Fraction(1, 4),
    ]
    wrongs = []
    for cand in cands:
        if cand != p_corr and cand not in wrongs and cand > 0:
            wrongs.append(cand)
        if len(wrongs) == 3:
            break

    choices, ans = shuffle_abcd(
        rng,
        frac_tex(p_corr.numerator, p_corr.denominator),
        [frac_tex(w.numerator, w.denominator) for w in wrongs],
    )

    return {
        "stem": (
            f"{intro}. Początkowe liczebności przedstawia tabela.\n"
            f"Wyjęto losowo bez zwracania ${removed}$ sztuki i okazało się, że każda z nich miała wariant *{cols[0]}*."
        ),
        "table_data": [
            [h1, cols[0], cols[1], cols[2], cols[3]],
            [h2, f"${c0}$", f"${c1}$", f"${c2}$", f"${c3}$"],
        ],
        "command": f"Jakie jest prawdopodobieństwo, że kolejny losowo wyjęty {item_acc} również będzie miał wariant *{cols[0]}*? Wybierz właściwą odpowiedź spośród podanych.",
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Początkowo było łącznie ${init_tot}$ sztuk. Po wyjęciu ${removed}$ sztuk zostało ${rem_tot}$ elementów.",
            f"W wariancie *{cols[0]}* pozostało ${c0} - {removed} = {rem_target}$ sztuk, więc $P = \\frac{{{rem_target}}}{{{rem_tot}}} = {frac_tex(p_corr.numerator, p_corr.denominator)}$ (odpowiedź **{ans}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna odpowiedź.", "0 pkt – odpowiedź błędna lub brak."],
    }


@register_template(
    template_id="prawdop_kule_parzystosc_sumy_ab_cd",
    topic_id="prawdopodobienstwo",
    subtype="ab_cd",
    points=1,
    difficulty=3,
    cke_ref="Styl CKE – rozumowanie kombinatoryczne i parzystość",
)
def gen_kule_parzystosc_sumy(rng):
    variant = rng.choice(["parity_cards", "product_even"])
    if variant == "parity_cards":
        k = rng.choice([4, 5, 6, 7])
        max_n = 2 * k + 1
        sum_even = k * (k + 1)
        sum_odd_k = k * k
        if rng.random() < 0.5:
            opts1, a1 = {"A": "nieparzystymi", "B": "parzystymi"}, "A"
        else:
            opts1, a1 = {"A": "parzystymi", "B": "nieparzystymi"}, "B"

        if rng.random() < 0.5:
            opts2, a2 = {"C": f"${sum_even}$", "D": f"${sum_odd_k}$"}, "C"
        else:
            opts2, a2 = {"C": f"${sum_odd_k}$", "D": f"${sum_even}$"}, "D"

        obj = rng.choice(["żetonów", "kartoników", "identycznych tabliczek"])
        return {
            "stem": (
                f"Na stole ułożono ${max_n}$ {obj} ponumerowanych kolejnymi liczbami naturalnymi od $1$ do ${max_n}$. "
                f"Zabto ze stołu dokładnie ${k}$ z nich tak, że suma numerów dowolnych dwóch pozostawionych {obj} jest liczbą parzystą."
            ).replace("Zabto", "Zabrano"),
            "command": "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D.",
            "ab_cd_parts": [
                {"prefix": f"Na stole pozostały wyłącznie elementy oznaczone liczbami", "suffix": ".", "options": opts1},
                {"prefix": f"Suma numerów na wszystkich ${k}$ zabranych elementach jest równa", "suffix": ".", "options": opts2},
            ],
            "correct_answer": f"{a1}{a2}",
            "solution_steps": [
                f"Na stole zostało ${k + 1}$ elementów o tej samej parzystości. Ponieważ parzystych w zbiorze $1..{max_n}$ jest tylko ${k}$, musiały zostać wszystkie ${k + 1}$ liczb **nieparzystych** (**{a1}**).",
                f"Zabrano wszystkie ${k}$ liczb parzystych, których suma wynosi ${sum_even}$ (**{a2}**).",
            ],
            "scoring_scheme": ["1 pkt – poprawna para odpowiedzi.", "0 pkt – odpowiedź niepełna lub błędna."],
        }

    # product_even: losujemy jedną kartę z 1..2n, ile sprzyja podzielności przez 3 lub parzystości iloczynu z ustaloną liczbą
    n = rng.choice([12, 15, 18, 20, 24])
    div3 = n // 3
    p_div3 = Fraction(div3, n)
    p_wrong = Fraction(div3 + 1, n)
    # Ile co najmniej kart trzeba wyciągnąć w ciemno ze zbioru 1..n, aby na pewno trafić na liczbę parzystą? (n - n//2 + 1)
    odd_cnt = (n + 1) // 2
    min_draw = odd_cnt + 1

    f_good = frac_tex(p_div3.numerator, p_div3.denominator)
    f_bad = frac_tex(p_wrong.numerator, p_wrong.denominator)
    if rng.random() < 0.5:
        opts1, a1 = {"A": f_good, "B": f_bad}, "A"
    else:
        opts1, a1 = {"A": f_bad, "B": f_good}, "B"

    if rng.random() < 0.5:
        opts2, a2 = {"C": f"${min_draw}$", "D": f"${odd_cnt}$"}, "C"
    else:
        opts2, a2 = {"C": f"${odd_cnt}$", "D": f"${min_draw}$"}, "D"

    return {
        "stem": f"W pudełku znajduje się ${n}$ żetonów ponumerowanych kolejnymi liczbami naturalnymi od $1$ do ${n}$.",
        "command": "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D.",
        "ab_cd_parts": [
            {"prefix": "Przy losowaniu jednego żetonu prawdopodobieństwo wylosowania liczby podzielnej przez $3$ wynosi", "suffix": ".", "options": opts1},
            {"prefix": "Aby mieć pewność, że wśród wyjętych bez podglądania żetonów jest co najmniej jeden z liczbą parzystą, należy wyjąć przynajmniej", "suffix": " żetonów.", "options": opts2},
        ],
        "correct_answer": f"{a1}{a2}",
        "solution_steps": [
            f"W zbiorze $\\{{1, \\dots, {n}\\}}$ jest ${div3}$ liczb podzielnych przez $3$, więc $P = \\frac{{{div3}}}{{{n}}} = {f_good}$ (**{a1}**).",
            f"W najgorszym przypadku wyjmiemy najpierw wszystkie ${odd_cnt}$ żetonów nieparzystych, więc pewność daje dopiero ${odd_cnt} + 1 = {min_draw}$ żetonów (**{a2}**).",
        ],
        "scoring_scheme": ["1 pkt – poprawna para odpowiedzi.", "0 pkt – odpowiedź niepełna lub błędna."],
    }
