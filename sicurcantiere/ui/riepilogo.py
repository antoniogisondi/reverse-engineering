"""Riquadri di riepilogo del cantiere (pagina Dati generali)."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from sicurcantiere import analisi, controlli
from sicurcantiere.documenti.comune import data_it, euro
from sicurcantiere.repository import Repository

# Stati dei riquadri: determinano il colore del bordo sinistro (vedi tema.py).
OK, ATTENZIONE, ERRORE, NEUTRO = "ok", "attenzione", "errore", "neutro"


@dataclass(frozen=True)
class Voce:
    chiave: str
    titolo: str
    valore: str
    nota: str = ""
    stato: str = NEUTRO


def calcola(repo: Repository) -> list[Voce]:
    c = repo.cantiere()
    fasi = repo.elenco("fasi")
    imprese = repo.elenco("imprese")
    rischi = repo.elenco("rischi")
    costi = analisi.totale_costi(repo.elenco("costi"))
    periodo = analisi.periodo_lavori(fasi)
    ug = analisi.uomini_giorno(fasi)
    obblighi = analisi.obblighi(imprese, fasi)
    interferenze = analisi.interferenze(fasi, analisi.livelli_fasi(rischi))
    prescrizioni = repo.prescrizioni()
    gravi = [i for i in interferenze if i.gravita >= 6]
    scoperte = [i for i in gravi if not prescrizioni.get(i.chiave, "").strip()]
    segnalazioni = controlli.controlla(repo)
    errori = sum(1 for s in segnalazioni if s.livello == controlli.ERRORE)
    avvisi = len(segnalazioni) - errori

    incidenza = f" ({costi / c['importo_lavori'] * 100:.1f}%)".replace(".", ",") if c["importo_lavori"] else ""
    return [
        Voce("importo", "Importo dei lavori", euro(c["importo_lavori"]),
             f"Costi della sicurezza: {euro(costi)}{incidenza}"),
        Voce("durata", "Durata dei lavori",
             f"{analisi.giorni_lavorativi(*periodo)} gg lavorativi" if periodo else "-",
             f"{data_it(periodo[0])} - {data_it(periodo[1])}" if periodo else "Date delle fasi mancanti",
             NEUTRO if periodo else ATTENZIONE),
        Voce("uomini_giorno", "Entità del cantiere", f"{ug} uomini-giorno",
             f"Soglia per la notifica: {analisi.SOGLIA_UOMINI_GIORNO}",
             ATTENZIONE if ug >= analisi.SOGLIA_UOMINI_GIORNO else NEUTRO),
        Voce("picco", "Picco di lavoratori", str(analisi.picco_lavoratori(fasi)), "presenti contemporaneamente"),
        Voce("imprese", "Imprese esecutrici", str(obblighi.imprese),
             f"{len(imprese)} soggetti in elenco"),
        Voce("interferenze", "Interferenze", str(len(interferenze)),
             f"{len(gravi)} gravi, {len(scoperte)} senza prescrizioni" if interferenze else "Nessuna contemporaneità",
             ERRORE if scoperte else ATTENZIONE if interferenze else OK),
        Voce("psc", "PSC e coordinatori", "Obbligatori" if obblighi.psc else "Non obbligatori",
             "art. 90 c. 3-4 (più imprese)" if obblighi.psc else "Una sola impresa esecutrice",
             ATTENZIONE if obblighi.psc else OK),
        Voce("notifica", "Notifica preliminare", "Obbligatoria" if obblighi.notifica else "Non obbligatoria",
             "art. 99 D.Lgs. 81/2008", ATTENZIONE if obblighi.notifica else OK),
        Voce("controlli", "Controlli", "Nessun problema" if not segnalazioni else
             (f"{errori} errori" if errori != 1 else "1 errore") if errori else
             (f"{avvisi} avvisi" if avvisi != 1 else "1 avviso"),
             f"{avvisi} avvisi" if errori else "Pagina Documenti e controlli",
             ERRORE if errori else ATTENZIONE if avvisi else OK),
    ]


class Tessera(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("tessera")
        self.titolo = QLabel()
        self.titolo.setObjectName("tesseraTitolo")
        self.valore = QLabel()
        self.valore.setObjectName("tesseraValore")
        self.nota = QLabel()
        self.nota.setObjectName("tesseraNota")
        self.nota.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 12, 10)
        layout.setSpacing(2)
        layout.addWidget(self.titolo)
        layout.addWidget(self.valore)
        layout.addWidget(self.nota)

    def imposta(self, voce: Voce) -> None:
        self.titolo.setText(voce.titolo.upper())
        self.valore.setText(voce.valore)
        self.nota.setText(voce.nota)
        if self.property("stato") != voce.stato:
            self.setProperty("stato", voce.stato)
            # Riapplica il foglio di stile per il nuovo valore della proprietà.
            self.style().unpolish(self)
            self.style().polish(self)


class Riepilogo(QWidget):
    COLONNE = 3

    def __init__(self) -> None:
        super().__init__()
        self.griglia = QGridLayout(self)
        self.griglia.setContentsMargins(0, 0, 0, 0)
        self.griglia.setSpacing(10)
        self.tessere: dict[str, Tessera] = {}

    def aggiorna(self, repo: Repository) -> None:
        for n, voce in enumerate(calcola(repo)):
            tessera = self.tessere.get(voce.chiave)
            if tessera is None:
                tessera = self.tessere[voce.chiave] = Tessera()
                self.griglia.addWidget(tessera, n // self.COLONNE, n % self.COLONNE)
            tessera.imposta(voce)
