"""Licenza nell'interfaccia: stato, attivazione del PC, PC della licenza, prova gratuita, sola lettura."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import licenza, licenza_pc
from sicurcantiere.documenti.comune import data_it
from sicurcantiere.ui.lavoro_ai import impostazioni_comuni

CHIAVE_CODICE = "licenza/codice"
CHIAVE_INIZIO_PROVA = "prova/inizio"
CHIAVE_CANTIERE_PROVA = "prova/cantiere"
MODIFICA, LETTURA = "modifica", "lettura"


def codice_salvato() -> str:
    return impostazioni_comuni().value(CHIAVE_CODICE, "", type=str)


def inizio_prova() -> date | None:
    valore = impostazioni_comuni().value(CHIAVE_INIZIO_PROVA, "", type=str)
    try:
        return date.fromisoformat(valore) if valore else None
    except ValueError:
        return None


def stato_corrente(programma: str) -> licenza.Stato:
    """Stato della licenza per il programma; la prova parte al primo avvio senza licenza.

    Con le attivazioni attive, una licenza valida ma non attivata su questo PC (o con l'attivazione
    scaduta, revocata...) diventa SOLA_LETTURA, con il motivo e cosa fare.
    """
    inizio = inizio_prova()
    stato = licenza.stato(programma, codice_salvato(), inizio)
    if stato.tipo == licenza.PROVA and inizio is None:
        impostazioni_comuni().setValue(CHIAVE_INIZIO_PROVA, date.today().isoformat())
    if stato.tipo == licenza.LICENZA and licenza_pc.attive():
        situazione = licenza_pc.situazione(programma, codice_salvato())
        if situazione.sola_lettura:
            stato = licenza.Stato(licenza.SOLA_LETTURA, stato.licenza, scaduta=stato.scaduta,
                                  motivo=situazione.motivo, cosa_fare=situazione.cosa_fare)
        else:
            stato.avvisi = situazione.avvisi
    elif stato.tipo in (licenza.PROVA_FINITA, licenza.NON_INCLUSO):
        stato.cosa_fare = "Puoi aprire e stampare i cantieri già creati, in sola lettura."
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
        return ("La prova gratuita di 30 giorni è terminata: inserisci la licenza per continuare. "
                "I cantieri già creati si aprono in sola lettura.")
    l = stato.licenza
    if stato.tipo == licenza.NON_INCLUSO:
        return (f"{nome_programma} non è incluso nella tua licenza (piano {l.nome_piano}). "
                "Puoi aggiungerlo passando al piano Completo.")
    if stato.tipo == licenza.SOLA_LETTURA:
        return f"{stato.motivo} {stato.cosa_fare}".strip()
    postazioni = "1 postazione" if l.postazioni == 1 else f"{l.postazioni} postazioni"
    testo = f"Licenza {l.nome_piano} n. {l.id} intestata a {l.cliente}, per {postazioni}"
    if l.scadenza is None:
        testo += ", senza scadenza."
    elif l.scaduta():
        testo += (f", scaduta il {data_it(l.scadenza.isoformat())}. Il programma continua a funzionare; per "
                  "ricevere gli aggiornamenti normativi e l'assistenza è necessario rinnovarla.")
    else:
        testo += f", valida fino al {data_it(l.scadenza.isoformat())}."
    return " ".join([testo, *stato.avvisi])


def testo_barra(stato: licenza.Stato) -> str:
    """Breve indicazione per la barra di stato (vuota se tutto è in regola)."""
    if stato.tipo == licenza.PROVA:
        giorni = "1 giorno rimanente" if stato.giorni_prova == 1 else f"{stato.giorni_prova} giorni rimanenti"
        return f"Prova gratuita: {giorni}"
    if stato.tipo == licenza.SOLA_LETTURA:
        return "Sola lettura: licenza da sistemare"
    if stato.tipo in (licenza.PROVA_FINITA, licenza.NON_INCLUSO):
        return "Sola lettura: licenza mancante"
    if stato.tipo == licenza.LICENZA and stato.avvisi:
        return "Licenza: collegati a internet per la verifica"
    if stato.tipo == licenza.LICENZA and stato.scaduta:
        return "Licenza scaduta: rinnovala per ricevere gli aggiornamenti"
    if stato.tipo == licenza.LICENZA:
        return f"Licenza {stato.licenza.nome_piano} · {stato.licenza.cliente}"
    return ""


def apri_acquisto() -> None:
    contatto = licenza.CONTATTO_ACQUISTO
    if contatto:
        QDesktopServices.openUrl(QUrl(contatto if "://" in contatto else f"mailto:{contatto}"))


def modo_apertura(genitore: QWidget, programma: str, percorso: Path) -> str | None:
    """Come aprire un cantiere: MODIFICA, LETTURA (licenza non valida: i dati restano consultabili) o None.

    Durante la prova si lavora su un solo cantiere (il primo creato o aperto); gli altri si aprono in
    sola lettura.
    """
    stato = stato_corrente(programma)
    if not stato.utilizzabile:
        return LETTURA
    if stato.tipo != licenza.PROVA:
        return MODIFICA
    impostazioni = impostazioni_comuni()
    scelto = impostazioni.value(CHIAVE_CANTIERE_PROVA, "", type=str)
    attuale = str(Path(percorso).resolve()).lower()
    if not scelto:
        impostazioni.setValue(CHIAVE_CANTIERE_PROVA, attuale)
        return MODIFICA
    if scelto == attuale:
        return MODIFICA
    QMessageBox.information(
        genitore, "Prova gratuita",
        f"La prova gratuita comprende un solo cantiere:\n{scelto}\n\n"
        "Questo cantiere si apre in sola lettura. Per lavorare su altri cantieri inserisci la licenza in "
        "«Aiuto > Licenza».")
    return LETTURA


def consenti_cantiere(genitore: QWidget, programma: str, percorso: Path) -> bool:
    """Si può creare un nuovo cantiere (licenza valida, o il primo cantiere della prova)?"""
    stato = stato_corrente(programma)
    if not stato.utilizzabile:
        QMessageBox.information(genitore, "Licenza", descrizione(stato, programma.upper()))
        return False
    return modo_apertura(genitore, programma, percorso) == MODIFICA


class _Attesa:
    """Cursore di attesa durante le richieste al server delle licenze."""

    def __enter__(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

    def __exit__(self, *_):
        QApplication.restoreOverrideCursor()


def _messaggio_rete() -> str:
    return ("Non è stato possibile collegarsi al server delle licenze. Controlla la connessione a internet e riprova. "
            f"Il programma funziona comunque per {licenza_pc.GIORNI_ATTESA} giorni; senza internet puoi usare "
            "«Attivazione senza internet».")


class DialogoPC(QDialog):
    """PC su cui è attiva la licenza, con «Disattiva» per liberare un posto (trasferimento)."""

    def __init__(self, programma: str, codice: str, genitore: QWidget | None = None, messaggio: str = ""):
        super().__init__(genitore)
        self.programma, self.codice = programma, codice
        self.liberati = 0
        self.setWindowTitle("PC della licenza")
        self.setMinimumWidth(640)
        self.messaggio = QLabel(messaggio)
        self.messaggio.setWordWrap(True)
        self.messaggio.setVisible(bool(messaggio))
        if messaggio:
            self.messaggio.setObjectName("statusBanner")
            self.messaggio.setProperty("state", "error")
        self.riepilogo = QLabel()
        self.riepilogo.setWordWrap(True)
        self.tabella = QTableWidget(0, 4)
        self.tabella.setHorizontalHeaderLabels(["PC", "Attivato il", "Ultimo uso", ""])
        self.tabella.verticalHeader().hide()
        self.tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabella.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        intestazione = self.tabella.horizontalHeader()
        intestazione.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for colonna in (1, 2):
            intestazione.setSectionResizeMode(colonna, QHeaderView.ResizeMode.ResizeToContents)
        intestazione.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tabella.setColumnWidth(3, 120)
        nota = QLabel("Disattiva un PC che non usi più (per esempio il vecchio portatile): il posto si libera e puoi "
                      "attivare la licenza su questo PC. Il PC disattivato, alla prossima apertura, chiederà di "
                      "essere attivato di nuovo.")
        nota.setObjectName("hint")
        nota.setWordWrap(True)
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        pulsanti.button(QDialogButtonBox.StandardButton.Close).setText("Chiudi")
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        for w in (self.messaggio, self.riepilogo, self.tabella, nota, pulsanti):
            layout.addWidget(w)
        self.dati: dict = {}

    def carica(self) -> bool:
        """Legge l'elenco dal server; False (con un messaggio) se non è raggiungibile."""
        try:
            with _Attesa():
                self.dati = licenza_pc.gestore(self.programma).elenco_pc(self.codice)
        except licenza_pc.ErroreRete:
            QMessageBox.warning(self.parent() or self, "PC della licenza", _messaggio_rete())
            return False
        except licenza_pc.ErroreServer as e:
            QMessageBox.warning(self.parent() or self, "PC della licenza", str(e))
            return False
        self._mostra()
        return True

    def _mostra(self) -> None:
        d = self.dati
        rimasti = d.get("trasferimenti_rimasti", 0)
        self.riepilogo.setText(
            f"<b>{d.get('attivi', 0)} PC attivi su {d.get('posti', 0)}.</b> Questo mese puoi ancora attivare "
            f"{rimasti} {'PC nuovo' if rimasti == 1 else 'PC nuovi'}.")
        elenco = d.get("pc") or []
        self.tabella.setRowCount(len(elenco))
        for r, pc in enumerate(elenco):
            nome = pc.get("nome", "") + (" (questo PC)" if pc.get("questo") else "") + \
                (" · attivato senza internet" if pc.get("offline") else "")
            for c, testo in enumerate((nome, data_it(pc.get("attivato", "")), data_it(pc.get("ultimo_uso", "")))):
                self.tabella.setItem(r, c, QTableWidgetItem(testo))
            if not pc.get("questo"):
                pulsante = QPushButton("Disattiva")
                pulsante.clicked.connect(lambda _=False, p=pc: self._disattiva(p))
                self.tabella.setCellWidget(r, 3, pulsante)
        self.tabella.resizeRowsToContents()

    def _disattiva(self, pc: dict) -> None:
        if QMessageBox.question(self, "Disattiva il PC",
                                f"Disattivare la licenza su «{pc.get('nome')}»? Il posto si libera subito.") \
                != QMessageBox.StandardButton.Yes:
            return
        try:
            with _Attesa():
                licenza_pc.gestore(self.programma).libera(self.codice, pc["id"])
        except (licenza_pc.ErroreRete, licenza_pc.ErroreServer) as e:
            QMessageBox.warning(self, "Disattiva il PC", _messaggio_rete() if isinstance(e, licenza_pc.ErroreRete)
                                else str(e))
            return
        self.liberati += 1
        self.carica()


