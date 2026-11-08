"""Dział 7: Prędkość, droga, czas oraz obliczenia zegarowe i jednostki."""

from __future__ import annotations

from fractions import Fraction

from ..math_text import frac_tex, pl_num, shuffle_abcd
from .base import register_template


@register_template(
    template_id="predkosc_zegar_abcd",
    topic_id="predkosc_droga_czas",
    subtype="abcd",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – Informator CKE 2025 zad. 1",
)
def gen_zegar_opoznienie_abcd(rng):
    # Zegar spóźnia się o k minut w ciągu każdej godziny (stałe tempo). Ustawiono o godz. H0:00. Którą godzinę wskaże, gdy naprawdę będzie H1:M1?
    delay_per_h = rng.choice([4, 6, 8])  # dzieli się przez 4 kwadranse lub pół godziny!
    start_h = rng.choice([8, 9, 10])
    hours_whole = rng.randint(3, 5)
    half = 30  # 3.5 lub 4.5 h
    real_end_h = start_h + hours_whole
    real_end_m = half
    total_delay = delay_per_h * hours_whole + (delay_per_h // 2)

    total_mins_from_midnight = real_end_h * 60 + real_end_m - total_delay
    sh_h, sh_m = divmod(total_mins_from_midnight, 60)
    corr = f"${sh_h}:{sh_m:02d}$"

    # Dystraktory: dodanie zamiast odjęcia, pominięcie pół godziny, błędny przelicznik
    t_plus = real_end_h * 60 + real_end_m + total_delay
    t_no_half = real_end_h * 60 + real_end_m - (delay_per_h * hours_whole)
    t_more = total_mins_from_midnight - delay_per_h

    distractors = [
        f"${t_plus // 60}:{t_plus % 60:02d}$",
        f"${t_no_half // 60}:{t_no_half % 60:02d}$",
        f"${t_more // 60}:{t_more % 60:02d}$",
    ]
    choices, ans = shuffle_abcd(rng, corr, distractors)

    stem = (
        f"Kasia zauważyła, że stary zegar ścienny w ciągu każdej godziny spóźnia się dokładnie o ${delay_per_h}$ minuty "
        f"(w każdym kolejnym półgodzinnym odstępie opóźnienie narasta jednakowo). "
        f"Gdy poprawnie działający zegarek wskazywał godzinę ${start_h}:00$, Kasia nastawiła na zegarze ściennym tę samą godzinę."
    )
    command = (
        f"Którą godzinę wskaże ten zegar ścienny tego samego dnia w chwili, gdy poprawnie działający zegarek "
        f"będzie wskazywał godzinę ${real_end_h}:{real_end_m:02d}$? Wybierz właściwą odpowiedź spośród podanych."
    )

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Od godziny ${start_h}:00$ do godziny ${real_end_h}:{real_end_m:02d}$ upłynęło ${hours_whole}$ godziny i $30$ minut (czyli ${hours_whole},5$ godziny).",
            f"W ciągu ${hours_whole}$ pełnych godzin zegar spóźni się o ${hours_whole} \\cdot {delay_per_h} = {hours_whole * delay_per_h}$ min, "
            f"a w ciągu kolejnych $30$ minut – o dodatkowe ${delay_per_h // 2}$ min. Łączne opóźnienie wynosi ${total_delay}$ minut.",
            f"Od godziny ${real_end_h}:{real_end_m:02d}$ odejmujemy ${total_delay}$ minut i otrzymujemy godzinę {corr} (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="predkosc_pomiar_odcinkowy_abcd",
    topic_id="predkosc_droga_czas",
    subtype="abcd",
    points=1,
    difficulty=1,
    cke_ref="Styl CKE – CKE Grudzień 2024 zad. 14",
)
def gen_pomiar_odcinkowy_abcd(rng):
    # Samochód przejechał s km w t minut. Jaka była średnia prędkość w km/h?
    s_km, t_min = rng.choice([
        (3, 2),     # 90 km/h
        (4, 3),     # 80 km/h
        (5, 4),     # 75 km/h
        (6, 4),     # 90 km/h
        (8, 5),     # 96 km/h
        (7, 5),     # 84 km/h
    ])
    v_kmh = (s_km * 60) // t_min
    corr = f"${v_kmh}\\text{{ km/h}}$"
    distractors = [
        f"${v_kmh - 15}\\text{{ km/h}}$",
        f"${s_km * t_min * 10}\\text{{ km/h}}$",
        f"${v_kmh + 12}\\text{{ km/h}}$",
    ]
    choices, ans = shuffle_abcd(rng, corr, distractors)

    stem = (
        f"Odcinkowy pomiar prędkości zarejestrował, że samochód osobowy pokonał odcinek drogi ekspresowej "
        f"o długości ${s_km}$ km w czasie równym ${t_min}$ minuty."
    )
    command = "Średnia prędkość tego samochodu na tym odcinku drogi była równa – wybierz właściwą odpowiedź spośród podanych."

    return {
        "stem": stem,
        "command": command,
        "choices": choices,
        "correct_answer": ans,
        "solution_steps": [
            f"Zamieniamy czas na ułamek godziny: ${t_min}\\text{{ min}} =$ {frac_tex(str(t_min), '60')} $\\text{{ h}}$.",
            f"Obliczamy średnią prędkość ze wzoru $v =$ {frac_tex('s', 't')}: "
            f"$v = {s_km} :$ {frac_tex(str(t_min), '60')} $= {s_km} \\cdot$ {frac_tex('60', str(t_min))} $= {v_kmh}\\text{{ km/h}}$ (odpowiedź **{ans}**).",
        ],
    }


