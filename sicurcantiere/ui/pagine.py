"""Pagine della finestra principale."""

from __future__ import annotations

from collections import Counter
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
    QFrame,
    QGridLayout,
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
from sicurcantiere.archivio import ATTREZZATURE, TIPOLOGIE, per_categoria
from sicurcantiere.archivio_utente import LAVORAZIONE, ArchivioAnagrafiche
from sicurcantiere.documenti.comune import euro
from sicurcantiere.documenti.fascicolo import genera_fascicolo
from sicurcantiere.documenti.maestranze import genera_schede_lavoratori, genera_tesserini
from sicurcantiere.documenti.moduli import genera_consegna_dpi
from sicurcantiere.documenti.sostanze import genera_elenco_sostanze
from sicurcantiere.documenti.notifica import genera_notifica
from sicurcantiere.documenti.pos import SEZIONI_POS, chiave_testo, genera_pos
from sicurcantiere.documenti.psc import genera_psc
from sicurcantiere.relazione import SEZIONI
from sicurcantiere.repository import Repository
from sicurcantiere.ui import archivio_anagrafiche, tema
from sicurcantiere.ui.icone import icona
from sicurcantiere.ui.lavoro_ai import esegui_ai, registra_pulsante_ai
from sicurcantiere.ui.maestranze import PannelloLavoratori
from sicurcantiere.ui.modulo import ModuloRecord
from sicurcantiere.ui.struttura import StrutturaFase
from sicurcantiere.ui.gantt import ZOOM, ZOOM_PREDEFINITO, Gantt, colore_livello
from sicurcantiere.ui.riepilogo import Riepilogo
from sicurcantiere.ui.riepilogo import calcola as calcola_riepilogo
from sicurcantiere.ui.tabella import Colonna, TabellaCrud

RUOLI = anagrafiche.RUOLI_SOGGETTI
TIPI_IMPRESA = anagrafiche.TIPI_IMPRESA
TIPI_ATTREZZATURA = ["Macchina", "Attrezzo", "Opera provvisionale"]


def _titolo(testo: str) -> QLabel:
    etichetta = QLabel(testo)
    etichetta.setObjectName("pageTitle")
    etichetta.setWordWrap(True)
    return etichetta


def primario(pulsante: QPushButton) -> QPushButton:
    """Pulsante principale della pagina, nel colore del programma."""
    return tema.imposta_variante(pulsante, "primary")


def pulsante_ai(testo: str) -> QPushButton:
    """Pulsante che chiede qualcosa all'assistente AI (viola, come gli avvisi dell'assistente)."""
    pulsante = QPushButton(icona("ai", tema.correnti()["ai"]), testo)
    tema.imposta_variante(pulsante, "ai")
    registra_pulsante_ai(pulsante)  # nascosto finché l'assistente è spento
    return pulsante


def _riquadro(titolo: str, widget: QWidget) -> QGroupBox:
    g = QGroupBox(titolo)
    QVBoxLayout(g).addWidget(widget)
    return g


AVVISO_RESPONSABILITA = ("Il documento va riletto, completato dove serve e firmato da chi ne risponde "
                         "(datore di lavoro per il POS, coordinatore per il PSC): il programma è uno strumento "
                         "di redazione e non sostituisce la valutazione dei rischi.")


