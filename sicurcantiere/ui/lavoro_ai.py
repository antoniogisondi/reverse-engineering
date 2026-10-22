"""Integrazione dell'assistente AI nell'interfaccia: impostazioni ed esecuzione in background.

L'assistente è incluso nella licenza e passa dal server SicurCantiere (nessuna chiave API sul PC):
senza una licenza valida non è disponibile e i suoi pulsanti non compaiono.
"""

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
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import licenza
from sicurcantiere.ai import AVANZATO, FORNITORI, INTEGRATO, STANDARD, AssistenteAI, ErroreAI, server_ai

CHIAVE_ATTIVO = "ai/attivo"
CHIAVE_MOTORE = "ai/motore"
NOME = FORNITORI[INTEGRATO].nome

# Dove viene elaborato il testo. La sede vera la dice il server SicurCantiere (riga SEDE di ai.env, così
# cambiando fornitore non serve una nuova versione del programma): si chiede con `aggiorna_sedi` e si
# ricorda l'ultima ricevuta. Questi testi valgono solo finché il server non ha mai risposto.
SEDI = {
    STANDARD: "il fornitore del motore Standard indicato dal server SicurCantiere",
    AVANZATO: "Claude di Anthropic, negli Stati Uniti (fuori dall'Unione europea)",
}
CHIAVE_SEDE = "ai/sede/"


def sede(nome_motore: str) -> str:
    """Dove viene elaborato il testo con il motore indicato: l'ultima sede comunicata dal server."""
    ricevuta = impostazioni_comuni().value(CHIAVE_SEDE + nome_motore, "", type=str)
    return ricevuta or SEDI.get(nome_motore, SEDI[STANDARD])


def _ricorda_sedi(stato: dict[str, Any]) -> None:
    impostazioni = impostazioni_comuni()
    for nome_motore, dati in (stato.get("motori") or {}).items():
        if isinstance(dati, dict) and str(dati.get("sede") or "").strip():
            impostazioni.setValue(CHIAVE_SEDE + nome_motore, str(dati["sede"]).strip())


def aggiorna_sedi() -> bool:
    """Chiede al server dove elabora i testi ogni motore (senza mostrare errori: resta l'ultima nota)."""
    if not server_ai() or not codice_licenza():
        return False
    try:
        credito_integrato()
    except Exception:  # noqa: BLE001 - senza risposta resta la sede già nota
        return False
    return True

DATI_INVIATI = (
    "<b>Dati inviati</b>, solo quando premi un pulsante dell'assistente:"
    "<ul><li>le descrizioni di lavorazioni, rischi, macchine e attrezzature;</li>"
    "<li>i dati generali dell'opera (natura, comune, importo, descrizione) e i testi del POS di cui chiedi la bozza;</li>"
    "<li>la descrizione dell'attività da valutare;</li>"
    "<li>il testo della scheda di sicurezza o del PSC che importi;</li>"
    "<li>il codice di licenza, per il controllo del credito.</li></ul>"
    "<b>Dati non inviati</b>: nomi, dati e idoneità dei lavoratori, nominativi di committente, "
    "coordinatori e imprese, indirizzo del cantiere (salvo quelli scritti nel PSC che importi). "
    "Non scrivere dati personali nelle descrizioni."
)

# Pulsanti dell'assistente, nascosti quando non è disponibile o è spento.
_pulsanti_ai: "weakref.WeakSet[QWidget]" = weakref.WeakSet()


def impostazioni_comuni() -> QSettings:
    """Impostazioni condivise da tutti i programmi SicurCantiere."""
    return QSettings(QCoreApplication.organizationName() or "SicurCantiere", "Comune")


def codice_licenza() -> str:
    return impostazioni_comuni().value("licenza/codice", "", type=str)


def licenza_ai() -> licenza.Licenza | None:
    """La licenza che dà diritto all'assistente: valida e non scaduta (altrimenti None)."""
    try:
        l = licenza.leggi(codice_licenza())
    except (licenza.ErroreLicenza, ValueError):
        return None
    return None if l.scaduta() else l


def ai_disponibile() -> bool:
    """L'assistente c'è: licenza valida e server SicurCantiere configurato."""
    return bool(server_ai()) and licenza_ai() is not None


def ai_attiva() -> bool:
    """Assistente disponibile e acceso dall'utente (spento di serie)."""
    _togli_chiavi_vecchie()
    valore = impostazioni_comuni().value(CHIAVE_ATTIVO, None)
    return ai_disponibile() and str(valore).lower() in ("1", "true")