@register_template(
    template_id="predkosc_rowerzysta_pf",
    topic_id="predkosc_droga_czas",
    subtype="pf",
    points=1,
    difficulty=2,
    cke_ref="Styl CKE – CKE Maj 2021 zad. 10",
)
def gen_rowerzysta_pf(rng):
    # Rowerzysta jedzie ze stałą prędkością v km/h (np. 18 lub 36 km/h -> 5 lub 10 m/s)
    v_kmh = rng.choice([18, 27, 36, 54])
    v_ms = v_kmh * 1000 / 3600  # 5, 7.5, 10, 15 m/s
    mins = rng.choice([20, 40])
    dist_km = v_kmh * mins // 60

    s1_true = rng.choice([True, False])
    shown_ms = v_ms if s1_true else (v_kmh / 6.0)

    s2_true = rng.choice([True, False])
    shown_dist = dist_km if s2_true else (dist_km + 3)

    stem = f"Kolarz porusza się po płaskim odcinku szosy ze stałą prędkością równą ${v_kmh}\\text{{ km/h}}$."
    command = "Oceń prawdziwość podanych zdań. Wybierz P, jeśli zdanie jest prawdziwe, albo F – jeśli jest fałszywe."

    st1 = f"Prędkość tego kolarza wyrażona w metrach na sekundę jest równa ${pl_num(shown_ms)}\\text{{ m/s}}$."
    st2 = f"W ciągu ${mins}$ minut ten kolarz pokona drogę równą ${shown_dist}$ km."

    p1 = "P" if s1_true else "F"
    p2 = "P" if s2_true else "F"

    f_unit = frac_tex(str(v_kmh * 1000), "3600")
    return {
        "stem": stem,
        "command": command,
        "pf_statements": [(st1, p1), (st2, p2)],
        "correct_answer": p1 + p2,
        "solution_steps": [
            f"Przeliczamy jednostki prędkości: ${v_kmh}\\text{{ km/h}} =$ {f_unit} $\\text{{ m/s}} = {pl_num(v_ms)}\\text{{ m/s}}$ -> zdanie pierwsze: **{p1}**.",
            f"Czas ${mins}\\text{{ min}}$ to {frac_tex(str(mins), '60')} $= $ {frac_tex(str(mins // 20), '3')} godziny. "
            f"Droga wynosi $s = {v_kmh} \\cdot$ {frac_tex(str(mins // 20), '3')} $= {dist_km}\\text{{ km}}$ -> zdanie drugie: **{p2}**.",
        ],
    }


@register_template(
    template_id="predkosc_pociag_2pkt",
    topic_id="predkosc_droga_czas",
    subtype="otwarte_2pkt",
    points=2,
    difficulty=2,
    cke_ref="Styl CKE – CKE Maj 2023 zad. 17 / Maj 2022 zad. 17",
)
def gen_pociag_dlugosc_2pkt(rng):
    # Pociąg przebył ze stałą prędkością drogę S metrów w czasie t1 sekund.
    # Drogę równą swojej długości przebywa w czasie t2 sekund (mijając słup). Oblicz długość pociągu (lub prędkość w km/h)!
    v_ms = rng.choice([15, 20, 25])  # 54, 72 lub 90 km/h
    t1 = rng.choice([40, 50, 60])
    s1 = v_ms * t1
    t2 = rng.choice([12, 14, 16, 18])
    train_len = v_ms * t2

    stem = (
        f"Pociąg osobowy poruszający się ze stałą prędkością przebył drogę ${s1}$ metrów w czasie ${t1}$ sekund. "
        f"Przy zachowaniu tej samej stałej prędkości ten pociąg mija słup telegraficzny (czyli pokonuje drogę "
        f"równą swojej długości) w czasie ${t2}$ sekund."
    )
    command = "Oblicz długość tego pociągu (w metrach) oraz jego prędkość wyrażoną w km/h. Zapisz obliczenia."

    v_kmh = int(round(v_ms * 3.6))
    f_vt = frac_tex(str(s1), str(t1))
    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"Długość: {train_len} m, prędkość: {v_kmh} km/h",
        "solution_steps": [
            f"Obliczamy prędkość pociągu w metrach na sekundę: $v =$ {f_vt} $= {v_ms}\\text{{ m/s}}$.",
            f"Obliczamy długość pociągu: $d = v \\cdot t_2 = {v_ms}\\text{{ m/s}} \\cdot {t2}\\text{{ s}} = {train_len}\\text{{ m}}$.",
            f"Przeliczamy prędkość na km/h: ${v_ms}\\text{{ m/s}} = {v_ms} \\cdot 3,6\\text{{ km/h}} = {v_kmh}\\text{{ km/h}}$.",
            f"**Odpowiedź:** Pociąg ma długość ${train_len}$ m i jedzie z prędkością ${v_kmh}$ km/h.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie prędkości pociągu ({v_ms} m/s) lub ułożenie poprawnej proporcji na długość pociągu ({train_len} m).",
            f"2 pkt – poprawne obliczenie zarówno długości pociągu ({train_len} m), jak i prędkości w km/h ({v_kmh} km/h).",
        ],
        "grid_height_mm": 50.0,
    }


