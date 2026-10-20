"""Pagine della finestra principale."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QDate, Qt, QTimer, QUrl
from PySide6.QtGui import QBrush, QColor, QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import anagrafiche, analisi, controlli
from sicurcantiere.archivio import ATTREZZATURE, per_categoria
from sicurcantiere.documenti.comune import euro
from sicurcantiere.documenti.fascicolo import genera_fascicolo
from sicurcantiere.documenti.moduli import genera_consegna_dpi
from sicurcantiere.documenti.sostanze import genera_elenco_sostanze
from sicurcantiere.documenti.notifica import genera_notifica
from sicurcantiere.documenti.pos import SEZIONI_POS, chiave_testo, genera_pos
from sicurcantiere.documenti.psc import genera_psc
from sicurcantiere.relazione import SEZIONI
from sicurcantiere.repository import Repository
from sicurcantiere.ui.icone import icona
from sicurcantiere.ui.lavoro_ai import esegui_ai
from sicurcantiere.ui.gantt import ZOOM, ZOOM_PREDEFINITO, Gantt, colore_livello
from sicurcantiere.ui.riepilogo import Riepilogo
from sicurcantiere.ui.riepilogo import calcola as calcola_riepilogo
from sicurcantiere.ui.tabella import Colonna, TabellaCrud

RUOLI = anagrafiche.RUOLI_SOGGETTI
TIPI_IMPRESA = anagrafiche.TIPI_IMPRESA
TIPI_ATTREZZATURA = ["Macchina", "Attrezzo", "Opera provvisionale"]


def _titolo(testo: str) -> QLabel:
    etichetta = QLabel(testo)
    etichetta.setObjectName("titoloPagina")
    return etichetta


def primario(pulsante: QPushButton) -> QPushButton:
    """Evidenzia il pulsante con il colore di accento del tema."""
    pulsante.setProperty("primario", True)
    return pulsante


def _riquadro(titolo: str, widget: QWidget) -> QGroupBox:
    g = QGroupBox(titolo)
    QVBoxLayout(g).addWidget(widget)
    return g


def contesto_cantiere(repo: Repository) -> str:
    """Riepilogo testuale del progetto da passare all'assistente AI."""
    c = repo.cantiere()
    imprese = {i["id"]: i["ragione_sociale"] for i in repo.elenco("imprese")}
    righe = [
        f"Opera: {c['nome']}", f"Natura: {c['natura_opera']}",
        f"Indirizzo: {c['indirizzo']} {c['comune']} {c['provincia']}".strip(),
        f"Importo lavori: {c['importo_lavori']:.0f} euro",
        f"Descrizione: {c['descrizione']}",
        "Soggetti: " + "; ".join(f"{s['ruolo']}: {s['nome']}" for s in anagrafiche.soggetti(repo)),
        "Imprese: " + "; ".join(f"{i['ragione_sociale']} ({i['tipo']})" for i in repo.elenco("imprese")),
        "Fasi di lavoro:",
    ]
    for f in repo.elenco("fasi"):
        righe.append(f"- {f['codice']} {f['descrizione']}, impresa {imprese.get(f['impresa_id'], 'da definire')}, "
                     f"dal {f['data_inizio'] or '?'} al {f['data_fine'] or '?'}, zona {f['zona'] or '-'}")
    return "\n".join(righe)


class TestiLiberi(QWidget):
    """Editor di più sezioni di testo, salvate con un breve ritardo."""

    def __init__(self, repo: Repository, sezioni: list[tuple[str, str]],
                 chiave: Callable[[str], str] = lambda s: s, altezza: int = 120,
                 contesto_ai: Callable[[], str] | None = None):
        super().__init__()
        self.repo = repo
        self.chiave = chiave
        self.contesto_ai = contesto_ai
        self.titoli = dict(sezioni)
        self.editor: dict[str, QPlainTextEdit] = {}
        self._in_sospeso: dict[str, str] = {}
        self._timer = QTimer(self, singleShot=True, interval=700)
        self._timer.timeout.connect(self.salva_in_sospeso)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for sezione, titolo in sezioni:
            editor = QPlainTextEdit()
            editor.setMinimumHeight(altezza)
            editor.textChanged.connect(lambda s=sezione: self._modificato(s))
            riquadro = _riquadro(titolo, editor)
            if contesto_ai is not None:
                bozza = QPushButton(icona("ai", "#E8792B"), "Bozza con l'assistente AI")
                bozza.setToolTip("Scrive o migliora il testo della sezione partendo dai dati del progetto")
                bozza.clicked.connect(lambda _=False, s=sezione: self._bozza_ai(s))
                riquadro.layout().addWidget(bozza, alignment=Qt.AlignmentFlag.AlignRight)
            layout.addWidget(riquadro)
            self.editor[sezione] = editor

    def _bozza_ai(self, sezione: str) -> None:
        assert self.contesto_ai is not None
        titolo = self.titoli[sezione]
        contesto = self.contesto_ai()
        attuale = self.editor[sezione].toPlainText()
        esegui_ai(self, f"L'assistente sta scrivendo «{titolo}»...",
                  lambda ai: ai.scrivi_sezione(titolo, contesto, attuale),
                  lambda testo: self.imposta_testo(sezione, testo))

    def imposta_testo(self, sezione: str, testo: str) -> None:
        """Sostituisce il testo di una sezione (annullabile con Ctrl+Z) e lo salva."""
        editor = self.editor[sezione]
        cursore = editor.textCursor()
        cursore.select(cursore.SelectionType.Document)
        cursore.insertText(testo)
        self.salva_in_sospeso()

    def _modificato(self, sezione: str) -> None:
        self._in_sospeso[self.chiave(sezione)] = self.editor[sezione].toPlainText()
        self._timer.start()

    def salva_in_sospeso(self) -> None:
        self._timer.stop()
        for chiave, testo in self._in_sospeso.items():
            self.repo.salva_testo(chiave, testo)
        self._in_sospeso.clear()

    def carica(self, chiave: Callable[[str], str] | None = None) -> None:
        self.salva_in_sospeso()
        if chiave is not None:
            self.chiave = chiave
        for sezione, editor in self.editor.items():
            editor.blockSignals(True)
            editor.setPlainText(self.repo.testo(self.chiave(sezione)))
            editor.blockSignals(False)


