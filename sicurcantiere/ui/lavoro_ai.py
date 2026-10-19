"""Integrazione dell'assistente AI nell'interfaccia: impostazioni ed esecuzione in background."""

from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import QCoreApplication, QObject, QRunnable, QSettings, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressDialog,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere.ai import ANTHROPIC, FORNITORE_PREDEFINITO, FORNITORI, OPENAI, AssistenteAI, ErroreAI

CHIAVE_FORNITORE = "ai/fornitore"
VARIABILI_AMBIENTE = {OPENAI: "OPENAI_API_KEY", ANTHROPIC: "ANTHROPIC_API_KEY"}


def impostazioni_comuni() -> QSettings:
    """Impostazioni condivise da tutti i programmi SicurCantiere (la chiave si inserisce una volta)."""
    return QSettings(QCoreApplication.organizationName() or "SicurCantiere", "Comune")


def _chiave_api(fornitore: str) -> str:
    return f"ai/{fornitore}/chiave"


def _chiave_modello(fornitore: str) -> str:
    return f"ai/{fornitore}/modello"


def assistente() -> AssistenteAI:
    impostazioni = impostazioni_comuni()
    fornitore = impostazioni.value(CHIAVE_FORNITORE, FORNITORE_PREDEFINITO, type=str)
    if fornitore not in FORNITORI:
        fornitore = FORNITORE_PREDEFINITO
    return AssistenteAI(
        fornitore=fornitore,
        api_key=impostazioni.value(_chiave_api(fornitore), "", type=str) or None,
        modello=impostazioni.value(_chiave_modello(fornitore), "", type=str) or None,
    )


class DialogoImpostazioniAI(QDialog):
    def __init__(self, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.setWindowTitle("Impostazioni dell'assistente AI")
        self.setMinimumWidth(560)
        self.impostazioni = impostazioni_comuni()
        self.fornitore = QComboBox()
        for chiave, f in FORNITORI.items():
            self.fornitore.addItem(f.nome, chiave)
        self.chiave = QLineEdit()
        self.chiave.setEchoMode(QLineEdit.EchoMode.Password)
        self.modello = QComboBox()
        self.modello.setEditable(True)
        self.modello.setToolTip("Si può anche scrivere il nome di un altro modello disponibile sull'account.")
        self._valori: dict[str, tuple[str, str]] = {}
        attuale = self.impostazioni.value(CHIAVE_FORNITORE, FORNITORE_PREDEFINITO, type=str)
        self.fornitore.setCurrentIndex(max(self.fornitore.findData(attuale), 0))
        self._corrente = self.fornitore.currentData()
        self._carica_fornitore(self._corrente)
        self.fornitore.currentIndexChanged.connect(self._cambia_fornitore)

        nota = QLabel(
            "L'assistente propone valori e testi che vanno sempre verificati prima dell'uso. "
            "Le descrizioni inviate vengono elaborate dal fornitore scelto: non inserire dati "
            "personali non necessari. Le chiavi vengono salvate nelle impostazioni di questo computer."
        )
        nota.setWordWrap(True)
        nota.setObjectName("sottotitolo")
        modulo = QFormLayout()
        modulo.addRow("Fornitore", self.fornitore)
        modulo.addRow("Chiave API", self.chiave)
        modulo.addRow("Modello", self.modello)
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.accepted.connect(self._salva)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(modulo)
        layout.addWidget(nota)
        layout.addWidget(pulsanti)

    def _carica_fornitore(self, fornitore: str) -> None:
        f = FORNITORI[fornitore]
        chiave, modello = self._valori.get(fornitore) or (
            self.impostazioni.value(_chiave_api(fornitore), "", type=str),
            self.impostazioni.value(_chiave_modello(fornitore), "", type=str) or f.modello_predefinito,
        )
        self.chiave.setText(chiave)
        self.chiave.setPlaceholderText(f"Vuoto: usa la variabile d'ambiente {VARIABILI_AMBIENTE[fornitore]}")
        self.modello.clear()
        for valore, nome in f.modelli:
            self.modello.addItem(nome, valore)
        indice = self.modello.findData(modello)
        if indice >= 0:
            self.modello.setCurrentIndex(indice)
        else:
            self.modello.setEditText(modello)

    def _modello_scelto(self) -> str:
        indice = self.modello.findText(self.modello.currentText())
        return self.modello.itemData(indice) if indice >= 0 else self.modello.currentText().strip()

    def _cambia_fornitore(self) -> None:
        self._valori[self._corrente] = (self.chiave.text().strip(), self._modello_scelto())
        self._corrente = self.fornitore.currentData()
        self._carica_fornitore(self._corrente)

    def _salva(self) -> None:
        self._valori[self._corrente] = (self.chiave.text().strip(), self._modello_scelto())
        for fornitore, (chiave, modello) in self._valori.items():
            self.impostazioni.setValue(_chiave_api(fornitore), chiave)
            self.impostazioni.setValue(_chiave_modello(fornitore), modello)
        self.impostazioni.setValue(CHIAVE_FORNITORE, self._corrente)
        self.accept()


class _Segnali(QObject):
    completato = Signal(object)
    fallito = Signal(str)


class _Lavoro(QRunnable):
    def __init__(self, funzione: Callable[[], Any]):
        super().__init__()
        self.funzione = funzione
        self.segnali = _Segnali()

    def run(self) -> None:
        try:
            risultato = self.funzione()
        except ErroreAI as e:
            self.segnali.fallito.emit(str(e))
        except Exception as e:  # noqa: BLE001 - qualsiasi errore va mostrato all'utente
            self.segnali.fallito.emit(f"Errore imprevisto: {e}")
        else:
            self.segnali.completato.emit(risultato)


# Riferimenti ai lavori in corso, per evitare che vengano distrutti prima del termine.
_in_corso: set[_Lavoro] = set()


def esegui_ai(genitore: QWidget, messaggio: str, funzione: Callable[[AssistenteAI], Any],
              al_termine: Callable[[Any], None]) -> None:
    """Esegue `funzione(assistente)` in un thread separato mostrando un'attesa."""
    attesa = QProgressDialog(messaggio, "", 0, 0, genitore)
    attesa.setWindowTitle("Assistente AI")
    attesa.setCancelButton(None)
    attesa.setWindowModality(Qt.WindowModality.WindowModal)
    attesa.setMinimumDuration(0)
    attesa.show()

    ai = assistente()
    lavoro = _Lavoro(lambda: funzione(ai))
    _in_corso.add(lavoro)

    def fine() -> None:
        attesa.close()
        _in_corso.discard(lavoro)

    def ok(risultato: Any) -> None:
        fine()
        al_termine(risultato)

    def errore(testo: str) -> None:
        fine()
        QMessageBox.warning(genitore, "Assistente AI", testo)

    # Connessioni accodate: i segnali partono dal thread di lavoro, ma "segnali"
    # appartiene al thread principale, dove vengono quindi eseguite ok/errore.
    lavoro.segnali.completato.connect(ok, Qt.ConnectionType.QueuedConnection)
    lavoro.segnali.fallito.connect(errore, Qt.ConnectionType.QueuedConnection)
    QThreadPool.globalInstance().start(lavoro)
