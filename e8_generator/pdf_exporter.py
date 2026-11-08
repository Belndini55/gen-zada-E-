"""Eksporter arkuszy egzaminacyjnych oraz kluczy odpowiedzi do formatu PDF w autentycznej szacie CKE OMAP-100."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Dict, List

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
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

from .cke_archive import EMPIRICAL_STATS
from .diagrams import render_diagram
from .math_text import pl_plural, to_rl_markup
from .models import SUBTYPE_LABELS, TOPICS, ExamSheet, Task

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


# ---------------------------------------------------------------------------
# Autentyczna paleta barw arkuszy CKE E8 (OMAP-100 2025/2026)
# ---------------------------------------------------------------------------
C_BLACK = colors.HexColor("#0F172A")
C_PURE_BLACK = colors.HexColor("#000000")
C_DARK = colors.HexColor("#1E293B")
C_MUTED = colors.HexColor("#475569")

# Szałwiowo-oliwkowa zieleń pasków zadań "Zadanie X. (0–Y)" oraz paska "WYPEŁNIA UCZEŃ"
C_CKE_BAR = colors.HexColor("#C5D9A4")
C_CKE_BAR_LIGHT = colors.HexColor("#E8F0D8")
# Oliwkowe logo CKE w lewym górnym rogu okładki
C_CKE_LOGO_BG = colors.HexColor("#D8DF8E")
# Zielone logo "E8" w centralnej ramce okładki oraz akcenty instrukcji CKE
C_CKE_E8_GREEN = colors.HexColor("#7FA64E")
C_CKE_TEXT_GREEN = colors.HexColor("#537A26")
# Karmazynowa czerwień kodu arkusza "O-100" oraz "OMAP-100-..."
C_CKE_CRIMSON = colors.HexColor("#C00000")
# Łososiowo-ceglasta czerwień kratki skanera 5x5 mm i ostrzeżeń marginesowych w zadaniach otwartych
C_CKE_SALMON_GRID = colors.HexColor("#DA8A82")
C_CKE_SALMON_TICK = colors.HexColor("#CD7067")
C_CKE_SALMON_TEXT = colors.HexColor("#C0625A")

C_BORDER = colors.HexColor("#262626")
C_LIGHT_GRAY = colors.HexColor("#F4F6F8")


class CKEOpenScannerGridFlowable(Flowable):
    """Autentyczna kratka CKE 5 mm × 5 mm w kolorze łososiowo-czerwonym (#DA8A82)
    wewnątrz czarnej ramki skanera, ze znacznikami i pionowymi napisami ostrzegawczymi na marginesach."""

    def __init__(self, width_pt: float, height_mm: float = 52.0, include_answer_box: bool = True):
        super().__init__()
        self.grid_step = 5.0 * mm
        # Rezerwujemy po 4.5 mm z lewej i prawej na pionowe ostrzeżenia CKE poza ramką
        self.side_pad = 4.6 * mm
        usable_w = width_pt - 2 * self.side_pad
        cols = max(10, int(usable_w // self.grid_step))
        self.frame_w = cols * self.grid_step
        self.x0 = (width_pt - self.frame_w) / 2.0

        rows = max(6, int(round((height_mm * mm) / self.grid_step)))
        self.grid_h = rows * self.grid_step
        self.top_warn_h = 4.2 * mm
        self.include_answer_box = include_answer_box
        self.ans_h = 8.5 * mm if include_answer_box else 0.0
        self.gap_h = 2.2 * mm if include_answer_box else 0.0

        self.width = width_pt
        self.height = self.top_warn_h + self.grid_h + self.gap_h + self.ans_h

    def draw(self):
        c = self.canv
        c.saveState()
        y_grid_bottom = self.ans_h + self.gap_h
        y_grid_top = y_grid_bottom + self.grid_h
        x0 = self.x0
        x1 = x0 + self.frame_w

        # 1. Wewnętrzne linie kratki 5×5 mm w kolorze CKE salmon-red
        c.setStrokeColor(C_CKE_SALMON_GRID)
        c.setLineWidth(0.42)
        nx = int(round(self.frame_w / self.grid_step))
        ny = int(round(self.grid_h / self.grid_step))
        for i in range(1, nx):
            x = x0 + i * self.grid_step
            c.line(x, y_grid_bottom, x, y_grid_top)
        for j in range(1, ny):
            y = y_grid_bottom + j * self.grid_step
            c.line(x0, y, x1, y)

        # 2. Krótkie znaczniki pozycjonujące skanera CKE na zewnątrz narożników
        c.setStrokeColor(C_CKE_SALMON_TICK)
        c.setLineWidth(0.75)
        tk = 2.3 * mm
        # Górne i dolne znaczniki
        for cx in (x0, x1):
            c.line(cx, y_grid_top + 0.6 * mm, cx, y_grid_top + 0.6 * mm + tk)
            c.line(cx, y_grid_bottom - 0.6 * mm - tk, cx, y_grid_bottom - 0.6 * mm)

        # 3. Napisy ostrzegawcze CKE poza ramką (góra + lewy i prawy margines pionowo)
        warn_txt = "Zapisy na marginesie poza ramką nie będą oceniane."
        c.setFillColor(C_CKE_SALMON_TEXT)
        c.setFont("DejaVu-Italic", 6.5)
        c.drawCentredString(x0 + self.frame_w * 0.27, y_grid_top + 1.2 * mm, warn_txt)
        c.drawCentredString(x0 + self.frame_w * 0.73, y_grid_top + 1.2 * mm, warn_txt)

        if self.grid_h >= 38 * mm:
            # Lewy margines (obrót +90°)
            c.saveState()
            c.translate(x0 - 1.5 * mm, y_grid_bottom + self.grid_h / 2.0)
            c.rotate(90)
            c.drawCentredString(0, 0, warn_txt)
            c.restoreState()

            # Prawy margines (obrót -90°)
            c.saveState()
            c.translate(x1 + 1.5 * mm, y_grid_bottom + self.grid_h / 2.0)
            c.rotate(-90)
            c.drawCentredString(0, 0, warn_txt)
            c.restoreState()

        # 4. Wyrazista czarna ramka pola ocenianego (1.1 pt jak w druku CKE)
        c.setStrokeColor(C_PURE_BLACK)
        c.setLineWidth(1.1)
        c.rect(x0, y_grid_bottom, self.frame_w, self.grid_h, stroke=1, fill=0)

        # 5. Dolne okienko "Odpowiedź:" wewnątrz szerokości ramki
        if self.include_answer_box:
            c.setFillColor(colors.white)
            c.setStrokeColor(C_PURE_BLACK)
            c.setLineWidth(0.95)
            c.rect(x0, 0, self.frame_w, self.ans_h, stroke=1, fill=1)
            c.setFillColor(C_PURE_BLACK)
            c.setFont("DejaVu-Bold", 9.3)
            c.drawString(x0 + 3.2 * mm, 2.7 * mm, "Odpowiedź:")
            c.setStrokeColor(C_CKE_SALMON_GRID)
            c.setLineWidth(0.55)
            c.setDash(1.8, 1.4)
            c.line(x0 + 28 * mm, 2.3 * mm, x1 - 3.5 * mm, 2.3 * mm)

        c.restoreState()


class CKECoverLogoFlowable(Flowable):
    """Wektorowy znak CKE (oliwkowy pionowy prostokąt 'CKE' + napis CENTRALNA KOMISJA EGZAMINACYJNA)."""

    def __init__(self):
        super().__init__()
        self.width = 76 * mm
        self.height = 14.5 * mm

    def draw(self):
        c = self.canv
        c.saveState()
        # Pionowy oliwkowy prostokąt CKE
        bw, bh = 6.8 * mm, 13.8 * mm
        c.setFillColor(C_CKE_LOGO_BG)
        c.setStrokeColor(C_PURE_BLACK)
        c.setLineWidth(0.75)
        c.rect(0, 0.3 * mm, bw, bh, stroke=1, fill=1)

        c.saveState()
        c.translate(bw * 0.72, bh * 0.5 + 0.3 * mm)
        c.rotate(90)
        c.setFillColor(C_PURE_BLACK)
        c.setFont("DejaVu-Bold", 10.2)
        c.drawCentredString(0, 0, "CKE")
        c.restoreState()

        c.setFillColor(C_PURE_BLACK)
        c.setFont("DejaVu-Bold", 7.8)
        c.drawString(bw + 2.6 * mm, 9.6 * mm, "CENTRALNA")
        c.drawString(bw + 2.6 * mm, 5.7 * mm, "KOMISJA")
        c.drawString(bw + 2.6 * mm, 1.8 * mm, "EGZAMINACYJNA")
        c.restoreState()


class CKEHeroEmblemFlowable(Flowable):
    """Wektorowy zielony emblemat 'E8' (#7FA64E) do centralnej ramki tytułowej okładki CKE."""

    def __init__(self):
        super().__init__()
        self.width = 32 * mm
        self.height = 24 * mm

    def draw(self):
        c = self.canv
        c.saveState()
        # Dekoracyjna podwójna ramka w zieleni CKE
        c.setFillColor(C_CKE_BAR_LIGHT)
        c.setStrokeColor(C_CKE_E8_GREEN)
        c.setLineWidth(1.8)
        c.roundRect(1 * mm, 1 * mm, 29 * mm, 22 * mm, 2.2 * mm, stroke=1, fill=1)

        c.setFillColor(C_CKE_E8_GREEN)
        c.setFont("DejaVu-Bold", 28)
        c.drawCentredString(15.5 * mm, 5.5 * mm, "E8")
        c.restoreState()


class CKEBarcodeBoxFlowable(Flowable):
    """Wektorowa ramka kodu kreskowego CKE na dole okładki (np. OMAP-100-2605 z czerwonym '100')."""

    def __init__(self, exam_code: str, seed: int):
        super().__init__()
        self.exam_code = exam_code or "OMAP-100-2605"
        self.seed = seed
        self.width = 56 * mm
        self.height = 16.5 * mm

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(colors.white)
        c.setStrokeColor(C_PURE_BLACK)
        c.setLineWidth(0.8)
        c.rect(0, 0, self.width, self.height, stroke=1, fill=1)

        # Podziel kod typu OMAP-100-2605 tak, by człon '100' był w czerwieni CKE #C00000
        parts = self.exam_code.split("-")
        y_txt = self.height - 4.3 * mm
        c.setFont("DejaVu-Bold", 8.8)
        if len(parts) >= 3 and parts[1] == "100":
            p1 = parts[0] + "-"
            p2 = "100"
            p3 = "-" + "-".join(parts[2:])
            w1 = pdfmetrics.stringWidth(p1, "DejaVu-Bold", 8.8)
            w2 = pdfmetrics.stringWidth(p2, "DejaVu-Bold", 8.8)
            w3 = pdfmetrics.stringWidth(p3, "DejaVu-Bold", 8.8)
            sx = (self.width - (w1 + w2 + w3)) / 2.0
            c.setFillColor(C_PURE_BLACK)
            c.drawString(sx, y_txt, p1)
            c.setFillColor(C_CKE_CRIMSON)
            c.drawString(sx + w1, y_txt, p2)
            c.setFillColor(C_PURE_BLACK)
            c.drawString(sx + w1 + w2, y_txt, p3)
        else:
            c.setFillColor(C_PURE_BLACK)
            c.drawCentredString(self.width / 2.0, y_txt, self.exam_code)

        # Wektorowe paski kodu kreskowego (deterministyczne względem exam_code + seed)
        x_cur = 4.2 * mm
        x_end = self.width - 4.2 * mm
        bar_y0 = 1.8 * mm
        bar_h = 8.6 * mm
        c.setFillColor(C_PURE_BLACK)
        val = abs(hash(f"{self.exam_code}:{self.seed}")) | 0xA53C91
        idx = 0
        while x_cur < x_end - 1.0 * mm:
            bit = (val >> (idx % 29)) & 3
            bw = (0.38 + 0.24 * (bit % 3)) * mm
            gap = (0.34 + 0.20 * ((bit >> 1) & 1)) * mm
            if x_cur + bw > x_end:
                break
            c.rect(x_cur, bar_y0, bw, bar_h, stroke=0, fill=1)
            x_cur += bw + gap
            idx += 1

        c.restoreState()


# Alias zachowujący pełną kompatybilność wsteczną
SquaredGridFlowable = CKEOpenScannerGridFlowable


class NumberedCKECanvas(canvas.Canvas):
    """Canvas z dwuprzebiegową numeracją stron 'Strona X z Y' oraz autentyczną stopką CKE."""

    def __init__(
        self,
        *args,
        header_left: str = "",
        header_right: str = "",
        exam_code: str = "OMAP-100-2605",
        suppress_first_header: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self._header_left = header_left
        self._header_right = header_right
        self._exam_code = exam_code
        self._suppress_first_header = suppress_first_header

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
        margin_x = 15 * mm
        self.saveState()

        is_cover = self._suppress_first_header and self._pageNumber == 1

        if not is_cover:
            # Dyskretny pasek górny na stronach wewnętrznych
            self.setStrokeColor(C_CKE_BAR)
            self.setLineWidth(1.1)
            self.line(margin_x, page_h - 12.0 * mm, page_w - margin_x, page_h - 12.0 * mm)
            self.setFont("DejaVu", 7.6)
            self.setFillColor(C_MUTED)
            self.drawString(margin_x, page_h - 10.2 * mm, self._header_left)
            self.drawRightString(page_w - margin_x, page_h - 10.2 * mm, self._header_right)

        # Stopka w stylu CKE: wyśrodkowane "Strona X z Y", po lewej kod OMAP-100
        self.setFont("DejaVu-Bold", 8.6)
        self.setFillColor(C_PURE_BLACK)
        self.drawCentredString(page_w / 2.0, 8.0 * mm, f"Strona {self._pageNumber} z {total_pages}")

        if not is_cover:
            self.setFont("DejaVu", 7.4)
            self.setFillColor(C_MUTED)
            self.drawString(margin_x, 8.0 * mm, self._exam_code)
            self.drawRightString(page_w - margin_x, 8.0 * mm, "Więcej arkuszy: Generator E8 (wzorzec CKE)")

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
            fontSize=9.9,
            leading=14.6,
            textColor=C_BLACK,
            spaceAfter=3.5,
        ),
        "command": ParagraphStyle(
            "command",
            fontName="DejaVu-Bold",
            fontSize=9.9,
            leading=14.3,
            textColor=C_PURE_BLACK,
            spaceBefore=2.5,
            spaceAfter=4.5,
        ),
        "task_hdr": ParagraphStyle(
            "task_hdr",
            fontName="DejaVu-Bold",
            fontSize=10.3,
            leading=13.2,
            textColor=C_PURE_BLACK,
        ),
        "task_meta": ParagraphStyle(
            "task_meta",
            fontName="DejaVu",
            fontSize=8.0,
            leading=10.8,
            textColor=C_DARK,
            alignment=TA_RIGHT,
        ),
        "choice": ParagraphStyle(
            "choice",
            fontName="DejaVu",
            fontSize=9.7,
            leading=14.0,
            textColor=C_BLACK,
        ),
        "center": ParagraphStyle(
            "center",
            fontName="DejaVu",
            fontSize=9.4,
            leading=13.2,
            alignment=TA_CENTER,
            textColor=C_BLACK,
        ),
        "center_bold": ParagraphStyle(
            "center_bold",
            fontName="DejaVu-Bold",
            fontSize=9.4,
            leading=13.2,
            alignment=TA_CENTER,
            textColor=C_PURE_BLACK,
        ),
        "title_big": ParagraphStyle(
            "title_big",
            fontName="DejaVu-Bold",
            fontSize=15.5,
            leading=20.0,
            alignment=TA_CENTER,
            textColor=C_PURE_BLACK,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="DejaVu",
            fontSize=10.5,
            leading=14.5,
            alignment=TA_CENTER,
            textColor=C_DARK,
        ),
        "small": ParagraphStyle(
            "small",
            fontName="DejaVu",
            fontSize=8.6,
            leading=12.4,
            textColor=C_DARK,
        ),
        "step": ParagraphStyle(
            "step",
            fontName="DejaVu",
            fontSize=9.4,
            leading=14.2,
            textColor=C_BLACK,
            leftIndent=6,
            spaceAfter=2.2,
        ),
        "rubric": ParagraphStyle(
            "rubric",
            fontName="DejaVu",
            fontSize=8.7,
            leading=12.8,
            textColor=C_DARK,
            leftIndent=8,
            spaceAfter=1.4,
        ),
    }


def _build_cover_flowables(sheet: ExamSheet, content_w: float, styles: dict) -> List[Flowable]:
    """Buduje autentyczną pierwszą stronę okładki CKE E8 (OMAP-100 2025/2026)."""
    cfg = sheet.config
    flows: List[Flowable] = []

    # 1. Znak CKE w lewym górnym rogu
    flows.append(CKECoverLogoFlowable())
    flows.append(Spacer(1, 2.5 * mm))

    # 2. Pasek "WYPEŁNIA UCZEŃ" (#C5D9A4) + kratki KOD UCZNIA i PESEL po lewej oraz ramka O-100 po prawej
    wyp_bar = Table(
        [[Paragraph("<b>WYPEŁNIA UCZEŃ</b>", ParagraphStyle("wu", fontName="DejaVu-Bold", fontSize=8.6, leading=10.5, alignment=TA_CENTER, textColor=C_PURE_BLACK))]],
        colWidths=[112 * mm],
    )
    wyp_bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_CKE_BAR),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))

    code_tbl = Table([["" for _ in range(3)]], colWidths=[6.4 * mm] * 3, rowHeights=[7.2 * mm])
    code_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.95, C_PURE_BLACK),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
    ]))

    pesel_tbl = Table([["" for _ in range(11)]], colWidths=[6.1 * mm] * 11, rowHeights=[7.2 * mm])
    pesel_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.95, C_PURE_BLACK),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
    ]))

    lbl_st = ParagraphStyle("lbl_cke", fontName="DejaVu-Bold", fontSize=7.8, leading=9.8, textColor=C_PURE_BLACK)
    codes_grid = Table(
        [
            [Paragraph("KOD UCZNIA", lbl_st), Paragraph("PESEL", lbl_st)],
            [code_tbl, pesel_tbl],
        ],
        colWidths=[27 * mm, 85 * mm],
    )
    codes_grid.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    left_student_col = Table([[wyp_bar], [codes_grid]], colWidths=[112 * mm])
    left_student_col.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    sticker_w = 54 * mm
    sticker_box = Table(
        [
            [Paragraph("<font color='#C00000' size='11'><b>O-100</b></font>", styles["center_bold"])],
            [Paragraph("Miejsce na naklejkę", ParagraphStyle("mn", parent=styles["center"], fontSize=8.0, textColor=C_MUTED))],
        ],
        colWidths=[sticker_w],
        rowHeights=[7.5 * mm, 13.5 * mm],
    )
    sticker_box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.9, C_PURE_BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
    ]))

    top_row = Table(
        [[left_student_col, "", sticker_box]],
        colWidths=[112 * mm, content_w - 112 * mm - sticker_w, sticker_w],
    )
    top_row.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flows.append(top_row)
    flows.append(Spacer(1, 5.5 * mm))

    # 3. Centralna czarna ramka tytułowa z zielonym emblematem E8 (#7FA64E)
    date_txt = cfg.exam_date_str.strip() or "maj / czerwiec 2026 r."
    school_line = f" · <b>{cfg.school_or_group.strip()}</b>" if cfg.school_or_group.strip() else ""
    hero_right = [
        Paragraph("<b>Egzamin ósmoklasisty</b>", ParagraphStyle("eh1", fontName="DejaVu-Bold", fontSize=15.0, leading=19.0, textColor=C_PURE_BLACK)),
        Paragraph("<b>Matematyka</b>", ParagraphStyle("eh2", fontName="DejaVu-Bold", fontSize=13.5, leading=17.5, textColor=C_CKE_TEXT_GREEN)),
        Spacer(1, 2.2 * mm),
        Paragraph(f"<b>DATA:</b> {date_txt}{school_line}", ParagraphStyle("em1", fontName="DejaVu", fontSize=9.0, leading=12.5, textColor=C_PURE_BLACK)),
        Paragraph(f"<b>GODZINA ROZPOCZĘCIA:</b> 9:00 &nbsp;&nbsp;·&nbsp;&nbsp; <b>WERSJA:</b> {cfg.variant_code} (#{sheet.used_seed})", ParagraphStyle("em2", fontName="DejaVu", fontSize=9.0, leading=12.5, textColor=C_PURE_BLACK)),
        Paragraph(f"<b>CZAS PRACY:</b> {cfg.duration_minutes} minut &nbsp;&nbsp;·&nbsp;&nbsp; <b>LICZBA PUNKTÓW DO UZYSKANIA:</b> {sheet.total_points}", ParagraphStyle("em3", fontName="DejaVu-Bold", fontSize=9.0, leading=12.5, textColor=C_PURE_BLACK)),
    ]
    hero_tbl = Table(
        [[CKEHeroEmblemFlowable(), hero_right]],
        colWidths=[37 * mm, content_w - 37 * mm],
    )
    hero_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.25, C_PURE_BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 4 * mm),
        ("LEFTPADDING", (1, 0), (1, 0), 3 * mm),
        ("RIGHTPADDING", (1, 0), (1, 0), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5 * mm),
    ]))
    flows.append(hero_tbl)
    flows.append(Spacer(1, 5.5 * mm))

    # 4. Instrukcja dla ucznia w stylu CKE OMAP-100 (z zielonymi wyróżnieniami #537A26)
    n_closed = len(sheet.closed_tasks)
    n_open = len(sheet.open_tasks)
    pts_word = pl_plural(sheet.total_points, "punkt", "punkty", "punktów")

    flows.append(Paragraph("<b>Instrukcja dla ucznia</b>", ParagraphStyle("inst_h", fontName="DejaVu-Bold", fontSize=10.8, leading=14.0, textColor=C_PURE_BLACK)))
    flows.append(Spacer(1, 1.8 * mm))

    inst_style = ParagraphStyle("inst_cke", fontName="DejaVu", fontSize=8.7, leading=12.5, spaceAfter=2.4, leftIndent=11, firstLineIndent=-11, textColor=C_PURE_BLACK)
    g_hex = "#537A26"
    instructions = [
        f"1. Sprawdź, czy na kolejno ponumerowanych stronach jest wydrukowanych <b>{len(sheet.tasks)} zadań</b> "
        f"(zadania zamknięte: 1–{n_closed if n_closed else '–'}, zadania otwarte: "
        f"{(n_closed + 1) if n_open else '–'}–{len(sheet.tasks) if n_open else '–'}). "
        "Ewentualny brak stron lub innych elementów arkusza zgłoś nauczycielowi.",
        f"2. Na tej stronie wpisz swój kod i numer PESEL. Za rozwiązanie wszystkich zadań można otrzymać łącznie <b>{sheet.total_points} {pts_word}</b>.",
        f"3. Rozwiązania zadań i odpowiedzi zapisuj w miejscu na to przeznaczonym. W zadaniach otwartych wykorzystaj "
        f"<font color='{g_hex}'><b>kratkowane pole rozwiązań zadań otwartych</b></font> – zapisy poza czarną ramką nie będą oceniane.",
        f"4. W zadaniach zamkniętych wybierz właściwą odpowiedź spośród podanych oraz przenieś swoje odpowiedzi na "
        f"<font color='{g_hex}'><b>kartę odpowiedzi</b></font> (jeśli została dołączona na końcu arkusza).",
        "5. W rozwiązaniach zadań otwartych przedstaw tok rozumowania prowadzący do wyniku – sam wynik bez obliczeń może nie uzyskać maksymalnej liczby punktów.",
        "6. Pisz czytelnie. Używaj tylko długopisu lub pióra z czarnym tuszem/atramentem. Nie używaj korektora, a błędne zapisy wyraźnie przekreśl.",
        "7. Rysunki wykonuj długopisem. Nie korzystaj z ołówka ani z <b>kalkulatora</b>.",
        "8. Zapisy w brudnopisie nie będą sprawdzane i nie będą oceniane.",
    ]
    for line in instructions:
        flows.append(Paragraph(line, inst_style))

    flows.append(Spacer(1, 5.5 * mm))

    # 5. Dolny wiersz okładki: "Powodzenia!" + ramka kodu kreskowego OMAP-100-XXXX
    pow_par = Paragraph("<b><i>Powodzenia!</i></b>", ParagraphStyle("pow_cke", fontName="DejaVu-BoldItalic", fontSize=11.0, leading=14.0, alignment=TA_RIGHT, textColor=C_PURE_BLACK))
    right_bottom = Table(
        [[pow_par], [Spacer(1, 2.0 * mm)], [CKEBarcodeBoxFlowable(cfg.exam_code, sheet.used_seed)]],
        colWidths=[56 * mm],
    )
    right_bottom.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
    ]))

    left_note = Paragraph(
        f"<font size='7.6' color='#475569'>Układ wizualny wzorowany na arkuszu CKE <b>{cfg.exam_code}</b><br/>"
        f"{cfg.subtitle}</font>",
        styles["small"],
    )
    bottom_row = Table(
        [[left_note, right_bottom]],
        colWidths=[content_w - 56 * mm, 56 * mm],
    )
    bottom_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    flows.append(bottom_row)
    flows.append(PageBreak())
    return flows


