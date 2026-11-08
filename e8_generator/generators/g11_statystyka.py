"""Dział 11: Statystyka opisowa, tabele i odczytywanie diagramów."""

from __future__ import annotations

from ..math_text import frac_tex, pl_num, shuffle_abcd
from ..models import DiagramSpec
from .base import register_template


@register_template(
    template_id="statystyka_srednia_ksiazka_abcd",
    topic_id="statystyka_diagramy",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Czerwiec 2025 zad. 1",
)
def gen_srednia_ksiazka_abcd(rng):
    avg = rng.choice([45, 50, 55, 60, 65])
    total_5 = 5 * avg
    # Wylosuj 4 dni tak, by piąty (sobota) wyszedł dodatni i realistyczny
    d1 = avg + rng.randint(-12, 8)
    d2 = avg + rng.randint(-10, 12)
    d3 = avg + rng.randint(-15, 10)
    d4 = avg + rng.randint(-8, 14)
    sat = total_5 - (d1 + d2 + d3 + d4)
    if sat <= 15:
        d1 -= 20
        sat += 20

    sum_4 = d1 + d2 + d3 + d4
    corr = f"${sat}$"
    distractors = [
        f"${avg}$",
        f"${sum_4 // 4}$" if (sum_4 // 4) != sat else f"${sat - 8}$",
        f"${sat + 10}$",
    ]
    choices, ans = shuffle_abcd(rng, corr, distractors)

    table = [
        ["Dzień tygodnia", "Wtorek", "Środa", "Czwartek", "Piątek"],
        ["Liczba przeczytanych stron", str(d1), str(d2), str(d3), str(d4)],
    ]

    stem = (
        f"Robert rozpoczął czytanie książki we wtorek i zakończył w sobotę. W tabeli zapisano liczbę stron, "
        f"które przeczytał w kolejnych dniach od wtorku do piątku. Od wtorku do soboty włącznie Robert czytał "
        f"dziennie średnio ${avg}$ stron tej książki."
    )
    command = "Ile stron tej książki Robert przeczytał w sobotę? Wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "table_data": table,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Przez $5$ dni (od wtorku do soboty) Robert przeczytał łącznie $5 \\cdot {avg} = {total_5}$ stron.",
            f"Od wtorku do piątku przeczytał ${d1} + {d2} + {d3} + {d4} = {sum_4}$ stron.",
            f"W sobotę przeczytał zatem ${total_5} - {sum_4} = {sat}$ stron (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="statystyka_diagram_kwartaly_pf",
    topic_id="statystyka_diagramy",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Styczeń 2026 zad. 1",
    has_diagram=True,
)
def gen_diagram_kwartaly_pf(rng):
    # Zysk firmy w 4 kwartałach w tys. zł: suma podzielna przez 4 i 5 (np. 80 lub 100 lub 120)
    vals = rng.choice([
        [15, 25, 20, 40],  # suma 100, średnia 25, I kw. = 15/100 = 3/20, IV kw. = 2/5
        [20, 30, 25, 45],  # suma 120, średnia 30, I kw. = 1/6
        [10, 20, 15, 35],  # suma 80, średnia 20, II kw. = 1/4
        [25, 15, 30, 50],  # suma 120, średnia 30, III kw. = 1/4
    ])
    vals = list(vals)
    total = sum(vals)
    avg = total // 4

    # Zdanie 1: ułamek zysku w wybranym kwartale
    # Znajdź kwartał dający ładny ułamek
    q_names = ["I kwartale", "II kwartale", "III kwartale", "IV kwartale"]
    idx_q = 1 if total == 80 else (2 if vals[2] * 4 == total else 0)
    from math import gcd
    g = gcd(vals[idx_q], total)
    num_r, den_r = vals[idx_q] // g, total // g

    s1_true = rng.choice([True, False])
    shown_den = den_r if s1_true else (den_r - 1 if den_r > 2 else den_r + 1)

    s2_true = rng.choice([True, False])
    shown_avg = avg if s2_true else (avg + 5)

    diag = DiagramSpec(
        kind="bar_chart",
        params={
            "categories": ["I kw.", "II kw.", "III kw.", "IV kw."],
            "values": vals,
            "ylabel": "Zysk (tys. zł)",
            "y_step": 10,
            "show_values": False,
        },
        width_mm=84.0,
    )

    stem = "Na diagramie słupkowym przedstawiono zysk pewnej firmy (w tysiącach złotych) osiągnięty w kolejnych czterech kwartałach ubiegłego roku."
    command = "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe."

    st1 = f"Zysk tej firmy w {q_names[idx_q]} stanowił {frac_tex(str(num_r), str(shown_den))} łącznego zysku z całego roku."
    st2 = f"Średni kwartalny zysk tej firmy w ubiegłym roku był równy ${shown_avg}$ tys. zł."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": [
            f"Odczytujemy wartości z diagramu: ${vals[0]}$, ${vals[1]}$, ${vals[2]}$, ${vals[3]}$ (tys. zł). "
            f"Łączny zysk roczny wynosi ${total}$ tys. zł.",
            f"Udział zysku w {q_names[idx_q]}: {frac_tex(str(vals[idx_q]), str(total))} $=$ {frac_tex(str(num_r), str(den_r))} -> zdanie pierwsze: **{p1}**.",
            f"Średni zysk kwartalny: ${total} : 4 = {avg}$ tys. zł -> zdanie drugie: **{p2}**.",
        ],
    }


