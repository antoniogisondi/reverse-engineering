"""Pagina delle valutazioni dei rischi specifici (NIOSH, OCRA, ...)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere.documenti.valutazione import genera_valutazione
from sicurcantiere.repository import Repository
from sicurcantiere.ui.lavoro_ai import esegui_ai
from sicurcantiere.ui.pagine import Pagina, _riquadro, primario
from sicurcantiere.ui.tabella import Colonna, TabellaCrud
from sicurcantiere.valutazioni import COLORI, METODI, Campo, Esito, Metodo

# Chiavi aggiuntive salvate insieme ai parametri del metodo.
DESCRIZIONE = "descrizione"
IPOTESI = "ipotesi_ai"


ALTEZZA_CAMPO = 30


def _widget_campo(campo: Campo, valore: Any) -> QWidget:
    # Altezza minima esplicita: senza, nel riquadro scorrevole il modulo
    # verrebbe schiacciato invece di mostrare la barra di scorrimento.
    w = _crea_widget_campo(campo, valore)
    w.setMinimumHeight(ALTEZZA_CAMPO)
    return w


def _crea_widget_campo(campo: Campo, valore: Any) -> QWidget:
    if campo.tipo == "numero":
        w = QDoubleSpinBox()
        w.setDecimals(campo.decimali)
        w.setRange(campo.minimo, campo.massimo)
        w.setSuffix(campo.suffisso)
        w.setValue(float(valore))
        if campo.aiuto:
            w.setToolTip(campo.aiuto)
        return w
    if campo.tipo == "scelta":
        w = QComboBox()
        for v, etichetta in campo.scelte:
            w.addItem(etichetta, v)
        w.setCurrentIndex(max(w.findData(valore), 0))
        return w
    w = QLineEdit(str(valore))
    return w


def _valore_widget(campo: Campo, w: QWidget) -> Any:
    if isinstance(w, QDoubleSpinBox):
        return w.value()
    if isinstance(w, QComboBox):
        return w.currentData()
    return w.text()


def _collega(w: QWidget, slot) -> None:
    if isinstance(w, QDoubleSpinBox):
        w.valueChanged.connect(slot)
    elif isinstance(w, QComboBox):
        w.currentIndexChanged.connect(slot)
    else:
        w.textChanged.connect(slot)


class EditorParametri(QWidget):
    """Modulo dei parametri di un metodo, con l'eventuale tabella dei compiti."""

    modificato = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.metodo: Metodo | None = None
        self.campi: dict[str, QWidget] = {}
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.modulo = QFormLayout()
        self.layout_.addLayout(self.modulo)
        self.tabella = QTableWidget()
        self.tabella.verticalHeader().setVisible(False)
        self.tabella.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.pulsanti_compiti = QHBoxLayout()
        aggiungi = QPushButton("Aggiungi compito")
        rimuovi = QPushButton("Rimuovi compito")
        aggiungi.clicked.connect(self._aggiungi_compito)
        rimuovi.clicked.connect(self._rimuovi_compito)
        self.pulsanti_compiti.addWidget(aggiungi)
        self.pulsanti_compiti.addWidget(rimuovi)
        self.pulsanti_compiti.addStretch()
        self.riquadro_compiti = QGroupBox("Compiti")
        lc = QVBoxLayout(self.riquadro_compiti)
        lc.addLayout(self.pulsanti_compiti)
        lc.addWidget(self.tabella)
        self.layout_.addWidget(self.riquadro_compiti)
        self.layout_.addStretch()

    def imposta(self, metodo: Metodo, dati: dict[str, Any]) -> None:
        self.metodo = metodo
        dati = metodo.normalizza(dati)
        while self.modulo.rowCount():
            self.modulo.removeRow(0)
        self.campi = {}
        for campo in metodo.campi:
            w = _widget_campo(campo, dati[campo.chiave])
            _collega(w, lambda *_: self.modificato.emit())
            self.modulo.addRow(campo.etichetta, w)
            self.campi[campo.chiave] = w
        self.riquadro_compiti.setVisible(bool(metodo.colonne_compiti))
        self.tabella.setRowCount(0)
        self.tabella.setColumnCount(len(metodo.colonne_compiti))
        self.tabella.setHorizontalHeaderLabels(
            [c.etichetta + (f" ({c.suffisso.strip()})" if c.suffisso.strip() else "") for c in metodo.colonne_compiti]
        )
        for compito in dati.get("compiti", []):
            self._riga_compito(compito)

    def _riga_compito(self, compito: dict[str, Any]) -> None:
        assert self.metodo is not None
        r = self.tabella.rowCount()
        self.tabella.insertRow(r)
        for c, campo in enumerate(self.metodo.colonne_compiti):
            w = _widget_campo(campo, compito.get(campo.chiave, campo.predefinito))
            if isinstance(w, QDoubleSpinBox):
                w.setSuffix("")
            _collega(w, lambda *_: self.modificato.emit())
            self.tabella.setCellWidget(r, c, w)
        self.tabella.setRowHeight(r, 34)

    def _aggiungi_compito(self) -> None:
        if self.metodo is None:
            return
        self._riga_compito(self.metodo.compito_predefinito())
        self.modificato.emit()

    def _rimuovi_compito(self) -> None:
        r = self.tabella.currentRow()
        if r < 0:
            r = self.tabella.rowCount() - 1
        if r >= 0:
            self.tabella.removeRow(r)
            self.modificato.emit()

    def dati(self) -> dict[str, Any]:
        assert self.metodo is not None
        dati = {chiave: _valore_widget(campo, self.campi[chiave])
                for campo in self.metodo.campi for chiave in [campo.chiave]}
        if self.metodo.colonne_compiti:
            dati["compiti"] = [
                {campo.chiave: _valore_widget(campo, self.tabella.cellWidget(r, c))
                 for c, campo in enumerate(self.metodo.colonne_compiti)}
                for r in range(self.tabella.rowCount())
            ]
        return dati