def _build_compact_header(sheet: ExamSheet, content_w: float, styles: dict) -> List[Flowable]:
    """Kompaktowy nagłówek w kolorach CKE na górze 1. strony, gdy pełna okładka jest wyłączona."""
    cfg = sheet.config
    left_txt = f"<b>{cfg.title}</b><br/><font size='8.6' color='#1E293B'>{cfg.subtitle}"
    if cfg.school_or_group.strip():
        left_txt += f" · {cfg.school_or_group.strip()}"
    left_txt += "</font>"

    right_txt = (
        f"<font color='#C00000'><b>{cfg.exam_code}</b></font> · <b>{cfg.variant_code}</b> (#{sheet.used_seed})<br/>"
        f"<font size='8.4'>Zadań: {len(sheet.tasks)} · Suma pkt: <b>{sheet.total_points}</b> · Czas: {cfg.duration_minutes} min</font>"
    )
    hdr_tbl = Table(
        [[Paragraph(left_txt, styles["body"]), Paragraph(right_txt, ParagraphStyle("r", parent=styles["body"], alignment=TA_RIGHT))]],
        colWidths=[content_w * 0.58, content_w * 0.42],
    )
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_CKE_BAR),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    name_row = Table(
        [[Paragraph("<b>Imię i nazwisko / KOD UCZNIA:</b> ..........................................................................", styles["small"]),
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


def _make_twin_box_table(k1: str, k2: str) -> Table:
    """Tworzy bliźniacze kwadratowe okienka wyboru [ A | B ] lub [ C | D ] dokładnie jak w zadaniach CKE."""
    t = Table(
        [[Paragraph(f"<b>{k1}</b>", ParagraphStyle("tb1", fontName="DejaVu-Bold", fontSize=9.2, leading=10.5, alignment=TA_CENTER)),
          Paragraph(f"<b>{k2}</b>", ParagraphStyle("tb2", fontName="DejaVu-Bold", fontSize=9.2, leading=10.5, alignment=TA_CENTER))]],
        colWidths=[6.8 * mm, 6.8 * mm],
        rowHeights=[6.4 * mm],
    )
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.9, C_PURE_BLACK),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def _build_task_flowables(task: Task, content_w: float, styles: dict, include_open_grid: bool) -> List[Flowable]:
    """Buduje blok pojedynczego zadania egzaminacyjnego w oryginalnej kolorystyce CKE OMAP-100."""
    items: List[Flowable] = []

    # Autentyczny bezramkowy szałwiowo-oliwkowy pasek CKE: "Zadanie X. (0–Y)"
    hdr_text = f"Zadanie {task.number}. (0–{task.points})"
    hdr_tbl = Table([[Paragraph(hdr_text, styles["task_hdr"])]], colWidths=[content_w])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_CKE_BAR),
        ("TOPPADDING", (0, 0), (-1, -1), 3.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6.5),
    ]))
    items.append(hdr_tbl)
    items.append(Spacer(1, 2.2 * mm))

    # Treść zadania (stem)
    items.append(_make_paragraph(task.stem, styles["body"]))

    # Opcjonalna tabela danych (z nagłówkiem w jasnej zieleni CKE)
    if task.table_data:
        items.append(Spacer(1, 1.5 * mm))
        ncols = len(task.table_data[0])
        if ncols == 2:
            col_widths = [58 * mm, 34 * mm]
        else:
            first_w = min(56 * mm, content_w * 0.35)
            rem_w = min((content_w - first_w) / (ncols - 1), 32 * mm)
            col_widths = [first_w] + [rem_w] * (ncols - 1)

        t_rows = []
        for r_idx, row in enumerate(task.table_data):
            st = styles["center_bold"] if r_idx == 0 else styles["center"]
            t_rows.append([_make_paragraph(cell, st) for cell in row])

        data_tbl = Table(t_rows, colWidths=col_widths, hAlign="CENTER")
        data_tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.75, C_PURE_BLACK),
            ("BACKGROUND", (0, 0), (-1, 0), C_CKE_BAR_LIGHT),
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
        max_h = 54 * mm
        if target_h > max_h:
            scale = max_h / target_h
            target_w *= scale
            target_h = max_h
        img_flow = RLImage(img_path, width=target_w, height=target_h)
        img_flow.hAlign = "CENTER"
        items.append(Spacer(1, 1.0 * mm))
        items.append(img_flow)
        items.append(Spacer(1, 1.4 * mm))

    # Polecenie pogrubione
    items.append(_make_paragraph(task.command, styles["command"]))

    # Sekcja odpowiedzi zależna od typu zadania
    if task.subtype == "abcd":
        letters = ["A", "B", "C", "D"]
        raw_lens = [len(task.choices.get(L, "")) for L in letters]
        max_len = max(raw_lens) if raw_lens else 0

        if max_len <= 26:
            row = [_make_paragraph(f"**{L}.** {task.choices[L]}", styles["choice"]) for L in letters]
            ans_tbl = Table([row], colWidths=[content_w / 4.0] * 4)
        elif max_len <= 52:
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
            ("GRID", (0, 0), (-1, -1), 0.8, C_PURE_BLACK),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, -1), 6),
            ("RIGHTPADDING", (0, 0), (0, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        items.append(pf_tbl)

    elif task.subtype == "ab_cd":
        for part in task.ab_cd_parts:
            keys = sorted(part["options"].keys())  # ["A", "B"] lub ["C", "D"]
            sfx = part.get("suffix", ".")
            twin = _make_twin_box_table(keys[0], keys[1])
            sent_tbl = Table(
                [[_make_paragraph(part["prefix"], styles["body"]), twin, _make_paragraph(sfx, styles["body"])]],
                colWidths=[content_w - 26 * mm, 15.5 * mm, 10.5 * mm],
            )
            sent_tbl.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            items.append(sent_tbl)

            opt_row = [
                _make_paragraph(f"**{keys[0]}.** {part['options'][keys[0]]}", styles["choice"]),
                _make_paragraph(f"**{keys[1]}.** {part['options'][keys[1]]}", styles["choice"]),
            ]
            opt_tbl = Table([opt_row], colWidths=[content_w * 0.46, content_w * 0.46], hAlign="LEFT")
            opt_tbl.setStyle(TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            items.append(opt_tbl)

    elif task.subtype == "uzasadnienie":
        jd = task.justification_data
        ab_dict = jd.get("choices_ab", {"A": "Tak,", "B": "Nie,"})
        conn = jd.get("connector", "ponieważ")
        reasons = jd.get("reasons", {})

        left_sub = Table(
            [
                [_make_paragraph(f"**A.** {ab_dict['A']}", styles["choice"])],
                [_make_paragraph(f"**B.** {ab_dict['B']}", styles["choice"])],
            ],
            colWidths=[27 * mm],
        )
        left_sub.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.75, C_PURE_BLACK),
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
            ("GRID", (0, 0), (-1, -1), 0.75, C_PURE_BLACK),
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
            items.append(CKEOpenScannerGridFlowable(content_w, height_mm=task.grid_height_mm, include_answer_box=True))
        else:
            items.append(Spacer(1, 3 * mm))

    items.append(Spacer(1, 5.2 * mm))
    return [KeepTogether(items)]


def _build_transfer_banner(content_w: float) -> Flowable:
    """ Charakterystyczny pasek przypomnienia CKE po zadaniach zamkniętych."""
    tbl = Table(
        [[Paragraph(
            "<font color='#537A26'><b>PRZENIEŚ ROZWIĄZANIA ZADAŃ ZAMKNIĘTYCH NA KARTĘ ODPOWIEDZI!</b></font>",
            ParagraphStyle("tr_b", fontName="DejaVu-Bold", fontSize=9.4, leading=12.5, alignment=TA_CENTER),
        )]],
        colWidths=[content_w],
    )
    tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.9, C_CKE_E8_GREEN),
        ("BACKGROUND", (0, 0), (-1, -1), C_CKE_BAR_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tbl


def _build_answer_card_flowables(sheet: ExamSheet, content_w: float, styles: dict) -> List[Flowable]:
    """Buduje stronę KARTY ODPOWIEDZI w kolorystyce CKE OMAP-100 (szałwiowa zieleń + łososiowe kratki OMR)."""
    closed = sheet.closed_tasks
    if not closed:
        return []

    flows: List[Flowable] = [PageBreak()]
    hdr = Table(
        [[
            Paragraph("<b>KARTA ODPOWIEDZI – ZADANIA ZAMKNIĘTE</b>", styles["task_hdr"]),
            Paragraph(f"<font color='#C00000'><b>{sheet.config.exam_code}</b></font> · <b>{sheet.config.variant_code}</b>", ParagraphStyle("kr", parent=styles["task_hdr"], alignment=TA_RIGHT)),
        ]],
        colWidths=[content_w * 0.65, content_w * 0.35],
    )
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_CKE_BAR),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    flows.append(hdr)
    flows.append(Spacer(1, 3 * mm))

    code_row = Table(
        [[
            Paragraph("<b>KOD UCZNIA:</b> [ ___ | ___ | ___ ]", styles["small"]),
            Paragraph("<b>PESEL:</b> [ __ | __ | __ | __ | __ | __ | __ | __ | __ | __ | __ ]", ParagraphStyle("pr", parent=styles["small"], alignment=TA_RIGHT)),
        ]],
        colWidths=[content_w * 0.36, content_w * 0.64],
    )
    flows.append(code_row)
    flows.append(Spacer(1, 3 * mm))
    flows.append(Paragraph(
        "Zamaluj całkowicie właściwą kratkę (np. <b>■</b>) długopisem z czarnym tuszem. "
        "W przypadku pomyłki otocz błędnie zaznaczoną kratkę kółkiem i zamaluj właściwą.",
        styles["small"],
    ))
    flows.append(Spacer(1, 3.5 * mm))

    rows = [[
        Paragraph("<b>Nr zad.</b>", styles["center_bold"]),
        Paragraph("<b>Typ zadania</b>", styles["center_bold"]),
        Paragraph("<b>Kratki odpowiedzi (zamaluj właściwe)</b>", styles["center_bold"]),
    ]]
    cell_st = ParagraphStyle("omr", fontName="DejaVu-Bold", fontSize=8.8, leading=11.5, alignment=TA_CENTER, textColor=C_CKE_SALMON_TEXT)
    for t in closed:
        if t.subtype == "abcd":
            bubbles = "[ A ] &nbsp;&nbsp;&nbsp; [ B ] &nbsp;&nbsp;&nbsp; [ C ] &nbsp;&nbsp;&nbsp; [ D ]"
            t_lbl = "Wybór A / B / C / D"
        elif t.subtype == "pf":
            bubbles = "Zdanie 1.: &nbsp; [ P ] &nbsp; [ F ] &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Zdanie 2.: &nbsp; [ P ] &nbsp; [ F ]"
            t_lbl = "Prawda / Fałsz"
        elif t.subtype == "ab_cd":
            bubbles = "Zdanie 1.: &nbsp; [ A ] &nbsp; [ B ] &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Zdanie 2.: &nbsp; [ C ] &nbsp; [ D ]"
            t_lbl = "Podwójny wybór A/B i C/D"
        else:
            bubbles = "Stwierdzenie: [ A ] [ B ] &nbsp;&nbsp;&nbsp;&nbsp; Uzasadnienie: [ 1 ] [ 2 ] [ 3 ]"
            t_lbl = "Odpowiedź z uzasadnieniem"

        rows.append([
            Paragraph(f"<b>{t.number}.</b>", styles["center_bold"]),
            Paragraph(t_lbl, styles["small"]),
            Paragraph(bubbles, cell_st),
        ])

    omr_tbl = Table(rows, colWidths=[18 * mm, 52 * mm, content_w - 70 * mm])
    omr_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.7, C_CKE_SALMON_TICK),
        ("BOX", (0, 0), (-1, -1), 1.0, C_PURE_BLACK),
        ("BACKGROUND", (0, 0), (-1, 0), C_CKE_BAR_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    flows.append(omr_tbl)

    # Tabela dla egzaminatora na punkty z zadań otwartych
    if sheet.open_tasks:
        flows.append(Spacer(1, 6 * mm))
        wyp_egz = Table(
            [[Paragraph("<b>WYPEŁNIA EGZAMINATOR / NAUCZYCIEL – ZADANIA OTWARTE</b>", styles["center_bold"])]],
            colWidths=[content_w],
        )
        wyp_egz.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_CKE_BAR),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        flows.append(wyp_egz)

        open_hdr = [Paragraph("<b>Zadanie</b>", styles["center_bold"])] + [
            Paragraph(f"<b>{t.number}. (0–{t.points})</b>", styles["center_bold"]) for t in sheet.open_tasks
        ] + [Paragraph("<b>SUMA</b>", styles["center_bold"])]
        open_pts = [Paragraph("<b>Punkty</b>", styles["center_bold"])] + [
            Paragraph("", styles["center"]) for _ in sheet.open_tasks
        ] + [Paragraph(f"/ {sum(t.points for t in sheet.open_tasks)}", styles["center"])]

        ncols = len(open_hdr)
        egz_tbl = Table([open_hdr, open_pts], colWidths=[content_w / ncols] * ncols, rowHeights=[7 * mm, 9 * mm])
        egz_tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.8, C_PURE_BLACK),
            ("BACKGROUND", (0, 0), (-1, 0), C_CKE_BAR_LIGHT),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        flows.append(egz_tbl)

    return flows


