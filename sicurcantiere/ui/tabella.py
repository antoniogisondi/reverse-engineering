"""Tabella modificabile collegata a una tabella del progetto.

Ogni modifica di cella viene salvata subito nel file di progetto.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from PySide6.QtCore import QDate, Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStyle,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QGridLayout,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere.repository import Repository
from sicurcantiere.ui import tema

RUOLO_ID = Qt.ItemDataRole.UserRole


@dataclass
class Colonna:
    campo: str
    titolo: str
    # testo | testo_lungo | intero | decimale | data | scelta | spunta | calcolata
    tipo: str = "testo"
    scelte: Callable[[], list[tuple[Any, str]]] | None = None
    scelta_libera: bool = False  # la combo accetta anche testo non in elenco
    calcola: Callable[[dict[str, Any]], str] | None = None
    minimo: float = 0
    massimo: float = 1_000_000_000
    larghezza: int | None = None
    suggerimento: str = ""  # spiegazione mostrata passando sull'intestazione
    disegno: Callable[[QWidget], QStyledItemDelegate] | None = None  # delegato che disegna la cella (badge)
    vuota: str = ""  # se indicato, la cella vuota è evidenziata con questo testo (per esempio «da assegnare»)
    aiuto: Callable[[dict[str, Any]], str] | None = None  # testo completo al passaggio del mouse sulla cella


def formatta(colonna: Colonna, riga: dict[str, Any]) -> str:
    if colonna.tipo == "calcolata":
        return colonna.calcola(riga) if colonna.calcola else ""
    if colonna.tipo == "spunta":
        return ""
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
        if col.tipo in ("calcolata", "spunta"):
            return None
        if col.tipo in ("testo_lungo", "dpi"):
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
            if not col.scelta_libera:
                QTimer.singleShot(0, e.showPopup)  # l'elenco si apre subito, senza un secondo clic
            return e
        return QLineEdit(genitore)

    def initStyleOption(self, opzioni, indice):  # noqa: N802 - nome di Qt
        super().initStyleOption(opzioni, indice)
        if opzioni.state & QStyle.StateFlag.State_Selected:
            opzioni.font.setBold(True)  # la riga selezionata non si confonde con il fondo degli avvisi

    def paint(self, painter, opzioni, indice):
        super().paint(painter, opzioni, indice)
        selezionata = bool(opzioni.state & QStyle.StateFlag.State_Selected)
        sopra = bool(opzioni.state & QStyle.StateFlag.State_MouseOver)
        if self.tabella.colonne[indice.column()].tipo == "scelta" and (selezionata or sopra):
            tema.disegna_freccia(painter, opzioni.rect, tema.correnti()["tx3"])
        if selezionata and indice.column() == self.tabella.prima_colonna_visibile():
            r = opzioni.rect
            painter.fillRect(r.x(), r.y(), 3, r.height(), QColor(tema.correnti()["acc_s"]))

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


class _TestoCrescente(QPlainTextEdit):
    """Testo su più righe che si allunga mentre si scrive (da 3 righe fino a circa 14)."""

    def __init__(self, genitore=None):
        super().__init__(genitore)
        tema.evidenzia_spazi(self)
        self.document().documentLayout().documentSizeChanged.connect(lambda *_: self._adatta())
        self._adatta()

    def _adatta(self) -> None:
        riga = self.fontMetrics().lineSpacing()
        righe = max(3, min(14, int(self.document().size().height()) + 1))
        self.setFixedHeight(riga * righe + 16)

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome di Qt
        super().resizeEvent(evento)
        self._adatta()


class EditorDPI(QWidget):
    """DPI come etichette, scelti dall'elenco per parte del corpo (si confrontano meglio e finiscono uguali
    nei documenti); il testo salvato è l'elenco separato da punto e virgola."""

    cambiato = Signal()

    def __init__(self, genitore=None):
        super().__init__(genitore)
        self._voci: list[str] = []
        self.etichette = QLabel()
        self.etichette.setWordWrap(True)
        self.etichette.setTextFormat(Qt.TextFormat.RichText)
        scegli = QPushButton("Scegli i DPI...")
        scegli.clicked.connect(self._scegli)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.etichette)
        layout.addWidget(scegli, alignment=Qt.AlignmentFlag.AlignLeft)

    def imposta(self, testo: str) -> None:
        import re

        self._voci = [v.strip() for v in re.split(r"[;\n]", testo or "") if v.strip()]
        c = tema.correnti()
        if not self._voci:
            self.etichette.setText(f"<span style='color:{c['tx3']}'>Nessun DPI indicato.</span>")
            return
        self.etichette.setText(" ".join(
            f"<span style='background:{c['surface2']}; color:{c['tx']}'>&nbsp;{v}&nbsp;</span>&nbsp;"
            for v in self._voci))

    def testo(self) -> str:
        return "; ".join(self._voci)

    def _scegli(self) -> None:
        from sicurcantiere.ui.modulo import DialogoDPI

        dialogo = DialogoDPI(self._voci, [], self)
        if dialogo.exec():
            self.imposta("; ".join(dialogo.scelti()))
            self.cambiato.emit()


