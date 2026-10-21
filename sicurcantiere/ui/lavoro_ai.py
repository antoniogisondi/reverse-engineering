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
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere.ai import (
    ANTHROPIC,
    AVANZATO,
    DEEPSEEK,
    FORNITORE_PREDEFINITO,
    FORNITORI,
    INTEGRATO,
    OPENAI,
    STANDARD,
    VARIABILI_AMBIENTE,
    AssistenteAI,
    ErroreAI,
    server_ai,
)

CHIAVE_FORNITORE = "ai/fornitore"
CHIAVE_ATTIVO = "ai/attivo"

# Dove il fornitore tratta i dati (dalle informative dei fornitori): da dire a chi attiva l'assistente.
SEDI = {
    DEEPSEEK: "in Cina, fuori dall'Unione europea",
    OPENAI: "negli Stati Uniti, fuori dall'Unione europea",
    ANTHROPIC: "negli Stati Uniti, fuori dall'Unione europea",
    INTEGRATO: ("passando dal server SicurCantiere: con il motore Standard il testo è elaborato da DeepSeek "
                "(in Cina, fuori dall'Unione europea), con l'Avanzato da Claude di Anthropic (negli Stati Uniti). "
                "Il credito si verifica qui sotto"),
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


def fornitori_disponibili() -> list[str]:
    """Fornitori da proporre: l'assistente incluso solo se il server SicurCantiere è attivo."""
    return [f for f in FORNITORI if f != INTEGRATO or server_ai()]


def fornitore_predefinito() -> str:
    return INTEGRATO if server_ai() else FORNITORE_PREDEFINITO


def codice_licenza() -> str:
    return impostazioni_comuni().value("licenza/codice", "", type=str)


def assistente() -> AssistenteAI:
    impostazioni = impostazioni_comuni()
    fornitore = impostazioni.value(CHIAVE_FORNITORE, fornitore_predefinito(), type=str)
    if fornitore not in fornitori_disponibili():
        fornitore = fornitore_predefinito()
    if fornitore == INTEGRATO:
        modello = impostazioni.value(_chiave_modello(INTEGRATO), STANDARD, type=str)
        return AssistenteAI(fornitore=INTEGRATO, api_key=codice_licenza() or None,
                            modello=modello if modello in (STANDARD, AVANZATO) else STANDARD)
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
        for chiave in fornitori_disponibili():
            self.fornitore.addItem(FORNITORI[chiave].nome, chiave)
        self.chiave = QLineEdit()
        self.chiave.setEchoMode(QLineEdit.EchoMode.Password)
        self.modello = QComboBox()
        self.modello.setEditable(True)
        self.modello.setToolTip("Si può anche scrivere il nome di un altro modello disponibile sull'account.")
        self._valori: dict[str, tuple[str, str]] = {}
        attuale = self.impostazioni.value(CHIAVE_FORNITORE, fornitore_predefinito(), type=str)
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
        self.credito = QLabel()
        self.credito.setWordWrap(True)
        verifica = QPushButton("Verifica il credito")
        verifica.clicked.connect(self._verifica_credito)
        riga_credito = QWidget()
        lay_credito = QHBoxLayout(riga_credito)
        lay_credito.setContentsMargins(0, 0, 0, 0)
        lay_credito.addWidget(self.credito, 1)
        lay_credito.addWidget(verifica)
        modulo = QFormLayout()
        self.modulo = modulo
        modulo.addRow("Fornitore", self.fornitore)
        modulo.addRow("Chiave API", self.chiave)
        modulo.addRow("Modello", self.modello)
        modulo.addRow("Credito AI", riga_credito)
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
        integrato = self._corrente == INTEGRATO
        self.modulo.setRowVisible(self.chiave, not integrato)
        self.modulo.setRowVisible(self.modulo.rowCount() - 1, integrato)
        self.modello.setEditable(not integrato)
        f = FORNITORI[self._corrente]
        if integrato:
            self.destinazione.setText(f"Incluso nella licenza, senza chiavi da inserire: i dati vanno {SEDI[INTEGRATO]}.")
            if not self.credito.text():
                self.credito.setText("Quota mensile secondo il piano della licenza.")
        else:
            self.destinazione.setText(f"I dati vanno a {f.nome}, che li elabora {SEDI.get(self._corrente, '')}.")

    def _verifica_credito(self) -> None:
        try:
            stato = credito_integrato()
        except ErroreAI as e:
            self.credito.setText(str(e))
            return
        c = stato.get("credito", {})
        self.credito.setText(
            f"Restano {c.get('residuo', 0) / 1e6:.2f} milioni di crediti (quota del mese {c.get('quota', 0) / 1e6:.1f} "
            f"milioni, usati {c.get('usati_mese', 0) / 1e6:.2f}; ricariche {c.get('extra', 0) / 1e6:.2f})."
            .replace(".", ","))

    def _carica_fornitore(self, fornitore: str) -> None:
        f = FORNITORI[fornitore]
        chiave, modello = self._valori.get(fornitore) or (
            self.impostazioni.value(_chiave_api(fornitore), "", type=str),
            self.impostazioni.value(_chiave_modello(fornitore), "", type=str) or f.modello_predefinito,
        )
        self.chiave.setText(chiave)
        if fornitore in VARIABILI_AMBIENTE:
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


def credito_integrato() -> dict[str, Any]:
    """Credito AI della licenza, chiesto al server SicurCantiere."""
    import json
    import urllib.error
    import urllib.request

    if not codice_licenza():
        raise ErroreAI("L'assistente incluso richiede una licenza: inserirla in Aiuto > Licenza.")
    richiesta = urllib.request.Request(f"{server_ai()}/api/ai/stato", method="POST",
                                       data=json.dumps({"licenza": codice_licenza()}).encode(),
                                       headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(richiesta, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            messaggio = json.loads(e.read().decode()).get("errore", "")
        except (ValueError, AttributeError):
            messaggio = ""
        raise ErroreAI(messaggio or f"Servizio SicurCantiere AI non disponibile ({e.code}).") from e
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        raise ErroreAI("Impossibile contattare il servizio SicurCantiere AI: controllare la connessione.") from e


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
