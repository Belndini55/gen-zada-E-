"""Dział 6: Równania pierwszego stopnia z jedną niewiadomą i zadania tekstowe."""

from __future__ import annotations

from ..math_text import frac_tex, pl_num, shuffle_abcd
from .base import register_template


@register_template(
    template_id="rownania_model_abcd",
    topic_id="rownania_tekstowe",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2022 zad. 11",
)
def gen_rownanie_model_abcd(rng):
    # W trzech pudełkach jest razem total kul. W drugim jest 2 razy więcej niż w pierwszym, a w trzecim o d mniej niż w drugim.
    x_val = rng.randint(12, 25)
    d = rng.randint(4, 11)
    total = x_val + 2 * x_val + (2 * x_val - d)

    corr = f"$x + 2x + (2x - {d}) = {total}$"
    w1 = f"$x + 2x + (x - {d}) = {total}$"
    w2 = f"$x + 2x + (2x + {d}) = {total}$"
    w3 = f"$x + (x + 2) + (x + 2 - {d}) = {total}$"

    choices, ans = shuffle_abcd(rng, corr, [w1, w2, w3])

    stem = (
        f"Na trzech półkach ustawiono łącznie ${total}$ książek. Na drugiej półce stoi dwa razy więcej książek "
        f"niż na pierwszej półce, a na trzeciej półce – o ${d}$ książek mniej niż na **drugiej** półce."
    )
    command = (
        "Dokończ zdanie. Wybierz właściwą odpowiedź spośród podanych.\n"
        "Jeżeli przez $x$ oznaczymy liczbę książek stojących na pierwszej półce, to sytuację z zadania opisuje równanie"
    )

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Pierwsza półka: $x$ książek.",
            f"Druga półka (dwa razy więcej niż na pierwszej): $2x$ książek.",
            f"Trzecia półka (o ${d}$ mniej niż na drugiej): $2x - {d}$ książek.",
            f"Łączna liczba książek wynosi ${total}$, skąd otrzymujemy równanie {corr} (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="rownania_sprawdzenie_pf",
    topic_id="rownania_tekstowe",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2020 zad. 8",
)
def gen_rownania_pf(rng):
    # Równanie 1: (2x - a)/3 = b -> x = (3b + a)/2
    b = rng.randint(2, 6)
    a = rng.choice([2, 4, 6]) if (3 * b) % 2 == 0 else rng.choice([1, 3, 5])
    x_sol = (3 * b + a) // 2

    s1_true = rng.choice([True, False])
    shown_x = x_sol if s1_true else x_sol - 2

    # Równanie 2: 3(x - k) = 3x - 3k (tożsamościowe vs sprzeczne)
    k = rng.randint(2, 5)
    s2_true = rng.choice([True, False])
    rhs_const = 3 * k if s2_true else k

    stem = (
        f"Rozważmy dwa równania z niewiadomą $x$:\n"
        f"I.  {frac_tex(f'2x - {a}', '3')} $= {b}$\n"
        f"II. $3(x - {k}) = 3x - {rhs_const}$"
    )
    command = "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe."

    st1 = f"Rozwiązaniem równania I jest liczba $x = {shown_x}$."
    st2 = "Równanie II spełnia każda liczba rzeczywista."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    return {
        "stem": stem,
        "command": command,
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": [
            f"W równaniu I mnożymy obie strony przez $3$: $2x - {a} = {3 * b}$, skąd $2x = {3 * b + a}$, czyli $x = {x_sol}$ -> zdanie pierwsze: **{p1}**.",
            f"W równaniu II lewa strona jest równa $3x - {3 * k}$, a prawa $3x - {rhs_const}$ -> zdanie drugie: **{p2}**.",
        ],
    }


