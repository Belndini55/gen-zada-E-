"""Dział 5: Wyrażenia algebraiczne – zapisywanie, przekształcanie i wartości liczbowe."""

from __future__ import annotations

from ..math_text import frac_tex, pl_num, shuffle_abcd
from .base import register_template


@register_template(
    template_id="wyrazenia_wartosc_min_abcd",
    topic_id="wyrazenia_algebraiczne",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2022 zad. 7",
)
def gen_wartosc_wyrazenia_min_abcd(rng):
    # Dane jest wyrażenie (n^4 - c)/d lub (c - n^2)/d dla zestawu liczb {-3, -1, 0, 2}
    mode = rng.choice(["even_pow_min", "neg_sq_max"])
    c = rng.choice([3, 5, 7])
    d = rng.choice([2, 4, 6])

    if mode == "even_pow_min":
        # (n^4 - c)/d przyjmuje najmniejszą wartość dla n = 0! Uczniowie często mylnie wybierają -3.
        expr_tex = frac_tex(f"n^4 - {c}", str(d))
        nums = [-3, -1, 0, 2]
        corr = "$0$"
        distractors = ["$-3$", "$-1$", "$2$"]
        q_word = "najmniejsza"
        expl = (
            f"Ponieważ wykładnik potęgi ($4$) jest parzysty, dla każdej liczby rzeczywistej $n \\neq 0$ zachodzi $n^4 > 0$, "
            f"natomiast dla $n = 0$ mamy $0^4 = 0$. Zatem licznik $n^4 - {c}$ (a więc i cały ułamek o dodatnim mianowniku ${d}$) "
            f"przyjmuje najmniejszą wartość równą $-${frac_tex(str(c), str(d))} dla $n = 0$."
        )
    else:
        # (c - n^2)/d przyjmuje największą wartość dla n = 0, a najmniejszą dla n = -3!
        expr_tex = frac_tex(f"{c} - n^2", str(d))
        nums = [-3, -2, 0, 2]
        corr = "$-3$"
        distractors = ["$-2$", "$0$", "$2$"]
        q_word = "najmniejsza"
        expl = (
            f"Sprawdzamy wartości $n^2$: dla $n = -3$ mamy $(-3)^2 = 9$, dla $n = -2$ oraz $n = 2$ mamy $n^2 = 4$, "
            f"a dla $n = 0$ mamy $0^2 = 0$. Najmniejszy licznik ${c} - 9 = {c - 9}$ otrzymujemy dla $n = -3$."
        )

    choices, ans = shuffle_abcd(rng, corr, distractors)
    nums_str = ",  ".join(f"${pl_num(x)}$" for x in nums)

    stem = f"Dane jest wyrażenie {expr_tex} oraz cztery liczby: {nums_str}."
    command = f"Dla której spośród podanych liczb wartość tego wyrażenia jest {q_word}? Wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            expl,
            f"Poprawna odpowiedź to **{ans}** ({corr}).",
        ],
    }


