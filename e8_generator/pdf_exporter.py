"""Eksporter arkuszy egzaminacyjnych oraz kluczy odpowiedzi do formatu PDF w stylu CKE."""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Flowable,
    Image as RLImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .diagrams import render_diagram
from .math_text import pl_plural, to_rl_markup
from .models import ExamSheet, SUBTYPE_LABELS, Task

_FONTS_REGISTERED = False


def ensure_fonts() -> None:
    """Rejestruje czcionki DejaVu Sans (z pełnym wsparciem polskich znaków i symboli matematycznych)."""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    ttf_dir = Path(matplotlib.__file__).resolve().parent / "mpl-data" / "fonts" / "ttf"
    pdfmetrics.registerFont(TTFont("DejaVu", str(ttf_dir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(ttf_dir / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Italic", str(ttf_dir / "DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-BoldItalic", str(ttf_dir / "DejaVuSans-BoldOblique.ttf")))
    pdfmetrics.registerFontFamily(
        "DejaVu",
        normal="DejaVu",
        bold="DejaVu-Bold",
        italic="DejaVu-Italic",
        boldItalic="DejaVu-BoldItalic",
    )
    _FONTS_REGISTERED = True


# Kolory w stylu arkuszy CKE
C_BLACK = colors.HexColor("#111827")
C_DARK = colors.HexColor("#1E293B")
C_MUTED = colors.HexColor("#475569")
C_BORDER = colors.HexColor("#334155")
C_LIGHT_BG = colors.HexColor("#F1F5F9")
C_HEADER_BG = colors.HexColor("#E2E8F0")
C_GRID_LINE = colors.HexColor("#CBD5E1")
C_ACCENT = colors.HexColor("#1E3A8A")


class SquaredGridFlowable(Flowable):
    """Kratka 5 mm × 5 mm do obliczeń w zadaniach otwartych (dokładnie jak w arkuszach CKE)."""

    def __init__(self, width_pt: float, height_mm: float = 52.0, include_answer_box: bool = True):
        super().__init__()
        self.grid_step = 5.0 * mm
        cols = int(width_pt // self.grid_step)
        self.w = cols * self.grid_step
        rows = max(6, int(round((height_mm * mm) / self.grid_step)))
        self.grid_h = rows * self.grid_step
        self.include_answer_box = include_answer_box
        self.ans_h = 9.0 * mm if include_answer_box else 0.0
        self.gap_h = 2.5 * mm if include_answer_box else 0.0
        self.width = width_pt
        self.height = self.grid_h + self.gap_h + self.ans_h

    def draw(self):
        c = self.canv
        c.saveState()
        y_grid_bottom = self.ans_h + self.gap_h

        # Linie wewnętrzne kratki 5x5 mm
        c.setStrokeColor(C_GRID_LINE)
        c.setLineWidth(0.35)
        nx = int(round(self.w / self.grid_step))
        ny = int(round(self.grid_h / self.grid_step))
        for i in range(1, nx):
            x = i * self.grid_step
            c.line(x, y_grid_bottom, x, y_grid_bottom + self.grid_h)
        for j in range(1, ny):
            y = y_grid_bottom + j * self.grid_step
            c.line(0, y, self.w, y)

        # Ramka zewnętrzna kratki
        c.setStrokeColor(C_BORDER)
        c.setLineWidth(0.7)
        c.rect(0, y_grid_bottom, self.w, self.grid_h, stroke=1, fill=0)

        # Dolna ramka "Odpowiedź:"
        if self.include_answer_box:
            c.setFillColor(C_LIGHT_BG)
            c.setStrokeColor(C_BORDER)
            c.setLineWidth(0.75)
            c.rect(0, 0, self.w, self.ans_h, stroke=1, fill=1)
            c.setFillColor(C_BLACK)
            c.setFont("DejaVu-Bold", 9.5)
            c.drawString(3.5 * mm, 2.8 * mm, "Odpowiedź:")
            c.setStrokeColor(C_MUTED)
            c.setLineWidth(0.5)
            c.setDash(1.5, 1.5)
            c.line(29 * mm, 2.4 * mm, self.w - 4 * mm, 2.4 * mm)

        c.restoreState()


class NumberedCKECanvas(canvas.Canvas):
    """Canvas z dwuprzebiegową numeracją stron 'Strona X z Y' oraz nagłówkiem i stopką CKE."""

    def __init__(self, *args, header_left: str = "", header_right: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self._header_left = header_left
        self._header_right = header_right

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_chrome(total_pages)
            super().showPage()
        super().save()

    def _draw_page_chrome(self, total_pages: int):
        page_w, page_h = A4
        margin_x = 16 * mm
        self.saveState()

        # Nagłówek
        self.setStrokeColor(C_GRID_LINE)
        self.setLineWidth(0.5)
        self.line(margin_x, page_h - 12.5 * mm, page_w - margin_x, page_h - 12.5 * mm)
        self.setFont("DejaVu", 7.8)
        self.setFillColor(C_MUTED)
        self.drawString(margin_x, page_h - 10.5 * mm, self._header_left)
        self.drawRightString(page_w - margin_x, page_h - 10.5 * mm, self._header_right)

        # Stopka "Strona X z Y"
        self.line(margin_x, 12.5 * mm, page_w - margin_x, 12.5 * mm)
        self.setFont("DejaVu", 7.8)
        self.setFillColor(C_MUTED)
        self.drawString(margin_x, 8.2 * mm, "Generator Zadań E8 – Matematyka (układ w stylu CKE)")
        self.setFont("DejaVu-Bold", 8.5)
        self.setFillColor(C_BLACK)
        self.drawRightString(page_w - margin_x, 8.2 * mm, f"Strona {self._pageNumber} z {total_pages}")

        self.restoreState()


def _make_paragraph(text: str, base_style: ParagraphStyle) -> Paragraph:
    markup, max_math_h = to_rl_markup(text, font_size=base_style.fontSize)
    if max_math_h > base_style.leading * 0.85:
        adj_leading = max(base_style.leading, max_math_h + 6.0)
        style = ParagraphStyle(
            name=f"{base_style.name}_math",
            parent=base_style,
            leading=adj_leading,
        )
        return Paragraph(markup, style)
    return Paragraph(markup, base_style)


def _get_styles() -> dict[str, ParagraphStyle]:
    return {
        "body": ParagraphStyle(
            "body",
            fontName="DejaVu",
            fontSize=10.0,
            leading=14.8,
            textColor=C_BLACK,
            spaceAfter=4,
        ),
        "command": ParagraphStyle(
            "command",
            fontName="DejaVu-Bold",
            fontSize=10.0,
            leading=14.5,
            textColor=C_BLACK,
            spaceBefore=3,
            spaceAfter=5,
        ),
        "task_hdr": ParagraphStyle(
            "task_hdr",
            fontName="DejaVu-Bold",
            fontSize=10.5,
            leading=13.5,
            textColor=C_BLACK,
        ),
        "task_meta": ParagraphStyle(
            "task_meta",
            fontName="DejaVu",
            fontSize=8.2,
            leading=11.0,
            textColor=C_MUTED,
            alignment=TA_RIGHT,
        ),
        "choice": ParagraphStyle(
            "choice",
            fontName="DejaVu",
            fontSize=9.8,
            leading=14.2,
            textColor=C_BLACK,
        ),
        "center": ParagraphStyle(
            "center",
            fontName="DejaVu",
            fontSize=9.5,
            leading=13.5,
            alignment=TA_CENTER,
            textColor=C_BLACK,
        ),
        "center_bold": ParagraphStyle(
            "center_bold",
            fontName="DejaVu-Bold",
            fontSize=9.5,
            leading=13.5,
            alignment=TA_CENTER,
            textColor=C_BLACK,
        ),
        "title_big": ParagraphStyle(
            "title_big",
            fontName="DejaVu-Bold",
            fontSize=17.0,
            leading=22.0,
            alignment=TA_CENTER,
            textColor=C_BLACK,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="DejaVu",
            fontSize=11.0,
            leading=15.0,
            alignment=TA_CENTER,
            textColor=C_DARK,
        ),
        "small": ParagraphStyle(
            "small",
            fontName="DejaVu",
            fontSize=8.8,
            leading=13.0,
            textColor=C_DARK,
        ),
        "step": ParagraphStyle(
            "step",
            fontName="DejaVu",
            fontSize=9.5,
            leading=14.4,
            textColor=C_BLACK,
            leftIndent=6,
            spaceAfter=2.5,
        ),
        "rubric": ParagraphStyle(
            "rubric",
            fontName="DejaVu",
            fontSize=8.8,
            leading=13.0,
            textColor=C_DARK,
            leftIndent=8,
            spaceAfter=1.5,
        ),
    }


def _build_cover_flowables(sheet: ExamSheet, content_w: float, styles: dict) -> List[Flowable]:
    cfg = sheet.config
    flows: List[Flowable] = []

    # Górny pasek: KOD UCZNIA (3 kratki) + PESEL (11 kratek) + Miejsce na naklejkę
    code_cells = [["" for _ in range(3)]]
    code_tbl = Table(code_cells, colWidths=[6.5 * mm] * 3, rowHeights=[7.5 * mm])
    code_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.9, C_BLACK),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
    ]))

    pesel_cells = [["" for _ in range(11)]]
    pesel_tbl = Table(pesel_cells, colWidths=[6.2 * mm] * 11, rowHeights=[7.5 * mm])
    pesel_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.9, C_BLACK),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
    ]))

    sticker_box = Table(
        [[Paragraph("<i>Miejsce na naklejkę<br/>lub pieczątkę szkoły</i>", ParagraphStyle("st", parent=styles["center"], fontSize=8, textColor=C_MUTED))]],
        colWidths=[48 * mm],
        rowHeights=[16 * mm],
    )
    sticker_box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, C_MUTED),
        ("LINEABOVE", (0, 0), (-1, -1), 0.7, C_MUTED),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT_BG),
    ]))

    lbl_style = ParagraphStyle("lbl_sm", fontName="DejaVu-Bold", fontSize=7.8, leading=10, textColor=C_DARK)
    left_student = Table(
        [
            [Paragraph("KOD UCZNIA", lbl_style), Paragraph("PESEL", lbl_style)],
            [code_tbl, pesel_tbl],
        ],
        colWidths=[25 * mm, 74 * mm],
    )
    left_student.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    top_row = Table([[left_student, sticker_box]], colWidths=[content_w - 50 * mm, 50 * mm])
    top_row.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flows.append(top_row)
    flows.append(Spacer(1, 10 * mm))

    # Tytuł główny arkusza
    title_box_content = [
        [Paragraph(cfg.title.upper(), styles["title_big"])],
        [Paragraph(cfg.subtitle, styles["subtitle"])],
    ]
    if cfg.school_or_group.strip():
        title_box_content.append([Paragraph(f"<b>{cfg.school_or_group.strip()}</b>", styles["center"])])

    title_tbl = Table(title_box_content, colWidths=[content_w])
    title_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.2, C_BLACK),
        ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT_BG),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (0, -1), (0, -1), 10),
    ]))
    flows.append(title_tbl)
    flows.append(Spacer(1, 7 * mm))

    # Metryczka: Data, Czas pracy, Punkty, Wersja
    n_closed = len(sheet.closed_tasks)
    n_open = len(sheet.open_tasks)
    pts_word = pl_plural(sheet.total_points, "punkt", "punkty", "punktów")
    date_txt = cfg.exam_date_str.strip() or "........................................"

    meta_rows = [
        [Paragraph(f"<b>DATA:</b> {date_txt}", styles["body"]),
         Paragraph(f"<b>OZNACZENIE ZESTAWU:</b> {cfg.variant_code} (#{sheet.used_seed})", styles["body"])],
        [Paragraph(f"<b>CZAS PRACY:</b> {cfg.duration_minutes} minut", styles["body"]),
         Paragraph(f"<b>LICZBA PUNKTÓW DO UZYSKANIA:</b> {sheet.total_points} ({pts_word})", styles["body"])],
        [Paragraph(f"<b>LICZBA ZADAŃ:</b> {len(sheet.tasks)} (zamkniętych: {n_closed}, otwartych: {n_open})", styles["body"]),
         Paragraph("<b>IMIĘ I NAZWISKO:</b> ...............................................", styles["body"])],
    ]
    meta_tbl = Table(meta_rows, colWidths=[content_w * 0.48, content_w * 0.52])
    meta_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    flows.append(meta_tbl)
    flows.append(Spacer(1, 8 * mm))

    # Instrukcja dla zdającego (dokładnie w stylu CKE)
    flows.append(Paragraph("<b>Instrukcja dla zdającego</b>", ParagraphStyle("inst_h", parent=styles["body"], fontSize=11.5)))
    flows.append(Spacer(1, 2 * mm))

    instructions = [
        f"1. Sprawdź, czy ten arkusz egzaminacyjny zawiera <b>{len(sheet.tasks)} zadań</b> "
        f"(zadania zamknięte: 1–{n_closed if n_closed else '–'}, zadania otwarte: "
        f"{(n_closed + 1) if n_open else '–'}–{len(sheet.tasks) if n_open else '–'}). "
        "Ewentualny brak stron lub zadań zgłoś nauczycielowi.",
        "2. Rozwiązania zadań i odpowiedzi zapisuj w miejscu na to przeznaczonym przy każdym zadaniu.",
        "3. W zadaniach zamkniętych wybierz właściwą odpowiedź spośród podanych (zakreśl odpowiednią literę lub kratkę w tabeli).",
        "4. W rozwiązaniach <b>zadań otwartych</b> zapisz wszystkie wykonywane obliczenia, ponieważ w kryteriach CKE oceniany jest również tok rozumowania i sposób rozwiązania.",
        "5. Pisz czytelnie. Używaj długopisu lub pióra z czarnym tuszem/atramentem. Nie używaj korektora, a błędne zapisy wyraźnie przekreśl.",
        "6. Pamiętaj, że na egzaminie ósmoklasisty z matematyki <b>nie można korzystać z kalkulatora</b>.",
    ]
    for line in instructions:
        flows.append(Paragraph(line, ParagraphStyle("inst_p", parent=styles["body"], fontSize=9.4, leading=14.0, spaceAfter=3.5)))

    flows.append(Spacer(1, 10 * mm))
    flows.append(Paragraph("<i>Powodzenia!</i>", ParagraphStyle("pow", parent=styles["center_bold"], fontSize=11)))
    flows.append(PageBreak())
    return flows