class ModuloRecord(QWidget):
    """Modulo con i campi di un record di una tabella.

    Ogni campo è (campo, etichetta) per il testo oppure (campo, etichetta, tipo, opzioni) con tipo
    testo, scelta (elenco modificabile), data, numero, spunta o impresa; (None, titolo) inserisce
    un titolo di gruppo. Si salvano solo i campi modificati nel modulo, così un aggiornamento del
    record fatto altrove (per esempio dall'assistente AI) non viene sovrascritto con i valori
    vecchi rimasti nei campi.
    """

    DATA_VUOTA = QDate(2000, 1, 1)

    def __init__(self, repo: Repository, tabella: str, campi: list[tuple]):
        super().__init__()
        self.repo = repo
        self.tabella = tabella
        self.id_: int | None = None
        self.campi: dict[str, QWidget] = {}
        self.tipi: dict[str, str] = {}
        self._modificati: set[str] = set()
        self._caricamento = False
        modulo = QFormLayout(self)
        for voce in campi:
            campo, etichetta = voce[0], voce[1]
            if campo is None:
                titolo = QLabel(etichetta)
                titolo.setObjectName("titoloGruppo")
                modulo.addRow(titolo)
                continue
            tipo = voce[2] if len(voce) > 2 else "testo"
            opzioni = voce[3] if len(voce) > 3 else []
            w = self._crea(campo, tipo, opzioni)
            modulo.addRow("" if tipo == "spunta" else etichetta, w)
            if tipo == "spunta":
                w.setText(etichetta)
            self.campi[campo] = w
            self.tipi[campo] = tipo

    def _crea(self, campo: str, tipo: str, opzioni: list[str]) -> QWidget:
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
            return w
        if tipo == "impresa":
            w = QComboBox()
            w.currentIndexChanged.connect(subito)
            return w
        if tipo == "data":
            w = QDateEdit()
            w.setCalendarPopup(True)
            w.setDisplayFormat("dd/MM/yyyy")
            w.setMinimumDate(self.DATA_VUOTA)
            w.setSpecialValueText("non indicata")
            w.dateChanged.connect(subito)
            return w
        if tipo == "numero":
            w = QDoubleSpinBox()
            w.setRange(0, 1e10)
            w.setDecimals(2)
            w.setGroupSeparatorShown(True)
            w.setSuffix(" €")
            w.valueChanged.connect(modificato)
            w.editingFinished.connect(lambda: self._salva(campo))
            return w
        if tipo == "spunta":
            w = QCheckBox()
            w.toggled.connect(subito)
            return w
        w = QLineEdit()
        w.textChanged.connect(modificato)
        w.editingFinished.connect(lambda: self._salva(campo))
        return w

    def valore(self, campo: str) -> Any:
        w, tipo = self.campi[campo], self.tipi[campo]
        if tipo == "scelta":
            return w.currentText().strip()
        if tipo == "impresa":
            return w.currentData()
        if tipo == "data":
            return None if w.date() == self.DATA_VUOTA else w.date().toString(Qt.DateFormat.ISODate)
        if tipo == "numero":
            return w.value()
        if tipo == "spunta":
            return int(w.isChecked())
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
            d = QDate.fromString(valore or "", Qt.DateFormat.ISODate)
            w.setDate(d if d.isValid() else self.DATA_VUOTA)
        elif tipo == "numero":
            w.setValue(float(valore or 0))
        elif tipo == "spunta":
            w.setChecked(bool(valore))
        else:
            w.setText(valore or "")

    def _salva(self, campo: str) -> None:
        if self.id_ is not None and campo in self._modificati:
            self.repo.aggiorna(self.tabella, self.id_, **{campo: self.valore(campo)})
            self._modificati.discard(campo)

    def salva_in_sospeso(self) -> None:
        if self.id_ is not None and self._modificati and self.repo.leggi(self.tabella, self.id_):
            self.repo.aggiorna(self.tabella, self.id_, **{c: self.valore(c) for c in self._modificati})
        self._modificati.clear()

    def carica(self, id_: int | None) -> None:
        self.salva_in_sospeso()
        self.id_ = id_
        record = self.repo.leggi(self.tabella, id_) if id_ is not None else None
        self._caricamento = True
        try:
            for campo in self.campi:
                self._imposta(campo, record[campo] if record else None)
        finally:
            self._caricamento = False
        self.setEnabled(record is not None)


class Pagina(QWidget):
    titolo = ""
    voce = ""  # nome breve nella barra di navigazione
    icona = "cantiere"  # nome in ui/icone.py

    def __init__(self, repo: Repository):
        super().__init__()
        self.repo = repo
        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(_titolo(self.titolo))

    def aggiorna(self) -> None:
        """Ricarica i dati quando la pagina viene mostrata."""

    def salva_in_sospeso(self) -> None:
        """Salva le modifiche non ancora scritte (cambio pagina, chiusura)."""

    def genera_principale(self) -> None:
        """Genera il documento principale del programma (pulsante nella barra degli strumenti)."""
        raise NotImplementedError


