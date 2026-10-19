"""Pagine della finestra principale."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import analisi
from sicurcantiere.archivio import LAVORAZIONI
from sicurcantiere.documenti.psc import euro, genera_psc
from sicurcantiere.relazione import SEZIONI
from sicurcantiere.repository import Repository
from sicurcantiere.ui.gantt import Gantt
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


def _titolo(testo: str) -> QLabel:
    etichetta = QLabel(testo)
    font = etichetta.font()
    font.setPointSizeF(font.pointSizeF() * 1.4)
    font.setBold(True)
    etichetta.setFont(font)
    return etichetta


class Pagina(QWidget):
    titolo = ""

    def __init__(self, repo: Repository):
        super().__init__()
        self.repo = repo
        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(_titolo(self.titolo))

    def aggiorna(self) -> None:
        """Ricarica i dati quando la pagina viene mostrata."""


class PaginaDatiGenerali(Pagina):
    titolo = "Dati generali del cantiere"
    CAMPI = [
        ("nome", "Denominazione dell'opera"),
        ("natura_opera", "Natura dell'opera"),
        ("indirizzo", "Indirizzo"),
        ("comune", "Comune"),
        ("provincia", "Provincia"),
    ]

    def __init__(self, repo: Repository):
        super().__init__(repo)
        modulo = QFormLayout()
        self.campi: dict[str, QLineEdit] = {}
        for campo, etichetta in self.CAMPI:
            e = QLineEdit()
            e.editingFinished.connect(lambda c=campo, w=e: self.repo.aggiorna_cantiere(**{c: w.text()}))
            modulo.addRow(etichetta, e)
            self.campi[campo] = e
        self.campi["provincia"].setMaxLength(2)

        self.importo = QDoubleSpinBox()
        self.importo.setRange(0, 1e10)
        self.importo.setDecimals(2)
        self.importo.setGroupSeparatorShown(True)
        self.importo.setSuffix(" €")
        self.importo.editingFinished.connect(
            lambda: self.repo.aggiorna_cantiere(importo_lavori=self.importo.value())
        )
        modulo.addRow("Importo presunto dei lavori", self.importo)

        self.descrizione = QPlainTextEdit()
        self.descrizione.setPlaceholderText("Descrizione sintetica dell'opera")
        self._timer = QTimer(self, singleShot=True, interval=700)
        self._timer.timeout.connect(self._salva_descrizione)
        self.descrizione.textChanged.connect(self._timer.start)
        modulo.addRow("Descrizione", self.descrizione)
        self.layout_.addLayout(modulo)

        riquadro = QGroupBox("Obblighi (D.Lgs. 81/2008)")
        self.obblighi = QLabel()
        self.obblighi.setWordWrap(True)
        QVBoxLayout(riquadro).addWidget(self.obblighi)
        self.layout_.addWidget(riquadro)

    def _salva_descrizione(self) -> None:
        self.repo.aggiorna_cantiere(descrizione=self.descrizione.toPlainText())

    _caricata = False

    def salva_in_sospeso(self) -> None:
        # I campi di testo salvano all'uscita dal campo: alla chiusura della
        # finestra potrebbe non accadere, quindi salviamo tutto qui.
        self._timer.stop()
        if not self._caricata:
            return
        self.repo.aggiorna_cantiere(
            **{campo: e.text() for campo, e in self.campi.items()},
            importo_lavori=self.importo.value(),
            descrizione=self.descrizione.toPlainText(),
        )

    def aggiorna(self) -> None:
        self._caricata = True
        c = self.repo.cantiere()
        for campo, e in self.campi.items():
            e.setText(c[campo])
        self.importo.setValue(c["importo_lavori"])
        self.descrizione.blockSignals(True)
        self.descrizione.setPlainText(c["descrizione"])
        self.descrizione.blockSignals(False)
        o = analisi.obblighi(self.repo.elenco("imprese"), self.repo.elenco("fasi"))
        self.obblighi.setText("\n".join(o.descrizione()))


class PaginaSoggetti(Pagina):
    titolo = "Soggetti con compiti di sicurezza"

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
    titolo = "Imprese e lavoratori autonomi"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.tabella = TabellaCrud(repo, "imprese", [
            Colonna("ragione_sociale", "Ragione sociale", larghezza=240),
            Colonna("tipo", "Tipo", "scelta", scelte=lambda: [(t, t) for t in TIPI_IMPRESA],
                    larghezza=150),
            Colonna("partita_iva", "P. IVA", larghezza=120),
            Colonna("indirizzo", "Indirizzo", larghezza=200),
            Colonna("referente", "Referente", larghezza=150),
            Colonna("telefono", "Telefono"),
        ])
        self.layout_.addWidget(self.tabella)

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
        self.resize(520, 420)
        self.elenco = QListWidget()
        for i, lav in enumerate(LAVORAZIONI):
            item = QListWidgetItem(f"{lav['codice']}  {lav['descrizione']}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.elenco.addItem(item)
        pulsanti = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Selezionare le lavorazioni da aggiungere al cantiere:"))
        layout.addWidget(self.elenco)
        layout.addWidget(pulsanti)

    def selezionate(self) -> list[dict]:
        return [
            LAVORAZIONI[self.elenco.item(r).data(Qt.ItemDataRole.UserRole)]
            for r in range(self.elenco.count())
            if self.elenco.item(r).checkState() == Qt.CheckState.Checked
        ]


class PaginaFasi(Pagina):
    titolo = "Fasi di lavoro, rischi e cronoprogramma"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.fasi = TabellaCrud(repo, "fasi", [
            Colonna("codice", "Codice", larghezza=70),
            Colonna("descrizione", "Lavorazione", larghezza=300),
            Colonna("impresa_id", "Impresa", "scelta", scelte=self._imprese, larghezza=200),
            Colonna("data_inizio", "Inizio", "data", larghezza=100),
            Colonna("data_fine", "Fine", "data", larghezza=100),
            Colonna("lavoratori", "Lavoratori", "intero", minimo=0, massimo=999),
        ], valida=_valida_fase)
        archivio = QPushButton("Importa da archivio...")
        archivio.clicked.connect(self._importa)
        self.fasi.pulsanti.insertWidget(2, archivio)

        self.rischi = TabellaCrud(repo, "rischi", [
            Colonna("descrizione", "Rischio", "testo_lungo"),
            Colonna("probabilita", "P", "intero", minimo=1, massimo=4, larghezza=40),
            Colonna("danno", "D", "intero", minimo=1, massimo=4, larghezza=40),
            Colonna("livello", "Livello", "calcolata", larghezza=110, calcola=lambda r: (
                f"{(l := analisi.livello_rischio(r['probabilita'], r['danno']))} "
                f"{analisi.classe_rischio(l)}")),
            Colonna("misure", "Misure di prevenzione e protezione", "testo_lungo"),
            Colonna("dpi", "DPI", "testo_lungo"),
        ])
        self.rischi.setEnabled(False)

        self.gantt = Gantt()
        scorrimento = QScrollArea()
        scorrimento.setWidget(self.gantt)
        scorrimento.setWidgetResizable(False)

        riquadro_rischi = QGroupBox("Rischi della fase selezionata")
        QVBoxLayout(riquadro_rischi).addWidget(self.rischi)

        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(self.fasi)
        divisore.addWidget(scorrimento)
        divisore.addWidget(riquadro_rischi)
        divisore.setSizes([300, 200, 300])
        self.layout_.addWidget(divisore)

        self.fasi.selezione_cambiata.connect(self._fase_selezionata)
        self.fasi.modificata.connect(self._aggiorna_gantt)

    def _imprese(self) -> list[tuple[int | None, str]]:
        return [(None, "(da definire)")] + [
            (i["id"], i["ragione_sociale"] or f"Impresa {i['id']}") for i in self.repo.elenco("imprese")
        ]

    def _fase_selezionata(self, id_: int | None) -> None:
        self.rischi.setEnabled(id_ is not None)
        self.rischi.imposta_filtro(fase_id=id_ if id_ is not None else -1)

    def _aggiorna_gantt(self) -> None:
        self.gantt.imposta_fasi(self.fasi.righe())

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

    def aggiorna(self) -> None:
        self.fasi.ricarica()
        self._aggiorna_gantt()


class PaginaCosti(Pagina):
    titolo = "Stima dei costi della sicurezza"

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

    def __init__(self, repo: Repository):
        super().__init__(repo)
        contenuto = QWidget()
        layout = QVBoxLayout(contenuto)
        self.editor: dict[str, QPlainTextEdit] = {}
        self._in_sospeso: set[str] = set()
        self._timer = QTimer(self, singleShot=True, interval=700)
        self._timer.timeout.connect(self.salva_in_sospeso)
        for chiave, titolo in SEZIONI:
            riquadro = QGroupBox(titolo)
            editor = QPlainTextEdit()
            editor.setMinimumHeight(120)
            editor.textChanged.connect(lambda k=chiave: self._modificato(k))
            QVBoxLayout(riquadro).addWidget(editor)
            layout.addWidget(riquadro)
            self.editor[chiave] = editor
        scorrimento = QScrollArea()
        scorrimento.setWidgetResizable(True)
        scorrimento.setWidget(contenuto)
        self.layout_.addWidget(scorrimento)

    def _modificato(self, chiave: str) -> None:
        self._in_sospeso.add(chiave)
        self._timer.start()

    def salva_in_sospeso(self) -> None:
        self._timer.stop()
        for chiave in self._in_sospeso:
            self.repo.salva_testo(chiave, self.editor[chiave].toPlainText())
        self._in_sospeso.clear()

    def aggiorna(self) -> None:
        for chiave, editor in self.editor.items():
            editor.blockSignals(True)
            editor.setPlainText(self.repo.testo(chiave))
            editor.blockSignals(False)


class PaginaDocumenti(Pagina):
    titolo = "Documenti"

    def __init__(self, repo: Repository):
        super().__init__(repo)
        pulsante = QPushButton("Genera Piano di Sicurezza e Coordinamento (.docx)...")
        pulsante.clicked.connect(self._genera_psc)
        riga = QHBoxLayout()
        riga.addWidget(pulsante)
        riga.addStretch()
        self.layout_.addLayout(riga)

        riquadro = QGroupBox("Interferenze rilevate dal cronoprogramma")
        self.interferenze = QListWidget()
        QVBoxLayout(riquadro).addWidget(self.interferenze)
        self.layout_.addWidget(riquadro)

    def _genera_psc(self) -> None:
        nome = self.repo.cantiere()["nome"] or "PSC"
        predefinito = self.repo.progetto.percorso.with_name(f"PSC - {nome}.docx")
        percorso, _ = QFileDialog.getSaveFileName(
            self, "Salva PSC", str(predefinito), "Documento Word (*.docx)"
        )
        if not percorso:
            return
        try:
            file = genera_psc(self.repo, percorso)
        except PermissionError:
            QMessageBox.warning(self, "Errore", "Impossibile scrivere il file: è aperto in Word?")
            return
        risposta = QMessageBox.question(self, "PSC generato", f"Creato {Path(file).name}.\nAprirlo ora?")
        if risposta == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(file)))

    def aggiorna(self) -> None:
        self.interferenze.clear()
        elenco = analisi.interferenze(self.repo.elenco("fasi"))
        if not elenco:
            self.interferenze.addItem("Nessuna lavorazione contemporanea di imprese diverse.")
        for i in elenco:
            self.interferenze.addItem(
                f"{i.fase_a['codice']} {i.fase_a['descrizione']}  ↔  "
                f"{i.fase_b['codice']} {i.fase_b['descrizione']}  "
                f"({i.inizio:%d/%m/%Y} - {i.fine:%d/%m/%Y})"
            )


PAGINE: list[type[Pagina]] = [
    PaginaDatiGenerali,
    PaginaSoggetti,
    PaginaImprese,
    PaginaFasi,
    PaginaCosti,
    PaginaRelazione,
    PaginaDocumenti,
]