def _build_compact_header(sheet: ExamSheet, content_w: float, styles: dict) -> List[Flowable]:
    """Kompaktowy nagłówek na górze pierwszej strony, gdy strona tytułowa CKE jest wyłączona."""
    cfg = sheet.config
    left_txt = f"<b>{cfg.title}</b><br/><font size='9' color='#475569'>{cfg.subtitle}"
    if cfg.school_or_group.strip():
        left_txt += f" · {cfg.school_or_group.strip()}"
    left_txt += "</font>"

    right_txt = (
        f"<b>{cfg.variant_code}</b> (#{sheet.used_seed})<br/>"
        f"<font size='8.5'>Zadań: {len(sheet.tasks)} · Suma pkt: <b>{sheet.total_points}</b> · Czas: {cfg.duration_minutes} min</font>"
    )
    hdr_tbl = Table(
        [[Paragraph(left_txt, styles["body"]), Paragraph(right_txt, ParagraphStyle("r", parent=styles["body"], alignment=TA_RIGHT))]],
        colWidths=[content_w * 0.62, content_w * 0.38],
    )
    hdr_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.9, C_BLACK),
        ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    name_row = Table(
        [[Paragraph("<b>Imię i nazwisko / Kod ucznia:</b> ..........................................................................", styles["small"]),
          Paragraph(f"<b>Data:</b> {cfg.exam_date_str.strip() or '........................'}", ParagraphStyle("rd", parent=styles["small"], alignment=TA_RIGHT))]],
        colWidths=[content_w * 0.68, content_w * 0.32],
    )
    name_row.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [hdr_tbl, name_row, Spacer(1, 3 * mm)]