def build_exam_pdf_bytes(sheet: ExamSheet) -> bytes:
    """Generuje plik PDF arkusza egzaminacyjnego dla ucznia w szacie CKE OMAP-100 i zwraca `bytes`."""
    ensure_fonts()
    styles = _get_styles()
    buf = io.BytesIO()

    margin_x = 15 * mm
    margin_y = 15.5 * mm
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

    n_closed = len(sheet.closed_tasks)
    for idx, task in enumerate(sheet.tasks, start=1):
        story.extend(
            _build_task_flowables(
                task,
                content_w=content_w,
                styles=styles,
                include_open_grid=sheet.config.include_answer_grid_for_open,
            )
        )
        if idx == n_closed and n_closed > 0 and sheet.config.include_answer_card:
            story.append(_build_transfer_banner(content_w))
            story.append(Spacer(1, 5 * mm))

    if sheet.config.include_scratchpad_page:
        story.append(PageBreak())
        brud_bar = Table([[Paragraph("<b>BRUDNOPIS</b> (zapisy w brudnopisie nie będą oceniane)", styles["center_bold"])]], colWidths=[content_w])
        brud_bar.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_CKE_BAR),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(brud_bar)
        story.append(Spacer(1, 4 * mm))
        story.append(CKEOpenScannerGridFlowable(content_w, height_mm=220.0, include_answer_box=False))

    if sheet.config.include_answer_card and n_closed > 0:
        story.extend(_build_answer_card_flowables(sheet, content_w, styles))

    header_left = f"{sheet.config.title} – ARKUSZ ZADAŃ"
    header_right = f"{sheet.config.variant_code} · Zestaw #{sheet.used_seed}"

    doc.build(
        story,
        canvasmaker=lambda *a, **kw: NumberedCKECanvas(
            *a,
            header_left=header_left,
            header_right=header_right,
            exam_code=sheet.config.exam_code,
            suppress_first_header=sheet.config.include_cover_page,
            **kw,
        ),
    )
    return buf.getvalue()


