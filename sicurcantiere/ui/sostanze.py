"""Pagina delle sostanze e miscele pericolose (programma POS)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QPainter, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import anagrafiche, sds, sostanze
from sicurcantiere.documenti.comune import nome_fase
from sicurcantiere.documenti.sostanze import lavorazioni_sostanza
from sicurcantiere.repository import Repository
from sicurcantiere.ui.lavoro_ai import esegui_ai
from sicurcantiere.ui.pagine import ModuloRecord, Pagina, primario
from sicurcantiere.ui.tabella import Colonna, TabellaCrud

CAMPI_TESTO = ("nome", "produttore", "avvertenza", "stato_fisico", "dpi", "misure", "conservazione")


def immagine_pittogramma(codice: str, lato: int = 64) -> QPixmap:
    """Rombo a bordo rosso con la sigla del pittogramma (rappresentazione semplificata)."""
    pixmap = QPixmap(lato, lato)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    m = lato / 2
    rombo = QPolygonF([QPointF(m, 2), QPointF(lato - 2, m), QPointF(m, lato - 2), QPointF(2, m)])
    p.setPen(QPen(QColor("#D0021B"), lato * 0.07))
    p.setBrush(QColor("#FFFFFF"))
    p.drawPolygon(rombo)
    p.setPen(QColor("#1D2733"))
    font = p.font()
    font.setPixelSize(int(lato * 0.17))
    font.setBold(True)
    p.setFont(font)
    p.drawText(QRectF(0, 0, lato, lato), Qt.AlignmentFlag.AlignCenter, codice)
    p.end()
    return pixmap


class PannelloClassificazione(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.pittogrammi = QHBoxLayout()
        self.pittogrammi.setSpacing(12)
        self.testo = QLabel()
        self.testo.setWordWrap(True)
        self.testo.setTextFormat(Qt.TextFormat.RichText)
        self.testo.setAlignment(Qt.AlignmentFlag.AlignTop)
        contenuto = QWidget()
        lc = QVBoxLayout(contenuto)
        lc.addLayout(self.pittogrammi)
        lc.addWidget(self.testo)
        lc.addStretch()
        scorrimento = QScrollArea()
        scorrimento.setWidgetResizable(True)
        scorrimento.setWidget(contenuto)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scorrimento)

    def mostra(self, testo_codici: str) -> None:
        while self.pittogrammi.count():
            w = self.pittogrammi.takeAt(0).widget()
            if w is not None:
                w.deleteLater()
        codici = sostanze.codici_h(testo_codici)
        for codice in sostanze.pittogrammi(codici):
            riquadro = QWidget()
            lr = QVBoxLayout(riquadro)
            lr.setContentsMargins(0, 0, 0, 0)
            immagine = QLabel()
            immagine.setPixmap(immagine_pittogramma(codice))
            immagine.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nome = QLabel(sostanze.PITTOGRAMMI[codice])
            nome.setObjectName("sottotitolo")
            nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lr.addWidget(immagine)
            lr.addWidget(nome)
            self.pittogrammi.addWidget(riquadro)
        self.pittogrammi.addStretch()
        if not codici:
            self.testo.setText("<i>Inserire le frasi H della scheda di sicurezza (sezione 2), "
                               "per esempio «H315, H317, H318», oppure importare la scheda in PDF.</i>")
            return
        frasi = "".join(f"<tr><td><b>{c}</b></td><td>{sostanze.descrizione(c)}</td></tr>" for c in codici)
        parti = [f"<p><b>Indicazioni di pericolo</b></p><table cellspacing='4'>{frasi}</table>"]
        for categoria in sostanze.categorie(codici):
            colore = "#D93B30" if categoria.grave else "#B9770E"
            misure = "".join(f"<li>{m}</li>" for m in categoria.misure)
            parti.append(f"<p><b style='color:{colore}'>● {categoria.nome}</b></p><ul>{misure}</ul>")
        self.testo.setText("".join(parti))


class DialogoFasi(QDialog):
    """Elenco a spunta delle lavorazioni del cantiere."""

    def __init__(self, repo: Repository, scelte: set[int], titolo: str, intestazione: str,
                 genitore: QWidget | None = None):
        super().__init__(genitore)
        self.setWindowTitle(titolo)
        self.resize(560, 480)
        imprese = {i["id"]: i["ragione_sociale"] for i in repo.elenco("imprese")}
        self.elenco = QListWidget()
        for f in repo.elenco("fasi"):
            testo = nome_fase(f) or f"Fase n. {f['id']}"
            if f["impresa_id"] in imprese:
                testo += f"  ({imprese[f['impresa_id']]})"
            item = QListWidgetItem(testo)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if f["id"] in scelte else Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, f["id"])
            self.elenco.addItem(item)
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        etichetta = QLabel(intestazione)
        etichetta.setWordWrap(True)
        layout.addWidget(etichetta)
        if not self.elenco.count():
            layout.addWidget(QLabel("Inserire prima le lavorazioni nella pagina «Lavorazioni e rischi»."))
        layout.addWidget(self.elenco)
        layout.addWidget(pulsanti)

    def scelte(self) -> list[int]:
        return [self.elenco.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.elenco.count())
                if self.elenco.item(i).checkState() == Qt.CheckState.Checked]


class DialogoLavorazioni(DialogoFasi):
    """Lavorazioni in cui si usa la sostanza."""

    def __init__(self, repo: Repository, sostanza_id: int, genitore: QWidget | None = None):
        sostanza = repo.leggi("sostanze", sostanza_id) or {}
        super().__init__(repo, set(repo.fasi_sostanza(sostanza_id)), "Lavorazioni in cui si usa la sostanza",
                         f"<b>{sostanza.get('nome') or 'Sostanza'}</b>: spuntare tutte le lavorazioni "
                         "in cui viene utilizzata.", genitore)


class PaginaSostanze(Pagina):
    titolo = "Sostanze e miscele pericolose"
    voce = "Sostanze pericolose"
    icona = "sostanze"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.id_: int | None = None
        self.tabella = TabellaCrud(repo, "sostanze", [
            Colonna("nome", "Prodotto", larghezza=220),
            Colonna("impresa_id", "Impresa", "scelta", larghezza=170, scelte=self._imprese),
            Colonna("lavorazioni", "Lavorazioni in cui si usa", "calcolata", larghezza=260,
                    calcola=lambda r: lavorazioni_sostanza(self.repo, r) or "(nessuna)"),
            Colonna("codici_h", "Frasi H", larghezza=180),
            Colonna("avvertenza", "Avvertenza", "scelta", larghezza=100,
                    scelte=lambda: [("", "-"), ("Pericolo", "Pericolo"), ("Attenzione", "Attenzione")]),
            Colonna("data_sds", "Scheda SDS del", "data", larghezza=110),
            Colonna("pittogrammi", "Pittogrammi", "calcolata", calcola=lambda r: ", ".join(
                sostanze.PITTOGRAMMI[p] for p in sostanze.pittogrammi(sostanze.codici_h(r["codici_h"])))),
        ], valori_nuovo=self._valori_nuovo)
        importa = primario(QPushButton("Importa da scheda di sicurezza (PDF)..."))
        importa.clicked.connect(self._importa_pdf)
        self.apri_scheda = QPushButton("Apri la scheda")
        self.apri_scheda.clicked.connect(self._apri_scheda)
        self.tabella.pulsanti.insertWidget(2, importa)
        self.tabella.pulsanti.insertWidget(3, self.apri_scheda)
        self.tabella.aggiungi_pulsante("Lavorazioni...", self._scegli_lavorazioni)
        self.tabella.selezione_cambiata.connect(self._seleziona)
        self.tabella.modificata.connect(self._aggiorna_classificazione)

        self.dati = ModuloRecord(repo, "sostanze", [
            ("produttore", "Produttore / fornitore"),
            ("stato_fisico", "Stato fisico"),
            ("quantita", "Quantità presente in cantiere"),
            ("uso", "Altri usi o note sull'uso"),
            ("conservazione", "Conservazione"),
            ("dpi", "DPI (sezione 8 della scheda)"),
            ("misure", "Misure specifiche"),
        ])
        self.classificazione = PannelloClassificazione()
        self.schede = QTabWidget()
        self.schede.addTab(self.classificazione, "Classificazione e misure")
        self.schede.addTab(self.dati, "Dati del prodotto")
        self.schede.setEnabled(False)

        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(self.tabella)
        divisore.addWidget(self.schede)
        divisore.setSizes([260, 520])
        self.layout_.addWidget(divisore)

    def _imprese(self):
        return [(None, "(da definire)")] + [
            (i["id"], i["ragione_sociale"] or f"Impresa {i['id']}") for i in self.repo.elenco("imprese")
        ]

    def _scegli_lavorazioni(self) -> None:
        if self.id_ is None:
            QMessageBox.information(self, "Lavorazioni", "Selezionare prima la sostanza.")
            return
        dialogo = DialogoLavorazioni(self.repo, self.id_, self)
        if dialogo.exec():
            self.repo.salva_fasi_sostanza(self.id_, dialogo.scelte())
            id_ = self.id_
            self.tabella.ricarica()
            self.tabella.seleziona(id_)

    def _valori_nuovo(self) -> dict:
        imprese = [i for i in self.repo.elenco("imprese") if not anagrafiche.autonomo(i)]
        return {"impresa_id": imprese[0]["id"]} if len(imprese) == 1 else {}

    def _seleziona(self, id_: int | None) -> None:
        self.id_ = id_
        self.schede.setEnabled(id_ is not None)
        self.dati.carica(id_)
        self._aggiorna_classificazione()

    def _aggiorna_classificazione(self) -> None:
        riga = self.repo.leggi("sostanze", self.id_) if self.id_ is not None else None
        self.classificazione.mostra(riga["codici_h"] if riga else "")
        self.apri_scheda.setEnabled(bool(riga and riga["file_sds"] and Path(riga["file_sds"]).exists()))

    def _apri_scheda(self) -> None:
        riga = self.repo.leggi("sostanze", self.id_) if self.id_ is not None else None
        if riga and riga["file_sds"]:
            QDesktopServices.openUrl(QUrl.fromLocalFile(riga["file_sds"]))

    def _importa_pdf(self) -> None:
        percorso, _ = QFileDialog.getOpenFileName(self, "Scheda di dati di sicurezza", "", "PDF (*.pdf)")
        if not percorso:
            return
        try:
            dati, testo = sds.leggi_pdf(percorso)
        except sds.ErroreSDS as e:
            QMessageBox.warning(self, "Scheda di sicurezza", str(e))
            return
        id_ = self.repo.inserisci(
            "sostanze", **self._valori_nuovo(),
            nome=dati.nome or Path(percorso).stem, codici_h=", ".join(dati.codici_h),
            avvertenza=dati.avvertenza, data_sds=dati.data_revisione or None, file_sds=percorso,
        )
        self.tabella.ricarica()
        self.tabella.seleziona(id_)
        risposta = QMessageBox.question(
            self, "Scheda importata",
            f"Dal PDF sono state lette {len(dati.codici_h)} indicazioni di pericolo.\n"
            "Completare gli altri dati (produttore, DPI, misure, conservazione) con l'assistente AI?")
        if risposta == QMessageBox.StandardButton.Yes:
            esegui_ai(self, "L'assistente sta leggendo la scheda di sicurezza...",
                      lambda ai: ai.estrai_sds(testo), lambda risultato: self._applica_ai(id_, risultato))

    def _applica_ai(self, id_: int, risultato: dict) -> None:
        riga = self.repo.leggi("sostanze", id_)
        if riga is None:
            return
        modifiche = {}
        for campo in CAMPI_TESTO:
            valore = risultato.get(campo, "")
            # Si completano solo i campi vuoti; il nome letto dal PDF ha la precedenza.
            if valore and (not riga[campo].strip() or (campo == "nome" and riga[campo] == Path(riga["file_sds"]).stem)):
                modifiche[campo] = valore
        codici = sostanze.elenco_codici(f"{riga['codici_h']}, {risultato.get('codici_h', '')}")
        if codici != riga["codici_h"]:
            modifiche["codici_h"] = codici
        data = risultato.get("data_revisione", "")
        if not riga["data_sds"] and len(data) == 10 and data[4] == "-":
            modifiche["data_sds"] = data
        if modifiche:
            self.repo.aggiorna("sostanze", id_, **modifiche)
        self.tabella.ricarica()
        self.tabella.seleziona(id_)
        self.dati.carica(id_)
        self._aggiorna_classificazione()

    def salva_in_sospeso(self) -> None:
        self.dati.salva_in_sospeso()

    def aggiorna(self) -> None:
        self.tabella.ricarica()