def _togli_chiavi_vecchie() -> None:
    """Le chiavi API delle versioni precedenti non servono più: si cancellano da questo PC."""
    impostazioni = impostazioni_comuni()
    for fornitore in FORNITORI:
        for voce in (f"ai/{fornitore}/chiave", f"ai/{fornitore}/modello"):
            if impostazioni.contains(voce):
                impostazioni.remove(voce)
    if impostazioni.contains("ai/fornitore"):
        impostazioni.remove("ai/fornitore")


def _mostra_pulsante_ai(pulsante: QWidget, attiva: bool) -> None:
    if pulsante.parentWidget() is None:
        # Un pulsante non ancora inserito nella pagina, se mostrato, diventa una
        # finestra a sé che compare e sparisce: qui si decide solo se seguirà la
        # pagina (che lo mostrerà insieme a sé) o se resterà nascosto.
        pulsante.setAttribute(Qt.WidgetAttribute.WA_WState_ExplicitShowHide, not attiva)
        pulsante.setAttribute(Qt.WidgetAttribute.WA_WState_Hidden, True)
    else:
        pulsante.setVisible(attiva)


def registra_pulsante_ai(pulsante: QWidget) -> None:
    _pulsanti_ai.add(pulsante)
    _mostra_pulsante_ai(pulsante, ai_attiva())


def aggiorna_pulsanti_ai() -> None:
    attiva = ai_attiva()
    for pulsante in list(_pulsanti_ai):
        _mostra_pulsante_ai(pulsante, attiva)


def motore() -> str:
    """Motore scelto; l'avanzato solo con il piano Studio."""
    scelto = impostazioni_comuni().value(CHIAVE_MOTORE, STANDARD, type=str)
    l = licenza_ai()
    return AVANZATO if scelto == AVANZATO and l is not None and l.piano == "studio" else STANDARD


def assistente() -> AssistenteAI:
    return AssistenteAI(fornitore=INTEGRATO, api_key=codice_licenza() or None, modello=motore())


def perche_non_disponibile() -> str:
    if licenza_ai() is None:
        return ("L'assistente AI è incluso nella licenza e si usa senza chiavi né account: per attivarlo "
                "inserisci una licenza valida in «Aiuto > Licenza».")
    if not server_ai():
        return "L'assistente AI non è ancora disponibile in questa versione del programma."
    return ("L'assistente AI è disattivato: puoi attivarlo da «Strumenti > Impostazioni assistente AI», dove "
            "sono indicati i dati che vengono inviati.")


