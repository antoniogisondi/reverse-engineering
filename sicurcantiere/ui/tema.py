"""Tema grafico: tavolozza dei colori e foglio di stile Qt, chiaro e scuro."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class Colori:
    sfondo: str          # sfondo della finestra
    superficie: str      # pannelli, campi e tabelle
    superficie_alt: str  # righe alternate, intestazioni
    bordo: str
    testo: str
    testo_debole: str
    primario: str        # blu della barra laterale
    primario_testo: str
    accento: str         # arancio "cantiere"
    accento_hover: str
    selezione: str
    icone: str           # colore delle icone sulla superficie


CHIARO = Colori(
    sfondo="#F3F5F8", superficie="#FFFFFF", superficie_alt="#F6F8FB", bordo="#D5DBE3",
    testo="#1D2733", testo_debole="#5E6B7A", primario="#1F3A5F", primario_testo="#E8EEF5",
    accento="#E8792B", accento_hover="#D0661C", selezione="#DCE8F7", icone="#1F3A5F",
)
SCURO = Colori(
    sfondo="#171C23", superficie="#1F262F", superficie_alt="#252D37", bordo="#36414E",
    testo="#E4E9EF", testo_debole="#9AA7B5", primario="#111821", primario_testo="#C9D4E0",
    accento="#F08A3E", accento_hover="#F49D5C", selezione="#2D4A6E", icone="#C9D4E0",
)


def colori(scuro: bool) -> Colori:
    return SCURO if scuro else CHIARO


def _tavolozza(c: Colori) -> QPalette:
    p = QPalette()
    ruoli = {
        QPalette.ColorRole.Window: c.sfondo,
        QPalette.ColorRole.WindowText: c.testo,
        QPalette.ColorRole.Base: c.superficie,
        QPalette.ColorRole.AlternateBase: c.superficie_alt,
        QPalette.ColorRole.Text: c.testo,
        QPalette.ColorRole.Button: c.superficie,
        QPalette.ColorRole.ButtonText: c.testo,
        QPalette.ColorRole.ToolTipBase: c.superficie,
        QPalette.ColorRole.ToolTipText: c.testo,
        QPalette.ColorRole.PlaceholderText: c.testo_debole,
        QPalette.ColorRole.Highlight: c.selezione,
        QPalette.ColorRole.HighlightedText: c.testo,
        QPalette.ColorRole.Mid: c.bordo,
        QPalette.ColorRole.Link: c.accento,
    }
    for ruolo, colore in ruoli.items():
        p.setColor(ruolo, QColor(colore))
    for ruolo in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText, QPalette.ColorRole.ButtonText):
        p.setColor(QPalette.ColorGroup.Disabled, ruolo, QColor(c.testo_debole))
    return p


def foglio_di_stile(c: Colori) -> str:
    return f"""
    QWidget {{ font-size: 10pt; }}
    QMainWindow, QDialog {{ background: {c.sfondo}; }}

    /* Barra laterale */
    QListWidget#navigazione {{
        background: {c.primario}; color: {c.primario_testo}; border: none; border-radius: 0;
        padding-top: 8px; outline: 0;
    }}
    QListWidget#navigazione::item {{
        padding: 9px 10px; margin: 1px 8px; border-radius: 6px;
        border-left: 3px solid transparent;
    }}
    QListWidget#navigazione::item:hover {{ background: rgba(255, 255, 255, 0.08); }}
    QListWidget#navigazione::item:selected {{
        background: rgba(255, 255, 255, 0.14); color: #FFFFFF;
        border-left: 3px solid {c.accento};
    }}
    QLabel#marchio {{
        background: {c.primario}; color: #FFFFFF; font-size: 13pt; font-weight: 700;
        padding: 14px 16px 6px 16px;
    }}

    /* Barra degli strumenti e di stato */
    QToolBar {{
        background: {c.superficie}; border: none; border-bottom: 1px solid {c.bordo};
        spacing: 4px; padding: 4px 8px;
    }}
    QToolBar QToolButton {{ padding: 5px 8px; border-radius: 6px; color: {c.testo}; }}
    QToolBar QToolButton:hover {{ background: {c.superficie_alt}; }}
    QToolBar QToolButton:checked {{ background: {c.selezione}; }}
    QToolBar QToolButton:disabled {{ color: {c.testo_debole}; }}
    QToolBar::separator {{ background: {c.bordo}; width: 1px; margin: 6px 6px; }}
    QStatusBar {{ background: {c.superficie}; border-top: 1px solid {c.bordo}; color: {c.testo_debole}; }}
    QStatusBar QLabel {{ padding: 0 8px; }}
    QMenuBar {{ background: {c.superficie}; color: {c.testo}; }}
    QMenuBar::item:selected, QMenu::item:selected {{ background: {c.selezione}; }}
    QMenu {{ background: {c.superficie}; color: {c.testo}; border: 1px solid {c.bordo}; }}

    /* Titoli */
    QLabel#titoloPagina {{ font-size: 16pt; font-weight: 600; color: {c.testo}; padding: 2px 0 6px 0; }}
    QLabel#sottotitolo {{ color: {c.testo_debole}; }}
    QLabel#titoloGruppo {{ font-weight: 600; color: {c.accento}; padding: 10px 0 2px 0; }}

    /* Riquadri di riepilogo */
    QFrame#tessera {{
        background: {c.superficie}; border: 1px solid {c.bordo}; border-radius: 8px;
        border-left: 4px solid {c.bordo};
    }}
    QFrame#tessera[stato="ok"] {{ border-left-color: #27AE60; }}
    QFrame#tessera[stato="attenzione"] {{ border-left-color: #E6A23C; }}
    QFrame#tessera[stato="errore"] {{ border-left-color: #D93B30; }}
    QFrame#tessera[stato="neutro"] {{ border-left-color: {c.primario if c is CHIARO else c.selezione}; }}
    QLabel#tesseraTitolo {{ color: {c.testo_debole}; font-size: 8pt; font-weight: 600; }}
    QLabel#tesseraValore {{ color: {c.testo}; font-size: 15pt; font-weight: 600; }}
    QLabel#tesseraNota {{ color: {c.testo_debole}; font-size: 9pt; }}

    /* Schede dei cantieri recenti */
    QPushButton#schedaRecente {{
        background: {c.superficie}; border: 1px solid {c.bordo}; border-radius: 8px;
        padding: 12px 14px; text-align: left; color: {c.testo};
    }}
    QLabel#schedaTitolo {{ font-size: 11pt; font-weight: 600; color: {c.testo}; }}
    QPushButton#schedaRecente:hover {{ border: 1px solid {c.accento}; background: {c.superficie_alt}; }}

    /* Pulsanti */
    QPushButton {{
        background: {c.superficie}; color: {c.testo}; border: 1px solid {c.bordo};
        border-radius: 6px; padding: 6px 14px;
    }}
    QPushButton:hover {{ border-color: {c.accento}; }}
    QPushButton:pressed {{ background: {c.superficie_alt}; }}
    QPushButton:disabled {{ color: {c.testo_debole}; }}
    QPushButton[primario="true"] {{
        background: {c.accento}; color: #FFFFFF; border: 1px solid {c.accento}; font-weight: 600;
    }}
    QPushButton[primario="true"]:hover {{ background: {c.accento_hover}; }}

    /* Campi */
    QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {{
        background: {c.superficie}; color: {c.testo}; border: 1px solid {c.bordo};
        border-radius: 5px; padding: 4px 6px; selection-background-color: {c.selezione};
        selection-color: {c.testo};
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
    QDateEdit:focus, QComboBox:focus {{ border: 1px solid {c.accento}; }}
    /* Le frecce dei campi numerici non si integrano con il tema: si usano
       tastiera e rotellina. Nasconderle con setButtonSymbols(NoButtons)
       lascerebbe il campo vuoto (il testo verrebbe compresso a 1 pixel). */
    QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{ width: 0px; border: none; }}

    /* Tabelle ed elenchi */
    QTableWidget, QTreeWidget, QListWidget {{
        background: {c.superficie}; alternate-background-color: {c.superficie_alt};
        color: {c.testo}; border: 1px solid {c.bordo}; border-radius: 6px;
        gridline-color: {c.bordo}; selection-background-color: {c.selezione};
        selection-color: {c.testo};
    }}
    QHeaderView::section {{
        background: {c.superficie_alt}; color: {c.testo_debole}; font-weight: 600;
        border: none; border-bottom: 1px solid {c.bordo}; border-right: 1px solid {c.bordo};
        padding: 5px 6px;
    }}

    /* Riquadri e schede */
    QGroupBox {{
        background: {c.superficie}; border: 1px solid {c.bordo}; border-radius: 8px;
        margin-top: 14px; padding: 12px 8px 8px 8px; font-weight: 600; color: {c.testo};
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; color: {c.testo}; }}
    QTabWidget::pane {{ border: 1px solid {c.bordo}; border-radius: 6px; background: {c.superficie}; top: -1px; }}
    QTabBar::tab {{
        background: transparent; color: {c.testo_debole}; padding: 7px 14px;
        border-bottom: 2px solid transparent;
    }}
    QTabBar::tab:selected {{ color: {c.testo}; border-bottom: 2px solid {c.accento}; font-weight: 600; }}
    QTabBar::tab:hover {{ color: {c.testo}; }}
    QScrollArea {{ border: none; background: transparent; }}
    QSplitter::handle {{ background: transparent; }}
    QSplitter::handle:vertical {{ height: 8px; }}
    QToolTip {{ background: {c.superficie}; color: {c.testo}; border: 1px solid {c.bordo}; }}
    """


def applica(app: QApplication, scuro: bool = False) -> Colori:
    c = colori(scuro)
    app.setStyle("Fusion")
    app.setPalette(_tavolozza(c))
    app.setStyleSheet(foglio_di_stile(c))
    return c
