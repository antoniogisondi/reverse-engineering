"""Maestranze e lavoratori autonomi dell'impresa: dati, mansioni, DPI, formazione, tesserini e schede."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QBrush, QColor, QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import anagrafiche
from sicurcantiere.documenti.comune import data_it, nome_fase
from sicurcantiere.documenti.maestranze import genera_schede_lavoratori, genera_tesserini
from sicurcantiere.documenti.pos import elenco_dpi
from sicurcantiere.repository import Repository
from sicurcantiere.ui.modulo import ModuloRecord, immagine_anteprima
from sicurcantiere.ui.tabella import Colonna, TabellaCrud

ROSSO = QColor("#C0392B")
RUOLO_COPPIA = Qt.ItemDataRole.UserRole


def salva_e_apri(genitore: QWidget, repo: Repository, nome: str, funzione: Callable[[str], Any]) -> None:
    predefinito = repo.progetto.percorso.with_name(f"{nome}.docx".replace("/", "-"))
    percorso, _ = QFileDialog.getSaveFileName(genitore, "Salva documento", str(predefinito), "Documento Word (*.docx)")
    if not percorso:
        return
    try:
        file = funzione(percorso)
    except PermissionError:
        QMessageBox.warning(genitore, "Errore", "Impossibile scrivere il file: è aperto in Word?")
        return
    risposta = QMessageBox.question(genitore, "Documento generato", f"Creato {Path(file).name}.\nAprirlo ora?")
    if risposta == QMessageBox.StandardButton.Yes:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(file)))


def dpi_suggeriti(repo: Repository, lavoratore: dict[str, Any]) -> list[str]:
    """DPI delle schede di rischio delle lavorazioni assegnate (o di tutte quelle dell'impresa)."""
    fasi = {f for f, _ in repo.mansioni(lavoratore["id"])}
    if not fasi:
        fasi = {f["id"] for f in repo.elenco("fasi", impresa_id=lavoratore["impresa_id"])}
    return elenco_dpi([r["dpi"] for f in fasi for r in repo.rischi(fase_id=f)])


class DialogoMansioni(QDialog):
    """Lavorazioni svolte dal lavoratore e macchine o attrezzature che utilizza.

    In rosso le lavorazioni e le attrezzature a cui non è ancora assegnato nessun lavoratore.
    """

    def __init__(self, repo: Repository, lavoratore: dict[str, Any], genitore: QWidget | None = None):
        super().__init__(genitore)
        self.repo = repo
        self.lavoratore = lavoratore
        self.setWindowTitle("Mansioni del lavoratore")
        self.resize(640, 560)
        titolo = QLabel(f"<b>{anagrafiche.nominativo(lavoratore) or 'Lavoratore'}</b>"
                        + (f" ({lavoratore['mansione']})" if lavoratore["mansione"] else ""))
        aiuto = QLabel("Spuntare le lavorazioni svolte e, al loro interno, le macchine e le attrezzature utilizzate. "
                       "In rosso le voci che non hanno ancora nessun lavoratore assegnato.")
        aiuto.setWordWrap(True)
        aiuto.setObjectName("pageSubtitle")

        assegnate = {(r["fase_id"], r["attrezzatura_id"]) for r in repo.elenco("mansioni_lavoratori")}
        fasi_assegnate = {f for f, _ in assegnate}
        attrezzature_assegnate = {a for _, a in assegnate if a is not None}
        proprie = repo.mansioni(lavoratore["id"])

        self.albero = QTreeWidget()
        self.albero.setHeaderLabels(["Lavorazione / macchina o attrezzatura", "Periodo"])
        self.albero.setColumnWidth(0, 430)
        fasi = repo.elenco("fasi", impresa_id=lavoratore["impresa_id"]) or repo.elenco("fasi")
        for f in fasi:
            periodo = f"{data_it(f['data_inizio'])} - {data_it(f['data_fine'])}" if f["data_inizio"] else ""
            voce = QTreeWidgetItem(self.albero, [nome_fase(f) or f"Fase n. {f['id']}", periodo])
            voce.setFlags(voce.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            voce.setData(0, RUOLO_COPPIA, (f["id"], None))
            voce.setCheckState(0, Qt.CheckState.Checked if any(x == f["id"] for x, _ in proprie)
                               else Qt.CheckState.Unchecked)
            if f["id"] not in fasi_assegnate:
                voce.setForeground(0, QBrush(ROSSO))
            for a in repo.elenco("attrezzature", fase_id=f["id"]):
                figlio = QTreeWidgetItem(voce, [f"{a['nome']} ({a['tipo'].lower()})"])
                figlio.setFlags(figlio.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                figlio.setData(0, RUOLO_COPPIA, (f["id"], a["id"]))
                figlio.setCheckState(0, Qt.CheckState.Checked if (f["id"], a["id"]) in proprie
                                     else Qt.CheckState.Unchecked)
                if a["id"] not in attrezzature_assegnate:
                    figlio.setForeground(0, QBrush(ROSSO))
        self.albero.expandAll()
        self.albero.itemChanged.connect(self._cambiato)

        self.solo_svolte = QCheckBox("Mostra solo le mansioni svolte")
        self.solo_svolte.toggled.connect(self._filtra)
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.accepted.connect(self._conferma)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(titolo)
        layout.addWidget(aiuto)
        if not fasi:
            layout.addWidget(QLabel("Inserire prima le lavorazioni nella pagina «Lavorazioni e rischi»."))
        layout.addWidget(self.albero)
        layout.addWidget(self.solo_svolte)
        layout.addWidget(pulsanti)

    def _voci(self):
        for i in range(self.albero.topLevelItemCount()):
            fase = self.albero.topLevelItem(i)
            yield fase
            for j in range(fase.childCount()):
                yield fase.child(j)

    def _cambiato(self, item: QTreeWidgetItem, _colonna: int) -> None:
        # Spuntare un'attrezzatura spunta anche la sua lavorazione; togliere la lavorazione toglie tutto.
        self.albero.blockSignals(True)
        if item.parent() is not None and item.checkState(0) == Qt.CheckState.Checked:
            item.parent().setCheckState(0, Qt.CheckState.Checked)
        elif item.parent() is None and item.checkState(0) == Qt.CheckState.Unchecked:
            for j in range(item.childCount()):
                item.child(j).setCheckState(0, Qt.CheckState.Unchecked)
        self.albero.blockSignals(False)

    def _filtra(self, solo: bool) -> None:
        for item in self._voci():
            item.setHidden(solo and item.checkState(0) != Qt.CheckState.Checked)

    def coppie(self) -> set[tuple[int, int | None]]:
        return {tuple(item.data(0, RUOLO_COPPIA)) for item in self._voci()
                if item.checkState(0) == Qt.CheckState.Checked}

    def _conferma(self) -> None:
        self.repo.salva_mansioni(self.lavoratore["id"], self.coppie())
        self.accept()


class PannelloLavoratori(QWidget):
    """Elenco delle maestranze (o dei lavoratori autonomi) dell'impresa con il dettaglio."""

    def __init__(self, repo: Repository, autonomi: bool = False):
        super().__init__()
        self.repo = repo
        self.autonomi = autonomi
        self.impresa_id: int | None = None
        colonne = [
            Colonna("nome", "Nome", larghezza=150),
            Colonna("cognome", "Cognome", larghezza=150),
            Colonna("mansione", "Qualifica", "scelta", scelte=lambda: [(m, m) for m in anagrafiche.MANSIONI],
                    scelta_libera=True, larghezza=180),
        ]
        if not autonomi:
            colonne.append(Colonna("matricola", "Matricola", larghezza=90))
        colonne.append(Colonna("idoneita_scadenza", "Idoneità sanitaria fino al", "data"))
        self.tabella = TabellaCrud(repo, "lavoratori", colonne,
                                   valori_nuovo=lambda: {"autonomo": int(self.autonomi)})
        self.tabella.imposta_filtro(impresa_id=-1, autonomo=int(autonomi))
        self.tabella.aggiungi_pulsante("Mansioni...", self.mansioni)
        self.tabella.aggiungi_pulsante("Tesserini...", self.tesserini)
        self.tabella.aggiungi_pulsante("Schede lavoratori...", self.schede)

        campi: list[tuple] = [(None, "Dettaglio"),
                              ("data_nascita", "Data di nascita", "data"),
                              ("luogo_nascita", "Luogo di nascita")]
        if autonomi:
            campi += [("data_inizio", "Inizio attività in cantiere", "data"),
                      ("data_fine", "Fine attività in cantiere", "data")]
        else:
            campi += [("data_assunzione", "Data di assunzione", "data")]
        campi += [("foto", "Foto per il tesserino", "immagine"),
                  ("dpi", "DPI consegnati", "dpi", lambda l: dpi_suggeriti(self.repo, l))]
        if autonomi:
            campi += [(None, "Dati fiscali"),
                      ("indirizzo", "Indirizzo"),
                      ("codice_fiscale", "Codice fiscale"),
                      ("partita_iva", "Partita IVA")]
        else:
            campi += [(None, "Informazione, formazione e addestramento")]
            campi += [(campo, testo, "spunta") for campo, testo in anagrafiche.FORMAZIONE]
            campi += [("formazione", "Altro (corsi, attestati, abilitazioni)", "testo_lungo")]
        self.dettaglio = ModuloRecord(repo, "lavoratori", campi)
        self.dettaglio.salvato = self._salvato
        self.foto = QLabel("(Foto vuota)")
        self.foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foto.setFixedSize(160, 190)
        self.foto.setObjectName("pageSubtitle")
        self.mansioni_testo = QLabel()
        self.mansioni_testo.setWordWrap(True)
        self.mansioni_testo.setObjectName("pageSubtitle")

        sotto = QWidget()
        hs = QHBoxLayout(sotto)
        colonna = QVBoxLayout()
        colonna.addWidget(self.mansioni_testo)
        colonna.addWidget(self.dettaglio)
        colonna.addStretch()
        hs.addLayout(colonna, 1)
        hs.addWidget(self.foto, alignment=Qt.AlignmentFlag.AlignTop)
        scorrimento = QScrollArea()
        scorrimento.setWidgetResizable(True)
        scorrimento.setWidget(sotto)

        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(self.tabella)
        divisore.addWidget(scorrimento)
        divisore.setSizes([180, 400])
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(divisore)
        self.tabella.selezione_cambiata.connect(self._selezionato)
        self._selezionato(None)

    def imposta_impresa(self, impresa_id: int | None) -> None:
        self.impresa_id = impresa_id
        self.tabella.imposta_filtro(impresa_id=impresa_id if impresa_id is not None else -1,
                                    autonomo=int(self.autonomi))

    def _selezionato(self, id_: int | None) -> None:
        self.dettaglio.carica(id_)
        record = self.dettaglio.record
        immagine_anteprima(self.foto, record["foto"] if record else "")
        self._mostra_mansioni()

    def _mostra_mansioni(self) -> None:
        id_ = self.tabella.id_selezionato()
        if id_ is None:
            self.mansioni_testo.setText("")
            return
        fasi = [self.repo.leggi("fasi", f) for f in dict.fromkeys(f for f, _ in self.repo.mansioni(id_))]
        nomi = [nome_fase(f) for f in fasi if f]
        self.mansioni_testo.setText("Lavorazioni svolte: " + ("; ".join(nomi) if nomi else
                                    "nessuna (pulsante «Mansioni...»)"))

    def _salvato(self, campo: str) -> None:
        if campo == "foto" and self.dettaglio.record:
            immagine_anteprima(self.foto, self.dettaglio.record["foto"])

    def _lavoratore(self) -> dict[str, Any] | None:
        id_ = self.tabella.id_selezionato()
        if id_ is None:
            QMessageBox.information(self, "Mansioni", "Selezionare prima un lavoratore.")
            return None
        return self.repo.leggi("lavoratori", id_)

    def mansioni(self) -> None:
        lavoratore = self._lavoratore()
        if lavoratore and DialogoMansioni(self.repo, lavoratore, self).exec():
            self._mostra_mansioni()

    def _impresa(self) -> dict[str, Any] | None:
        return self.repo.leggi("imprese", self.impresa_id) if self.impresa_id is not None else None

    def tesserini(self) -> None:
        if impresa := self._impresa():
            salva_e_apri(self, self.repo, f"Tesserini - {impresa['ragione_sociale']}",
                         lambda p: genera_tesserini(self.repo, impresa["id"], p))

    def schede(self) -> None:
        if impresa := self._impresa():
            salva_e_apri(self, self.repo, f"Schede lavoratori - {impresa['ragione_sociale']}",
                         lambda p: genera_schede_lavoratori(self.repo, impresa["id"], p))

    def salva_in_sospeso(self) -> None:
        self.dettaglio.salva_in_sospeso()