@register_template(
    template_id="rownania_podzial_uzasadnienie",
    topic_id="rownania_tekstowe",
    subtype="uzasadnienie",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2023 zad. 9",
)
def gen_rownanie_naturalne_uzasadnienie(rng):
    # Czy w trzech kolejnych dniach Marcin mógł przeczytać łącznie S stron, jeśli każdego kolejnego dnia czytał o d stron więcej?
    d = rng.choice([4, 5, 6])
    can_be = rng.choice([True, False])
    x0 = rng.randint(15, 32)
    # x + (x+d) + (x+2d) = 3x + 3d (zawsze podzielne przez 3!)
    if can_be:
        S = 3 * x0 + 3 * d
    else:
        S = 3 * x0 + 3 * d + rng.choice([1, 2])

    rhs = S - 3 * d
    ans_ab = "A" if can_be else "B"

    r_corr = (
        f"równanie $x + (x + {d}) + (x + {2 * d}) = {S}$ sprowadza się do postaci $3x = {rhs}$, "
        f"a liczba ${rhs}$ {'jest' if can_be else 'nie jest'} podzielna przez $3$."
    )
    r_w1 = f"liczba ${S}$ jest większa od sumy różnic ${d} + {2 * d} = {3 * d}$."
    r_w2 = f"równanie $3x + {d} = {S}$ ma rozwiązanie wymierne."

    r_list = [r_corr, r_w1, r_w2]
    rng.shuffle(r_list)
    r_dict = {str(i + 1): r_list[i] for i in range(3)}
    c_num = next(k for k, v in r_dict.items() if v == r_corr)

    stem = (
        f"Marcin czytał książkę przez trzy kolejne dni. Każdego następnego dnia przeczytał dokładnie o ${d}$ stron "
        f"więcej niż dnia poprzedniego."
    )
    command = (
        f"Czy Marcin mógł w ciągu tych trzech dni przeczytać łącznie dokładnie ${S}$ stron? "
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
            f"Oznaczmy przez $x$ liczbę stron przeczytanych pierwszego dnia ($x$ musi być liczbą naturalną).",
            f"W kolejnych dniach Marcin przeczytał $x$, $x + {d}$ oraz $x + {2 * d}$ stron.",
            f"Suma stron wynosi $3x + {3 * d} = {S}$, czyli $3x = {rhs}$. Odpowiedź: **{ans_ab}{c_num}**.",
        ],
    }


@register_template(
    template_id="rownania_zbiorniki_2pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: Informator CKE 2025 (zbiorniki z wodą)",
)
def gen_zbiorniki_woda_2pkt(rng):
    # W pierwszym zbiorniku było k razy więcej wody niż w drugim (x w drugim, kx w pierwszym).
    # Gdy do każdego dolano po d litrów, w pierwszym było 2 razy więcej niż w drugim: kx + d = 2(x + d) -> (k-2)x = d!
    k = rng.choice([3, 4, 5])
    x2 = rng.randint(5, 14)
    d = (k - 2) * x2
    x1 = k * x2
    total_after = (x1 + d) + (x2 + d)

    stem = (
        f"W pierwszym zbiorniku było na początku ${k}$ razy więcej wody niż w drugim zbiorniku. "
        f"Następnie do każdego z obu zbiorników dolano po ${d}$ litrów wody. Okazało się wówczas, "
        f"że w pierwszym zbiorniku jest dwa razy więcej wody niż w drugim."
    )
    command = "Oblicz, ile łącznie litrów wody znajduje się teraz (po dolaniu) w obu zbiornikach. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"{total_after} l",
        "solution_steps": [
            f"Oznaczmy przez $x$ początkową ilość wody (w litrach) w drugim zbiorniku. Wtedy w pierwszym zbiorniku było ${k}x$ litrów.",
            f"Po dolaniu po ${d}$ litrów w drugim zbiorniku jest $x + {d}$ litrów, a w pierwszym ${k}x + {d}$ litrów.",
            f"Układamy i rozwiązujemy równanie: ${k}x + {d} = 2(x + {d})$, czyli ${k}x + {d} = 2x + {2 * d}$, skąd ${k - 2}x = {d}$, więc $x = {x2}$.",
            f"Po dolaniu w pierwszym zbiorniku jest ${k} \\cdot {x2} + {d} = {x1 + d}$ l, a w drugim ${x2} + {d} = {x2 + d}$ l; "
            f"razem: ${x1 + d} + {x2 + d} = {total_after}$ litrów.",
            f"**Odpowiedź:** W obu zbiornikach znajduje się łącznie ${total_after}$ litrów wody.",
        ],
        "scoring_scheme": [
            f"1 pkt – ułożenie poprawnego równania opisującego treść zadania, np. {k}x + {d} = 2(x + {d}).",
            f"2 pkt – poprawne rozwiązanie równania (x = {x2}) i obliczenie łącznej ilości wody po dolaniu ({total_after} l).",
        ],
        "grid_height_mm": 52.0,
    }


