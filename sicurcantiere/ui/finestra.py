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
from sicurcantiere.db import ESTENSIONE, ErroreProgetto, Progetto
from sicurcantiere.repository import Repository
from sicurcantiere.ui import tema
from sicurcantiere.ui.icone import icona
from sicurcantiere.ui.pagine import PAGINE, Pagina, PaginaDocumenti, primario

FILTRO = f"Progetti SicurCantiere (*{ESTENSIONE})"
MAX_RECENTI = 8
INTERVALLO_STATO_MS = 3000


class Benvenuto(QWidget):
    def __init__(self, finestra: FinestraPrincipale, colore_icona: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addStretch()
        logo = QLabel()
        logo.setPixmap(icona("cantiere", colore_icona, 96).pixmap(96, 96))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        titolo = QLabel("SicurCantiere")
        titolo.setObjectName("titoloPagina")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titolo)
        sottotitolo = QLabel("Sicurezza nei cantieri temporanei o mobili - D.Lgs. 81/2008")
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
        layout.addStretch()


class FinestraPrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.navigazione.currentRowChanged.connect(self._mostra_pagina)
        marchio = QLabel("SicurCantiere")
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
        self.azione_salva_con_nome = self._azione(
            "Salva &con nome...", self.salva_con_nome, QKeySequence.StandardKey.SaveAs,
            "Salva una copia del cantiere con un altro nome")
        self.azione_chiudi = self._azione("C&hiudi cantiere", self._chiudi_progetto)
        self.azione_psc = self._azione("Genera &PSC", self._genera_psc, "Ctrl+P",
                                       "Genera il Piano di Sicurezza e Coordinamento")
        self.azione_controlli = self._azione("&Controlli", self._vai_ai_controlli, "F7",
                                             "Mostra i controlli di completezza")
        self.azione_tema = self._azione("Tema &scuro", self._cambia_tema)
        self.azione_tema.setCheckable(True)
        self.azione_tema.setChecked(self.scuro)
        self.azione_info = self._azione("&Informazioni", self._informazioni)
        self.azioni_progetto = [self.azione_salva_con_nome, self.azione_chiudi,
                                self.azione_psc, self.azione_controlli]

    def _crea_menu(self) -> None:
        menu = self.menuBar().addMenu("&File")
        menu.addAction(self.azione_nuovo)
        menu.addAction(self.azione_apri)
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
        for a in (self.azione_nuovo, self.azione_apri, self.azione_salva_con_nome):
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
            (self.azione_salva_con_nome, "salva"), (self.azione_psc, "psc"),
            (self.azione_controlli, "controlli"), (self.azione_tema, "tema"),
            (self.azione_info, "info"),
        ):
            azione.setIcon(icona(nome, c))
        self.setWindowIcon(icona("cantiere", tema.CHIARO.accento, 64))
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
            f"<b>SicurCantiere {__version__}</b><br>"
            "Piani di sicurezza e coordinamento, cronoprogramma e costi della sicurezza "
            "secondo il D.Lgs. 81/2008.<br><br>"
            "I contenuti generati vanno sempre verificati dal coordinatore.",
        )

    # --- gestione progetto ---

    def _cartella_iniziale(self) -> str:
        recenti = self._recenti()
        return str(Path(recenti[0]).parent) if recenti else str(Path.home())

    def nuovo(self) -> None:
        percorso, _ = QFileDialog.getSaveFileName(
            self, "Nuovo cantiere", str(Path(self._cartella_iniziale()) / f"Cantiere{ESTENSIONE}"), FILTRO
        )
        if not percorso:
            return
        percorso = Path(percorso)
        if percorso.suffix.lower() != ESTENSIONE:
            percorso = percorso.with_suffix(ESTENSIONE)
        if self.progetto and percorso.resolve() == self.progetto.percorso.resolve():
            QMessageBox.warning(self, "Nuovo cantiere", "Il file è già aperto: scegliere un altro nome.")
            return
        self._carica(Progetto(percorso, crea=True))

    def apri(self) -> None:
        percorso, _ = QFileDialog.getOpenFileName(self, "Apri cantiere", self._cartella_iniziale(), FILTRO)
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
            self, "Salva con nome", str(self.progetto.percorso), FILTRO
        )
        if not percorso:
            return
        percorso = Path(percorso)
        if percorso.suffix.lower() != ESTENSIONE:
            percorso = percorso.with_suffix(ESTENSIONE)
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
        for classe in PAGINE:
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
        self.setWindowTitle(f"{progetto.percorso.name} - SicurCantiere")
        self.stato_file.setText(str(progetto.percorso))
        self.stato_salvataggio.setText("Salvataggio automatico attivo")
        self._timer_stato.start()
        self._aggiorna_stato()

    def _mostra_benvenuto(self) -> None:
        while self.contenitore.count():
            w = self.contenitore.widget(0)
            self.contenitore.removeWidget(w)
            w.deleteLater()
        self.contenitore.addWidget(Benvenuto(self, self.colori.icone))

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
        self.setWindowTitle("SicurCantiere")
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

    def _pagina_documenti(self) -> PaginaDocumenti | None:
        return next((p for p in self.pagine if isinstance(p, PaginaDocumenti)), None)

    def _vai_ai_controlli(self) -> None:
        pagina = self._pagina_documenti()
        if pagina is not None:
            self.navigazione.setCurrentRow(self.pagine.index(pagina))

    def _genera_psc(self) -> None:
        pagina = self._pagina_documenti()
        if pagina is not None:
            self._salva_in_sospeso()
            pagina._psc()

    def _aggiorna_stato(self) -> None:
        """Aggiorna l'ora dell'ultimo salvataggio e il riepilogo dei controlli."""
        if not self.progetto:
            return
        modifiche = self.progetto.conn.total_changes
        if modifiche != self._modifiche_viste:
            self._modifiche_viste = modifiche
            self.stato_salvataggio.setText(f"Salvato alle {datetime.now():%H:%M:%S}")
        elenco = controlli.controlla(self.pagine[0].repo) if self.pagine else []
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