class PannelloDettaglio(QScrollArea):
    """Modifica della riga selezionata, a destra dell'elenco: un campo per colonna, etichetta sopra."""

    def __init__(self, tabella: TabellaCrud):
        super().__init__()
        self.tabella = tabella
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setObjectName("detailPanel")
        self._id: int | None = None
        self._caricamento = False
        self.editori: dict[str, QWidget] = {}
        self._timer: dict[str, QTimer] = {}

        contenuto = QWidget()
        contenuto.setObjectName("detailBody")
        self.titolo = QLabel()
        self.titolo.setObjectName("sectionTitle")
        self.titolo.setWordWrap(True)
        self.vuoto = QLabel()
        self.vuoto.setObjectName("hint")
        self.vuoto.setWordWrap(True)
        griglia = QGridLayout()
        griglia.setHorizontalSpacing(14)
        griglia.setVerticalSpacing(10)
        riga = colonna = 0
        for col in tabella.colonne:
            editore = self._crea(col)
            if editore is None:
                continue
            blocco = QWidget()
            lb = QVBoxLayout(blocco)
            lb.setContentsMargins(0, 0, 0, 0)
            lb.setSpacing(4)
            if col.tipo != "spunta":
                nome = QLabel(col.titolo)
                nome.setObjectName("fieldLabel")
                nome.setWordWrap(True)
                if col.suggerimento:
                    nome.setToolTip(col.suggerimento)
                lb.addWidget(nome)
            lb.addWidget(editore)
            largo = col.tipo in ("testo_lungo", "spunta", "dpi") or col.larghezza is None or (col.larghezza or 0) >= 200
            if largo:
                if colonna:
                    riga, colonna = riga + 1, 0
                griglia.addWidget(blocco, riga, 0, 1, 2)
                riga += 1
            else:
                griglia.addWidget(blocco, riga, colonna)
                colonna += 1
                if colonna == 2:
                    riga, colonna = riga + 1, 0
        griglia.setColumnStretch(0, 1)
        griglia.setColumnStretch(1, 1)
        self.campi = QWidget()
        self.campi.setLayout(griglia)
        self.extra = QVBoxLayout()  # spazio per controlli propri della pagina (etichette DPI, pulsanti AI...)
        layout = QVBoxLayout(contenuto)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        layout.addWidget(self.titolo)
        layout.addWidget(self.vuoto)
        layout.addWidget(self.campi)
        layout.addLayout(self.extra)
        layout.addStretch()
        self.setWidget(contenuto)
        self.carica(None)

    # --- campi ---

    def _crea(self, col: Colonna) -> QWidget | None:
        campo = col.campo
        if col.tipo == "calcolata":
            w = QLabel()
            w.setObjectName("detailValue")
            w.setWordWrap(True)
        elif col.tipo == "testo_lungo":
            w = _TestoCrescente()
            self._timer[campo] = t = QTimer(self, singleShot=True, interval=600)
            t.timeout.connect(lambda: self._salva(campo))
            w.textChanged.connect(lambda: None if self._caricamento else t.start())
        elif col.tipo == "intero":
            w = QSpinBox()
            w.setRange(int(col.minimo), int(col.massimo))
            if col.minimo == 0:
                tema.numero_vuoto(w)
            w.valueChanged.connect(lambda *_: None if self._caricamento else self._salva(campo))
        elif col.tipo == "decimale":
            w = QDoubleSpinBox()
            w.setDecimals(2)
            w.setRange(col.minimo, col.massimo)
            w.setGroupSeparatorShown(True)
            if col.minimo == 0:
                tema.numero_vuoto(w)
            w.editingFinished.connect(lambda: self._salva(campo))
        elif col.tipo == "data":
            from sicurcantiere.ui.modulo import CampoData

            w = CampoData()
            w.dateChanged.connect(lambda *_: None if self._caricamento else self._salva(campo))
        elif col.tipo == "scelta":
            w = QComboBox()
            w.setEditable(col.scelta_libera)
            w.activated.connect(lambda *_: self._salva(campo))
            if col.scelta_libera:
                w.lineEdit().editingFinished.connect(lambda: self._salva(campo))
        elif col.tipo == "dpi":
            w = EditorDPI()
            w.cambiato.connect(lambda: None if self._caricamento else self._salva(campo))
        elif col.tipo == "spunta":
            w = QCheckBox(col.titolo)
            if col.suggerimento:
                w.setToolTip(col.suggerimento)
            w.toggled.connect(lambda *_: None if self._caricamento else self._salva(campo))
        else:
            w = QLineEdit()
            w.editingFinished.connect(lambda: self._salva(campo))
        self.editori[campo] = w
        return w

    def _valore(self, campo: str) -> Any:
        w = self.editori[campo]
        if isinstance(w, EditorDPI):
            return w.testo()
        if isinstance(w, QPlainTextEdit):
            return w.toPlainText()
        if isinstance(w, QCheckBox):
            return 1 if w.isChecked() else 0
        if isinstance(w, (QSpinBox, QDoubleSpinBox)):
            return w.value()
        if isinstance(w, QComboBox):
            testo = w.currentText()
            i = w.findText(testo)
            return w.itemData(i) if i >= 0 else testo
        if isinstance(w, QDateEdit):
            return w.valore()
        return w.text()

    def _salva(self, campo: str) -> None:
        if self._caricamento or self._id is None:
            return
        r = next((n for n, riga in enumerate(self.tabella._righe) if riga["id"] == self._id), None)
        if r is None:
            return
        c = next(n for n, col in enumerate(self.tabella.colonne) if col.campo == campo)
        valore = self._valore(campo)
        if valore is None and self.tabella.riga(r).get(campo) in (None, ""):
            return
        self.tabella.salva_cella(r, c, valore)
        self._aggiorna_calcolate(self.tabella.riga(r))

    def salva_in_sospeso(self) -> None:
        for campo, timer in self._timer.items():
            if timer.isActive():
                timer.stop()
                self._salva(campo)

    def _aggiorna_calcolate(self, riga: dict[str, Any]) -> None:
        for col in self.tabella.colonne:
            if col.tipo == "calcolata":
                self.editori[col.campo].setText(formatta(col, riga) or "—")
        self.titolo.setText(self._titolo(riga))

    def _titolo(self, riga: dict[str, Any]) -> str:
        for col in self.tabella.colonne:
            if col.tipo not in ("spunta", "calcolata"):
                testo = formatta(col, riga).strip()
                if testo:
                    return testo.split("\n")[0][:120]
        return "Nuova voce"

    def carica(self, id_: int | None) -> None:
        self.salva_in_sospeso()
        self._id = id_
        riga = next((r for r in self.tabella._righe if r["id"] == id_), None) if id_ is not None else None
        self.campi.setVisible(riga is not None)
        self.titolo.setVisible(riga is not None)
        self.vuoto.setVisible(riga is None)
        self.vuoto.setText(self.tabella.testo_vuoto())
        if riga is None:
            return
        self._caricamento = True
        try:
            for col in self.tabella.colonne:
                w = self.editori.get(col.campo)
                valore = riga.get(col.campo)
                if w is None or col.tipo == "calcolata":
                    continue
                if isinstance(w, EditorDPI):
                    w.imposta(valore or "")
                elif isinstance(w, QPlainTextEdit):
                    if w.toPlainText() != (valore or ""):
                        w.setPlainText(valore or "")
                elif isinstance(w, QCheckBox):
                    w.setChecked(bool(valore))
                elif isinstance(w, QSpinBox):
                    w.setValue(int(valore or 0))
                elif isinstance(w, QDoubleSpinBox):
                    w.setValue(float(valore or 0))
                elif isinstance(w, QDateEdit):
                    w.imposta(valore)
                elif isinstance(w, QComboBox):
                    w.clear()
                    for v, etichetta in col.scelte() if col.scelte else []:
                        w.addItem(etichetta, v)
                    i = w.findData(valore)
                    if i >= 0:
                        w.setCurrentIndex(i)
                    elif col.scelta_libera:
                        w.setEditText(str(valore or ""))
                    else:
                        w.setCurrentIndex(-1)
                else:
                    w.setText("" if valore is None else str(valore))
        finally:
            self._caricamento = False
        self._aggiorna_calcolate(riga)

    def primo_campo(self) -> None:
        """Cursore sul primo campo da compilare (dopo «Aggiungi»)."""
        for col in self.tabella.colonne:
            w = self.editori.get(col.campo)
            if w is not None and col.tipo not in ("calcolata", "spunta"):
                w.setFocus()
                if isinstance(w, QComboBox) and not col.scelta_libera:
                    QTimer.singleShot(0, w.showPopup)
                return