class DialogoLicenza(QDialog):
    """Stato della licenza, inserimento del codice e attivazione di questo PC."""

    def __init__(self, programma: str, nome_programma: str, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.programma, self.nome_programma = programma, nome_programma
        self.setWindowTitle("Licenza")
        self.setMinimumWidth(580)
        self.stato = QLabel()
        self.stato.setWordWrap(True)
        self.dettagli = QLabel()
        self.dettagli.setObjectName("hint")
        self.dettagli.setWordWrap(True)
        # il codice è personale: nascosto come una password, si può mostrare per controllarlo
        self.codice = QLineEdit()
        self.codice.setEchoMode(QLineEdit.EchoMode.Password)
        self.codice.setPlaceholderText("Incolla qui il codice di licenza ricevuto (inizia con SC1-)")
        self.codice.setText(codice_salvato())
        self.mostra = QCheckBox("Mostra il codice")
        self.mostra.toggled.connect(lambda si: self.codice.setEchoMode(
            QLineEdit.EchoMode.Normal if si else QLineEdit.EchoMode.Password))
        self.errore = QLabel()
        self.errore.setObjectName("errorMessage")
        self.errore.setWordWrap(True)
        self.errore.hide()

        self.p_pc = QPushButton("PC della licenza...")
        self.p_pc.clicked.connect(self.mostra_pc)
        self.p_disattiva = QPushButton("Disattiva questo PC")
        self.p_disattiva.clicked.connect(self.disattiva_questo)
        self.p_offline = QPushButton("Attivazione senza internet")
        menu = QMenu(self.p_offline)
        menu.addAction("1. Salva il file di richiesta...").triggered.connect(self.salva_richiesta)
        menu.addAction("2. Carica il file di attivazione...").triggered.connect(self.carica_attivazione)
        self.p_offline.setMenu(menu)
        riga_pc = QHBoxLayout()
        for p in (self.p_pc, self.p_disattiva, self.p_offline):
            riga_pc.addWidget(p)
        riga_pc.addStretch()

        pulsanti = QDialogButtonBox()
        attiva = pulsanti.addButton("Attiva la licenza", QDialogButtonBox.ButtonRole.AcceptRole)
        attiva.setProperty("variant", "primary")
        pulsanti.addButton("Chiudi", QDialogButtonBox.ButtonRole.RejectRole)
        pulsanti.accepted.connect(self._attiva)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.stato)
        layout.addWidget(self.dettagli)
        layout.addWidget(QLabel("Codice di licenza"))
        layout.addWidget(self.codice)
        layout.addWidget(self.mostra)
        layout.addWidget(self.errore)
        layout.addLayout(riga_pc)
        if licenza.CONTATTO_ACQUISTO:
            acquisto = QPushButton("Come acquistare o rinnovare la licenza")
            acquisto.setProperty("variant", "quiet")
            acquisto.clicked.connect(apri_acquisto)
            layout.addWidget(acquisto)
        layout.addWidget(pulsanti)
        self._mostra()

    # --- stato ---

    def _mostra(self) -> None:
        stato = stato_corrente(self.programma)
        self.stato.setText(descrizione(stato, self.nome_programma))
        attive = licenza_pc.attive() and bool(codice_salvato())
        certificato = licenza_pc.gestore(self.programma).certificato()[0] if licenza_pc.attive() else None
        if certificato is not None:
            self.dettagli.setText(
                f"Attivata su questo PC ({certificato.posti} {'posto' if certificato.posti == 1 else 'posti'} nella "
                f"licenza). Ultima verifica: {certificato.emesso.astimezone():%d/%m/%Y %H:%M}"
                + (" (attivazione senza internet)." if certificato.offline else "."))
        else:
            self.dettagli.setText("")
        self.dettagli.setVisible(bool(self.dettagli.text()))
        for p in (self.p_pc, self.p_offline):
            p.setVisible(licenza_pc.attive())
        self.p_pc.setEnabled(attive)
        self.p_disattiva.setVisible(certificato is not None)

    def _codice(self) -> str | None:
        codice = "".join(self.codice.text().split())
        try:
            licenza.leggi(codice)
        except licenza.ErroreLicenza as e:
            self.errore.setText(str(e))
            self.errore.show()
            return None
        self.errore.hide()
        return codice

    # --- azioni ---

    def _attiva(self) -> None:
        codice = self._codice()
        if codice is None:
            return
        impostazioni_comuni().setValue(CHIAVE_CODICE, codice)
        l = licenza.leggi(codice)
        if not licenza_pc.attive():
            self._mostra()
            QMessageBox.information(self, "Licenza", f"Licenza attivata: piano {l.nome_piano}, intestata a {l.cliente}.")
            self.accept()
            return
        for _ in range(3):  # dopo aver liberato un posto si riprova
            try:
                with _Attesa():
                    certificato = licenza_pc.attiva(self.programma, codice)
            except licenza_pc.ErroreRete:
                self._mostra()
                QMessageBox.warning(self, "Licenza", _messaggio_rete())
                return
            except licenza_pc.ErroreServer as e:
                if e.codice == licenza_pc.POSTI_ESAURITI:
                    dialogo = DialogoPC(self.programma, codice, self, str(e))
                    dialogo.dati = e.dati
                    dialogo._mostra()
                    dialogo.exec()
                    if dialogo.liberati:
                        continue
                self._mostra()
                self.errore.setText(str(e))
                self.errore.show()
                return
            self._mostra()
            QMessageBox.information(
                self, "Licenza",
                f"Licenza attivata su questo PC: piano {l.nome_piano}, intestata a {l.cliente} "
                f"({certificato.posti} {'posto' if certificato.posti == 1 else 'posti'} nella licenza).")
            self.accept()
            return

    def mostra_pc(self) -> None:
        dialogo = DialogoPC(self.programma, codice_salvato(), self)
        if dialogo.carica():
            dialogo.exec()
        self._mostra()

    def disattiva_questo(self) -> None:
        if QMessageBox.question(
                self, "Disattiva questo PC",
                "Disattivare la licenza su questo PC? Il posto si libera e potrai attivarla su un altro PC. "
                "Su questo PC i cantieri si apriranno in sola lettura finché non la riattivi.") \
                != QMessageBox.StandardButton.Yes:
            return
        try:
            with _Attesa():
                licenza_pc.disattiva(self.programma)
        except licenza_pc.ErroreRete:
            QMessageBox.warning(self, "Disattiva questo PC", "Serve la connessione a internet per liberare il posto.")
            return
        except licenza_pc.ErroreServer as e:
            QMessageBox.warning(self, "Disattiva questo PC", str(e))
            return
        self._mostra()
        QMessageBox.information(self, "Disattiva questo PC", "Licenza disattivata su questo PC: il posto è libero.")

    def salva_richiesta(self, destinazione: str | None = None) -> Path | None:
        codice = self._codice()
        if codice is None:
            return None
        impostazioni_comuni().setValue(CHIAVE_CODICE, codice)
        if not destinazione:
            destinazione, _ = QFileDialog.getSaveFileName(
                self, "Salva il file di richiesta", str(Path.home() / "Richiesta attivazione SicurCantiere.screq"),
                "Richiesta di attivazione (*.screq)")
            if not destinazione:
                return None
        percorso = Path(destinazione)
        percorso.write_text(licenza_pc.gestore(self.programma).richiesta_offline(codice), encoding="utf-8")
        QMessageBox.information(
            self, "Attivazione senza internet",
            f"File di richiesta salvato:\n{percorso}\n\nMandalo all'assistenza di SicurCantiere (per esempio per "
            "email da un altro dispositivo): riceverai un file di attivazione da caricare qui con «2. Carica il file "
            "di attivazione». Il file di attivazione vale 90 giorni.")
        return percorso

    def carica_attivazione(self, origine: str | None = None) -> bool:
        if not origine:
            origine, _ = QFileDialog.getOpenFileName(self, "Carica il file di attivazione", str(Path.home()),
                                                     "Attivazione SicurCantiere (*.sclic);;Tutti i file (*)")
            if not origine:
                return False
        from sicur_license.certificato import ErroreCertificato

        try:
            certificato = licenza_pc.importa_offline(self.programma, Path(origine).read_text(encoding="utf-8"))
        except (OSError, ErroreCertificato, json.JSONDecodeError) as e:
            QMessageBox.warning(self, "Attivazione senza internet", f"File non valido: {e}")
            return False
        self._mostra()
        QMessageBox.information(self, "Attivazione senza internet",
                                f"Licenza attivata su questo PC fino al {certificato.valido_fino.astimezone():%d/%m/%Y}.")
        return True
