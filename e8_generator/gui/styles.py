"""Arkusze stylów QSS dla aplikacji desktopowej PyQt6: motyw Jasny (CKE OMAP-100) oraz motyw Ciemny."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

_PREFS_PATH = Path.home() / ".gen_zadan_e8_ui.json"


LIGHT_STYLESHEET = """
QMainWindow, QWidget#RootWidget, QWidget#FormScrollBody, QWidget#CardsScrollBody {
    background-color: #F2F5EE;
    color: #0F172A;
    font-family: "Segoe UI", "DejaVu Sans", sans-serif;
    font-size: 13px;
}

QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #C9D6B8;
    border-radius: 8px;
    margin-top: 12px;
    padding: 14px 12px 10px 12px;
    font-weight: 600;
    color: #1E293B;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 6px;
    background-color: #FFFFFF;
    color: #466A1E;
    font-size: 13px;
    font-weight: 700;
}

QLabel {
    color: #1E293B;
    background-color: transparent;
}

QLabel#MutedLabel {
    color: #556558;
    font-size: 12px;
}

QLabel#RedistributionBanner {
    background-color: #EFF6E4;
    color: #3D5E18;
    border: 1px solid #C5D9A4;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 11.5px;
    font-weight: 600;
}

QLabel#SummaryBadge {
    background-color: #EAF2DC;
    color: #365414;
    border: 1px solid #B6CF8E;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 700;
    font-size: 13px;
}

QLabel#HeaderTitle {
    font-size: 16px;
    font-weight: 700;
    color: #1A2E05;
}

QLabel#SheetStatusLabel {
    font-size: 13px;
    font-weight: 600;
    color: #1E293B;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #C4D0BA;
    border-radius: 6px;
    padding: 5px 8px;
    color: #0F172A;
    min-height: 22px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1.5px solid #5B822E;
    background-color: #FFFFFF;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #B6CF8E;
    selection-background-color: #E3ECD4;
    selection-color: #1A2E05;
}

QCheckBox {
    spacing: 6px;
    color: #1E293B;
    padding: 2px 0px;
}

QCheckBox#AccentCheckBox {
    font-weight: 700;
    color: #3D5E18;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #C4D0BA;
    border-radius: 6px;
    padding: 6px 12px;
    color: #1E293B;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #F6F9F2;
    border-color: #8BA868;
}

QPushButton:pressed {
    background-color: #E3ECD4;
}

QPushButton#PrimaryGenerateBtn {
    background-color: #537A26;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 11px 18px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#PrimaryGenerateBtn:hover {
    background-color: #638F2E;
}

QPushButton#PrimaryGenerateBtn:pressed {
    background-color: #3E5C1B;
}

QPushButton#CompactPrimaryBtn {
    background-color: #537A26;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 6px 13px;
    font-size: 12.5px;
    font-weight: 700;
}

QPushButton#CompactPrimaryBtn:hover {
    background-color: #638F2E;
}

QPushButton#ExportBundleBtn {
    background-color: #B91C1C;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 700;
}

QPushButton#ExportBundleBtn:hover {
    background-color: #DC2626;
}

QPushButton#ExportBtn {
    background-color: #EFF6E4;
    color: #3D5E18;
    border: 1px solid #B6CF8E;
    border-radius: 6px;
    padding: 7px 13px;
    font-weight: 600;
}

QPushButton#ExportBtn:hover {
    background-color: #DFECCB;
}

QPushButton#SmallGhostBtn {
    padding: 3px 8px;
    font-size: 12px;
    font-weight: 600;
    color: #334155;
}

QTabWidget::pane {
    border: 1px solid #C9D6B8;
    border-radius: 8px;
    background-color: #FFFFFF;
    top: -1px;
}

QTabBar::tab {
    background-color: #E3ECD4;
    color: #3F5232;
    border: 1px solid #C9D6B8;
    border-bottom: none;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 8px 14px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #3D5E18;
    font-weight: 700;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QFrame#TaskCard {
    background-color: #FFFFFF;
    border: 1px solid #C9D6B8;
    border-radius: 8px;
}

