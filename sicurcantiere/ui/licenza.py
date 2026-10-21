"""Licenza nell'interfaccia: stato, inserimento del codice, prova gratuita con un solo cantiere."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import licenza
from sicurcantiere.documenti.comune import data_it
from sicurcantiere.ui.lavoro_ai import impostazioni_comuni

CHIAVE_CODICE = "licenza/codice"
CHIAVE_INIZIO_PROVA = "prova/inizio"
CHIAVE_CANTIERE_PROVA = "prova/cantiere"


def codice_salvato() -> str:
    return impostazioni_comuni().value(CHIAVE_CODICE, "", type=str)


def inizio_prova() -> date | None:
    valore = impostazioni_comuni().value(CHIAVE_INIZIO_PROVA, "", type=str)
    try:
        return date.fromisoformat(valore) if valore else None
    except ValueError:
        return None


def stato_corrente(programma: str) -> licenza.Stato:
    """Stato della licenza per il programma; la prova parte al primo avvio senza licenza."""
    inizio = inizio_prova()
    stato = licenza.stato(programma, codice_salvato(), inizio)
    if stato.tipo == licenza.PROVA and inizio is None:
        impostazioni_comuni().setValue(CHIAVE_INIZIO_PROVA, date.today().isoformat())
    licenza.registra(stato)  # i documenti generati riportano il titolare della licenza
    return stato


def descrizione(stato: licenza.Stato, nome_programma: str) -> str:
    """Una o due frasi sullo stato, per la finestra Licenza e la pagina iniziale."""
    if stato.tipo == licenza.LIBERO:
        return "Controllo delle licenze non attivo."
    if stato.tipo == licenza.PROVA:
        return (f"Prova gratuita: restano {stato.giorni_prova} giorni, con un solo cantiere. "
                "Inserisci la licenza per continuare senza limiti.")
    if stato.tipo == licenza.PROVA_FINITA:
        return "La prova gratuita di 30 giorni è terminata: inserisci la licenza per continuare."
    l = stato.licenza
    if stato.tipo == licenza.NON_INCLUSO:
        return (f"{nome_programma} non è incluso nella tua licenza (piano {l.nome_piano}). "
                "Si può aggiungere passando al piano Completo.")
    postazioni = "1 postazione" if l.postazioni == 1 else f"{l.postazioni} postazioni"
    testo = f"Licenza {l.nome_piano} n. {l.id} intestata a {l.cliente}, per {postazioni}"
    if l.scadenza is None:
        return testo + ", senza scadenza."
    if l.scaduta():
        return (testo + f", scaduta il {data_it(l.scadenza.isoformat())}. Il programma continua a "
                "funzionare; per aggiornamenti normativi e assistenza va rinnovata.")
    return testo + f", valida fino al {data_it(l.scadenza.isoformat())}."


def testo_barra(stato: licenza.Stato) -> str:
    """Breve indicazione per la barra di stato (vuota se tutto è in regola)."""
    if stato.tipo == licenza.PROVA:
        return f"Prova gratuita: {stato.giorni_prova} giorni"
    if stato.tipo == licenza.LICENZA and stato.scaduta:
        return "Licenza scaduta: rinnova per gli aggiornamenti"
    if stato.tipo == licenza.LICENZA:
        return f"Licenza {stato.licenza.nome_piano} · {stato.licenza.cliente}"
    return ""


def apri_acquisto() -> None:
    contatto = licenza.CONTATTO_ACQUISTO
    if contatto:
        QDesktopServices.openUrl(QUrl(contatto if "://" in contatto else f"mailto:{contatto}"))


def consenti_cantiere(genitore: QWidget, programma: str, percorso: Path) -> bool:
    """Durante la prova si lavora su un solo cantiere: il primo creato o aperto."""
    stato = stato_corrente(programma)
    if not stato.utilizzabile:
        QMessageBox.information(genitore, "Licenza", descrizione(stato, programma.upper()))
        return False
    if stato.tipo != licenza.PROVA:
        return True
    impostazioni = impostazioni_comuni()
    scelto = impostazioni.value(CHIAVE_CANTIERE_PROVA, "", type=str)
    attuale = str(Path(percorso).resolve()).lower()
    if not scelto:
        impostazioni.setValue(CHIAVE_CANTIERE_PROVA, attuale)
        return True
    if scelto == attuale:
        return True
    QMessageBox.information(
        genitore, "Prova gratuita",
        f"La prova gratuita comprende un solo cantiere:\n{scelto}\n\n"
        "Per lavorare su altri cantieri inserisci la licenza da Aiuto > Licenza.")
    return False


class DialogoLicenza(QDialog):
    """Stato della licenza e inserimento del codice ricevuto via email."""

    def __init__(self, programma: str, nome_programma: str, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.programma, self.nome_programma = programma, nome_programma
        self.setWindowTitle("Licenza")
        self.setMinimumWidth(560)
        self.stato = QLabel()
        self.stato.setWordWrap(True)
        self.codice = QPlainTextEdit()
        self.codice.setPlaceholderText("Incolla qui il codice di licenza ricevuto (inizia con SC1-)")
        self.codice.setMaximumHeight(90)
        self.codice.setPlainText(codice_salvato())
        self.errore = QLabel()
        self.errore.setObjectName("errorMessage")
        self.errore.setWordWrap(True)
        self.errore.hide()
        pulsanti = QDialogButtonBox()
        attiva = pulsanti.addButton("Attiva la licenza", QDialogButtonBox.ButtonRole.AcceptRole)
        attiva.setProperty("variant", "primary")
        pulsanti.addButton("Chiudi", QDialogButtonBox.ButtonRole.RejectRole)
        pulsanti.accepted.connect(self._attiva)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.stato)
        layout.addWidget(QLabel("Codice di licenza"))
        layout.addWidget(self.codice)
        layout.addWidget(self.errore)
        if licenza.CONTATTO_ACQUISTO:
            acquisto = QPushButton("Come acquistare o rinnovare la licenza")
            acquisto.setProperty("variant", "quiet")
            acquisto.clicked.connect(apri_acquisto)
            layout.addWidget(acquisto)
        layout.addWidget(pulsanti)
        self._mostra()

    def _mostra(self) -> None:
        self.stato.setText(descrizione(stato_corrente(self.programma), self.nome_programma))

    def _attiva(self) -> None:
        codice = "".join(self.codice.toPlainText().split())
        try:
            l = licenza.leggi(codice)
        except licenza.ErroreLicenza as e:
            self.errore.setText(str(e))
            self.errore.show()
            return
        impostazioni_comuni().setValue(CHIAVE_CODICE, codice)
        self.errore.hide()
        self._mostra()
        QMessageBox.information(self, "Licenza", f"Licenza attivata: piano {l.nome_piano}, intestata a {l.cliente}.")
        self.accept()
