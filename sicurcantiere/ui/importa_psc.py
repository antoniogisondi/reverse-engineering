"""«Nuovo POS da un PSC...»: legge il PSC del coordinatore e prepara i file .spo delle imprese scelte."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressDialog,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere import importa_psc
from sicurcantiere.ai import ErroreAI
from sicurcantiere.ui import lavoro_ai


class Annullato(Exception):
    """L'utente ha premuto Annulla durante un lavoro in background."""


class _Segnali(QObject):
    progresso = Signal(int, int, str)
    completato = Signal(object)
    fallito = Signal(str)


class _Lavoro(QRunnable):
    """Esegue `funzione(avanzamento)` in un thread; `avanzamento(n, totale, testo)` aggiorna la barra."""

    def __init__(self, funzione: Callable):
        super().__init__()
        self.funzione = funzione
        self.segnali = _Segnali()
        self.annullato = False

    def _avanzamento(self, n: int, totale: int, testo: str = "") -> None:
        if self.annullato:
            raise Annullato()
        self.segnali.progresso.emit(n, totale, testo)

    def run(self) -> None:
        try:
            risultato = self.funzione(self._avanzamento)
        except Annullato:
            self.segnali.fallito.emit("")
        except (ErroreAI, importa_psc.ErroreImportazione) as e:
            self.segnali.fallito.emit(str(e))
        except Exception as e:  # noqa: BLE001 - qualsiasi errore va mostrato all'utente
            self.segnali.fallito.emit(f"Errore imprevisto: {e}")
        else:
            self.segnali.completato.emit(risultato)


_in_corso: set[_Lavoro] = set()


def in_background(genitore: QWidget, titolo: str, messaggio: str, funzione: Callable,
                  al_termine: Callable[[Any], None]) -> None:
    """Lavoro lungo senza bloccare la finestra: barra di avanzamento e pulsante Annulla."""
    attesa = QProgressDialog(messaggio, "Annulla", 0, 0, genitore)
    attesa.setWindowTitle(titolo)
    attesa.setWindowModality(Qt.WindowModality.WindowModal)
    attesa.setMinimumDuration(0)
    attesa.setMinimumWidth(420)
    attesa.show()
    lavoro = _Lavoro(funzione)
    _in_corso.add(lavoro)

    def progresso(n: int, totale: int, testo: str) -> None:
        attesa.setMaximum(totale)
        attesa.setValue(n)
        if testo:
            attesa.setLabelText(testo)

    def fine() -> None:
        attesa.close()
        _in_corso.discard(lavoro)

    def ok(risultato: Any) -> None:
        fine()
        al_termine(risultato)

    def errore(testo: str) -> None:
        fine()
        if testo:  # vuoto: annullato dall'utente
            QMessageBox.warning(genitore, titolo, testo)

    def annulla() -> None:
        lavoro.annullato = True
        attesa.setLabelText("Annullamento in corso...")

    attesa.canceled.connect(annulla)
    lavoro.segnali.progresso.connect(progresso, Qt.ConnectionType.QueuedConnection)
    lavoro.segnali.completato.connect(ok, Qt.ConnectionType.QueuedConnection)
    lavoro.segnali.fallito.connect(errore, Qt.ConnectionType.QueuedConnection)
    QThreadPool.globalInstance().start(lavoro)


TITOLO = "Nuovo POS da un PSC"


def avvia(finestra) -> None:
    """Sceglie il PSC, lo fa leggere all'assistente (una volta) e crea i file del POS."""
    if not lavoro_ai.ai_attiva():
        QMessageBox.information(
            finestra, TITOLO,
            "Per leggere un PSC fatto con un altro programma serve l'assistente AI. "
            + lavoro_ai.perche_non_disponibile()
            + "\n\nSe il PSC è stato fatto con SicurCantiere PSC l'assistente non serve: basta aprirlo in "
            "SicurCantiere PSC e usare «Prepara il POS dell'impresa...» nella pagina Imprese.")
        return
    percorso, _ = QFileDialog.getOpenFileName(finestra, "Scegli il PSC del coordinatore", "",
                                              "PSC (*.pdf *.docx)")
    if not percorso:
        return

    def leggi_file(avanzamento):
        grezzo = importa_psc.estrai_testo(
            percorso, lambda n, tot: avanzamento(n, tot, f"Lettura del documento: pagina {n} di {tot}..."))
        return importa_psc.pulisci_testo(grezzo)

    in_background(finestra, TITOLO, "Lettura del documento...", leggi_file,
                  lambda testo: _conferma_e_analizza(finestra, percorso, testo))


