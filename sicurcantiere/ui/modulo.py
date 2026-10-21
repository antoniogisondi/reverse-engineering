"""Modulo di campi collegato a un record e scelta dei DPI da elenco."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QDate, Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import anagrafiche
from sicurcantiere.repository import Repository
from sicurcantiere.ui import tema

DATA_VUOTA = QDate(1900, 1, 1)
FILTRO_IMMAGINI = "Immagini (*.png *.jpg *.jpeg *.bmp)"


class CampoData(QDateEdit):
    """Data che può restare vuota; il calendario si apre sul mese corrente se è vuota."""

    def __init__(self) -> None:
        super().__init__()
        self.setCalendarPopup(True)
        self.setDisplayFormat("dd/MM/yyyy")
        self.setMinimumDate(DATA_VUOTA)
        self.setSpecialValueText("non indicata")

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome di Qt
        super().mousePressEvent(evento)
        if self.date() == DATA_VUOTA:
            oggi = QDate.currentDate()
            self.calendarWidget().setCurrentPage(oggi.year(), oggi.month())

    def valore(self) -> str | None:
        return None if self.date() == DATA_VUOTA else self.date().toString(Qt.DateFormat.ISODate)

    def imposta(self, valore: str | None) -> None:
        d = QDate.fromString(valore or "", Qt.DateFormat.ISODate)
        self.setDate(d if d.isValid() else DATA_VUOTA)


class DialogoDPI(QDialog):
    """Elenco dei DPI per parte del corpo, da spuntare."""

    def __init__(self, scelti: list[str], suggeriti: list[str] = (), genitore: QWidget | None = None):
        super().__init__(genitore)
        self.setWindowTitle("Elenco DPI")
        self.resize(460, 560)
        self.albero = QTreeWidget()
        self.albero.setHeaderHidden(True)
        scelti_l = {s.lower() for s in scelti}
        noti: set[str] = set()
        for categoria, voci in anagrafiche.CATALOGO_DPI.items():
            gruppo = QTreeWidgetItem(self.albero, [categoria])
            gruppo.setFlags(gruppo.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            font = gruppo.font(0)
            font.setBold(True)
            gruppo.setFont(0, font)
            for voce in voci:
                self._voce(gruppo, voce, voce.lower() in scelti_l)
                noti.add(voce.lower())
        altri = [v for v in list(scelti) + list(suggeriti) if v.lower() not in noti]
        if altri:
            gruppo = QTreeWidgetItem(self.albero, ["Altri DPI e DPI delle lavorazioni"])
            for voce in dict.fromkeys(altri):
                self._voce(gruppo, voce, voce.lower() in scelti_l)
        self.albero.expandAll()
        self.suggeriti = [s.lower() for s in suggeriti]

        tutti = QPushButton("Seleziona i DPI delle lavorazioni")
        tutti.setEnabled(bool(suggeriti))
        tutti.setToolTip("Spunta i DPI previsti dalle schede di rischio delle lavorazioni assegnate.")
        tutti.clicked.connect(self._suggeriti)
        nessuno = QPushButton("Deseleziona tutto")
        nessuno.clicked.connect(lambda: self._tutti(False))
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        riga = QHBoxLayout()
        riga.addWidget(tutti)
        riga.addWidget(nessuno)
        riga.addStretch()
        layout = QVBoxLayout(self)
        layout.addWidget(self.albero)
        layout.addLayout(riga)
        layout.addWidget(pulsanti)

    @staticmethod
    def _voce(gruppo: QTreeWidgetItem, testo: str, spuntata: bool) -> None:
        item = QTreeWidgetItem(gruppo, [testo])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(0, Qt.CheckState.Checked if spuntata else Qt.CheckState.Unchecked)

    def _voci(self):
        for i in range(self.albero.topLevelItemCount()):
            gruppo = self.albero.topLevelItem(i)
            for j in range(gruppo.childCount()):
                yield gruppo.child(j)

    def _tutti(self, stato: bool) -> None:
        for item in self._voci():
            item.setCheckState(0, Qt.CheckState.Checked if stato else Qt.CheckState.Unchecked)

    def _suggeriti(self) -> None:
        for item in self._voci():
            if item.text(0).lower() in self.suggeriti:
                item.setCheckState(0, Qt.CheckState.Checked)

    def scelti(self) -> list[str]:
        return [item.text(0) for item in self._voci() if item.checkState(0) == Qt.CheckState.Checked]


class ModuloRecord(QWidget):
    """Modulo con i campi di un record di una tabella.

    Ogni campo è (campo, etichetta) per il testo oppure (campo, etichetta, tipo, opzioni) con tipo
    testo, testo_lungo, scelta (elenco modificabile), data, numero, spunta, spunte (più voci da
    spuntare tra le opzioni, salvate separate da «;»), impresa, immagine o dpi; (None, titolo) inserisce un titolo di gruppo. Per il tipo dpi le opzioni sono una
    funzione che dal record restituisce i DPI suggeriti. Si salvano solo i campi modificati nel
    modulo, così un aggiornamento del record fatto altrove (per esempio dall'assistente AI) non
    viene sovrascritto con i valori vecchi rimasti nei campi.
    """

    salvato = None  # funzione chiamata dopo ogni salvataggio, con il nome del campo

    def __init__(self, repo: Repository, tabella: str, campi: list[tuple]):
        super().__init__()
        self.repo = repo
        self.tabella = tabella
        self.id_: int | None = None
        self.record: dict[str, Any] | None = None
        self.campi: dict[str, QWidget] = {}
        self.tipi: dict[str, str] = {}
        self._modificati: set[str] = set()
        self._caricamento = False
        self._opzioni: dict[str, Any] = {}
        self.modulo = QFormLayout(self)
        for voce in campi:
            campo, etichetta = voce[0], voce[1]
            if campo is None:
                titolo = QLabel(etichetta)
                titolo.setObjectName("sectionTitle")
                self.modulo.addRow(titolo)
                continue
            tipo = voce[2] if len(voce) > 2 else "testo"
            self._opzioni[campo] = voce[3] if len(voce) > 3 else []
            self.tipi[campo] = tipo
            contenitore = self._crea(campo, tipo, self._opzioni[campo])
            self.modulo.addRow("" if tipo == "spunta" else etichetta, contenitore)
            if tipo == "spunta":
                self.campi[campo].setText(etichetta)
        tema.stile_modulo(self.modulo)

    # --- creazione dei campi ---

    def _crea(self, campo: str, tipo: str, opzioni: Any) -> QWidget:
        def modificato(*_: Any) -> None:
            if not self._caricamento:
                self._modificati.add(campo)

        def subito(*_: Any) -> None:
            if not self._caricamento:
                self._modificati.add(campo)
                self._salva(campo)

        if tipo == "scelta":
            w = QComboBox()
            w.setEditable(True)
            w.addItems([""] + list(opzioni))
            w.currentTextChanged.connect(modificato)
            w.activated.connect(lambda *_: self._salva(campo))
            w.lineEdit().editingFinished.connect(lambda: self._salva(campo))
        elif tipo == "impresa":
            w = QComboBox()
            w.currentIndexChanged.connect(subito)
        elif tipo == "data":
            w = CampoData()
            w.dateChanged.connect(subito)
        elif tipo == "numero":
            w = QDoubleSpinBox()
            w.setRange(0, 1e10)
            w.setDecimals(2)
            w.setGroupSeparatorShown(True)
            w.setSuffix(" €")
            w.valueChanged.connect(modificato)
            w.editingFinished.connect(lambda: self._salva(campo))
        elif tipo == "spunta":
            w = QCheckBox()
            w.toggled.connect(subito)
        elif tipo == "spunte":
            w = QWidget()
            griglia = QGridLayout(w)
            griglia.setContentsMargins(0, 2, 0, 2)
            griglia.setHorizontalSpacing(18)
            griglia.setVerticalSpacing(6)
            w.caselle = []
            for n, voce in enumerate(opzioni):
                casella = QCheckBox(voce)
                casella.setMinimumHeight(22)
                casella.toggled.connect(subito)
                griglia.addWidget(casella, n // 3, n % 3)
                w.caselle.append(casella)
            griglia.setColumnStretch(3, 1)
        elif tipo in ("testo_lungo", "dpi"):
            w = QPlainTextEdit()
            w.setFixedHeight(70)
            timer = QTimer(self, singleShot=True, interval=700)
            timer.timeout.connect(lambda: self._salva(campo))
            w.textChanged.connect(lambda: (modificato(), timer.start()))
        else:
            w = QLineEdit()
            w.textChanged.connect(modificato)
            w.editingFinished.connect(lambda: self._salva(campo))
        self.campi[campo] = w

        if tipo not in ("immagine", "dpi"):
            return w
        contenitore = QWidget()
        riga = QHBoxLayout(contenitore)
        riga.setContentsMargins(0, 0, 0, 0)
        riga.addWidget(w, 1)
        if tipo == "immagine":
            w.setPlaceholderText("Nessuna immagine")
            sfoglia = QPushButton("Sfoglia...")
            sfoglia.clicked.connect(lambda: self._scegli_immagine(campo))
            togli = QPushButton("Togli")
            togli.clicked.connect(lambda: (w.setText(""), self._modificati.add(campo), self._salva(campo)))
            riga.addWidget(sfoglia)
            riga.addWidget(togli)
        else:
            scegli = QPushButton("Elenco DPI...")
            scegli.clicked.connect(lambda: self._scegli_dpi(campo))
            riga.addWidget(scegli, alignment=Qt.AlignmentFlag.AlignTop)
        return contenitore

    def _scegli_immagine(self, campo: str) -> None:
        percorso, _ = QFileDialog.getOpenFileName(self, "Scegli un'immagine", "", FILTRO_IMMAGINI)
        if percorso:
            self.campi[campo].setText(percorso)
            self._modificati.add(campo)
            self._salva(campo)

    def _scegli_dpi(self, campo: str) -> None:
        if self.record is None:
            return
        suggeriti = self._opzioni[campo](self.record) if callable(self._opzioni[campo]) else []
        attuali = anagrafiche.dpi_lavoratore({"dpi": self.valore(campo)})
        dialogo = DialogoDPI(attuali, suggeriti, self)
        if dialogo.exec():
            self.campi[campo].setPlainText("; ".join(dialogo.scelti()))
            self._modificati.add(campo)
            self._salva(campo)

    # --- valori ---

    def valore(self, campo: str) -> Any:
        w, tipo = self.campi[campo], self.tipi[campo]
        if tipo == "scelta":
            return w.currentText().strip()
        if tipo == "impresa":
            return w.currentData()
        if tipo == "data":
            return w.valore()
        if tipo == "numero":
            return w.value()
        if tipo == "spunta":
            return int(w.isChecked())
        if tipo == "spunte":
            return "; ".join(c.text() for c in w.caselle if c.isChecked())
        if tipo in ("testo_lungo", "dpi"):
            return w.toPlainText()
        return w.text()

    def _imposta(self, campo: str, valore: Any) -> None:
        w, tipo = self.campi[campo], self.tipi[campo]
        if tipo == "scelta":
            w.setCurrentText(valore or "")
        elif tipo == "impresa":
            w.clear()
            w.addItem("—", None)
            for i in self.repo.elenco("imprese"):
                if i["id"] != self.id_:
                    w.addItem(i["ragione_sociale"] or f"Impresa n. {i['id']}", i["id"])
            w.setCurrentIndex(max(w.findData(valore), 0))
        elif tipo == "data":
            w.imposta(valore)
        elif tipo == "numero":
            w.setValue(float(valore or 0))
        elif tipo == "spunta":
            w.setChecked(bool(valore))
        elif tipo == "spunte":
            scelte = {v.strip() for v in (valore or "").split(";")}
            for c in w.caselle:
                c.setChecked(c.text() in scelte)
        elif tipo in ("testo_lungo", "dpi"):
            w.setPlainText(valore or "")
        else:
            w.setText(valore or "")

    def _salva(self, campo: str) -> None:
        if self.id_ is not None and campo in self._modificati:
            self.repo.aggiorna(self.tabella, self.id_, **{campo: self.valore(campo)})
            self._modificati.discard(campo)
            self.record = self.repo.leggi(self.tabella, self.id_)
            if self.salvato:
                self.salvato(campo)

    def salva_in_sospeso(self) -> None:
        if self.id_ is not None and self._modificati and self.repo.leggi(self.tabella, self.id_):
            self.repo.aggiorna(self.tabella, self.id_, **{c: self.valore(c) for c in self._modificati})
        self._modificati.clear()

    def carica(self, id_: int | None) -> None:
        self.salva_in_sospeso()
        self.id_ = id_
        self.record = self.repo.leggi(self.tabella, id_) if id_ is not None else None
        self._caricamento = True
        try:
            for campo in self.campi:
                self._imposta(campo, self.record[campo] if self.record else None)
        finally:
            self._caricamento = False
        self.setEnabled(self.record is not None)


def immagine_anteprima(etichetta: QLabel, percorso: str, lato: int = 150) -> None:
    """Mostra la foto (o il testo «Foto vuota») in un'etichetta."""
    from PySide6.QtGui import QPixmap

    pixmap = QPixmap(percorso) if percorso else QPixmap()
    if pixmap.isNull():
        etichetta.setPixmap(QPixmap())
        etichetta.setText("(Foto vuota)")
    else:
        etichetta.setPixmap(pixmap.scaled(lato, lato, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))

