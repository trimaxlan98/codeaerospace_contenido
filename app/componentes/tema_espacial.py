"""Tema visual espacial de la app (mismo lenguaje que las presentaciones: fondo #0a0e27, cian #00d9ff, Rajdhani / DM Sans / Space Mono)."""
from PySide6.QtGui import QFont, QFontDatabase

FONDO, PANEL, BORDE, TINTA, TENUE, ACENTO, ACENTO2, AMBAR = "#0a0e27", "#10183a", "#1f2c5c", "#E8EEF8", "#8FA1BF", "#00D9FF", "#37CFA0", "#F59E0B"

QSS = f"""
* {{ font-family: "DM Sans", "Inter", sans-serif; font-size: 14px; color: {TINTA}; }}
QMainWindow, QWidget#raiz, QDialog {{ background: {FONDO}; }}
QTabWidget::pane {{ border: 1px solid {BORDE}; border-radius: 10px; background: {FONDO}; top: -1px; }}
QTabBar::tab {{ font-family: "Rajdhani"; font-weight: 700; font-size: 17px; letter-spacing: 1px; padding: 8px 22px;
  background: transparent; color: {TENUE}; border: 1px solid transparent; border-bottom: 2px solid transparent; }}
QTabBar::tab:selected {{ color: {ACENTO}; border-bottom: 2px solid {ACENTO}; }}
QTabBar::tab:hover {{ color: {TINTA}; }}
QLabel#titulo {{ font-family: "Rajdhani"; font-size: 26px; font-weight: 700; letter-spacing: 1px; }}
QLabel#seccion {{ font-family: "Space Mono"; font-size: 11px; color: {ACENTO}; letter-spacing: 2px; }}
QLabel#nota {{ color: {TENUE}; font-size: 12px; }}
QLabel#ok {{ color: {ACENTO2}; font-size: 12px; }}
QLabel#aviso {{ color: {AMBAR}; font-size: 12px; }}
QGroupBox {{ border: 1px solid {BORDE}; border-radius: 10px; margin-top: 14px; padding: 14px 10px 10px 10px; background: {PANEL}; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 14px; padding: 0 6px; color: {ACENTO}; font-family: "Space Mono"; font-size: 11px; letter-spacing: 2px; }}
QPushButton {{ font-family: "Rajdhani"; font-weight: 700; font-size: 16px; letter-spacing: 1px; padding: 8px 18px;
  background: {PANEL}; border: 1px solid {ACENTO}; border-radius: 8px; color: {ACENTO}; }}
QPushButton:hover {{ background: {ACENTO}; color: {FONDO}; }}
QPushButton:disabled {{ border-color: {BORDE}; color: {TENUE}; background: transparent; }}
QPushButton#primario {{ background: {ACENTO}; color: {FONDO}; }}
QPushButton#primario:hover {{ background: #5CE8FF; }}
QPushButton#primario:disabled {{ background: {BORDE}; color: {TENUE}; }}
QComboBox, QLineEdit, QSpinBox {{ background: {FONDO}; border: 1px solid {BORDE}; border-radius: 6px; padding: 6px 10px; selection-background-color: {ACENTO}; selection-color: {FONDO}; }}
QComboBox:hover, QLineEdit:focus {{ border-color: {ACENTO}; }}
QComboBox QAbstractItemView {{ background: {PANEL}; border: 1px solid {BORDE}; selection-background-color: {ACENTO}; selection-color: {FONDO}; }}
QListWidget {{ background: {FONDO}; border: 1px solid {BORDE}; border-radius: 8px; padding: 4px; outline: 0; }}
QListWidget::item {{ padding: 8px 6px; border-radius: 6px; }}
QListWidget::item:selected {{ background: {BORDE}; color: {TINTA}; }}
QListWidget::item:hover {{ background: #16214a; }}
QPlainTextEdit {{ font-family: "Space Mono", "DejaVu Sans Mono"; font-size: 11px; background: #060922; border: 1px solid {BORDE}; border-radius: 8px; color: #B8C7E0; }}
QRadioButton, QCheckBox {{ spacing: 8px; }}
QRadioButton::indicator, QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid #4a5c99; background: {FONDO}; }}
QRadioButton::indicator {{ border-radius: 9px; }} QCheckBox::indicator {{ border-radius: 4px; }}
QRadioButton::indicator:checked, QCheckBox::indicator:checked {{ background: {ACENTO}; border-color: {ACENTO}; }}
QListWidget::indicator {{ width: 16px; height: 16px; border: 1px solid #4a5c99; border-radius: 4px; background: {FONDO}; }}
QListWidget::indicator:checked {{ background: {ACENTO}; border-color: {ACENTO}; }}
QSlider::groove:horizontal {{ height: 6px; border-radius: 3px; background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #ff3c6e,stop:0.17 #ffb020,stop:0.33 #c6f24a,stop:0.5 #37cfa0,stop:0.67 #00d9ff,stop:0.83 #a78bfa,stop:1 #ff3c6e); }}
QSlider::handle:horizontal {{ width: 18px; height: 18px; margin: -7px 0; border-radius: 9px; background: {TINTA}; border: 2px solid {FONDO}; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }} QScrollBar::handle:vertical {{ background: {BORDE}; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
"""


def aplicar(app):
    """Carga el estilo y deja DM Sans como fuente base (si no está instalada Qt usa la de respaldo)."""
    app.setStyleSheet(QSS)
    if "DM Sans" in QFontDatabase.families():
        app.setFont(QFont("DM Sans", 10))


def fuentes_faltantes(nombres):
    """Fuentes de `nombres` que no están instaladas (para avisar antes de abrir el .pptx)."""
    inst = set(QFontDatabase.families())
    return sorted(n for n in set(nombres) if n not in inst)
