"""Finestra principale."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSettings, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import __version__, controlli
from sicurcantiere.db import ErroreProgetto, Progetto, anteprima
from sicurcantiere.repository import Repository
from sicurcantiere.ui import aggiornamenti, archivio_anagrafiche, tema
from sicurcantiere.ui.edizioni import ESTENSIONI, PSC, Edizione
from sicurcantiere.ui.icone import icona, icona_applicazione
from sicurcantiere import licenza
from sicurcantiere.ui import licenza as licenza_ui
from sicurcantiere.ui.guida import DialogoGuida
from sicurcantiere.ui.lavoro_ai import DialogoImpostazioniAI, aggiorna_pulsanti_ai
from sicurcantiere.ui.pagine import Pagina, primario

MAX_RECENTI = 8
INTERVALLO_STATO_MS = 3000


def _etichetta(testo: str, nome: str, a_capo: bool = False) -> QLabel:
    e = QLabel(testo)
    e.setObjectName(nome)
    e.setWordWrap(a_capo)
    e.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    return e


def _data_breve(istante: datetime) -> str:
    oggi = datetime.now().date()
    if istante.date() == oggi:
        return f"Oggi, {istante:%H:%M}"
    if (oggi - istante.date()).days == 1:
        return "Ieri"
    return f"{istante:%d/%m/%Y}"


class SchedaRecente(QPushButton):
    """Scheda cliccabile di un cantiere recente: nome, luogo, file e data di modifica."""

    def __init__(self, percorso: str):
        super().__init__()
        self.setObjectName("recentCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.percorso = percorso
        dati = anteprima(percorso) or {}
        file = Path(percorso)
        luogo = " ".join(v for v in (dati.get("comune", ""),
                                      f"({dati['provincia']})" if dati.get("provincia") else "") if v)
        try:
            modificato = _data_breve(datetime.fromtimestamp(file.stat().st_mtime))
        except OSError:
            modificato = ""
        self.setToolTip(percorso)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        layout.addWidget(_etichetta(dati.get("nome") or file.stem, "recentTitle"))
        layout.addWidget(_etichetta(luogo or " ", "pageSubtitle"))
        riga = QHBoxLayout()
        riga.setSpacing(8)
        riga.addWidget(_etichetta(file.suffix, "extBadge"))
        nome_file = _etichetta(file.stem, "hint")
        nome_file.setProperty("mono", True)
        riga.addWidget(nome_file, 1)
        riga.addWidget(_etichetta(modificato, "hint"))
        layout.addLayout(riga)
        self.setMinimumHeight(88)


class PulsanteGrande(QPushButton):
    """Pulsante della pagina iniziale: titolo, riga di spiegazione e scorciatoia."""

    def __init__(self, nome_icona: str, titolo: str, nota: str, scorciatoia: str, principale: bool):
        super().__init__()
        self.setProperty("large", True)
        if principale:
            tema.imposta_variante(self, "primary")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        c = tema.correnti()
        immagine = QLabel()
        immagine.setPixmap(icona(nome_icona, c["acc_tx"] if principale else c["acc_s"], 24).pixmap(24, 24))
        immagine.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        testi = QVBoxLayout()
        testi.setSpacing(2)
        testi.addWidget(_etichetta(titolo, "largeTitle"))
        testi.addWidget(_etichetta(nota, "largeNote"))
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 16, 10)
        layout.setSpacing(14)
        layout.addWidget(immagine)
        layout.addLayout(testi, 1)
        if scorciatoia:
            layout.addWidget(_etichetta(scorciatoia, "kbd"), 0, Qt.AlignmentFlag.AlignVCenter)
        self.setMinimumHeight(70)


class Benvenuto(QWidget):
    """Pagina iniziale: marchio del programma, nuovo e apri, i tre passi e i cantieri recenti."""

    COLONNE_RECENTI = 3
    MAX_SCHEDE = 6

    def __init__(self, finestra: FinestraPrincipale, recenti: list[str]):
        super().__init__()
        edizione = finestra.edizione
        sigla = edizione.nome.split()[-1]
        colonna = QVBoxLayout()
        colonna.setSpacing(16)

        marchio = QHBoxLayout()
        marchio.setSpacing(18)
        logo = QLabel(f"SC\n{sigla}")
        logo.setObjectName("logoTile")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(64, 64)
        nomi = QVBoxLayout()
        nomi.setSpacing(2)
        nomi.addStretch()
        nomi.addWidget(_etichetta(edizione.nome, "heroTitle"))
        nomi.addWidget(_etichetta(f"{edizione.sottotitolo} · D.Lgs. 81/2008", "pageSubtitle", True))
        nomi.addStretch()
        marchio.addWidget(logo)
        marchio.addLayout(nomi, 1)
        colonna.addLayout(marchio)

        stato = licenza_ui.stato_corrente(edizione.chiave)
        if not stato.utilizzabile:
            blocco = QVBoxLayout()
            titolo = "Non incluso nella tua licenza" if stato.tipo == licenza.NON_INCLUSO else "Prova terminata"
            blocco.addWidget(_etichetta(titolo, "sectionTitle"))
            blocco.addWidget(_etichetta(licenza_ui.descrizione(stato, edizione.nome), "pageSubtitle", True))
            azioni = QHBoxLayout()
            inserisci = QPushButton("Inserisci la licenza...")
            tema.imposta_variante(inserisci, "primary")
            inserisci.clicked.connect(finestra.mostra_licenza)
            azioni.addWidget(inserisci)
            if licenza.CONTATTO_ACQUISTO:
                acquista = QPushButton("Come acquistarlo")
                acquista.clicked.connect(licenza_ui.apri_acquisto)
                azioni.addWidget(acquista)
            azioni.addStretch()
            blocco.addLayout(azioni)
            riquadro = QFrame()
            riquadro.setObjectName("card")
            lay_riquadro = QVBoxLayout(riquadro)
            lay_riquadro.setContentsMargins(16, 14, 16, 14)
            lay_riquadro.addLayout(blocco)
            colonna.addWidget(riquadro)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(12)
        nuovo = PulsanteGrande("nuovo", "Nuovo cantiere...",
                               f"Crea un nuovo file {edizione.estensione} e inizia dalla prima pagina", "Ctrl+N", True)
        nuovo.clicked.connect(finestra.nuovo)
        apri = PulsanteGrande("apri", "Apri cantiere...", "Anche da una cartella di rete", "Ctrl+O", False)
        apri.clicked.connect(finestra.apri)
        nuovo.setEnabled(stato.utilizzabile)
        apri.setEnabled(stato.utilizzabile)
        pulsanti.addWidget(nuovo, 1)
        pulsanti.addWidget(apri, 1)
        if edizione.chiave == "pos":
            da_psc = PulsanteGrande("psc", "Nuovo POS da un PSC...", "Dal PSC del coordinatore, in PDF o Word",
                                    "", False)
            da_psc.clicked.connect(finestra.nuovo_da_psc)
            da_psc.setEnabled(stato.utilizzabile)
            pulsanti.addWidget(da_psc, 1)
        colonna.addLayout(pulsanti)

        passi = QFrame()
        passi.setObjectName("card")
        lay_passi = QHBoxLayout(passi)
        lay_passi.setContentsMargins(16, 12, 16, 12)
        lay_passi.setSpacing(24)
        for n, (titolo, nota) in enumerate((
            ("Compila le pagine", "Dall'alto in basso, nella barra a sinistra"),
            ("Risolvi i controlli", "Errori in rosso, avvisi in arancio"),
            ("Genera il documento", "In Word, da rileggere e firmare"),
        ), start=1):
            numero = QLabel(str(n))
            numero.setObjectName("stepNumber")
            numero.setAlignment(Qt.AlignmentFlag.AlignCenter)
            testi = QVBoxLayout()
            testi.setSpacing(1)
            testi.addWidget(_etichetta(titolo, "sectionTitle"))
            testi.addWidget(_etichetta(nota, "hint"))
            passo = QHBoxLayout()
            passo.setSpacing(10)
            passo.addWidget(numero)
            passo.addLayout(testi, 1)
            lay_passi.addLayout(passo, 1)
        colonna.addWidget(passi)

        if recenti:
            colonna.addSpacing(8)
            colonna.addWidget(_etichetta("Cantieri recenti", "sectionTitle"))
            griglia = QGridLayout()
            griglia.setSpacing(12)
            for n, percorso in enumerate(recenti[:self.MAX_SCHEDE]):
                scheda = SchedaRecente(percorso)
                scheda.clicked.connect(lambda _=False, p=percorso: finestra.apri_file(p))
                griglia.addWidget(scheda, n // self.COLONNE_RECENTI, n % self.COLONNE_RECENTI)
            for c in range(self.COLONNE_RECENTI):
                griglia.setColumnStretch(c, 1)
            colonna.addLayout(griglia)

        contenitore = QWidget()
        contenitore.setMaximumWidth(900)
        contenitore.setLayout(colonna)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.addStretch(1)
        riga = QHBoxLayout()
        riga.addStretch()
        riga.addWidget(contenitore, 10)
        riga.addStretch()
        layout.addLayout(riga)
        layout.addStretch(2)


class FinestraPrincipale(QMainWindow):
    def __init__(self, edizione: Edizione = PSC):
        super().__init__()
        self.edizione = edizione
        self.filtro = (
            f"{edizione.descrizione_file} (*{edizione.estensione});;"
            f"Tutti i cantieri SicurCantiere ({' '.join('*' + e for e in ESTENSIONI)})"
        )
        self.impostazioni = QSettings()
        self.progetto: Progetto | None = None
        self.pagine: list[Pagina] = []
        self.scuro = self.impostazioni.value("tema_scuro", False, type=bool)
        self.colori = tema.colori(self.scuro, edizione.chiave)
        self._modifiche_viste = 0

        # Barra laterale: cantiere aperto ed elenco numerato delle pagine, con i problemi di ognuna.
        self.navigazione = QListWidget()
        self.navigazione.setObjectName("nav")
        self.navigazione.setItemDelegate(tema.DelegatoNavigazione(self.navigazione))
        self.navigazione.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.navigazione.currentRowChanged.connect(self._mostra_pagina)
        self.nome_cantiere = QLabel()
        self.nome_cantiere.setObjectName("projectName")
        self.nome_cantiere.setWordWrap(True)
        self.luogo_cantiere = QLabel()
        self.luogo_cantiere.setObjectName("projectPlace")
        self.suggerimento_navigazione = QLabel("Apri o crea un cantiere per iniziare a compilare.")
        self.suggerimento_navigazione.setObjectName("navHint")
        self.suggerimento_navigazione.setWordWrap(True)
        separatore = QFrame()
        separatore.setObjectName("navRule")
        laterale = QFrame()
        laterale.setObjectName("sidePanel")
        laterale.setFixedWidth(248)
        lay_laterale = QVBoxLayout(laterale)
        lay_laterale.setContentsMargins(10, 14, 0, 0)
        lay_laterale.setSpacing(0)
        for w in (self.nome_cantiere, self.luogo_cantiere, self.suggerimento_navigazione, separatore):
            lay_laterale.addWidget(w)
        lay_laterale.addSpacing(8)
        lay_laterale.addWidget(self.navigazione, 1)

        self.contenitore = QStackedWidget()
        self.contenitore.setObjectName("pages")
        contenuto = QWidget()
        contenuto.setObjectName("centralArea")
        lay_contenuto = QVBoxLayout(contenuto)
        lay_contenuto.setContentsMargins(0, 0, 0, 0)
        lay_contenuto.addWidget(self.contenitore)

        centrale = QWidget()
        centrale.setObjectName("centralArea")
        layout = QHBoxLayout(centrale)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(laterale)
        layout.addWidget(contenuto, 1)
        self.setCentralWidget(centrale)

        self._crea_azioni()
        self._crea_menu()
        self._crea_barra_strumenti()
        self._crea_barra_stato()
        self._applica_icone()

        self._timer_stato = QTimer(self, interval=INTERVALLO_STATO_MS)
        self._timer_stato.timeout.connect(self._aggiorna_stato)

        self._chiudi_progetto()
        self._aggiorna_licenza()
        self.resize(1280, 820)
        geometria = self.impostazioni.value("geometria")
        if geometria is not None:
            self.restoreGeometry(geometria)

    # --- azioni, menu e barre ---

    def _azione(self, testo: str, slot, scorciatoia=None, suggerimento: str = "") -> QAction:
        a = QAction(testo, self)
        if scorciatoia is not None:
            a.setShortcut(scorciatoia)
        a.setToolTip(suggerimento or testo.replace("&", "").rstrip("."))
        a.triggered.connect(slot)
        return a

    def _crea_azioni(self) -> None:
        self.azione_nuovo = self._azione("&Nuovo cantiere...", self.nuovo, QKeySequence.StandardKey.New)
        self.azione_apri = self._azione("&Apri...", self.apri, QKeySequence.StandardKey.Open)
        self.azione_salva = self._azione(
            "&Salva", self.salva, QKeySequence.StandardKey.Save,
            "Salva le modifiche (il programma salva anche da solo ogni modifica)")
        self.azione_salva_con_nome = self._azione(
            "Salva &con nome...", self.salva_con_nome, QKeySequence.StandardKey.SaveAs,
            "Salva una copia del cantiere con un altro nome")
        self.azione_chiudi = self._azione("C&hiudi cantiere", self._chiudi_progetto)
        self.azione_da_psc = self._azione("Nuovo POS da un &PSC...", self.nuovo_da_psc,
                                          suggerimento="Legge il PSC del coordinatore (PDF o Word) e prepara il "
                                                       "file del POS delle imprese scelte")
        self.azione_psc = self._azione(self.edizione.azione_principale, self._genera_principale, "Ctrl+P")
        self.azione_controlli = self._azione("&Controlli", self._vai_ai_controlli, "F7",
                                             "Mostra i controlli di completezza")
        self.azione_tema = self._azione("Tema &scuro", self._cambia_tema)
        self.azione_tema.setCheckable(True)
        self.azione_tema.setChecked(self.scuro)
        self.azione_info = self._azione("&Informazioni", self._informazioni)
        self.azione_licenza = self._azione("&Licenza...", self.mostra_licenza)
        self.azione_guida = self._azione("&Guida rapida", lambda: DialogoGuida(
            self.edizione.nome.split()[-1], self).exec(), QKeySequence.StandardKey.HelpContents)
        self.azione_aggiornamenti = self._azione(
            "Controlla &aggiornamenti...", lambda: aggiornamenti.controlla(self, manuale=True))
        self.azione_ai = self._azione("Impostazioni assistente &AI...", lambda: DialogoImpostazioniAI(self).exec())
        self.azione_archivio = self._azione("Archivio &anagrafiche...", lambda: archivio_anagrafiche.gestisci(self))
        self.azioni_progetto = [self.azione_salva, self.azione_salva_con_nome, self.azione_chiudi,
                                self.azione_psc, self.azione_controlli]

    def _crea_menu(self) -> None:
        menu = self.menuBar().addMenu("&File")
        menu.addAction(self.azione_nuovo)
        if self.edizione.chiave == "pos":
            menu.addAction(self.azione_da_psc)
        menu.addAction(self.azione_apri)
        menu.addAction(self.azione_salva)
        menu.addAction(self.azione_salva_con_nome)
        self.menu_recenti = menu.addMenu("File &recenti")
        self.menu_recenti.aboutToShow.connect(self._popola_recenti)
        menu.addAction(self.azione_chiudi)
        menu.addSeparator()
        esci = self._azione("&Esci", self.close, QKeySequence.StandardKey.Quit)
        menu.addAction(esci)

        strumenti = self.menuBar().addMenu("&Strumenti")
        strumenti.addAction(self.azione_psc)
        strumenti.addAction(self.azione_controlli)
        strumenti.addSeparator()
        strumenti.addAction(self.azione_archivio)
        strumenti.addAction(self.azione_ai)

        vista = self.menuBar().addMenu("&Visualizza")
        vista.addAction(self.azione_tema)

        aiuto = self.menuBar().addMenu("&Aiuto")
        aiuto.addAction(self.azione_guida)
        aiuto.addAction(self.azione_aggiornamenti)
        aiuto.addAction(self.azione_licenza)
        aiuto.addSeparator()
        aiuto.addAction(self.azione_info)

    def _crea_barra_strumenti(self) -> None:
        barra = QToolBar("Strumenti")
        barra.setObjectName("barraStrumenti")
        barra.setMovable(False)
        barra.setIconSize(QSize(20, 20))
        barra.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        for a in (self.azione_nuovo, self.azione_apri, self.azione_salva, self.azione_salva_con_nome):
            barra.addAction(a)
        barra.addSeparator()
        barra.addAction(self.azione_psc)
        barra.widgetForAction(self.azione_psc).setObjectName("generate")
        barra.addAction(self.azione_controlli)
        self.addToolBar(barra)
        self.barra_strumenti = barra

    def _crea_barra_stato(self) -> None:
        self.stato_file = QLabel()
        self.stato_file.setObjectName("filePath")
        self.stato_salvataggio = QLabel()
        self.stato_salvataggio.setObjectName("savedLabel")
        self.stato_controlli = QPushButton()
        self.stato_controlli.setObjectName("checksIndicator")
        self.stato_controlli.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stato_controlli.setToolTip("Apre la pagina dei controlli (F7)")
        self.stato_controlli.clicked.connect(self._vai_ai_controlli)
        barra = self.statusBar()
        barra.setSizeGripEnabled(False)
        barra.addWidget(self.stato_file)
        barra.addWidget(self.stato_salvataggio, 1)
        self.stato_licenza = QPushButton()
        self.stato_licenza.setObjectName("licenseIndicator")
        tema.imposta_variante(self.stato_licenza, "quiet")
        self.stato_licenza.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stato_licenza.clicked.connect(self.mostra_licenza)
        barra.addPermanentWidget(self.stato_licenza)
        barra.addPermanentWidget(self.stato_controlli)

    def _applica_icone(self) -> None:
        c = self.colori.icone
        for azione, nome in (
            (self.azione_nuovo, "nuovo"), (self.azione_apri, "apri"),
            (self.azione_salva, "salva"), (self.azione_salva_con_nome, "salva_con_nome"),
            (self.azione_psc, "psc"),
            (self.azione_controlli, "controlli"), (self.azione_tema, "tema"),
            (self.azione_info, "info"), (self.azione_ai, "ai"),
        ):
            azione.setIcon(icona(nome, c))
        self.setWindowIcon(icona_applicazione(self.edizione.colore))

    def _cambia_tema(self) -> None:
        self.scuro = self.azione_tema.isChecked()
        self.impostazioni.setValue("tema_scuro", self.scuro)
        app = QApplication.instance()
        if app is not None:
            self.colori = tema.applica(app, self.scuro, self.edizione.chiave)
        self._applica_icone()
        if not self.pagine:
            self._mostra_benvenuto()
        self._aggiorna_stato()

    # --- file recenti e informazioni ---

    def _recenti(self) -> list[str]:
        valore = self.impostazioni.value("recenti", [])
        if isinstance(valore, str):
            valore = [valore]
        return [v for v in valore or [] if Path(v).exists()]

    def _aggiungi_recente(self, percorso: Path) -> None:
        recenti = [str(percorso)] + [r for r in self._recenti() if r != str(percorso)]
        self.impostazioni.setValue("recenti", recenti[:MAX_RECENTI])

    def _popola_recenti(self) -> None:
        self.menu_recenti.clear()
        recenti = self._recenti()
        if not recenti:
            self.menu_recenti.addAction("(nessuno)").setEnabled(False)
        for r in recenti:
            self.menu_recenti.addAction(r).triggered.connect(lambda _=False, p=r: self.apri_file(p))

    def mostra_licenza(self) -> None:
        licenza_ui.DialogoLicenza(self.edizione.chiave, self.edizione.nome, self).exec()
        self._aggiorna_licenza()
        aggiorna_pulsanti_ai()  # l'assistente incluso dipende dalla licenza
        if not self.pagine:
            self._mostra_benvenuto()

    def _aggiorna_licenza(self) -> None:
        testo = licenza_ui.testo_barra(licenza_ui.stato_corrente(self.edizione.chiave))
        self.stato_licenza.setText(testo)
        self.stato_licenza.setVisible(bool(testo))

    def _informazioni(self) -> None:
        QMessageBox.about(
            self, "Informazioni",
            f"<b>{self.edizione.nome}</b> versione {__version__}<br>"
            f"{self.edizione.sottotitolo}, secondo il D.Lgs. 81/2008.<br><br>"
            f"{licenza_ui.descrizione(licenza_ui.stato_corrente(self.edizione.chiave), self.edizione.nome)}<br><br>"
            "I documenti generati vanno riletti e firmati da chi ne risponde: il programma è uno "
            "strumento di redazione.<br><br>"
            "Caratteri Ubuntu (Ubuntu Font Licence 1.0, © Canonical Ltd.).",
        )

    # --- gestione progetto ---

    def _cartella_iniziale(self) -> str:
        recenti = self._recenti()
        return str(Path(recenti[0]).parent) if recenti else str(Path.home())

    def nuovo(self) -> None:
        # Niente conferma di sovrascrittura di Windows: scegliere un cantiere esistente qui di
        # solito vuol dire volerlo aprire, e «Sì» lo sostituirebbe con uno vuoto.
        percorso, _ = QFileDialog.getSaveFileName(
            self, "Nuovo cantiere", str(Path(self._cartella_iniziale()) / f"Cantiere{self.edizione.estensione}"),
            self.filtro, options=QFileDialog.Option.DontConfirmOverwrite,
        )
        if not percorso:
            return
        percorso = Path(percorso)
        if percorso.suffix.lower() not in ESTENSIONI:
            percorso = percorso.with_suffix(self.edizione.estensione)
        if self.progetto and percorso.resolve() == self.progetto.percorso.resolve():
            QMessageBox.warning(self, "Nuovo cantiere", "Il file è già aperto: scegliere un altro nome.")
            return
        if not licenza_ui.consenti_cantiere(self, self.edizione.chiave, percorso):
            return
        if percorso.exists():
            scelta = self._scelta_file_esistente(percorso)
            if scelta == "apri":
                self.apri_file(percorso)
                return
            if scelta != "sostituisci":
                return
        self._carica(Progetto(percorso, crea=True))

    def _scelta_file_esistente(self, percorso: Path) -> str:
        """Chiede cosa fare se il nuovo cantiere ha il nome di un file esistente: apri, sostituisci o annulla."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle("Nuovo cantiere")
        box.setText(f"Esiste già un cantiere «{percorso.name}» in questa cartella.")
        box.setInformativeText("Per lavorarci scegliere «Apri il cantiere». «Sostituisci» crea al suo posto un "
                               "cantiere vuoto (resta una copia di sicurezza del vecchio).")
        apri = box.addButton("Apri il cantiere", QMessageBox.ButtonRole.AcceptRole)
        sostituisci = box.addButton("Sostituisci con uno vuoto", QMessageBox.ButtonRole.DestructiveRole)
        box.addButton("Annulla", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(apri)
        box.exec()
        return "apri" if box.clickedButton() is apri else "sostituisci" if box.clickedButton() is sostituisci \
            else "annulla"

    def apri(self) -> None:
        percorso, _ = QFileDialog.getOpenFileName(self, "Apri cantiere", self._cartella_iniziale(), self.filtro)
        if percorso:
            self.apri_file(percorso)

    def nuovo_da_psc(self) -> None:
        from sicurcantiere.ui import importa_psc

        if licenza_ui.stato_corrente(self.edizione.chiave).utilizzabile:
            importa_psc.avvia(self)

    def apri_file(self, percorso: str | Path) -> None:
        if not licenza_ui.consenti_cantiere(self, self.edizione.chiave, Path(percorso)):
            return
        try:
            progetto = Progetto(percorso)
        except (ErroreProgetto, OSError) as e:
            QMessageBox.critical(self, "Impossibile aprire il cantiere", str(e))
            return
        self._carica(progetto)

    def salva_con_nome(self) -> None:
        if not self.progetto:
            return
        self._salva_in_sospeso()
        percorso, _ = QFileDialog.getSaveFileName(
            self, "Salva con nome", str(self.progetto.percorso.with_suffix(self.edizione.estensione)), self.filtro
        )
        if not percorso:
            return
        percorso = Path(percorso)
        if percorso.suffix.lower() not in ESTENSIONI:
            percorso = percorso.with_suffix(self.edizione.estensione)
        if percorso.resolve() == self.progetto.percorso.resolve():
            return  # Il progetto è già salvato automaticamente.
        try:
            if percorso.exists():
                percorso.unlink()
            self.progetto.salva_con_nome(percorso)
        except OSError as e:
            QMessageBox.critical(self, "Salvataggio non riuscito", str(e))
            return
        self.apri_file(percorso)

    def salva(self) -> None:
        """Scrive subito nel file anche i campi in modifica (il resto è già salvato)."""
        if not self.progetto:
            return
        self._salva_in_sospeso()
        self.progetto.conn.commit()
        self._modifiche_viste = self.progetto.conn.total_changes
        self.stato_salvataggio.setText(f"Salvato alle {datetime.now():%H:%M:%S}")
        self.statusBar().showMessage("Modifiche salvate nel file del cantiere.", 4000)

    def _salva_in_sospeso(self) -> None:
        for pagina in self.pagine:
            pagina.salva_in_sospeso()

    def _carica(self, progetto: Progetto) -> None:
        self._chiudi_progetto()
        self.progetto = progetto
        self._modifiche_viste = progetto.conn.total_changes
        repo = Repository(progetto)
        benvenuto = self.contenitore.widget(0)
        self.contenitore.removeWidget(benvenuto)
        benvenuto.deleteLater()
        self.navigazione.blockSignals(True)
        self.navigazione.clear()
        self.navigazione.blockSignals(False)
        for classe in self.edizione.pagine:
            pagina = classe(repo)
            self.pagine.append(pagina)
            self.contenitore.addWidget(pagina)
        self._popola_navigazione()
        self.suggerimento_navigazione.hide()
        self.nome_cantiere.show()
        self.luogo_cantiere.show()
        self.navigazione.setEnabled(True)
        self.navigazione.setCurrentRow(0)
        for a in self.azioni_progetto:
            a.setEnabled(True)
        self._aggiungi_recente(progetto.percorso)
        self.setWindowTitle(f"{progetto.percorso.name} - {self.edizione.nome}")
        self.stato_file.setText(str(progetto.percorso))
        self.stato_salvataggio.setText("Salvataggio automatico attivo")
        self._timer_stato.start()
        self._aggiorna_stato()

    def _mostra_benvenuto(self) -> None:
        while self.contenitore.count():
            w = self.contenitore.widget(0)
            self.contenitore.removeWidget(w)
            w.deleteLater()
        self.contenitore.addWidget(Benvenuto(self, self._recenti()))

    def _chiudi_progetto(self) -> None:
        self._salva_in_sospeso()
        self._timer_stato.stop()
        self.navigazione.blockSignals(True)
        self.navigazione.clear()
        self.navigazione.blockSignals(False)
        self.pagine = []
        self._mostra_benvenuto()
        if self.progetto:
            self.progetto.chiudi()
            self.progetto = None
        self._popola_navigazione()
        self.navigazione.setEnabled(False)
        self.nome_cantiere.hide()
        self.luogo_cantiere.hide()
        self.suggerimento_navigazione.show()
        for a in self.azioni_progetto:
            a.setEnabled(False)
        self.setWindowTitle(self.edizione.nome)
        self.stato_file.setText("Nessun cantiere aperto")
        self.stato_salvataggio.setText("")
        self.stato_controlli.hide()

    def _popola_navigazione(self) -> None:
        """Voci numerate della barra laterale, una per pagina del programma."""
        self.navigazione.blockSignals(True)
        self.navigazione.clear()
        for n, classe in enumerate(self.edizione.pagine, start=1):
            item = QListWidgetItem(classe.voce or classe.titolo)
            item.setData(Qt.ItemDataRole.UserRole, n)
            self.navigazione.addItem(item)
        self.navigazione.blockSignals(False)

    def _mostra_pagina(self, indice: int) -> None:
        if not (0 <= indice < len(self.pagine)):
            return
        self._salva_in_sospeso()
        self.contenitore.setCurrentWidget(self.pagine[indice])
        self.pagine[indice].aggiorna()
        self._aggiorna_stato()

    def _pagina_principale(self) -> Pagina | None:
        """Pagina che genera il documento principale e mostra i controlli."""
        return next((p for p in self.pagine if type(p).genera_principale is not Pagina.genera_principale), None)

    def _vai_ai_controlli(self) -> None:
        pagina = self._pagina_principale()
        if pagina is not None:
            self.navigazione.setCurrentRow(self.pagine.index(pagina))

    def vai_a_sezione(self, sezione: str) -> None:
        """Mostra la pagina a cui appartiene una sezione dei controlli."""
        for r, pagina in enumerate(self.pagine):
            if sezione in pagina.sezioni_controlli:
                self.navigazione.setCurrentRow(r)
                return
        for r, pagina in enumerate(self.pagine):
            if "*" in pagina.sezioni_controlli:
                self.navigazione.setCurrentRow(r)
                return

    def _genera_principale(self) -> None:
        pagina = self._pagina_principale()
        if pagina is not None:
            self._salva_in_sospeso()
            self.navigazione.setCurrentRow(self.pagine.index(pagina))
            pagina.genera_principale()

    def _aggiorna_stato(self) -> None:
        """Aggiorna l'ora dell'ultimo salvataggio e il riepilogo dei controlli."""
        if not self.progetto:
            return
        modifiche = self.progetto.conn.total_changes
        if modifiche != self._modifiche_viste:
            self._modifiche_viste = modifiche
            self.stato_salvataggio.setText(f"✓ Salvato alle {datetime.now():%H:%M:%S}")
        elenco = self.edizione.controlla(self.pagine[0].repo) if self.pagine else []
        errori = sum(1 for s in elenco if s.livello == controlli.ERRORE)
        avvisi = len(elenco) - errori
        testo_avvisi = f"{avvisi} avviso" if avvisi == 1 else f"{avvisi} avvisi"
        if errori:
            livello = "error"
            testo = (f"{errori} errore" if errori == 1 else f"{errori} errori") + f" · {testo_avvisi}"
        elif avvisi:
            livello, testo = "warning", testo_avvisi
        else:
            livello, testo = "ok", "Nessun problema"
        self.stato_controlli.setText(testo)
        self.stato_controlli.show()
        if self.stato_controlli.property("level") != livello:
            self.stato_controlli.setProperty("level", livello)
            self.stato_controlli.style().unpolish(self.stato_controlli)
            self.stato_controlli.style().polish(self.stato_controlli)
        self._aggiorna_navigazione(elenco)

    def _aggiorna_navigazione(self, elenco: list[controlli.Segnalazione]) -> None:
        """Nome del cantiere e problemi di ogni pagina nella barra laterale."""
        if not self.pagine:
            return
        c = self.pagine[0].repo.cantiere()
        self.nome_cantiere.setText(c["nome"] or self.progetto.percorso.stem)
        self.luogo_cantiere.setText(" ".join(v for v in (c["comune"], f"({c['provincia']})" if c["provincia"]
                                                         else "") if v))
        dichiarate = {s for p in self.pagine for s in p.sezioni_controlli}
        for r, pagina in enumerate(self.pagine):
            proprie = [s for s in elenco if s.sezione in pagina.sezioni_controlli
                       or ("*" in pagina.sezioni_controlli and s.sezione not in dichiarate)]
            if not pagina.sezioni_controlli:
                stato = None
            elif any(s.livello == controlli.ERRORE for s in proprie):
                stato = "error"
            else:
                stato = "warning" if proprie else "done"
            item = self.navigazione.item(r)
            if item is not None and (item.data(Qt.ItemDataRole.UserRole + 1), item.data(Qt.ItemDataRole.UserRole + 2)) \
                    != (stato, len(proprie)):
                item.setData(Qt.ItemDataRole.UserRole + 1, stato)
                item.setData(Qt.ItemDataRole.UserRole + 2, len(proprie))

    def closeEvent(self, evento) -> None:
        self._chiudi_progetto()
        self.impostazioni.setValue("geometria", self.saveGeometry())
        super().closeEvent(evento)
