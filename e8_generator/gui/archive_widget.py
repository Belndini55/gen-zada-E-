"""Zakładka GUI: Archiwum 12 oficjalnych arkuszy CKE (2019–2026) oraz interaktywna statystyka prawdopodobieństwa."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..cke_archive import (
    EMPIRICAL_STATS,
    HISTORICAL_CKE_EXAMS,
    SESSION_BY_ID,
    sample_topic_quotas_stratified,
)
from ..models import SUBTYPE_LABELS, TOPIC_BY_ID, TOPICS, ExamSheet


class CKEArchiveStatsWidget(QWidget):
    """Panel prezentujący empiryczne prawdopodobieństwa CKE, równą redystrybucję oraz katalog 12 sesji CKE."""

    mirror_session_requested = pyqtSignal(str)  # emituje session_id, np. "cke_2026_05"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._is_dark: bool = False
        self._active_probs: Dict[str, float] = {
            t.id: EMPIRICAL_STATS[t.id].base_probability for t in TOPICS
        }
        self._current_sheet: Optional[ExamSheet] = None
        self._tasks_per_sheet_hint: int = 20

        self._build_ui()
        self._populate_session_table()
        self.refresh_probabilities(self._active_probs, None)

    def set_dark_mode(self, is_dark: bool) -> None:
        if self._is_dark != is_dark:
            self._is_dark = is_dark
            self.refresh_probabilities(self._active_probs, self._current_sheet, self._tasks_per_sheet_hint)

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        lay.addWidget(splitter, 1)

        # ================= GÓRNA SEKCJA: ROZKŁAD PRAWDOPODOBIEŃSTWA CKE =================
        grp_stats = QGroupBox("Rozkład prawdopodobieństwa działów CKE (12 arkuszy z lat 2019–2026, łącznie 240 zadań)")
        gs_lay = QVBoxLayout(grp_stats)
        gs_lay.setSpacing(6)

        top_bar = QHBoxLayout()
        self._lbl_formula_info = QLabel(
            "Gdy wykreślisz (odznaczysz) wybrane działy w panelu po lewej stronie, ich łączny procent CKE jest "
            "<b>dzielony po równo</b> pomiędzy wszystkie pozostałe aktywne działy:  "
            "<b>p'ᵢ = pᵢ + (suma % wykreślonych) / (liczba aktywnych)</b>."
        )
        self._lbl_formula_info.setWordWrap(True)
        self._lbl_formula_info.setObjectName("MutedLabel")
        top_bar.addWidget(self._lbl_formula_info, 1)

        self._btn_monte_carlo = QPushButton("Przetestuj rozkład (symulacja 1 000 arkuszy)")
        self._btn_monte_carlo.setObjectName("ExportBtn")
        self._btn_monte_carlo.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_monte_carlo.setToolTip(
            "Losuje 1 000 pełnych rozkładów zadań dla aktualnie zaznaczonych działów "
            "i porównuje średni udział % każdego działu z celem matematycznym."
        )
        self._btn_monte_carlo.clicked.connect(self._run_monte_carlo_test)
        top_bar.addWidget(self._btn_monte_carlo)
        gs_lay.addLayout(top_bar)

        self._tbl_probs = QTableWidget(len(TOPICS), 6)
        self._tbl_probs.setHorizontalHeaderLabels([
            "Dział E8",
            "Baza CKE (240 zad.)",
            "Cel aktywny %",
            "Wykres udziału",
            "W bieżącym arkuszu",
            "Test 1 000 arkuszy",
        ])
        self._tbl_probs.verticalHeader().setVisible(False)
        self._tbl_probs.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tbl_probs.setAlternatingRowColors(True)
        hdr = self._tbl_probs.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._tbl_probs.setColumnWidth(3, 135)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # Tworzymy paski postępu JEDNOKROTNIE, aby uniknąć nakładania widżetów przy ukrytej zakładce
        self._prob_bars: List[QProgressBar] = []
        for r in range(len(TOPICS)):
            bar = QProgressBar(self._tbl_probs)
            bar.setRange(0, 1000)
            bar.setValue(0)
            self._tbl_probs.setCellWidget(r, 3, bar)
            self._prob_bars.append(bar)

        gs_lay.addWidget(self._tbl_probs, 1)

        splitter.addWidget(grp_stats)

        # ================= DOLNA SEKCJA: PRZEGLĄDARKA 12 ARKUSZY CKE =================
        grp_arch = QGroupBox("Katalog autentycznych arkuszy CKE Egzaminu Ósmoklasisty (2019–2026)")
        ga_lay = QVBoxLayout(grp_arch)
        ga_lay.setSpacing(6)

        arch_bar = QHBoxLayout()
        arch_bar.addWidget(QLabel("Wybierz arkusz CKE:"))

        self._combo_session = QComboBox()
        for sess in HISTORICAL_CKE_EXAMS:
            self._combo_session.addItem(
                f"{sess.name} [{sess.code}] – {sess.total_tasks} zad., {sess.total_points} pkt ({sess.duration_min} min)",
                userData=sess.session_id,
            )
        self._combo_session.currentIndexChanged.connect(self._populate_session_table)
        arch_bar.addWidget(self._combo_session, 1)

        self._btn_mirror = QPushButton("Generuj nowe zadania wg układu tej sesji")
        self._btn_mirror.setObjectName("CompactPrimaryBtn")
        self._btn_mirror.setToolTip(
            "Układa zupełnie nowe, losowo wygenerowane zadania z zachowaniem rozkładu działów i punktacji wybranego arkusza CKE."
        )
        self._btn_mirror.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_mirror.clicked.connect(self._on_mirror_clicked)
        arch_bar.addWidget(self._btn_mirror)
        ga_lay.addLayout(arch_bar)

        self._lbl_session_meta = QLabel()
        self._lbl_session_meta.setObjectName("MutedLabel")
        ga_lay.addWidget(self._lbl_session_meta)

        self._tbl_session = QTableWidget(0, 5)
        self._tbl_session.setHorizontalHeaderLabels([
            "Zad.",
            "Pkt",
            "Typ CKE",
            "Dział podstawy programowej",
            "Temat oryginalnego zadania CKE",
        ])
        self._tbl_session.verticalHeader().setVisible(False)
        self._tbl_session.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tbl_session.setAlternatingRowColors(True)
        shdr = self._tbl_session.horizontalHeader()
        shdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        shdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        shdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        shdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        shdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        ga_lay.addWidget(self._tbl_session, 1)

        splitter.addWidget(grp_arch)
        splitter.setSizes([400, 340])

    def refresh_probabilities(
        self,
        active_probs: Dict[str, float],
        sheet: Optional[ExamSheet],
        tasks_per_sheet_hint: int = 20,
    ) -> None:
        """Odświeża tabelę prawdopodobieństwa po zmianie checkboxów lub po wygenerowaniu nowego arkusza."""
        self._active_probs = dict(active_probs)
        if sheet is not None:
            self._current_sheet = sheet
            self._tasks_per_sheet_hint = max(1, len(sheet.tasks))
        else:
            self._tasks_per_sheet_hint = max(1, tasks_per_sheet_hint)

        sheet_counts: Dict[str, int] = {}
        sheet_pts: Dict[str, int] = {}
        n_sheet = 0
        if self._current_sheet is not None:
            n_sheet = len(self._current_sheet.tasks)
            for t in self._current_sheet.tasks:
                sheet_counts[t.topic_id] = sheet_counts.get(t.topic_id, 0) + 1
                sheet_pts[t.topic_id] = sheet_pts.get(t.topic_id, 0) + t.points

        bold_font = QFont()
        bold_font.setBold(True)
        muted_fg = QColor("#64748B") if self._is_dark else QColor("#94A3B8")
        boost_fg = QColor("#A3E635") if self._is_dark else QColor("#3D5E18")
        hint_fg = QColor("#94A3B8") if self._is_dark else QColor("#64748B")

        for row, top in enumerate(TOPICS):
            st = EMPIRICAL_STATS[top.id]
            base_p = st.base_probability
            act_p = active_probs.get(top.id, 0.0)
            diff_p = act_p - base_p

            it_name = QTableWidgetItem(top.short_name)
            if act_p <= 0.0:
                it_name.setForeground(muted_fg)
            self._tbl_probs.setItem(row, 0, it_name)

            base_txt = f"{st.total_tasks}/240  ({base_p * 100:.1f}%)".replace(".", ",")
            it_base = QTableWidgetItem(base_txt)
            it_base.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tbl_probs.setItem(row, 1, it_base)

            if act_p <= 0.0:
                act_txt = "0,0% (wykreślony)"
                it_act = QTableWidgetItem(act_txt)
                it_act.setForeground(muted_fg)
            elif abs(diff_p) > 1e-4:
                sign = "+" if diff_p > 0 else ""
                act_txt = f"{act_p * 100:.2f}% ({sign}{diff_p * 100:.2f}%)".replace(".", ",")
                it_act = QTableWidgetItem(act_txt)
                it_act.setFont(bold_font)
                it_act.setForeground(boost_fg)
            else:
                act_txt = f"{act_p * 100:.2f}%".replace(".", ",")
                it_act = QTableWidgetItem(act_txt)
                it_act.setFont(bold_font)
            it_act.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tbl_probs.setItem(row, 2, it_act)

            bar = self._prob_bars[row]
            bar.setValue(min(1000, int(round(act_p * 1000))))
            bar.setFormat(f"{act_p * 100:.1f}%".replace(".", ","))

            if n_sheet > 0:
                cnt = sheet_counts.get(top.id, 0)
                pts = sheet_pts.get(top.id, 0)
                sh_txt = f"{cnt} zad. ({cnt / n_sheet * 100:.0f}%, {pts} pkt)"
            else:
                sh_txt = "—"
            it_sh = QTableWidgetItem(sh_txt)
            it_sh.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tbl_probs.setItem(row, 4, it_sh)

            if self._tbl_probs.item(row, 5) is None:
                it_mc = QTableWidgetItem("kliknij „Przetestuj”")
                it_mc.setForeground(hint_fg)
                it_mc.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._tbl_probs.setItem(row, 5, it_mc)

        self._tbl_probs.resizeRowsToContents()

    def _run_monte_carlo_test(self) -> None:
        """Symuluje 1 000 arkuszy metodą Madowa dla bieżących prawdopodobieństw i wyświetla zbieżność."""
        n_sheets = 1000
        n_tasks = max(1, self._tasks_per_sheet_hint)
        rng = random.Random()
        totals = {t.id: 0 for t in TOPICS}
        for _ in range(n_sheets):
            q = sample_topic_quotas_stratified(rng, n_tasks, self._active_probs)
            for tid, cnt in q.items():
                totals[tid] += cnt

        ok_fg = QColor("#4ADE80") if self._is_dark else QColor("#166534")
        norm_fg = QColor("#E2E8F0") if self._is_dark else QColor("#1E293B")
        grand_total = n_sheets * n_tasks
        for row, top in enumerate(TOPICS):
            sim_pct = (totals[top.id] / grand_total) * 100.0
            tgt_pct = self._active_probs.get(top.id, 0.0) * 100.0
            err = abs(sim_pct - tgt_pct)
            txt = f"{sim_pct:.2f}% (błąd {err:.2f}%)".replace(".", ",")
            it = QTableWidgetItem(txt)
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it.setForeground(ok_fg if err < 0.25 else norm_fg)
            self._tbl_probs.setItem(row, 5, it)

    def _populate_session_table(self) -> None:
        sess_id = self._combo_session.currentData()
        sess = SESSION_BY_ID.get(sess_id)
        if not sess:
            return

        self._lbl_session_meta.setText(
            f"Data egzaminu: <b>{sess.date_str}</b> · Formuła CKE: <b>{sess.formula_years}</b> · "
            f"Zadania zamknięte: <b>{sess.closed_count}</b> · Zadania otwarte: <b>{sess.open_count}</b> · "
            f"Suma punktów: <b>{sess.total_points}</b>"
        )

        self._tbl_session.setRowCount(len(sess.tasks))
        for r, ht in enumerate(sess.tasks):
            it_num = QTableWidgetItem(f"{ht.number}.")
            it_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tbl_session.setItem(r, 0, it_num)

            it_pts = QTableWidgetItem(f"0–{ht.points}")
            it_pts.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tbl_session.setItem(r, 1, it_pts)

            sub_short = {
                "abcd": "A/B/C/D",
                "pf": "P / F",
                "ab_cd": "A/B i C/D",
                "uzasadnienie": "A/B + 1/2/3",
                "otwarte_2pkt": "Otwarte (2 pkt)",
                "otwarte_3pkt": "Otwarte (3 pkt)",
                "otwarte_4pkt": "Otwarte (4 pkt)",
            }.get(ht.subtype, SUBTYPE_LABELS.get(ht.subtype, ht.subtype))
            it_sub = QTableWidgetItem(sub_short)
            it_sub.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tbl_session.setItem(r, 2, it_sub)

            t_info = TOPIC_BY_ID.get(ht.topic_id)
            it_top = QTableWidgetItem(t_info.short_name if t_info else ht.topic_id)
            self._tbl_session.setItem(r, 3, it_top)

            self._tbl_session.setItem(r, 4, QTableWidgetItem(ht.label))

        self._tbl_session.resizeRowsToContents()

    def _on_mirror_clicked(self) -> None:
        sess_id = self._combo_session.currentData()
        if sess_id:
            self.mirror_session_requested.emit(str(sess_id))
