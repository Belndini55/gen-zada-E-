"""Arkusz stylów QSS dla aplikacji desktopowej PyQt6 w kolorystyce arkuszy CKE OMAP-100 (oliwkowa zieleń + czerwień CKE)."""

APP_STYLESHEET = """
QMainWindow, QWidget#RootWidget {
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

QCheckBox {
    spacing: 6px;
    color: #1E293B;
    padding: 2px 0px;
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
"""