@register_template(
    template_id="rownania_bilety_wycieczka_3pkt",
    topic_id="rownania_tekstowe",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Wzorzec: CKE Styczeń 2026 zad. 16 / Maj 2023 zad. 18",
)
def gen_druzyna_zespoly_3pkt(rng):
    # Drużynę harcerską można podzielić na k1-osobowe zastępy (bez reszty).
    # Gdyby drużyna liczyła o M osób więcej, można by ją podzielić na k2-osobowe zastępy, a zastępów byłoby o R mniej (lub o R więcej)!
    # Niech liczba zastępów na początku to n: liczba osób H = k1 * n.
    # Po dodaniu M osób: H + M = k2 * (n - R) -> k1*n + M = k2*n - k2*R -> (k2 - k1)*n = M + k2*R
    k1, k2 = rng.choice([(4, 6), (5, 7), (4, 7), (6, 8)])
    n = rng.randint(7, 13)
    H = k1 * n
    n2 = n - rng.choice([1, 2])
    M = k2 * n2 - H
    # Upewnijmy się, że M > 0; jeśli nie, zwiększmy n2 lub n
    while M <= 0:
        n += 2
        H = k1 * n
        n2 = n - 1
        M = k2 * n2 - H
    diff_groups = n - n2

    stem = (
        f"Drużynę harcerską liczącą pewną liczbę osób podzielono na równe, ${k1}$-osobowe zastępy "
        f"(każdy harcerz należał dokładnie do jednego zastępu). Gdyby do tej drużyny dołączyło jeszcze ${M}$ osób, "
        f"to wszystkich harcerzy można by podzielić na równe, ${k2}$-osobowe zastępy i wówczas liczba zastępów "
        f"byłaby o ${diff_groups}$ mniejsza niż obecnie."
    )
    command = "Oblicz, ilu harcerzy liczy obecnie ta drużyna. Zapisz obliczenia."

    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"{H} harcerzy",
        "solution_steps": [
            f"Oznaczmy przez $n$ obecną liczbę ${k1}$-osobowych zastępów. Wówczas drużyna liczy obecnie ${k1}n$ harcerzy.",
            f"Gdyby dołączyło ${M}$ osób, drużyna liczyłaby ${k1}n + {M}$ osób, a liczba ${k2}$-osobowych zastępów wynosiłaby $n - {diff_groups}$.",
            f"Zapisujemy równanie: ${k1}n + {M} = {k2}(n - {diff_groups})$.",
            f"Rozwiązujemy równanie: ${k1}n + {M} = {k2}n - {k2 * diff_groups}$, stąd ${k2 - k1}n = {M + k2 * diff_groups}$, czyli $n = {n}$.",
            f"Obliczamy obecną liczbę harcerzy: ${k1} \\cdot {n} = {H}$.",
            f"**Odpowiedź:** Drużyna liczy obecnie ${H}$ harcerzy.",
        ],
        "scoring_scheme": [
            "1 pkt – wprowadzenie niewiadomej i poprawne wyrażenie obu sposobów podziału drużyny.",
            f"2 pkt – zapisanie poprawnego równania, np. {k1}n + {M} = {k2}(n − {diff_groups}), i wyznaczenie wartości niewiadomej (n = {n}).",
            f"3 pkt – obliczenie obecnej liczby harcerzy ({H}) i zapisanie odpowiedzi.",
        ],
        "grid_height_mm": 64.0,
    }