QFrame#ExportBar {
    background-color: #FFFFFF;
    border: 1px solid #C9D6B8;
    border-radius: 8px;
}

QFrame#PreviewToolbar {
    background-color: #F6F9F2;
    border-bottom: 1px solid #DCE6CE;
}

QTableWidget {
    background-color: #FFFFFF;
    alternate-background-color: #F8FAF5;
    color: #0F172A;
    gridline-color: #DCE6CE;
    border: 1px solid #C9D6B8;
    border-radius: 6px;
    selection-background-color: #E8F0D8;
    selection-color: #0F172A;
}

QHeaderView::section {
    background-color: #C5D9A4;
    color: #0F172A;
    font-weight: 700;
    padding: 5px 6px;
    border: none;
    border-right: 1px solid #AFC68B;
    border-bottom: 1px solid #9AB374;
}

QProgressBar {
    border: 1px solid #C5D9A4;
    border-radius: 4px;
    background-color: #F4F7F0;
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: #1E293B;
}

QProgressBar::chunk {
    background-color: #8EB659;
    border-radius: 3px;
}

QToolTip {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #475569;
    padding: 5px 8px;
    border-radius: 4px;
}
"""


DARK_STYLESHEET = """
QMainWindow, QWidget#RootWidget, QWidget#FormScrollBody, QWidget#CardsScrollBody {
    background-color: #0F172A;
    color: #E2E8F0;
    font-family: "Segoe UI", "DejaVu Sans", sans-serif;
    font-size: 13px;
}

QGroupBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 12px;
    padding: 14px 12px 10px 12px;
    font-weight: 600;
    color: #F1F5F9;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 6px;
    background-color: #1E293B;
    color: #A3E635;
    font-size: 13px;
    font-weight: 700;
}

QLabel {
    color: #E2E8F0;
    background-color: transparent;
}

QLabel#MutedLabel {
    color: #94A3B8;
    font-size: 12px;
}

QLabel#RedistributionBanner {
    background-color: #192B18;
    color: #BEF264;
    border: 1px solid #3F6212;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 11.5px;
    font-weight: 600;
}

QLabel#SummaryBadge {
    background-color: #1D3118;
    color: #D9F99D;
    border: 1px solid #4D7C0F;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 700;
    font-size: 13px;
}

QLabel#HeaderTitle {
    font-size: 16px;
    font-weight: 700;
    color: #ECFCCB;
}

QLabel#SheetStatusLabel {
    font-size: 13px;
    font-weight: 600;
    color: #F1F5F9;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: #0F172A;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 5px 8px;
    color: #F8FAFC;
    min-height: 22px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1.5px solid #84CC16;
    background-color: #131E35;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 1px solid #4D7C0F;
    selection-background-color: #2D4A1E;
    selection-color: #ECFCCB;
}

QCheckBox {
    spacing: 6px;
    color: #E2E8F0;
    padding: 2px 0px;
}

QCheckBox#AccentCheckBox {
    font-weight: 700;
    color: #A3E635;
}

QPushButton {
    background-color: #273549;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 12px;
    color: #F1F5F9;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #84CC16;
}

QPushButton:pressed {
    background-color: #1E293B;
}

QPushButton#PrimaryGenerateBtn {
    background-color: #5C8B29;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 11px 18px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#PrimaryGenerateBtn:hover {
    background-color: #6EA333;
}

QPushButton#PrimaryGenerateBtn:pressed {
    background-color: #466A1E;
}

QPushButton#CompactPrimaryBtn {
    background-color: #5C8B29;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 6px 13px;
    font-size: 12.5px;
    font-weight: 700;
}

QPushButton#CompactPrimaryBtn:hover {
    background-color: #6EA333;
}

QPushButton#ExportBundleBtn {
    background-color: #DC2626;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 700;
}

QPushButton#ExportBundleBtn:hover {
    background-color: #EF4444;
}