def _build_task_flowables(task: Task, content_w: float, styles: dict, include_open_grid: bool) -> List[Flowable]:
    """Buduje blok pojedynczego zadania egzaminacyjnego w układzie CKE."""
    items: List[Flowable] = []

    # Pasek nagłówka zadania: "Zadanie X. (0–1)" lub "Zadanie X. (0–2)" / "(0–3)"
    hdr_text = f"Zadanie {task.number}. (0–{task.points})"
    hdr_tbl = Table([[Paragraph(hdr_text, styles["task_hdr"])]], colWidths=[content_w])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_HEADER_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3.0, C_BLACK),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ]))
    items.append(hdr_tbl)
    items.append(Spacer(1, 2.2 * mm))

    # Treść zadania (stem)
    items.append(_make_paragraph(task.stem, styles["body"]))

    # Opcjonalna tabela danych
    if task.table_data:
        items.append(Spacer(1, 1.5 * mm))
        ncols = len(task.table_data[0])
        col_w = min(content_w / ncols, 42 * mm)
        if ncols == 2:
            col_widths = [58 * mm, 32 * mm]
        else:
            first_w = min(56 * mm, content_w * 0.36)
            rem_w = min((content_w - first_w) / (ncols - 1), 26 * mm)
            col_widths = [first_w] + [rem_w] * (ncols - 1)

        t_rows = []
        for r_idx, row in enumerate(task.table_data):
            st = styles["center_bold"] if r_idx == 0 else styles["center"]
            t_rows.append([_make_paragraph(cell, st) for cell in row])

        data_tbl = Table(t_rows, colWidths=col_widths, hAlign="CENTER")
        data_tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.65, C_BLACK),
            ("BACKGROUND", (0, 0), (-1, 0), C_LIGHT_BG),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        items.append(data_tbl)
        items.append(Spacer(1, 2.0 * mm))

    # Opcjonalny rysunek pomocniczy
    if task.diagram is not None:
        img_path, w_px, h_px = render_diagram(task.diagram)
        target_w = min(task.diagram.width_mm * mm, content_w * 0.85)
        target_h = target_w * (h_px / max(1, w_px))
        # Ogranicz wysokość rysunku, aby zmieścił się estetycznie
        max_h = 56 * mm
        if target_h > max_h:
            scale = max_h / target_h
            target_w *= scale
            target_h = max_h
        img_flow = RLImage(img_path, width=target_w, height=target_h)
        img_flow.hAlign = "CENTER"
        items.append(Spacer(1, 1.2 * mm))
        items.append(img_flow)
        items.append(Spacer(1, 1.5 * mm))

    # Polecenie pogrubione
    items.append(_make_paragraph(task.command, styles["command"]))

    # Sekcja odpowiedzi zależna od typu zadania
    if task.subtype == "abcd":
        letters = ["A", "B", "C", "D"]
        raw_lens = [len(task.choices.get(L, "")) for L in letters]
        max_len = max(raw_lens) if raw_lens else 0

        if max_len <= 26:
            # 4 kolumny w jednym wierszu
            row = [_make_paragraph(f"**{L}.** {task.choices[L]}", styles["choice"]) for L in letters]
            ans_tbl = Table([row], colWidths=[content_w / 4.0] * 4)
        elif max_len <= 52:
            # Układ 2x2
            r1 = [
                _make_paragraph(f"**A.** {task.choices['A']}", styles["choice"]),
                _make_paragraph(f"**B.** {task.choices['B']}", styles["choice"]),
            ]
            r2 = [
                _make_paragraph(f"**C.** {task.choices['C']}", styles["choice"]),
                _make_paragraph(f"**D.** {task.choices['D']}", styles["choice"]),
            ]
            ans_tbl = Table([r1, r2], colWidths=[content_w / 2.0] * 2)
        else:
            # 4 pełne wiersze dla dłuższych zdań
            rows = [[_make_paragraph(f"**{L}.** {task.choices[L]}", styles["choice"])] for L in letters]
            ans_tbl = Table(rows, colWidths=[content_w])

        ans_tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        items.append(ans_tbl)

    elif task.subtype == "pf":
        pf_rows = []
        for stmt, _ in task.pf_statements:
            pf_rows.append([
                _make_paragraph(stmt, styles["choice"]),
                Paragraph("<b>P</b>", styles["center_bold"]),
                Paragraph("<b>F</b>", styles["center_bold"]),
            ])
        pf_w_box = 11 * mm
        pf_tbl = Table(pf_rows, colWidths=[content_w - 2 * pf_w_box, pf_w_box, pf_w_box])
        pf_tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.7, C_BLACK),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, -1), 6),
            ("RIGHTPADDING", (0, 0), (0, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        items.append(pf_tbl)

    elif task.subtype == "ab_cd":
        for idx, part in enumerate(task.ab_cd_parts):
            keys = sorted(part["options"].keys())  # ["A", "B"] albo ["C", "D"]
            box_tag = f"**[{keys[0]} / {keys[1]}]**"
            sent = f"{part['prefix']} {box_tag}{part.get('suffix', '.')}"
            items.append(_make_paragraph(sent, styles["body"]))
            opt_row = [
                _make_paragraph(f"**{keys[0]}.** {part['options'][keys[0]]}", styles["choice"]),
                _make_paragraph(f"**{keys[1]}.** {part['options'][keys[1]]}", styles["choice"]),
            ]
            opt_tbl = Table([opt_row], colWidths=[content_w * 0.45, content_w * 0.45], hAlign="LEFT")
            opt_tbl.setStyle(TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            items.append(opt_tbl)

    elif task.subtype == "uzasadnienie":
        jd = task.justification_data
        ab_dict = jd.get("choices_ab", {"A": "Tak,", "B": "Nie,"})
        conn = jd.get("connector", "ponieważ")
        reasons = jd.get("reasons", {})

        # Klasyczna tabela CKE: lewa kolumna A/B, środkowa "ponieważ", prawa 1/2/3
        left_sub = Table(
            [
                [_make_paragraph(f"**A.** {ab_dict['A']}", styles["choice"])],
                [_make_paragraph(f"**B.** {ab_dict['B']}", styles["choice"])],
            ],
            colWidths=[27 * mm],
        )
        left_sub.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.65, C_BLACK),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))

        right_w = content_w - 29 * mm - 22 * mm
        right_rows = [
            [_make_paragraph(f"**{k}.** {reasons[k]}", styles["choice"])]
            for k in sorted(reasons.keys())
        ]
        right_sub = Table(right_rows, colWidths=[right_w])
        right_sub.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.65, C_BLACK),
            ("TOPPADDING", (0, 0), (-1, -1), 4.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

        uz_tbl = Table(
            [[left_sub, Paragraph(f"<i>{conn}</i>", styles["center"]), right_sub]],
            colWidths=[29 * mm, 22 * mm, right_w],
        )
        uz_tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        items.append(uz_tbl)

    elif task.is_open:
        if include_open_grid:
            items.append(Spacer(1, 1.5 * mm))
            items.append(SquaredGridFlowable(content_w, height_mm=task.grid_height_mm, include_answer_box=True))
        else:
            items.append(Spacer(1, 3 * mm))

    items.append(Spacer(1, 5.5 * mm))
    return [KeepTogether(items)]


def build_exam_pdf_bytes(sheet: ExamSheet) -> bytes:
    """Generuje plik PDF arkusza egzaminacyjnego dla ucznia i zwraca zawartość jako `bytes`."""
    ensure_fonts()
    styles = _get_styles()
    buf = io.BytesIO()

    margin_x = 16 * mm
    margin_y = 17 * mm
    content_w = A4[0] - 2 * margin_x

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=margin_y,
        bottomMargin=margin_y,
        title=f"{sheet.config.title} – {sheet.config.variant_code}",
    )

    story: List[Flowable] = []
    if sheet.config.include_cover_page:
        story.extend(_build_cover_flowables(sheet, content_w, styles))
    else:
        story.extend(_build_compact_header(sheet, content_w, styles))

    for task in sheet.tasks:
        story.extend(
            _build_task_flowables(
                task,
                content_w=content_w,
                styles=styles,
                include_open_grid=sheet.config.include_answer_grid_for_open,
            )
        )

    if sheet.config.include_scratchpad_page:
        story.append(PageBreak())
        story.append(Paragraph("<b>BRUDNOPIS</b> (zapisy w brudnopisie nie podlegają ocenie)", styles["center_bold"]))
        story.append(Spacer(1, 4 * mm))
        story.append(SquaredGridFlowable(content_w, height_mm=225.0, include_answer_box=False))

    header_left = f"{sheet.config.title} – ARKUSZ ZADAŃ"
    header_right = f"{sheet.config.variant_code} · Zestaw #{sheet.used_seed}"

    doc.build(
        story,
        canvasmaker=lambda *a, **kw: NumberedCKECanvas(*a, header_left=header_left, header_right=header_right, **kw),
    )
    return buf.getvalue()


