"""Arkusz stylów QSS dla aplikacji desktopowej PyQt6 (jasny, czytelny styl edukacyjny CKE)."""

APP_STYLESHEET = """
QMainWindow, QWidget#RootWidget {
    background-color: #F1F5F9;
    color: #0F172A;
    font-family: "Segoe UI", "DejaVu Sans", sans-serif;
    font-size: 13px;
}

QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
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
    color: #1E3A8A;
    font-size: 13px;
    font-weight: 700;
}

QLabel {
    color: #1E293B;
}

QLabel#MutedLabel {
    color: #64748B;
    font-size: 12px;
}

QLabel#SummaryBadge {
    background-color: #EFF6FF;
    color: #1E3A8A;
    border: 1px solid #BFDBFE;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 700;
    font-size: 13px;
}

QLabel#HeaderTitle {
    font-size: 16px;
    font-weight: 700;
    color: #0F172A;
}

QLabel#SheetStatusLabel {
    font-size: 13px;
    font-weight: 600;
    color: #334155;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 5px 8px;
    color: #0F172A;
    min-height: 22px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1.5px solid #2563EB;
    background-color: #FFFFFF;
}

QCheckBox {
    spacing: 7px;
    color: #1E293B;
    padding: 2px 0px;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 12px;
    color: #1E293B;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #F8FAFC;
    border-color: #94A3B8;
}

QPushButton:pressed {
    background-color: #E2E8F0;
}

QPushButton#PrimaryGenerateBtn {
    background-color: #1E3A8A;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 11px 18px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#PrimaryGenerateBtn:hover {
    background-color: #1D4ED8;
}

QPushButton#PrimaryGenerateBtn:pressed {
    background-color: #172554;
}

QPushButton#ExportBundleBtn {
    background-color: #0F766E;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 700;
}

QPushButton#ExportBundleBtn:hover {
    background-color: #0D9488;
}

QPushButton#ExportBtn {
    background-color: #EFF6FF;
    color: #1E3A8A;
    border: 1px solid #93C5FD;
    border-radius: 6px;
    padding: 7px 13px;
    font-weight: 600;
}

QPushButton#ExportBtn:hover {
    background-color: #DBEAFE;
}

QPushButton#SmallGhostBtn {
    padding: 3px 8px;
    font-size: 12px;
    font-weight: 600;
    color: #334155;
}

QTabWidget::pane {
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    background-color: #FFFFFF;
    top: -1px;
}

QTabBar::tab {
    background-color: #E2E8F0;
    color: #475569;
    border: 1px solid #CBD5E1;
    border-bottom: none;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 8px 16px;
    margin-right: 4px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #1E3A8A;
    font-weight: 700;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QFrame#TaskCard {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
}

QFrame#ExportBar {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
}

QFrame#PreviewToolbar {
    background-color: #F8FAFC;
    border-bottom: 1px solid #E2E8F0;
}
"""
