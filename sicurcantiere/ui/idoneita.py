"""Scheda «Idoneità e patente» dell'impresa: patente a crediti (art. 27), DURC di congruità e verifica
dell'idoneità tecnico-professionale (Allegato XVII), con l'esito che compare nei controlli e nei documenti."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import anagrafiche
from sicurcantiere.repository import Repository
from sicurcantiere.ui import tema
from sicurcantiere.ui.modulo import ModuloRecord


class PannelloIdoneita(QScrollArea):
    def __init__(self, repo: Repository, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.id_: int | None = None
        self._carico = False
        self._timer = QTimer(self, singleShot=True, interval=500)
        self._timer.timeout.connect(self.salva_in_sospeso)

        self.modulo = ModuloRecord(repo, "imprese", [
            (None, "Patente a crediti (art. 27 del D.Lgs. 81/2008)"),
            ("patente_stato", "Situazione", "scelta", anagrafiche.PATENTE_STATI),
            ("patente_numero", "Numero o codice della patente"),
            ("patente_crediti", "Crediti alla data della verifica", "intero"),
            ("patente_verificata", "Verificata sul portale INL il", "data"),
            (None, "DURC di congruità della manodopera (D.M. 143/2021)"),
            ("durc_congruita", "Situazione", "scelta", anagrafiche.DURC_CONGRUITA),
            ("durc_congruita_data", "Rilasciato il", "data"),
            (None, "Verifica dell'idoneità tecnico-professionale (art. 90, comma 9, e Allegato XVII)"),
            ("idoneita_verificata", "Verifica eseguita il", "data"),
        ])
        self.avviso_patente = QLabel()
        self.avviso_patente.setWordWrap(True)
        self.avviso_patente.setObjectName("hint")

        self.griglia = QGridLayout()
        self.griglia.setColumnStretch(0, 3)
        self.griglia.setColumnStretch(2, 2)
        self.righe: dict[str, tuple[QComboBox, QLineEdit]] = {}
        self.esito = QLabel()
        self.esito.setObjectName("sectionTitle")
        tutti = QPushButton("Segna tutti come acquisiti")
        tutti.setToolTip("Imposta «Acquisito» per i documenti non ancora indicati")
        tutti.clicked.connect(self._tutti_acquisiti)
        riga_esito = QHBoxLayout()
        riga_esito.addWidget(self.esito, 1)
        riga_esito.addWidget(tutti)
        self.verbale = QPushButton("Genera il verbale...")
        self.verbale.setToolTip("Verbale di verifica dell'idoneità tecnico-professionale (Allegato XVII) di questa "
                                "impresa o di questo lavoratore autonomo, in Word")
        self.verbale.clicked.connect(lambda: self.genera_verbale())
        riga_esito.addWidget(self.verbale)
        corpo = QVBoxLayout()
        corpo.addLayout(riga_esito)
        corpo.addLayout(self.griglia)
        nota = QLabel("Il committente o il responsabile dei lavori verifica l'idoneità delle imprese affidatarie, "
                      "esecutrici e dei lavoratori autonomi (art. 90, comma 9); l'impresa affidataria quella delle "
                      "imprese a cui subappalta (art. 97, comma 2). «Genera il verbale...» ne prepara il verbale in Word.")
        nota.setWordWrap(True)
        nota.setObjectName("hint")
        corpo.addWidget(nota)
        self.riquadro_voci = tema.cornice("Documenti richiesti dall'Allegato XVII", corpo)

        contenuto = QWidget()
        layout = QVBoxLayout(contenuto)
        layout.addWidget(self.modulo)
        layout.addWidget(self.avviso_patente)
        layout.addWidget(self.riquadro_voci)
        layout.addStretch()
        self.setWidget(contenuto)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        for campo in ("patente_stato", "patente_crediti"):
            w = self.modulo.campi[campo]
            (w.currentTextChanged if campo == "patente_stato" else w.valueChanged).connect(
                lambda *_: self._aggiorna_avvisi())

    # --- voci dell'Allegato XVII ---

    def _costruisci_righe(self, impresa: dict) -> None:
        while self.griglia.count():
            w = self.griglia.takeAt(0).widget()
            if w is not None:
                w.hide()  # fino all'eliminazione resterebbe visibile nell'angolo del riquadro
                w.deleteLater()
        self.righe.clear()
        for r, (chiave, testo) in enumerate(anagrafiche.voci_idoneita(impresa)):
            etichetta = QLabel(testo, self.riquadro_voci)
            etichetta.setWordWrap(True)
            esito = QComboBox(self.riquadro_voci)
            for voce in anagrafiche.ESITI_IDONEITA:
                esito.addItem(voce or "Da verificare", voce)
            nota = QLineEdit(self.riquadro_voci)
            nota.setPlaceholderText("Estremi, data, scadenza...")
            esito.currentIndexChanged.connect(self._modificato)
            nota.textChanged.connect(self._modificato)
            self.griglia.addWidget(etichetta, r, 0)
            self.griglia.addWidget(esito, r, 1)
            self.griglia.addWidget(nota, r, 2)
            self.righe[chiave] = (esito, nota)

    def _modificato(self, *_args) -> None:
        if not self._carico:
            self._timer.start()
            self._aggiorna_avvisi()

    def _tutti_acquisiti(self) -> None:
        for esito, _ in self.righe.values():
            if not esito.currentData():
                esito.setCurrentIndex(esito.findData("Acquisito"))
        if self.id_ is not None and not self.repo.leggi("imprese", self.id_)["idoneita_verificata"]:
            self.repo.aggiorna("imprese", self.id_, idoneita_verificata=date.today().isoformat())
            self.modulo.carica(self.id_)
        self.salva_in_sospeso()

    def _valori(self) -> str:
        return json.dumps({k: {"esito": e.currentData(), "nota": n.text().strip()} for k, (e, n) in self.righe.items()},
                          ensure_ascii=False)

    def _aggiorna_avvisi(self) -> None:
        if self.id_ is None:
            return
        impresa = dict(self.repo.leggi("imprese", self.id_) or {})
        impresa["patente_stato"] = self.modulo.valore("patente_stato")
        impresa["patente_crediti"] = self.modulo.valore("patente_crediti")
        impresa["idoneita"] = self._valori()
        regolare = anagrafiche.patente_regolare(impresa)
        self.avviso_patente.setText(
            "Indica la situazione della patente: dal 1° ottobre 2024 le imprese e i lavoratori autonomi che operano "
            "nei cantieri devono esserne in possesso, salvo le esenzioni previste (art. 27)." if regolare is None else
            f"Attenzione: con meno di {anagrafiche.CREDITI_MINIMI} crediti, o senza patente, l'impresa non può operare "
            "nel cantiere." if regolare is False else "Patente a crediti regolare.")
        c = tema.correnti()
        esito = anagrafiche.esito_idoneita(impresa)
        colore = c["ok"] if esito == "Idonea" else c["err"] if esito == "Documentazione incompleta" else c["tx2"]
        self.esito.setText(f"Esito della verifica: {esito}")
        self.esito.setStyleSheet(f"color: {colore};")

    def genera_verbale(self, destinazione: str | None = None) -> Path | None:
        """Verbale di verifica dell'idoneità dell'impresa (o del lavoratore autonomo) mostrata."""
        if self.id_ is None:
            return None
        self.salva_in_sospeso()
        from sicurcantiere.documenti.idoneita import genera_verifica_idoneita

        if not destinazione:
            impresa = self.repo.leggi("imprese", self.id_) or {}
            nome = (impresa.get("ragione_sociale") or "impresa").replace("/", "-")
            proposta = self.repo.progetto.percorso.with_name(f"Verifica idoneità - {nome}.docx")
            destinazione, _ = QFileDialog.getSaveFileName(self, "Salva il verbale", str(proposta),
                                                          "Documento Word (*.docx)")
            if not destinazione:
                return None
        try:
            file = genera_verifica_idoneita(self.repo, self.id_, destinazione)
        except PermissionError:
            QMessageBox.warning(self, "Salvataggio non riuscito",
                                "Impossibile scrivere il file. Se è aperto in Word, chiudilo e riprova.")
            return None
        if QApplication.platformName() != "offscreen":
            from sicurcantiere.ui.anteprima import documento_creato
            from sicurcantiere.ui.pagine import AVVISO_RESPONSABILITA

            documento_creato(self, file, avviso=AVVISO_RESPONSABILITA)
        return Path(file)

    # --- caricamento e salvataggio ---

    def imposta_impresa(self, id_: int | None) -> None:
        self.salva_in_sospeso()
        self.id_ = id_
        self.modulo.carica(id_)
        impresa = self.repo.leggi("imprese", id_) if id_ is not None else None
        self._carico = True
        self._costruisci_righe(impresa or {})
        self.verbale.setEnabled(impresa is not None)
        if impresa is not None:
            for chiave, valori in anagrafiche.leggi_idoneita(impresa).items():
                esito, nota = self.righe[chiave]
                esito.setCurrentIndex(max(esito.findData(valori["esito"]), 0))
                nota.setText(valori["nota"])
        self._carico = False
        self._aggiorna_avvisi()

    def salva_in_sospeso(self) -> None:
        self._timer.stop()
        self.modulo.salva_in_sospeso()
        if self.id_ is None or not self.righe:
            return
        valori = self._valori()
        attuale = self.repo.leggi("imprese", self.id_)
        if attuale is not None and attuale["idoneita"] != valori:
            self.repo.aggiorna("imprese", self.id_, idoneita=valori)
