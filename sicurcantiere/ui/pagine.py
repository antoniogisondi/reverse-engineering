"""Pagine della finestra principale."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QBrush, QColor, QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
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

from sicurcantiere import analisi, controlli
from sicurcantiere.archivio import ATTREZZATURE, per_categoria
from sicurcantiere.documenti.comune import euro
from sicurcantiere.documenti.fascicolo import genera_fascicolo
from sicurcantiere.documenti.notifica import genera_notifica
from sicurcantiere.documenti.pos import SEZIONI_POS, chiave_testo, genera_pos
from sicurcantiere.documenti.psc import genera_psc
from sicurcantiere.relazione import SEZIONI
from sicurcantiere.repository import Repository
from sicurcantiere.ui.gantt import ZOOM, ZOOM_PREDEFINITO, Gantt, colore_livello
from sicurcantiere.ui.riepilogo import Riepilogo
from sicurcantiere.ui.tabella import Colonna, TabellaCrud

RUOLI = [
    "Committente",
    "Responsabile dei lavori",
    "Coordinatore per la progettazione (CSP)",
    "Coordinatore per l'esecuzione (CSE)",
    "Progettista",
    "Direttore dei lavori",
]
TIPI_IMPRESA = ["Affidataria", "Esecutrice", "Lavoratore autonomo"]
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


class TestiLiberi(QWidget):
    """Editor di più sezioni di testo, salvate con un breve ritardo."""

    def __init__(self, repo: Repository, sezioni: list[tuple[str, str]],
                 chiave: Callable[[str], str] = lambda s: s, altezza: int = 120):
        super().__init__()
        self.repo = repo
        self.chiave = chiave
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
            layout.addWidget(_riquadro(titolo, editor))
            self.editor[sezione] = editor

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
    """Modulo con campi di testo collegati a un record di una tabella."""

    def __init__(self, repo: Repository, tabella: str, campi: list[tuple[str, str]]):
        super().__init__()
        self.repo = repo
        self.tabella = tabella
        self.id_: int | None = None
        self.campi: dict[str, QLineEdit] = {}
        modulo = QFormLayout(self)
        for campo, etichetta in campi:
            e = QLineEdit()
            e.editingFinished.connect(lambda c=campo: self._salva(c))
            modulo.addRow(etichetta, e)
            self.campi[campo] = e

    def _salva(self, campo: str) -> None:
        if self.id_ is not None:
            self.repo.aggiorna(self.tabella, self.id_, **{campo: self.campi[campo].text()})

    def salva_in_sospeso(self) -> None:
        if self.id_ is not None and self.repo.leggi(self.tabella, self.id_):
            self.repo.aggiorna(self.tabella, self.id_, **{c: e.text() for c, e in self.campi.items()})

    def carica(self, id_: int | None) -> None:
        self.salva_in_sospeso()
        self.id_ = id_
        record = self.repo.leggi(self.tabella, id_) if id_ is not None else None
        for campo, e in self.campi.items():
            e.setText(record[campo] if record else "")
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


class PaginaDatiGenerali(Pagina):
    titolo = "Dati generali del cantiere"
    voce = "Dati generali"
    icona = "cantiere"
    CAMPI = [
        ("nome", "Denominazione dell'opera"),
        ("natura_opera", "Natura dell'opera"),
        ("indirizzo", "Indirizzo"),
        ("comune", "Comune"),
        ("provincia", "Provincia"),
    ]

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self._caricata = False
        self.riepilogo = Riepilogo()
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
        self.riepilogo.aggiorna(self.repo)


class PaginaSoggetti(Pagina):
    titolo = "Soggetti con compiti di sicurezza"
    voce = "Soggetti"
    icona = "soggetti"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.tabella = TabellaCrud(repo, "soggetti", [
            Colonna("ruolo", "Ruolo", "scelta", scelte=lambda: [(r, r) for r in RUOLI],
                    scelta_libera=True, larghezza=260),
            Colonna("nome", "Nominativo", larghezza=200),
            Colonna("codice_fiscale", "Codice fiscale", larghezza=150),
            Colonna("indirizzo", "Indirizzo", larghezza=200),
            Colonna("telefono", "Telefono", larghezza=110),
            Colonna("email", "Email"),
        ])
        self.layout_.addWidget(self.tabella)

    def aggiorna(self) -> None:
        self.tabella.ricarica()


class PaginaImprese(Pagina):
    titolo = "Imprese, lavoratori e dati per il POS"
    voce = "Imprese e lavoratori"
    icona = "imprese"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.tabella = TabellaCrud(repo, "imprese", [
            Colonna("ragione_sociale", "Ragione sociale", larghezza=240),
            Colonna("tipo", "Tipo", "scelta", scelte=lambda: [(t, t) for t in TIPI_IMPRESA],
                    larghezza=150),
            Colonna("partita_iva", "P. IVA", larghezza=120),
            Colonna("indirizzo", "Sede", larghezza=200),
            Colonna("referente", "Referente", larghezza=150),
            Colonna("telefono", "Telefono"),
        ])

        self.figure = ModuloRecord(repo, "imprese", [
            ("codice_fiscale", "Codice fiscale"),
            ("datore_lavoro", "Datore di lavoro"),
            ("rspp", "RSPP"),
            ("medico_competente", "Medico competente"),
            ("rls", "RLS / RLST"),
            ("preposto", "Direttore tecnico / capocantiere / preposto"),
            ("addetti_emergenze", "Addetti primo soccorso, antincendio, evacuazione"),
            ("posizione_inail_inps", "Posizioni INAIL / INPS / Cassa edile"),
            ("orario_lavoro", "Orario di lavoro in cantiere"),
        ])
        self.lavoratori = TabellaCrud(repo, "lavoratori", [
            Colonna("nome", "Nominativo", larghezza=200),
            Colonna("mansione", "Mansione", larghezza=180),
            Colonna("formazione", "Formazione e addestramento", "testo_lungo"),
            Colonna("idoneita_scadenza", "Idoneità sanitaria fino al", "data", larghezza=160),
        ])
        self.testi_pos = TestiLiberi(repo, SEZIONI_POS, altezza=80)
        scorrimento = QScrollArea()
        scorrimento.setWidgetResizable(True)
        scorrimento.setWidget(self.testi_pos)

        self.schede = QTabWidget()
        self.schede.addTab(self.figure, "Figure della sicurezza")
        self.schede.addTab(self.lavoratori, "Lavoratori")
        self.schede.addTab(scorrimento, "Testi del POS")
        self.schede.setEnabled(False)

        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(self.tabella)
        divisore.addWidget(self.schede)
        divisore.setSizes([250, 450])
        self.layout_.addWidget(divisore)
        self.tabella.selezione_cambiata.connect(self._impresa_selezionata)

    def _impresa_selezionata(self, id_: int | None) -> None:
        self.schede.setEnabled(id_ is not None)
        self.figure.carica(id_)
        self.lavoratori.imposta_filtro(impresa_id=id_ if id_ is not None else -1)
        self.testi_pos.carica(lambda s, i=id_ if id_ is not None else -1: chiave_testo(i, s))

    def salva_in_sospeso(self) -> None:
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
        self.testi = TestiLiberi(repo, SEZIONI)
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
    titolo = "Documenti, revisioni e controlli"
    voce = "Documenti e controlli"
    icona = "documenti"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        griglia = QGroupBox("Genera documento (.docx)")
        layout = QVBoxLayout(griglia)
        for testo, azione in (
            ("Piano di Sicurezza e Coordinamento (PSC)", self._psc),
            ("Fascicolo dell'opera", self._fascicolo),
            ("Notifica preliminare", self._notifica),
        ):
            b = QPushButton(testo)
            if azione == self._psc:
                primario(b)
            b.clicked.connect(azione)
            layout.addWidget(b)
        riga_pos = QHBoxLayout()
        self.impresa_pos = QComboBox()
        b = QPushButton("Piano Operativo di Sicurezza (POS) per l'impresa:")
        b.clicked.connect(self._pos)
        riga_pos.addWidget(b)
        riga_pos.addWidget(self.impresa_pos, 1)
        layout.addLayout(riga_pos)

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
        return [("PSC", "PSC"), ("FASCICOLO", "Fascicolo dell'opera")] + [
            (f"POS:{i['id']}", f"POS - {i['ragione_sociale']}") for i in self.repo.elenco("imprese")
        ]

    def _controlla(self) -> list[controlli.Segnalazione]:
        self.controlli.clear()
        elenco = controlli.controlla(self.repo)
        if not elenco:
            self.controlli.addItem("Nessun problema rilevato.")
        for s in elenco:
            item = QListWidgetItem(f"[{s.livello}] {s.sezione}: {s.messaggio}")
            item.setForeground(QBrush(QColor("#C0392B" if s.livello == controlli.ERRORE else "#B9770E")))
            self.controlli.addItem(item)
        return elenco

    def _genera(self, nome: str, funzione: Callable[[str], Any]) -> None:
        errori = [s for s in self._controlla() if s.livello == controlli.ERRORE]
        if errori:
            risposta = QMessageBox.question(
                self, "Controlli", f"Ci sono {len(errori)} errori nei dati (vedi elenco).\nGenerare comunque?")
            if risposta != QMessageBox.StandardButton.Yes:
                return
        predefinito = self.repo.progetto.percorso.with_name(f"{nome}.docx")
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

    def _nome_cantiere(self) -> str:
        return self.repo.cantiere()["nome"] or "Cantiere"

    def _psc(self) -> None:
        self._genera(f"PSC - {self._nome_cantiere()}", lambda p: genera_psc(self.repo, p))

    def _fascicolo(self) -> None:
        self._genera(f"Fascicolo - {self._nome_cantiere()}", lambda p: genera_fascicolo(self.repo, p))

    def _notifica(self) -> None:
        self._genera(f"Notifica preliminare - {self._nome_cantiere()}", lambda p: genera_notifica(self.repo, p))

    def _pos(self) -> None:
        impresa = self.impresa_pos.currentData()
        if impresa is None:
            QMessageBox.information(self, "POS", "Inserire prima un'impresa.")
            return
        self._genera(f"POS - {self.impresa_pos.currentText()}", lambda p: genera_pos(self.repo, impresa, p))

    def aggiorna(self) -> None:
        self.impresa_pos.clear()
        for i in self.repo.elenco("imprese"):
            if i["tipo"] != "Lavoratore autonomo":
                self.impresa_pos.addItem(i["ragione_sociale"] or f"Impresa {i['id']}", i["id"])
        self.revisioni.ricarica()
        self._controlla()


PAGINE: list[type[Pagina]] = [
    PaginaDatiGenerali,
    PaginaSoggetti,
    PaginaImprese,
    PaginaFasi,
    PaginaInterferenze,
    PaginaCosti,
    PaginaRelazione,
    PaginaFascicolo,
    PaginaDocumenti,
]
