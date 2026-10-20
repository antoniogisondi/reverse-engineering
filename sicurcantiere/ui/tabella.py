"""Tabella modificabile collegata a una tabella del progetto.

Ogni modifica di cella viene salvata subito nel file di progetto.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere.repository import Repository

RUOLO_ID = Qt.ItemDataRole.UserRole


@dataclass
class Colonna:
    campo: str
    titolo: str
    # testo | testo_lungo | intero | decimale | data | scelta | calcolata
    tipo: str = "testo"
    scelte: Callable[[], list[tuple[Any, str]]] | None = None
    scelta_libera: bool = False  # la combo accetta anche testo non in elenco
    calcola: Callable[[dict[str, Any]], str] | None = None
    minimo: float = 0
    massimo: float = 1_000_000_000
    larghezza: int | None = None


def formatta(colonna: Colonna, riga: dict[str, Any]) -> str:
    if colonna.tipo == "calcolata":
        return colonna.calcola(riga) if colonna.calcola else ""
    valore = riga.get(colonna.campo)
    if valore is None:
        return ""
    if colonna.tipo == "data":
        d = QDate.fromString(str(valore), Qt.DateFormat.ISODate)
        return d.toString("dd/MM/yyyy") if d.isValid() else ""
    if colonna.tipo == "decimale":
        return f"{float(valore):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if colonna.tipo == "scelta" and colonna.scelte:
        for v, etichetta in colonna.scelte():
            if v == valore:
                return etichetta
    return str(valore)


class _Delegato(QStyledItemDelegate):
    def __init__(self, tabella: TabellaCrud):
        super().__init__(tabella)
        self.tabella = tabella

    def createEditor(self, genitore, opzioni, indice):
        col = self.tabella.colonne[indice.column()]
        if col.tipo == "calcolata":
            return None
        if col.tipo == "testo_lungo":
            return QPlainTextEdit(genitore)
        if col.tipo == "intero":
            e = QSpinBox(genitore)
            e.setRange(int(col.minimo), int(col.massimo))
            return e
        if col.tipo == "decimale":
            e = QDoubleSpinBox(genitore)
            e.setDecimals(2)
            e.setRange(col.minimo, col.massimo)
            e.setGroupSeparatorShown(True)
            return e
        if col.tipo == "data":
            e = QDateEdit(genitore)
            e.setCalendarPopup(True)
            e.setDisplayFormat("dd/MM/yyyy")
            return e
        if col.tipo == "scelta":
            e = QComboBox(genitore)
            e.setEditable(col.scelta_libera)
            for valore, etichetta in col.scelte() if col.scelte else []:
                e.addItem(etichetta, valore)
            return e
        return QLineEdit(genitore)

    def setEditorData(self, editor, indice):
        col = self.tabella.colonne[indice.column()]
        valore = self.tabella.riga(indice.row()).get(col.campo)
        if isinstance(editor, QPlainTextEdit):
            editor.setPlainText(valore or "")
        elif isinstance(editor, QSpinBox):
            editor.setValue(int(valore or 0))
        elif isinstance(editor, QDoubleSpinBox):
            editor.setValue(float(valore or 0))
        elif isinstance(editor, QDateEdit):
            d = QDate.fromString(str(valore or ""), Qt.DateFormat.ISODate)
            editor.setDate(d if d.isValid() else self.tabella.data_predefinita(indice.row(), col))
        elif isinstance(editor, QComboBox):
            i = editor.findData(valore)
            if i >= 0:
                editor.setCurrentIndex(i)
            elif col.scelta_libera:
                editor.setEditText(str(valore or ""))
        elif isinstance(editor, QLineEdit):
            editor.setText("" if valore is None else str(valore))

    def setModelData(self, editor, modello, indice):
        if isinstance(editor, QPlainTextEdit):
            valore = editor.toPlainText()
        elif isinstance(editor, (QSpinBox, QDoubleSpinBox)):
            valore = editor.value()
        elif isinstance(editor, QDateEdit):
            valore = editor.date().toString(Qt.DateFormat.ISODate)
        elif isinstance(editor, QComboBox):
            testo = editor.currentText()
            i = editor.findText(testo)
            valore = editor.itemData(i) if i >= 0 else testo
        else:
            valore = editor.text()
        self.tabella.salva_cella(indice.row(), indice.column(), valore)


class TabellaCrud(QWidget):
    """Elenco di record con pulsanti Aggiungi/Elimina."""

    modificata = Signal()
    selezione_cambiata = Signal(object)  # id del record selezionato o None

    def __init__(self, repo: Repository, tabella: str, colonne: list[Colonna],
                 valori_nuovo: Callable[[], dict[str, Any]] | None = None,
                 valida: Callable[[dict[str, Any]], str | None] | None = None,
                 genitore: QWidget | None = None):
        super().__init__(genitore)
        self.repo = repo
        self.nome_tabella = tabella
        self.colonne = colonne
        self.valori_nuovo = valori_nuovo or (lambda: {})
        self.valida = valida
        self.filtro: dict[str, Any] = {}
        self._righe: list[dict[str, Any]] = []

        self.vista = QTableWidget(0, len(colonne))
        self.vista.setAlternatingRowColors(True)
        self.vista.setHorizontalHeaderLabels([c.titolo for c in colonne])
        self.vista.setItemDelegate(_Delegato(self))
        self.vista.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.vista.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.vista.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.vista.setWordWrap(True)
        self.vista.verticalHeader().setVisible(False)
        intestazione = self.vista.horizontalHeader()
        intestazione.setStretchLastSection(True)
        for i, c in enumerate(colonne):
            if c.larghezza:
                self.vista.setColumnWidth(i, c.larghezza)
            elif c.tipo == "testo_lungo":
                intestazione.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.vista.itemSelectionChanged.connect(
            lambda: self.selezione_cambiata.emit(self.id_selezionato())
        )

        self.btn_aggiungi = QPushButton("Aggiungi")
        self.btn_elimina = QPushButton("Elimina")
        self.btn_aggiungi.clicked.connect(self.aggiungi)
        self.btn_elimina.clicked.connect(self.elimina)
        self.pulsanti = QHBoxLayout()
        self.pulsanti.addWidget(self.btn_aggiungi)
        self.pulsanti.addWidget(self.btn_elimina)
        self.pulsanti.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.pulsanti)
        layout.addWidget(self.vista)

    def aggiungi_pulsante(self, testo: str, azione) -> QPushButton:
        """Pulsante aggiuntivo accanto ad Aggiungi ed Elimina."""
        b = QPushButton(testo)
        b.clicked.connect(lambda: azione())
        self.pulsanti.insertWidget(self.pulsanti.count() - 1, b)
        return b

    # --- dati ---

    def riga(self, indice: int) -> dict[str, Any]:
        return self._righe[indice]

    def righe(self) -> list[dict[str, Any]]:
        return list(self._righe)

    def id_selezionato(self) -> int | None:
        indici = self.vista.selectionModel().selectedRows()
        if not indici:
            return None
        return self._righe[indici[0].row()]["id"]

    def imposta_filtro(self, **filtro: Any) -> None:
        self.filtro = filtro
        self.ricarica()

    def ricarica(self) -> None:
        selezionato = self.id_selezionato()
        self._righe = self.repo.elenco(self.nome_tabella, **self.filtro)
        self.vista.blockSignals(True)
        self.vista.setRowCount(len(self._righe))
        for r in range(len(self._righe)):
            self._mostra_riga(r)
        self.vista.blockSignals(False)
        self.vista.resizeRowsToContents()
        self.seleziona(selezionato)
        self.selezione_cambiata.emit(self.id_selezionato())

    def seleziona(self, id_: int | None) -> None:
        for r, riga in enumerate(self._righe):
            if riga["id"] == id_:
                self.vista.selectRow(r)
                return
        self.vista.clearSelection()

    def _mostra_riga(self, r: int) -> None:
        for c, col in enumerate(self.colonne):
            item = QTableWidgetItem(formatta(col, self._righe[r]))
            if col.tipo == "calcolata":
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if col.tipo in ("intero", "decimale", "calcolata"):
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.vista.setItem(r, c, item)

    def data_predefinita(self, r: int, colonna: Colonna) -> QDate:
        # Una data di fine parte dalla data di inizio della stessa riga.
        inizio = self._righe[r].get("data_inizio")
        if colonna.campo != "data_inizio" and inizio:
            d = QDate.fromString(inizio, Qt.DateFormat.ISODate)
            if d.isValid():
                return d
        return QDate.currentDate()

    def salva_cella(self, r: int, c: int, valore: Any) -> None:
        riga = self._righe[r]
        col = self.colonne[c]
        if riga.get(col.campo) == valore:
            return
        if self.valida and (errore := self.valida({**riga, col.campo: valore})):
            QMessageBox.warning(self, "Valore non valido", errore)
            return
        try:
            self.repo.aggiorna(self.nome_tabella, riga["id"], **{col.campo: valore})
        except Exception as e:  # noqa: BLE001 - mostriamo l'errore all'utente
            QMessageBox.warning(self, "Valore non salvato", str(e))
            return
        self._righe[r] = self.repo.leggi(self.nome_tabella, riga["id"]) or riga
        self.vista.blockSignals(True)
        self._mostra_riga(r)
        self.vista.blockSignals(False)
        self.vista.resizeRowToContents(r)
        self.modificata.emit()

    # --- azioni ---

    def aggiungi(self) -> None:
        nuovo = self.repo.inserisci(self.nome_tabella, **{**self.filtro, **self.valori_nuovo()})
        self.ricarica()
        self.seleziona(nuovo)
        self.modificata.emit()

    def elimina(self) -> None:
        id_ = self.id_selezionato()
        if id_ is None:
            return
        risposta = QMessageBox.question(self, "Elimina", "Eliminare la riga selezionata?")
        if risposta != QMessageBox.StandardButton.Yes:
            return
        self.repo.elimina(self.nome_tabella, id_)
        self.ricarica()
        self.modificata.emit()