class PannelloEsito(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("tessera")
        self.titolo = QLabel("RISULTATO")
        self.titolo.setObjectName("tesseraTitolo")
        self.indice = QLabel()
        self.indice.setObjectName("tesseraValore")
        self.classe = QLabel()
        self.classe.setWordWrap(True)
        self.dettagli = QLabel()
        self.dettagli.setWordWrap(True)
        self.dettagli.setTextFormat(Qt.TextFormat.RichText)
        self.misure = QLabel()
        self.misure.setWordWrap(True)
        self.misure.setTextFormat(Qt.TextFormat.RichText)
        layout = QVBoxLayout(self)
        for w in (self.titolo, self.indice, self.classe, self.dettagli, self.misure):
            layout.addWidget(w)
        layout.addStretch()

    def mostra(self, esito: Esito) -> None:
        colore = COLORI[esito.colore]
        self.indice.setText(f"Indice: {esito.indice_testo}")
        self.classe.setText(f"<b style='color:{colore}'>● {esito.classe}</b>")
        righe = "".join(f"<tr><td>{k}</td><td align='right'><b>{v}</b></td></tr>" for k, v in esito.dettagli)
        if esito.righe_compiti:
            righe += "<tr><td colspan='2'><br><i>Dettaglio per compito nella relazione stampata</i></td></tr>"
        self.dettagli.setText(f"<table width='100%' cellspacing='3'>{righe}</table>")
        note = "".join(f"<p><i>{n}</i></p>" for n in esito.note)
        elenco = "".join(f"<li>{m}</li>" for m in esito.misure)
        self.misure.setText(f"{note}<p><b>Misure di prevenzione e protezione</b></p><ul>{elenco}</ul>")
        stato = {"verde": "ok", "giallo": "attenzione"}.get(esito.colore, "errore")
        if self.property("stato") != stato:
            self.setProperty("stato", stato)
            self.style().unpolish(self)
            self.style().polish(self)


class PaginaValutazioni(Pagina):
    titolo = "Valutazioni dei rischi specifici"
    voce = "Valutazioni specifiche"
    icona = "valutazioni"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.id_: int | None = None
        self.tabella = TabellaCrud(repo, "valutazioni", [
            Colonna("titolo", "Valutazione", larghezza=240),
            Colonna("metodo", "Metodo", "scelta", larghezza=330,
                    scelte=lambda: [(k, m.nome) for k, m in METODI.items()]),
            Colonna("mansione", "Mansione / gruppo omogeneo", larghezza=200),
            Colonna("fase_id", "Fase", "scelta", larghezza=200, scelte=self._fasi),
            Colonna("data", "Data", "data", larghezza=95),
            Colonna("esito", "Risultato", "calcolata", calcola=self._esito_riga),
        ], valori_nuovo=lambda: {"metodo": "niosh", "data": date.today().isoformat()})
        self.tabella.selezione_cambiata.connect(self._seleziona)
        self.tabella.modificata.connect(self._riga_modificata)

        # Descrizione dell'attività e compilazione con l'AI.
        self.descrizione = QPlainTextEdit()
        self.descrizione.setPlaceholderText(
            "Descrivi l'attività come la vedresti in cantiere: cosa si solleva o si ripete, pesi, "
            "altezze, quante volte, per quanto tempo, pause, posture... Es.: «Il manovale carica in "
            "betoniera sacchi di cemento da 25 kg presi da un bancale a terra, circa 2 sacchi al "
            "minuto per 3 ore al giorno, ruotando il busto»."
        )
        self.descrizione.setMaximumHeight(110)
        self.descrizione.textChanged.connect(self._programma_salvataggio)
        compila = primario(QPushButton("Compila con l'assistente AI"))
        compila.clicked.connect(self._compila_ai)
        self.ipotesi = QLabel()
        self.ipotesi.setWordWrap(True)
        self.ipotesi.setObjectName("sottotitolo")
        box_ai = QWidget()
        lai = QVBoxLayout(box_ai)
        lai.setContentsMargins(0, 0, 0, 0)
        lai.addWidget(self.descrizione)
        riga = QHBoxLayout()
        riga.addWidget(compila)
        riga.addStretch()
        lai.addLayout(riga)
        lai.addWidget(self.ipotesi)

        self.editor = EditorParametri()
        self.editor.modificato.connect(self._parametri_modificati)
        self.note = QPlainTextEdit()
        self.note.setPlaceholderText("Note del valutatore (riportate nella relazione)")
        self.note.setMaximumHeight(80)
        self.note.textChanged.connect(self._programma_salvataggio)

        sinistra = QWidget()
        ls = QVBoxLayout(sinistra)
        ls.addWidget(_riquadro("Descrizione dell'attività", box_ai))
        ls.addWidget(_riquadro("Parametri del metodo", self.editor))
        ls.addWidget(_riquadro("Note", self.note))
        scorrimento = QScrollArea()
        scorrimento.setWidgetResizable(True)
        scorrimento.setWidget(sinistra)

        self.esito = PannelloEsito()
        relazione = QPushButton("Genera relazione (.docx)...")
        relazione.clicked.connect(self._genera)
        destra = QWidget()
        ld = QVBoxLayout(destra)
        ld.setContentsMargins(0, 0, 0, 0)
        ld.addWidget(self.esito, 1)
        ld.addWidget(relazione)
        scorrimento_esito = QScrollArea()
        scorrimento_esito.setWidgetResizable(True)
        scorrimento_esito.setWidget(destra)

        orizzontale = QSplitter(Qt.Orientation.Horizontal)
        orizzontale.addWidget(scorrimento)
        orizzontale.addWidget(scorrimento_esito)
        orizzontale.setSizes([620, 420])
        self.dettaglio = orizzontale
        self.dettaglio.setEnabled(False)

        verticale = QSplitter(Qt.Orientation.Vertical)
        verticale.addWidget(self.tabella)
        verticale.addWidget(orizzontale)
        verticale.setSizes([180, 620])
        self.layout_.addWidget(verticale)

        self._timer = QTimer(self, singleShot=True, interval=500)
        self._timer.timeout.connect(self.salva_in_sospeso)

    # --- dati ---

    def _fasi(self) -> list[tuple[int | None, str]]:
        return [(None, "(nessuna)")] + [
            (f["id"], f"{f['codice']} {f['descrizione']}".strip()) for f in self.repo.elenco("fasi")
        ]

    def _esito_riga(self, riga: dict[str, Any]) -> str:
        metodo = METODI.get(riga["metodo"])
        if metodo is None:
            return ""
        try:
            esito = metodo.esegui(json.loads(riga["dati"] or "{}"))
        except ValueError:
            return ""
        return f"{esito.indice_testo} - {esito.classe}"

    def _seleziona(self, id_: int | None) -> None:
        self.salva_in_sospeso()
        self.id_ = id_
        self.dettaglio.setEnabled(id_ is not None)
        if id_ is None:
            return
        riga = self.repo.leggi("valutazioni", id_)
        dati = self.repo.dati_valutazione(id_)
        metodo = METODI.get(riga["metodo"], METODI["niosh"])
        self.editor.blockSignals(True)
        self.editor.imposta(metodo, dati)
        self.editor.blockSignals(False)
        for w, testo in ((self.descrizione, dati.get(DESCRIZIONE, "")), (self.note, riga["note"])):
            w.blockSignals(True)
            w.setPlainText(testo)
            w.blockSignals(False)
        self._mostra_ipotesi(dati.get(IPOTESI) or [])
        self._aggiorna_esito()

    def _riga_modificata(self) -> None:
        # Cambiando il metodo nella tabella si ricostruisce l'editor.
        if self.id_ is not None:
            riga = self.repo.leggi("valutazioni", self.id_)
            if riga and self.editor.metodo and riga["metodo"] != self.editor.metodo.chiave:
                self.id_, vecchio = None, self.id_
                self._seleziona(vecchio)

    def _parametri_modificati(self) -> None:
        self._aggiorna_esito()
        self._programma_salvataggio()

    def _programma_salvataggio(self) -> None:
        if self.id_ is not None:
            self._timer.start()

    def _dati_correnti(self) -> dict[str, Any]:
        dati = self.editor.dati()
        dati[DESCRIZIONE] = self.descrizione.toPlainText()
        precedenti = self.repo.dati_valutazione(self.id_) if self.id_ is not None else {}
        if precedenti.get(IPOTESI):
            dati[IPOTESI] = precedenti[IPOTESI]
        return dati

    def salva_in_sospeso(self) -> None:
        self._timer.stop()
        if self.id_ is None or self.editor.metodo is None or not self.repo.leggi("valutazioni", self.id_):
            return
        self.repo.salva_dati_valutazione(self.id_, self._dati_correnti())
        self.repo.aggiorna("valutazioni", self.id_, note=self.note.toPlainText())
        self._aggiorna_riga_tabella()

    def _aggiorna_riga_tabella(self) -> None:
        id_ = self.id_
        self.tabella.blockSignals(True)
        self.tabella.ricarica()
        self.tabella.seleziona(id_)
        self.tabella.blockSignals(False)

    def _aggiorna_esito(self) -> None:
        if self.editor.metodo is not None:
            self.esito.mostra(self.editor.metodo.esegui(self.editor.dati()))

    def _mostra_ipotesi(self, ipotesi: list[str]) -> None:
        if ipotesi:
            self.ipotesi.setText("Ipotesi dell'assistente da verificare: " + "; ".join(ipotesi))
        else:
            self.ipotesi.setText("")

    # --- azioni ---

    def _compila_ai(self) -> None:
        if self.id_ is None or self.editor.metodo is None:
            return
        testo = self.descrizione.toPlainText().strip()
        if len(testo) < 15:
            QMessageBox.information(self, "Assistente AI", "Descrivere prima l'attività da valutare.")
            return
        metodo = self.editor.metodo
        id_ = self.id_
        esegui_ai(self, "L'assistente sta compilando i parametri...",
                  lambda ai: ai.compila_valutazione(metodo, testo),
                  lambda risultato: self._applica_ai(id_, metodo, risultato))

    def _applica_ai(self, id_: int, metodo: Metodo, risultato) -> None:
        if self.id_ != id_ or not self.repo.leggi("valutazioni", id_):
            return  # l'utente ha cambiato valutazione nel frattempo
        self.editor.imposta(metodo, risultato.dati)
        riga = self.repo.leggi("valutazioni", id_)
        modifiche = {}
        if not riga["titolo"].strip() and risultato.titolo:
            modifiche["titolo"] = risultato.titolo
        if not riga["mansione"].strip() and risultato.mansione:
            modifiche["mansione"] = risultato.mansione
        if modifiche:
            self.repo.aggiorna("valutazioni", id_, **modifiche)
        dati = {**self.editor.dati(), DESCRIZIONE: self.descrizione.toPlainText(), IPOTESI: risultato.ipotesi}
        self.repo.salva_dati_valutazione(id_, dati)
        self._mostra_ipotesi(risultato.ipotesi)
        self._aggiorna_esito()
        self._aggiorna_riga_tabella()

    def _genera(self) -> None:
        if self.id_ is None:
            return
        self.salva_in_sospeso()
        riga = self.repo.leggi("valutazioni", self.id_)
        predefinito = self.repo.progetto.percorso.with_name(
            f"Valutazione - {riga['titolo'] or METODI[riga['metodo']].nome}.docx".replace("/", "-"))
        percorso, _ = QFileDialog.getSaveFileName(self, "Salva relazione", str(predefinito),
                                                  "Documento Word (*.docx)")
        if not percorso:
            return
        try:
            file = genera_valutazione(self.repo, self.id_, percorso)
        except PermissionError:
            QMessageBox.warning(self, "Errore", "Impossibile scrivere il file: è aperto in Word?")
            return
        if QMessageBox.question(self, "Relazione generata", f"Creato {Path(file).name}.\nAprirlo ora?") \
                == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(file)))

    def aggiorna(self) -> None:
        self.tabella.ricarica()