@register_template(
    template_id="statystyka_mediana_srednia_ab_cd",
    topic_id="statystyka_diagramy",
    subtype="ab_cd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2021 zad. 4",
)
def gen_statystyka_ab_cd(rng):
    # 6 wyników nieuporządkowanych, suma podzielna przez 6
    base = rng.randint(5, 10)
    # Zestaw symetryczny lub kontrolowany
    sorted_vals = [base - 3, base - 2, base, base + 2, base + 3, base + 6]
    # Suma = 6*base + 6 -> średnia = base + 1; mediana = (sorted_vals[2] + sorted_vals[3])/2 = base + 1!
    # Zmieńmy tak, by średnia != mediana:
    sorted_vals = [base - 3, base - 1, base, base + 2, base + 4, base + 4]
    # Suma = 6*base + 6 -> średnia = base + 1; mediana = (base + base + 2)/2 = base + 1 -> zróbmy:
    sorted_vals = [base - 4, base - 2, base - 1, base + 1, base + 4, base + 8]
    # Suma = 6*base + 6 -> średnia = base + 1; mediana = ((base-1) + (base+1))/2 = base!
    avg_val = sum(sorted_vals) // 6  # base + 1
    med_val = (sorted_vals[2] + sorted_vals[3]) // 2  # base

    shuffled = list(sorted_vals)
    rng.shuffle(shuffled)
    # Upewnijmy się, że środkowe w nieposortowanym nie dają przypadkiem med_val, żeby wychwycić brak sortowania
    corr1 = f"${avg_val}$"
    wrong1 = f"${avg_val + 1}$"
    if rng.choice([True, False]):
        opts1 = {"A": corr1, "B": wrong1}
        c1 = "A"
    else:
        opts1 = {"A": wrong1, "B": corr1}
        c1 = "B"

    corr2 = f"${med_val}$"
    wrong2 = f"${med_val + 2}$"
    if rng.choice([True, False]):
        opts2 = {"C": corr2, "D": wrong2}
        c2 = "C"
    else:
        opts2 = {"C": wrong2, "D": corr2}
        c2 = "D"

    vals_str = ",  ".join(str(v) for v in shuffled)
    stem = f"W sześciu kolejnych konkursach wiedzy uczeń uzyskał następujące liczby punktów:\n${vals_str}$."
    command = "Uzupełnij zdania. Wybierz odpowiedź spośród oznaczonych literami A i B oraz odpowiedź spośród oznaczonych literami C i D."

    parts = [
        {"prefix": "Średnia arytmetyczna liczby uzyskanych punktów jest równa", "suffix": ".", "options": opts1},
        {"prefix": "Mediana (wartość środkowa) tego zestawu wyników jest równa", "suffix": ".", "options": opts2},
    ]

    return {
        "stem": stem,
        "command": command,
        "ab_cd_parts": parts,
        "correct_answer": c1 + c2,
        "solution_steps": [
            f"Obliczamy średnią arytmetyczną: $({ ' + '.join(str(v) for v in shuffled) }) : 6 = {sum(shuffled)} : 6 = {avg_val}$ (wybór **{c1}**).",
            f"Porządkujemy wyniki rosnąco: ${', '.join(str(v) for v in sorted_vals)}$. "
            f"Mediana dla parzystej liczby danych to średnia dwóch środkowych wyrazów: $({sorted_vals[2]} + {sorted_vals[3]}) : 2 = {med_val}$ (wybór **{c2}**).",
        ],
    }