class TabellaCrud(QFrame):
    """Elenco di record con pulsanti Aggiungi/Elimina, in un riquadro con intestazione."""

    modificata = Signal()
    selezione_cambiata = Signal(object)  # id del record selezionato o None

    def __init__(self, repo: Repository, tabella: str, colonne: list[Colonna],
                 valori_nuovo: Callable[[], dict[str, Any]] | None = None,
                 valida: Callable[[dict[str, Any]], str | None] | None = None,
                 genitore: QWidget | None = None, elenco: list[str] | None = None,
                 vuoto: str = ""):
        super().__init__(genitore)
        self.repo = repo
        self.nome_tabella = tabella
        self.colonne = colonne
        self.valori_nuovo = valori_nuovo or (lambda: {})
        self.valida = valida
        self.filtro: dict[str, Any] = {}
        self._righe: list[dict[str, Any]] = []
        self.elenco = elenco  # colonne visibili nell'elenco; le altre si modificano nel pannello di dettaglio
        self._vista: Callable[[dict[str, Any]], bool] | None = None  # righe mostrate (filtri dell'elenco)
        self._filtri: list[tuple[QPushButton, str, Callable[[dict[str, Any]], bool] | None]] = []
        self._testo_vuoto = vuoto

        self.vista = QTableWidget(0, len(colonne))
        self.vista.setAlternatingRowColors(True)
        self.vista.setHorizontalHeaderLabels([c.titolo for c in colonne])
        for n, c in enumerate(colonne):
            if c.suggerimento:
                self.vista.horizontalHeaderItem(n).setToolTip(c.suggerimento)
            if c.disegno is not None:
                self.vista.setItemDelegateForColumn(n, c.disegno(self.vista))
        self.vista.setItemDelegate(_Delegato(self))
        self.vista.setShowGrid(False)
        self.vista.setMouseTracking(True)
        self.vista.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.vista.verticalHeader().setMinimumSectionSize(32)
        # Altezza delle righe secondo il testo, ma rifatta quando cambia la larghezza delle colonne:
        # misurata a tabella nascosta (colonne strettissime) darebbe righe altissime.
        self.vista.verticalHeader().setMaximumSectionSize(180)
        self.vista.horizontalHeader().sectionResized.connect(lambda *_: self._adatta_righe())
        self.vista.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.vista.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.vista.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
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
        self.vista.itemChanged.connect(self._spunta_cambiata)
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

        # Intestazione del riquadro: titolo facoltativo con il numero di righe, poi i pulsanti.
        self.setObjectName("card")
        self.titolo = QLabel()
        self.titolo.setObjectName("cardTitle")
        self.conteggio = QLabel()
        self.conteggio.setObjectName("countBadge")
        self.titolo.hide()
        self.conteggio.hide()
        intestazione = QFrame()
        intestazione.setObjectName("cardHeader")
        lay_intestazione = QHBoxLayout(intestazione)
        lay_intestazione.setContentsMargins(12, 6, 10, 6)
        lay_intestazione.addWidget(self.titolo)
        lay_intestazione.addWidget(self.conteggio)
        lay_intestazione.addSpacing(8)
        lay_intestazione.addLayout(self.pulsanti, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        layout.addWidget(intestazione)
        self.riga_filtri = QHBoxLayout()
        self.riga_filtri.setContentsMargins(10, 6, 10, 6)
        self.riga_filtri.setSpacing(6)
        self._contenitore_filtri = QWidget()
        self._contenitore_filtri.setLayout(self.riga_filtri)
        self._contenitore_filtri.hide()
        layout.addWidget(self._contenitore_filtri)
        self.dettaglio: PannelloDettaglio | None = None
        if elenco:
            for i, c in enumerate(colonne):
                self.vista.setColumnHidden(i, c.campo not in elenco)
            intestazione_vista = self.vista.horizontalHeader()
            for i, c in enumerate(colonne):
                if c.campo in elenco and c.tipo == "testo_lungo":
                    intestazione_vista.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            self.vista.setWordWrap(False)
            self.vista.verticalHeader().setMaximumSectionSize(48)
            self.dettaglio = PannelloDettaglio(self)
            self.divisore = QSplitter(Qt.Orientation.Horizontal)
            self.divisore.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.divisore.setChildrenCollapsible(False)
            self.divisore.addWidget(self.vista)
            self.divisore.addWidget(self.dettaglio)
            self.divisore.setStretchFactor(0, 3)
            self.divisore.setStretchFactor(1, 2)
            self.dettaglio.setMinimumWidth(300)
            self.selezione_cambiata.connect(self.dettaglio.carica)
            layout.addWidget(self.divisore)
        else:
            layout.addWidget(self.vista)

    def aggiungi_filtri(self, filtri: list[tuple[str, Callable[[dict[str, Any]], bool] | None]]) -> None:
        """Pulsanti a scelta sopra l'elenco («Tutti», «Alti e molto alti»...), con il numero di voci."""
        for nome, predicato in filtri:
            b = QPushButton(nome)
            b.setCheckable(True)
            b.setObjectName("filterChip")
            b.clicked.connect(lambda _=False, pulsante=b: self._scegli_filtro(pulsante))
            self.riga_filtri.addWidget(b)
            self._filtri.append((b, nome, predicato))
        self.riga_filtri.addStretch()
        self._contenitore_filtri.show()
        self._filtri[0][0].setChecked(True)

    def _scegli_filtro(self, pulsante: QPushButton) -> None:
        for b, _nome, predicato in self._filtri:
            b.setChecked(b is pulsante)
            if b is pulsante:
                self._vista = predicato
        self._applica_vista()

    def _applica_vista(self) -> None:
        for b, nome, predicato in self._filtri:
            b.setText(f"{nome}  {sum(1 for r in self._righe if predicato is None or predicato(r))}")
        for r, riga in enumerate(self._righe):
            self.vista.setRowHidden(r, self._vista is not None and not self._vista(riga))

    def prima_colonna_visibile(self) -> int:
        return next((i for i in range(len(self.colonne)) if not self.vista.isColumnHidden(i)), 0)

    def testo_vuoto(self) -> str:
        if self._righe:
            return "Seleziona una voce nell'elenco per vederne e modificarne i dati."
        return self._testo_vuoto or "Nessuna voce. Usa «Aggiungi» per inserire la prima."

    def salva_in_sospeso(self) -> None:
        if self.dettaglio is not None:
            self.dettaglio.salva_in_sospeso()

    def _adatta_righe(self) -> None:
        if self.isVisible():
            self.vista.resizeRowsToContents()

    def showEvent(self, evento) -> None:
        super().showEvent(evento)
        self.vista.resizeRowsToContents()

    def imposta_titolo(self, testo: str) -> None:
        """Titolo del riquadro (per esempio «Imprese»), con il numero di righe accanto."""
        self.titolo.setText(testo)
        self.titolo.setVisible(bool(testo))
        self.conteggio.setVisible(bool(testo))
        self.conteggio.setText(str(len(self._righe)))

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
        self.conteggio.setText(str(len(self._righe)))
        if self._filtri:
            self._applica_vista()
        self.seleziona(selezionato)
        self.selezione_cambiata.emit(self.id_selezionato())

    def seleziona_prima(self) -> None:
        """Seleziona la prima riga se non ce n'è una selezionata (la parte sotto non resta vuota)."""
        if self.id_selezionato() is None and self._righe:
            self.vista.selectRow(0)

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
            if col.tipo == "spunta":
                item.setFlags((item.flags() | Qt.ItemFlag.ItemIsUserCheckable) & ~Qt.ItemFlag.ItemIsEditable)
                item.setCheckState(Qt.CheckState.Checked if self._righe[r].get(col.campo) else Qt.CheckState.Unchecked)
            if col.tipo in ("intero", "decimale", "calcolata"):
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if col.aiuto is not None:
                item.setToolTip(col.aiuto(self._righe[r]))
            if col.vuota and self._righe[r].get(col.campo) in (None, "", 0):
                # dato obbligatorio mancante: cella evidenziata, come i dati da completare dei documenti
                c_ = tema.correnti()
                item.setText(col.vuota)
                item.setBackground(QColor(c_["warn_bg"]))
                item.setForeground(QColor(c_["warn"]))
                item.setToolTip(f"{col.titolo}: {col.vuota}")
            self.vista.setItem(r, c, item)

    def _spunta_cambiata(self, item: QTableWidgetItem) -> None:
        r, c = item.row(), item.column()
        if c >= len(self.colonne) or self.colonne[c].tipo != "spunta" or r >= len(self._righe):
            return
        valore = 1 if item.checkState() == Qt.CheckState.Checked else 0
        if int(self._righe[r].get(self.colonne[c].campo) or 0) != valore:
            self.salva_cella(r, c, valore)

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
        self.salva_in_sospeso()
        nuovo = self.repo.inserisci(self.nome_tabella, **{**self.filtro, **self.valori_nuovo()})
        self.ricarica()
        self.seleziona(nuovo)
        self.modificata.emit()
        if self.dettaglio is not None:
            self.dettaglio.carica(nuovo)
            self.dettaglio.primo_campo()
        else:
            col = self.prima_colonna_visibile()
            r = next((n for n, riga in enumerate(self._righe) if riga["id"] == nuovo), None)
            if r is not None and self.colonne[col].tipo not in ("calcolata", "spunta"):
                self.vista.setCurrentCell(r, col)
                self.vista.editItem(self.vista.item(r, col))

    def elimina(self) -> None:
        id_ = self.id_selezionato()
        if id_ is None:
            return
        risposta = QMessageBox.question(self, "Elimina", "Vuoi eliminare la riga selezionata?")
        if risposta != QMessageBox.StandardButton.Yes:
            return
        self.repo.elimina(self.nome_tabella, id_)
        self.ricarica()
        self.modificata.emit()
