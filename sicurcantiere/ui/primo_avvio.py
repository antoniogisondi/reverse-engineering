"""Panoramica al primo avvio: quattro schermate che spiegano come si lavora con il programma.
Si rivede da «Aiuto > Panoramica del programma»."""

from __future__ import annotations

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere.ui import tema

CHIAVE_VISTA = "primo_avvio/vista"


def _schermate(nome: str, documento: str) -> list[tuple[str, str]]:
    return [
        (f"Benvenuto in {nome}",
         f"{nome} ti accompagna nella redazione del {documento} e dei documenti collegati, dai dati del cantiere "
         "fino al documento firmato. Ogni cantiere è un file che puoi salvare dove preferisci, anche in una "
         "cartella condivisa dello studio."
         "<br><br>Per iniziare: <b>File &gt; Nuovo cantiere</b>, oppure <b>Nuovo da modello</b> per ripartire "
         "da un cantiere simile già fatto."),
        ("Le pagine a sinistra",
         "Le pagine seguono l'ordine del lavoro: dati generali, soggetti, imprese, lavorazioni e così via. Il "
         "numero accanto a ogni pagina indica quante cose restano da sistemare; quando la pagina è completa compare "
         "la spunta verde."
         "<br><br>Il salvataggio è automatico. <b>Ctrl+Z</b> annulla l'ultima operazione, anche un'eliminazione; "
         "<b>Ctrl+F</b> cerca in tutto il cantiere."),
        ("Il documento",
         f"Dalla pagina dei documenti componi la <b>bozza</b> del {documento}: resta salvata nel cantiere, con la "
         "scritta BOZZA e i dati mancanti evidenziati in giallo. Il riquadro «Dati da completare» porta "
         "direttamente alla pagina in cui si compila ogni dato."
         "<br><br>Quando è tutto pronto la <b>emetti</b>: diventa la revisione definitiva, che puoi vedere in "
         "anteprima, esportare in Word o in PDF e segnare come consegnata."),
        ("Assistente e licenza",
         "L'assistente AI propone rischi, misure e testi a partire dai dati del cantiere; si attiva in "
         "<b>Strumenti &gt; Impostazioni assistente AI</b> ed è incluso nella licenza. I suoi suggerimenti vanno "
         "sempre verificati."
         "<br><br>La licenza si inserisce in <b>Aiuto &gt; Licenza</b>. La guida completa è in <b>Aiuto &gt; "
         "Guida</b>."),
    ]


class DialogoPrimoAvvio(QDialog):
    def __init__(self, nome: str, documento: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(f"Panoramica di {nome}")
        self.setMinimumSize(620, 380)
        self.pila = QStackedWidget(self)
        schermate = _schermate(nome, documento)
        for n, (titolo, testo) in enumerate(schermate, 1):
            pagina = QWidget(self.pila)
            lp = QVBoxLayout(pagina)
            passo = QLabel(f"{n} di {len(schermate)}", pagina)
            passo.setObjectName("hint")
            intestazione = QLabel(titolo, pagina)
            intestazione.setObjectName("pageTitle")
            corpo = QLabel(testo, pagina)
            corpo.setWordWrap(True)
            lp.addWidget(passo)
            lp.addWidget(intestazione)
            lp.addSpacing(8)
            lp.addWidget(corpo)
            lp.addStretch()
            self.pila.addWidget(pagina)
        self.non_mostrare = QCheckBox("Non mostrare più all'avvio", self)
        self.non_mostrare.setChecked(True)
        self.indietro = QPushButton("Indietro", self)
        self.avanti = QPushButton("Avanti", self)
        tema.imposta_variante(self.avanti, "primary")
        self.indietro.clicked.connect(lambda: self._vai(-1))
        self.avanti.clicked.connect(lambda: self._vai(1))
        basso = QHBoxLayout()
        basso.addWidget(self.non_mostrare)
        basso.addStretch()
        basso.addWidget(self.indietro)
        basso.addWidget(self.avanti)
        layout = QVBoxLayout(self)
        layout.addWidget(self.pila, 1)
        layout.addLayout(basso)
        self._aggiorna()

    def _vai(self, passo: int) -> None:
        indice = self.pila.currentIndex() + passo
        if indice >= self.pila.count():
            self.accept()
            return
        self.pila.setCurrentIndex(max(0, indice))
        self._aggiorna()

    def _aggiorna(self) -> None:
        ultima = self.pila.currentIndex() == self.pila.count() - 1
        self.indietro.setEnabled(self.pila.currentIndex() > 0)
        self.avanti.setText("Inizia" if ultima else "Avanti")

    def done(self, risultato: int) -> None:
        QSettings().setValue(CHIAVE_VISTA, self.non_mostrare.isChecked())
        super().done(risultato)


def da_mostrare() -> bool:
    return not QSettings().value(CHIAVE_VISTA, False, type=bool)
