"""Finestre dei modelli di cantiere: scelta del modello per un nuovo cantiere e salvataggio del cantiere
aperto come modello."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from sicurcantiere import modelli


class DialogoModelli(QDialog):
    """Elenco dei modelli del programma: se ne sceglie uno per creare un nuovo cantiere."""

    def __init__(self, estensione: str, parent=None):
        super().__init__(parent)
        self.estensione = estensione
        self.setWindowTitle("Nuovo cantiere da un modello")
        self.resize(560, 420)
        guida = QLabel("Scegli il modello da cui partire: il nuovo cantiere ne riprende lavorazioni, rischi, testi "
                       "e costi, da adattare al caso. Per creare un modello apri un cantiere e usa «File > Salva come "
                       "modello...».", self)
        guida.setWordWrap(True)
        guida.setObjectName("hint")
        self.elenco = QListWidget(self)
        self.elenco.itemDoubleClicked.connect(lambda _: self.accept())
        elimina = QPushButton("Elimina il modello", self)
        elimina.clicked.connect(self._elimina)
        self.pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                                         self)
        self.pulsanti.button(QDialogButtonBox.StandardButton.Ok).setText("Crea il cantiere")
        self.pulsanti.button(QDialogButtonBox.StandardButton.Cancel).setText("Annulla")
        self.pulsanti.accepted.connect(self.accept)
        self.pulsanti.rejected.connect(self.reject)
        basso = QHBoxLayout()
        basso.addWidget(elimina)
        basso.addStretch()
        basso.addWidget(self.pulsanti)
        layout = QVBoxLayout(self)
        layout.addWidget(guida)
        layout.addWidget(self.elenco, 1)
        layout.addLayout(basso)
        self._popola()

    def _popola(self) -> None:
        self.elenco.clear()
        for percorso in modelli.elenco(self.estensione):
            voce = QListWidgetItem(percorso.stem)
            voce.setData(Qt.ItemDataRole.UserRole, str(percorso))
            self.elenco.addItem(voce)
        if self.elenco.count():
            self.elenco.setCurrentRow(0)
        else:
            self.elenco.addItem("Nessun modello salvato.")
            self.elenco.item(0).setFlags(Qt.ItemFlag.NoItemFlags)
        self.pulsanti.button(QDialogButtonBox.StandardButton.Ok).setEnabled(self.scelto() is not None)

    def scelto(self) -> Path | None:
        voce = self.elenco.currentItem()
        valore = voce.data(Qt.ItemDataRole.UserRole) if voce else None
        return Path(valore) if valore else None

    def _elimina(self) -> None:
        modello = self.scelto()
        if modello and QMessageBox.question(self, "Elimina il modello", f"Eliminare il modello «{modello.stem}»? "
                                            "I cantieri già creati non cambiano.") == QMessageBox.StandardButton.Yes:
            modelli.elimina(modello)
            self._popola()


def chiedi_nome_modello(parent, proposta: str) -> str | None:
    nome, ok = QInputDialog.getText(parent, "Salva come modello",
                                    "Nome del modello (per esempio «Ristrutturazione di appartamento»):",
                                    text=proposta)
    return nome.strip() if ok and nome.strip() else None
