"""Dział 1: Liczby naturalne, całkowite, ułamki, podzielność i oś liczbowa."""

from __future__ import annotations

from fractions import Fraction

from ..math_text import frac_tex, mixed_frac_tex, pl_num, shuffle_abcd
from ..models import DiagramSpec
from .base import register_template


@register_template(
    template_id="liczby_temperatury_abcd",
    topic_id="liczby_dzialania",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Czerwiec 2024 zad. 1",
)
def gen_temperatury(rng):
    # Cztery miejscowości górskie i cztery różne temperatury ujemne/dodatnie
    towns = ["Szklarskiej Porębie", "Karpaczu", "Wiśle", "Zakopanem"]
    towns_nom = ["Szklarskiej Porębie.", "Karpaczu.", "Wiśle.", "Zakopanem."]

    t_szkl = rng.choice([-11, -10, -9, -8, -7])
    diff = rng.choice([4, 5, 6, 7])
    t_karp = t_szkl + diff

    # Wybierz dwie pozostałe temperatury różne od t_szkl i t_karp, takie by nie różniły się o diff
    used = {t_szkl, t_karp}
    candidates = [t for t in range(-12, 4) if t not in used and (t + diff) not in used and (t - diff) not in used]
    t1, t2 = sorted(rng.sample(candidates, 2))
    # W Wiśle niższa niż w Zakopanem -> t_wisla = t1, t_zak = t2
    t_wisla, t_zak = t1, t2

    shown = [t_szkl, t_karp, t_wisla, t_zak]
    rng.shuffle(shown)
    shown_str = ",  ".join(f"${pl_num(x)}^\\circ\\text{{C}}$" for x in shown)

    target_idx = rng.choice([0, 1, 2, 3])
    temps_by_idx = [t_szkl, t_karp, t_wisla, t_zak]
    target_temp = temps_by_idx[target_idx]
    correct_town = towns_nom[target_idx]

    stem = (
        f"Adam zapisał w przypadkowej kolejności cztery wartości temperatury odnotowane zimowego wieczoru "
        f"w {towns[0]}, w {towns[1]}, w {towns[2]} oraz w {towns[3]}:\n"
        f"{shown_str}.\n"
        f"Wiadomo, że temperatura w Karpaczu była o ${diff}^\\circ\\text{{C}}$ wyższa niż w Szklarskiej Porębie, "
        f"natomiast w Wiśle była niższa niż w Zakopanem."
    )
    command = (
        f"Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\n"
        f"Temperaturę ${pl_num(target_temp)}^\\circ\\text{{C}}$ odnotowano w"
    )
    choices, ans = shuffle_abcd(rng, correct_town, [t for i, t in enumerate(towns_nom) if i != target_idx])

    steps = [
        f"Szukamy wśród podanych liczb pary różniącej się dokładnie o ${diff}^\\circ\\text{{C}}$: "
        f"${pl_num(t_karp)} - ({pl_num(t_szkl)}) = {diff}$.",
        f"Zatem w Szklarskiej Porębie było ${pl_num(t_szkl)}^\\circ\\text{{C}}$, a w Karpaczu ${pl_num(t_karp)}^\\circ\\text{{C}}$.",
        f"Pozostałe dwie wartości to ${pl_num(t_wisla)}^\\circ\\text{{C}}$ oraz ${pl_num(t_zak)}^\\circ\\text{{C}}$. "
        f"Ponieważ w Wiśle było chłodniej niż w Zakopanem, w Wiśle zanotowano ${pl_num(t_wisla)}^\\circ\\text{{C}}$, "
        f"a w Zakopanem ${pl_num(t_zak)}^\\circ\\text{{C}}$.",
        f"Szukana temperatura ${pl_num(target_temp)}^\\circ\\text{{C}}$ wystąpiła w {correct_town[:-1]} (odpowiedź **{ans}**).",
    ]
    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": steps,
    }


