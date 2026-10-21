"""Integrazione dell'assistente AI nell'interfaccia: impostazioni ed esecuzione in background."""

from __future__ import annotations

import weakref
from typing import Any, Callable

from PySide6.QtCore import QCoreApplication, QObject, QRunnable, QSettings, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QCheckBox,
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

from sicurcantiere.ai import (
    ANTHROPIC,
    DEEPSEEK,
    FORNITORE_PREDEFINITO,
    FORNITORI,
    OPENAI,
    VARIABILI_AMBIENTE,
    AssistenteAI,
    ErroreAI,
)

CHIAVE_FORNITORE = "ai/fornitore"
CHIAVE_ATTIVO = "ai/attivo"

# Dove il fornitore tratta i dati (dalle informative dei fornitori): da dire a chi attiva l'assistente.
SEDI = {
    DEEPSEEK: "in Cina, fuori dall'Unione europea",
    OPENAI: "negli Stati Uniti, fuori dall'Unione europea",
    ANTHROPIC: "negli Stati Uniti, fuori dall'Unione europea",
}

DATI_INVIATI = (
    "<b>Cosa viene inviato</b>, solo quando premi un pulsante dell'assistente:"
    "<ul><li>le descrizioni di lavorazioni, rischi, macchine e attrezzature;</li>"
    "<li>i dati generali dell'opera (natura, comune, importo, descrizione) e i testi del POS di cui chiedi la bozza;</li>"
    "<li>la descrizione dell'attività da valutare;</li>"
    "<li>il testo della scheda di sicurezza che importi.</li></ul>"
    "<b>Cosa non viene inviato</b>: nomi, dati e idoneità dei lavoratori, nominativi di committente, "
    "coordinatori e imprese, indirizzo del cantiere. Non scrivere dati personali nelle descrizioni."
)

# Pulsanti dell'assistente, nascosti quando è spento.
_pulsanti_ai: "weakref.WeakSet[QWidget]" = weakref.WeakSet()


def ai_attiva() -> bool:
    """Assistente spento di serie; acceso se l'utente lo ha attivato (o aveva già una chiave salvata)."""
    impostazioni = impostazioni_comuni()
    valore = impostazioni.value(CHIAVE_ATTIVO, None)
    if valore is None:
        return any(impostazioni.value(_chiave_api(f), "", type=str) for f in FORNITORI)
    return str(valore).lower() in ("1", "true")


def registra_pulsante_ai(pulsante: QWidget) -> None:
    _pulsanti_ai.add(pulsante)
    pulsante.setVisible(ai_attiva())


def aggiorna_pulsanti_ai() -> None:
    attiva = ai_attiva()
    for pulsante in list(_pulsanti_ai):
        pulsante.setVisible(attiva)


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

        self.attiva = QCheckBox("Usa l'assistente AI")
        self.attiva.setChecked(ai_attiva())
        self.attiva.toggled.connect(self._mostra_stato)
        spiegazione = QLabel("L'assistente è spento di serie: finché non lo attivi, i suoi pulsanti non compaiono "
                             "e nessun dato lascia questo computer.")
        spiegazione.setWordWrap(True)
        spiegazione.setObjectName("hint")
        self.destinazione = QLabel()
        self.destinazione.setWordWrap(True)
        self.destinazione.setObjectName("warningMessage")
        dati = QLabel(DATI_INVIATI)
        dati.setWordWrap(True)
        nota = QLabel("L'assistente propone valori e testi che vanno sempre verificati prima dell'uso. "
                      "Le chiavi vengono salvate nelle impostazioni di questo computer.")
        nota.setWordWrap(True)
        nota.setObjectName("hint")
        modulo = QFormLayout()
        modulo.addRow("Fornitore", self.fornitore)
        modulo.addRow("Chiave API", self.chiave)
        modulo.addRow("Modello", self.modello)
        self.campi_ai = QWidget()
        lay_campi = QVBoxLayout(self.campi_ai)
        lay_campi.setContentsMargins(0, 0, 0, 0)
        lay_campi.addLayout(modulo)
        lay_campi.addWidget(self.destinazione)
        lay_campi.addWidget(dati)
        lay_campi.addWidget(nota)
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.accepted.connect(self._salva)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.attiva)
        layout.addWidget(spiegazione)
        layout.addWidget(self.campi_ai)
        layout.addWidget(pulsanti)
        self._mostra_stato()

    def _mostra_stato(self) -> None:
        self.campi_ai.setEnabled(self.attiva.isChecked())
        f = FORNITORI[self._corrente]
        self.destinazione.setText(f"I dati vanno a {f.nome}, che li elabora {SEDI.get(self._corrente, '')}.")

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
        self._mostra_stato()

    def _salva(self) -> None:
        self._valori[self._corrente] = (self.chiave.text().strip(), self._modello_scelto())
        for fornitore, (chiave, modello) in self._valori.items():
            self.impostazioni.setValue(_chiave_api(fornitore), chiave)
            self.impostazioni.setValue(_chiave_modello(fornitore), modello)
        self.impostazioni.setValue(CHIAVE_FORNITORE, self._corrente)
        self.impostazioni.setValue(CHIAVE_ATTIVO, self.attiva.isChecked())
        aggiorna_pulsanti_ai()
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
    if not ai_attiva():
        QMessageBox.information(genitore, "Assistente AI", "L'assistente AI non è attivo: si attiva da "
                                "Strumenti > Impostazioni assistente AI, dove è spiegato quali dati vengono inviati.")
        return
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