@register_template(
    template_id="wyrazenia_opis_slowny_abcd",
    topic_id="wyrazenia_algebraiczne",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Wzorzec: CKE Maj 2023 zad. 8",
)
def gen_opis_slowny_abcd(rng):
    a = rng.randint(3, 6)
    b = rng.randint(4, 9)
    c = rng.randint(2, 5)
    d = rng.randint(3, 8)

    # Ania do liczby x dodała b, a wynik pomnożyła przez a -> a(x + b)
    # Bartek liczbę y pomnożył przez c, a do wyniku dodał d -> cy + d
    corr = f"${a}(x + {b})$ oraz ${c}y + {d}$"
    d1 = f"${a}x + {b}$ oraz ${c}y + {d}$"
    d2 = f"${a}(x + {b})$ oraz ${c}(y + {d})$"
    d3 = f"${a}x + {b}$ oraz ${c}(y + {d})$"

    choices, ans = shuffle_abcd(rng, corr, [d1, d2, d3])

    stem = (
        f"Ania pomyślała pewną liczbę $x$, dodała do niej ${b}$, a otrzymany wynik pomnożyła przez ${a}$.\n"
        f"Bartek pomyślał pewną liczbę $y$, pomnożył ją przez ${c}$, a następnie do otrzymanego iloczynu dodał ${d}$."
    )
    command = "Która para wyrażeń algebraicznych poprawnie opisuje wyniki otrzymane przez Anię i Bartka? Wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Ania najpierw wykonała dodawanie $(x + {b})$, a potem całą sumę pomnożyła przez ${a}$, co zapisujemy jako ${a}(x + {b})$.",
            f"Bartek najpierw pomnożył $y$ przez ${c}$ (otrzymując ${c}y$), a potem dodał ${d}$, co daje ${c}y + {d}$.",
            f"Poprawna para wyrażeń to {corr} (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="wyrazenia_redukcja_pf",
    topic_id="wyrazenia_algebraiczne",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Wzorzec: CKE Maj 2023 zad. 3",
)
def gen_redukcja_pf(rng):
    # W = 3x(x - a) - (x^2 - bx) = 3x^2 - 3ax - x^2 + bx = 2x^2 + (b - 3a)x
    a = rng.randint(2, 5)
    b = 3 * a + rng.choice([2, 4, -2])
    coef_x2 = 2
    coef_x = b - 3 * a
    sign_x = "+" if coef_x >= 0 else "-"

    s1_true = rng.choice([True, False])
    shown_coef_x = coef_x if s1_true else (-b - 3 * a)  # klasyczny błąd ze znakiem po minusie przed nawiasem!
    sh_sign = "+" if shown_coef_x >= 0 else "-"

    x_val = -2
    real_val = coef_x2 * (x_val ** 2) + coef_x * x_val
    s2_true = rng.choice([True, False])
    shown_val = real_val if s2_true else (coef_x2 * (-4) + coef_x * x_val)

    stem = f"Dane jest wyrażenie algebraiczne $W = 3x(x - {a}) - (x^2 - {b}x)$."
    command = "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe."

    st1 = f"Po wykonaniu działań i redukcji wyrazów podobnych wyrażenie $W$ przyjmuje postać $2x^2 {sh_sign} {abs(shown_coef_x)}x$."
    st2 = f"Dla $x = -2$ wartość liczbowa wyrażenia $W$ jest równa ${pl_num(shown_val)}$."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    return {
        "stem": stem,
        "command": command,
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": [
            f"Opuszczamy nawiasy, pamiętając o zmianie znaków po minusie: "
            f"$W = 3x^2 - {3 * a}x - x^2 + {b}x = 2x^2 {sign_x} {abs(coef_x)}x$ -> zdanie pierwsze: **{p1}**.",
            f"Podstawiamy $x = -2$: $W = 2 \\cdot (-2)^2 {sign_x} {abs(coef_x)} \\cdot (-2) = 8 + ({pl_num(coef_x * (-2))}) = {pl_num(real_val)}$ -> zdanie drugie: **{p2}**.",
        ],
    }


@register_template(
    template_id="wyrazenia_prostokat_2pkt",
    topic_id="wyrazenia_algebraiczne",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Wzorzec: CKE Czerwiec 2023 zad. 16",
)
def gen_wyrazenia_obwod_2pkt(rng):
    # Trójkąt ma boki: x, 2x - a oraz x + b. Zapisz obwód w najprostszej postaci i oblicz boki dla obwodu L albo wartość dla x=k.
    a = rng.randint(2, 5)
    b = rng.randint(4, 9)
    # Zadbajmy o nierówność trójkąta dla x >= a+2
    x_val = a + rng.randint(4, 7)
    perim_val = 4 * x_val - a + b
    diff_const = b - a
    sign_c = "+" if diff_const >= 0 else "-"

    stem = (
        f"Długości boków pewnego trójkąta wyrażone w centymetrach opisano za pomocą wyrażeń algebraicznych:\n"
        f"$x$,   $2x - {a}$   oraz   $x + {b}$   (gdzie $x > {a}$)."
    )
    command = (
        f"Zapisz w najprostszej postaci wyrażenie algebraiczne opisujące obwód tego trójkąta, "
        f"a następnie oblicz ten obwód dla $x = {x_val}$ cm. Zapisz obliczenia."
    )

    simp_str = f"4x {sign_c} {abs(diff_const)}" if diff_const != 0 else "4x"
    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"{simp_str}; obwód = {perim_val} cm",
        "solution_steps": [
            f"Zapisujemy sumę długości trzech boków trójkąta i redukujemy wyrazy podobne: "
            f"$Obw = x + (2x - {a}) + (x + {b}) = {simp_str}$.",
            f"Podstawiamy $x = {x_val}$: $Obw = 4 \\cdot {x_val} {sign_c} {abs(diff_const)} = {perim_val}$ (cm).",
            f"**Odpowiedź:** Wyrażenie opisujące obwód to ${simp_str}$, a dla $x = {x_val}$ cm obwód wynosi ${perim_val}$ cm.",
        ],
        "scoring_scheme": [
            f"1 pkt – zapisanie sumy boków i poprawne uproszczenie wyrażenia do postaci {simp_str}.",
            f"2 pkt – poprawne obliczenie wartości obwodu dla x = {x_val} ({perim_val} cm).",
        ],
        "grid_height_mm": 48.0,
    }