@register_template(
    template_id="predkosc_wycieczka_etapy_3pkt",
    topic_id="predkosc_droga_czas",
    subtype="otwarte_3pkt",
    points=3,
    difficulty=3,
    cke_ref="Styl CKE – CKE Maj 2021 zad. 18",
)
def gen_wycieczka_rowerowa_3pkt(rng):
    # Grupa turystów wyruszyła o godz. H0:M0 na trasę o długości D km.
    # Pierwsze s1 km jechała z prędkością v1 km/h, potem zrobiła przerwę P minut, a resztę trasy z prędkością v2 km/h.
    # O której godzinie dotarli do celu?
    v1, t1_min = rng.choice([(16, 45), (18, 40), (15, 36), (20, 45)])
    s1 = v1 * t1_min // 60
    pause_min = rng.choice([20, 25, 30])
    v2, t2_min = rng.choice([(12, 50), (15, 40), (18, 30), (16, 30)])
    s2 = v2 * t2_min // 60
    total_dist = s1 + s2

    start_h = rng.choice([8, 9])
    start_m = rng.choice([15, 30, 40])
    total_trip_min = t1_min + pause_min + t2_min

    end_total = start_h * 60 + start_m + total_trip_min
    end_h, end_m = divmod(end_total, 60)

    stem = (
        f"Grupa rowerzystów wyruszyła na wycieczkę o godzinie ${start_h}:{start_m:02d}$, aby pokonać trasę o łącznej długości "
        f"${total_dist}$ km. Pierwszy odcinek o długości ${s1}$ km rowerzyści przejechali ze stałą prędkością ${v1}\\text{{ km/h}}$. "
        f"Następnie zrobili przerwę trwającą ${pause_min}$ minut, po czym pozostałą część trasy pokonali ze stałą prędkością "
        f"${v2}\\text{{ km/h}}$."
    )
    command = "Oblicz, o której godzinie grupa rowerzystów dotarła do celu wycieczki. Zapisz obliczenia."

    ans_time = f"{end_h}:{end_m:02d}"
    return {
        "stem": stem,
        "command": command,
        "correct_answer": f"godz. {ans_time}",
        "solution_steps": [
            f"Obliczamy czas jazdy na pierwszym odcinku: $t_1 =$ {frac_tex(str(s1), str(v1))} $\\text{{ h}} =$ "
            f"{frac_tex(str(s1), str(v1))} $\\cdot 60\\text{{ min}} = {t1_min}\\text{{ min}}$.",
            f"Długość drugiego odcinka wynosi: $s_2 = {total_dist} - {s1} = {s2}$ km.",
            f"Obliczamy czas jazdy na drugim odcinku: $t_2 =$ {frac_tex(str(s2), str(v2))} $\\text{{ h}} = {t2_min}\\text{{ min}}$.",
            f"Łączny czas wycieczki wraz z przerwą wynosi: ${t1_min} + {pause_min} + {t2_min} = {total_trip_min}\\text{{ min}} = "
            f"{total_trip_min // 60}\\text{{ godz. }} {total_trip_min % 60}\\text{{ min}}$.",
            f"Dodajemy ten czas do godziny wyjazdu ${start_h}:{start_m:02d}$ i otrzymujemy godzinę **${ans_time}$**.",
        ],
        "scoring_scheme": [
            f"1 pkt – obliczenie czasu przejazdu pierwszego ({t1_min} min) albo drugiego ({t2_min} min) odcinka trasy.",
            f"2 pkt – obliczenie łącznego czasu trwania całej wycieczki wraz z postojem ({total_trip_min} min).",
            f"3 pkt – poprawne wyznaczenie godziny przyjazdu na metę ({ans_time}).",
        ],
        "grid_height_mm": 62.0,
    }
