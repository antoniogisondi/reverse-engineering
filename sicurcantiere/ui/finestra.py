"""Finestra principale."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import __version__
from sicurcantiere.db import ESTENSIONE, ErroreProgetto, Progetto
from sicurcantiere.repository import Repository
from sicurcantiere.ui.pagine import PAGINE, Pagina

FILTRO = f"Progetti SicurCantiere (*{ESTENSIONE})"
MAX_RECENTI = 8


class Benvenuto(QWidget):
    def __init__(self, finestra: FinestraPrincipale):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addStretch()
        titolo = QLabel("SicurCantiere")
        font = titolo.font()
        font.setPointSizeF(font.pointSizeF() * 2.2)
        font.setBold(True)
        titolo.setFont(font)
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titolo)
        sottotitolo = QLabel("Sicurezza nei cantieri temporanei o mobili - D.Lgs. 81/2008")
        sottotitolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sottotitolo)
        pulsanti = QHBoxLayout()
        pulsanti.addStretch()
        for testo, azione in (("Nuovo cantiere...", finestra.nuovo), ("Apri cantiere...", finestra.apri)):
            b = QPushButton(testo)
            b.setMinimumWidth(160)
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

        self.navigazione = QListWidget()
        self.navigazione.setFixedWidth(200)
        self.navigazione.currentRowChanged.connect(self._mostra_pagina)
        self.contenitore = QStackedWidget()
        centrale = QWidget()
        layout = QHBoxLayout(centrale)
        layout.addWidget(self.navigazione)
        layout.addWidget(self.contenitore, 1)
        self.setCentralWidget(centrale)

        self._crea_menu()
        self._chiudi_progetto()
        self.resize(1200, 800)
        geometria = self.impostazioni.value("geometria")
        if geometria is not None:
            self.restoreGeometry(geometria)

    # --- menu ---

    def _crea_menu(self) -> None:
        menu = self.menuBar().addMenu("&File")
        for testo, scorciatoia, slot in (
            ("&Nuovo cantiere...", QKeySequence.StandardKey.New, self.nuovo),
            ("&Apri...", QKeySequence.StandardKey.Open, self.apri),
        ):
            a = QAction(testo, self, shortcut=scorciatoia)
            a.triggered.connect(slot)
            menu.addAction(a)
        self.azione_salva_con_nome = QAction("Salva &con nome...", self,
                                             shortcut=QKeySequence.StandardKey.SaveAs)
        self.azione_salva_con_nome.triggered.connect(self.salva_con_nome)
        menu.addAction(self.azione_salva_con_nome)
        self.menu_recenti = menu.addMenu("File &recenti")
        self.menu_recenti.aboutToShow.connect(self._popola_recenti)
        self.azione_chiudi = QAction("C&hiudi cantiere", self)
        self.azione_chiudi.triggered.connect(self._chiudi_progetto)
        menu.addAction(self.azione_chiudi)
        menu.addSeparator()
        esci = QAction("&Esci", self, shortcut=QKeySequence.StandardKey.Quit)
        esci.triggered.connect(self.close)
        menu.addAction(esci)

        aiuto = self.menuBar().addMenu("&Aiuto")
        info = QAction("&Informazioni", self)
        info.triggered.connect(self._informazioni)
        aiuto.addAction(info)

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
            salva = getattr(pagina, "salva_in_sospeso", None)
            if salva:
                salva()

    def _carica(self, progetto: Progetto) -> None:
        self._chiudi_progetto()
        self.progetto = progetto
        repo = Repository(progetto)
        benvenuto = self.contenitore.widget(0)
        self.contenitore.removeWidget(benvenuto)
        benvenuto.deleteLater()
        for classe in PAGINE:
            pagina = classe(repo)
            self.pagine.append(pagina)
            self.contenitore.addWidget(pagina)
            self.navigazione.addItem(classe.voce or classe.titolo)
        self.navigazione.setEnabled(True)
        self.navigazione.setCurrentRow(0)
        self.azione_salva_con_nome.setEnabled(True)
        self.azione_chiudi.setEnabled(True)
        self._aggiungi_recente(progetto.percorso)
        self.setWindowTitle(f"{progetto.percorso.name} - SicurCantiere")

    def _chiudi_progetto(self) -> None:
        self._salva_in_sospeso()
        self.navigazione.blockSignals(True)
        self.navigazione.clear()
        self.navigazione.blockSignals(False)
        while self.contenitore.count():
            w = self.contenitore.widget(0)
            self.contenitore.removeWidget(w)
            w.deleteLater()
        self.pagine = []
        if self.progetto:
            self.progetto.chiudi()
            self.progetto = None
        self.contenitore.addWidget(Benvenuto(self))
        self.navigazione.setEnabled(False)
        self.azione_salva_con_nome.setEnabled(False)
        self.azione_chiudi.setEnabled(False)
        self.setWindowTitle("SicurCantiere")

    def _mostra_pagina(self, indice: int) -> None:
        if not (0 <= indice < len(self.pagine)):
            return
        self._salva_in_sospeso()
        self.contenitore.setCurrentWidget(self.pagine[indice])
        self.pagine[indice].aggiorna()

    def closeEvent(self, evento) -> None:
        self._chiudi_progetto()
        self.impostazioni.setValue("geometria", self.saveGeometry())
        super().closeEvent(evento)