def _conferma_e_analizza(finestra, percorso: str, testo: str) -> None:
    ai = lavoro_ai.assistente()
    fornitore = f"SicurCantiere AI ({'Avanzato' if ai.modello == 'avanzato' else 'Standard'})"
    token = importa_psc.stima_token(testo)
    n_parti = len(importa_psc.parti(testo))
    if QMessageBox.question(
            finestra, TITOLO,
            f"Il PSC verrà letto dall'assistente {fornitore}, elaborato da {lavoro_ai.SEDI[ai.modello]}, in "
            f"{n_parti} richieste per circa {token * (8 if ai.modello == 'avanzato' else 1):,} crediti AI"
            .replace(",", ".") + (" (motore Avanzato: 8 crediti per token)" if ai.modello == "avanzato" else "")
            + ". La lettura si fa una volta sola e serve per i POS di tutte le imprese del PSC.\n\n"
            "Il PSC contiene nomi e recapiti dei soggetti e delle imprese: verranno inviati al fornitore insieme "
            "al resto del testo.\n\nContinuare?") != QMessageBox.StandardButton.Yes:
        return

    def analizza(avanzamento):
        analisi = ai.analizza_psc(testo, lambda n, tot: avanzamento(
            n - 1, tot, f"Lettura del PSC con l'assistente {fornitore}: parte {n} di {tot}..."))
        analisi.file = percorso
        return analisi

    in_background(finestra, TITOLO, f"Lettura del PSC con l'assistente {fornitore}...", analizza,
                  lambda analisi: _scegli_e_crea(finestra, analisi))


def _scegli_e_crea(finestra, analisi: importa_psc.Analisi) -> None:
    if not analisi.imprese and not analisi.fasi:
        QMessageBox.warning(finestra, TITOLO, "Nel documento non sono state trovate imprese né "
                                                              "lavorazioni: è davvero un PSC?")
        return
    dialogo = DialogoImpresePSC(analisi, finestra)
    if not dialogo.exec():
        return
    scelte = dialogo.scelte()
    if not scelte:
        return
    nome_cantiere = analisi.cantiere.get("nome", "") or Path(analisi.file).stem
    cartella = Path(analisi.file).parent

    def nome_file(impresa: dict) -> str:
        nome = f"POS {nome_cantiere} - {impresa['ragione_sociale']}"
        return "".join(c for c in nome if c not in '<>:"/\\|?*').strip()[:150] + ".spo"

    if len(scelte) == 1:
        destinazione, _ = QFileDialog.getSaveFileName(finestra, "Salva il file del POS",
                                                      str(cartella / nome_file(scelte[0][0])), "Cantiere POS (*.spo)")
        if not destinazione:
            return
        destinazioni = [Path(destinazione).with_suffix(".spo")]
    else:
        scelta = QFileDialog.getExistingDirectory(finestra, "Cartella in cui salvare i file dei POS", str(cartella))
        if not scelta:
            return
        destinazioni = [Path(scelta) / nome_file(i) for i, _ in scelte]
    creati = []
    for (impresa, fasi), destinazione in zip(scelte, destinazioni):
        try:
            creati.append(importa_psc.crea_spo(analisi, impresa, destinazione, fasi))
        except Exception as e:  # noqa: BLE001 - un file non creato non deve fermare gli altri
            QMessageBox.warning(finestra, "Nuovo POS da un PSC", f"{destinazione.name}: non creato ({e}).")
    if not creati:
        return
    elenco = "\n".join(f"• {p.name}" for p in creati)
    if QMessageBox.question(
            finestra, "Nuovo POS da un PSC",
            f"Creati {len(creati)} file:\n{elenco}\n\nContengono cantiere, soggetti, impresa, lavorazioni con rischi "
            "e attrezzature, prescrizioni e interferenze del PSC. Completa i dati mancanti (figure, lavoratori, "
            "testi del POS) e controlla i rischi segnati «verificare» prima di generare il POS.\n\n"
            f"Aprire ora {creati[0].name}?") == QMessageBox.StandardButton.Yes:
        finestra.apri_file(creati[0])