@register_template(
    template_id="liczby_os_liczbowa_pf",
    topic_id="liczby_dzialania",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2021 zad. 2",
    has_diagram=True,
)
def gen_os_liczbowa_pf(rng):
    # Oś liczbowa z równym krokiem step = 0.25, 0.4 lub 0.5
    step_num, step_den = rng.choice([(1, 4), (2, 5), (1, 2), (3, 4)])
    step = Fraction(step_num, step_den)
    # 9 kresek od indeksu 0 do 8; podpisujemy dwie kreski i zaznaczamy punkty A i B
    idx0 = rng.choice([-4, -3, -2])
    ticks = list(range(idx0, idx0 + 9))
    val_at = lambda k: k * step

    # Podpiszmy dwie kreski całkowite lub wymierne
    lbl1_idx = 0
    lbl2_idx = step_den if (0 + step_den) <= idx0 + 8 else idx0 + 4
    labeled_ticks = {
        lbl1_idx: pl_num(val_at(lbl1_idx)),
        lbl2_idx: pl_num(val_at(lbl2_idx)),
    }

    a_idx = idx0 + 1
    b_idx = idx0 + 7
    val_a = val_at(a_idx)
    val_b = val_at(b_idx)

    # Zdanie 1: współrzędna punktu A lub suma A + B
    s1_true = rng.choice([True, False])
    sum_ab = val_a + val_b
    shown_sum = sum_ab if s1_true else (sum_ab + step)

    # Zdanie 2: odległość między A i B
    dist_ab = val_b - val_a
    s2_true = rng.choice([True, False])
    shown_dist = dist_ab if s2_true else (dist_ab - step)

    def fmt_frac_or_dec(fr: Fraction) -> str:
        if fr.denominator in (1, 2, 4, 5):
            return f"${pl_num(float(fr))}$"
        return frac_tex(fr.numerator, fr.denominator)

    st1 = f"Suma współrzędnych punktów $A$ i $B$ jest równa {fmt_frac_or_dec(shown_sum)}."
    st2 = f"Odległość między punktami $A$ i $B$ na osi liczbowej jest równa {fmt_frac_or_dec(shown_dist)}."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    diag = DiagramSpec(
        kind="number_line",
        params={
            "ticks": ticks,
            "labeled_ticks": labeled_ticks,
            "points": [{"x": a_idx, "label": "A"}, {"x": b_idx, "label": "B"}],
        },
        width_mm=98.0,
    )

    stem = "Na osi liczbowej zaznaczono punkty $A$ oraz $B$. Odstępy między sąsiednimi kreskami podziałki są równe."
    command = "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe."

    steps = [
        f"Między podpisanymi liczbami ${labeled_ticks[lbl1_idx]}$ i ${labeled_ticks[lbl2_idx]}$ znajduje się "
        f"${abs(lbl2_idx - lbl1_idx)}$ jednostkowych odcinków podziałki, więc jeden odcinek ma długość ${pl_num(float(step))}$.",
        f"Odczytujemy współrzędne: $A = {pl_num(float(val_a))}$ oraz $B = {pl_num(float(val_b))}$.",
        f"Suma współrzędnych: ${pl_num(float(val_a))} + {pl_num(float(val_b))} = {pl_num(float(sum_ab))}$ -> zdanie pierwsze: **{p1}**.",
        f"Odległość między $A$ i $B$: ${pl_num(float(val_b))} - ({pl_num(float(val_a))}) = {pl_num(float(dist_ab))}$ -> zdanie drugie: **{p2}**.",
    ]
    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": steps,
    }