def build_key_pdf_bytes(sheet: ExamSheet) -> bytes:
    """Generuje osobny plik PDF z kluczem odpowiedzi, statystyką działów CKE, rozwiązaniami i punktacją."""
    ensure_fonts()
    styles = _get_styles()
    buf = io.BytesIO()

    margin_x = 15 * mm
    margin_y = 16 * mm
    content_w = A4[0] - 2 * margin_x

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=margin_y,
        bottomMargin=margin_y,
        title=f"Klucz odpowiedzi i zasady oceniania – {sheet.config.variant_code}",
    )

    story: List[Flowable] = []

    # Nagłówek klucza w kolorystyce CKE
    hdr_block = Table(
        [
            [Paragraph("ZASADY OCENIANIA ROZWIĄZAŃ ZADAŃ I KLUCZ ODPOWIEDZI", styles["title_big"])],
            [Paragraph(
                f"{sheet.config.title} · <font color='#C00000'><b>{sheet.config.exam_code}</b></font> · "
                f"<b>{sheet.config.variant_code}</b> (Zestaw #{sheet.used_seed}) · "
                f"Suma punktów: <b>{sheet.total_points}</b>",
                styles["center"],
            )],
        ],
        colWidths=[content_w],
    )
    hdr_block.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.1, C_PURE_BLACK),
        ("BACKGROUND", (0, 0), (-1, -1), C_CKE_BAR),
        ("TOPPADDING", (0, 0), (0, 0), 7),
        ("BOTTOMPADDING", (0, -1), (0, -1), 7),
    ]))
    story.append(hdr_block)
    story.append(Spacer(1, 4.5 * mm))

    # 1. Szybka tabela odpowiedzi dla zadań zamkniętych
    closed = sheet.closed_tasks
    if closed:
        story.append(Paragraph("<b>1. Klucz odpowiedzi do zadań zamkniętych (po 1 pkt)</b>", styles["command"]))
        per_row = min(8, len(closed))
        col_w = content_w / per_row
        for chunk_start in range(0, len(closed), per_row):
            chunk = closed[chunk_start:chunk_start + per_row]
            r_num = [Paragraph(f"<b>Zad. {t.number}</b>", styles["center_bold"]) for t in chunk]
            r_ans = [Paragraph(f"<font color='#537A26'><b>{t.correct_answer}</b></font>", styles["center_bold"]) for t in chunk]
            while len(r_num) < per_row:
                r_num.append(Paragraph("", styles["center"]))
                r_ans.append(Paragraph("", styles["center"]))
            quick_tbl = Table([r_num, r_ans], colWidths=[col_w] * per_row)
            quick_tbl.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.65, C_PURE_BLACK),
                ("BACKGROUND", (0, 0), (-1, 0), C_CKE_BAR_LIGHT),
                ("TOPPADDING", (0, 0), (-1, -1), 3.8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.8),
            ]))
            story.append(quick_tbl)
            story.append(Spacer(1, 2.2 * mm))
        story.append(Spacer(1, 2.0 * mm))

    # 2. Podsumowanie rozkładu działów CKE w tym zestawie
    if sheet.topic_probabilities:
        story.append(Paragraph("<b>2. Rozkład prawdopodobieństwa działów CKE (2019–2026) i pokrycie w arkuszu</b>", styles["command"]))
        counts_in_sheet: Dict[str, int] = {}
        pts_in_sheet: Dict[str, int] = {}
        for t in sheet.tasks:
            counts_in_sheet[t.topic_id] = counts_in_sheet.get(t.topic_id, 0) + 1
            pts_in_sheet[t.topic_id] = pts_in_sheet.get(t.topic_id, 0) + t.points

        dist_rows = [[
            Paragraph("<b>Dział podstawy programowej</b>", styles["small"]),
            Paragraph("<b>Waga CKE</b>", styles["center_bold"]),
            Paragraph("<b>Cel aktywny</b>", styles["center_bold"]),
            Paragraph("<b>W tym arkuszu</b>", styles["center_bold"]),
        ]]
        n_tasks_tot = max(1, len(sheet.tasks))
        for top in TOPICS:
            p_act = sheet.topic_probabilities.get(top.id, 0.0)
            cnt = counts_in_sheet.get(top.id, 0)
            if p_act <= 0 and cnt == 0:
                continue
            p_base = EMPIRICAL_STATS[top.id].base_probability if top.id in EMPIRICAL_STATS else 0.0
            pts_t = pts_in_sheet.get(top.id, 0)
            dist_rows.append([
                Paragraph(top.short_name, styles["small"]),
                Paragraph(f"{p_base * 100:.1f}%".replace(".", ","), styles["center"]),
                Paragraph(f"<b>{p_act * 100:.1f}%</b>".replace(".", ","), styles["center"]),
                Paragraph(f"{cnt} zad. ({cnt / n_tasks_tot * 100:.0f}%, {pts_t} pkt)", styles["center"]),
            ])
        dist_tbl = Table(dist_rows, colWidths=[content_w * 0.43, content_w * 0.17, content_w * 0.18, content_w * 0.22])
        dist_tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.55, C_BORDER),
            ("BACKGROUND", (0, 0), (-1, 0), C_CKE_BAR_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(dist_tbl)
        story.append(Spacer(1, 4.5 * mm))

    # 3. Szczegółowe rozwiązania wszystkich zadań
    sec_num = "3" if sheet.topic_probabilities else "2"
    story.append(Paragraph(f"<b>{sec_num}. Pełne rozwiązania krok po kroku oraz kryteria punktowania CKE</b>", styles["command"]))
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
            colWidths=[content_w * 0.54, content_w * 0.46],
        )
        t_hdr.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_CKE_BAR),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.4),
            ("LEFTPADDING", (0, 0), (0, -1), 6.5),
            ("RIGHTPADDING", (-1, 0), (-1, -1), 5.5),
        ]))
        block.append(t_hdr)
        block.append(Spacer(1, 1.5 * mm))

        for step_txt in task.solution_steps:
            block.append(_make_paragraph(f"• {step_txt}", styles["step"]))

        if task.scoring_scheme:
            block.append(Spacer(1, 1 * mm))
            block.append(Paragraph("<font color='#537A26'><b>Schemat punktowania CKE:</b></font>", styles["rubric"]))
            for sc in task.scoring_scheme:
                block.append(_make_paragraph(f"– {sc}", styles["rubric"]))

        block.append(Spacer(1, 4.0 * mm))
        story.append(KeepTogether(block))

    header_left = f"ZASADY OCENIANIA I KLUCZ – {sheet.config.title}"
    header_right = f"{sheet.config.variant_code} · Zestaw #{sheet.used_seed}"

    doc.build(
        story,
        canvasmaker=lambda *a, **kw: NumberedCKECanvas(
            *a,
            header_left=header_left,
            header_right=header_right,
            exam_code=sheet.config.exam_code,
            suppress_first_header=False,
            **kw,
        ),
    )
    return buf.getvalue()