class DialogoImpresePSC(QDialog):
    """Imprese trovate nel PSC: si spuntano quelle di cui preparare il POS e, per ognuna, le sue fasi."""

    def __init__(self, analisi: importa_psc.Analisi, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.analisi = analisi
        self.setWindowTitle("Imprese del PSC")
        self.resize(720, 620)
        c = analisi.cantiere
        intestazione = QLabel(
            f"<b>{c.get('nome') or 'Cantiere'}</b> {('· ' + c['comune']) if c.get('comune') else ''}<br>"
            f"Trovati: {len(analisi.imprese)} imprese, {len(analisi.fasi)} fasi di lavoro, "
            f"{len(analisi.interferenze)} interferenze, {len(analisi.richieste_pos)} richieste ai POS.")
        intestazione.setWordWrap(True)
        self.imprese = QListWidget()
        for i in analisi.imprese:
            n = len(analisi.fasi_impresa(i["ragione_sociale"]))
            voce = QListWidgetItem(f"{i['ragione_sociale']}   —   {i.get('ruolo') or 'ruolo non indicato'}, "
                                   f"{n} fasi assegnate dal PSC")
            voce.setFlags(voce.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            voce.setCheckState(Qt.CheckState.Unchecked)
            self.imprese.addItem(voce)
        self.impresa_fasi = QComboBox()
        self.impresa_fasi.addItems([i["ragione_sociale"] for i in analisi.imprese])
        self.fasi = QListWidget()
        self._fasi_scelte: dict[int, set[int]] = {
            n: {k for k, f in enumerate(analisi.fasi) if importa_psc.stessa_impresa(f["impresa"], i["ragione_sociale"])}
            for n, i in enumerate(analisi.imprese)}
        self.impresa_fasi.currentIndexChanged.connect(self._mostra_fasi)
        self.fasi.itemChanged.connect(self._fase_cambiata)

        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.button(QDialogButtonBox.StandardButton.Ok).setText("Crea i file dei POS")
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(intestazione)
        layout.addWidget(QLabel("Spunta le imprese di cui preparare il POS:"))
        layout.addWidget(self.imprese, 2)
        aiuto = QLabel("Fasi svolte dall'impresa: quelle che il PSC le assegna sono già spuntate; se il PSC non "
                       "assegna le fasi alle imprese, spunta qui quelle che svolge.")
        aiuto.setWordWrap(True)
        layout.addWidget(aiuto)
        layout.addWidget(self.impresa_fasi)
        layout.addWidget(self.fasi, 3)
        layout.addWidget(pulsanti)
        self._mostra_fasi()

    def _mostra_fasi(self) -> None:
        n = self.impresa_fasi.currentIndex()
        self.fasi.blockSignals(True)
        self.fasi.clear()
        for k, f in enumerate(self.analisi.fasi):
            testo = f["descrizione"] + (f"   ({f['impresa']})" if f["impresa"] else "")
            voce = QListWidgetItem(testo)
            voce.setData(Qt.ItemDataRole.UserRole, k)
            voce.setFlags(voce.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            voce.setCheckState(Qt.CheckState.Checked if k in self._fasi_scelte.get(n, set())
                               else Qt.CheckState.Unchecked)
            self.fasi.addItem(voce)
        self.fasi.blockSignals(False)

    def _fase_cambiata(self, voce: QListWidgetItem) -> None:
        scelte = self._fasi_scelte.setdefault(self.impresa_fasi.currentIndex(), set())
        k = voce.data(Qt.ItemDataRole.UserRole)
        if voce.checkState() == Qt.CheckState.Checked:
            scelte.add(k)
        else:
            scelte.discard(k)

    def scelte(self) -> list[tuple[dict, list[dict]]]:
        """(impresa, fasi) per ogni impresa spuntata."""
        return [(i, [self.analisi.fasi[k] for k in sorted(self._fasi_scelte.get(n, set()))])
                for n, i in enumerate(self.analisi.imprese)
                if self.imprese.item(n).checkState() == Qt.CheckState.Checked]
