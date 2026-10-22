"""Pagina delle valutazioni dei rischi specifici (NIOSH, OCRA, ...)."""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import Qt, QTimer, Signal
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

from sicurcantiere.documenti.valutazione import genera_valutazione, lavorazioni_valutazione
from sicurcantiere.repository import Repository
from sicurcantiere.ui import tema
from sicurcantiere.ui.lavoro_ai import esegui_ai
from sicurcantiere.ui.pagine import Pagina, _riquadro, pulsante_ai
from sicurcantiere.ui.sostanze import DialogoFasi
from sicurcantiere.ui.tabella import Colonna, TabellaCrud
from sicurcantiere.valutazioni import COLORI, METODI, Campo, Esito, Metodo, automatiche

# Esempi di descrizione mostrati nel campo vuoto, per metodo.
ESEMPI = {
    "niosh": "«Il manovale carica in betoniera sacchi di cemento da 25 kg presi da un bancale a terra, "
             "circa 2 sacchi al minuto per 3 ore al giorno, ruotando il busto».",
    "niosh_composto": "«Il magazziniere scarica sacchi da 25 kg dal camion (1 al minuto) e sposta casse "
                      "da 12 kg sugli scaffali (3 al minuto), per 4 ore».",
    "traino_spinta": "«Il manovale spinge la carriola carica di calcestruzzo per circa 15 m, 20 volte all'ora; "
                     "con il dinamometro forza iniziale 22 kg e di mantenimento 12 kg».",
    "trasporto": "«Il manovale porta a mano i blocchi da 12 kg dal bancale al piano di lavoro, a 5 m, "
                 "3 al minuto per 2 ore».",
    "ocra": "«Il ferraiolo lega i ferri con la tenaglia per circa 5 ore, con movimenti rapidi del polso "
            "destro e pause di 10 minuti ogni 2 ore».",
    "rumore": "«Il muratore usa il martello demolitore per 1 ora e mezza, la smerigliatrice per 45 minuti, "
              "poi carica le macerie per 4 ore; usa inserti auricolari».",
    "vibrazioni": "«Il manovale usa il martello demolitore elettrico per circa 1 ora al giorno e la "
                  "smerigliatrice per mezz'ora».",
}

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




