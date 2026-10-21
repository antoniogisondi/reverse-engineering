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
from sicurcantiere.ui import archivio_anagrafiche, tema
from sicurcantiere.ui.edizioni import ESTENSIONI, PSC, Edizione
from sicurcantiere.ui.icone import icona, icona_applicazione
from sicurcantiere.ui.lavoro_ai import DialogoImpostazioniAI
from sicurcantiere.ui.pagine import Pagina, primario

MAX_RECENTI = 8
INTERVALLO_STATO_MS = 3000


class SchedaRecente(QPushButton):
    """Scheda cliccabile di un cantiere recente."""

    def __init__(self, percorso: str, colore_icona: str):
        super().__init__()
        self.setObjectName("schedaRecente")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.percorso = percorso
        dati = anteprima(percorso) or {}
        file = Path(percorso)
        nome = dati.get("nome") or file.stem
        luogo = " ".join(v for v in (dati.get("comune", ""),
                                      f"({dati['provincia']})" if dati.get("provincia") else "") if v)
        try:
            modificato = f"modificato il {datetime.fromtimestamp(file.stat().st_mtime):%d/%m/%Y %H:%M}"
        except OSError:
            modificato = ""
        self.setToolTip(percorso)

        icona_lbl = QLabel()
        icona_lbl.setPixmap(icona("cantiere", colore_icona, 32).pixmap(32, 32))
        titolo = QLabel(nome)
        titolo.setObjectName("schedaTitolo")
        dettagli = QLabel(" · ".join(v for v in (luogo, modificato) if v))
        dettagli.setObjectName("sottotitolo")
        dettagli.setWordWrap(True)
        nome_file = QLabel(file.name)
        nome_file.setObjectName("sottotitolo")
        testi = QVBoxLayout()
        testi.setSpacing(2)
        for w in (titolo, dettagli, nome_file):
            testi.addWidget(w)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(icona_lbl, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(testi, 1)
        for w in (icona_lbl, titolo, dettagli, nome_file):
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setMinimumHeight(78)


class Benvenuto(QWidget):
    COLONNE_RECENTI = 3
    MAX_SCHEDE = 6

    def __init__(self, finestra: FinestraPrincipale, colore_icona: str, recenti: list[str]):
        super().__init__()
        edizione = finestra.edizione
        layout = QVBoxLayout(self)
        layout.addStretch(1)
        logo = QLabel()
        logo.setPixmap(icona_applicazione(edizione.colore).pixmap(96, 96))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        titolo = QLabel(edizione.nome)
        titolo.setObjectName("titoloPagina")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titolo)
        sottotitolo = QLabel(f"{edizione.sottotitolo} - D.Lgs. 81/2008")
        sottotitolo.setObjectName("sottotitolo")
        sottotitolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sottotitolo)
        pulsanti = QHBoxLayout()
        pulsanti.addStretch()
        for testo, nome_icona, azione, evidenziato in (
            ("Nuovo cantiere...", "nuovo", finestra.nuovo, True),
            ("Apri cantiere...", "apri", finestra.apri, False),
        ):
            b = QPushButton(icona(nome_icona, "#FFFFFF" if evidenziato else colore_icona), testo)
            b.setIconSize(QSize(18, 18))
            b.setMinimumWidth(180)
            if evidenziato:
                primario(b)
            b.clicked.connect(azione)
            pulsanti.addWidget(b)
        pulsanti.addStretch()
        layout.addSpacing(20)
        layout.addLayout(pulsanti)

        if recenti:
            layout.addSpacing(36)
            contenitore = QWidget()
            contenitore.setMaximumWidth(1000)
            griglia = QGridLayout(contenitore)
            griglia.setContentsMargins(0, 0, 0, 0)
            griglia.setSpacing(12)
            intestazione = QLabel("Cantieri recenti")
            intestazione.setObjectName("schedaTitolo")
            griglia.addWidget(intestazione, 0, 0, 1, self.COLONNE_RECENTI)
            for n, percorso in enumerate(recenti[:self.MAX_SCHEDE]):
                scheda = SchedaRecente(percorso, colore_icona)
                scheda.clicked.connect(lambda _=False, p=percorso: finestra.apri_file(p))
                griglia.addWidget(scheda, 1 + n // self.COLONNE_RECENTI, n % self.COLONNE_RECENTI)
            for c in range(self.COLONNE_RECENTI):
                griglia.setColumnStretch(c, 1)
            riga = QHBoxLayout()
            riga.addStretch()
            riga.addWidget(contenitore, 4)
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
        self.colori = tema.colori(self.scuro)
        self._modifiche_viste = 0

        # Barra laterale: nome del programma ed elenco delle sezioni.
        self.navigazione = QListWidget()
        self.navigazione.setObjectName("navigazione")
        self.navigazione.setIconSize(QSize(20, 20))
        self.navigazione.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.navigazione.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.navigazione.currentRowChanged.connect(self._mostra_pagina)
        marchio = QLabel(self.edizione.nome)
        marchio.setObjectName("marchio")
        laterale = QFrame()
        laterale.setFixedWidth(220)
        lay_laterale = QVBoxLayout(laterale)
        lay_laterale.setContentsMargins(0, 0, 0, 0)
        lay_laterale.setSpacing(0)
        lay_laterale.addWidget(marchio)
        lay_laterale.addWidget(self.navigazione, 1)

        self.contenitore = QStackedWidget()
        contenuto = QWidget()
        lay_contenuto = QVBoxLayout(contenuto)
        lay_contenuto.setContentsMargins(16, 10, 16, 10)
        lay_contenuto.addWidget(self.contenitore)

        centrale = QWidget()
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
        self.azione_psc = self._azione(self.edizione.azione_principale, self._genera_principale, "Ctrl+P")
        self.azione_controlli = self._azione("&Controlli", self._vai_ai_controlli, "F7",
                                             "Mostra i controlli di completezza")
        self.azione_tema = self._azione("Tema &scuro", self._cambia_tema)
        self.azione_tema.setCheckable(True)
        self.azione_tema.setChecked(self.scuro)
        self.azione_info = self._azione("&Informazioni", self._informazioni)
        self.azione_ai = self._azione("Impostazioni assistente &AI...", lambda: DialogoImpostazioniAI(self).exec())
        self.azione_archivio = self._azione("Archivio &anagrafiche...", lambda: archivio_anagrafiche.gestisci(self))
        self.azioni_progetto = [self.azione_salva, self.azione_salva_con_nome, self.azione_chiudi,
                                self.azione_psc, self.azione_controlli]

    def _crea_menu(self) -> None:
        menu = self.menuBar().addMenu("&File")
        menu.addAction(self.azione_nuovo)
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
        barra.addAction(self.azione_controlli)
        spaziatore = QWidget()
        spaziatore.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        barra.addWidget(spaziatore)
        barra.addAction(self.azione_tema)
        self.addToolBar(barra)
        self.barra_strumenti = barra

    def _crea_barra_stato(self) -> None:
        self.stato_file = QLabel()
        self.stato_salvataggio = QLabel()
        self.stato_controlli = QPushButton()
        self.stato_controlli.setFlat(True)
        self.stato_controlli.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stato_controlli.setStyleSheet("QPushButton { border: none; padding: 2px 8px; }")
        self.stato_controlli.clicked.connect(self._vai_ai_controlli)
        barra = self.statusBar()
        barra.setSizeGripEnabled(False)
        barra.addWidget(self.stato_file, 1)
        barra.addPermanentWidget(self.stato_salvataggio)
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
        for r in range(self.navigazione.count()):
            item = self.navigazione.item(r)
            item.setIcon(icona(item.data(Qt.ItemDataRole.UserRole), self.colori.primario_testo))

    def _cambia_tema(self) -> None:
        self.scuro = self.azione_tema.isChecked()
        self.impostazioni.setValue("tema_scuro", self.scuro)
        app = QApplication.instance()
        if app is not None:
            self.colori = tema.applica(app, self.scuro)
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

    def _informazioni(self) -> None:
        QMessageBox.about(
            self, "Informazioni",
            f"<b>{self.edizione.nome} {__version__}</b><br>"
            f"{self.edizione.sottotitolo}, secondo il D.Lgs. 81/2008.<br><br>"
            "I contenuti generati vanno sempre verificati dal coordinatore.",
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

    def apri_file(self, percorso: str | Path) -> None:
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
        for classe in self.edizione.pagine:
            pagina = classe(repo)
            self.pagine.append(pagina)
            self.contenitore.addWidget(pagina)
            item = QListWidgetItem(classe.voce or classe.titolo)
            item.setData(Qt.ItemDataRole.UserRole, classe.icona)
            item.setIcon(icona(classe.icona, self.colori.primario_testo))
            self.navigazione.addItem(item)
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
        self.contenitore.addWidget(Benvenuto(self, self.colori.icone, self._recenti()))

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
        self.navigazione.setEnabled(False)
        for a in self.azioni_progetto:
            a.setEnabled(False)
        self.setWindowTitle(self.edizione.nome)
        self.stato_file.setText("Nessun cantiere aperto")
        self.stato_salvataggio.setText("")
        self.stato_controlli.setText("")
        self.stato_controlli.setIcon(icona("controlli", self.colori.testo_debole))

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
            self.stato_salvataggio.setText(f"Salvato alle {datetime.now():%H:%M:%S}")
        elenco = self.edizione.controlla(self.pagine[0].repo) if self.pagine else []
        errori = sum(1 for s in elenco if s.livello == controlli.ERRORE)
        avvisi = len(elenco) - errori
        testo_avvisi = f"{avvisi} avviso" if avvisi == 1 else f"{avvisi} avvisi"
        if errori:
            colore = "#C0392B"
            testo = (f"{errori} errore" if errori == 1 else f"{errori} errori") + f", {testo_avvisi}"
        elif avvisi:
            colore, testo = "#B9770E", testo_avvisi
        else:
            colore, testo = "#27AE60", "Nessun problema"
        self.stato_controlli.setText(testo)
        self.stato_controlli.setIcon(icona("controlli", colore))
        self.stato_controlli.setStyleSheet(
            f"QPushButton {{ border: none; padding: 2px 8px; color: {colore}; font-weight: 600; }}")

    def closeEvent(self, evento) -> None:
        self._chiudi_progetto()
        self.impostazioni.setValue("geometria", self.saveGeometry())
        super().closeEvent(evento)