@register_template(
    template_id="statystyka_nowi_zawodnicy_2pkt",
    topic_id="statystyka_diagramy",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2020 zad. 16",
)
def gen_srednia_dolaczenie_2pkt(rng):
    n1 = rng.choice([6, 8, 9])
    avg1 = rng.randint(12, 18)
    avg2 = avg1 + rng.choice([1, 2])
    # Dołączyło 2 zawodników, z czego jeden zdobył p1 pkt, ile zdobył drugi?
    sum1 = n1 * avg1
    sum2 = (n1 + 2) * avg2
    both_new = sum2 - sum1
    p_first = both_new // 2 - rng.randint(1, 3)
    p_second = both_new - p_first

    stem = (
        f"Średnia arytmetyczna liczby punktów zdobytych w turnieju łuczniczym przez ${n1}$ zawodników była równa ${avg1}$. "
        f"Gdy do klasyfikacji dopisano wyniki jeszcze dwóch zawodników – Marka i Pawła – średnia arytmetyczna wyników "
        f"wszystkich ${n1 + 2}$ osób wzrosła do ${avg2}$. Wiadomo, że Marek zdobył ${p_first}$ punktów."
    )
    command = "Oblicz, ile punktów zdobył Paweł. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"{p_second} pkt",
        "solution_steps": [
            f"Suma punktów pierwszych ${n1}$ zawodników wynosi: ${n1} \\cdot {avg1} = {sum1}$.",
            f"Suma punktów wszystkich ${n1 + 2}$ zawodników wynosi: ${n1 + 2} \\cdot {avg2} = {sum2}$.",
            f"Marek i Paweł zdobyli razem ${sum2} - {sum1} = {both_new}$ punktów, więc Paweł zdobył ${both_new} - {p_first} = {p_second}$ punktów.",
            f"**Odpowiedź:** Paweł zdobył ${p_second}$ punktów.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie sumy punktów przed dopisaniem ({sum1}) oraz po dopisaniu dwóch zawodników ({sum2}).",
            f"2 pkt – poprawne obliczenie liczby punktów zdobytych przez Pawła ({p_second}).",
        ],
        "grid_height_mm": 48.0,
    }


@register_template(
    template_id="statystyka_diagram_bilety_3pkt",
    topic_id="statystyka_diagramy",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2024 zad. 17",
    has_diagram=True,
)
def gen_diagram_kino_3pkt(rng):
    # Liczba sprzedanych biletów od piątku do niedzieli na diagramie słupkowym; ułamek ulgowych i ceny biletów!
    fri = rng.choice([40, 50, 60])
    sat = rng.choice([80, 90, 100])
    sun = rng.choice([60, 70, 80])
    total_tickets = fri + sat + sun
    # Upewnijmy się, że total_tickets dzieli się przez 5
    pct_reduced = rng.choice([40, 60])
    n_reduced = total_tickets * pct_reduced // 100
    n_normal = total_tickets - n_reduced

    p_red = rng.choice([18, 20, 22])
    p_norm = p_red + rng.choice([8, 10])
    revenue = n_reduced * p_red + n_normal * p_norm

    diag = DiagramSpec(
        kind="bar_chart",
        params={
            "categories": ["Piątek", "Sobota", "Niedziela"],
            "values": [fri, sat, sun],
            "ylabel": "Liczba biletów",
            "y_step": 20,
            "show_values": True,
        },
        width_mm=82.0,
    )

    stem = (
        f"Na diagramie przedstawiono liczbę wszystkich biletów sprzedanych w małym kinie studyjnym w trzy kolejne dni weekendu. "
        f"Spośród wszystkich biletów sprzedanych łącznie w te trzy dni dokładnie ${pct_reduced}\\%$ stanowiły bilety ulgowe, "
        f"a pozostałe – bilety normalne. Bilet ulgowy kosztował ${p_red}$ zł, a bilet normalny – ${p_norm}$ zł."
    )
    command = "Oblicz łączny przychód kina ze sprzedaży wszystkich biletów w ten weekend. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "diagram": diag,
        "correct_answer": f"{pl_num(revenue)} zł",
        "solution_steps": [
            f"Odczytujemy z diagramu i sumujemy liczbę sprzedanych biletów: ${fri} + {sat} + {sun} = {total_tickets}$.",
            f"Liczba biletów ulgowych: ${pct_reduced}\\% \\cdot {total_tickets} = {n_reduced}$. "
            f"Liczba biletów normalnych: ${total_tickets} - {n_reduced} = {n_normal}$.",
            f"Obliczamy łączny przychód: ${n_reduced} \\cdot {p_red} + {n_normal} \\cdot {p_norm} = "
            f"{n_reduced * p_red} + {n_normal * p_norm} = {pl_num(revenue)}$ zł.",
            f"**Odpowiedź:** Łączny przychód kina wyniósł ${pl_num(revenue)}$ zł.",
        ],
        "scoring_scheme": [
            f"1 pkt – odczytanie danych z diagramu i obliczenie łącznej liczby sprzedanych biletów ({total_tickets}).",
            f"2 pkt – obliczenie liczby biletów ulgowych ({n_reduced}) oraz normalnych ({n_normal}).",
            f"3 pkt – obliczenie całkowitego przychodu ze sprzedaży ({pl_num(revenue)} zł).",
        ],
        "grid_height_mm": 60.0,
    }
