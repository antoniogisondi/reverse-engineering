"""Vista ad albero della struttura di una fase (lavoratori, attrezzi, macchine, rischi, misure, DPI)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from sicurcantiere import analisi
from sicurcantiere.repository import Repository
from sicurcantiere.struttura import struttura_fase
from sicurcantiere.ui import tema
from sicurcantiere.ui.icone import icona
from sicurcantiere.valutazioni import METODI

GIALLO = QColor("#9A6B00")


class StrutturaFase(QWidget):
    def __init__(self, repo: Repository):
        super().__init__()
        self.repo = repo
        self.albero = QTreeWidget()
        self.albero.setHeaderLabels(["Struttura della fase", "Livello / dettaglio"])
        self.albero.setColumnWidth(0, 520)
        self.albero.setItemDelegateForColumn(1, tema.DelegatoStruttura(self.albero))
        aiuto = QLabel("Riepilogo in sola lettura: rischi, misure e DPI si modificano nelle altre schede; "
                       "i lavoratori si assegnano con «Mansioni...» nella pagina dell'impresa.")
        aiuto.setObjectName("pageSubtitle")
        aiuto.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(aiuto)
        layout.addWidget(self.albero)

    def _nodo(self, padre, testo: str, dettaglio: str = "", nome_icona: str = "", colore: QColor | None = None):
        item = QTreeWidgetItem(padre, [testo, dettaglio])
        if nome_icona:
            item.setIcon(0, icona(nome_icona))
        if colore is not None:
            item.setForeground(0, QBrush(colore))
        return item

    def _rischi(self, padre, rischi: list[dict]) -> None:
        for r in rischi:
            livello = analisi.livello_rischio(r["probabilita"], r["danno"])
            dettaglio = f"{livello} {analisi.classe_rischio(livello)}"
            valutazione = None
            if r.get("valutazione_id"):
                v = self.repo.leggi("valutazioni", r["valutazione_id"])
                if v and v["metodo"] in METODI:
                    esito = METODI[v["metodo"]].esegui(self.repo.dati_valutazione(v["id"]))
                    dettaglio += f" - valutazione: {esito.indice_testo} {esito.classe}"
                    valutazione = (f"{esito.indice_testo} {esito.classe}", esito.colore)
            nodo = self._nodo(padre, r["descrizione"], dettaglio, "interferenze")
            # livello nel riquadro colorato e, accanto, il risultato della valutazione in un secondo riquadro
            nodo.setData(1, Qt.ItemDataRole.UserRole, (livello, valutazione))
            if r["misure"]:
                self._nodo(nodo, "Misure: " + r["misure"], colore=GIALLO)
            if r["dpi"]:
                self._nodo(nodo, "DPI: " + r["dpi"], colore=GIALLO)

    def _attrezzature(self, padre, elenco: list[dict], operatore: bool) -> None:
        for a in elenco:
            nodo = self._nodo(padre, a["nome"], a["tipo"], "cantiere" if operatore else "valutazioni")
            self._rischi(nodo, a["rischi"])
            if a["misure"]:
                self._nodo(nodo, f"{a['nome']}: misure preventive e protettive", a["misure"].replace("\n", " "),
                           colore=GIALLO)
            if a["dpi"]:
                chi = "operatore" if operatore else "utilizzatore"
                self._nodo(nodo, f"DPI: {chi} {a['nome'].lower()}", a["dpi"], colore=GIALLO)

    def mostra(self, fase_id: int | None) -> None:
        self.albero.clear()
        if fase_id is None:
            return
        s = struttura_fase(self.repo, fase_id)
        lavoratori = self._nodo(self.albero, "LAVORATORI", ", ".join(s["lavoratori"]) or "nessuno assegnato",
                                "imprese")
        addetto = self._nodo(lavoratori, s["addetto"], "", "soggetti")
        self._rischi(addetto, s["rischi_lavorazione"])
        if s["attrezzi"]:
            attrezzi = self._nodo(addetto, "ATTREZZI", str(len(s["attrezzi"])), "valutazioni")
            self._attrezzature(attrezzi, s["attrezzi"], operatore=False)
        if s["macchine"]:
            macchine = self._nodo(self.albero, "MACCHINE", str(len(s["macchine"])), "cantiere")
            self._attrezzature(macchine, s["macchine"], operatore=True)
        self.albero.expandToDepth(1)
