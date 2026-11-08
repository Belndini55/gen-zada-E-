"""Baza autentycznych arkuszy CKE Egzaminu Ósmoklasisty z matematyki (2019–2026)
oraz silnik statystyczny rozkładu prawdopodobieństwa działów i typów zadań.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .models import TOPICS


@dataclass(frozen=True)
class HistoricalTaskEntry:
    """Pojedyncze zadanie z oficjalnego arkusza CKE E8."""
    number: int
    topic_id: str
    subtype: str  # "abcd", "pf", "ab_cd", "uzasadnienie", "otwarte_2pkt", "otwarte_3pkt"
    points: int
    label: str


@dataclass(frozen=True)
class HistoricalExamSession:
    """Metadane i pełny rozkład zadań oficjalnego arkusza CKE."""
    session_id: str
    code: str
    name: str
    date_str: str
    formula_years: str
    duration_min: int
    tasks: Tuple[HistoricalTaskEntry, ...]

    @property
    def total_tasks(self) -> int:
        return len(self.tasks)

    @property
    def total_points(self) -> int:
        return sum(t.points for t in self.tasks)

    @property
    def closed_count(self) -> int:
        return sum(1 for t in self.tasks if t.points == 1)

    @property
    def open_count(self) -> int:
        return sum(1 for t in self.tasks if t.points > 1)


# ---------------------------------------------------------------------------
# Pełny katalog 12 oficjalnych arkuszy CKE z lat 2019–2026 (241 zadań CKE)
# ---------------------------------------------------------------------------
HISTORICAL_CKE_EXAMS: Tuple[HistoricalExamSession, ...] = (
    # 1. CKE Maj 2026 (termin główny, OMAP-100-2605) – 20 zadań, 30 pkt
    HistoricalExamSession(
        session_id="cke_2026_05",
        code="OMAP-100-2605",
        name="CKE Maj 2026 (termin główny)",
        date_str="12 maja 2026 r.",
        formula_years="2025–2026",
        duration_min=125,
        tasks=(
            HistoricalTaskEntry(1, "statystyka_diagramy", "abcd", 1, "Diagram kołowy – podział procentowy testu (40 zadań)"),
            HistoricalTaskEntry(2, "liczby_dzialania", "abcd", 1, "Wyznaczanie NWD i NWW dwóch liczb"),
            HistoricalTaskEntry(3, "pierwiastki", "abcd", 1, "Wartość wyrażenia z pierwiastkiem równa zeru"),
            HistoricalTaskEntry(4, "potegi_notacja", "abcd", 1, "Iloczyn potęg o dwóch podstawach (2^5 · 3 · 3^4 · 2^3)"),
            HistoricalTaskEntry(5, "procenty_proporcje", "abcd", 1, "Wyrażenie na zakupy z dwiema zniżkami procentowymi"),
            HistoricalTaskEntry(6, "prawdopodobienstwo", "ab_cd", 1, "Kule 1..11 – parzystość sumy wylosowanych kul"),
            HistoricalTaskEntry(7, "rownania_tekstowe", "abcd", 1, "Kosze z jabłkami i pomarańczami (suma i różnica)"),
            HistoricalTaskEntry(8, "wyrazenia_algebraiczne", "ab_cd", 1, "Wzór na sumę S = 1/2 n(n+1) – podstawienie i przekształcenie"),
            HistoricalTaskEntry(9, "statystyka_diagramy", "abcd", 1, "Trzecia liczba z dwóch średnich arytmetycznych"),
            HistoricalTaskEntry(10, "geometria_plaska", "pf", 1, "Trójkąt równoboczny o boku 2 cm – wysokość i pole"),
            HistoricalTaskEntry(11, "geometria_plaska", "abcd", 1, "Kąty czworokąta z zależności między miarami"),
            HistoricalTaskEntry(12, "uklad_wspolrzednych", "pf", 1, "Odległości punktów na kratce (strony świata)"),
            HistoricalTaskEntry(13, "geometria_plaska", "abcd", 1, "Pięciokąt z kwadratu i trójkąta – pole kwadratu"),
            HistoricalTaskEntry(14, "geometria_przestrzenna", "abcd", 1, "Pole powierzchni słupka z trzech sześcianów"),
            HistoricalTaskEntry(15, "rownania_tekstowe", "otwarte_2pkt", 2, "Kartki origami w czterech kolorach (160 szt.)"),
            HistoricalTaskEntry(16, "predkosc_droga_czas", "otwarte_3pkt", 3, "Uzasadnij, że przejazd Jodłowo–Dębina trwał > 1 h"),
            HistoricalTaskEntry(17, "statystyka_diagramy", "otwarte_3pkt", 3, "Tabela Dnia Sportu – brakująca liczba i procent całości"),
            HistoricalTaskEntry(18, "geometria_przestrzenna", "otwarte_2pkt", 2, "Stosunek objętości ostrosłupa wpisanego w sześcian"),
            HistoricalTaskEntry(19, "geometria_plaska", "otwarte_3pkt", 3, "Łąka w kształcie trapezu – opakowania nasion i koszt"),
            HistoricalTaskEntry(20, "geometria_plaska", "otwarte_3pkt", 3, "Obwód równoległoboku z rozciętego prostokąta"),
        ),
    ),
    # 2. CKE Czerwiec 2026 (termin dodatkowy, OMAP-100-2606) – 20 zadań, 30 pkt
    HistoricalExamSession(
        session_id="cke_2026_06",
        code="OMAP-100-2606",
        name="CKE Czerwiec 2026 (termin dodatkowy)",
        date_str="czerwiec 2026 r.",
        formula_years="2025–2026",
        duration_min=125,
        tasks=(
            HistoricalTaskEntry(1, "statystyka_diagramy", "abcd", 1, "Średnia arytmetyczna z diagramu słupkowego"),
            HistoricalTaskEntry(2, "procenty_proporcje", "abcd", 1, "Podział kwoty w zadanym stosunku"),
            HistoricalTaskEntry(3, "rownania_tekstowe", "abcd", 1, "Rozwiązanie równania liniowego z nawiasami"),
            HistoricalTaskEntry(4, "potegi_notacja", "abcd", 1, "Największa wartość wyrażenia potęgowego"),
            HistoricalTaskEntry(5, "prawdopodobienstwo", "abcd", 1, "Zliczanie liczb o zadanej sumie cyfr"),
            HistoricalTaskEntry(6, "pierwiastki", "abcd", 1, "Wyrażenie z pierwiastkiem sześciennym z liczby ujemnej"),
            HistoricalTaskEntry(7, "liczby_dzialania", "uzasadnienie", 1, "Podzielność sumy kolejnych liczb całkowitych"),
            HistoricalTaskEntry(8, "prawdopodobienstwo", "pf", 1, "Prawdopodobieństwo losowania dnia miesiąca z kalendarza"),
            HistoricalTaskEntry(9, "liczby_dzialania", "ab_cd", 1, "Kolejność działań na ułamkach zwykłych i dziesiętnych"),
            HistoricalTaskEntry(10, "predkosc_droga_czas", "abcd", 1, "Droga, prędkość i czas między godzinami zegarowymi"),
            HistoricalTaskEntry(11, "uklad_wspolrzednych", "pf", 1, "Dwa odcinki w układzie współrzędnych – długość i prostopadłość"),
            HistoricalTaskEntry(12, "geometria_plaska", "abcd", 1, "Obwód równoległoboku z przekątną prostopadłą do boku"),
            HistoricalTaskEntry(13, "geometria_plaska", "abcd", 1, "Osie symetrii figury ułożonej z patyczków"),
            HistoricalTaskEntry(14, "geometria_przestrzenna", "ab_cd", 1, "Siatka sześcianu – obwód siatki a pole powierzchni"),
            HistoricalTaskEntry(15, "liczby_dzialania", "otwarte_2pkt", 2, "Dopełnienie ułamków do całości (część pozostałej grupy)"),
            HistoricalTaskEntry(16, "rownania_tekstowe", "otwarte_3pkt", 3, "Gra w rzuty do kosza – punkty i relacje"),
            HistoricalTaskEntry(17, "procenty_proporcje", "otwarte_3pkt", 3, "Cena za litr soku w dwóch promocjach sklepowych"),
            HistoricalTaskEntry(18, "geometria_plaska", "otwarte_2pkt", 2, "Miary kątów trójkąta przy prostych równoległych"),
            HistoricalTaskEntry(19, "geometria_plaska", "otwarte_3pkt", 3, "Pole trapezu prostokątnego z kątem 45°"),
            HistoricalTaskEntry(20, "geometria_przestrzenna", "otwarte_3pkt", 3, "Objętość i pole graniastosłupa trójkątnego"),
        ),
    ),
    # 3. CKE Maj 2025 (termin główny, OMAP-100-2505) – 21 zadań, 30 pkt
    HistoricalExamSession(
        session_id="cke_2025_05",
        code="OMAP-100-2505",
        name="CKE Maj 2025 (termin główny)",
        date_str="14 maja 2025 r.",
        formula_years="2025–2026",
        duration_min=125,
        tasks=(
            HistoricalTaskEntry(1, "statystyka_diagramy", "ab_cd", 1, "Diagram oszczędności na deskorolkę – procent kwoty"),
            HistoricalTaskEntry(2, "liczby_dzialania", "abcd", 1, "Wyrażenie z ułamkiem mieszanym i dzielnikiem ujemnym"),
            HistoricalTaskEntry(3, "liczby_dzialania", "abcd", 1, "Reszta z dzielenia – rozpoznawanie liczby w zbiorze"),
            HistoricalTaskEntry(4, "statystyka_diagramy", "ab_cd", 1, "Średnia ważona dwóch grup uczniów"),
            HistoricalTaskEntry(5, "wyrazenia_algebraiczne", "abcd", 1, "Wyznaczenie wielkości ze wzoru algebraicznego"),
            HistoricalTaskEntry(6, "wyrazenia_algebraiczne", "abcd", 1, "Układanie wyrażenia algebraicznego z opisu słownego"),
            HistoricalTaskEntry(7, "pierwiastki", "pf", 1, "Ocena prawdziwości wyrażeń z pierwiastkami"),
            HistoricalTaskEntry(8, "potegi_notacja", "abcd", 1, "Zapis ilorazu i iloczynu potęg o wspólnej podstawie"),
            HistoricalTaskEntry(9, "predkosc_droga_czas", "abcd", 1, "Prędkość, droga i czas – zamiana m/s i km/h"),
            HistoricalTaskEntry(10, "prawdopodobienstwo", "abcd", 1, "Prawdopodobieństwo wylosowania losu z przedziału numerów"),
            HistoricalTaskEntry(11, "geometria_plaska", "pf", 1, "Podział trójkąta i porównanie pól trójkątów"),
            HistoricalTaskEntry(12, "liczby_dzialania", "pf", 1, "Współrzędne punktów podziału odcinka na osi liczbowej"),
            HistoricalTaskEntry(13, "geometria_plaska", "abcd", 1, "Obwód trapezu zbudowanego z mniejszych figur"),
            HistoricalTaskEntry(14, "uklad_wspolrzednych", "abcd", 1, "Brakujący wierzchołek figury w układzie współrzędnych"),
            HistoricalTaskEntry(15, "geometria_przestrzenna", "abcd", 1, "Pole powierzchni całkowitej prostopadłościanu"),
            HistoricalTaskEntry(16, "liczby_dzialania", "otwarte_2pkt", 2, "Trzeci składnik sumy ułamków zwykłych i dziesiętnych"),
            HistoricalTaskEntry(17, "rownania_tekstowe", "otwarte_3pkt", 3, "Plakaty Basi, Marka i Andrzeja – równanie z relacji"),
            HistoricalTaskEntry(18, "geometria_plaska", "otwarte_2pkt", 2, "Miary kątów trapezu ABCD z podziału przekątną"),
            HistoricalTaskEntry(19, "geometria_plaska", "otwarte_2pkt", 2, "Stosunek pól figur i skala wymiarów"),
            HistoricalTaskEntry(20, "geometria_plaska", "otwarte_3pkt", 3, "Pole czworokąta AECF wpisanego w kwadrat/prostokąt"),
            HistoricalTaskEntry(21, "geometria_przestrzenna", "otwarte_3pkt", 3, "Suma długości wszystkich krawędzi ostrosłupa"),
        ),
    ),
    # 4. CKE Czerwiec 2025 (termin dodatkowy, OMAP-100-2506) – 21 zadań, 30 pkt
    HistoricalExamSession(
        session_id="cke_2025_06",
        code="OMAP-100-2506",
        name="CKE Czerwiec 2025 (termin dodatkowy)",
        date_str="czerwiec 2025 r.",
        formula_years="2025–2026",
        duration_min=125,
        tasks=(
            HistoricalTaskEntry(1, "statystyka_diagramy", "abcd", 1, "Brakująca wartość z 5 dni na podstawie średniej"),
            HistoricalTaskEntry(2, "liczby_dzialania", "abcd", 1, "Skracanie ułamka po wielokrotnym połowieniu"),
            HistoricalTaskEntry(3, "predkosc_droga_czas", "abcd", 1, "Dzielenie z resztą w jednostkach czasu (nagrania)"),
            HistoricalTaskEntry(4, "potegi_notacja", "ab_cd", 1, "Iloraz potęg i mnożnik przy wspólnej podstawie"),
            HistoricalTaskEntry(5, "liczby_dzialania", "uzasadnienie", 1, "Podzielność sumy i iloczynu liczb naturalnych"),
            HistoricalTaskEntry(6, "prawdopodobienstwo", "abcd", 1, "Losowanie karty z figurą geometryczną"),
            HistoricalTaskEntry(7, "procenty_proporcje", "abcd", 1, "Odtwarzanie całości z jej ułamka / procentu"),
            HistoricalTaskEntry(8, "rownania_tekstowe", "abcd", 1, "Równanie liniowe pierwszego stopnia z ułamkiem"),
            HistoricalTaskEntry(9, "geometria_plaska", "uzasadnienie", 1, "Porównanie pól kwadratu i rombu o tym samym boku"),
            HistoricalTaskEntry(10, "geometria_plaska", "pf", 1, "Wnioski o kątach wewnętrznych trójkąta"),
            HistoricalTaskEntry(11, "wyrazenia_algebraiczne", "abcd", 1, "Zapis wyrażenia algebraicznego z opisu"),
            HistoricalTaskEntry(12, "geometria_plaska", "abcd", 1, "Pole trapezu prostokątnego"),
            HistoricalTaskEntry(13, "geometria_przestrzenna", "pf", 1, "Sześcian – pole powierzchni, objętość i krawędź"),
            HistoricalTaskEntry(14, "uklad_wspolrzednych", "abcd", 1, "Rozpoznanie czworokąta w układzie współrzędnych"),
            HistoricalTaskEntry(15, "geometria_przestrzenna", "abcd", 1, "Sześcienne kostki w pudełku prostopadłościennym"),
            HistoricalTaskEntry(16, "procenty_proporcje", "otwarte_2pkt", 2, "Składane zmiany procentowe – porównanie cen (80% i 120%)"),
            HistoricalTaskEntry(17, "liczby_dzialania", "otwarte_3pkt", 3, "Ułamek z reszty przy kolejnych wydatkach z budżetu"),
            HistoricalTaskEntry(18, "predkosc_droga_czas", "otwarte_2pkt", 2, "Porównanie czasów podróży dwóch uczestników"),
            HistoricalTaskEntry(19, "liczby_dzialania", "otwarte_2pkt", 2, "Iloczyn współrzędnych punktów na osi liczbowej"),
            HistoricalTaskEntry(20, "geometria_plaska", "otwarte_3pkt", 3, "Pole trójkąta równoramiennego z obwodu i różnicy boków"),
            HistoricalTaskEntry(21, "geometria_przestrzenna", "otwarte_3pkt", 3, "Wysokość ostrosłupa prawidłowego z obwodu podstawy i objętości"),
        ),
    ),
    # 5. CKE Grudzień 2024 (oficjalny próbny CKE nowej formuły, OMAP-100-2412) – 21 zadań, 30 pkt
    HistoricalExamSession(
        session_id="cke_2024_12",
        code="OMAP-100-2412",
        name="CKE Grudzień 2024 (próbny CKE)",
        date_str="grudzień 2024 r.",
        formula_years="2025–2026",
        duration_min=125,
        tasks=(
            HistoricalTaskEntry(1, "procenty_proporcje", "pf", 1, "Odczyt i przeliczenie masy składników z etykiety"),
            HistoricalTaskEntry(2, "potegi_notacja", "pf", 1, "Prawdziwość równości dla iloczynu i ilorazu potęg"),
            HistoricalTaskEntry(3, "wyrazenia_algebraiczne", "abcd", 1, "Mnożenie nawiasów i redukcja wyrazów podobnych"),
            HistoricalTaskEntry(4, "pierwiastki", "abcd", 1, "Porównywanie liczb z pierwiastkami kwadratowymi"),
            HistoricalTaskEntry(5, "prawdopodobienstwo", "abcd", 1, "Prawdopodobieństwo wylosowania kuli z opisu krotności"),
            HistoricalTaskEntry(6, "liczby_dzialania", "abcd", 1, "Zbiór liczb na osi liczbowej"),
            HistoricalTaskEntry(7, "statystyka_diagramy", "abcd", 1, "Odtworzenie liczebności całości z diagramu kołowego"),
            HistoricalTaskEntry(8, "statystyka_diagramy", "abcd", 1, "Średnia arytmetyczna po zmianie liczebności zbioru"),
            HistoricalTaskEntry(9, "geometria_plaska", "abcd", 1, "Pole kwadratu z obwodu odciętego prostokąta"),
            HistoricalTaskEntry(10, "geometria_plaska", "abcd", 1, "Miara kąta przy prostych równoległych i prostopadłych"),
            HistoricalTaskEntry(11, "geometria_plaska", "abcd", 1, "Pole czworokąta z prostopadłych przekątnych"),
            HistoricalTaskEntry(12, "geometria_plaska", "uzasadnienie", 1, "Przystawanie trójkątów (Tak/Nie + cecha)"),
            HistoricalTaskEntry(13, "geometria_przestrzenna", "abcd", 1, "Objętość graniastosłupa z relacji krawędzi"),
            HistoricalTaskEntry(14, "predkosc_droga_czas", "abcd", 1, "Średnia prędkość na odcinkowym pomiarze prędkości"),
            HistoricalTaskEntry(15, "geometria_plaska", "pf", 1, "Cięciwa okręgu, obwód trójkąta i długość okręgu"),
            HistoricalTaskEntry(16, "liczby_dzialania", "otwarte_2pkt", 2, "Wspólne wielokrotności (NWW) – ilu klientów dostało 2 gratisy"),
            HistoricalTaskEntry(17, "rownania_tekstowe", "otwarte_3pkt", 3, "Wykazanie równoboczności trójkąta z boków algebraicznych"),
            HistoricalTaskEntry(18, "geometria_plaska", "otwarte_3pkt", 3, "Pole trapezu równoramiennego z ramienia i podstaw"),
            HistoricalTaskEntry(19, "rownania_tekstowe", "otwarte_3pkt", 3, "Ceny trzech przedmiotów z zależności sumarycznych"),
            HistoricalTaskEntry(20, "geometria_przestrzenna", "otwarte_2pkt", 2, "Pole powierzchni bocznej graniastosłupa z siatki"),
            HistoricalTaskEntry(21, "geometria_przestrzenna", "otwarte_2pkt", 2, "Liczba sześciennych foremek z wody (część pojemności)"),
        ),
    ),
    # 6. CKE Maj 2024 (termin główny, OMAP-100-2405) – 19 zadań, 25 pkt
    HistoricalExamSession(
        session_id="cke_2024_05",
        code="OMAP-100-2405",
        name="CKE Maj 2024 (termin główny)",
        date_str="15 maja 2024 r.",
        formula_years="2021–2024",
        duration_min=100,
        tasks=(
            HistoricalTaskEntry(1, "statystyka_diagramy", "pf", 1, "Diagram nauki hiszpańskiego – czas łączny i zmiana %"),
            HistoricalTaskEntry(2, "liczby_dzialania", "abcd", 1, "Liczba ułamków o mianowniku 4 między 3 a 5"),
            HistoricalTaskEntry(3, "statystyka_diagramy", "pf", 1, "Średnia trzech liczb (12, 14, k) równa 16"),
            HistoricalTaskEntry(4, "liczby_dzialania", "ab_cd", 1, "Iloczyn i suma ułamków dodatnich i ujemnych"),
            HistoricalTaskEntry(5, "geometria_plaska", "abcd", 1, "Kąt w trapezie z odcinkiem równoległym do ramienia"),
            HistoricalTaskEntry(6, "wyrazenia_algebraiczne", "abcd", 1, "Równoważne przekształcenia wzoru 5x = y/w"),
            HistoricalTaskEntry(7, "potegi_notacja", "pf", 1, "Działania na potęgach 3·9^5 oraz 2^8·2^7 / 2^10"),
            HistoricalTaskEntry(8, "prawdopodobienstwo", "abcd", 1, "Balony w pudełku – losowanie trzeciego po dwóch czerwonych"),
            HistoricalTaskEntry(9, "wyrazenia_algebraiczne", "abcd", 1, "Przekształcenie wyrażenia x(x+4) - 3(2x-5)"),
            HistoricalTaskEntry(10, "predkosc_droga_czas", "abcd", 1, "Czas odjazdu pociągu Olsztyn–Gdynia z opóźnieniem"),
            HistoricalTaskEntry(11, "procenty_proporcje", "pf", 1, "Wykres proporcjonalności zużycia farby do pola powierzchni"),
            HistoricalTaskEntry(12, "uklad_wspolrzednych", "abcd", 1, "Przesunięcie punktu P1(-1,-2) o wektor (+4, +3)"),
            HistoricalTaskEntry(13, "geometria_plaska", "abcd", 1, "Stosunek boków prostokąta podzielonego na 6 kwadratów"),
            HistoricalTaskEntry(14, "geometria_plaska", "pf", 1, "Wydłużenie przyprostokątnych do trójkąta o polu 200 cm^2"),
            HistoricalTaskEntry(15, "geometria_przestrzenna", "ab_cd", 1, "Pole ściany bocznej 2/9 P a pole podstawy ostrosłupa"),
            HistoricalTaskEntry(16, "rownania_tekstowe", "otwarte_2pkt", 2, "Zestawy puzzli Eli (2/5) i Ani (1/3) – razem 440 szt."),
            HistoricalTaskEntry(17, "geometria_plaska", "otwarte_3pkt", 3, "Prostokąt podzielony na 3 trójkąty – pole trapezu ABCE"),
            HistoricalTaskEntry(18, "procenty_proporcje", "otwarte_3pkt", 3, "Sprzedaż 120 kg truskawek w 3 rodzajach opakowań"),
            HistoricalTaskEntry(19, "geometria_przestrzenna", "otwarte_2pkt", 2, "Różnica wysokości dwóch wież ze sześcianów i ostrosłupa"),
        ),
    ),
    # 7. CKE Czerwiec 2024 (termin dodatkowy, OMAP-100-2406) – 19 zadań, 25 pkt
    HistoricalExamSession(
        session_id="cke_2024_06",
        code="OMAP-100-2406",
        name="CKE Czerwiec 2024 (termin dodatkowy)",
        date_str="11 czerwca 2024 r.",
        formula_years="2021–2024",
        duration_min=100,
        tasks=(
            HistoricalTaskEntry(1, "liczby_dzialania", "abcd", 1, "Temperatury w miejscowościach – różnice liczb ujemnych"),
            HistoricalTaskEntry(2, "liczby_dzialania", "ab_cd", 1, "Brakujący składnik działania na liczbach całkowitych"),
            HistoricalTaskEntry(3, "potegi_notacja", "pf", 1, "Porównywanie i równość wyrażeń potęgowych"),
            HistoricalTaskEntry(4, "wyrazenia_algebraiczne", "ab_cd", 1, "Kulki trzech kolorów – wyrażenie na łączną liczbę kulek"),
            HistoricalTaskEntry(5, "liczby_dzialania", "abcd", 1, "Wartość wyrażenia z liczb odczytanych z osi liczbowej"),
            HistoricalTaskEntry(6, "liczby_dzialania", "uzasadnienie", 1, "Cechy podzielności liczb wielocyfrowych"),
            HistoricalTaskEntry(7, "geometria_plaska", "abcd", 1, "Miary kątów trójkąta z różnicy kątów"),
            HistoricalTaskEntry(8, "procenty_proporcje", "abcd", 1, "Zawartość procentowa rodzynek po dosypaniu orzechów"),
            HistoricalTaskEntry(9, "statystyka_diagramy", "pf", 1, "Średnia liczba punktów po kolejnym meczu"),
            HistoricalTaskEntry(10, "pierwiastki", "abcd", 1, "Pierwiastki kwadratowe i sześcienne z ułamków"),
            HistoricalTaskEntry(11, "uklad_wspolrzednych", "abcd", 1, "Współrzędne wierzchołków figury na kratce"),
            HistoricalTaskEntry(12, "procenty_proporcje", "abcd", 1, "Przeliczanie odległości na planie w zadanej skali"),
            HistoricalTaskEntry(13, "geometria_plaska", "abcd", 1, "Obwód figury powstałej po rozcięciu kwadratu"),
            HistoricalTaskEntry(14, "liczby_dzialania", "abcd", 1, "Ułamek pozostałej części działki"),
            HistoricalTaskEntry(15, "geometria_przestrzenna", "abcd", 1, "Liczba brył na podstawie łącznej liczby krawędzi"),
            HistoricalTaskEntry(16, "prawdopodobienstwo", "otwarte_2pkt", 2, "Prawdopodobieństwo wyniku > 20 pkt z diagramu gry"),
            HistoricalTaskEntry(17, "rownania_tekstowe", "otwarte_3pkt", 3, "Małe i duże opakowania – wyznaczenie pojemności"),
            HistoricalTaskEntry(18, "geometria_plaska", "otwarte_2pkt", 2, "Pole kwietnika na prostokątnym trawniku z alejką"),
            HistoricalTaskEntry(19, "geometria_przestrzenna", "otwarte_3pkt", 3, "Objętość graniastosłupa z dwóch sum krawędzi"),
        ),
    ),
    # 8. CKE Maj 2023 (termin główny, OMAP-100-2305) – 19 zadań, 25 pkt
    HistoricalExamSession(
        session_id="cke_2023_05",
        code="OMAP-100-2305",
        name="CKE Maj 2023 (termin główny)",
        date_str="24 maja 2023 r.",
        formula_years="2021–2024",
        duration_min=100,
        tasks=(
            HistoricalTaskEntry(1, "procenty_proporcje", "pf", 1, "Przepis na 8 gofrów – proporcjonalne przeliczanie składników"),
            HistoricalTaskEntry(2, "liczby_dzialania", "abcd", 1, "Hasło z sześcianu liczby i wspólnego mianownika (NWW)"),
            HistoricalTaskEntry(3, "wyrazenia_algebraiczne", "abcd", 1, "Wartość wyrażenia 2x^2 - 2 dla x = 1 oraz x = -1"),
            HistoricalTaskEntry(4, "liczby_dzialania", "abcd", 1, "Układanie jednakowych książek na dwóch półkach"),
            HistoricalTaskEntry(5, "pierwiastki", "ab_cd", 1, "Suma i różnica pierwiastków kwadratowych"),
            HistoricalTaskEntry(6, "rownania_tekstowe", "abcd", 1, "Grusze i jabłonie w sadzie (o 40% więcej i o 50 więcej)"),
            HistoricalTaskEntry(7, "potegi_notacja", "ab_cd", 1, "Iloraz 10^8 / 5^8 oraz iloczyn 2^6 · 25^3"),
            HistoricalTaskEntry(8, "wyrazenia_algebraiczne", "abcd", 1, "Zapis par wyrażeń z opisu słownego (4(x+7) i 5y+3)"),
            HistoricalTaskEntry(9, "geometria_przestrzenna", "abcd", 1, "Wierzchołki ostrosłupa (16) a wierzchołki graniastosłupa"),
            HistoricalTaskEntry(10, "procenty_proporcje", "abcd", 1, "Skala planu miasta 1 : 4000 – odległość przystanków"),
            HistoricalTaskEntry(11, "prawdopodobienstwo", "pf", 1, "Losowanie kuli z urny (18 białych, 12 czarnych)"),
            HistoricalTaskEntry(12, "geometria_plaska", "abcd", 1, "Obwód prostokąta ze środków boków i tw. Pitagorasa"),
            HistoricalTaskEntry(13, "uklad_wspolrzednych", "pf", 1, "Równoległość i prostopadłość odcinków łamanej na kratce"),
            HistoricalTaskEntry(14, "geometria_plaska", "uzasadnienie", 1, "Układanie kwadratu o polu 49 cm^2 z trzech prostokątów"),
            HistoricalTaskEntry(15, "geometria_plaska", "pf", 1, "Czworokąt podzielony przekątną na trójkąt równoboczny i równoramienny"),
            HistoricalTaskEntry(16, "rownania_tekstowe", "otwarte_2pkt", 2, "Bilety do teatru i kina – układanie równania (400 zł)"),
            HistoricalTaskEntry(17, "predkosc_droga_czas", "otwarte_2pkt", 2, "Pociąg (700 m w 50 s) – obliczenie długości pociągu (15 s)"),
            HistoricalTaskEntry(18, "geometria_plaska", "otwarte_3pkt", 3, "Pole czworokąta podzielonego przekątną – wysokość trójkąta"),
            HistoricalTaskEntry(19, "geometria_przestrzenna", "otwarte_3pkt", 3, "Figura z 5 jednakowych klocków prostopadłościennych – objętość"),
        ),
    ),
    # 9. CKE Maj 2022 (termin główny, OMAP-100-2205) – 19 zadań, 25 pkt
    HistoricalExamSession(
        session_id="cke_2022_05",
        code="OMAP-100-2205",
        name="CKE Maj 2022 (termin główny)",
        date_str="25 maja 2022 r.",
        formula_years="2021–2024",
        duration_min=100,
        tasks=(
            HistoricalTaskEntry(1, "statystyka_diagramy", "pf", 1, "Ankieta o filmach – diagram procentowy i liczebność grupy"),
            HistoricalTaskEntry(2, "liczby_dzialania", "abcd", 1, "Wartość wyrażenia 4^2 / 5 - 3^2"),
            HistoricalTaskEntry(3, "liczby_dzialania", "abcd", 1, "Suma największej i najmniejszej liczby trzycyfrowej o sumie cyfr 6"),
            HistoricalTaskEntry(4, "liczby_dzialania", "uzasadnienie", 1, "Podzielność sumy 323 + 160 przez 3 z uzasadnieniem"),
            HistoricalTaskEntry(5, "potegi_notacja", "abcd", 1, "Porównywanie wyrażeń potęgowych z liczbą 10^100"),
            HistoricalTaskEntry(6, "procenty_proporcje", "ab_cd", 1, "Proporcjonalność zużycia materiału na bluzki S i L"),
            HistoricalTaskEntry(7, "wyrazenia_algebraiczne", "abcd", 1, "Najmniejsza wartość wyrażenia (n^4 - 3)/6 dla podanych n"),
            HistoricalTaskEntry(8, "pierwiastki", "abcd", 1, "Szacowanie liczby pierwiastek z 60 między kolejnymi całkowitymi"),
            HistoricalTaskEntry(9, "liczby_dzialania", "abcd", 1, "Podział odcinka PS na 8 równych części na osi liczbowej"),
            HistoricalTaskEntry(10, "liczby_dzialania", "abcd", 1, "Rozmiar pliku prezentacji (2,5 razy większy – o ile MB więcej)"),
            HistoricalTaskEntry(11, "rownania_tekstowe", "abcd", 1, "Ziemia ogrodowa zużywana w trzech miesiącach – wybór równania"),
            HistoricalTaskEntry(12, "liczby_dzialania", "abcd", 1, "Zakup biletów 75-minutowych i 20-minutowych w automacie"),
            HistoricalTaskEntry(13, "geometria_plaska", "abcd", 1, "Kąty w trójkącie ABC z odcinkiem AD = BD"),
            HistoricalTaskEntry(14, "prawdopodobienstwo", "abcd", 1, "Dokładanie zielonych kulek do pudełka do P = 1/4"),
            HistoricalTaskEntry(15, "geometria_plaska", "pf", 1, "Trapez z trzech trójkątów prostokątnych 3-4-5 – pole i obwód"),
            HistoricalTaskEntry(16, "rownania_tekstowe", "otwarte_2pkt", 2, "Naszyjnik Hani z korali – zielone stanowią 20% całości"),
            HistoricalTaskEntry(17, "predkosc_droga_czas", "otwarte_2pkt", 2, "Prędkość kierowcy w km/h (22,5 km od 7:50 do 8:05)"),
            HistoricalTaskEntry(18, "geometria_plaska", "otwarte_3pkt", 3, "Romb o obwodzie 52 cm i przekątnej 24 cm – druga przekątna"),
            HistoricalTaskEntry(19, "geometria_przestrzenna", "otwarte_3pkt", 3, "Siatka graniastosłupa prawidłowego czworokątnego – objętość"),
        ),
    ),
    # 10. CKE Maj 2021 (termin główny, OMAP-100-2105) – 19 zadań, 25 pkt
    HistoricalExamSession(
        session_id="cke_2021_05",
        code="OMAP-100-2105",
        name="CKE Maj 2021 (termin główny)",
        date_str="26 maja 2021 r.",
        formula_years="2021–2024",
        duration_min=100,
        tasks=(
            HistoricalTaskEntry(1, "statystyka_diagramy", "pf", 1, "Diagram medali olimpijskich – udział ułamkowy i średnia"),
            HistoricalTaskEntry(2, "liczby_dzialania", "abcd", 1, "Porównywanie czterech działań na liczbach ujemnych"),
            HistoricalTaskEntry(3, "liczby_dzialania", "ab_cd", 1, "Suma i różnica ułamków zwykłych 3/7 i 3/5"),
            HistoricalTaskEntry(4, "potegi_notacja", "abcd", 1, "Zapis potęgi (60 000 000)^3 w postaci 6^3 · 10^21"),
            HistoricalTaskEntry(5, "liczby_dzialania", "uzasadnienie", 1, "Podzielność iloczynu 5 kolejnych liczb całkowitych przez 10"),
            HistoricalTaskEntry(6, "procenty_proporcje", "ab_cd", 1, "Obliczanie podatku dochodowego z progów procentowych"),
            HistoricalTaskEntry(7, "pierwiastki", "abcd", 1, "Szacowanie wartości wyrażenia (-pierwiastek z 10) + 5"),
            HistoricalTaskEntry(8, "wyrazenia_algebraiczne", "ab_cd", 1, "Wzory na trójki pitagorejskie – parzystość i różnica c - b"),
            HistoricalTaskEntry(9, "wyrazenia_algebraiczne", "abcd", 1, "Wyznaczenie największej liczby w trójce pitagorejskiej dla a = 9"),
            HistoricalTaskEntry(10, "statystyka_diagramy", "abcd", 1, "Średnia cen 3 zeszytów i bloku rysunkowego"),
            HistoricalTaskEntry(11, "prawdopodobienstwo", "ab_cd", 1, "Loteria 150 losów – prawdopodobieństwo po wyciągnięciu 30 pustych"),
            HistoricalTaskEntry(12, "geometria_plaska", "abcd", 1, "Kąt między dwiema wysokościami w trójkącie"),
            HistoricalTaskEntry(13, "liczby_dzialania", "abcd", 1, "Cięcie listewki 50 cm co 5 cm i co 2 cm – wspólne linie (NWW)"),
            HistoricalTaskEntry(14, "geometria_przestrzenna", "abcd", 1, "Objętość piasku zajmującego 3/4 prostopadłościennej skrzyni"),
            HistoricalTaskEntry(15, "geometria_przestrzenna", "abcd", 1, "Pole powierzchni bryły ze sklejonych podstawami dwóch ostrosłupów"),
            HistoricalTaskEntry(16, "liczby_dzialania", "otwarte_2pkt", 2, "Podział tabliczki czekolady (1/2 + 5/12 + 1/6) – uzasadnienie"),
            HistoricalTaskEntry(17, "predkosc_droga_czas", "otwarte_3pkt", 3, "Trasa skutera na siatce kwadratowej – godzina przyjazdu"),
            HistoricalTaskEntry(18, "rownania_tekstowe", "otwarte_2pkt", 2, "Zakup puszek karmy (10 zabrakło 11 zł, 6 zostało 3,40 zł)"),
            HistoricalTaskEntry(19, "geometria_plaska", "otwarte_3pkt", 3, "Wysokość trójkąta opuszczona na przekątną prostokąta 12×16"),
        ),
    ),
    # 11. CKE Czerwiec 2020 (termin główny, OMAP-100-2006) – 21 zadań, 30 pkt
    HistoricalExamSession(
        session_id="cke_2020_06",
        code="OMAP-100-2006",
        name="CKE Czerwiec 2020 (termin główny)",
        date_str="17 czerwca 2020 r.",
        formula_years="2019–2020",
        duration_min=100,
        tasks=(
            HistoricalTaskEntry(1, "procenty_proporcje", "ab_cd", 1, "Tabela etapów rajdu rowerowego – procent i ułamek trasy"),
            HistoricalTaskEntry(2, "liczby_dzialania", "abcd", 1, "Wartość wyrażenia 5/7 - 2/7 · (-3/2)"),
            HistoricalTaskEntry(3, "procenty_proporcje", "abcd", 1, "Podział kosztu auta 154 000 zł w stosunku 2 : 3 : 6"),
            HistoricalTaskEntry(4, "liczby_dzialania", "pf", 1, "Punkty podziału odcinka na 5 części na osi liczbowej"),
            HistoricalTaskEntry(5, "predkosc_droga_czas", "abcd", 1, "Pociąg (150 m) przejeżdżający przez tunel (350 m) z v = 20 m/s"),
            HistoricalTaskEntry(6, "pierwiastki", "abcd", 1, "Wartość wyrażenia pierwiastek(3) · (pierwiastek(27) - pierwiastek(12))"),
            HistoricalTaskEntry(7, "potegi_notacja", "abcd", 1, "Rozpoznawanie wyrażeń równych potędze 3^15"),
            HistoricalTaskEntry(8, "statystyka_diagramy", "abcd", 1, "Diagram skoku wzwyż – ilu zawodników powyżej średniej"),
            HistoricalTaskEntry(9, "geometria_przestrzenna", "abcd", 1, "Sklejanie kostki sześciennej z siatki z symbolami"),
            HistoricalTaskEntry(10, "wyrazenia_algebraiczne", "abcd", 1, "Wyznaczanie podstawy x ze wzoru na pole trapezu"),
            HistoricalTaskEntry(11, "geometria_plaska", "pf", 1, "Romb o boku 4 cm i kącie ostrym 60° – przekątna i pole"),
            HistoricalTaskEntry(12, "wyrazenia_algebraiczne", "ab_cd", 1, "Reguła długości kolejnych łamanych na kratce"),
            HistoricalTaskEntry(13, "procenty_proporcje", "abcd", 1, "Obniżki cen łyżew w trzech sklepach Alfa, Beta, Gamma"),
            HistoricalTaskEntry(14, "geometria_plaska", "abcd", 1, "Obwód połowy trójkąta równobocznego o boku 10 cm"),
            HistoricalTaskEntry(15, "wyrazenia_algebraiczne", "abcd", 1, "Pole trójkąta zapisane wyrażeniem algebraicznym"),
            HistoricalTaskEntry(16, "geometria_plaska", "otwarte_2pkt", 2, "Uzasadnij, że trójkąt z kątem równym różnicy dwóch pozostałych jest prostokątny"),
            HistoricalTaskEntry(17, "prawdopodobienstwo", "otwarte_2pkt", 2, "Zliczanie możliwości wyboru miejsc w przedziale kolejowym"),
            HistoricalTaskEntry(18, "rownania_tekstowe", "otwarte_2pkt", 2, "Książki (2/3 nagród) i e-booki (o 8 mniej) na konkurs"),
            HistoricalTaskEntry(19, "liczby_dzialania", "otwarte_3pkt", 3, "Kalendarz marca i liczba uszytych poduszek w zakładzie"),
            HistoricalTaskEntry(20, "procenty_proporcje", "otwarte_3pkt", 3, "Koszt worków nasion trawy na boisko prostokątne 46 m × 30 m"),
            HistoricalTaskEntry(21, "geometria_przestrzenna", "otwarte_3pkt", 3, "Objętość ostrosłupa prawidłowego czworokątnego z siatki"),
        ),
    ),
    # 12. CKE Kwiecień 2019 (termin główny, OMAP-100-1904) – 21 zadań, 30 pkt
    HistoricalExamSession(
        session_id="cke_2019_04",
        code="OMAP-100-1904",
        name="CKE Kwiecień 2019 (termin główny)",
        date_str="16 kwietnia 2019 r.",
        formula_years="2019–2020",
        duration_min=100,
        tasks=(
            HistoricalTaskEntry(1, "liczby_dzialania", "pf", 1, "Obliczenia kalendarzowe – dni tygodnia urodzin rodzeństwa"),
            HistoricalTaskEntry(2, "liczby_dzialania", "abcd", 1, "Ile liczb naturalnych ma zaokrąglenie do dziesiątek równe 1450"),
            HistoricalTaskEntry(3, "potegi_notacja", "abcd", 1, "Które iloczyny i ilorazy potęg są równe 50^8"),
            HistoricalTaskEntry(4, "pierwiastki", "abcd", 1, "Szacowanie wyrażeń z pierwiastkami mniejszych od 10"),
            HistoricalTaskEntry(5, "liczby_dzialania", "ab_cd", 1, "Dzielenie kartonu na karty do gry z resztą dla 5 graczy"),
            HistoricalTaskEntry(6, "procenty_proporcje", "abcd", 1, "Syrop z cukru i wody w stosunku 5 : 3 – procent cukru"),
            HistoricalTaskEntry(7, "statystyka_diagramy", "pf", 1, "Średnia zarobków w firmie po odejściu dwóch pracowników"),
            HistoricalTaskEntry(8, "wyrazenia_algebraiczne", "abcd", 1, "Mnożenie sum algebraicznych (2a + 3b)(3b - 2a)"),
            HistoricalTaskEntry(9, "uklad_wspolrzednych", "abcd", 1, "Ćwiartka układu współrzędnych zawierająca środek odcinka KL"),
            HistoricalTaskEntry(10, "wyrazenia_algebraiczne", "pf", 1, "Obwód figury z dwóch prostokątów o boku a"),
            HistoricalTaskEntry(11, "geometria_plaska", "abcd", 1, "Rozpoznawanie trójkątów przystających z kątów i boków"),
            HistoricalTaskEntry(12, "geometria_plaska", "abcd", 1, "Kąt w równoległoboku połączonym z trójkątem równoramiennym"),
            HistoricalTaskEntry(13, "geometria_plaska", "abcd", 1, "Długość boku w dwóch sklejonych trójkątach prostokątnych"),
            HistoricalTaskEntry(14, "pierwiastki", "abcd", 1, "Budowa największego sześcianu z 203 klocków (sześciany liczb)"),
            HistoricalTaskEntry(15, "geometria_przestrzenna", "abcd", 1, "Suma długości krawędzi ostrosłupa z fragmentu siatki"),
            HistoricalTaskEntry(16, "procenty_proporcje", "otwarte_2pkt", 2, "Diagram procentowy meczów drużyny – liczba przegranych"),
            HistoricalTaskEntry(17, "predkosc_droga_czas", "otwarte_2pkt", 2, "Porównanie czasu przejazdu samochodu i busa na trasie 120 km"),
            HistoricalTaskEntry(18, "rownania_tekstowe", "otwarte_2pkt", 2, "Bukiet z goździków i róż – uzasadnienie podzielności ceny"),
            HistoricalTaskEntry(19, "rownania_tekstowe", "otwarte_3pkt", 3, "Konkurencje na Dzień Sportu (1/2, potem 1/3 reszty i 12 pozostałych)"),
            HistoricalTaskEntry(20, "geometria_plaska", "otwarte_3pkt", 3, "Wymiary działki 3750 m^2 podzielonej na 3 jednakowe prostokąty"),
            HistoricalTaskEntry(21, "geometria_plaska", "otwarte_3pkt", 3, "Różnica obwodów trójkąta prostokątnego 12×16 i złożonego trapezu"),
        ),
    ),
)

SESSION_BY_ID: Dict[str, HistoricalExamSession] = {s.session_id: s for s in HISTORICAL_CKE_EXAMS}


@dataclass(frozen=True)
class TopicEmpiricalStat:
    """Empiryczne statystyki pojedynczego działu wyliczone ze wszystkich arkuszy CKE."""
    topic_id: str
    total_tasks: int
    closed_tasks: int
    open_tasks: int
    total_points: int
    sessions_present: int
    base_probability: float       # udział w ogólnej liczbie zadań CKE (suma po 12 działach = 1.0)
    closed_probability: float     # udział wśród zadań zamkniętych CKE
    open_probability: float       # udział wśród zadań otwartych CKE
    avg_relative_position: float  # średnia pozycja w arkuszu (0.0 = początek, 1.0 = koniec)


def compute_empirical_topic_stats() -> Dict[str, TopicEmpiricalStat]:
    """Przelicza na żywo wszystkie historyczne arkusze CKE z katalogu i wyznacza rozkłady prawdopodobieństwa."""
    tot_all = sum(len(s.tasks) for s in HISTORICAL_CKE_EXAMS)
    tot_closed = sum(s.closed_count for s in HISTORICAL_CKE_EXAMS)
    tot_open = sum(s.open_count for s in HISTORICAL_CKE_EXAMS)

    counts_all: Dict[str, int] = {t.id: 0 for t in TOPICS}
    counts_closed: Dict[str, int] = {t.id: 0 for t in TOPICS}
    counts_open: Dict[str, int] = {t.id: 0 for t in TOPICS}
    points_sum: Dict[str, int] = {t.id: 0 for t in TOPICS}
    sess_present: Dict[str, int] = {t.id: 0 for t in TOPICS}
    rel_positions: Dict[str, List[float]] = {t.id: [] for t in TOPICS}

    for sess in HISTORICAL_CKE_EXAMS:
        seen_in_sess: set[str] = set()
        n_s = max(1, len(sess.tasks) - 1)
        for idx, item in enumerate(sess.tasks):
            tid = item.topic_id
            counts_all[tid] = counts_all.get(tid, 0) + 1
            points_sum[tid] = points_sum.get(tid, 0) + item.points
            if item.points == 1:
                counts_closed[tid] = counts_closed.get(tid, 0) + 1
            else:
                counts_open[tid] = counts_open.get(tid, 0) + 1
            seen_in_sess.add(tid)
            rel_positions[tid].append(idx / n_s)
        for tid in seen_in_sess:
            sess_present[tid] = sess_present.get(tid, 0) + 1

    stats: Dict[str, TopicEmpiricalStat] = {}
    for idx, t in enumerate(TOPICS):
        tid = t.id
        pos_list = rel_positions[tid]
        avg_pos = sum(pos_list) / len(pos_list) if pos_list else (idx / max(1, len(TOPICS) - 1))
        stats[tid] = TopicEmpiricalStat(
            topic_id=tid,
            total_tasks=counts_all[tid],
            closed_tasks=counts_closed[tid],
            open_tasks=counts_open[tid],
            total_points=points_sum[tid],
            sessions_present=sess_present[tid],
            base_probability=counts_all[tid] / max(1, tot_all),
            closed_probability=counts_closed[tid] / max(1, tot_closed),
            open_probability=counts_open[tid] / max(1, tot_open),
            avg_relative_position=avg_pos,
        )
    return stats


EMPIRICAL_STATS: Dict[str, TopicEmpiricalStat] = compute_empirical_topic_stats()


def compute_empirical_closed_subtype_shares(allowed_subtypes: Sequence[str]) -> Dict[str, float]:
    """Wyznacza empiryczny rozkład podtypów zadań zamkniętych (ABCD / PF / AB_CD / Uzasadnienie) z CKE.
    Gdy część podtypów zostanie wyłączona, ich procent rozkłada się równo pomiędzy pozostałe aktywne podtypy.
    """
    counts: Dict[str, int] = {"abcd": 0, "pf": 0, "ab_cd": 0, "uzasadnienie": 0}
    total = 0
    for sess in HISTORICAL_CKE_EXAMS:
        for item in sess.tasks:
            if item.points == 1 and item.subtype in counts:
                counts[item.subtype] += 1
                total += 1

    base = {k: counts[k] / max(1, total) for k in counts}
    active = [k for k in counts if k in set(allowed_subtypes)]
    if not active:
        active = list(counts.keys())

    removed_share = sum(base[k] for k in counts if k not in active)
    equal_bonus = removed_share / len(active)
    return {k: (base[k] + equal_bonus if k in active else 0.0) for k in counts}


def compute_active_topic_probabilities(selected_topics: Optional[Sequence[str]] = None) -> Dict[str, float]:
    """Zwraca docelowe prawdopodobieństwa działów (suma = 1.0).

    Zasada redystrybucji zgodna z wymaganiem użytkownika:
    - Każdy dział startuje ze swoim rzeczywistym historycznym udziałem procentowym z arkuszy CKE (np. 7,1%).
    - Jeżeli jeden lub więcej działów zostanie wykreślonych (odznaczonych w ustawieniach),
      łączny procent wykreślonych działów rozkłada się RÓWNO pomiędzy wszystkie pozostałe aktywne działy:
          p'_i = p_i + (suma_wykreslonych / liczba_aktywnych)
    """
    all_ids = [t.id for t in TOPICS]
    if not selected_topics:
        active_set = set(all_ids)
    else:
        active_set = {tid for tid in selected_topics if tid in EMPIRICAL_STATS}
        if not active_set:
            active_set = set(all_ids)

    active_list = [tid for tid in all_ids if tid in active_set]
    removed_mass = sum(EMPIRICAL_STATS[tid].base_probability for tid in all_ids if tid not in active_set)
    equal_share = removed_mass / len(active_list)

    result: Dict[str, float] = {}
    for tid in all_ids:
        if tid in active_set:
            result[tid] = EMPIRICAL_STATS[tid].base_probability + equal_share
        else:
            result[tid] = 0.0

    # Normalizacja numeryczna dla perfekcyjnej sumy 1.0
    s = sum(result.values())
    if s > 0:
        for tid in active_list:
            result[tid] /= s
    return result


def sample_topic_quotas_stratified(
    rng: random.Random,
    total_tasks: int,
    active_probs: Dict[str, float],
) -> Dict[str, int]:
    """Losuje dokładne liczby zadań dla działów metodą systematycznego losowania reszt (algorytm Madowa).

    Własności matematyczne:
    1. Dla KAŻDEGO pojedynczego arkusza liczba zadań z działu `i` wynosi
       floor(N * p'_i) albo ceil(N * p'_i) – arkusz trzyma się wag CKE najściślej jak pozwalają liczby całkowite.
    2. Wartość oczekiwana E[c_i / N] po wielu losowaniach jest DOKŁADNIE równa p'_i (np. temat mający 7% w CKE
       stanowi dokładnie 7,0% generowanych zadań w symulacji wielokrotnej).
    3. Suma zadań zawsze wynosi dokładnie `total_tasks`.
    """
    active_ids = [tid for tid, p in active_probs.items() if p > 0]
    quotas: Dict[str, int] = {tid: 0 for tid in active_probs}
    if total_tasks <= 0 or not active_ids:
        return quotas

    # Tasujemy kolejność aktywnych działów, aby wyeliminować jakąkolwiek korelację sąsiedztwa
    shuffled = list(active_ids)
    rng.shuffle(shuffled)

    remainders: List[Tuple[str, float]] = []
    allocated = 0
    for tid in shuffled:
        exact = total_tasks * active_probs[tid]
        base_int = int(math.floor(exact + 1e-12))
        rem = max(0.0, exact - base_int)
        quotas[tid] = base_int
        allocated += base_int
        remainders.append((tid, rem))

    k_extra = total_tasks - allocated
    if k_extra <= 0:
        return quotas

    # Systematyczne losowanie Madowa na przedziale [0, k_extra) z pojedynczym przesunięciem losowym u ~ U(0, 1)
    u = rng.random()
    cum = 0.0
    chosen_extra: List[str] = []
    for tid, rem in remainders:
        prev = cum
        cum += rem
        # Sprawdzamy, czy między prev a cum wypadł punkt postaci (m + u)
        if math.floor(cum - u + 1e-12) > math.floor(prev - u + 1e-12):
            chosen_extra.append(tid)

    # Zabezpieczenie przed błędami zaokrągleń zmiennoprzecinkowych na granicy przedziału
    while len(chosen_extra) < k_extra:
        candidates = [tid for tid, _ in sorted(remainders, key=lambda x: x[1], reverse=True) if tid not in chosen_extra]
        if not candidates:
            candidates = shuffled
        chosen_extra.append(candidates[0])
    if len(chosen_extra) > k_extra:
        chosen_extra = chosen_extra[:k_extra]

    for tid in chosen_extra:
        quotas[tid] += 1

    return quotas
