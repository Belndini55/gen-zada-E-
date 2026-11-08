"""Modele danych dla generatora arkuszy i zadań E8 z matematyki (v2 – CKE 2019–2026)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Działy tematyczne (zgodne z podstawą programową i arkuszami CKE E8)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TopicInfo:
    id: str
    name: str
    short_name: str
    description: str


TOPICS: List[TopicInfo] = [
    TopicInfo(
        id="liczby_dzialania",
        name="Liczby, ułamki, podzielność i oś liczbowa",
        short_name="Liczby i ułamki",
        description="Działania na ułamkach zwykłych i dziesiętnych, podzielność, cyfry rzymskie, temperatury, oś liczbowa.",
    ),
    TopicInfo(
        id="procenty_proporcje",
        name="Procenty, obniżki cen i proporcje",
        short_name="Procenty i proporcje",
        description="Obliczenia procentowe, podwyżki i obniżki w sklepach, przepisy kulinarne, skala i proporcjonalność prosta.",
    ),
    TopicInfo(
        id="potegi_notacja",
        name="Potęgi i notacja wykładnicza",
        short_name="Potęgi i notacja",
        description="Działania na potęgach o tych samych podstawach lub wykładnikach, zamiana podstaw, notacja wykładnicza.",
    ),
    TopicInfo(
        id="pierwiastki",
        name="Pierwiastki kwadratowe i sześcienne",
        short_name="Pierwiastki",
        description="Obliczanie i upraszczanie pierwiastków, wyłączanie czynnika przed znak pierwiastka, szacowanie na osi.",
    ),
    TopicInfo(
        id="wyrazenia_algebraiczne",
        name="Wyrażenia algebraiczne",
        short_name="Wyrażenia algebr.",
        description="Zapisywanie wyrażeń, przekształcanie wzorów, redukcja wyrazów podobnych, wartości liczbowe wyrażeń.",
    ),
    TopicInfo(
        id="rownania_tekstowe",
        name="Równania i zadania tekstowe",
        short_name="Równania tekstowe",
        description="Układanie i rozwiązywanie równań pierwszego stopnia z jedną niewiadomą w zadaniach z treścią.",
    ),
    TopicInfo(
        id="predkosc_droga_czas",
        name="Prędkość, droga, czas i jednostki",
        short_name="Prędkość, droga, czas",
        description="Obliczenia zegarowe, wykresy drogi od czasu, zamiana jednostek czasu i drogi, średnia prędkość.",
    ),
    TopicInfo(
        id="uklad_wspolrzednych",
        name="Układ współrzędnych na płaszczyźnie",
        short_name="Układ współrzędnych",
        description="Środek i długość odcinka, przesunięcia punktów, współrzędne wierzchołków oraz pola figur na kratce.",
    ),
    TopicInfo(
        id="geometria_plaska",
        name="Geometria płaska (kąty, trójkąty, wielokąty)",
        short_name="Geometria płaska",
        description="Kąty, twierdzenie Pitagorasa, trójkąty szczególne, pola i obwody czworokątów, okrąg i cięciwa.",
    ),
    TopicInfo(
        id="geometria_przestrzenna",
        name="Geometria przestrzenna (graniastosłup i ostrosłup)",
        short_name="Bryły (3D)",
        description="Własności graniastosłupów i ostrosłupów, siatki brył, pole powierzchni i objętość, poziom wody.",
    ),
    TopicInfo(
        id="statystyka_diagramy",
        name="Statystyka, tabele i diagramy",
        short_name="Statystyka i diagramy",
        description="Średnia arytmetyczna, odczytywanie i interpretacja danych z tabel oraz diagramów słupkowych i kołowych.",
    ),
    TopicInfo(
        id="prawdopodobienstwo",
        name="Prawdopodobieństwo i kombinatoryka",
        short_name="Prawdopodobieństwo",
        description="Klasyczne prawdopodobieństwo (losowanie kul, kostka), reguła mnożenia i parzystość w kombinatoryce.",
    ),
]

TOPIC_BY_ID: Dict[str, TopicInfo] = {t.id: t for t in TOPICS}


# ---------------------------------------------------------------------------
# Typy zadań (zgodne z arkuszami CKE)
# ---------------------------------------------------------------------------
CLOSED_SUBTYPES = ("abcd", "pf", "ab_cd", "uzasadnienie")
OPEN_SUBTYPES = ("otwarte_2pkt", "otwarte_3pkt")

SUBTYPE_LABELS: Dict[str, str] = {
    "abcd": "Wybór wielokrotny (A, B, C, D)",
    "pf": "Prawda / Fałsz (P / F)",
    "ab_cd": "Podwójne uzupełnianie (A/B oraz C/D)",
    "uzasadnienie": "Odpowiedź z uzasadnieniem (A/B + 1/2/3)",
    "otwarte_2pkt": "Otwarte krótkiej odpowiedzi (0–2 pkt)",
    "otwarte_3pkt": "Otwarte rozszerzonej odpowiedzi (0–3 pkt)",
}


@dataclass
class DiagramSpec:
    """Opis rysunku pomocniczego generowanego dynamicznie przez Matplotlib."""
    kind: str
    params: Dict[str, Any] = field(default_factory=dict)
    caption: str = ""
    width_mm: float = 82.0


@dataclass
class Task:
    """Pojedyncze wygenerowane zadanie egzaminacyjne w stylu CKE."""
    number: int
    topic_id: str
    subtype: str
    points: int
    difficulty: int
    template_id: str
    cke_ref: str

    stem: str
    command: str

    table_data: Optional[List[List[str]]] = None
    diagram: Optional[DiagramSpec] = None

    choices: Dict[str, str] = field(default_factory=dict)
    pf_statements: List[tuple[str, str]] = field(default_factory=list)
    ab_cd_parts: List[Dict[str, Any]] = field(default_factory=list)
    justification_data: Dict[str, Any] = field(default_factory=dict)

    correct_answer: str = ""
    solution_steps: List[str] = field(default_factory=list)
    scoring_scheme: List[str] = field(default_factory=list)
    grid_height_mm: float = 55.0

    @property
    def is_open(self) -> bool:
        return self.subtype in OPEN_SUBTYPES

    @property
    def topic_name(self) -> str:
        t = TOPIC_BY_ID.get(self.topic_id)
        return t.short_name if t else self.topic_id


@dataclass(frozen=True)
class ExamPreset:
    id: str
    name: str
    description: str
    closed_count: int
    open_2pt_count: int
    open_3pt_count: int
    duration_minutes: int
    exam_code: str = "OMAP-100-2605"


PRESETS: List[ExamPreset] = [
    ExamPreset(
        id="cke_2026_20",
        name="Pełny arkusz CKE Maj/Czerwiec 2026 (20 zadań · 30 pkt · 125 min)",
        description="Najnowszy układ CKE 2026: 14 zadań zamkniętych (14 pkt) + 6 zadań otwartych (2×2 pkt + 4×3 pkt = 16 pkt).",
        closed_count=14,
        open_2pt_count=2,
        open_3pt_count=4,
        duration_minutes=125,
        exam_code="OMAP-100-2605",
    ),
    ExamPreset(
        id="cke_2025_2026_21",
        name="Pełny arkusz CKE 2025 (21 zadań · 30 pkt · 125 min)",
        description="Układ CKE 2025: 15 zadań zamkniętych (15 pkt) + 6 zadań otwartych (3×2 pkt + 3×3 pkt = 15 pkt).",
        closed_count=15,
        open_2pt_count=3,
        open_3pt_count=3,
        duration_minutes=125,
        exam_code="OMAP-100-2505",
    ),
    ExamPreset(
        id="cke_2021_2024_19",
        name="Arkusz CKE z lat 2021–2024 (19 zadań · 25 pkt · 100 min)",
        description="Klasyczny układ z lat 2021–2024: 15 zadań zamkniętych (15 pkt) + 4 zadania otwarte (2×2 pkt + 2×3 pkt = 10 pkt).",
        closed_count=15,
        open_2pt_count=2,
        open_3pt_count=2,
        duration_minutes=100,
        exam_code="OMAP-100-2405",
    ),
    ExamPreset(
        id="kartkowka_10",
        name="Szybki trening / sprawdzian (10 zadań · 13 pkt · 45 min)",
        description="Krótki zestaw na jedną lekcję: 8 zadań zamkniętych (8 pkt) + 2 zadania otwarte (2 pkt + 3 pkt).",
        closed_count=8,
        open_2pt_count=1,
        open_3pt_count=1,
        duration_minutes=45,
        exam_code="OMAP-100-TREN",
    ),
    ExamPreset(
        id="custom",
        name="Własna konfiguracja (wybierz działy, typy i liczbę zadań)",
        description="Pełna kontrola nad tematami, rodzajami zadań zamkniętych/otwartych i liczbą zadań.",
        closed_count=10,
        open_2pt_count=2,
        open_3pt_count=2,
        duration_minutes=90,
        exam_code="OMAP-100-WLAS",
    ),
]

PRESET_BY_ID: Dict[str, ExamPreset] = {p.id: p for p in PRESETS}


@dataclass
class ExamConfig:
    """Konfiguracja ustawiana przez użytkownika w oknie programu."""
    preset_id: str = "cke_2026_20"
    title: str = "EGZAMIN ÓSMOKLASISTY Z MATEMATYKI"
    subtitle: str = "Arkusz w formule CKE (OMAP-100)"
    exam_code: str = "OMAP-100-2605"
    school_or_group: str = ""
    exam_date_str: str = ""
    variant_code: str = "Wersja A"
    duration_minutes: int = 125

    # Działy tematyczne (pusta lista lub wszystkie = cały materiał E8)
    selected_topics: List[str] = field(default_factory=lambda: [t.id for t in TOPICS])

    # Tryb rozkładu prawdopodobieństwa działów:
    # - "cke_probabilistic": empiryczne wagi CKE 2019–2026 + równa redystrybucja odznaczonych działów
    # - "mirror_session:<session_id>": odwzorowanie 1:1 wybranego arkusza CKE (np. "mirror_session:cke_2026_05")
    # - "uniform": równe prawdopodobieństwo wszystkich zaznaczonych działów
    distribution_mode: str = "cke_probabilistic"

    # Liczby zadań
    closed_count: int = 14
    open_2pt_count: int = 2
    open_3pt_count: int = 4

    # Dozwolone podtypy zadań zamkniętych
    allowed_closed_subtypes: List[str] = field(default_factory=lambda: list(CLOSED_SUBTYPES))

    # Poziom trudności: "standard" (mieszany jak CKE), "easy" (łatwiejsze), "hard" (trudniejsze)
    difficulty_mode: str = "standard"

    # Opcje układu arkusza PDF w stylu CKE OMAP-100
    include_cover_page: bool = True
    include_answer_grid_for_open: bool = True
    include_answer_card: bool = True
    include_scratchpad_page: bool = False
    include_diagrams: bool = True
    include_cke_ref_in_key: bool = True

    # Opcjonalne ziarno losowości (None = losowe przy każdym kliknięciu)
    seed: Optional[int] = None


@dataclass
class ExamSheet:
    """Wygenerowany kompletny arkusz wraz z metadanymi, rozkładem % i listą zadań."""
    config: ExamConfig
    used_seed: int
    tasks: List[Task]
    topic_probabilities: Dict[str, float] = field(default_factory=dict)

    @property
    def total_points(self) -> int:
        return sum(t.points for t in self.tasks)

    @property
    def closed_tasks(self) -> List[Task]:
        return [t for t in self.tasks if not t.is_open]

    @property
    def open_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.is_open]


@dataclass
class TaskTemplate:
    """Rejestrowany wzorzec (szablon) zadania parametrycznego."""
    template_id: str
    topic_id: str
    subtype: str
    points: int
    difficulty: int
    cke_ref: str
    has_diagram: bool
    generator_fn: Callable[[Any], Dict[str, Any]]
