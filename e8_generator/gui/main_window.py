"""Główne okno aplikacji desktopowej Generator Zadań E8 – Matematyka (PyQt6, v2 – CKE OMAP-100)."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..cke_archive import (
    EMPIRICAL_STATS,
    HISTORICAL_CKE_EXAMS,
    SESSION_BY_ID,
    compute_active_topic_probabilities,
)
from ..engine import generate_exam_sheet, replace_single_task
from ..models import (
    CLOSED_SUBTYPES,
    PRESET_BY_ID,
    PRESETS,
    SUBTYPE_LABELS,
    TOPICS,
    ExamConfig,
    ExamSheet,
)
from ..pdf_exporter import build_exam_pdf_bytes, build_key_pdf_bytes
from .archive_widget import CKEArchiveStatsWidget
from .preview_widget import PdfPreviewWidget
from .styles import (
    detect_system_dark_mode,
    get_stylesheet,
    load_saved_theme_mode,
    save_theme_mode,
)
from .task_list_widget import TaskListWidget


class MainWindow(QMainWindow):
    """Główne okno programu z formularzem konfiguracji CKE po lewej i podglądem PDF / statystyką po prawej."""

    def __init__(self, initial_theme_mode: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("Generator Zadań E8 – Matematyka (wzorzec i statystyka CKE 2019–2026)")
        self.resize(1420, 900)
        self.setMinimumSize(1080, 700)

        self._theme_mode: str = initial_theme_mode or load_saved_theme_mode()
        self._is_dark: bool = False
        self._current_sheet: Optional[ExamSheet] = None
        self._exam_pdf_bytes: Optional[bytes] = None
        self._key_pdf_bytes: Optional[bytes] = None
        self._updating_preset_fields: bool = False

        self._topic_checks: Dict[str, QCheckBox] = {}
        self._subtype_checks: Dict[str, QCheckBox] = {}

        self._build_ui()
        self._setup_shortcuts()
        self.apply_theme_mode(self._theme_mode, persist=(initial_theme_mode is None))
        self._refresh_live_topic_percentages()

        # Wygeneruj od razu pierwszy przykładowy arkusz po uruchomieniu
        self.generate_new_sheet()

    # ------------------------------------------------------------------
    # Budowa interfejsu użytkownika
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("RootWidget")
        self.setCentralWidget(root)

        main_lay = QHBoxLayout(root)
        main_lay.setContentsMargins(10, 10, 10, 10)
        main_lay.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        main_lay.addWidget(splitter)

        # ================= LEWY PANEL: FORMULARZ KONFIGURACJI =================
        left_panel = QWidget()
        left_panel.setMinimumWidth(525)
        left_panel.setMaximumWidth(610)
        left_vbox = QVBoxLayout(left_panel)
        left_vbox.setContentsMargins(0, 0, 0, 0)
        left_vbox.setSpacing(8)

        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        form_body = QWidget()
        form_body.setObjectName("FormScrollBody")
        form_lay = QVBoxLayout(form_body)
        form_lay.setContentsMargins(4, 2, 16, 8)
        form_lay.setSpacing(8)

        # Nagłówek aplikacji + przełącznik motywu (Jasny / Ciemny / Systemowy)
        hdr_row = QHBoxLayout()
        hdr_row.setSpacing(8)
        app_hdr = QLabel("Generator Zadań E8 – Matematyka")
        app_hdr.setObjectName("HeaderTitle")
        hdr_row.addWidget(app_hdr, 1)

        self._combo_theme = QComboBox()
        self._combo_theme.setToolTip("Wybierz motyw interfejsu: Jasny, Ciemny lub Systemowy (skrót: Ctrl+D)")
        self._combo_theme.addItem("Motyw: Systemowy", userData="system")
        self._combo_theme.addItem("Motyw: Jasny (CKE)", userData="light")
        self._combo_theme.addItem("Motyw: Ciemny", userData="dark")
        idx_theme = self._combo_theme.findData(self._theme_mode)
        if idx_theme >= 0:
            self._combo_theme.setCurrentIndex(idx_theme)
        self._combo_theme.currentIndexChanged.connect(self._on_theme_combo_changed)
        hdr_row.addWidget(self._combo_theme)

        app_sub = QLabel(
            "Generuje za każdym razem nowe, autorskie zadania w szacie graficznej CKE (OMAP-100) "
            "oraz wg empirycznego prawdopodobieństwa działów z 12 arkuszy CKE (2019–2026)."
        )
        app_sub.setObjectName("MutedLabel")
        app_sub.setWordWrap(True)
        form_lay.addLayout(hdr_row)
        form_lay.addWidget(app_sub)

        # 1. Układ arkusza (Preset)
        grp_preset = QGroupBox("1. Układ arkusza / szybki szablon CKE")
        gp_lay = QVBoxLayout(grp_preset)
        gp_lay.setSpacing(6)

        self._combo_preset = QComboBox()
        self._combo_preset.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self._combo_preset.setMinimumContentsLength(18)
        for p in PRESETS:
            self._combo_preset.addItem(p.name, userData=p.id)
        self._combo_preset.currentIndexChanged.connect(self._on_preset_changed)
        gp_lay.addWidget(self._combo_preset)

        self._lbl_preset_desc = QLabel(PRESETS[0].description)
        self._lbl_preset_desc.setObjectName("MutedLabel")
        self._lbl_preset_desc.setWordWrap(True)
        gp_lay.addWidget(self._lbl_preset_desc)
        form_lay.addWidget(grp_preset)

        # 2. Zakres tematyczny (Działy E8 + żywe % CKE)
        grp_topics = QGroupBox("2. Działy E8 i rozkład prawdopodobieństwa CKE")
        gt_lay = QVBoxLayout(grp_topics)
        gt_lay.setSpacing(6)

        dist_form = QFormLayout()
        dist_form.setSpacing(5)
        self._combo_dist = QComboBox()
        self._combo_dist.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self._combo_dist.setMinimumContentsLength(18)
        self._combo_dist.addItem(
            "Statystyka CKE 2019–2026 (równa redystrybucja %)",
            userData="cke_probabilistic",
        )
        for sess in HISTORICAL_CKE_EXAMS:
            self._combo_dist.addItem(
                f"Układ działów sesji: {sess.name} (nowe zadania)",
                userData=f"mirror_session:{sess.session_id}",
            )
        self._combo_dist.addItem(
            "Równy udział każdego aktywnego działu (1/N)",
            userData="uniform",
        )
        self._combo_dist.currentIndexChanged.connect(self._on_distribution_mode_changed)
        dist_form.addRow("Tryb rozkładu:", self._combo_dist)
        gt_lay.addLayout(dist_form)

        self._chk_all_topics = QCheckBox("Cały materiał E8 (wszystkie 12 działów wg wag CKE)")
        self._chk_all_topics.setChecked(True)
        self._chk_all_topics.setObjectName("AccentCheckBox")
        self._chk_all_topics.toggled.connect(self._on_all_topics_toggled)
        gt_lay.addWidget(self._chk_all_topics)

        quick_topic_btns = QGridLayout()
        quick_topic_btns.setHorizontalSpacing(6)
        quick_topic_btns.setVerticalSpacing(4)

        btn_sel_all = QPushButton("Zaznacz wszystkie")
        btn_sel_all.setObjectName("SmallGhostBtn")
        btn_sel_all.clicked.connect(lambda: self._set_all_individual_topics(True))

        btn_sel_none = QPushButton("Odznacz wszystkie")
        btn_sel_none.setObjectName("SmallGhostBtn")
        btn_sel_none.clicked.connect(lambda: self._set_all_individual_topics(False))

        btn_sel_geom = QPushButton("Tylko geometria")
        btn_sel_geom.setObjectName("SmallGhostBtn")
        btn_sel_geom.clicked.connect(self._select_only_geometry)

        btn_sel_alg = QPushButton("Tylko liczby i algebra")
        btn_sel_alg.setObjectName("SmallGhostBtn")
        btn_sel_alg.clicked.connect(self._select_only_algebra)

        quick_topic_btns.addWidget(btn_sel_all, 0, 0)
        quick_topic_btns.addWidget(btn_sel_none, 0, 1)
        quick_topic_btns.addWidget(btn_sel_geom, 1, 0)
        quick_topic_btns.addWidget(btn_sel_alg, 1, 1)
        gt_lay.addLayout(quick_topic_btns)

        topics_grid = QGridLayout()
        topics_grid.setHorizontalSpacing(8)
        topics_grid.setVerticalSpacing(3)
        for idx, t_info in enumerate(TOPICS):
            chk = QCheckBox(t_info.short_name)
            chk.setChecked(True)
            base_pct = EMPIRICAL_STATS[t_info.id].base_probability * 100.0
            chk.setToolTip(
                f"{t_info.name}\n{t_info.description}\n"
                f"Empiryczny udział w arkuszach CKE (2019–2026): {base_pct:.2f}%"
            )
            chk.toggled.connect(self._on_individual_topic_toggled)
            self._topic_checks[t_info.id] = chk
            topics_grid.addWidget(chk, idx // 2, idx % 2)
        gt_lay.addLayout(topics_grid)

        self._lbl_redistribution = QLabel()
        self._lbl_redistribution.setObjectName("RedistributionBanner")
        self._lbl_redistribution.setWordWrap(True)
        gt_lay.addWidget(self._lbl_redistribution)

        form_lay.addWidget(grp_topics)

        # 3. Typy, liczba zadań i poziom trudności
        grp_counts = QGroupBox("3. Typ, liczba zadań i poziom trudności")
        gc_lay = QVBoxLayout(grp_counts)
        gc_lay.setSpacing(8)

        counts_form = QFormLayout()
        counts_form.setSpacing(6)

        self._spin_closed = QSpinBox()
        self._spin_closed.setRange(0, 40)
        self._spin_closed.setValue(PRESETS[0].closed_count)
        self._spin_closed.valueChanged.connect(self._on_counts_manually_changed)
        counts_form.addRow("Zadania zamknięte (po 1 pkt):", self._spin_closed)

        self._spin_open2 = QSpinBox()
        self._spin_open2.setRange(0, 15)
        self._spin_open2.setValue(PRESETS[0].open_2pt_count)
        self._spin_open2.valueChanged.connect(self._on_counts_manually_changed)
        counts_form.addRow("Zadania otwarte krótkie (0–2 pkt):", self._spin_open2)

        self._spin_open3 = QSpinBox()
        self._spin_open3.setRange(0, 15)
        self._spin_open3.setValue(PRESETS[0].open_3pt_count)
        self._spin_open3.valueChanged.connect(self._on_counts_manually_changed)
        counts_form.addRow("Zadania otwarte rozszerzone (0–3 pkt):", self._spin_open3)

        self._combo_diff = QComboBox()
        self._combo_diff.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self._combo_diff.setMinimumContentsLength(16)
        self._combo_diff.addItem("Egzamin CKE (mieszany – zalecany)", userData="standard")
        self._combo_diff.addItem("Łatwiejszy (rozgrzewka i pewniaki)", userData="easy")
        self._combo_diff.addItem("Trudniejszy (zadania na 90–100%)", userData="hard")
        counts_form.addRow("Poziom trudności:", self._combo_diff)

        gc_lay.addLayout(counts_form)

        self._lbl_summary = QLabel()
        self._lbl_summary.setObjectName("SummaryBadge")
        self._lbl_summary.setWordWrap(True)
        self._lbl_summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gc_lay.addWidget(self._lbl_summary)

        lbl_subtypes = QLabel("Dozwolone formy zadań zamkniętych:")
        lbl_subtypes.setObjectName("MutedLabel")
        gc_lay.addWidget(lbl_subtypes)

        for st_id in CLOSED_SUBTYPES:
            chk_st = QCheckBox(SUBTYPE_LABELS[st_id])
            chk_st.setChecked(True)
            self._subtype_checks[st_id] = chk_st
            gc_lay.addWidget(chk_st)

        form_lay.addWidget(grp_counts)

        # 4. Metryczka i wygląd PDF CKE OMAP-100
        grp_pdf = QGroupBox("4. Szata graficzna CKE (OMAP-100) i opcje PDF")
        gpdf_lay = QVBoxLayout(grp_pdf)
        gpdf_lay.setSpacing(6)

        meta_form = QFormLayout()
        meta_form.setSpacing(6)

        self._edit_title = QLineEdit("EGZAMIN ÓSMOKLASISTY Z MATEMATYKI")
        meta_form.addRow("Tytuł główny:", self._edit_title)

        self._edit_subtitle = QLineEdit("Arkusz w formule CKE (OMAP-100)")
        meta_form.addRow("Podtytuł:", self._edit_subtitle)

        row_code_school = QHBoxLayout()
        self._edit_exam_code = QLineEdit(PRESETS[0].exam_code)
        self._edit_exam_code.setMaximumWidth(135)
        self._edit_exam_code.setToolTip("Kod arkusza CKE na okładce, w stopce i kodzie kreskowym (np. OMAP-100-2605)")
        self._edit_school = QLineEdit("")
        self._edit_school.setPlaceholderText("np. Klasa 8b / SP nr 5")
        row_code_school.addWidget(self._edit_exam_code)
        row_code_school.addWidget(self._edit_school, 1)
        meta_form.addRow("Kod CKE / szkoła:", row_code_school)

        row_ver_time = QHBoxLayout()
        self._edit_variant = QLineEdit("Wersja A")
        self._edit_variant.setMaximumWidth(110)
        self._spin_duration = QSpinBox()
        self._spin_duration.setRange(10, 240)
        self._spin_duration.setSuffix(" min")
        self._spin_duration.setValue(PRESETS[0].duration_minutes)
        row_ver_time.addWidget(self._edit_variant)
        row_ver_time.addWidget(QLabel("Czas:"))
        row_ver_time.addWidget(self._spin_duration)
        meta_form.addRow("Wersja i czas:", row_ver_time)

        row_date_seed = QHBoxLayout()
        self._edit_date = QLineEdit(datetime.date.today().strftime("%d.%m.%Y r."))
        self._edit_seed = QLineEdit("")
        self._edit_seed.setPlaceholderText("losowy")
        self._edit_seed.setToolTip("Wpisz liczbę (np. 2026), aby powtórzyć identyczny zestaw zadań.")
        self._edit_seed.setMaximumWidth(90)
        row_date_seed.addWidget(self._edit_date, 1)
        row_date_seed.addWidget(QLabel("Nr/Seed:"))
        row_date_seed.addWidget(self._edit_seed)
        meta_form.addRow("Data / zestaw:", row_date_seed)

        gpdf_lay.addLayout(meta_form)

        self._chk_cover = QCheckBox("Okładka CKE OMAP-100 (logo E8, KOD, PESEL, O-100, kod kreskowy)")
        self._chk_cover.setChecked(True)
        gpdf_lay.addWidget(self._chk_cover)

        self._chk_grid = QCheckBox("Czerwona kratka skanera 5×5 mm z ostrzeżeniami pod zadaniami otwartymi")
        self._chk_grid.setChecked(True)
        gpdf_lay.addWidget(self._chk_grid)

        self._chk_answer_card = QCheckBox("Dołącz Kartę Odpowiedzi CKE (OMR + tabela egzaminatora) na końcu")
        self._chk_answer_card.setChecked(True)
        gpdf_lay.addWidget(self._chk_answer_card)

        self._chk_diagrams = QCheckBox("Rysunki pomocnicze w kolorach CKE (geometria, wykresy, kratka)")
        self._chk_diagrams.setChecked(True)
        gpdf_lay.addWidget(self._chk_diagrams)

        self._chk_scratchpad = QCheckBox("Dodaj stronę brudnopisu na końcu arkusza")
        self._chk_scratchpad.setChecked(False)
        gpdf_lay.addWidget(self._chk_scratchpad)

        form_lay.addWidget(grp_pdf)
        form_lay.addStretch(1)

        form_scroll.setWidget(form_body)
        left_vbox.addWidget(form_scroll, 1)

        # Dolny przycisk główny "Generuj nowy arkusz"
        self._btn_generate = QPushButton("Generuj nowy arkusz CKE (Ctrl+G)")
        self._btn_generate.setObjectName("PrimaryGenerateBtn")
        self._btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_generate.clicked.connect(self.generate_new_sheet)
        left_vbox.addWidget(self._btn_generate)

        splitter.addWidget(left_panel)

        # ================= PRAWY PANEL: PODGLĄD, STATYSTYKA CKE I EKSPORT PDF =================
        right_panel = QWidget()
        right_vbox = QVBoxLayout(right_panel)
        right_vbox.setContentsMargins(0, 0, 0, 0)
        right_vbox.setSpacing(8)

        export_bar = QFrame()
        export_bar.setObjectName("ExportBar")
        eb_lay = QHBoxLayout(export_bar)
        eb_lay.setContentsMargins(14, 8, 14, 8)
        eb_lay.setSpacing(8)

        self._lbl_status = QLabel("Gotowy do generowania")
        self._lbl_status.setObjectName("SheetStatusLabel")
        eb_lay.addWidget(self._lbl_status, 1)

        btn_save_exam = QPushButton("Zapisz Arkusz PDF")
        btn_save_exam.setObjectName("ExportBtn")
        btn_save_exam.setToolTip("Zapisz plik PDF z samym arkuszem zadań dla ucznia (szata CKE OMAP-100)")
        btn_save_exam.clicked.connect(self.save_exam_pdf)
        eb_lay.addWidget(btn_save_exam)

        btn_save_key = QPushButton("Zapisz Klucz PDF")
        btn_save_key.setObjectName("ExportBtn")
        btn_save_key.setToolTip("Zapisz plik PDF z kluczem odpowiedzi, rozkładem % CKE i rozwiązaniami krok po kroku")
        btn_save_key.clicked.connect(self.save_key_pdf)
        eb_lay.addWidget(btn_save_key)

        btn_save_both = QPushButton("Zapisz Komplet (2×PDF)")
        btn_save_both.setObjectName("ExportBundleBtn")
        btn_save_both.setToolTip("Zapisz jednocześnie dwa pliki PDF: arkusz zadań CKE oraz klucz odpowiedzi")
        btn_save_both.clicked.connect(self.save_both_pdfs)
        eb_lay.addWidget(btn_save_both)

        right_vbox.addWidget(export_bar)

        # 4 zakładki w prawym panelu
        self._tabs = QTabWidget()
        self._exam_preview = PdfPreviewWidget()
        self._key_preview = PdfPreviewWidget()
        self._task_list = TaskListWidget()
        self._task_list.replace_task_requested.connect(self._on_replace_single_task)
        self._archive_stats = CKEArchiveStatsWidget()
        self._archive_stats.mirror_session_requested.connect(self._on_mirror_session_requested)

        self._tabs.addTab(self._exam_preview, "Arkusz CKE (PDF)")
        self._tabs.addTab(self._key_preview, "Klucz i Rozwiązania (PDF)")
        self._tabs.addTab(self._task_list, "Lista zadań (wymiana)")
        self._tabs.addTab(self._archive_stats, "Statystyka i Archiwum CKE")

        right_vbox.addWidget(self._tabs, 1)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([540, 880])

        self._update_summary_badge()

    def _setup_shortcuts(self) -> None:
        act_gen = QAction("Generuj", self)
        act_gen.setShortcut(QKeySequence("Ctrl+G"))
        act_gen.triggered.connect(self.generate_new_sheet)
        self.addAction(act_gen)

        act_save = QAction("Zapisz komplet PDF", self)
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self.save_both_pdfs)
        self.addAction(act_save)

        act_theme = QAction("Przełącz motyw jasny/ciemny", self)
        act_theme.setShortcut(QKeySequence("Ctrl+D"))
        act_theme.triggered.connect(self.toggle_dark_mode)
        self.addAction(act_theme)

    # ------------------------------------------------------------------
    # Obsługa motywu jasnego / ciemnego / systemowego
    # ------------------------------------------------------------------
    def _on_theme_combo_changed(self, _index: int) -> None:
        mode = str(self._combo_theme.currentData() or "system")
        self.apply_theme_mode(mode, persist=True)

    def toggle_dark_mode(self) -> None:
        new_mode = "light" if self._is_dark else "dark"
        self.apply_theme_mode(new_mode, persist=True)

    def apply_theme_mode(self, mode: str, persist: bool = True) -> None:
        if mode not in ("system", "light", "dark"):
            mode = "system"
        self._theme_mode = mode
        if persist:
            save_theme_mode(mode)

        idx = self._combo_theme.findData(mode)
        if idx >= 0 and self._combo_theme.currentIndex() != idx:
            self._combo_theme.blockSignals(True)
            self._combo_theme.setCurrentIndex(idx)
            self._combo_theme.blockSignals(False)

        if mode == "dark":
            is_dark = True
        elif mode == "light":
            is_dark = False
        else:
            is_dark = detect_system_dark_mode()

        self._is_dark = is_dark
        self.setStyleSheet(get_stylesheet(is_dark))
        self._exam_preview.set_dark_mode(is_dark)
        self._key_preview.set_dark_mode(is_dark)
        self._task_list.set_dark_mode(is_dark)
        self._archive_stats.set_dark_mode(is_dark)

    # ------------------------------------------------------------------
    # Dynamiczne przeliczanie procentów działów CKE + równej redystrybucji
    # ------------------------------------------------------------------
    def _compute_ui_active_probabilities(self) -> Dict[str, float]:
        checked_ids = [t.id for t in TOPICS if self._topic_checks[t.id].isChecked()]
        if not checked_ids:
            return {t.id: 0.0 for t in TOPICS}
        mode = str(self._combo_dist.currentData() or "cke_probabilistic")
        if mode == "uniform":
            eq = 1.0 / len(checked_ids)
            return {t.id: (eq if t.id in checked_ids else 0.0) for t in TOPICS}
        return compute_active_topic_probabilities(checked_ids)

    def _refresh_live_topic_percentages(self) -> None:
        """Aktualizuje na żywo etykiety % na wszystkich 12 checkboxach oraz pasek wyjaśnienia redystrybucji."""
        probs = self._compute_ui_active_probabilities()
        checked_ids = [t.id for t in TOPICS if self._topic_checks[t.id].isChecked()]
        n_active = len(checked_ids)
        n_removed = len(TOPICS) - n_active
        mode = str(self._combo_dist.currentData() or "cke_probabilistic")

        for t_info in TOPICS:
            chk = self._topic_checks[t_info.id]
            p = probs.get(t_info.id, 0.0) * 100.0
            if chk.isChecked():
                pct_str = f"{p:.1f}%".replace(".", ",")
                chk.setText(f"{t_info.short_name} ({pct_str})")
            else:
                chk.setText(f"{t_info.short_name} (0%)")

        if n_active == 0:
            self._lbl_redistribution.setText("Zaznacz co najmniej jeden dział, aby wyznaczyć rozkład zadań.")
        elif mode == "uniform":
            eq_pct = f"{100.0 / n_active:.1f}".replace(".", ",")
            self._lbl_redistribution.setText(
                f"Tryb równych wag: każdy z {n_active} zaznaczonych działów ma dokładnie {eq_pct}% szans."
            )
        elif n_removed == 0:
            self._lbl_redistribution.setText(
                "Aktywne wszystkie 12 działów: oryginalne empiryczne prawdopodobieństwa CKE (2019–2026)."
            )
        else:
            removed_sum = sum(
                EMPIRICAL_STATS[t.id].base_probability for t in TOPICS if not self._topic_checks[t.id].isChecked()
            ) * 100.0
            bonus_each = removed_sum / n_active
            rem_s = f"{removed_sum:.1f}".replace(".", ",")
            bon_s = f"{bonus_each:.2f}".replace(".", ",")
            self._lbl_redistribution.setText(
                f"Wykreślono {n_removed} z 12 działów (łącznie {rem_s}% CKE) → "
                f"rozdzielono po równo +{bon_s}% na każdy z {n_active} aktywnych działów."
            )

        total_tasks_hint = self._spin_closed.value() + self._spin_open2.value() + self._spin_open3.value()
        self._archive_stats.refresh_probabilities(probs, self._current_sheet, total_tasks_hint)

    # ------------------------------------------------------------------
    # Logika formularza i przełączników
    # ------------------------------------------------------------------
    def _on_preset_changed(self, _index: int) -> None:
        preset_id = self._combo_preset.currentData()
        preset = PRESET_BY_ID.get(preset_id)
        if not preset:
            return
        self._lbl_preset_desc.setText(preset.description)
        if preset_id == "custom":
            return

        self._updating_preset_fields = True
        try:
            self._spin_closed.setValue(preset.closed_count)
            self._spin_open2.setValue(preset.open_2pt_count)
            self._spin_open3.setValue(preset.open_3pt_count)
            self._spin_duration.setValue(preset.duration_minutes)
            self._edit_exam_code.setText(preset.exam_code)
            is_full = (preset.closed_count + preset.open_2pt_count + preset.open_3pt_count) >= 14
            self._chk_cover.setChecked(is_full)
            self._chk_answer_card.setChecked(is_full)
        finally:
            self._updating_preset_fields = False
        self._update_summary_badge()
        self._refresh_live_topic_percentages()

    def _on_distribution_mode_changed(self, _index: int) -> None:
        mode = str(self._combo_dist.currentData() or "cke_probabilistic")
        if mode.startswith("mirror_session:"):
            sess_id = mode.split(":", 1)[1]
            sess = SESSION_BY_ID.get(sess_id)
            if sess:
                self._updating_preset_fields = True
                try:
                    c_cnt = sess.closed_count
                    o2_cnt = sum(1 for t in sess.tasks if t.points == 2)
                    o3_cnt = sum(1 for t in sess.tasks if t.points >= 3)
                    self._spin_closed.setValue(c_cnt)
                    self._spin_open2.setValue(o2_cnt)
                    self._spin_open3.setValue(o3_cnt)
                    self._spin_duration.setValue(sess.duration_min)
                    self._edit_exam_code.setText(sess.code)
                    self._edit_subtitle.setText(f"Zestaw nowych zadań wg układu sesji {sess.name}")
                finally:
                    self._updating_preset_fields = False
                self._update_summary_badge()
        self._refresh_live_topic_percentages()

    def _on_mirror_session_requested(self, sess_id: str) -> None:
        target_data = f"mirror_session:{sess_id}"
        idx = self._combo_dist.findData(target_data)
        if idx >= 0:
            self._combo_dist.setCurrentIndex(idx)
        self.generate_new_sheet()
        self._tabs.setCurrentIndex(0)

    def _on_counts_manually_changed(self) -> None:
        if not self._updating_preset_fields:
            idx_custom = self._combo_preset.findData("custom")
            if idx_custom >= 0 and self._combo_preset.currentIndex() != idx_custom:
                self._combo_preset.blockSignals(True)
                self._combo_preset.setCurrentIndex(idx_custom)
                self._lbl_preset_desc.setText(PRESET_BY_ID["custom"].description)
                self._combo_preset.blockSignals(False)
            # Jeśli był aktywny tryb mirror_session, przełącz na cke_probabilistic przy ręcznej zmianie liczby zadań
            if str(self._combo_dist.currentData() or "").startswith("mirror_session:"):
                self._combo_dist.blockSignals(True)
                self._combo_dist.setCurrentIndex(0)
                self._combo_dist.blockSignals(False)
        self._update_summary_badge()
        self._refresh_live_topic_percentages()

    def _update_summary_badge(self) -> None:
        c = self._spin_closed.value()
        o2 = self._spin_open2.value()
        o3 = self._spin_open3.value()
        total_tasks = c + o2 + o3
        total_pts = c * 1 + o2 * 2 + o3 * 3
        self._lbl_summary.setText(f"Podsumowanie zestawu:  {total_tasks} zadań   |   Suma punktów: {total_pts} pkt")

    def _on_all_topics_toggled(self, checked: bool) -> None:
        if checked:
            self._set_all_individual_topics(True)

    def _set_all_individual_topics(self, state: bool) -> None:
        for chk in self._topic_checks.values():
            chk.blockSignals(True)
            chk.setChecked(state)
            chk.blockSignals(False)
        self._chk_all_topics.blockSignals(True)
        self._chk_all_topics.setChecked(state)
        self._chk_all_topics.blockSignals(False)
        self._refresh_live_topic_percentages()

    def _select_only_geometry(self) -> None:
        geom_ids = {"uklad_wspolrzednych", "geometria_plaska", "geometria_przestrzenna"}
        for tid, chk in self._topic_checks.items():
            chk.blockSignals(True)
            chk.setChecked(tid in geom_ids)
            chk.blockSignals(False)
        self._chk_all_topics.blockSignals(True)
        self._chk_all_topics.setChecked(False)
        self._chk_all_topics.blockSignals(False)
        self._refresh_live_topic_percentages()

    def _select_only_algebra(self) -> None:
        alg_ids = {
            "liczby_dzialania",
            "procenty_proporcje",
            "potegi_notacja",
            "pierwiastki",
            "wyrazenia_algebraiczne",
            "rownania_tekstowe",
        }
        for tid, chk in self._topic_checks.items():
            chk.blockSignals(True)
            chk.setChecked(tid in alg_ids)
            chk.blockSignals(False)
        self._chk_all_topics.blockSignals(True)
        self._chk_all_topics.setChecked(False)
        self._chk_all_topics.blockSignals(False)
        self._refresh_live_topic_percentages()

    def _on_individual_topic_toggled(self) -> None:
        all_on = all(chk.isChecked() for chk in self._topic_checks.values())
        self._chk_all_topics.blockSignals(True)
        self._chk_all_topics.setChecked(all_on)
        self._chk_all_topics.blockSignals(False)
        self._refresh_live_topic_percentages()

    # ------------------------------------------------------------------
    # Odczyt konfiguracji i generowanie arkusza
    # ------------------------------------------------------------------
    def _collect_config(self) -> Optional[ExamConfig]:
        c_cnt = self._spin_closed.value()
        o2_cnt = self._spin_open2.value()
        o3_cnt = self._spin_open3.value()
        if c_cnt + o2_cnt + o3_cnt == 0:
            QMessageBox.warning(self, "Brak zadań", "Ustaw co najmniej jedno zadanie (zamknięte lub otwarte).")
            return None

        if self._chk_all_topics.isChecked():
            selected_topics: List[str] = [t.id for t in TOPICS]
        else:
            selected_topics = [tid for tid, chk in self._topic_checks.items() if chk.isChecked()]
            if not selected_topics:
                QMessageBox.warning(
                    self,
                    "Nie wybrano tematów",
                    "Zaznacz przynajmniej jeden dział tematyczny albo włącz opcję „Cały materiał E8”.",
                )
                return None

        allowed_subtypes = [sid for sid, chk in self._subtype_checks.items() if chk.isChecked()]
        if c_cnt > 0 and not allowed_subtypes:
            QMessageBox.warning(
                self,
                "Brak typu zadań zamkniętych",
                "Zaznacz przynajmniej jeden rodzaj zadań zamkniętych (np. Wybór wielokrotny A, B, C, D).",
            )
            return None

        seed_val: Optional[int] = None
        seed_raw = self._edit_seed.text().strip()
        if seed_raw:
            try:
                seed_val = int(seed_raw)
            except ValueError:
                QMessageBox.warning(self, "Błędny numer zestawu (Seed)", "Pole Nr/Seed musi być liczbą całkowitą lub pozostać puste.")
                return None

        return ExamConfig(
            preset_id=str(self._combo_preset.currentData()),
            title=self._edit_title.text().strip() or "EGZAMIN ÓSMOKLASISTY Z MATEMATYKI",
            subtitle=self._edit_subtitle.text().strip() or "Arkusz w formule CKE (OMAP-100)",
            exam_code=self._edit_exam_code.text().strip() or "OMAP-100-2605",
            school_or_group=self._edit_school.text().strip(),
            exam_date_str=self._edit_date.text().strip(),
            variant_code=self._edit_variant.text().strip() or "Wersja A",
            duration_minutes=self._spin_duration.value(),
            selected_topics=selected_topics,
            distribution_mode=str(self._combo_dist.currentData() or "cke_probabilistic"),
            closed_count=c_cnt,
            open_2pt_count=o2_cnt,
            open_3pt_count=o3_cnt,
            allowed_closed_subtypes=allowed_subtypes,
            difficulty_mode=str(self._combo_diff.currentData()),
            include_cover_page=self._chk_cover.isChecked(),
            include_answer_grid_for_open=self._chk_grid.isChecked(),
            include_answer_card=self._chk_answer_card.isChecked(),
            include_scratchpad_page=self._chk_scratchpad.isChecked(),
            include_diagrams=self._chk_diagrams.isChecked(),
            seed=seed_val,
        )

    def generate_new_sheet(self) -> None:
        cfg = self._collect_config()
        if cfg is None:
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self._current_sheet = generate_exam_sheet(cfg)
            self._rebuild_previews()
        finally:
            QApplication.restoreOverrideCursor()

    def _on_replace_single_task(self, task_index: int) -> None:
        if self._current_sheet is None:
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            replace_single_task(self._current_sheet, task_index)
            self._rebuild_previews()
        finally:
            QApplication.restoreOverrideCursor()

    def _rebuild_previews(self) -> None:
        if self._current_sheet is None:
            return
        sheet = self._current_sheet
        self._exam_pdf_bytes = build_exam_pdf_bytes(sheet)
        self._key_pdf_bytes = build_key_pdf_bytes(sheet)

        self._exam_preview.set_pdf_bytes(self._exam_pdf_bytes)
        self._key_preview.set_pdf_bytes(self._key_pdf_bytes)
        self._task_list.set_sheet(sheet)
        self._archive_stats.refresh_probabilities(
            sheet.topic_probabilities or self._compute_ui_active_probabilities(),
            sheet,
            len(sheet.tasks),
        )

        full_status = (
            f"{sheet.config.exam_code} · {sheet.config.variant_code} · Zestaw #{sheet.used_seed} · "
            f"{len(sheet.tasks)} zadań ({len(sheet.closed_tasks)} zamkn. + {len(sheet.open_tasks)} otw.) · "
            f"{sheet.total_points} pkt"
        )
        self._lbl_status.setText(
            f"{sheet.config.exam_code} · #{sheet.used_seed} · "
            f"{len(sheet.tasks)} zad. ({sheet.total_points} pkt)"
        )
        self._lbl_status.setToolTip(full_status)

    # ------------------------------------------------------------------
    # Zapisywanie wygenerowanych plików PDF
    # ------------------------------------------------------------------
    def _default_stem_name(self) -> str:
        if not self._current_sheet:
            return "E8_matematyka"
        ver = self._current_sheet.config.variant_code.replace(" ", "_")
        return f"E8_matematyka_{ver}_{self._current_sheet.used_seed}"

    def save_exam_pdf(self) -> None:
        if not self._exam_pdf_bytes:
            return
        default_name = f"{self._default_stem_name()}_ARKUSZ.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Zapisz Arkusz Egzaminacyjny PDF", default_name, "Pliki PDF (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        Path(path).write_bytes(self._exam_pdf_bytes)
        QMessageBox.information(self, "Zapisano arkusz", f"Arkusz zadań został zapisany w pliku:\n{path}")

    def save_key_pdf(self) -> None:
        if not self._key_pdf_bytes:
            return
        default_name = f"{self._default_stem_name()}_KLUCZ.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Zapisz Klucz Odpowiedzi i Rozwiązania PDF", default_name, "Pliki PDF (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        Path(path).write_bytes(self._key_pdf_bytes)
        QMessageBox.information(self, "Zapisano klucz", f"Klucz odpowiedzi i rozwiązań został zapisany w pliku:\n{path}")

    def save_both_pdfs(self) -> None:
        if not self._exam_pdf_bytes or not self._key_pdf_bytes:
            return
        default_name = f"{self._default_stem_name()}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Wybierz nazwę bazową kompletu (zostaną zapisane 2 pliki: _ARKUSZ.pdf oraz _KLUCZ.pdf)",
            default_name,
            "Pliki PDF (*.pdf)",
        )
        if not path:
            return
        base = path[:-4] if path.lower().endswith(".pdf") else path
        exam_path = f"{base}_ARKUSZ.pdf"
        key_path = f"{base}_KLUCZ.pdf"
        Path(exam_path).write_bytes(self._exam_pdf_bytes)
        Path(key_path).write_bytes(self._key_pdf_bytes)
        QMessageBox.information(
            self,
            "Zapisano komplet PDF",
            f"Pomyślnie zapisano oba pliki PDF:\n\n1) Arkusz dla ucznia:\n{exam_path}\n\n2) Klucz z rozwiązaniami:\n{key_path}",
        )
