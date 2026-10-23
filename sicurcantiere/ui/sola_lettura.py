"""Sola lettura: cantiere consultabile, stampabile ed esportabile, ma non modificabile.

Con la licenza non valida (scaduta, revocata, non attivata su questo PC...) i dati dell'utente restano
sempre accessibili: il cantiere si apre da una copia temporanea, così il file originale non può
cambiare in nessun caso, e i campi della pagina diventano non modificabili. Restano utilizzabili la
navigazione, la ricerca, i controlli e, per i documenti già composti, l'apertura in Word, l'anteprima e
l'esportazione in PDF (i pulsanti con la proprietà «solaLettura» a True).
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QLineEdit,
    QPlainTextEdit,
    QRadioButton,
    QTabBar,
    QTextEdit,
    QWidget,
)

CONSENTITO = "solaLettura"
# pulsanti che cambiano solo la vista (filtri degli elenchi, Elenco/Cronoprogramma): restano attivi
NOMI_CONSENTITI = {"filterChip", "segment"}

_attiva = False


def attiva() -> bool:
    """La finestra mostra un cantiere in sola lettura (lo leggono i pannelli con azioni sui documenti)."""
    return _attiva


def imposta(valore: bool) -> None:
    global _attiva
    _attiva = valore


def consenti(*widget) -> None:
    """Segna i pulsanti che restano attivi in sola lettura (aprire, vedere, esportare)."""
    for w in widget:
        w.setProperty(CONSENTITO, True)


def _consentito(w: QWidget) -> bool:
    if w.property(CONSENTITO) or w.objectName() in NOMI_CONSENTITI:
        return True
    genitore = w.parentWidget()  # frecce delle schede e parti interne dei campi numerici
    return isinstance(genitore, (QTabBar, QAbstractSpinBox))


def applica(radice: QWidget) -> None:
    """Rende non modificabili i campi sotto `radice` (si può ripetere: i pulsanti riattivati dalle pagine
    tornano disattivati)."""
    for w in radice.findChildren(QWidget):
        if isinstance(w, QTabBar) or _consentito(w):
            continue
        if isinstance(w, (QLineEdit, QTextEdit, QPlainTextEdit)):
            if not w.isReadOnly():
                w.setReadOnly(True)
        elif isinstance(w, QAbstractSpinBox) and not isinstance(w, QDateEdit):
            w.setReadOnly(True)
        elif isinstance(w, QAbstractItemView):
            w.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            w.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        elif isinstance(w, (QComboBox, QDateEdit, QCheckBox, QRadioButton)):
            if w.isEnabled():
                w.setEnabled(False)
        elif isinstance(w, QAbstractButton):
            if w.isEnabled():
                w.setEnabled(False)
