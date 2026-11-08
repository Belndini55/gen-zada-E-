"""Widżet podglądu stron A4 dokumentu PDF (renderowanie za pomocą pypdfium2)."""

from __future__ import annotations

from typing import List, Optional

import pypdfium2 as pdfium
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class PdfPreviewWidget(QWidget):
    """Przewijany podgląd kartek A4 dokumentu PDF z regulacją powiększenia."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._pdf_bytes: Optional[bytes] = None
        self._zoom: float = 1.25  # 1.0 ~ ok. 100% ekranowe
        self._page_labels: List[QLabel] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Pasek narzędzi powiększenia
        toolbar = QFrame()
        toolbar.setObjectName("PreviewToolbar")
        tb_lay = QHBoxLayout(toolbar)
        tb_lay.setContentsMargins(12, 6, 12, 6)
        tb_lay.setSpacing(8)

        self._page_info_lbl = QLabel("Brak wygenerowanego dokumentu")
        self._page_info_lbl.setObjectName("MutedLabel")
        tb_lay.addWidget(self._page_info_lbl)
        tb_lay.addStretch(1)

        btn_zoom_out = QPushButton("− Pomniejsz")
        btn_zoom_out.setObjectName("SmallGhostBtn")
        btn_zoom_out.clicked.connect(self._on_zoom_out)

        self._zoom_lbl = QLabel("100%")
        self._zoom_lbl.setMinimumWidth(48)
        self._zoom_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_zoom_in = QPushButton("+ Powiększ")
        btn_zoom_in.setObjectName("SmallGhostBtn")
        btn_zoom_in.clicked.connect(self._on_zoom_in)

        btn_zoom_reset = QPushButton("Dopasuj (100%)")
        btn_zoom_reset.setObjectName("SmallGhostBtn")
        btn_zoom_reset.clicked.connect(self._on_zoom_reset)

        tb_lay.addWidget(btn_zoom_out)
        tb_lay.addWidget(self._zoom_lbl)
        tb_lay.addWidget(btn_zoom_in)
        tb_lay.addWidget(btn_zoom_reset)
        root.addWidget(toolbar)

        # Obszar przewijania kartek A4
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { background-color: #CBD5E1; border: none; }")

        self._pages_container = QWidget()
        self._pages_container.setStyleSheet("background-color: #CBD5E1;")
        self._pages_layout = QVBoxLayout(self._pages_container)
        self._pages_layout.setContentsMargins(20, 18, 20, 24)
        self._pages_layout.setSpacing(18)
        self._pages_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self._scroll.setWidget(self._pages_container)
        root.addWidget(self._scroll, 1)

    def set_pdf_bytes(self, pdf_bytes: bytes) -> None:
        self._pdf_bytes = pdf_bytes
        self._rerender_pages()

    def _on_zoom_in(self) -> None:
        if self._zoom < 2.4:
            self._zoom = round(self._zoom + 0.2, 2)
            self._rerender_pages()

    def _on_zoom_out(self) -> None:
        if self._zoom > 0.65:
            self._zoom = round(self._zoom - 0.2, 2)
            self._rerender_pages()

    def _on_zoom_reset(self) -> None:
        self._zoom = 1.25
        self._rerender_pages()

    def _rerender_pages(self) -> None:
        pct = int(round((self._zoom / 1.25) * 100))
        self._zoom_lbl.setText(f"{pct}%")

        new_container = QWidget()
        new_container.setStyleSheet("background-color: #CBD5E1;")
        pages_layout = QVBoxLayout(new_container)
        pages_layout.setContentsMargins(20, 18, 20, 24)
        pages_layout.setSpacing(18)

        if not self._pdf_bytes:
            self._page_info_lbl.setText("Brak wygenerowanego dokumentu")
            self._scroll.setWidget(new_container)
            return

        doc = pdfium.PdfDocument(self._pdf_bytes)
        n_pages = len(doc)
        strony_word = (
            "strona"
            if n_pages == 1
            else ("strony" if 2 <= (n_pages % 10) <= 4 and not (12 <= (n_pages % 100) <= 14) else "stron")
        )
        self._page_info_lbl.setText(f"Podgląd wydruku A4: {n_pages} {strony_word}")

        for idx in range(n_pages):
            page = doc[idx]
            bmp = page.render(scale=self._zoom)
            pil_img = bmp.to_pil().convert("RGBA")
            raw = pil_img.tobytes("raw", "RGBA")
            qimg = QImage(
                raw, pil_img.width, pil_img.height, pil_img.width * 4, QImage.Format.Format_RGBA8888
            ).copy()
            pix = QPixmap.fromImage(qimg)

            card = QLabel()
            card.setPixmap(pix)
            card.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.setStyleSheet("background-color: #FFFFFF; border: 1px solid #94A3B8; padding: 0px;")
            card.setFixedSize(pix.width() + 2, pix.height() + 2)
            pages_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)

        pages_layout.addStretch(1)
        self._scroll.setWidget(new_container)