def build_key_pdf_bytes(sheet: ExamSheet) -> bytes:
    """Generuje osobny plik PDF z kluczem odpowiedzi, rozwiązaniami krok po kroku i schematem punktowania CKE."""
    ensure_fonts()
    styles = _get_styles()
    buf = io.BytesIO()

    margin_x = 16 * mm
    margin_y = 17 * mm
    content_w = A4[0] - 2 * margin_x

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=margin_y,
        bottomMargin=margin_y,
        title=f"Klucz odpowiedzi i rozwiązania – {sheet.config.variant_code}",
    )

    story: List[Flowable] = []

    # Nagłówek klucza
    hdr_block = Table(
        [
            [Paragraph("KLUCZ ODPOWIEDZI I ZASADY OCENIANIA ROZWIĄZAŃ", styles["title_big"])],
            [Paragraph(
                f"{sheet.config.title} · <b>{sheet.config.variant_code}</b> (Zestaw #{sheet.used_seed}) · "
                f"Suma punktów: <b>{sheet.total_points}</b>",
                styles["center"],
            )],
        ],
        colWidths=[content_w],
    )
    hdr_block.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.0, C_BLACK),
        ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT_BG),
        ("TOPPADDING", (0, 0), (0, 0), 8),
        ("BOTTOMPADDING", (0, -1), (0, -1), 8),
    ]))
    story.append(hdr_block)
    story.append(Spacer(1, 5 * mm))

    # Szybka tabela odpowiedzi dla zadań zamkniętych
    closed = sheet.closed_tasks
    if closed:
        story.append(Paragraph("<b>1. Szybki klucz odpowiedzi do zadań zamkniętych (po 1 pkt)</b>", styles["command"]))
        per_row = min(8, len(closed))
        col_w = content_w / per_row
        for chunk_start in range(0, len(closed), per_row):
            chunk = closed[chunk_start:chunk_start + per_row]
            r_num = [Paragraph(f"<b>Zad. {t.number}</b>", styles["center_bold"]) for t in chunk]
            r_ans = [Paragraph(f"<b>{t.correct_answer}</b>", styles["center_bold"]) for t in chunk]
            while len(r_num) < per_row:
                r_num.append(Paragraph("", styles["center"]))
                r_ans.append(Paragraph("", styles["center"]))
            quick_tbl = Table([r_num, r_ans], colWidths=[col_w] * per_row)
            quick_tbl.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.65, C_BLACK),
                ("BACKGROUND", (0, 0), (-1, 0), C_HEADER_BG),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(quick_tbl)
            story.append(Spacer(1, 2.5 * mm))
        story.append(Spacer(1, 3 * mm))

    # Szczegółowe rozwiązania wszystkich zadań
    story.append(Paragraph("<b>2. Pełne rozwiązania krok po kroku oraz kryteria punktowania</b>", styles["command"]))
    story.append(Spacer(1, 2 * mm))

    for task in sheet.tasks:
        block: List[Flowable] = []
        meta_bits = [task.topic_name, SUBTYPE_LABELS.get(task.subtype, task.subtype)]
        if sheet.config.include_cke_ref_in_key and task.cke_ref:
            meta_bits.append(task.cke_ref)
        meta_str = " · ".join(meta_bits)

        t_hdr = Table(
            [[
                _make_paragraph(f"Zadanie {task.number}. (0–{task.points})  —  Odpowiedź: **{task.correct_answer}**", styles["task_hdr"]),
                Paragraph(meta_str, styles["task_meta"]),
            ]],
            colWidths=[content_w * 0.56, content_w * 0.44],
        )
        t_hdr.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_HEADER_BG),
            ("LINEBEFORE", (0, 0), (0, -1), 2.8, C_ACCENT),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (0, -1), 6),
            ("RIGHTPADDING", (-1, 0), (-1, -1), 5),
        ]))
        block.append(t_hdr)
        block.append(Spacer(1, 1.5 * mm))

        for idx_s, step_txt in enumerate(task.solution_steps, start=1):
            block.append(_make_paragraph(f"• {step_txt}", styles["step"]))

        if task.scoring_scheme:
            block.append(Spacer(1, 1 * mm))
            block.append(Paragraph("<b>Schemat punktowania CKE:</b>", styles["rubric"]))
            for sc in task.scoring_scheme:
                block.append(_make_paragraph(f"– {sc}", styles["rubric"]))

        block.append(Spacer(1, 4.0 * mm))
        story.append(KeepTogether(block))

    header_left = f"KLUCZ ODPOWIEDZI I ROZWIĄZANIA – {sheet.config.title}"
    header_right = f"{sheet.config.variant_code} · Zestaw #{sheet.used_seed}"

    doc.build(
        story,
        canvasmaker=lambda *a, **kw: NumberedCKECanvas(*a, header_left=header_left, header_right=header_right, **kw),
    )
    return buf.getvalue()