def _quante(elenco: str) -> str:
    """«7 lavorazioni» al posto dell'elenco, che compare al passaggio del mouse."""
    n = len([v for v in elenco.split("; ") if v.strip()])
    return "nessuna" if not n else "1 lavorazione" if n == 1 else f"{n} lavorazioni"

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
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
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
        for c, campo in enumerate(metodo.colonne_compiti):
            # Testo descrittivo largo, numeri e scelte quanto basta per l'intestazione.
            larghezza = 210 if campo.tipo == "testo" else 230 if campo.tipo == "scelta" else 120
            self.tabella.setColumnWidth(c, max(larghezza, self.tabella.horizontalHeader().sectionSizeHint(c)))
        for compito in dati.get("compiti", []):
            self._riga_compito(compito)
        self._adatta_altezza()

    def _adatta_altezza(self) -> None:
        """Mostra tutte le righe dei compiti (fino a 8) senza barra di scorrimento interna."""
        righe = min(max(self.tabella.rowCount(), 2), 8)
        self.tabella.setMinimumHeight(self.tabella.horizontalHeader().sizeHint().height() + righe * 34 + 24)

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
        self._adatta_altezza()
        self.modificato.emit()

    def _rimuovi_compito(self) -> None:
        r = self.tabella.currentRow()
        if r < 0:
            r = self.tabella.rowCount() - 1
        if r >= 0:
            self.tabella.removeRow(r)
            self._adatta_altezza()
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
    sottotitolo = ("Le valutazioni necessarie vengono create automaticamente dai rischi delle lavorazioni: "
                   "restano da inserire i parametri.")
    icona = "valutazioni"
    sezioni_controlli = ("Valutazioni",)

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.id_: int | None = None
        self.tabella = TabellaCrud(repo, "valutazioni", [
            Colonna("titolo", "Valutazione", larghezza=220, suggerimento=(
                "Nome della valutazione: la identifica nell'elenco ed è il titolo usato nella "
                "relazione e nel POS (per esempio «Carico sacchi di cemento in betoniera»).")),
            Colonna("metodo", "Metodo", "scelta", larghezza=290,
                    scelte=lambda: [(k, m.nome) for k, m in METODI.items()]),
            Colonna("mansione", "Mansione / gruppo omogeneo", larghezza=180, suggerimento=(
                "Lavoratori esposti allo stesso rischio, a cui si riferisce l'esito "
                "(per esempio «Manovali», «Carpentieri»); per il rumore e le vibrazioni è il gruppo "
                "omogeneo di esposizione.")),
            Colonna("lavorazioni", "Lavorazioni", "calcolata", larghezza=130,
                    calcola=lambda r: _quante(lavorazioni_valutazione(self.repo, r)),
                    aiuto=lambda r: lavorazioni_valutazione(self.repo, r).replace("; ", "\n") or "Nessuna lavorazione",
                    suggerimento="Lavorazioni in cui si presenta il rischio: si scelgono con il pulsante «Lavorazioni...»."),
            Colonna("esito", "Risultato", "calcolata", calcola=self._esito_riga, disegno=tema.DelegatoRisultato),
        ], valori_nuovo=lambda: {"metodo": "niosh"})
        self.tabella.imposta_titolo("Valutazioni")
        self.tabella.aggiungi_pulsante("Lavorazioni...", self._scegli_lavorazioni)
        self.avviso = QLabel()
        self.avviso.setWordWrap(True)
        self.avviso.setObjectName("infoBanner")
        self.avviso.setVisible(False)
        self.layout_.addWidget(self.avviso)
        self.tabella.selezione_cambiata.connect(self._seleziona)
        self.tabella.modificata.connect(self._riga_modificata)

        # Descrizione dell'attività e compilazione con l'AI.
        self.descrizione = QPlainTextEdit()
        self.descrizione.setPlaceholderText(
            "Descrivi l'attività come la vedresti in cantiere: cosa si solleva o si ripete, pesi, "
            "altezze, quante volte, per quanto tempo, pause, posture... Per esempio: «Il manovale carica in "
            "betoniera sacchi di cemento da 25 kg presi da un bancale a terra, circa 2 sacchi al "
            "minuto per 3 ore al giorno, ruotando il busto»."
        )
        self.descrizione.setMaximumHeight(110)
        self.descrizione.textChanged.connect(self._programma_salvataggio)
        compila = pulsante_ai("Compila con l'assistente AI")
        compila.clicked.connect(self._compila_ai)
        self.ipotesi = QLabel()
        self.ipotesi.setWordWrap(True)
        self.ipotesi.setObjectName("pageSubtitle")
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
        relazione = QPushButton("Genera la relazione in Word...")
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

        self._modificato = False
        self._timer = QTimer(self, singleShot=True, interval=500)
        self._timer.timeout.connect(self.salva_in_sospeso)

    # --- dati ---

    def _scegli_lavorazioni(self) -> None:
        if self.id_ is None:
            QMessageBox.information(self, "Lavorazioni", "Seleziona prima una valutazione.")
            return
        riga = self.repo.leggi("valutazioni", self.id_)
        dialogo = DialogoFasi(self.repo, set(self.repo.fasi_valutazione(self.id_)),
                              "Lavorazioni della valutazione",
                              f"<b>{riga['titolo'] or 'Valutazione'}</b>: spunta tutte le lavorazioni "
                              "in cui si presenta il rischio valutato.", self)
        if dialogo.exec():
            self.repo.salva_fasi_valutazione(self.id_, dialogo.scelte())
            id_ = self.id_
            self.tabella.ricarica()
            self.tabella.seleziona(id_)

    def _esito_riga(self, riga: dict[str, Any]) -> str:
        metodo = METODI.get(riga["metodo"])
        if metodo is None:
            return ""
        if not json.loads(riga["dati"] or "{}"):
            return ""  # «Da eseguire» (vedi tema.DelegatoRisultato)
        try:
            esito = metodo.esegui(json.loads(riga["dati"] or "{}"))
        except ValueError:
            return ""
        return f"{esito.colore}|{esito.indice_testo}|{esito.classe.split(' (')[0]}"

    def _seleziona(self, id_: int | None) -> None:
        self.salva_in_sospeso()
        self.id_ = id_
        self.dettaglio.setEnabled(id_ is not None)
        if id_ is None:
            return
        riga = self.repo.leggi("valutazioni", id_)
        dati = self.repo.dati_valutazione(id_)
        metodo = METODI.get(riga["metodo"], METODI["niosh"])
        self.descrizione.setPlaceholderText(
            "Descrivi l'attività come la vedresti in cantiere: attrezzature, pesi, tempi, pause, posture. "
            f"Per esempio: {ESEMPI.get(metodo.chiave, '')}")
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
            self._modificato = True
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
        # Si salva solo dopo una modifica: una valutazione appena creata resta «da eseguire»
        # finché non se ne inseriscono i parametri, anche se viene solo aperta.
        modificato, self._modificato = self._modificato, False
        if not modificato or self.id_ is None or self.editor.metodo is None \
                or not self.repo.leggi("valutazioni", self.id_):
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
            QMessageBox.information(self, "Assistente AI", "Descrivi prima l'attività da valutare.")
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
        automatico = riga["titolo"] in {g.titolo for g in automatiche.GRUPPI}
        if (automatico or not riga["titolo"].strip()) and risultato.titolo:
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
        percorso, _ = QFileDialog.getSaveFileName(self, "Salva la relazione", str(predefinito),
                                                  "Documento Word (*.docx)")
        if not percorso:
            return
        try:
            file = genera_valutazione(self.repo, self.id_, percorso)
        except PermissionError:
            QMessageBox.warning(self, "Errore", "Impossibile salvare il file: verifica che non sia aperto in Word.")
            return
        from sicurcantiere.ui.anteprima import documento_creato

        documento_creato(self, file, "Relazione generata")

    def aggiorna(self) -> None:
        messaggi = automatiche.sincronizza(self.repo)
        self.avviso.setText("<br>".join(messaggi))
        self.avviso.setVisible(bool(messaggi))
        self.tabella.ricarica()
        self.tabella.seleziona_prima()