class PaginaDatiGenerali(Pagina):
    titolo = "Dati generali del cantiere"
    voce = "Dati generali"
    icona = "cantiere"
    funzione_riepilogo = staticmethod(calcola_riepilogo)
    CAMPI = [
        ("nome", "Denominazione dell'opera"),
        ("natura_opera", "Natura dell'opera"),
        ("indirizzo", "Indirizzo"),
        ("cap", "CAP"),
        ("comune", "Comune"),
        ("provincia", "Provincia"),
        ("titolo_abilitativo", "Titolo abilitativo (permesso, SCIA, CILA...)"),
    ]

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self._caricata = False
        self.riepilogo = Riepilogo(self.funzione_riepilogo) if self.funzione_riepilogo else None
        if self.riepilogo is not None:
            self.layout_.addWidget(self.riepilogo)
        self.layout_.addSpacing(8)
        modulo = QFormLayout()
        self.campi: dict[str, QLineEdit] = {}
        for campo, etichetta in self.CAMPI:
            e = QLineEdit()
            e.editingFinished.connect(lambda c=campo, w=e: self.repo.aggiorna_cantiere(**{c: w.text()}))
            modulo.addRow(etichetta, e)
            self.campi[campo] = e
        self.campi["provincia"].setMaxLength(2)

        self.importo = self._numero(" €", "importo_lavori")
        modulo.addRow("Importo presunto dei lavori", self.importo)
        self.costo_ug = self._numero(" €", "costo_uomo_giorno")
        self.costo_ug.setToolTip("Costo medio di un uomo-giorno, usato per stimare la durata delle fasi.")
        modulo.addRow("Costo medio uomo-giorno", self.costo_ug)

        self.descrizione = QPlainTextEdit()
        self.descrizione.setPlaceholderText("Descrizione sintetica dell'opera")
        self._timer = QTimer(self, singleShot=True, interval=700)
        self._timer.timeout.connect(self._salva_descrizione)
        self.descrizione.textChanged.connect(self._timer.start)
        modulo.addRow("Descrizione", self.descrizione)
        self.layout_.addLayout(modulo)


    def _numero(self, suffisso: str, campo: str) -> QDoubleSpinBox:
        s = QDoubleSpinBox()
        s.setRange(0, 1e10)
        s.setDecimals(2)
        s.setGroupSeparatorShown(True)
        s.setSuffix(suffisso)
        s.editingFinished.connect(lambda: self._salva_numero(campo, s.value()))
        return s

    def _salva_numero(self, campo: str, valore: float) -> None:
        self.repo.aggiorna_cantiere(**{campo: valore})
        if self.riepilogo is not None:
            self.riepilogo.aggiorna(self.repo)

    def _salva_descrizione(self) -> None:
        self.repo.aggiorna_cantiere(descrizione=self.descrizione.toPlainText())

    def salva_in_sospeso(self) -> None:
        # I campi salvano all'uscita dal campo: alla chiusura della finestra
        # potrebbe non accadere, quindi salviamo tutto qui.
        self._timer.stop()
        if not self._caricata:
            return
        self.repo.aggiorna_cantiere(
            **{campo: e.text() for campo, e in self.campi.items()},
            importo_lavori=self.importo.value(),
            costo_uomo_giorno=self.costo_ug.value(),
            descrizione=self.descrizione.toPlainText(),
        )

    def aggiorna(self) -> None:
        self._caricata = True
        c = self.repo.cantiere()
        for campo, e in self.campi.items():
            e.setText(c[campo])
        self.importo.setValue(c["importo_lavori"])
        self.costo_ug.setValue(c["costo_uomo_giorno"])
        self.descrizione.blockSignals(True)
        self.descrizione.setPlainText(c["descrizione"])
        self.descrizione.blockSignals(False)
        if self.riepilogo is not None:
            self.riepilogo.aggiorna(self.repo)


class PaginaSoggetti(Pagina):
    titolo = "Soggetti con compiti di sicurezza"
    voce = "Soggetti"
    icona = "soggetti"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.committente_rl = QCheckBox("Il committente è anche responsabile dei lavori")
        self.committente_rl.setToolTip("Nei documenti il committente compare anche come responsabile dei lavori "
                                       "e non serve inserire un responsabile dei lavori a parte.")
        self.committente_rl.toggled.connect(self._salva_committente_rl)
        self.layout_.addWidget(self.committente_rl)
        self.tabella = TabellaCrud(repo, "soggetti", [
            Colonna("ruolo", "Ruolo", "scelta", scelte=lambda: [(r, r) for r in RUOLI],
                    scelta_libera=True, larghezza=260),
            Colonna("nome", "Nominativo / ragione sociale", larghezza=210),
            Colonna("rappresentante", "Nella persona di", larghezza=170),
            Colonna("qualifica", "Qualifica", larghezza=140),
            Colonna("codice_fiscale", "Codice fiscale", larghezza=150),
            Colonna("partita_iva", "P. IVA", larghezza=110),
            Colonna("indirizzo", "Indirizzo", larghezza=200),
            Colonna("telefono", "Telefono", larghezza=110),
            Colonna("email", "Email", larghezza=170),
            Colonna("pec", "PEC"),
        ])
        self.layout_.addWidget(self.tabella)

    def _salva_committente_rl(self, attivo: bool) -> None:
        self.repo.aggiorna_cantiere(committente_rl=int(attivo))

    def aggiorna(self) -> None:
        self.committente_rl.blockSignals(True)
        self.committente_rl.setChecked(bool(self.repo.cantiere()["committente_rl"]))
        self.committente_rl.blockSignals(False)
        self.tabella.ricarica()


