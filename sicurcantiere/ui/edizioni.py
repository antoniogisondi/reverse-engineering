"""I programmi della famiglia SicurCantiere.

Condividono archivi, motore dei documenti e interfaccia; ognuno ha le sue
pagine, la sua estensione di file e i suoi controlli:

- SicurCantiere PSC: coordinatore (PSC, fascicolo dell'opera, notifica preliminare);
- SicurCantiere POS: impresa esecutrice (POS, valutazioni dei rischi specifici, DPI);
- SicurCantiere PiMUS: ponteggi.

I file hanno la stessa struttura interna, quindi ogni programma può aprire
anche i file degli altri (per esempio il POS può partire dal file del PSC).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from sicurcantiere import controlli, pimus
from sicurcantiere.repository import Repository
from sicurcantiere.ui.pagine import (
    Pagina,
    PaginaCosti,
    PaginaDatiGenerali,
    PaginaDocumenti,
    PaginaFascicolo,
    PaginaFasi,
    PaginaImprese,
    PaginaInterferenze,
    PaginaRelazione,
    PaginaSoggetti,
)
from sicurcantiere.ui.ponteggi import PaginaPonteggi
from sicurcantiere.ui.riepilogo import calcola_pos
from sicurcantiere.ui.sostanze import PaginaSostanze
from sicurcantiere.ui.valutazioni import PaginaValutazioni


@dataclass(frozen=True)
class Edizione:
    chiave: str
    nome: str
    sottotitolo: str
    estensione: str
    descrizione_file: str
    colore: str
    pagine: tuple[type[Pagina], ...]
    azione_principale: str  # testo del pulsante nella barra degli strumenti
    controlla: Callable[[Repository], list[controlli.Segnalazione]]


# --- PSC: solo quanto serve al coordinatore ---

class PaginaImpresePSC(PaginaImprese):
    titolo = "Imprese e lavoratori autonomi"
    voce = "Imprese"
    schede_visibili = ()


class PaginaDocumentiPSC(PaginaDocumenti):
    documenti = ("psc", "fascicolo", "notifica")
    principale = "psc"


# --- POS: dal punto di vista dell'impresa esecutrice ---

class PaginaCantierePOS(PaginaDatiGenerali):
    titolo = "Cantiere"
    voce = "Cantiere"
    funzione_riepilogo = staticmethod(calcola_pos)

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.foto = FotoCantiere(repo)
        self.layout_.addWidget(self.foto)

    def aggiorna(self) -> None:
        super().aggiorna()
        self.foto.aggiorna()


class FotoCantiere(QGroupBox):
    """Foto del cantiere riportate nel POS (capitolo «Lavoro»)."""

    def __init__(self, repo: Repository):
        super().__init__("Foto del cantiere (nel POS)")
        self.repo = repo
        self.elenco = QListWidget()
        self.elenco.setIconSize(QSize(96, 72))
        self.elenco.setMaximumHeight(110)
        self.elenco.setFlow(QListWidget.LeftToRight)
        self.elenco.setToolTip("Le foto restano nella loro cartella: il file del cantiere ne conserva il percorso.")
        aggiungi = QPushButton("Aggiungi foto...")
        aggiungi.clicked.connect(self._aggiungi)
        rimuovi = QPushButton("Rimuovi")
        rimuovi.clicked.connect(self._rimuovi)
        pulsanti = QHBoxLayout()
        pulsanti.addWidget(aggiungi)
        pulsanti.addWidget(rimuovi)
        pulsanti.addStretch()
        layout = QVBoxLayout(self)
        layout.addWidget(self.elenco)
        layout.addLayout(pulsanti)

    def percorsi(self) -> list[str]:
        return [r for r in self.repo.testo("foto_cantiere").splitlines() if r.strip()]

    def aggiorna(self) -> None:
        self.elenco.clear()
        for percorso in self.percorsi():
            voce = QListWidgetItem(QIcon(percorso), Path(percorso).name)
            voce.setToolTip(percorso if Path(percorso).is_file() else f"{percorso}\n(file non trovato)")
            self.elenco.addItem(voce)

    def _aggiungi(self) -> None:
        file, _ = QFileDialog.getOpenFileNames(self, "Foto del cantiere", "", "Immagini (*.png *.jpg *.jpeg *.bmp)")
        if file:
            self.repo.salva_testo("foto_cantiere", "\n".join(dict.fromkeys(self.percorsi() + file)))
            self.aggiorna()

    def _rimuovi(self) -> None:
        riga = self.elenco.currentRow()
        if riga < 0:
            return
        percorsi = self.percorsi()
        del percorsi[riga]
        self.repo.salva_testo("foto_cantiere", "\n".join(percorsi))
        self.aggiorna()


class PaginaSoggettiPOS(PaginaSoggetti):
    titolo = "Committente, coordinatori e direzione lavori"
    voce = "Committente e CSE"


class PaginaImpresePOS(PaginaImprese):
    titolo = "Impresa, figure della sicurezza e lavoratori"
    voce = "Impresa e lavoratori"


class PaginaFasiPOS(PaginaFasi):
    titolo = "Lavorazioni, rischi, macchine e attrezzature"
    voce = "Lavorazioni e rischi"
    cronoprogramma = False


class PaginaDocumentiPOS(PaginaDocumenti):
    titolo = "POS, modulistica e controlli"
    voce = "POS e controlli"
    documenti = ("pos", "sostanze", "dpi", "tesserini", "schede")
    principale = "pos"
    controlla = staticmethod(controlli.controlla_pos)


# --- PiMUS ---

class PaginaCantierePimus(PaginaDatiGenerali):
    titolo = "Cantiere"
    voce = "Cantiere"
    funzione_riepilogo = None


class PaginaImpresePimus(PaginaImprese):
    titolo = "Impresa che monta il ponteggio"
    voce = "Impresa"
    schede_visibili = ("dati", "figure")


def controlla_pimus(repo: Repository) -> list[controlli.Segnalazione]:
    segnalazioni = []
    c = repo.cantiere()
    if not (c["indirizzo"].strip() and c["comune"].strip()):
        segnalazioni.append(controlli.Segnalazione(controlli.ERRORE, "Cantiere", "Manca l'indirizzo del cantiere."))
    ponteggi = repo.elenco("ponteggi")
    if not ponteggi:
        segnalazioni.append(controlli.Segnalazione(controlli.ERRORE, "Ponteggi", "Nessun ponteggio inserito."))
    for p in ponteggi:
        for messaggio in pimus.avvisi(p):
            segnalazioni.append(controlli.Segnalazione(controlli.AVVISO, p["nome"] or "Ponteggio", messaggio))
    return segnalazioni


PSC = Edizione(
    chiave="psc", nome="SicurCantiere PSC",
    sottotitolo="Piano di sicurezza e coordinamento, fascicolo dell'opera, notifica preliminare",
    estensione=".scs", descrizione_file="Cantiere PSC", colore="#E8792B",
    pagine=(PaginaDatiGenerali, PaginaSoggetti, PaginaImpresePSC, PaginaFasi, PaginaInterferenze,
            PaginaCosti, PaginaRelazione, PaginaFascicolo, PaginaDocumentiPSC),
    azione_principale="Genera PSC", controlla=controlli.controlla,
)

POS = Edizione(
    chiave="pos", nome="SicurCantiere POS",
    sottotitolo="Piano operativo di sicurezza, valutazioni dei rischi specifici, sostanze pericolose, DPI",
    estensione=".spo", descrizione_file="Cantiere POS", colore="#2E86C1",
    pagine=(PaginaCantierePOS, PaginaSoggettiPOS, PaginaImpresePOS, PaginaFasiPOS, PaginaValutazioni,
            PaginaSostanze, PaginaDocumentiPOS),
    azione_principale="Genera POS", controlla=controlli.controlla_pos,
)

PIMUS = Edizione(
    chiave="pimus", nome="SicurCantiere PiMUS",
    sottotitolo="Piano di montaggio, uso e smontaggio dei ponteggi",
    estensione=".spm", descrizione_file="Ponteggi PiMUS", colore="#2E9C8F",
    pagine=(PaginaCantierePimus, PaginaImpresePimus, PaginaPonteggi),
    azione_principale="Genera PiMUS", controlla=controlla_pimus,
)

EDIZIONI: dict[str, Edizione] = {e.chiave: e for e in (PSC, POS, PIMUS)}
ESTENSIONI = tuple(e.estensione for e in EDIZIONI.values())