@register_template(
    template_id="liczby_podzielnosc_uzasadnienie",
    topic_id="liczby_dzialania",
    subtype="uzasadnienie",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2022 zad. 4",
)
def gen_podzielnosc_uzasadnienie(rng):
    div = rng.choice([3, 9])
    is_div = rng.choice([True, False])
    a = rng.randint(210, 580)
    b_base = rng.randint(120, 390)
    rem = (a + b_base) % div
    if is_div:
        b = b_base + ((div - rem) % div)
    else:
        shift = rng.choice([x for x in range(1, div) if (rem + x) % div != 0] or [1])
        b = b_base + shift if rem == 0 else b_base

    total = a + b
    digit_sum = sum(int(c) for c in str(total))
    last_digit = total % 10

    ans_ab = "A" if (total % div == 0) else "B"
    # Uzasadnienia 1, 2, 3
    r_correct = (
        f"suma cyfr liczby ${total}$ jest równa ${digit_sum}$, a liczba ${digit_sum}$ "
        f"{'jest' if total % div == 0 else 'nie jest'} podzielna przez ${div}$."
    )
    r_wrong1 = f"ostatnią cyfrą liczby ${total}$ jest ${last_digit}$."
    r_wrong2 = f"jeden ze składników sumy (${a}$ lub ${b}$) {'jest' if total % div != 0 else 'nie jest'} podzielny przez ${div}$."

    reasons_list = [r_correct, r_wrong1, r_wrong2]
    rng.shuffle(reasons_list)
    reasons_dict = {str(i + 1): reasons_list[i] for i in range(3)}
    corr_num = next(k for k, v in reasons_dict.items() if v == r_correct)

    stem = f"Liczba $k$ jest sumą liczb ${a}$ oraz ${b}$."
    command = f"Czy liczba $k$ jest podzielna przez ${div}$? Wybierz odpowiedź A albo B i jej uzasadnienie spośród 1., 2. albo 3."

    return {
        "stem": stem,
        "command": command,
        "justification_data": {
            "choices_ab": {"A": "Tak,", "B": "Nie,"},
            "connector": "ponieważ",
            "reasons": reasons_dict,
        },
        "correct_answer": f"{ans_ab}{corr_num}",
        "solution_steps": [
            f"Obliczamy wartość liczby $k$: $k = {a} + {b} = {total}$.",
            f"Obliczamy sumę cyfr liczby ${total}$: ${' + '.join(str(total))} = {digit_sum}$.",
            f"Liczba naturalna jest podzielna przez ${div}$ wtedy i tylko wtedy, gdy suma jej cyfr jest podzielna przez ${div}$. "
            f"Zatem poprawna odpowiedź to **{ans_ab}{corr_num}**.",
        ],
    }


@register_template(
    template_id="liczby_ulamki_otwarte_2pkt",
    topic_id="liczby_dzialania",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2020 zad. 16",
)
def gen_sloiki_sok_2pkt(rng):
    # Babcia przygotowała sok malinowy i rozlała do małych i dużych butelek
    small_num, small_den = rng.choice([(1, 4), (3, 10), (2, 5)])
    large_num, large_den = rng.choice([(3, 4), (3, 5)])
    n_small = rng.choice([6, 8, 10, 12])
    n_large = rng.choice([4, 6, 8])

    vol_small = Fraction(small_num, small_den) * n_small
    vol_large = Fraction(large_num, large_den) * n_large
    leftover = Fraction(rng.choice([1, 2, 3]), 5)
    total = vol_small + vol_large + leftover

    total_dec = float(total)
    left_dec = pl_num(float(leftover))

    stem = (
        f"Pani Marta przygotowała sok malinowy w dużym garnku. Część soku przelała do ${n_small}$ jednakowych małych butelek, "
        f"każda o pojemności {frac_tex(small_num, small_den)} litra, oraz do ${n_large}$ jednakowych większych butelek, "
        f"każda o pojemności {frac_tex(large_num, large_den)} litra. W garnku pozostało jeszcze ${left_dec}$ litra soku."
    )
    command = "Oblicz, ile litrów soku malinowego przygotowała na początku pani Marta. Zapisz obliczenia."

    ans_str = f"{pl_num(total_dec)} l"
    return {
        "stem": stem,
        "command": command,
        "correct_answer": ans_str,
        "solution_steps": [
            f"Obliczamy objętość soku w małych butelkach: ${n_small} \\cdot$ {frac_tex(small_num, small_den)} $= {pl_num(float(vol_small))}$ (l).",
            f"Obliczamy objętość soku w większych butelkach: ${n_large} \\cdot$ {frac_tex(large_num, large_den)} $= {pl_num(float(vol_large))}$ (l).",
            f"Dodajemy sok pozostały w garnku: ${pl_num(float(vol_small))} + {pl_num(float(vol_large))} + {left_dec} = {pl_num(total_dec)}$ (l).",
            f"**Odpowiedź:** Pani Marta przygotowała na początku ${pl_num(total_dec)}$ litra soku.",
        ],
        "scoring_scheme": [
            "1 pkt – poprawne obliczenie łącznej ilości soku w małych i większych butelkach.",
            f"2 pkt – poprawne dokończenie obliczeń i podanie odpowiedzi: {pl_num(total_dec)} l.",
        ],
        "grid_height_mm": 48.0,
    }