class PaginaImprese(Pagina):
    titolo = "Imprese, lavoratori e dati per il POS"
    voce = "Imprese e lavoratori"
    icona = "imprese"
    # Schede di dettaglio mostrate dal programma: dati, figure, lavoratori, pos.
    schede_visibili: tuple[str, ...] = ("dati", "figure", "lavoratori", "pos")

    CAMPI_DATI = [
        (None, "Anagrafica"),
        ("forma_giuridica", "Forma giuridica", "scelta", anagrafiche.FORME_GIURIDICHE),
        ("codice_fiscale", "Codice fiscale"),
        ("cciaa", "Iscrizione CCIAA (n. REA)"),
        ("ateco", "Codice ATECO / categoria ISTAT"),
        ("affidataria_id", "Impresa affidataria di riferimento", "impresa"),
        (None, "Sede legale e recapiti"),
        ("indirizzo", "Indirizzo"),
        ("cap", "CAP"),
        ("comune", "Comune"),
        ("provincia", "Provincia"),
        ("email", "Email"),
        ("pec", "PEC"),
        ("recapito_cantiere", "Ufficio o recapito in cantiere"),
        (None, "Posizioni assicurative e contratto"),
        ("inail", "Posizione INAIL (codice ditta / PAT)"),
        ("inps", "Matricola INPS"),
        ("cassa_edile", "Cassa edile (cassa e codice impresa)"),
        ("ccnl", "Contratto collettivo applicato", "scelta", anagrafiche.CCNL),
        ("organico", "Organico medio annuo"),
        ("durc_scadenza", "DURC valido fino al", "data"),
        (None, "Qualificazione"),
        ("dvr_data", "Data del documento di valutazione dei rischi", "data"),
        ("soa", "Attestazione SOA (categorie e classifiche)"),
        ("certificazioni", "Certificazioni (ISO 9001, ISO 45001, ...)"),
        (None, "Lavori in questo cantiere"),
        ("tipologia_lavori", "Tipologia dei lavori affidati"),
        ("importo_lavori", "Importo dei lavori da eseguire", "numero"),
        ("orario_lavoro", "Orario di lavoro in cantiere"),
    ]

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.tabella = TabellaCrud(repo, "imprese", [
            Colonna("ragione_sociale", "Ragione sociale", larghezza=240),
            Colonna("tipo", "Tipologia", "scelta", scelte=lambda: [(t, t) for t in TIPI_IMPRESA],
                    scelta_libera=True, larghezza=200),
            Colonna("partita_iva", "P. IVA", larghezza=120),
            Colonna("referente", "Referente", larghezza=150),
            Colonna("telefono", "Telefono"),
        ])

        self.dati = ModuloRecord(repo, "imprese", self.CAMPI_DATI)
        self.dati.campi["provincia"].setMaxLength(2)
        scorrimento_dati = QScrollArea()
        scorrimento_dati.setWidgetResizable(True)
        scorrimento_dati.setWidget(self.dati)

        # Datore di lavoro e figure della sicurezza (Allegato XV 3.2.1 lett. a e b).
        self.figure = ModuloRecord(repo, "imprese", [
            ("datore_lavoro", "Datore di lavoro"),
            ("rspp_datore", "Il datore di lavoro svolge direttamente i compiti di RSPP (art. 34)", "spunta"),
        ])
        self.elenco_figure = TabellaCrud(repo, "figure", [
            Colonna("ruolo", "Figura", "scelta", scelte=lambda: [(r, r) for r in anagrafiche.FIGURE_IMPRESA],
                    scelta_libera=True, larghezza=230),
            Colonna("nome", "Nominativo", larghezza=180),
            Colonna("qualifica", "Qualifica", larghezza=140),
            Colonna("codice_fiscale", "Codice fiscale", larghezza=150),
            Colonna("telefono", "Telefono", larghezza=110),
            Colonna("email", "Email", larghezza=160),
            Colonna("formazione", "Corso / attestato", larghezza=200),
            Colonna("formazione_scadenza", "Aggiornamento entro", "data"),
        ], valori_nuovo=lambda: {"ruolo": "Preposto"})
        self.elenco_figure.imposta_filtro(impresa_id=-1)
        pannello_figure = QWidget()
        lf = QVBoxLayout(pannello_figure)
        lf.addWidget(self.figure)
        aiuto = QLabel("Una riga per persona e per ruolo: RSPP, medico competente, RLS o RLST, preposti, "
                       "direttore tecnico, capocantiere, addetti al primo soccorso e antincendio.")
        aiuto.setObjectName("sottotitolo")
        aiuto.setWordWrap(True)
        lf.addWidget(aiuto)
        lf.addWidget(self.elenco_figure)

        self.lavoratori = TabellaCrud(repo, "lavoratori", [
            Colonna("nome", "Nominativo", larghezza=200),
            Colonna("mansione", "Mansione", larghezza=180),
            Colonna("formazione", "Formazione e addestramento", "testo_lungo"),
            Colonna("idoneita_scadenza", "Idoneità sanitaria fino al", "data", larghezza=160),
        ])
        self.testi_pos = TestiLiberi(repo, SEZIONI_POS, altezza=80, contesto_ai=self._contesto_ai)
        scorrimento = QScrollArea()
        scorrimento.setWidgetResizable(True)
        scorrimento.setWidget(self.testi_pos)

        self.schede = QTabWidget()
        for chiave, widget, titolo in (("dati", scorrimento_dati, "Dati dell'impresa"),
                                       ("figure", pannello_figure, "Figure della sicurezza"),
                                       ("lavoratori", self.lavoratori, "Lavoratori"),
                                       ("pos", scorrimento, "Testi del POS")):
            if chiave in self.schede_visibili:
                self.schede.addTab(widget, titolo)
        self.schede.setEnabled(False)
        self.schede.setVisible(bool(self.schede_visibili))
        # Le schede non mostrate restano figlie della pagina: senza un genitore
        # Qt le distruggerebbe mentre la pagina le usa ancora.
        for w in (scorrimento_dati, pannello_figure, self.lavoratori, scorrimento):
            if w.parent() is None:
                w.setParent(self)
                w.hide()

        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(self.tabella)
        divisore.addWidget(self.schede)
        divisore.setSizes([220, 480])
        self.layout_.addWidget(divisore)
        self.tabella.selezione_cambiata.connect(self._impresa_selezionata)

    def _contesto_ai(self) -> str:
        id_ = self.tabella.id_selezionato()
        impresa = self.repo.leggi("imprese", id_) if id_ is not None else None
        if impresa is None:
            return contesto_cantiere(self.repo)
        fasi = self.repo.elenco("fasi", impresa_id=id_)
        lavoratori = self.repo.elenco("lavoratori", impresa_id=id_)
        righe = [
            f"Impresa che redige il POS: {impresa['ragione_sociale']} ({impresa['tipo']})",
            f"Orario di lavoro: {impresa['orario_lavoro'] or 'non indicato'}",
            f"Tipologia dei lavori: {impresa['tipologia_lavori'] or 'non indicata'}",
            "Lavorazioni dell'impresa: " + "; ".join(f"{f['codice']} {f['descrizione']}" for f in fasi),
            "Lavoratori: " + "; ".join(f"{l['nome']} ({l['mansione']})" for l in lavoratori),
        ]
        return contesto_cantiere(self.repo) + "\n\n" + "\n".join(righe)

    def _impresa_selezionata(self, id_: int | None) -> None:
        self.schede.setEnabled(id_ is not None)
        self.dati.carica(id_)
        self.figure.carica(id_)
        self.elenco_figure.imposta_filtro(impresa_id=id_ if id_ is not None else -1)
        self.lavoratori.imposta_filtro(impresa_id=id_ if id_ is not None else -1)
        self.testi_pos.carica(lambda s, i=id_ if id_ is not None else -1: chiave_testo(i, s))

    def salva_in_sospeso(self) -> None:
        self.dati.salva_in_sospeso()
        self.figure.salva_in_sospeso()
        self.testi_pos.salva_in_sospeso()

    def aggiorna(self) -> None:
        self.tabella.ricarica()


def _valida_fase(fase: dict) -> str | None:
    inizio, fine = analisi.data(fase.get("data_inizio")), analisi.data(fase.get("data_fine"))
    if inizio and fine and fine < inizio:
        return "La data di fine non può precedere la data di inizio."
    return None


