"""Główne okno aplikacji desktopowej Generator Zadań E8 – Matematyka (PyQt6)."""

from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import Dict, Optional

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

from ..engine import generate_exam_sheet, replace_single_task
from ..models import (
    CLOSED_SUBTYPES,
    PRESETS,
    PRESET_BY_ID,
    SUBTYPE_LABELS,
    TOPICS,
    ExamConfig,
    ExamSheet,
)
from ..pdf_exporter import build_exam_pdf_bytes, build_key_pdf_bytes
from .preview_widget import PdfPreviewWidget
from .styles import APP_STYLESHEET
from .task_list_widget import TaskListWidget


class MainWindow(QMainWindow):
    """Główne okno programu z formularzem konfiguracji po lewej i podglądem PDF po prawej."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generator Zadań E8 – Matematyka (styl i poziom CKE)")
        self.resize(1380, 880)
        self.setMinimumSize(1040, 680)
        self.setStyleSheet(APP_STYLESHEET)

        self._current_sheet: Optional[ExamSheet] = None
        self._exam_pdf_bytes: Optional[bytes] = None
        self._key_pdf_bytes: Optional[bytes] = None
        self._updating_preset_fields: bool = False

        self._topic_checks: Dict[str, QCheckBox] = {}
        self._subtype_checks: Dict[str, QCheckBox] = {}

        self._build_ui()
        self._setup_shortcuts()

        # Wygeneruj od razu pierwszy przykładowy arkusz po uruchomieniu, żeby okno nie było puste
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
        left_panel.setMinimumWidth(455)
        left_panel.setMaximumWidth(530)
        left_vbox = QVBoxLayout(left_panel)
        left_vbox.setContentsMargins(0, 0, 0, 0)
        left_vbox.setSpacing(8)

        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        form_body = QWidget()
        form_lay = QVBoxLayout(form_body)
        form_lay.setContentsMargins(4, 2, 16, 8)
        form_lay.setSpacing(8)

        # Nagłówek aplikacji w lewym panelu
        app_hdr = QLabel("Generator Zadań E8 – Matematyka")
        app_hdr.setObjectName("HeaderTitle")
        app_sub = QLabel("Twórz pełne arkusze próbne CKE lub zestawy z wybranych działów wraz z kluczem odpowiedzi.")
        app_sub.setObjectName("MutedLabel")
        app_sub.setWordWrap(True)
        form_lay.addWidget(app_hdr)
        form_lay.addWidget(app_sub)

        # 1. Układ arkusza (Preset)
        grp_preset = QGroupBox("1. Układ arkusza / szybki szablon")
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

        # 2. Zakres tematyczny (Działy E8)
        grp_topics = QGroupBox("2. Z jakich tematów generować zadania?")
        gt_lay = QVBoxLayout(grp_topics)
        gt_lay.setSpacing(6)

        self._chk_all_topics = QCheckBox("Cały materiał E8 (wszystkie działy jak na egzaminie)")
        self._chk_all_topics.setChecked(True)
        self._chk_all_topics.setStyleSheet("font-weight: 700; color: #1E3A8A;")
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
        topics_grid.setHorizontalSpacing(10)
        topics_grid.setVerticalSpacing(3)
        for idx, t_info in enumerate(TOPICS):
            chk = QCheckBox(t_info.short_name)
            chk.setChecked(True)
            chk.setToolTip(f"{t_info.name}\n{t_info.description}")
            chk.toggled.connect(self._on_individual_topic_toggled)
            self._topic_checks[t_info.id] = chk
            topics_grid.addWidget(chk, idx // 2, idx % 2)
        gt_lay.addLayout(topics_grid)
        form_lay.addWidget(grp_topics)

        # 3. Typy, liczba zadań i poziom trudności
        grp_counts = QGroupBox("3. Typ, liczba zadań i poziom trudności")
        gc_lay = QVBoxLayout(grp_counts)
        gc_lay.setSpacing(8)

        counts_form = QFormLayout()
        counts_form.setSpacing(6)

        self._spin_closed = QSpinBox()
        self._spin_closed.setRange(0, 40)
        self._spin_closed.setValue(15)
        self._spin_closed.valueChanged.connect(self._on_counts_manually_changed)
        counts_form.addRow("Zadania zamknięte (po 1 pkt):", self._spin_closed)

        self._spin_open2 = QSpinBox()
        self._spin_open2.setRange(0, 15)
        self._spin_open2.setValue(3)
        self._spin_open2.valueChanged.connect(self._on_counts_manually_changed)
        counts_form.addRow("Zadania otwarte krótkie (0–2 pkt):", self._spin_open2)

        self._spin_open3 = QSpinBox()
        self._spin_open3.setRange(0, 15)
        self._spin_open3.setValue(3)
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

        # 4. Metryczka i wygląd PDF
        grp_pdf = QGroupBox("4. Nagłówek i opcje arkusza PDF")
        gpdf_lay = QVBoxLayout(grp_pdf)
        gpdf_lay.setSpacing(6)

        meta_form = QFormLayout()
        meta_form.setSpacing(6)

        self._edit_title = QLineEdit("EGZAMIN ÓSMOKLASISTY Z MATEMATYKI")
        meta_form.addRow("Tytuł główny:", self._edit_title)

        self._edit_subtitle = QLineEdit("Arkusz próbny w stylu CKE")
        meta_form.addRow("Podtytuł:", self._edit_subtitle)

        self._edit_school = QLineEdit("")
        self._edit_school.setPlaceholderText("np. Klasa 8b / Szkoła Podstawowa nr 5")
        meta_form.addRow("Szkoła / klasa:", self._edit_school)

        row_ver_time = QHBoxLayout()
        self._edit_variant = QLineEdit("Wersja A")
        self._edit_variant.setMaximumWidth(110)
        self._spin_duration = QSpinBox()
        self._spin_duration.setRange(10, 240)
        self._spin_duration.setSuffix(" min")
        self._spin_duration.setValue(125)
        row_ver_time.addWidget(self._edit_variant)
        row_ver_time.addWidget(QLabel("Czas:"))
        row_ver_time.addWidget(self._spin_duration)
        meta_form.addRow("Wersja i czas:", row_ver_time)

        row_date_seed = QHBoxLayout()
        self._edit_date = QLineEdit(datetime.date.today().strftime("%d.%m.%Y r."))
        self._edit_seed = QLineEdit("")
        self._edit_seed.setPlaceholderText("losowy")
        self._edit_seed.setToolTip("Wpisz liczbę (np. 101), aby powtórzyć identyczny zestaw zadań.")
        self._edit_seed.setMaximumWidth(90)
        row_date_seed.addWidget(self._edit_date, 1)
        row_date_seed.addWidget(QLabel("Nr/Seed:"))
        row_date_seed.addWidget(self._edit_seed)
        meta_form.addRow("Data / zestaw:", row_date_seed)

        gpdf_lay.addLayout(meta_form)

        self._chk_cover = QCheckBox("Strona tytułowa CKE (kod ucznia, PESEL, instrukcja)")
        self._chk_cover.setChecked(True)
        gpdf_lay.addWidget(self._chk_cover)

        self._chk_grid = QCheckBox("Kratka do obliczeń i ramka „Odpowiedź” pod zadaniami otwartymi")
        self._chk_grid.setChecked(True)
        gpdf_lay.addWidget(self._chk_grid)

        self._chk_diagrams = QCheckBox("Rysunki pomocnicze (geometria, wykresy, układ współrzędnych)")
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
        self._btn_generate = QPushButton("Generuj nowy arkusz (Ctrl+G)")
        self._btn_generate.setObjectName("PrimaryGenerateBtn")
        self._btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_generate.clicked.connect(self.generate_new_sheet)
        left_vbox.addWidget(self._btn_generate)

        splitter.addWidget(left_panel)

        # ================= PRAWY PANEL: PODGLĄD I EKSPORT PDF =================
        right_panel = QWidget()
        right_vbox = QVBoxLayout(right_panel)
        right_vbox.setContentsMargins(0, 0, 0, 0)
        right_vbox.setSpacing(8)

        # Pasek eksportu na górze prawego panelu
        export_bar = QFrame()
        export_bar.setObjectName("ExportBar")
        eb_lay = QHBoxLayout(export_bar)
        eb_lay.setContentsMargins(14, 8, 14, 8)
        eb_lay.setSpacing(8)

        self._lbl_status = QLabel("Gotowy do generowania")
        self._lbl_status.setObjectName("SheetStatusLabel")
        eb_lay.addWidget(self._lbl_status, 1)

        btn_save_exam = QPushButton("Zapisz Arkusz PDF...")
        btn_save_exam.setObjectName("ExportBtn")
        btn_save_exam.setToolTip("Zapisz plik PDF z samym arkuszem zadań dla ucznia")
        btn_save_exam.clicked.connect(self.save_exam_pdf)
        eb_lay.addWidget(btn_save_exam)

        btn_save_key = QPushButton("Zapisz Klucz PDF...")
        btn_save_key.setObjectName("ExportBtn")
        btn_save_key.setToolTip("Zapisz plik PDF z kluczem odpowiedzi, rozwiązaniami krok po kroku i punktacją CKE")
        btn_save_key.clicked.connect(self.save_key_pdf)
        eb_lay.addWidget(btn_save_key)

        btn_save_both = QPushButton("Zapisz Komplet (2×PDF)...")
        btn_save_both.setObjectName("ExportBundleBtn")
        btn_save_both.setToolTip("Zapisz jednocześnie dwa pliki PDF: arkusz zadań oraz klucz odpowiedzi")
        btn_save_both.clicked.connect(self.save_both_pdfs)
        eb_lay.addWidget(btn_save_both)

        right_vbox.addWidget(export_bar)

        # Zakładki podglądu
        self._tabs = QTabWidget()
        self._exam_preview = PdfPreviewWidget()
        self._key_preview = PdfPreviewWidget()
        self._task_list = TaskListWidget()
        self._task_list.replace_task_requested.connect(self._on_replace_single_task)

        self._tabs.addTab(self._exam_preview, "Podgląd Arkusza CKE (PDF)")
        self._tabs.addTab(self._key_preview, "Podgląd Klucza i Rozwiązań (PDF)")
        self._tabs.addTab(self._task_list, "Lista zadań (wymiana pojedynczych zadań)")

        right_vbox.addWidget(self._tabs, 1)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([470, 910])

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
            self._chk_cover.setChecked(preset.closed_count + preset.open_2pt_count + preset.open_3pt_count >= 14)
        finally:
            self._updating_preset_fields = False
        self._update_summary_badge()

    def _on_counts_manually_changed(self) -> None:
        if not self._updating_preset_fields:
            # Przełącz listę na "Własna konfiguracja", jeśli użytkownik ręcznie zmienił liczby zadań
            idx_custom = self._combo_preset.findData("custom")
            if idx_custom >= 0 and self._combo_preset.currentIndex() != idx_custom:
                self._combo_preset.blockSignals(True)
                self._combo_preset.setCurrentIndex(idx_custom)
                self._lbl_preset_desc.setText(PRESET_BY_ID["custom"].description)
                self._combo_preset.blockSignals(False)
        self._update_summary_badge()

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

    def _select_only_geometry(self) -> None:
        geom_ids = {"uklad_wspolrzednych", "geometria_plaska", "geometria_przestrzenna"}
        for tid, chk in self._topic_checks.items():
            chk.blockSignals(True)
            chk.setChecked(tid in geom_ids)
            chk.blockSignals(False)
        self._chk_all_topics.blockSignals(True)
        self._chk_all_topics.setChecked(False)
        self._chk_all_topics.blockSignals(False)

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

    def _on_individual_topic_toggled(self) -> None:
        all_on = all(chk.isChecked() for chk in self._topic_checks.values())
        self._chk_all_topics.blockSignals(True)
        self._chk_all_topics.setChecked(all_on)
        self._chk_all_topics.blockSignals(False)

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
            selected_topics = [t.id for t in TOPICS]
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
            subtitle=self._edit_subtitle.text().strip() or "Arkusz próbny w stylu CKE",
            school_or_group=self._edit_school.text().strip(),
            exam_date_str=self._edit_date.text().strip(),
            variant_code=self._edit_variant.text().strip() or "Wersja A",
            duration_minutes=self._spin_duration.value(),
            selected_topics=selected_topics,
            closed_count=c_cnt,
            open_2pt_count=o2_cnt,
            open_3pt_count=o3_cnt,
            allowed_closed_subtypes=allowed_subtypes,
            difficulty_mode=str(self._combo_diff.currentData()),
            include_cover_page=self._chk_cover.isChecked(),
            include_answer_grid_for_open=self._chk_grid.isChecked(),
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

        self._lbl_status.setText(
            f"{sheet.config.variant_code} · Zestaw #{sheet.used_seed} · "
            f"{len(sheet.tasks)} zadań ({len(sheet.closed_tasks)} zamkn. + {len(sheet.open_tasks)} otw.) · "
            f"{sheet.total_points} pkt"
        )

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