@register_template(
    template_id="liczby_ulamki_wydatki_3pkt",
    topic_id="liczby_dzialania",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Wzorzec: CKE Kwiecień 2019 zad. 17",
)
def gen_ulamki_oszczednosci_3pkt(rng):
    # Tomek wydał 1/a oszczędności na plecak, potem b/c POZOSTAŁEJ kwoty na buty, zostało mu R zł.
    # Dobierzmy tak, aby wszystkie kwoty były całkowite!
    den1 = rng.choice([3, 4, 5])
    num1 = 1
    # Pozostało (den1 - 1)/den1; drugi wydatek to ułamek reszty f2
    f2_num, f2_den = rng.choice([(2, 5), (3, 5), (1, 3), (3, 4)])
    frac_after_1 = Fraction(den1 - num1, den1)
    frac_left = frac_after_1 * Fraction(f2_den - f2_num, f2_den)

    # Dobierzmy początkową kwotę S jako wielokrotność mianownika frac_left.denominator
    mult = rng.randint(8, 18) * 10
    S = frac_left.denominator * mult
    plecak = int(S * Fraction(num1, den1))
    reszta1 = S - plecak
    buty = int(reszta1 * Fraction(f2_num, f2_den))
    left_zl = S - plecak - buty

    stem = (
        f"Tomek przeznaczył część swoich oszczędności na zakup sprzętu turystycznego. Najpierw wydał "
        f"{frac_tex(num1, den1)} wszystkich oszczędności na plecak, a następnie {frac_tex(f2_num, f2_den)} **pozostałej** kwoty "
        f"wydał na buty górskie. Po tych zakupach zostało mu jeszcze ${left_zl}$ zł."
    )
    command = "Oblicz, ile złotych kosztowały buty górskie oraz ile złotych oszczędności miał Tomek na początku. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"Buty: {buty} zł, początkowe oszczędności: {S} zł",
        "solution_steps": [
            f"Po zakupie plecaka Tomkowi pozostało $1 -$ {frac_tex(num1, den1)} $=$ {frac_tex(den1 - num1, den1)} początkowych oszczędności.",
            f"Na buty wydał {frac_tex(f2_num, f2_den)} z tej reszty, czyli {frac_tex(f2_num, f2_den)} $\\cdot$ {frac_tex(den1 - num1, den1)} $=$ "
            f"{frac_tex((den1 - num1) * f2_num, den1 * f2_den)} wszystkich oszczędności.",
            f"Ułamek oszczędności, który pozostał na końcu: {frac_tex(frac_left.numerator, frac_left.denominator)}.",
            f"Ponieważ {frac_tex(frac_left.numerator, frac_left.denominator)} oszczędności to ${left_zl}$ zł, cała kwota początkowa wynosi: "
            f"${left_zl} :$ {frac_tex(frac_left.numerator, frac_left.denominator)} $= {S}$ zł.",
            f"Koszt butów górskich: {frac_tex(f2_num, f2_den)} $\\cdot ({S} - {plecak}) =$ {frac_tex(f2_num, f2_den)} $\\cdot {reszta1} = {buty}$ zł.",
            f"**Odpowiedź:** Tomek miał na początku ${S}$ zł oszczędności, a buty kosztowały ${buty}$ zł.",
        ],
        "scoring_scheme": [
            "1 pkt – wyznaczenie ułamka pozostałej kwoty po pierwszym lub po obu zakupach (albo zapisanie poprawnego równania).",
            f"2 pkt – obliczenie początkowej kwoty oszczędności ({S} zł).",
            f"3 pkt – obliczenie ceny butów ({buty} zł) i podanie pełnej odpowiedzi.",
        ],
        "grid_height_mm": 64.0,
    }