class DialogoArchivio(QDialog):
    def __init__(self, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.setWindowTitle("Importa lavorazioni dall'archivio")
        self.resize(640, 520)
        self.filtro = QLineEdit()
        self.filtro.setPlaceholderText("Cerca una lavorazione...")
        self.filtro.textChanged.connect(self._filtra)
        self.albero = QTreeWidget()
        self.albero.setHeaderLabels(["Lavorazione", "Macchine e attrezzi"])
        self.albero.setColumnWidth(0, 360)
        for categoria, lavorazioni in per_categoria().items():
            nodo = QTreeWidgetItem([categoria])
            nodo.setFlags(nodo.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            self.albero.addTopLevelItem(nodo)
            for lav in lavorazioni:
                item = QTreeWidgetItem([f"{lav['codice']}  {lav['descrizione']}",
                                        ", ".join(lav["attrezzature"])])
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked)
                item.setData(0, Qt.ItemDataRole.UserRole, lav)
                nodo.addChild(item)
        self.albero.expandAll()
        pulsanti = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Selezionare le lavorazioni da aggiungere al cantiere:"))
        layout.addWidget(self.filtro)
        layout.addWidget(self.albero)
        layout.addWidget(pulsanti)

    def _foglie(self):
        for i in range(self.albero.topLevelItemCount()):
            nodo = self.albero.topLevelItem(i)
            for j in range(nodo.childCount()):
                yield nodo, nodo.child(j)

    def _filtra(self, testo: str) -> None:
        testo = testo.lower().strip()
        visibili: dict[int, bool] = {}
        for nodo, item in self._foglie():
            mostra = not testo or testo in item.text(0).lower() or testo in item.text(1).lower()
            item.setHidden(not mostra)
            visibili[id(nodo)] = visibili.get(id(nodo), False) or mostra
        for i in range(self.albero.topLevelItemCount()):
            nodo = self.albero.topLevelItem(i)
            nodo.setHidden(not visibili.get(id(nodo), False))

    def selezionate(self) -> list[dict]:
        return [item.data(0, Qt.ItemDataRole.UserRole) for _, item in self._foglie()
                if item.checkState(0) == Qt.CheckState.Checked]


class PaginaFasi(Pagina):
    titolo = "Fasi di lavoro e cronoprogramma (Gantt analitico)"
    voce = "Fasi e cronoprogramma"
    icona = "fasi"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.fasi = TabellaCrud(repo, "fasi", [
            Colonna("codice", "Codice", larghezza=60),
            Colonna("descrizione", "Lavorazione", larghezza=260),
            Colonna("impresa_id", "Impresa", "scelta", scelte=self._imprese, larghezza=170),
            Colonna("zona", "Zona", larghezza=90),
            Colonna("importo", "Importo €", "decimale", larghezza=100),
            Colonna("incidenza_manodopera", "Manodopera %", "decimale", massimo=100, larghezza=115),
            Colonna("lavoratori", "Squadra", "intero", minimo=0, massimo=999, larghezza=65),
            Colonna("data_inizio", "Inizio", "data", larghezza=95),
            Colonna("data_fine", "Fine", "data", larghezza=95),
            Colonna("uomini_giorno", "Uomini-giorno", "calcolata",
                    calcola=lambda f: str(analisi.uomini_giorno([f]) or "")),
        ], valida=_valida_fase)
        archivio = primario(QPushButton("Importa da archivio..."))
        archivio.clicked.connect(self._importa)
        calcola = QPushButton("Calcola durata")
        calcola.setToolTip("Data di fine da importo, incidenza della manodopera, squadra e costo uomo-giorno.")
        calcola.clicked.connect(self._calcola_durata)
        self.fasi.pulsanti.insertWidget(2, archivio)
        self.fasi.pulsanti.insertWidget(3, calcola)

        self.rischi = TabellaCrud(repo, "rischi", [
            Colonna("descrizione", "Rischio", "testo_lungo"),
            Colonna("fonte", "Origine", larghezza=130),
            Colonna("probabilita", "P", "intero", minimo=1, massimo=4, larghezza=40),
            Colonna("danno", "D", "intero", minimo=1, massimo=4, larghezza=40),
            Colonna("livello", "Livello", "calcolata", larghezza=110, calcola=lambda r: (
                f"{(l := analisi.livello_rischio(r['probabilita'], r['danno']))} "
                f"{analisi.classe_rischio(l)}")),
            Colonna("misure", "Misure di prevenzione e protezione", "testo_lungo"),
            Colonna("dpi", "DPI", "testo_lungo"),
        ])
        self.rischi.modificata.connect(self._aggiorna_gantt)
        suggerisci = QPushButton(icona("ai", "#E8792B"), "Suggerisci rischi con l'AI")
        suggerisci.clicked.connect(self._suggerisci_rischi)
        self.rischi.pulsanti.insertWidget(2, suggerisci)

        self.attrezzature = TabellaCrud(repo, "attrezzature", [
            Colonna("tipo", "Tipo", "scelta", scelte=lambda: [(t, t) for t in TIPI_ATTREZZATURA],
                    larghezza=160),
            Colonna("nome", "Nome", "scelta", scelta_libera=True,
                    scelte=lambda: [(n, n) for n in sorted(ATTREZZATURE)]),
        ])
        self.scelta_archivio = QComboBox()
        self.scelta_archivio.addItems(sorted(ATTREZZATURE))
        aggiungi_archivio = QPushButton("Aggiungi con i suoi rischi")
        aggiungi_archivio.clicked.connect(self._aggiungi_attrezzatura)
        self.attrezzature.pulsanti.insertWidget(2, QLabel("  Dall'archivio:"))
        self.attrezzature.pulsanti.insertWidget(3, self.scelta_archivio)
        self.attrezzature.pulsanti.insertWidget(4, aggiungi_archivio)

        self.dettaglio = QTabWidget()
        self.dettaglio.addTab(self.rischi, "Rischi e misure")
        self.dettaglio.addTab(self.attrezzature, "Macchine, attrezzi e opere provvisionali")
        self.dettaglio.setEnabled(False)

        self.gantt = Gantt()
        self.gantt.fase_modificata.connect(self._fase_trascinata)
        scorrimento = QScrollArea()
        scorrimento.setWidget(self.gantt)
        scorrimento.setWidgetResizable(False)
        self.zoom = QComboBox()
        self.zoom.addItems(list(ZOOM))
        self.zoom.setCurrentText(ZOOM_PREDEFINITO)
        self.zoom.currentTextChanged.connect(self.gantt.imposta_zoom)
        barra_gantt = QHBoxLayout()
        barra_gantt.addWidget(QLabel("Cronoprogramma - scala:"))
        barra_gantt.addWidget(self.zoom)
        barra_gantt.addStretch()
        aiuto = QLabel("Trascina una barra per spostare la fase, dal bordo destro per cambiarne la durata.")
        aiuto.setObjectName("sottotitolo")
        barra_gantt.addWidget(aiuto)
        riquadro_gantt = QWidget()
        lay_gantt = QVBoxLayout(riquadro_gantt)
        lay_gantt.setContentsMargins(0, 0, 0, 0)
        lay_gantt.addLayout(barra_gantt)
        lay_gantt.addWidget(scorrimento)

        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(self.fasi)
        divisore.addWidget(riquadro_gantt)
        divisore.addWidget(self.dettaglio)
        divisore.setSizes([200, 400, 220])
        self.layout_.addWidget(divisore)

        self.fasi.selezione_cambiata.connect(self._fase_selezionata)
        self.fasi.modificata.connect(self._aggiorna_gantt)

    def _imprese(self) -> list[tuple[int | None, str]]:
        return [(None, "(da definire)")] + [
            (i["id"], i["ragione_sociale"] or f"Impresa {i['id']}") for i in self.repo.elenco("imprese")
        ]

    def _fase_selezionata(self, id_: int | None) -> None:
        self.dettaglio.setEnabled(id_ is not None)
        filtro = id_ if id_ is not None else -1
        self.rischi.imposta_filtro(fase_id=filtro)
        self.attrezzature.imposta_filtro(fase_id=filtro)

    def _aggiorna_gantt(self) -> None:
        imprese = {i["id"]: i["ragione_sociale"] or f"Impresa {i['id']}" for i in self.repo.elenco("imprese")}
        self.gantt.imposta_fasi(self.fasi.righe(), analisi.livelli_fasi(self.repo.elenco("rischi")), imprese)

    def _fase_trascinata(self, id_: int, inizio: str, fine: str) -> None:
        self.repo.aggiorna("fasi", id_, data_inizio=inizio, data_fine=fine)
        self.fasi.ricarica()
        self.fasi.seleziona(id_)
        self._aggiorna_gantt()

    def _importa(self) -> None:
        dialogo = DialogoArchivio(self)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        ultima = None
        for lav in dialogo.selezionate():
            ultima = self.repo.importa_lavorazione(lav)
        self.fasi.ricarica()
        if ultima is not None:
            self.fasi.seleziona(ultima)
        self._aggiorna_gantt()

    def _aggiungi_attrezzatura(self) -> None:
        fase = self.fasi.id_selezionato()
        if fase is None:
            return
        self.repo.aggiungi_attrezzatura(fase, self.scelta_archivio.currentText())
        self.attrezzature.ricarica()
        self.rischi.ricarica()
        self._aggiorna_gantt()

    def _suggerisci_rischi(self) -> None:
        fase_id = self.fasi.id_selezionato()
        if fase_id is None:
            return
        fase = self.repo.leggi("fasi", fase_id)
        lavorazione = f"{fase['codice']} {fase['descrizione']}".strip()
        if not lavorazione:
            QMessageBox.information(self, "Assistente AI", "Indicare prima la descrizione della lavorazione.")
            return
        attrezzature = [a["nome"] for a in self.repo.elenco("attrezzature", fase_id=fase_id)]
        esistenti = [r["descrizione"] for r in self.repo.elenco("rischi", fase_id=fase_id)]
        esegui_ai(self, "L'assistente sta analizzando la lavorazione...",
                  lambda ai: ai.suggerisci_rischi(lavorazione, attrezzature, esistenti),
                  lambda proposte: self._scegli_rischi(fase_id, proposte))

    def _scegli_rischi(self, fase_id: int, proposte: list[dict]) -> None:
        if not proposte:
            QMessageBox.information(self, "Assistente AI", "Nessun rischio aggiuntivo individuato.")
            return
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Rischi suggeriti dall'assistente AI")
        dialogo.resize(760, 460)
        elenco = QListWidget()
        for r in proposte:
            livello = analisi.livello_rischio(r["probabilita"], r["danno"])
            item = QListWidgetItem(f"{r['descrizione']}  -  P{r['probabilita']} x D{r['danno']} = {livello} "
                                   f"{analisi.classe_rischio(livello)}\n    Misure: {r['misure']}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            elenco.addItem(item)
        nota = QLabel("Selezionare i rischi da aggiungere alla fase. Valori e misure restano modificabili.")
        nota.setWordWrap(True)
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.accepted.connect(dialogo.accept)
        pulsanti.rejected.connect(dialogo.reject)
        layout = QVBoxLayout(dialogo)
        layout.addWidget(nota)
        layout.addWidget(elenco)
        layout.addWidget(pulsanti)
        if dialogo.exec() != QDialog.DialogCode.Accepted or not self.repo.leggi("fasi", fase_id):
            return
        for i, r in enumerate(proposte):
            if elenco.item(i).checkState() == Qt.CheckState.Checked:
                self.repo.inserisci("rischi", fase_id=fase_id, **r)
        self.rischi.ricarica()
        self._aggiorna_gantt()

    def _calcola_durata(self) -> None:
        id_ = self.fasi.id_selezionato()
        if id_ is None:
            QMessageBox.information(self, "Calcola durata", "Selezionare una fase.")
            return
        f = self.repo.leggi("fasi", id_)
        costo = self.repo.cantiere()["costo_uomo_giorno"]
        giorni = analisi.durata_stimata(f["importo"], f["incidenza_manodopera"], costo, f["lavoratori"])
        inizio = analisi.data(f["data_inizio"])
        if giorni is None or inizio is None:
            QMessageBox.information(
                self, "Calcola durata",
                "Indicare data di inizio, importo, incidenza della manodopera e squadra della fase, "
                "e il costo medio uomo-giorno nei dati generali.")
            return
        fine = analisi.fine_dopo_giorni_lavorativi(inizio, giorni)
        self.repo.aggiorna("fasi", id_, data_fine=fine.isoformat())
        self.fasi.ricarica()
        self._aggiorna_gantt()

    def aggiorna(self) -> None:
        self.fasi.ricarica()
        self._aggiorna_gantt()


class PaginaInterferenze(Pagina):
    titolo = "Interferenze e prescrizioni di coordinamento"
    voce = "Interferenze"
    icona = "interferenze"
    COLONNE = ["Fase", "Fase interferente", "Zona", "Periodo", "Gravità", "Prescrizioni del coordinatore"]

    def __init__(self, repo: Repository):
        super().__init__(repo)
        nota = QLabel(
            "Sono elencate le fasi contemporanee di imprese diverse nella stessa zona (o con zona non "
            "indicata), dalla più grave. Scrivere le prescrizioni solo dove servono: alle altre il PSC "
            "applica la prescrizione generica di sfasamento."
        )
        nota.setWordWrap(True)
        self.layout_.addWidget(nota)
        self.vista = QTableWidget(0, len(self.COLONNE))
        self.vista.setAlternatingRowColors(True)
        self.vista.setHorizontalHeaderLabels(self.COLONNE)
        self.vista.verticalHeader().setVisible(False)
        self.vista.setWordWrap(True)
        self.vista.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        intestazione = self.vista.horizontalHeader()
        for i, larghezza in enumerate((220, 220, 90, 170, 100)):
            self.vista.setColumnWidth(i, larghezza)
        intestazione.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.vista.itemChanged.connect(self._modificata)
        self.layout_.addWidget(self.vista)
        self._chiavi: list[tuple[int, int]] = []

    def _modificata(self, item: QTableWidgetItem) -> None:
        if item.column() == 5:
            a, b = self._chiavi[item.row()]
            self.repo.salva_prescrizione(a, b, item.text())

    def aggiorna(self) -> None:
        fasi = self.repo.elenco("fasi")
        elenco = analisi.interferenze(fasi, analisi.livelli_fasi(self.repo.elenco("rischi")))
        prescrizioni = self.repo.prescrizioni()
        self._chiavi = [i.chiave for i in elenco]
        self.vista.blockSignals(True)
        self.vista.setRowCount(len(elenco))
        for r, i in enumerate(elenco):
            valori = [
                f"{i.fase_a['codice']} {i.fase_a['descrizione']}",
                f"{i.fase_b['codice']} {i.fase_b['descrizione']}",
                " / ".join(dict.fromkeys(z for z in (i.fase_a["zona"], i.fase_b["zona"]) if z)) or "-",
                f"{i.inizio:%d/%m/%Y} - {i.fine:%d/%m/%Y}",
                f"{i.gravita} {analisi.classe_rischio(i.gravita)}" if i.gravita else "-",
                prescrizioni.get(i.chiave, ""),
            ]
            for c, valore in enumerate(valori):
                item = QTableWidgetItem(valore)
                if c < 5:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if c == 4 and i.gravita:
                    colore = QColor(colore_livello(i.gravita))
                    colore.setAlpha(110)
                    item.setBackground(QBrush(colore))
                self.vista.setItem(r, c, item)
        self.vista.blockSignals(False)
        self.vista.resizeRowsToContents()


class PaginaCosti(Pagina):
    titolo = "Stima dei costi della sicurezza"
    voce = "Costi della sicurezza"
    icona = "costi"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.tabella = TabellaCrud(repo, "costi", [
            Colonna("codice", "Codice", larghezza=80),
            Colonna("descrizione", "Descrizione", "testo_lungo"),
            Colonna("unita", "U.M.", larghezza=60),
            Colonna("quantita", "Quantità", "decimale", larghezza=100),
            Colonna("prezzo_unitario", "Prezzo unitario", "decimale", larghezza=120),
            Colonna("importo", "Importo", "calcolata", larghezza=120,
                    calcola=lambda r: euro(r["quantita"] * r["prezzo_unitario"])),
        ])
        self.totale = QLabel()
        self.totale.setAlignment(Qt.AlignmentFlag.AlignRight)
        font = self.totale.font()
        font.setBold(True)
        self.totale.setFont(font)
        self.tabella.modificata.connect(self._totale)
        self.layout_.addWidget(self.tabella)
        self.layout_.addWidget(self.totale)

    def _totale(self) -> None:
        self.totale.setText(
            f"Totale costi della sicurezza: {euro(analisi.totale_costi(self.tabella.righe()))}"
        )

    def aggiorna(self) -> None:
        self.tabella.ricarica()
        self._totale()


class PaginaRelazione(Pagina):
    titolo = "Relazione del PSC"
    voce = "Relazione del PSC"
    icona = "relazione"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.testi = TestiLiberi(repo, SEZIONI, contesto_ai=lambda: contesto_cantiere(repo))
        scorrimento = QScrollArea()
        scorrimento.setWidgetResizable(True)
        scorrimento.setWidget(self.testi)
        self.layout_.addWidget(scorrimento)

    def salva_in_sospeso(self) -> None:
        self.testi.salva_in_sospeso()

    def aggiorna(self) -> None:
        self.testi.carica()


class PaginaFascicolo(Pagina):
    titolo = "Fascicolo dell'opera"
    voce = "Fascicolo dell'opera"
    icona = "fascicolo"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.interventi = TabellaCrud(repo, "interventi", [
            Colonna("parte_opera", "Parte d'opera", larghezza=130),
            Colonna("intervento", "Intervento di manutenzione", "testo_lungo"),
            Colonna("periodicita", "Periodicità", larghezza=100),
            Colonna("rischi", "Rischi", "testo_lungo"),
            Colonna("misure_in_dotazione", "Misure in dotazione dell'opera", "testo_lungo"),
            Colonna("misure_ausiliarie", "Misure ausiliarie", "testo_lungo"),
        ])
        self.elaborati = TabellaCrud(repo, "elaborati", [
            Colonna("titolo", "Elaborato tecnico", larghezza=320),
            Colonna("autore", "Autore", larghezza=200),
            Colonna("data", "Data", "data", larghezza=100),
            Colonna("collocazione", "Collocazione"),
        ])
        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(_riquadro("Schede II: interventi di manutenzione e misure di sicurezza",
                                     self.interventi))
        divisore.addWidget(_riquadro("Schede III: documentazione di supporto", self.elaborati))
        divisore.setSizes([450, 250])
        self.layout_.addWidget(divisore)

    def aggiorna(self) -> None:
        self.interventi.ricarica()
        self.elaborati.ricarica()


class PaginaDocumenti(Pagina):
    """Generazione dei documenti, revisioni e controlli.

    Le sottoclassi dei singoli programmi scelgono quali documenti offrire
    (`documenti`) e quali controlli eseguire (`controlla`).
    """

    titolo = "Documenti, revisioni e controlli"
    voce = "Documenti e controlli"
    icona = "documenti"
    # psc, fascicolo, notifica: documenti del cantiere; pos, dpi: documenti per impresa
    documenti: tuple[str, ...] = ("psc", "fascicolo", "notifica", "pos")
    principale = "psc"
    controlla = staticmethod(controlli.controlla)

    NOMI = {
        "psc": "Piano di Sicurezza e Coordinamento (PSC)",
        "fascicolo": "Fascicolo dell'opera",
        "notifica": "Notifica preliminare",
        "pos": "Piano Operativo di Sicurezza (POS)",
        "dpi": "Verbali di consegna dei DPI",
        "sostanze": "Elenco delle sostanze pericolose",
    }

    def __init__(self, repo: Repository):
        super().__init__(repo)
        griglia = QGroupBox("Genera documento (.docx)")
        layout = QVBoxLayout(griglia)
        self.impresa = QComboBox()
        per_impresa = [d for d in self.documenti if d in ("pos", "dpi", "sostanze")]
        if per_impresa:
            riga = QHBoxLayout()
            riga.addWidget(QLabel("Impresa:"))
            riga.addWidget(self.impresa, 1)
            layout.addLayout(riga)
        for chiave in self.documenti:
            b = QPushButton(self.NOMI[chiave])
            if chiave == self.principale:
                primario(b)
            b.clicked.connect(lambda _=False, k=chiave: self.genera(k))
            layout.addWidget(b)
        layout.addStretch()

        self.controlli = QListWidget()
        verifica = QPushButton("Esegui i controlli")
        verifica.clicked.connect(self._controlla)
        riquadro_controlli = QGroupBox("Controlli di completezza")
        lc = QVBoxLayout(riquadro_controlli)
        lc.addWidget(verifica, alignment=Qt.AlignmentFlag.AlignLeft)
        lc.addWidget(self.controlli)

        self.revisioni = TabellaCrud(repo, "revisioni", [
            Colonna("documento", "Documento", "scelta", scelte=self._documenti, larghezza=200),
            Colonna("numero", "Rev.", "intero", larghezza=60),
            Colonna("data", "Data", "data", larghezza=100),
            Colonna("descrizione", "Descrizione delle modifiche", "testo_lungo"),
        ])

        alto = QHBoxLayout()
        alto.addWidget(griglia, 1)
        alto.addWidget(_riquadro("Revisioni dei documenti", self.revisioni), 1)
        self.layout_.addLayout(alto)
        self.layout_.addWidget(riquadro_controlli, 1)

    def _documenti(self) -> list[tuple[str, str]]:
        voci = []
        if "psc" in self.documenti:
            voci.append(("PSC", "PSC"))
        if "fascicolo" in self.documenti:
            voci.append(("FASCICOLO", "Fascicolo dell'opera"))
        if "pos" in self.documenti:
            voci += [(f"POS:{i['id']}", f"POS - {i['ragione_sociale']}") for i in self.repo.elenco("imprese")]
        return voci

    def _controlla(self) -> list[controlli.Segnalazione]:
        self.controlli.clear()
        elenco = self.controlla(self.repo)
        if not elenco:
            self.controlli.addItem("Nessun problema rilevato.")
        for s in elenco:
            item = QListWidgetItem(f"[{s.livello}] {s.sezione}: {s.messaggio}")
            item.setForeground(QBrush(QColor("#C0392B" if s.livello == controlli.ERRORE else "#B9770E")))
            self.controlli.addItem(item)
        return elenco

    def _salva_docx(self, nome: str, funzione: Callable[[str], Any]) -> None:
        errori = [s for s in self._controlla() if s.livello == controlli.ERRORE]
        if errori:
            risposta = QMessageBox.question(
                self, "Controlli", f"Ci sono {len(errori)} errori nei dati (vedi elenco).\nGenerare comunque?")
            if risposta != QMessageBox.StandardButton.Yes:
                return
        predefinito = self.repo.progetto.percorso.with_name(f"{nome}.docx".replace("/", "-"))
        percorso, _ = QFileDialog.getSaveFileName(self, "Salva documento", str(predefinito),
                                                  "Documento Word (*.docx)")
        if not percorso:
            return
        try:
            file = funzione(percorso)
        except PermissionError:
            QMessageBox.warning(self, "Errore", "Impossibile scrivere il file: è aperto in Word?")
            return
        risposta = QMessageBox.question(self, "Documento generato", f"Creato {Path(file).name}.\nAprirlo ora?")
        if risposta == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(file)))

    def genera(self, chiave: str | None = None) -> None:
        chiave = chiave or self.principale
        cantiere = self.repo.cantiere()["nome"] or "Cantiere"
        if chiave in ("pos", "dpi", "sostanze"):
            impresa = self.impresa.currentData()
            if impresa is None:
                QMessageBox.information(self, "Documenti", "Inserire prima l'impresa.")
                return
            nome = self.impresa.currentText()
            if chiave == "pos":
                self._salva_docx(f"POS - {nome} - {cantiere}", lambda p: genera_pos(self.repo, impresa, p))
            elif chiave == "sostanze":
                self._salva_docx(f"Sostanze pericolose - {nome}",
                                 lambda p: genera_elenco_sostanze(self.repo, impresa, p))
            else:
                self._salva_docx(f"Consegna DPI - {nome}", lambda p: genera_consegna_dpi(self.repo, impresa, p))
            return
        funzioni = {"psc": genera_psc, "fascicolo": genera_fascicolo, "notifica": genera_notifica}
        nomi = {"psc": "PSC", "fascicolo": "Fascicolo", "notifica": "Notifica preliminare"}
        self._salva_docx(f"{nomi[chiave]} - {cantiere}", lambda p: funzioni[chiave](self.repo, p))

    def genera_principale(self) -> None:
        self.genera()

    def aggiorna(self) -> None:
        corrente = self.impresa.currentData()
        self.impresa.clear()
        for i in self.repo.elenco("imprese"):
            if i["tipo"] != "Lavoratore autonomo":
                self.impresa.addItem(i["ragione_sociale"] or f"Impresa {i['id']}", i["id"])
        self.impresa.setCurrentIndex(max(self.impresa.findData(corrente), 0))
        self.revisioni.ricarica()
        self._controlla()
