"""Licenza legata al PC: attivazione online, certificato, sola lettura (senza Qt).

Collega i programmi SicurCantiere al modulo comune `sicur_license` e al server delle attivazioni,
che è lo stesso del ponte dell'assistente AI. Il codice di licenza (SC1-...) resta quello che il
cliente ha già: il programma lo manda al server, che attiva questo PC se ci sono posti liberi.

Passaggio per chi ha già il codice: al primo avvio della versione con le attivazioni il PC si attiva
da solo in sottofondo. Se in quel momento non c'è internet il programma continua a funzionare per
GIORNI_ATTESA giorni, con un avviso; poi passa in sola lettura finché l'attivazione non riesce.
Se il server rifiuta l'attivazione (posti esauriti, licenza annullata...) la sola lettura è
immediata e il motivo è quello indicato dal server.
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from sicur_license import custodia
from sicur_license.cliente import (
    ALTRO_PC,
    CODICE_ERRATO,
    LICENZA_REVOCATA,
    LICENZA_SCADUTA,
    PC_LIBERATO,
    POSTI_ESAURITI,
    TROPPI_TRASFERIMENTI,
    ErroreRete,
    ErroreServer,
    Licenze,
    trasporto_http,
)
from sicur_license.stato import ATTIVA, Esito
from sicurcantiere import __data__, __version__, ai, licenza

GIORNI_ATTESA = 14  # con il codice ma senza attivazione (nessuna connessione): poi sola lettura
NON_INCLUSO_SERVER = "non_incluso"
DISATTIVATO = "disattivato"  # licenza disattivata da questo PC («Disattiva questo PC»)
# rifiuti del server che non aspettano: il programma passa subito in sola lettura (anche il PC liberato
# o disattivato, altrimenti un posto si potrebbe spostare avanti e indietro sfruttando l'attesa)
RIFIUTI_DEFINITIVI = {POSTI_ESAURITI, TROPPI_TRASFERIMENTI, CODICE_ERRATO, LICENZA_REVOCATA, LICENZA_SCADUTA,
                      NON_INCLUSO_SERVER, PC_LIBERATO, ALTRO_PC, DISATTIVATO}
COSA_FARE = {
    POSTI_ESAURITI: "I PC attivi sono in «Aiuto > Licenza...». Intanto puoi aprire e stampare i documenti già "
                    "creati.",
    TROPPI_TRASFERIMENTI: "Contatta l'assistenza di SicurCantiere. Intanto puoi aprire e stampare i documenti già "
                          "creati.",
    PC_LIBERATO: "Per usarla di nuovo qui, attivala da «Aiuto > Licenza...» (se i posti sono occupati potrai "
                 "liberarne uno). Intanto puoi aprire e stampare i documenti già creati.",
    DISATTIVATO: "Per usarla di nuovo qui, attivala da «Aiuto > Licenza...». Intanto puoi aprire e stampare i "
                 "documenti già creati.",
}

# Trasporto verso il server (sostituibile nei test); None = HTTP verso url_server()
trasporto = None


def url_server() -> str:
    return (os.environ.get("SICUR_LICENSE_SERVER") or ai.server_ai() or "").rstrip("/")


def attive() -> bool:
    """Attivazioni in uso: controllo delle licenze attivo e indirizzo del server noto."""
    return licenza.controllo_attivo() and bool(url_server() or trasporto)


def gestore(programma: str) -> Licenze:
    return Licenze(programma, base64.b64decode(licenza.chiave_pubblica()),
                   trasporto or trasporto_http(url_server()), versione=__version__,
                   data_versione=date.fromisoformat(__data__))


# --- memoria dell'ultimo tentativo (per il messaggio e il periodo di attesa) ---

def _memoria() -> dict:
    return custodia.leggi_memoria()


def _aggiorna_memoria(**valori) -> None:
    memoria = _memoria()
    for chiave, valore in valori.items():
        if valore is None:
            memoria.pop(chiave, None)
        else:
            memoria[chiave] = valore
    custodia.salva_memoria(memoria)


def ultimo_rifiuto() -> dict | None:
    """{codice, messaggio, pc...} dell'ultimo rifiuto definitivo del server, finché non si attiva."""
    valore = _memoria().get("rifiuto")
    return valore if isinstance(valore, dict) else None