def contesto_cantiere(repo: Repository) -> str:
    """Riepilogo del progetto da passare all'assistente AI.

    Senza dati personali: niente nomi di soggetti, imprese o lavoratori, niente indirizzo
    preciso; solo ruoli, tipologie, lavorazioni e il comune (vedi DialogoImpostazioniAI).
    """
    c = repo.cantiere()
    imprese = {i["id"]: i["tipo"] or "impresa" for i in repo.elenco("imprese")}
    righe = [
        f"Natura dell'opera: {c['natura_opera']}",
        f"Comune: {c['comune']} {c['provincia']}".strip(),
        f"Importo lavori: {c['importo_lavori']:.0f} euro",
        f"Descrizione: {c['descrizione']}",
        "Soggetti presenti: " + "; ".join(sorted({s["ruolo"] for s in anagrafiche.soggetti(repo)})),
        "Imprese: " + "; ".join(imprese.values()),
        "Fasi di lavoro:",
    ]
    for f in repo.elenco("fasi"):
        righe.append(f"- {f['codice']} {f['descrizione']}, {imprese.get(f['impresa_id'], 'impresa da definire')}, "
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
                bozza = pulsante_ai("Bozza con l'assistente AI")
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


class Pagina(QWidget):
    titolo = ""
    voce = ""  # nome breve nella barra di navigazione
    icona = "cantiere"  # nome in ui/icone.py
    sottotitolo = ""  # una riga sotto il titolo
    # Sezioni dei controlli che riguardano la pagina: il loro numero compare nella barra
    # laterale; "*" raccoglie quelle che nessuna pagina dichiara.
    sezioni_controlli: tuple[str, ...] = ()

    def __init__(self, repo: Repository):
        super().__init__()
        self.repo = repo
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(24, 16, 24, 14)
        self.layout_.setSpacing(12)
        intestazione = QVBoxLayout()
        intestazione.setSpacing(2)
        intestazione.addWidget(_titolo(self.titolo))
        self.etichetta_sottotitolo = QLabel(self.sottotitolo)
        self.etichetta_sottotitolo.setObjectName("pageSubtitle")
        self.etichetta_sottotitolo.setWordWrap(True)
        self.etichetta_sottotitolo.setVisible(bool(self.sottotitolo))
        intestazione.addWidget(self.etichetta_sottotitolo)
        self.layout_.addLayout(intestazione)

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
    sezioni_controlli = ("Cantiere", "Dati generali")
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
        self.campi: dict[str, QLineEdit] = {}
        etichette = dict(self.CAMPI)
        for campo in etichette:
            e = QLineEdit()
            e.editingFinished.connect(lambda c=campo, w=e: self.repo.aggiorna_cantiere(**{c: w.text()}))
            self.campi[campo] = e
        self.campi["provincia"].setMaxLength(2)
        self.importo = self._numero(" €", "importo_lavori")
        self.costo_ug = self._numero(" €", "costo_uomo_giorno")
        self.costo_ug.setToolTip("Costo medio di un uomo-giorno, usato per stimare la durata delle fasi.")
        self.descrizione = QPlainTextEdit()
        self.descrizione.setPlaceholderText("Descrizione sintetica dell'opera")
        self._timer = QTimer(self, singleShot=True, interval=700)
        self._timer.timeout.connect(self._salva_descrizione)
        self.descrizione.textChanged.connect(self._timer.start)

        # Griglia a quattro colonne: (riga, colonna, ampiezza) di ogni campo.
        griglia = QGridLayout()
        griglia.setHorizontalSpacing(14)
        griglia.setVerticalSpacing(10)
        for campo, (r, c, ampiezza) in {"nome": (0, 0, 4), "natura_opera": (1, 0, 2),
                                        "titolo_abilitativo": (1, 2, 2), "indirizzo": (2, 0, 1),
                                        "cap": (2, 1, 1), "comune": (2, 2, 1), "provincia": (2, 3, 1)}.items():
            griglia.addLayout(tema.campo_con_etichetta(etichette[campo], self.campi[campo]), r, c, 1, ampiezza)
        griglia.addLayout(tema.campo_con_etichetta("Importo presunto dei lavori", self.importo), 3, 0, 1, 2)
        griglia.addLayout(tema.campo_con_etichetta("Costo medio uomo-giorno", self.costo_ug), 3, 2, 1, 2)
        griglia.addLayout(tema.campo_con_etichetta("Descrizione sintetica", self.descrizione), 4, 0, 1, 4)
        for c, peso in enumerate((3, 1, 3, 1)):
            griglia.setColumnStretch(c, peso)
        griglia.setRowStretch(4, 1)
        self.riquadro_dati = tema.cornice("Dati dell'opera", griglia)
        self.corpo = QHBoxLayout()
        self.corpo.setSpacing(12)
        self.corpo.addWidget(self.riquadro_dati, 2)
        self.layout_.addLayout(self.corpo, 1)


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
    sezioni_controlli = ("Committente", "Soggetti")

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
        self.tabella.imposta_titolo("Soggetti")
        self.tabella.aggiungi_pulsante("Dall'archivio...", self._dall_archivio)
        self.tabella.aggiungi_pulsante("Salva in archivio", lambda: archivio_anagrafiche.salva_persona(
            self, self.repo, "soggetti", self.tabella.id_selezionato()))
        self.layout_.addWidget(self.tabella)

    def _dall_archivio(self) -> None:
        if (nuovo := archivio_anagrafiche.prendi_persona(self, self.repo, "soggetti")) is not None:
            self.tabella.ricarica()
            self.tabella.seleziona(nuovo)

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
    sezioni_controlli = ("Impresa", "Imprese", "Figure della sicurezza", "Lavoratori", "Testi del POS")
    # Schede di dettaglio mostrate dal programma: dati, figure, lavoratori, autonomi, pos.
    schede_visibili: tuple[str, ...] = ("dati", "figure", "lavoratori", "autonomi", "pos")

    CAMPI_DATI = [
        (None, "Anagrafica"),
        ("forma_giuridica", "Forma giuridica", "scelta", anagrafiche.FORME_GIURIDICHE),
        ("codice_fiscale", "Codice fiscale"),
        ("cciaa", "Registro imprese / CCIAA (n. REA)"),
        ("ateco", "Codice ATECO / categoria ISTAT"),
        ("logo", "Logo dell'impresa (frontespizio del POS)", "immagine"),
        (None, "Dati dei lavori"),
        ("affidataria_id", "Impresa affidataria di riferimento", "impresa"),
        ("aut_subappalto", "Autorizzazione al subappalto (estremi)"),
        ("tipologia_lavori", "Tipologia dei lavori affidati"),
        ("importo_lavori", "Importo dei lavori da eseguire", "numero"),
        ("data_inizio", "Inizio dei lavori dell'impresa", "data"),
        ("data_fine", "Fine dei lavori dell'impresa", "data"),
        ("orario_lavoro", "Orario di lavoro in cantiere"),
        (None, "Soggetto incaricato dall'impresa affidataria (art. 97)"),
        ("incaricato_97", "Nominativo"),
        ("incaricato_97_mansione", "Mansione"),
        (None, "Sede legale e recapiti"),
        ("indirizzo", "Indirizzo"),
        ("cap", "CAP"),
        ("comune", "Comune"),
        ("provincia", "Provincia"),
        ("fax", "Fax"),
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
        self.tabella.imposta_titolo("Imprese")
        self.tabella.aggiungi_pulsante("Dall'archivio...", self._impresa_dall_archivio)
        self.tabella.aggiungi_pulsante("Salva in archivio", lambda: archivio_anagrafiche.salva_impresa(
            self, self.repo, self.tabella.id_selezionato()))

        self.dati = ModuloRecord(repo, "imprese", self.CAMPI_DATI)
        self.dati.campi["provincia"].setMaxLength(2)
        scorrimento_dati = QScrollArea()
        scorrimento_dati.setWidgetResizable(True)
        scorrimento_dati.setWidget(self.dati)

        # Datore di lavoro e figure della sicurezza (Allegato XV 3.2.1 lett. a e b).
        self.figure = ModuloRecord(repo, "imprese", [
            ("datore_lavoro", "Datore di lavoro"),
            ("rspp_datore", "Il datore di lavoro svolge direttamente i compiti di RSPP (art. 34)", "spunta"),
            ("ruoli_datore", "Il datore di lavoro svolge anche il ruolo di", "spunte", anagrafiche.RUOLI_DATORE),
            ("figure_non_presenti", "Figure non presenti in questa impresa", "spunte",
             list(anagrafiche.FIGURE_FACOLTATIVE)),
            ("figure_motivazione", "Motivazione (se vuota si usa una frase standard)", "testo_lungo"),
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
        self.elenco_figure.aggiungi_pulsante("Dall'archivio...", self._figura_dall_archivio)
        self.elenco_figure.aggiungi_pulsante("Salva in archivio", lambda: archivio_anagrafiche.salva_persona(
            self, self.repo, "figure", self.elenco_figure.id_selezionato()))
        self.figure.campi["figure_motivazione"].setFixedHeight(46)
        contenuto_figure = QWidget()
        lf = QVBoxLayout(contenuto_figure)
        lf.addWidget(self.figure)
        aiuto = QLabel("Una riga per persona e per ruolo: RSPP, medico competente, RLS o RLST, preposti, "
                       "direttore tecnico, capocantiere, addetti al primo soccorso e antincendio. Se una persona "
                       "ha più ruoli (per esempio capocantiere e addetto al primo soccorso) basta una riga per "
                       "ciascun ruolo con lo stesso nome; i ruoli svolti dal datore di lavoro si spuntano sopra.")
        aiuto.setObjectName("pageSubtitle")
        aiuto.setWordWrap(True)
        lf.addWidget(aiuto)
        self.elenco_figure.setMinimumHeight(260)
        lf.addWidget(self.elenco_figure, 1)
        # con la finestra bassa la scheda scorre invece di schiacciare caselle e tabella
        pannello_figure = QScrollArea()
        pannello_figure.setWidgetResizable(True)
        pannello_figure.setFrameShape(QFrame.Shape.NoFrame)
        pannello_figure.setWidget(contenuto_figure)

        self.lavoratori = PannelloLavoratori(repo)
        self.autonomi = PannelloLavoratori(repo, autonomi=True)
        self.testi_pos = TestiLiberi(repo, SEZIONI_POS, altezza=80, contesto_ai=self._contesto_ai)
        scorrimento = QScrollArea()
        scorrimento.setWidgetResizable(True)
        scorrimento.setWidget(self.testi_pos)

        self.schede = QTabWidget()
        for chiave, widget, titolo in (("dati", scorrimento_dati, "Dati dell'impresa"),
                                       ("figure", pannello_figure, "Figure della sicurezza"),
                                       ("lavoratori", self.lavoratori, "Maestranze"),
                                       ("autonomi", self.autonomi, "Lavoratori autonomi"),
                                       ("pos", scorrimento, "Testi del POS")):
            if chiave in self.schede_visibili:
                self.schede.addTab(widget, titolo)
        self.schede.setEnabled(False)
        self.schede.setVisible(bool(self.schede_visibili))
        # Le schede non mostrate restano figlie della pagina: senza un genitore
        # Qt le distruggerebbe mentre la pagina le usa ancora.
        for w in (scorrimento_dati, pannello_figure, self.lavoratori, self.autonomi, scorrimento):
            if w.parent() is None:
                w.setParent(self)
                w.hide()

        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(self.tabella)
        divisore.addWidget(self.schede)
        divisore.setSizes([220, 480])
        self.layout_.addWidget(divisore)
        self.tabella.selezione_cambiata.connect(self._impresa_selezionata)

    def _impresa_dall_archivio(self) -> None:
        if (nuova := archivio_anagrafiche.prendi_impresa(self, self.repo)) is not None:
            self.tabella.ricarica()
            self.tabella.seleziona(nuova)

    def _figura_dall_archivio(self) -> None:
        impresa = self.tabella.id_selezionato()
        if impresa is not None and archivio_anagrafiche.prendi_persona(
                self, self.repo, "figure", impresa_id=impresa) is not None:
            self.elenco_figure.ricarica()

    def _contesto_ai(self) -> str:
        id_ = self.tabella.id_selezionato()
        impresa = self.repo.leggi("imprese", id_) if id_ is not None else None
        if impresa is None:
            return contesto_cantiere(self.repo)
        fasi = self.repo.elenco("fasi", impresa_id=id_)
        lavoratori = self.repo.elenco("lavoratori", impresa_id=id_)
        mansioni = Counter(l["mansione"] or "mansione non indicata" for l in lavoratori)
        righe = [
            f"Impresa che redige il POS: {impresa['tipo'] or 'impresa esecutrice'}",
            f"Orario di lavoro: {impresa['orario_lavoro'] or 'non indicato'}",
            f"Tipologia dei lavori: {impresa['tipologia_lavori'] or 'non indicata'}",
            "Lavorazioni dell'impresa: " + "; ".join(f"{f['codice']} {f['descrizione']}" for f in fasi),
            f"Lavoratori: {len(lavoratori)} (" + ", ".join(f"{n} {m}" for m, n in mansioni.items()) + ")",
        ]
        return contesto_cantiere(self.repo) + "\n\n" + "\n".join(righe)

    def _impresa_selezionata(self, id_: int | None) -> None:
        self.schede.setEnabled(id_ is not None)
        self.dati.carica(id_)
        self.figure.carica(id_)
        self.elenco_figure.imposta_filtro(impresa_id=id_ if id_ is not None else -1)
        self.lavoratori.imposta_impresa(id_)
        self.autonomi.imposta_impresa(id_)
        self.testi_pos.carica(lambda s, i=id_ if id_ is not None else -1: chiave_testo(i, s))

    def salva_in_sospeso(self) -> None:
        self.dati.salva_in_sospeso()
        self.figure.salva_in_sospeso()
        self.lavoratori.salva_in_sospeso()
        self.autonomi.salva_in_sospeso()
        self.testi_pos.salva_in_sospeso()

    def aggiorna(self) -> None:
        self.tabella.ricarica()
        self.tabella.seleziona_prima()


def _valida_fase(fase: dict) -> str | None:
    inizio, fine = analisi.data(fase.get("data_inizio")), analisi.data(fase.get("data_fine"))
    if inizio and fine and fine < inizio:
        return "La data di fine non può precedere la data di inizio."
    return None


class DialogoArchivio(QDialog):
    """Archivio delle lavorazioni per tipologia di intervento e categoria, più quelle dell'utente."""

    TUTTE = "Tutte le tipologie"

    def __init__(self, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.setWindowTitle("Importa lavorazioni dall'archivio")
        self.resize(700, 600)
        self.tipologia = QComboBox()
        self.tipologia.addItems([self.TUTTE] + TIPOLOGIE)
        self.tipologia.currentIndexChanged.connect(self._popola)
        self.filtro = QLineEdit()
        self.filtro.setPlaceholderText("Cerca una lavorazione...")
        self.filtro.textChanged.connect(self._filtra)
        self.albero = QTreeWidget()
        self.albero.setHeaderLabels(["Lavorazione", "Macchine e attrezzi"])
        self.albero.setColumnWidth(0, 380)
        self._spuntate: set[str] = set()
        self.albero.itemChanged.connect(self._ricorda)
        elimina = QPushButton("Elimina dalle lavorazioni utente")
        elimina.clicked.connect(self._elimina_utente)
        pulsanti = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        riga = QHBoxLayout()
        riga.addWidget(QLabel("Tipologia:"))
        riga.addWidget(self.tipologia, 1)
        basso = QHBoxLayout()
        basso.addWidget(elimina)
        basso.addStretch()
        basso.addWidget(pulsanti)
        layout = QVBoxLayout(self)
        layout.addLayout(riga)
        layout.addWidget(QLabel("Selezionare le lavorazioni da aggiungere al cantiere:"))
        layout.addWidget(self.filtro)
        layout.addWidget(self.albero)
        layout.addLayout(basso)
        self._popola()

    @staticmethod
    def _chiave(dati: dict) -> str:
        return ("utente:" + str(dati["id"])) if "dati" in dati else ("base:" + dati["codice"])

    def _popola(self) -> None:
        self.albero.blockSignals(True)
        self.albero.clear()
        tipologia = self.tipologia.currentText()
        for categoria, lavorazioni in per_categoria(None if tipologia == self.TUTTE else tipologia).items():
            nodo = QTreeWidgetItem(self.albero, [categoria])
            gruppi: dict[str, QTreeWidgetItem] = {}
            for lav in lavorazioni:
                padre = nodo
                if lav["gruppo"]:
                    if lav["gruppo"] not in gruppi:
                        gruppi[lav["gruppo"]] = QTreeWidgetItem(nodo, [lav["gruppo"]])
                    padre = gruppi[lav["gruppo"]]
                self._foglia(padre, f"{lav['codice']}  {lav['descrizione']}", ", ".join(lav["attrezzature"]), lav)
        archivio = ArchivioAnagrafiche()
        try:
            utente = archivio.elenco(LAVORAZIONE)
        finally:
            archivio.chiudi()
        nodo = QTreeWidgetItem(self.albero, ["UTENTE - lavorazioni personalizzate"])
        font = nodo.font(0)
        font.setBold(True)
        nodo.setFont(0, font)
        if not utente:
            vuoto = QTreeWidgetItem(nodo, ["(nessuna: in «Lavorazioni» usare «Salva nell'archivio utente»)"])
            vuoto.setDisabled(True)
        for voce in utente:
            self._foglia(nodo, voce["nome"], ", ".join(a["nome"] for a in voce["dati"].get("attrezzature", [])), voce)
        self.albero.expandAll()
        self.albero.blockSignals(False)
        self._filtra(self.filtro.text())

    def _foglia(self, nodo: QTreeWidgetItem, testo: str, attrezzi: str, dati: dict) -> None:
        item = QTreeWidgetItem(nodo, [testo, attrezzi])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(0, Qt.CheckState.Checked if self._chiave(dati) in self._spuntate
                           else Qt.CheckState.Unchecked)
        item.setData(0, Qt.ItemDataRole.UserRole, dati)

    def _ricorda(self, item: QTreeWidgetItem, _colonna: int) -> None:
        dati = item.data(0, Qt.ItemDataRole.UserRole)
        if dati:
            chiave = self._chiave(dati)
            if item.checkState(0) == Qt.CheckState.Checked:
                self._spuntate.add(chiave)
            else:
                self._spuntate.discard(chiave)

    def _foglie(self, nodo: QTreeWidgetItem | None = None):
        """Coppie (nodo padre, lavorazione) a qualsiasi livello dell'albero."""
        figli = ([self.albero.topLevelItem(i) for i in range(self.albero.topLevelItemCount())] if nodo is None
                 else [nodo.child(j) for j in range(nodo.childCount())])
        for figlio in figli:
            if figlio.data(0, Qt.ItemDataRole.UserRole):
                yield nodo, figlio
            else:
                yield from self._foglie(figlio)

    def _filtra(self, testo: str) -> None:
        testo = testo.lower().strip()

        def filtra(item: QTreeWidgetItem) -> bool:
            if item.data(0, Qt.ItemDataRole.UserRole):
                mostra = not testo or testo in item.text(0).lower() or testo in item.text(1).lower()
            else:
                risultati = [filtra(item.child(j)) for j in range(item.childCount())]
                mostra = not testo or any(risultati) or testo in item.text(0).lower()
            item.setHidden(not mostra)
            return mostra

        for i in range(self.albero.topLevelItemCount()):
            filtra(self.albero.topLevelItem(i))

    def _elimina_utente(self) -> None:
        item = self.albero.currentItem()
        dati = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        if not dati or "dati" not in dati:
            QMessageBox.information(self, "Archivio", "Selezionare una lavorazione del nodo UTENTE.")
            return
        if QMessageBox.question(self, "Archivio", f"Eliminare «{dati['nome']}» dalle lavorazioni utente?") \
                == QMessageBox.StandardButton.Yes:
            archivio = ArchivioAnagrafiche()
            try:
                archivio.elimina(dati["id"])
            finally:
                archivio.chiudi()
            self._spuntate.discard(self._chiave(dati))
            self._popola()

    def selezionate(self) -> list[dict]:
        return [item.data(0, Qt.ItemDataRole.UserRole) for _, item in self._foglie()
                if item.checkState(0) == Qt.CheckState.Checked]


class PaginaFasi(Pagina):
    titolo = "Fasi di lavoro e cronoprogramma (Gantt analitico)"
    voce = "Fasi e cronoprogramma"
    icona = "fasi"
    sezioni_controlli = ("Fasi", "Lavorazioni", "Rischi")
    # Nel PSC importi, squadre, date e Gantt delle fasi; nel POS non servono.
    cronoprogramma = True

    def __init__(self, repo: Repository):
        super().__init__(repo)
        self.fasi = TabellaCrud(repo, "fasi", [
            Colonna("codice", "Codice", larghezza=60),
            Colonna("lavorazione", "Lavorazione (gruppo di fasi)", "scelta", scelta_libera=True, larghezza=210,
                    scelte=lambda: [(g, g) for g in sorted({f["lavorazione"] for f in self.repo.elenco("fasi")
                                                             if f["lavorazione"]})],
                    suggerimento="La lavorazione più ampia di cui la fase fa parte, per esempio «Strutture in "
                                 "elevazione in c.a.»: raggruppa più fasi sotto un unico titolo nel POS. "
                                 "Facoltativa: per una fase isolata si può lasciare vuota."),
            Colonna("descrizione", "Fase di lavoro (attività svolta)", larghezza=280,
                    suggerimento="L'attività concreta, con i suoi rischi, macchine e lavoratori, per esempio "
                                 "«Getto del calcestruzzo di pilastri e travi con autopompa»."),
            Colonna("impresa_id", "Impresa", "scelta", scelte=self._imprese, larghezza=170),
        ] + ([
            Colonna("zona", "Zona", larghezza=90),
            Colonna("importo", "Importo €", "decimale", larghezza=100),
            Colonna("incidenza_manodopera", "Manodopera %", "decimale", massimo=100, larghezza=115),
            Colonna("lavoratori", "Squadra", "intero", minimo=0, massimo=999, larghezza=65),
            Colonna("data_inizio", "Inizio", "data", larghezza=95),
            Colonna("data_fine", "Fine", "data", larghezza=95),
            Colonna("uomini_giorno", "Uomini-giorno", "calcolata",
                    calcola=lambda f: str(analisi.uomini_giorno([f]) or "")),
        ] if self.cronoprogramma else []), valida=_valida_fase)
        self.fasi.imposta_titolo("Fasi di lavoro")
        archivio = primario(QPushButton("Importa da archivio..."))
        archivio.clicked.connect(self._importa)
        self.fasi.pulsanti.insertWidget(2, archivio)
        if self.cronoprogramma:
            calcola = QPushButton("Calcola durata")
            calcola.setToolTip("Data di fine da importo, incidenza della manodopera, squadra e costo uomo-giorno.")
            calcola.clicked.connect(self._calcola_durata)
            self.fasi.pulsanti.insertWidget(3, calcola)
        self.fasi.aggiungi_pulsante("Salva nell'archivio utente", self._salva_in_archivio)

        self.rischi = TabellaCrud(repo, "rischi", [
            Colonna("descrizione", "Rischio", "testo_lungo", larghezza=220),
            Colonna("fonte", "Origine", larghezza=130),
            Colonna("probabilita", "P", "intero", minimo=1, massimo=4, larghezza=40),
            Colonna("danno", "D", "intero", minimo=1, massimo=4, larghezza=40),
            Colonna("livello", "Livello P×D", "calcolata", larghezza=130, disegno=tema.DelegatoLivello,
                    calcola=lambda r: "" if r["non_presente"]
                    else str(analisi.livello_rischio(r["probabilita"], r["danno"]))),
            Colonna("misure", "Misure di prevenzione e protezione", "testo_lungo"),
            Colonna("dpi", "DPI", "testo_lungo", larghezza=200),
            Colonna("valutazione_id", "Valutazione specifica", "scelta", scelte=self._valutazioni, larghezza=200),
            Colonna("non_presente", "Non presente", "spunta", larghezza=95, suggerimento=(
                "Spuntare se il rischio, valutato, non è presente nella fase (per esempio macchina "
                "silenziata o lavorazione che non lo comporta): resta fuori da valutazioni specifiche, "
                "segnaletica e DPI, e nel POS compare con la motivazione.")),
            Colonna("motivazione", "Motivazione (se non presente)", "testo_lungo", larghezza=180),
        ])
        self.rischi.modificata.connect(self._aggiorna_gantt)
        suggerisci = pulsante_ai("Suggerisci rischi con l'AI")
        suggerisci.clicked.connect(self._suggerisci_rischi)
        self.rischi.pulsanti.insertWidget(2, suggerisci)

        self.attrezzature = TabellaCrud(repo, "attrezzature", [
            Colonna("tipo", "Tipo", "scelta", scelte=lambda: [(t, t) for t in TIPI_ATTREZZATURA],
                    larghezza=160),
            Colonna("nome", "Nome", "scelta", scelta_libera=True, larghezza=200,
                    scelte=lambda: [(n, n) for n in sorted(ATTREZZATURE)]),
            Colonna("descrizione", "Descrizione", "testo_lungo"),
            Colonna("misure", "Misure prima, durante e dopo l'uso", "testo_lungo"),
            Colonna("dpi", "DPI dell'operatore", "testo_lungo"),
        ])
        self.scelta_archivio = QComboBox()
        self.scelta_archivio.addItems(sorted(ATTREZZATURE))
        aggiungi_archivio = QPushButton("Aggiungi con i suoi rischi")
        aggiungi_archivio.clicked.connect(self._aggiungi_attrezzatura)
        self.attrezzature.pulsanti.insertWidget(2, QLabel("  Dall'archivio:"))
        self.attrezzature.pulsanti.insertWidget(3, self.scelta_archivio)
        self.attrezzature.pulsanti.insertWidget(4, aggiungi_archivio)
        self.attrezzature.modificata.connect(self._rischi_delle_attrezzature)
        suggerisci_attrezzature = pulsante_ai("Suggerisci con l'AI")
        suggerisci_attrezzature.setToolTip("Macchine, attrezzi e opere provvisionali per la fase, con scheda d'uso "
                                           "e rischi, compresi rumore, vibrazioni e movimentazione dei carichi.")
        suggerisci_attrezzature.clicked.connect(self._suggerisci_attrezzature)
        completa_attrezzatura = pulsante_ai("Completa rischi e scheda con l'AI")
        completa_attrezzatura.setToolTip("Per l'attrezzatura selezionata: descrizione, misure prima, durante e "
                                         "dopo l'uso, DPI e rischi mancanti.")
        completa_attrezzatura.clicked.connect(self._completa_attrezzatura)
        for b in (suggerisci_attrezzature, completa_attrezzatura):
            self.attrezzature.pulsanti.insertWidget(self.attrezzature.pulsanti.count() - 1, b)

        self.descrizione_fase = ModuloRecord(repo, "fasi", [
            ("dettaglio", "Descrizione dell'attività", "testo_lungo"),
            ("addetto", "Lavoratori impegnati (addetto)"),
            ("modalita", "Modalità organizzative", "testo_lungo"),
            ("turni", "Turni di lavoro", "testo_lungo"),
            ("procedure_psc", "Procedure complementari richieste dal PSC", "testo_lungo"),
        ])
        scorrimento_descrizione = QScrollArea()
        scorrimento_descrizione.setWidgetResizable(True)
        scorrimento_descrizione.setWidget(self.descrizione_fase)
        self.struttura = StrutturaFase(repo)

        self.dettaglio = QTabWidget()
        self.dettaglio.addTab(scorrimento_descrizione, "Descrizione e organizzazione")
        self.dettaglio.addTab(self.struttura, "Struttura")
        self.dettaglio.addTab(self.rischi, "Rischi e misure")
        self.dettaglio.addTab(self.attrezzature, "Macchine, attrezzi e opere provvisionali")
        self.dettaglio.setEnabled(False)
        self.dettaglio.currentChanged.connect(lambda _i: self._aggiorna_struttura())

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
        aiuto.setObjectName("pageSubtitle")
        barra_gantt.addWidget(aiuto)
        riquadro_gantt = QWidget()
        lay_gantt = QVBoxLayout(riquadro_gantt)
        lay_gantt.setContentsMargins(0, 0, 0, 0)
        lay_gantt.addLayout(barra_gantt)
        lay_gantt.addWidget(scorrimento)

        divisore = QSplitter(Qt.Orientation.Vertical)
        divisore.addWidget(self.fasi)
        if self.cronoprogramma:
            divisore.addWidget(riquadro_gantt)
        else:
            # Il cronoprogramma resta figlio della pagina (nascosto) per non essere distrutto.
            riquadro_gantt.setParent(self)
            riquadro_gantt.hide()
        divisore.addWidget(self.dettaglio)
        divisore.setSizes([200, 400, 220] if self.cronoprogramma else [300, 450])
        self.layout_.addWidget(divisore)

        self.fasi.selezione_cambiata.connect(self._fase_selezionata)
        self.fasi.modificata.connect(self._aggiorna_gantt)

    def _imprese(self) -> list[tuple[int | None, str]]:
        return [(None, "(da definire)")] + [
            (i["id"], i["ragione_sociale"] or f"Impresa {i['id']}") for i in self.repo.elenco("imprese")
        ]

    def _valutazioni(self) -> list[tuple[int | None, str]]:
        from sicurcantiere.valutazioni import METODI

        return [(None, "—")] + [
            (v["id"], v["titolo"] or (METODI[v["metodo"]].nome if v["metodo"] in METODI else v["metodo"]))
            for v in self.repo.elenco("valutazioni")
        ]

    def _fase_selezionata(self, id_: int | None) -> None:
        self.dettaglio.setEnabled(id_ is not None)
        filtro = id_ if id_ is not None else -1
        self.descrizione_fase.carica(id_)
        self.rischi.imposta_filtro(fase_id=filtro)
        self.attrezzature.imposta_filtro(fase_id=filtro)
        fase = self.repo.leggi("fasi", id_) if id_ is not None else None
        nome = f"{fase['codice']} {fase['descrizione']}".strip() if fase else ""
        self.rischi.imposta_titolo(nome)
        self.attrezzature.imposta_titolo(nome)
        self._aggiorna_struttura()

    def _aggiorna_struttura(self) -> None:
        if self.dettaglio.currentWidget() is self.struttura:
            self.struttura.mostra(self.fasi.id_selezionato())

    def salva_in_sospeso(self) -> None:
        self.descrizione_fase.salva_in_sospeso()

    def _aggiorna_gantt(self) -> None:
        imprese = {i["id"]: i["ragione_sociale"] or f"Impresa {i['id']}" for i in self.repo.elenco("imprese")}
        self.gantt.imposta_fasi(self.fasi.righe(), analisi.livelli_fasi(self.repo.rischi()), imprese)

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
            if "dati" in lav:  # lavorazione dell'archivio utente
                ultima = ArchivioAnagrafiche.inserisci_lavorazione(self.repo, lav)
            else:
                ultima = self.repo.importa_lavorazione(lav)
        self.fasi.ricarica()
        if ultima is not None:
            self.fasi.seleziona(ultima)
        self._aggiorna_gantt()

    def _salva_in_archivio(self) -> None:
        fase = self.fasi.id_selezionato()
        if fase is None:
            QMessageBox.information(self, "Archivio", "Selezionare prima la lavorazione da salvare.")
            return
        archivio = ArchivioAnagrafiche()
        try:
            archivio.salva_lavorazione(self.repo, fase)
        except ValueError as e:
            QMessageBox.warning(self, "Archivio", str(e))
            return
        finally:
            archivio.chiudi()
        QMessageBox.information(self, "Archivio", "Lavorazione salvata nel nodo UTENTE dell'archivio, con "
                                                  "macchine, attrezzi e rischi: si ritrova in «Importa da archivio».")

    def _aggiungi_attrezzatura(self) -> None:
        fase = self.fasi.id_selezionato()
        if fase is None:
            return
        self.repo.aggiungi_attrezzatura(fase, self.scelta_archivio.currentText())
        self.attrezzature.ricarica()
        self.rischi.ricarica()
        self._aggiorna_gantt()

    def _rischi_delle_attrezzature(self) -> None:
        """Una macchina o un attrezzo scritto a mano porta nella fase i suoi rischi specifici."""
        from sicurcantiere.valutazioni.automatiche import completa_rischi_attrezzature

        if completa_rischi_attrezzature(self.repo):
            self.rischi.ricarica()

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
        esistenti = [f"{r['descrizione']} ({r['fonte']})" if r["fonte"] else r["descrizione"]
                     for r in self.repo.elenco("rischi", fase_id=fase_id)]
        esegui_ai(self, "L'assistente sta analizzando la lavorazione...",
                  lambda ai: ai.suggerisci_rischi(lavorazione, attrezzature, esistenti),
                  lambda proposte: self._scegli_rischi(fase_id, proposte))

    @staticmethod
    def _testo_rischio(r: dict) -> str:
        livello = analisi.livello_rischio(r["probabilita"], r["danno"])
        origine = f" ({r['fonte']})" if r.get("fonte") else ""
        return (f"{r['descrizione']}{origine}  -  P{r['probabilita']} x D{r['danno']} = {livello} "
                f"{analisi.classe_rischio(livello)}\n    Misure: {r['misure']}")

    def _scegli_proposte(self, titolo: str, nota: str, testi: list[str]) -> list[int] | None:
        """Elenco a spunta delle proposte dell'assistente; restituisce gli indici scelti."""
        dialogo = QDialog(self)
        dialogo.setWindowTitle(titolo)
        dialogo.resize(760, 460)
        elenco = QListWidget()
        for testo in testi:
            item = QListWidgetItem(testo)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            elenco.addItem(item)
        etichetta = QLabel(nota)
        etichetta.setWordWrap(True)
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.accepted.connect(dialogo.accept)
        pulsanti.rejected.connect(dialogo.reject)
        layout = QVBoxLayout(dialogo)
        layout.addWidget(etichetta)
        layout.addWidget(elenco)
        layout.addWidget(pulsanti)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return None
        return [i for i in range(elenco.count()) if elenco.item(i).checkState() == Qt.CheckState.Checked]

    def _dopo_aggiunte(self) -> None:
        self._rischi_delle_attrezzature()
        self.attrezzature.ricarica()
        self.rischi.ricarica()
        self._aggiorna_gantt()

    def _scegli_rischi(self, fase_id: int, proposte: list[dict]) -> None:
        if not proposte:
            QMessageBox.information(self, "Assistente AI", "Nessun rischio aggiuntivo individuato.")
            return
        scelti = self._scegli_proposte(
            "Rischi suggeriti dall'assistente AI",
            "Selezionare i rischi da aggiungere alla fase. Valori e misure restano modificabili.",
            [self._testo_rischio(r) for r in proposte])
        if scelti is None or not self.repo.leggi("fasi", fase_id):
            return
        for i in scelti:
            self.repo.inserisci("rischi", fase_id=fase_id, **proposte[i])
        self._dopo_aggiunte()

    def _suggerisci_attrezzature(self) -> None:
        fase_id = self.fasi.id_selezionato()
        if fase_id is None:
            QMessageBox.information(self, "Assistente AI", "Selezionare una fase.")
            return
        fase = self.repo.leggi("fasi", fase_id)
        lavorazione = " - ".join(x for x in (fase["lavorazione"], f"{fase['codice']} {fase['descrizione']}".strip())
                                 if x)
        if not fase["descrizione"].strip():
            QMessageBox.information(self, "Assistente AI", "Indicare prima la descrizione della fase.")
            return
        esistenti = [a["nome"] for a in self.repo.elenco("attrezzature", fase_id=fase_id)]
        esegui_ai(self, "L'assistente sta individuando macchine e attrezzature...",
                  lambda ai: ai.suggerisci_attrezzature(lavorazione, fase["dettaglio"], esistenti,
                                                        sorted(ATTREZZATURE)),
                  lambda proposte: self._scegli_attrezzature(fase_id, proposte))

    def _scegli_attrezzature(self, fase_id: int, proposte: list[dict]) -> None:
        if not proposte:
            QMessageBox.information(self, "Assistente AI", "Nessuna attrezzatura aggiuntiva individuata.")
            return
        testi = []
        for a in proposte:
            if a["nome"] in ATTREZZATURE:
                rischi = [r["descrizione"] for r in ATTREZZATURE[a["nome"]]["rischi"]]
                origine = "scheda dell'archivio"
            else:
                rischi = [r["descrizione"] for r in a["rischi"]]
                origine = "proposta dall'assistente"
            testi.append(f"{a['nome']} ({a['tipo'].lower()}, {origine})\n    Rischi: {', '.join(rischi) or '-'}")
        scelti = self._scegli_proposte(
            "Macchine e attrezzature suggerite dall'assistente AI",
            "Selezionare le attrezzature da aggiungere alla fase con la loro scheda d'uso e i loro rischi. "
            "Per quelle presenti nell'archivio si usa la scheda dell'archivio.", testi)
        if scelti is None or not self.repo.leggi("fasi", fase_id):
            return
        for i in scelti:
            self.repo.aggiungi_attrezzatura_proposta(fase_id, proposte[i])
        self._dopo_aggiunte()

    def _completa_attrezzatura(self) -> None:
        id_ = self.attrezzature.id_selezionato()
        if id_ is None:
            QMessageBox.information(self, "Assistente AI", "Selezionare una macchina o un attrezzo.")
            return
        a = self.repo.leggi("attrezzature", id_)
        if not a["nome"].strip():
            QMessageBox.information(self, "Assistente AI", "Indicare prima il nome dell'attrezzatura.")
            return
        fase = self.repo.leggi("fasi", a["fase_id"])
        esistenti = [r["descrizione"] for r in self.repo.elenco("rischi", fase_id=a["fase_id"])
                     if r["fonte"] == a["nome"]]
        esegui_ai(self, "L'assistente sta compilando la scheda dell'attrezzatura...",
                  lambda ai: ai.completa_attrezzatura(a["nome"], a["tipo"], fase["descrizione"], esistenti),
                  lambda proposta: self._applica_attrezzatura(id_, proposta))

    def _applica_attrezzatura(self, id_: int, proposta: dict) -> None:
        from sicurcantiere.archivio_attrezzature import testo_misure

        a = self.repo.leggi("attrezzature", id_)
        if a is None:
            return
        rischi = [{**r, "fonte": a["nome"]} for r in proposta["rischi"]]
        scheda = []
        if not a["descrizione"].strip() and proposta["descrizione"]:
            scheda.append("Descrizione")
        if not a["misure"].strip() and any(proposta[k] for k in ("prima", "durante", "dopo")):
            scheda.append("Misure prima, durante e dopo l'uso")
        if not a["dpi"].strip() and proposta["dpi"]:
            scheda.append("DPI dell'operatore")
        testi = [f"Scheda d'uso: {', '.join(scheda)}"] if scheda else []
        testi += [self._testo_rischio(r) for r in rischi]
        if not testi:
            QMessageBox.information(self, "Assistente AI", "Scheda già completa e nessun rischio aggiuntivo.")
            return
        scelti = self._scegli_proposte(
            f"{a['nome']}: proposte dell'assistente AI",
            "Selezionare cosa aggiungere. I campi della scheda già compilati non vengono toccati.", testi)
        if scelti is None or not self.repo.leggi("attrezzature", id_):
            return
        if scheda and 0 in scelti:
            modifiche = {}
            if "Descrizione" in scheda:
                modifiche["descrizione"] = proposta["descrizione"]
            if "DPI dell'operatore" in scheda:
                modifiche["dpi"] = "; ".join(d.strip() for d in proposta["dpi"].split(",") if d.strip())
            if "Misure prima, durante e dopo l'uso" in scheda:
                modifiche["misure"] = testo_misure(proposta)
            self.repo.aggiorna("attrezzature", id_, **modifiche)
        primo = 1 if scheda else 0
        for i in scelti:
            if i >= primo:
                self.repo.inserisci("rischi", fase_id=a["fase_id"], **rischi[i - primo])
        self._dopo_aggiunte()

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
        self.fasi.seleziona_prima()
        self._aggiorna_gantt()


class PaginaInterferenze(Pagina):
    titolo = "Interferenze e prescrizioni di coordinamento"
    voce = "Interferenze"
    icona = "interferenze"
    sezioni_controlli = ("Interferenze",)
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
        elenco = analisi.interferenze(fasi, analisi.livelli_fasi(self.repo.rischi()))
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
    sezioni_controlli = ("Costi",)

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
        self.tabella.imposta_titolo("Costi della sicurezza")
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
        self.interventi.imposta_titolo("Interventi di manutenzione")
        self.elaborati = TabellaCrud(repo, "elaborati", [
            Colonna("titolo", "Elaborato tecnico", larghezza=320),
            Colonna("autore", "Autore", larghezza=200),
            Colonna("data", "Data", "data", larghezza=100),
            Colonna("collocazione", "Collocazione"),
        ])
        self.elaborati.imposta_titolo("Elaborati tecnici")
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

    PER_IMPRESA = ("pos", "dpi", "sostanze", "tesserini", "schede")
    NOMI = {
        "psc": "Piano di Sicurezza e Coordinamento (PSC)",
        "fascicolo": "Fascicolo dell'opera",
        "notifica": "Notifica preliminare",
        "pos": "Piano Operativo di Sicurezza (POS)",
        "dpi": "Verbali di consegna dei DPI",
        "sostanze": "Elenco delle sostanze pericolose",
        "tesserini": "Tesserini di riconoscimento dei lavoratori",
        "schede": "Schede dei lavoratori (mansioni, rischi, DPI, formazione)",
    }

    def __init__(self, repo: Repository):
        super().__init__(repo)
        griglia = QGroupBox("Genera documento (.docx)")
        layout = QVBoxLayout(griglia)
        self.impresa = QComboBox()
        per_impresa = [d for d in self.documenti if d in self.PER_IMPRESA]
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
        avviso = QLabel(AVVISO_RESPONSABILITA)
        avviso.setObjectName("hint")
        avviso.setWordWrap(True)
        layout.addWidget(avviso)

        self.controlli = QListWidget()
        self.controlli.setSpacing(2)
        self.controlli.itemDoubleClicked.connect(self._vai_al_controllo)
        self.controlli.itemActivated.connect(self._vai_al_controllo)
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
        self.revisioni.imposta_titolo("Revisioni del documento")

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
        c = tema.correnti()
        for s in elenco:
            errore = s.livello == controlli.ERRORE
            item = QListWidgetItem(icona("errore" if errore else "avviso", c["err"] if errore else c["warn"]),
                                   f"{s.livello} · {s.sezione}\n{s.messaggio}")
            item.setForeground(QBrush(QColor(c["err"] if errore else c["tx"])))
            item.setData(Qt.ItemDataRole.UserRole, s.sezione)
            item.setToolTip("Doppio clic per andare alla pagina da correggere")
            self.controlli.addItem(item)
        return elenco

    def _vai_al_controllo(self, item: QListWidgetItem) -> None:
        vai = getattr(self.window(), "vai_a_sezione", None)
        if vai is not None and item.data(Qt.ItemDataRole.UserRole):
            vai(item.data(Qt.ItemDataRole.UserRole))

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
        risposta = QMessageBox.question(
            self, "Documento generato",
            f"Creato {Path(file).name}.\n\n{AVVISO_RESPONSABILITA}\n\nAprirlo ora?")
        if risposta == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(file)))

    def genera(self, chiave: str | None = None) -> None:
        chiave = chiave or self.principale
        cantiere = self.repo.cantiere()["nome"] or "Cantiere"
        if chiave in self.PER_IMPRESA:
            impresa = self.impresa.currentData()
            if impresa is None:
                QMessageBox.information(self, "Documenti", "Inserire prima l'impresa.")
                return
            nome = self.impresa.currentText()
            if chiave == "pos":
                self._salva_docx(f"POS - {nome} - {cantiere}", lambda p: genera_pos(self.repo, impresa, p))
            elif chiave == "tesserini":
                self._salva_docx(f"Tesserini - {nome}", lambda p: genera_tesserini(self.repo, impresa, p))
            elif chiave == "schede":
                self._salva_docx(f"Schede lavoratori - {nome}",
                                 lambda p: genera_schede_lavoratori(self.repo, impresa, p))
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
            if not anagrafiche.autonomo(i):
                self.impresa.addItem(i["ragione_sociale"] or f"Impresa {i['id']}", i["id"])
        self.impresa.setCurrentIndex(max(self.impresa.findData(corrente), 0))
        self.revisioni.ricarica()
        self._controlla()
