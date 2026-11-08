"""Widżet listy kart zadań z podglądem rozwiązania, wymianą pojedynczego zadania oraz pełnym wsparciem ciemnego motywu."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..diagrams import render_diagram
from ..math_text import to_qt_html
from ..models import SUBTYPE_LABELS, ExamSheet, Task


class TaskCardWidget(QFrame):
    """Pojedyncza karta zadania z przyciskiem wymiany i rozwijanym rozwiązaniem."""

    replace_requested = pyqtSignal(int)

    def __init__(self, task_index: int, task: Task, is_dark: bool = False, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("TaskCard")
        self._task_index = task_index
        self._solution_visible = False

        if is_dark:
            badge_col = "#93C5FD" if not task.is_open else "#5EEAD4"
            meta_col = "#94A3B8"
            body_col = "#F1F5F9"
            opt_col = "#E2E8F0"
            sol_bg = "#132A1E"
            sol_border = "#22543D"
            sol_fg = "#BBF7D0"
            sol_math = "#BBF7D0"
        else:
            badge_col = "#1E3A8A" if not task.is_open else "#0F766E"
            meta_col = "#475569"
            body_col = "#0F172A"
            opt_col = "#1E293B"
            sol_bg = "#F0FDF4"
            sol_border = "#BBF7D0"
            sol_fg = "#14532D"
            sol_math = "#14532D"

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        # Górny pasek: numer, punkty, dział, styl CKE + przyciski akcji
        top = QHBoxLayout()
        top.setSpacing(8)
        hdr_lbl = QLabel(
            f"<span style='color:{badge_col}; font-weight:700; font-size:14px;'>"
            f"Zadanie {task.number}. (0–{task.points} pkt)</span>"
            f"&nbsp;&nbsp;<span style='color:{meta_col}; font-size:12px;'>"
            f"{task.topic_name} · {SUBTYPE_LABELS.get(task.subtype, task.subtype)} · <i>{task.cke_ref}</i></span>"
        )
        hdr_lbl.setWordWrap(True)
        hdr_lbl.setTextFormat(Qt.TextFormat.RichText)
        top.addWidget(hdr_lbl, 1)

        self._btn_toggle_sol = QPushButton("Pokaż odpowiedź")
        self._btn_toggle_sol.setObjectName("SmallGhostBtn")
        self._btn_toggle_sol.clicked.connect(self._toggle_solution)
        top.addWidget(self._btn_toggle_sol, 0, Qt.AlignmentFlag.AlignTop)

        btn_replace = QPushButton("Wymień zadanie")
        btn_replace.setObjectName("SmallGhostBtn")
        btn_replace.setToolTip("Wylosuj nowe zadanie na to miejsce (z zachowaniem punktacji i wybranych działów)")
        btn_replace.clicked.connect(lambda: self.replace_requested.emit(self._task_index))
        top.addWidget(btn_replace, 0, Qt.AlignmentFlag.AlignTop)
        lay.addLayout(top)

        # Treść zadania + polecenie
        stem_html = (
            f"<div style='line-height:1.45; color:{body_col};'>{to_qt_html(task.stem, color=body_col)}</div>"
            f"<div style='margin-top:6px; font-weight:700; color:{body_col};'>{to_qt_html(task.command, color=body_col)}</div>"
        )
        stem_lbl = QLabel(stem_html)
        stem_lbl.setWordWrap(True)
        stem_lbl.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(stem_lbl)

        # Opcjonalny rysunek pomocniczy
        if task.diagram is not None:
            img_path, _, _ = render_diagram(task.diagram)
            pix = QPixmap(img_path)
            if not pix.isNull():
                max_w = 340
                if pix.width() > max_w:
                    pix = pix.scaledToWidth(max_w, Qt.TransformationMode.SmoothTransformation)
                diag_lbl = QLabel()
                diag_lbl.setPixmap(pix)
                diag_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
                if is_dark:
                    diag_lbl.setStyleSheet(
                        "background-color: #F8FAFC; border: 1px solid #475569; border-radius: 6px; padding: 6px;"
                    )
                    diag_lbl.setFixedWidth(pix.width() + 14)
                lay.addWidget(diag_lbl)

        # Podgląd opcji w zadaniach zamkniętych
        opts_html = self._format_closed_options_html(task, opt_col)
        if opts_html:
            opts_lbl = QLabel(opts_html)
            opts_lbl.setWordWrap(True)
            opts_lbl.setTextFormat(Qt.TextFormat.RichText)
            lay.addWidget(opts_lbl)

        # Ukryty blok odpowiedzi i rozwiązania
        sol_lines = [f"<b>Poprawna odpowiedź:</b> {to_qt_html(task.correct_answer, color=sol_math)}"]
        for s in task.solution_steps:
            sol_lines.append(f"• {to_qt_html(s, color=sol_math)}")
        self._sol_box = QLabel("<br/>".join(sol_lines))
        self._sol_box.setWordWrap(True)
        self._sol_box.setTextFormat(Qt.TextFormat.RichText)
        self._sol_box.setStyleSheet(
            f"background-color: {sol_bg}; border: 1px solid {sol_border}; border-radius: 6px; "
            f"padding: 8px 10px; color: {sol_fg};"
        )
        self._sol_box.setVisible(False)
        lay.addWidget(self._sol_box)

    def _format_closed_options_html(self, task: Task, opt_col: str) -> str:
        if task.subtype == "abcd":
            parts = [
                f"<b>{L}.</b> {to_qt_html(task.choices[L], color=opt_col)}"
                for L in ("A", "B", "C", "D")
                if L in task.choices
            ]
            return f"<div style='margin-top:2px; color:{opt_col};'>" + "&nbsp;&nbsp;&nbsp;&nbsp;".join(parts) + "</div>"
        if task.subtype == "pf":
            rows = [f"[P / F] {to_qt_html(st, color=opt_col)}" for st, _ in task.pf_statements]
            return f"<div style='margin-top:2px; color:{opt_col};'>" + "<br/>".join(rows) + "</div>"
        if task.subtype == "ab_cd":
            rows = []
            for p in task.ab_cd_parts:
                ks = sorted(p["options"].keys())
                opts = " / ".join(f"<b>{k}:</b> {to_qt_html(p['options'][k], color=opt_col)}" for k in ks)
                rows.append(
                    f"{to_qt_html(p['prefix'], color=opt_col)} [{opts}]{to_qt_html(p.get('suffix', '.'), color=opt_col)}"
                )
            return f"<div style='margin-top:2px; color:{opt_col};'>" + "<br/>".join(rows) + "</div>"
        if task.subtype == "uzasadnienie":
            jd = task.justification_data
            reasons = jd.get("reasons", {})
            r_str = "<br/>".join(
                f"&nbsp;&nbsp;<b>{k}.</b> {to_qt_html(reasons[k], color=opt_col)}" for k in sorted(reasons.keys())
            )
            return f"<div style='margin-top:2px; color:{opt_col};'><b>A.</b> Tak / <b>B.</b> Nie, <i>ponieważ</i>:<br/>{r_str}</div>"
        return ""

    def _toggle_solution(self) -> None:
        self._solution_visible = not self._solution_visible
        self._sol_box.setVisible(self._solution_visible)
        self._btn_toggle_sol.setText("Ukryj odpowiedź" if self._solution_visible else "Pokaż odpowiedź")


class TaskListWidget(QWidget):
    """Lista wszystkich wygenerowanych zadań z natychmiastową wymianą wybranych pozycji."""

    replace_task_requested = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._sheet: Optional[ExamSheet] = None
        self._is_dark: bool = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        info_bar = QFrame()
        info_bar.setObjectName("PreviewToolbar")
        ib_lay = QHBoxLayout(info_bar)
        ib_lay.setContentsMargins(14, 7, 14, 7)
        lbl = QLabel(
            "Tutaj możesz szybko przejrzeć wszystkie nowo wygenerowane zadania, podejrzeć odpowiedzi lub kliknąć "
            "<b>„Wymień zadanie”</b>, aby wylosować zupełnie inne zadanie na dane miejsce."
        )
        lbl.setObjectName("MutedLabel")
        lbl.setWordWrap(True)
        ib_lay.addWidget(lbl)
        root.addWidget(info_bar)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container = QWidget()
        self._container.setObjectName("CardsScrollBody")
        self._cards_lay = QVBoxLayout(self._container)
        self._cards_lay.setContentsMargins(14, 14, 14, 18)
        self._cards_lay.setSpacing(10)
        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll, 1)

    def set_dark_mode(self, is_dark: bool) -> None:
        if self._is_dark != is_dark:
            self._is_dark = is_dark
            if self._sheet is not None:
                self._rebuild_cards()

    def set_sheet(self, sheet: ExamSheet) -> None:
        self._sheet = sheet
        self._rebuild_cards()

    def _rebuild_cards(self) -> None:
        while self._cards_lay.count():
            item = self._cards_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.hide()
                w.setParent(None)
                w.deleteLater()

        if self._sheet is None:
            return
        for idx, task in enumerate(self._sheet.tasks):
            card = TaskCardWidget(idx, task, is_dark=self._is_dark)
            card.replace_requested.connect(self.replace_task_requested.emit)
            self._cards_lay.addWidget(card)
        self._cards_lay.addStretch(1)