def registra_rifiuto(errore: ErroreServer) -> None:
    if errore.codice in RIFIUTI_DEFINITIVI:
        _aggiorna_memoria(rifiuto={"codice": errore.codice, "messaggio": str(errore)})


def attesa_dal(codice: str) -> date:
    """Primo giorno in cui il programma ha il codice ma non l'attivazione (inizio del periodo di attesa)."""
    memoria = _memoria()
    attesa = memoria.get("attesa") or {}
    if attesa.get("codice") != codice:
        attesa = {"codice": codice, "dal": date.today().isoformat()}
        _aggiorna_memoria(attesa=attesa)
    try:
        return date.fromisoformat(attesa["dal"])
    except (KeyError, ValueError):
        return date.today()


# --- azioni ---

def attiva(programma: str, codice: str):
    """Attiva questo PC con il codice. ErroreServer (posti esauriti con l'elenco dei PC...) o ErroreRete."""
    try:
        certificato = gestore(programma).attiva(codice)
    except ErroreServer as e:
        registra_rifiuto(e)
        raise
    _aggiorna_memoria(rifiuto=None, attesa=None)
    return certificato


def verifica_in_sottofondo(programma: str, codice: str) -> str:
    """All'avvio: rinnova il certificato, o attiva il PC se ha il codice ma non l'attivazione.

    Restituisce "" se è andata bene, altrimenti il messaggio (o "rete" senza connessione).
    """
    l = gestore(programma)
    try:
        certificato, _ = l.certificato()
        if certificato is not None:
            l.convalida()
        elif codice and ultimo_rifiuto() is None:
            # prima attivazione automatica (chi aveva già il codice); dopo un rifiuto o «Disattiva questo PC»
            # si riattiva solo a mano, da «Aiuto > Licenza...»
            attiva(programma, codice)
        else:
            return ""
    except ErroreRete:
        return "rete"
    except ErroreServer as e:
        registra_rifiuto(e)
        return str(e)
    _aggiorna_memoria(rifiuto=None)
    return ""


def importa_offline(programma: str, testo: str):
    certificato = gestore(programma).importa_offline(testo)
    _aggiorna_memoria(rifiuto=None, attesa=None)
    return certificato


def disattiva(programma: str) -> None:
    gestore(programma).disattiva()
    _aggiorna_memoria(rifiuto={"codice": DISATTIVATO, "messaggio": "La licenza è stata disattivata su questo PC."})


# --- stato combinato con il codice di licenza ---

@dataclass
class Situazione:
    """Cosa dice l'attivazione: tutto bene, sola lettura (con il motivo) o avvisi da mostrare."""
    sola_lettura: bool = False
    motivo: str = ""
    cosa_fare: str = ""
    avvisi: list[str] = field(default_factory=list)
    esito: Esito | None = None


def situazione(programma: str, codice: str, ora: datetime | None = None) -> Situazione:
    """Stato dell'attivazione per un programma con un codice di licenza valido."""
    ora = ora or datetime.now(timezone.utc)
    esito = gestore(programma).esito(ora)
    if esito.tipo == ATTIVA:
        return Situazione(avvisi=list(esito.avvisi), esito=esito)
    if not esito.serve_attivazione:
        return Situazione(True, esito.motivo, esito.cosa_fare, esito=esito)
    rifiuto = ultimo_rifiuto()
    if rifiuto:
        return Situazione(True, rifiuto.get("messaggio") or esito.motivo,
                          COSA_FARE.get(rifiuto.get("codice"), esito.cosa_fare), esito=esito)
    if esito.certificato is not None:  # certificato di un altro PC (copiato): niente attesa
        return Situazione(True, esito.motivo, esito.cosa_fare, esito=esito)
    giorni = GIORNI_ATTESA - (ora.astimezone().date() - attesa_dal(codice)).days
    if giorni > 0:
        quando = "entro oggi" if giorni == 1 else f"entro {giorni} giorni"
        return Situazione(avvisi=[f"Attivazione della licenza su questo PC da completare: collegati a internet "
                                  f"{quando} e riapri il programma, altrimenti passerà in sola lettura."], esito=esito)
    return Situazione(True, "La licenza non è ancora attivata su questo PC.",
                      "Collegati a internet e apri «Aiuto > Licenza...» per attivarla. Intanto puoi aprire e "
                      "stampare i documenti già creati.", esito=esito)