@register_template(
    template_id="wyrazenia_uzasadnij_kolejne_3pkt",
    topic_id="wyrazenia_algebraiczne",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Wzorzec: CKE Próbny 2021 zad. 17",
)
def gen_uzasadnij_kolejne_liczby_3pkt(rng):
    # Uzasadnij, że suma czterech kolejnych liczb nieparzystych jest podzielna przez 8 (lub trzech kolejnych parzystych przez 6)
    variant = rng.choice(["four_odd_div8", "three_consec_even_plus"])
    if variant == "four_odd_div8":
        stem = "Rozważmy dowolne cztery kolejne liczby całkowite nieparzyste."
        command = "Uzasadnij, że suma każdych czterech kolejnych liczb całkowitych nieparzystych jest podzielna przez $8$. Zapisz przekształcenia algebraiczne i wniosek."
        ans = "Suma ma postać 8(n + 2), gdzie n jest liczbą całkowitą, więc dzieli się przez 8."
        steps = [
            "Oznaczmy najmniejszą z czterech kolejnych liczb całkowitych nieparzystych jako $2n + 1$, gdzie $n$ jest dowolną liczbą całkowitą.",
            "Wówczas kolejne trzy liczby nieparzyste to: $2n + 3$, $2n + 5$ oraz $2n + 7$.",
            "Obliczamy ich sumę: $(2n + 1) + (2n + 3) + (2n + 5) + (2n + 7) = 8n + 16$.",
            "Wyłączamy czynnik $8$ przed nawias: $8n + 16 = 8(n + 2)$.",
            "Ponieważ $n$ jest liczbą całkowitą, to $n + 2$ również jest liczbą całkowitą, zatem iloczyn $8(n + 2)$ jest podzielny przez $8$, co należało uzasadnić.",
        ]
        rubric = [
            "1 pkt – poprawne zapisanie czterech kolejnych liczb nieparzystych za pomocą wyrażeń algebraicznych (np. 2n+1, 2n+3, 2n+5, 2n+7).",
            "2 pkt – obliczenie sumy tych wyrażeń (8n + 16).",
            "3 pkt – wyłączenie liczby 8 przed nawias: 8(n + 2) i sformułowanie poprawnego wniosku o podzielności.",
        ]
    else:
        # Liczba dwucyfrowa + liczba powstała po przestawieniu cyfr jest podzielna przez 11
        stem = (
            "W pewnej liczbie naturalnej dwucyfrowej cyfrę dziesiątek oznaczmy przez $a$, a cyfrę jedności przez $b$ "
            "(gdzie $a, b \\in \\{1, 2, \\dots, 9\\}$). Po przestawieniu cyfr tej liczby otrzymano drugą liczbę dwucyfrową."
        )
        command = "Uzasadnij, że suma obu tych liczb dwucyfrowych jest podzielna przez $11$. Zapisz przekształcenia i wniosek."
        ans = "Suma wynosi (10a + b) + (10b + a) = 11(a + b), więc jest podzielna przez 11."
        steps = [
            "Pierwsza liczba dwucyfrowa ma wartość $10a + b$.",
            "Po zamianie miejscami cyfry dziesiątek i cyfry jedności otrzymujemy drugą liczbę o wartości $10b + a$.",
            "Dodajemy obie liczby i redukujemy wyrazy podobne: $(10a + b) + (10b + a) = 11a + 11b = 11(a + b)$.",
            "Ponieważ $a + b$ jest liczbą całkowitą (naturalną), iloczyn $11(a + b)$ jest podzielny przez $11$, co kończy uzasadnienie.",
        ]
        rubric = [
            "1 pkt – poprawne zapisanie wartości obu liczb dwucyfrowych jako 10a + b oraz 10b + a.",
            "2 pkt – dodanie obu wyrażeń i redukcja wyrazów podobnych do postaci 11a + 11b.",
            "3 pkt – zapisanie wyniku jako iloczynu 11(a + b) i sformułowanie pełnego wniosku.",
        ]

    return {
        "stem": stem,
        "command": command,
        "correct_answer": ans,
        "solution_steps": steps,
        "scoring_scheme": rubric,
        "grid_height_mm": 60.0,
    }
