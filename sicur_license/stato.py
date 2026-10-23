"""Cosa può fare il programma con il certificato che ha: tutto, oppure sola lettura.

In sola lettura si aprono, si stampano e si esportano in PDF i documenti già fatti, ma non se ne
creano di nuovi e non si modificano: i dati dell'utente restano sempre accessibili (il consulente
ha obblighi di legge sui documenti già consegnati). Ogni esito ha il motivo e cosa fare.

Regole:
- certificato assente, alterato o di un altro PC → serve l'attivazione;
- orologio del PC spostato indietro → collegarsi a internet;
- licenza revocata o abbonamento scaduto → sola lettura, rinnovare o contattare l'assistenza;
- licenza perpetua: le versioni uscite dopo la fine degli aggiornamenti inclusi si aprono in sola
  lettura (le precedenti continuano a funzionare);
- certificato non rinnovato da 14 giorni (nessuna connessione) → sola lettura finché non ci si
  collega; tre giorni prima compare un avviso.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from sicur_license import impronta
from sicur_license.certificato import ABBONAMENTO, PERPETUA, PROVA, REVOCATA, Certificato

ATTIVA, DA_ATTIVARE, ALTRO_PC, OROLOGIO, REVOCATA_, SCADUTA, AGGIORNAMENTI, NON_INCLUSO, DA_CONVALIDARE = (
    "attiva", "da_attivare", "altro_pc", "orologio", "revocata", "scaduta", "aggiornamenti", "non_incluso",
    "da_convalidare")

GIORNI_AVVISO = 3             # avviso prima che serva la convalida online
GIORNI_AVVISO_OFFLINE = 14    # avviso prima della fine di un'attivazione offline
GIORNI_AVVISO_SCADENZA = 30   # avviso prima della scadenza della licenza
TOLLERANZA_OROLOGIO = timedelta(hours=24)


@dataclass
class Esito:
    tipo: str
    certificato: Certificato | None = None
    motivo: str = ""        # cosa succede, in una frase
    cosa_fare: str = ""     # cosa può fare l'utente
    avvisi: list[str] = field(default_factory=list)  # con la licenza attiva: promemoria

    @property
    def puo_modificare(self) -> bool:
        return self.tipo == ATTIVA

    @property
    def sola_lettura(self) -> bool:
        return not self.puo_modificare

    @property
    def serve_attivazione(self) -> bool:
        return self.tipo in (DA_ATTIVARE, ALTRO_PC)


def _data(giorno: date) -> str:
    return giorno.strftime("%d/%m/%Y")


def valuta(certificato: Certificato | None, programma: str, impronte_pc: list[str], ora: datetime,
           ultima_ora_vista: datetime | None = None, data_versione: date | None = None,
           errore: str = "") -> Esito:
    """Esito per `programma` («psc», «pos», ...) all'ora `ora` (con fuso orario).

    `data_versione` è la data di pubblicazione della versione in uso; `errore` il motivo per cui il
    certificato salvato non si è potuto leggere (alterato, danneggiato).
    """
    if certificato is None:
        return Esito(DA_ATTIVARE, motivo=errore or "Il programma non è ancora attivato su questo PC.",
                     cosa_fare="Inserisci il codice di licenza per attivarlo. Intanto puoi aprire e stampare i "
                               "documenti già creati.")
    c = certificato
    if not impronta.stesso_pc(list(c.impronte), impronte_pc):
        return Esito(ALTRO_PC, c, "La licenza salvata appartiene a un altro PC.",
                     "Attiva la licenza su questo PC con il tuo codice: se i posti sono tutti occupati potrai "
                     "liberarne uno.")
    riferimento = max(v for v in (ultima_ora_vista, c.emesso) if v is not None)
    if ora < riferimento - TOLLERANZA_OROLOGIO:
        return Esito(OROLOGIO, c, "La data del PC è precedente a quella dell'ultimo utilizzo.",
                     "Controlla data e ora di Windows e collegati a internet: il programma verificherà la licenza "
                     "e tornerà a funzionare.")
    if c.stato == REVOCATA:
        return Esito(REVOCATA_, c, "La licenza è stata disattivata.",
                     "Contatta l'assistenza di SicurCantiere. I documenti già creati restano consultabili.")
    if programma not in c.prodotti:
        return Esito(NON_INCLUSO, c, "Questo programma non è compreso nella tua licenza.",
                     "Puoi aggiungerlo alla licenza contattando SicurCantiere. Intanto puoi aprire e stampare i "
                     "documenti già creati.")
    oggi = ora.astimezone().date()
    if c.scadenza_licenza and oggi > c.scadenza_licenza and c.tipo in (ABBONAMENTO, PROVA):
        if c.tipo == PROVA:
            return Esito(SCADUTA, c, f"La prova gratuita è terminata il {_data(c.scadenza_licenza)}.",
                         "Acquista la licenza per continuare a creare e modificare i documenti. Quelli già creati "
                         "restano consultabili.")
        return Esito(SCADUTA, c, f"La licenza è scaduta il {_data(c.scadenza_licenza)}.",
                     "Rinnova l'abbonamento per continuare a creare e modificare i documenti. Quelli già creati "
                     "restano consultabili, stampabili ed esportabili in PDF.")
    if (c.tipo == PERPETUA and c.aggiornamenti_fino and data_versione
            and data_versione > c.aggiornamenti_fino):
        return Esito(AGGIORNAMENTI, c,
                     f"Questa versione è uscita dopo la fine degli aggiornamenti inclusi nella licenza "
                     f"({_data(c.aggiornamenti_fino)}).",
                     "Rinnova gli aggiornamenti, oppure reinstalla una versione pubblicata entro quella data.")
    if ora > c.valido_fino:
        if c.offline:
            return Esito(DA_CONVALIDARE, c, "L'attivazione offline è terminata.",
                         "Collegati a internet per convalidare la licenza, oppure chiedi un nuovo file di "
                         "attivazione all'assistenza.")
        return Esito(DA_CONVALIDARE, c, "Da molti giorni il programma non riesce a verificare la licenza.",
                     "Collegati a internet e riapri il programma: la verifica è automatica.")
    esito = Esito(ATTIVA, c)
    rimasti = c.valido_fino - ora
    if rimasti <= timedelta(days=GIORNI_AVVISO_OFFLINE if c.offline else GIORNI_AVVISO):
        giorni = max(rimasti.days, 0)
        quando = "entro oggi" if giorni == 0 else "entro domani" if giorni == 1 else f"entro {giorni} giorni"
        esito.avvisi.append(f"Collegati a internet {quando} per la verifica della licenza, altrimenti il programma "
                            "passerà in sola lettura.")
    if c.scadenza_licenza and c.tipo in (ABBONAMENTO, PROVA):
        if (c.scadenza_licenza - oggi).days <= GIORNI_AVVISO_SCADENZA:
            cosa = "La prova gratuita termina" if c.tipo == PROVA else "La licenza scade"
            esito.avvisi.append(f"{cosa} il {_data(c.scadenza_licenza)}.")
    return esito
