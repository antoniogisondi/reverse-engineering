"""Finestra «Cerca nel cantiere» (Ctrl+F): cerca mentre si scrive e porta alla pagina del risultato."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout

from sicurcantiere import ricerca
from sicurcantiere.repository import Repository


class DialogoRicerca(QDialog):
    def __init__(self, repo: Repository, vai_a_sezione, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.vai_a_sezione = vai_a_sezione
        self.setWindowTitle("Cerca nel cantiere")
        self.resize(720, 520)
        self.campo = QLineEdit(self)
        self.campo.setPlaceholderText("Cerca fasi, rischi, attrezzature, imprese, lavoratori, testi...")
        self.campo.setClearButtonEnabled(True)
        self.esito = QLabel(self)
        self.esito.setObjectName("hint")
        self.elenco = QListWidget(self)
        self.elenco.setSpacing(2)
        self.elenco.itemActivated.connect(self._apri)
        self.elenco.itemDoubleClicked.connect(self._apri)
        self._timer = QTimer(self, singleShot=True, interval=250)
        self._timer.timeout.connect(self._cerca)
        self.campo.textChanged.connect(lambda _: self._timer.start())
        self.campo.returnPressed.connect(self._primo)
        layout = QVBoxLayout(self)
        layout.addWidget(self.campo)
        layout.addWidget(self.esito)
        layout.addWidget(self.elenco, 1)
        self.esito.setText("Scrivi almeno due lettere. Doppio clic o Invio su un risultato per andare alla pagina.")

    def _cerca(self) -> None:
        self.elenco.clear()
        testo = self.campo.text()
        risultati = ricerca.cerca(self.repo, testo)
        for r in risultati:
            voce = QListWidgetItem(f"{r.tipo} · {r.titolo}\n{r.dettaglio}")
            voce.setData(Qt.ItemDataRole.UserRole, r.sezione)
            voce.setToolTip("Doppio clic per andare alla pagina")
            self.elenco.addItem(voce)
        if len(testo.strip()) < 2:
            self.esito.setText("Scrivi almeno due lettere. Doppio clic o Invio su un risultato per andare alla pagina.")
        else:
            self.esito.setText("Nessun risultato." if not risultati else
                               f"{len(risultati)} risultat{'o' if len(risultati) == 1 else 'i'}.")

    def _primo(self) -> None:
        self._cerca()
        if self.elenco.count():
            self._apri(self.elenco.item(0))

    def _apri(self, voce: QListWidgetItem) -> None:
        sezione = voce.data(Qt.ItemDataRole.UserRole)
        if sezione:
            self.vai_a_sezione(sezione)
            self.accept()
