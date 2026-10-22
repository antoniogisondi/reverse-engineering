"""Pagina dei ponteggi e del PiMUS."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import pimus
from sicurcantiere.documenti.pimus import genera_pimus
from sicurcantiere.repository import Repository
from sicurcantiere.ui.pagine import ModuloRecord, Pagina, TestiLiberi, contesto_cantiere, primario
from sicurcantiere.ui.tabella import Colonna, TabellaCrud


class PaginaPonteggi(Pagina):
    titolo = "Ponteggi e PiMUS"
    voce = "Ponteggi e PiMUS"
    icona = "ponteggi"
    sezioni_controlli = ("Ponteggi", "*")

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.id_: int | None = None
        self.tabella = TabellaCrud(repo, "ponteggi", [
            Colonna("nome", "Ponteggio / ubicazione", larghezza=220),
            Colonna("impresa_id", "Impresa che monta", "scelta", larghezza=190, scelte=self._imprese),
            Colonna("tipo", "Tipologia", "scelta", larghezza=200,
                    scelte=lambda: [(t, t) for t in pimus.TIPI_PONTEGGIO]),
            Colonna("altezza", "Altezza (m)", "decimale", larghezza=90, massimo=200),
            Colonna("lunghezza", "Sviluppo (m)", "decimale", larghezza=95, massimo=2000),
            Colonna("conforme_schemi", "Secondo schemi tipo", "scelta",
                    scelte=lambda: [(1, "Sì"), (0, "No (serve il progetto)")]),
        ], valori_nuovo=lambda: {"nome": "Ponteggio di facciata"})
        self.tabella.imposta_titolo("Ponteggi")
        genera = primario(QPushButton("Genera il PiMUS in Word..."))
        genera.clicked.connect(self._genera)
        self.tabella.pulsanti.insertWidget(2, genera)
        self.tabella.selezione_cambiata.connect(self._seleziona)
        self.tabella.modificata.connect(self._aggiorna_avvisi)

        self.avvisi = QLabel()
        self.avvisi.setWordWrap(True)
        self.avvisi.setStyleSheet("color: #D93B30;")

        self.dati = ModuloRecord(repo, "ponteggi", [
            ("fabbricante", "Fabbricante"),
            ("modello", "Modello"),
            ("autorizzazione", "Autorizzazione ministeriale (n. e data)"),
            ("classe_carico", "Classe / sovraccarico ammesso"),
            ("ancoraggi", "Ancoraggi (tipo e maglia)"),
            ("piano_appoggio", "Piano di appoggio"),
            ("progettista", "Progettista (se è richiesto il progetto)"),
            ("preposto", "Preposto al montaggio"),
            ("squadra", "Addetti al montaggio"),
            ("sollevamento", "Attrezzature di sollevamento"),
            ("dpi", "DPI specifici"),
        ])
        for campo in self.dati.campi.values():
            campo.editingFinished.connect(self._aggiorna_avvisi)

        self.testi = TestiLiberi(repo, [(k, t) for k, t, _ in pimus.SEZIONI], altezza=90,
                                 contesto_ai=self._contesto_ai)
        testi_base = QPushButton("Inserisci i testi base nelle sezioni vuote")
        testi_base.clicked.connect(self._testi_base)
        contenitore_testi = QWidget()
        lt = QVBoxLayout(contenitore_testi)
        lt.addWidget(testi_base, alignment=Qt.AlignmentFlag.AlignLeft)
        lt.addWidget(self.testi)
        scorrimento = QScrollArea()
        scorrimento.setWidgetResizable(True)
        scorrimento.setWidget(contenitore_testi)

        self.verifiche = TabellaCrud(repo, "verifiche_ponteggio", [
            Colonna("momento", "Momento", "scelta", larghezza=170,
                    scelte=lambda: [(m, m) for m in ("Prima del montaggio", "Durante l'uso")]),
            Colonna("voce", "Verifica", "testo_lungo"),
            Colonna("esito", "Esito", "scelta", larghezza=140, scelte=lambda: [(e, e or "Da eseguire") for e in pimus.ESITI]),
            Colonna("note", "Note", larghezza=200),
        ])
        self.verifiche.imposta_titolo("Verifiche")
        carica = QPushButton("Carica l'elenco delle verifiche")
        carica.clicked.connect(self._carica_verifiche)
        self.verifiche.pulsanti.insertWidget(2, carica)

        self.schede = QTabWidget()
        self.schede.addTab(self.dati, "Dati del ponteggio")
        self.schede.addTab(scorrimento, "Testi del PiMUS")
        self.schede.addTab(self.verifiche, "Verifiche (Allegato XIX)")
        self.schede.setEnabled(False)

        basso = QWidget()
        lb = QVBoxLayout(basso)
        lb.setContentsMargins(0, 0, 0, 0)
        lb.addWidget(self.avvisi)
        lb.addWidget(self.schede)
        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(self.tabella)
        divisore.addWidget(basso)
        divisore.setSizes([200, 600])
        self.layout_.addWidget(divisore)

    def _imprese(self):
        return [(None, "(da definire)")] + [
            (i["id"], i["ragione_sociale"] or f"Impresa {i['id']}") for i in self.repo.elenco("imprese")
        ]

    def _seleziona(self, id_: int | None) -> None:
        self.testi.salva_in_sospeso()
        self.id_ = id_
        self.schede.setEnabled(id_ is not None)
        self.dati.carica(id_)
        filtro = id_ if id_ is not None else -1
        self.testi.carica(lambda s, i=filtro: pimus.chiave_testo(i, s))
        self.verifiche.imposta_filtro(ponteggio_id=filtro)
        self._aggiorna_avvisi()

    def _aggiorna_avvisi(self) -> None:
        p = self.repo.leggi("ponteggi", self.id_) if self.id_ is not None else None
        messaggi = pimus.avvisi(p) if p else []
        self.avvisi.setText("\n".join(f"⚠ {m}" for m in messaggi))
        self.avvisi.setVisible(bool(messaggi))

    def _contesto_ai(self) -> str:
        p = self.repo.leggi("ponteggi", self.id_) if self.id_ is not None else {}
        # Senza nominativi (progettista, preposto, squadra): all'assistente non vanno dati personali.
        esclusi = ("id", "impresa_id", "progettista", "preposto", "squadra")
        ponteggio = "\n".join(f"{k}: {v}" for k, v in (p or {}).items() if k not in esclusi and v)
        return f"{contesto_cantiere(self.repo)}\n\nPonteggio oggetto del PiMUS:\n{ponteggio}"

    def _testi_base(self) -> None:
        for chiave, _, testo in pimus.SEZIONI:
            if not self.testi.editor[chiave].toPlainText().strip():
                self.testi.imposta_testo(chiave, testo)

    def _carica_verifiche(self) -> None:
        if self.id_ is None:
            return
        esistenti = {v["voce"] for v in self.repo.elenco("verifiche_ponteggio", ponteggio_id=self.id_)}
        for momento, voce in pimus.VERIFICHE:
            if voce not in esistenti:
                self.repo.inserisci("verifiche_ponteggio", ponteggio_id=self.id_, momento=momento, voce=voce)
        self.verifiche.ricarica()

    def _genera(self) -> None:
        if self.id_ is None:
            QMessageBox.information(self, "PiMUS", "Seleziona prima un ponteggio.")
            return
        self.salva_in_sospeso()
        p = self.repo.leggi("ponteggi", self.id_)
        predefinito = self.repo.progetto.percorso.with_name(f"PiMUS - {p['nome'] or 'ponteggio'}.docx")
        percorso, _ = QFileDialog.getSaveFileName(self, "Salva il PiMUS", str(predefinito), "Documento Word (*.docx)")
        if not percorso:
            return
        try:
            file = genera_pimus(self.repo, self.id_, percorso)
        except PermissionError:
            QMessageBox.warning(self, "Errore", "Impossibile salvare il file: verifica che non sia aperto in Word.")
            return
        if QMessageBox.question(self, "PiMUS generato", f"PiMUS creato: {Path(file).name}.\n\nVuoi aprirlo ora?") \
                == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(file)))

    def genera_principale(self) -> None:
        self._genera()

    def salva_in_sospeso(self) -> None:
        self.dati.salva_in_sospeso()
        self.testi.salva_in_sospeso()

    def aggiorna(self) -> None:
        self.tabella.ricarica()
