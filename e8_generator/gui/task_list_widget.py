"""Widżet listy kart zadań z możliwością podglądu rozwiązania i wymiany pojedynczego zadania."""

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

    def __init__(self, task_index: int, task: Task, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("TaskCard")
        self._task_index = task_index
        self._solution_visible = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        # Górny pasek: numer, punkty, dział, wzorzec CKE + przyciski akcji
        top = QHBoxLayout()
        top.setSpacing(8)
        badge_col = "#1E3A8A" if not task.is_open else "#0F766E"
        hdr_lbl = QLabel(
            f"<span style='color:{badge_col}; font-weight:700; font-size:14px;'>"
            f"Zadanie {task.number}. (0–{task.points} pkt)</span>"
            f"&nbsp;&nbsp;<span style='color:#475569; font-size:12px;'>"
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
        btn_replace.setToolTip("Wylosuj inne zadanie na to miejsce (z zachowaniem punktacji i wybranych działów)")
        btn_replace.clicked.connect(lambda: self.replace_requested.emit(self._task_index))
        top.addWidget(btn_replace, 0, Qt.AlignmentFlag.AlignTop)
        lay.addLayout(top)

        # Treść zadania + polecenie
        stem_html = (
            f"<div style='line-height:1.45; color:#0F172A;'>{to_qt_html(task.stem)}</div>"
            f"<div style='margin-top:6px; font-weight:700; color:#0F172A;'>{to_qt_html(task.command)}</div>"
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
                lay.addWidget(diag_lbl)

        # Podgląd opcji w zadaniach zamkniętych
        opts_html = self._format_closed_options_html(task)
        if opts_html:
            opts_lbl = QLabel(opts_html)
            opts_lbl.setWordWrap(True)
            opts_lbl.setTextFormat(Qt.TextFormat.RichText)
            lay.addWidget(opts_lbl)

        # Ukryty blok odpowiedzi i rozwiązania
        sol_lines = [f"<b>Poprawna odpowiedź:</b> {to_qt_html(task.correct_answer)}"]
        for s in task.solution_steps:
            sol_lines.append(f"• {to_qt_html(s)}")
        self._sol_box = QLabel("<br/>".join(sol_lines))
        self._sol_box.setWordWrap(True)
        self._sol_box.setTextFormat(Qt.TextFormat.RichText)
        self._sol_box.setStyleSheet(
            "background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 8px 10px; color: #14532D;"
        )
        self._sol_box.setVisible(False)
        lay.addWidget(self._sol_box)

    def _format_closed_options_html(self, task: Task) -> str:
        if task.subtype == "abcd":
            parts = [f"<b>{L}.</b> {to_qt_html(task.choices[L])}" for L in ("A", "B", "C", "D") if L in task.choices]
            return "<div style='margin-top:2px; color:#1E293B;'>" + "&nbsp;&nbsp;&nbsp;&nbsp;".join(parts) + "</div>"
        if task.subtype == "pf":
            rows = [f"[P / F] {to_qt_html(st)}" for st, _ in task.pf_statements]
            return "<div style='margin-top:2px; color:#1E293B;'>" + "<br/>".join(rows) + "</div>"
        if task.subtype == "ab_cd":
            rows = []
            for p in task.ab_cd_parts:
                ks = sorted(p["options"].keys())
                opts = " / ".join(f"<b>{k}:</b> {to_qt_html(p['options'][k])}" for k in ks)
                rows.append(f"{to_qt_html(p['prefix'])} [{opts}]{to_qt_html(p.get('suffix', '.'))}")
            return "<div style='margin-top:2px; color:#1E293B;'>" + "<br/>".join(rows) + "</div>"
        if task.subtype == "uzasadnienie":
            jd = task.justification_data
            reasons = jd.get("reasons", {})
            r_str = "<br/>".join(f"&nbsp;&nbsp;<b>{k}.</b> {to_qt_html(reasons[k])}" for k in sorted(reasons.keys()))
            return f"<div style='margin-top:2px; color:#1E293B;'><b>A.</b> Tak / <b>B.</b> Nie, <i>ponieważ</i>:<br/>{r_str}</div>"
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
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        info_bar = QFrame()
        info_bar.setObjectName("PreviewToolbar")
        ib_lay = QHBoxLayout(info_bar)
        ib_lay.setContentsMargins(14, 7, 14, 7)
        lbl = QLabel(
            "Tutaj możesz szybko przejrzeć poszczególne zadania, podejrzeć odpowiedzi lub kliknąć "
            "<b>„Wymień to zadanie”</b>, jeśli chcesz wylosować inne zadanie na dane miejsce."
        )
        lbl.setObjectName("MutedLabel")
        lbl.setWordWrap(True)
        ib_lay.addWidget(lbl)
        root.addWidget(info_bar)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container = QWidget()
        self._container.setStyleSheet("background-color: #F8FAFC;")
        self._cards_lay = QVBoxLayout(self._container)
        self._cards_lay.setContentsMargins(14, 14, 14, 18)
        self._cards_lay.setSpacing(10)
        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll, 1)

    def set_sheet(self, sheet: ExamSheet) -> None:
        while self._cards_lay.count():
            item = self._cards_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.hide()
                w.setParent(None)
                w.deleteLater()

        for idx, task in enumerate(sheet.tasks):
            card = TaskCardWidget(idx, task)
            card.replace_requested.connect(self.replace_task_requested.emit)
            self._cards_lay.addWidget(card)
        self._cards_lay.addStretch(1)