QPushButton#ExportBtn {
    background-color: #1D3118;
    color: #BEF264;
    border: 1px solid #4D7C0F;
    border-radius: 6px;
    padding: 7px 13px;
    font-weight: 600;
}

QPushButton#ExportBtn:hover {
    background-color: #284420;
}

QPushButton#SmallGhostBtn {
    padding: 3px 8px;
    font-size: 12px;
    font-weight: 600;
    color: #CBD5E1;
}

QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 8px;
    background-color: #1E293B;
    top: -1px;
}

QTabBar::tab {
    background-color: #152033;
    color: #94A3B8;
    border: 1px solid #334155;
    border-bottom: none;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 8px 14px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #1E293B;
    color: #A3E635;
    font-weight: 700;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QFrame#TaskCard {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
}

QFrame#ExportBar {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
}

QFrame#PreviewToolbar {
    background-color: #162235;
    border-bottom: 1px solid #334155;
}

QTableWidget {
    background-color: #1E293B;
    alternate-background-color: #172234;
    color: #E2E8F0;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 6px;
    selection-background-color: #2D4A1E;
    selection-color: #F8FAFC;
}

QTableCornerButton::section {
    background-color: #263A1B;
    border: none;
}

QHeaderView::section {
    background-color: #263A1B;
    color: #D9F99D;
    font-weight: 700;
    padding: 5px 6px;
    border: none;
    border-right: 1px solid #3F6212;
    border-bottom: 1px solid #4D7C0F;
}

QProgressBar {
    border: 1px solid #3F6212;
    border-radius: 4px;
    background-color: #0F172A;
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: #F8FAFC;
}

QProgressBar::chunk {
    background-color: #65A30D;
    border-radius: 3px;
}

QScrollBar:vertical {
    background: #162032;
    width: 10px;
    margin: 2px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #475569;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #64748B;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #162032;
    height: 10px;
    margin: 2px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #475569;
    min-width: 24px;
    border-radius: 5px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QMessageBox {
    background-color: #1E293B;
    color: #F1F5F9;
}

QToolTip {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #65A30D;
    padding: 5px 8px;
    border-radius: 4px;
}
"""

APP_STYLESHEET = LIGHT_STYLESHEET


def get_stylesheet(is_dark: bool) -> str:
    """Zwraca arkusz stylów QSS dla wybranego motywu (ciemnego lub jasnego)."""
    return DARK_STYLESHEET if is_dark else LIGHT_STYLESHEET


def detect_system_dark_mode(app: Optional[Any] = None) -> bool:
    """Wykrywa, czy system operacyjny ma aktywny motyw ciemny."""
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication
    except Exception:
        return False

    qapp = app or QApplication.instance()
    if qapp is None:
        return False
    try:
        hints = qapp.styleHints()
        if hasattr(hints, "colorScheme") and hasattr(Qt, "ColorScheme"):
            scheme = hints.colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                return True
            if scheme == Qt.ColorScheme.Light:
                return False
    except Exception:
        pass
    try:
        pal = qapp.palette()
        bg = pal.window().color()
        lum = 0.299 * bg.red() + 0.587 * bg.green() + 0.114 * bg.blue()
        return lum < 128
    except Exception:
        return False


def load_saved_theme_mode() -> str:
    """Odczytuje lokalnie zapisany wybór motywu ('system', 'light' lub 'dark')."""
    try:
        if _PREFS_PATH.is_file():
            data = json.loads(_PREFS_PATH.read_text(encoding="utf-8"))
            mode = str(data.get("theme_mode", "system"))
            if mode in ("system", "light", "dark"):
                return mode
    except Exception:
        pass
    return "system"


def save_theme_mode(mode: str) -> None:
    """Zapisuje wybór motywu lokalnie na dysku użytkownika."""
    if mode not in ("system", "light", "dark"):
        return
    try:
        _PREFS_PATH.write_text(json.dumps({"theme_mode": mode}, indent=2), encoding="utf-8")
    except Exception:
        pass