class DialogoImpostazioniAI(QDialog):
    """Accensione dell'assistente incluso nella licenza, scelta del motore e credito."""

    def __init__(self, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.setWindowTitle("Impostazioni dell'assistente AI")
        self.setMinimumWidth(560)
        self.impostazioni = impostazioni_comuni()
        disponibile = ai_disponibile()
        l = licenza_ai()

        self.attiva = QCheckBox("Usa l'assistente AI")
        self.attiva.setChecked(ai_attiva())
        self.attiva.setEnabled(disponibile)
        self.attiva.toggled.connect(self._mostra_stato)
        spiegazione = QLabel(
            "L'assistente è incluso nella licenza, senza chiavi né account da creare, con un credito mensile "
            "stabilito dal piano. È disattivato per impostazione predefinita: finché non lo attivi, i suoi "
            "pulsanti non compaiono e nessun dato lascia questo computer." if disponibile else perche_non_disponibile())
        spiegazione.setWordWrap(True)
        spiegazione.setObjectName("hint")

        self.motore = QComboBox()
        self.motore.addItem("Standard", STANDARD)
        if l is not None and l.piano == "studio":
            self.motore.addItem("Avanzato, con Claude (consuma 8 crediti per token)", AVANZATO)
        self.motore.setCurrentIndex(max(self.motore.findData(motore()), 0))
        self.motore.currentIndexChanged.connect(self._mostra_stato)
        self.credito = QLabel("Credito mensile stabilito dal piano della licenza.")
        self.credito.setWordWrap(True)
        verifica = QPushButton("Verifica il credito")
        verifica.clicked.connect(self._verifica_credito)
        riga_credito = QWidget()
        lay_credito = QHBoxLayout(riga_credito)
        lay_credito.setContentsMargins(0, 0, 0, 0)
        lay_credito.addWidget(self.credito, 1)
        lay_credito.addWidget(verifica)
        self.destinazione = QLabel()
        self.destinazione.setWordWrap(True)
        self.destinazione.setObjectName("warningMessage")
        dati = QLabel(DATI_INVIATI)
        dati.setWordWrap(True)
        nota = QLabel("L'assistente propone valori e testi che vanno sempre verificati prima dell'uso.")
        nota.setWordWrap(True)
        nota.setObjectName("hint")
        modulo = QFormLayout()
        modulo.addRow("Motore", self.motore)
        modulo.addRow("Credito AI", riga_credito)
        self.campi_ai = QWidget()
        lay_campi = QVBoxLayout(self.campi_ai)
        lay_campi.setContentsMargins(0, 0, 0, 0)
        lay_campi.addLayout(modulo)
        lay_campi.addWidget(self.destinazione)
        lay_campi.addWidget(dati)
        lay_campi.addWidget(nota)
        self.campi_ai.setVisible(disponibile)
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.button(QDialogButtonBox.StandardButton.Save).setEnabled(disponibile)
        pulsanti.accepted.connect(self._salva)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.attiva)
        layout.addWidget(spiegazione)
        layout.addWidget(self.campi_ai)
        layout.addWidget(pulsanti)
        self._mostra_stato()
        if disponibile:
            in_sottofondo(aggiorna_sedi, lambda _: self._mostra_stato())

    def _mostra_stato(self) -> None:
        self.campi_ai.setEnabled(self.attiva.isChecked())
        scelto = self.motore.currentData() or STANDARD
        self.destinazione.setText(f"I dati passano dal server SicurCantiere e sono elaborati da {sede(scelto)}.")

    def _verifica_credito(self) -> None:
        try:
            stato = credito_integrato()
        except ErroreAI as e:
            self.credito.setText(str(e))
            return
        self._mostra_stato()  # la sede appena comunicata dal server
        c = stato.get("credito", {})
        self.credito.setText(
            f"Restano {c.get('residuo', 0) / 1e6:.2f} milioni di crediti (quota del mese {c.get('quota', 0) / 1e6:.1f} "
            f"milioni, usati {c.get('usati_mese', 0) / 1e6:.2f}; ricariche {c.get('extra', 0) / 1e6:.2f})."
            .replace(".", ","))

    def _salva(self) -> None:
        self.impostazioni.setValue(CHIAVE_ATTIVO, self.attiva.isChecked())
        self.impostazioni.setValue(CHIAVE_MOTORE, self.motore.currentData() or STANDARD)
        aggiorna_pulsanti_ai()
        self.accept()


def credito_integrato() -> dict[str, Any]:
    """Credito AI della licenza, chiesto al server SicurCantiere."""
    import json
    import urllib.error
    import urllib.request

    if not codice_licenza():
        raise ErroreAI("L'assistente AI richiede una licenza: inseriscila in «Aiuto > Licenza».")
    richiesta = urllib.request.Request(f"{server_ai()}/api/ai/stato", method="POST",
                                       data=json.dumps({"licenza": codice_licenza()}).encode(),
                                       headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(richiesta, timeout=15) as r:
            stato = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            messaggio = json.loads(e.read().decode()).get("errore", "")
        except (ValueError, AttributeError):
            messaggio = ""
        raise ErroreAI(messaggio or f"Servizio SicurCantiere AI non disponibile ({e.code}).") from e
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        raise ErroreAI("Impossibile contattare il servizio SicurCantiere AI: verifica la connessione a "
                       "Internet.") from e
    _ricorda_sedi(stato)
    return stato


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
        QMessageBox.information(genitore, "Assistente AI", perche_non_disponibile())
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


def in_sottofondo(funzione: Callable[[], Any], al_termine: Callable[[Any], None] | None = None) -> None:
    """Esegue `funzione` in un thread separato, senza attesa né messaggi di errore."""
    lavoro = _Lavoro(funzione)
    _in_corso.add(lavoro)

    def fine(risultato: Any = None) -> None:
        _in_corso.discard(lavoro)
        if al_termine is not None and risultato is not None:
            try:
                al_termine(risultato)
            except RuntimeError:
                pass  # la finestra che aspettava il risultato è già chiusa

    lavoro.segnali.completato.connect(fine)
    lavoro.segnali.fallito.connect(lambda _: _in_corso.discard(lavoro))
    QThreadPool.globalInstance().start(lavoro)
