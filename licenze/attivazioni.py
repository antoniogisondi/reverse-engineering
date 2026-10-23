"""Server delle attivazioni: limite di PC per licenza, certificati firmati, trasferimenti e registro.

Fa parte del server pubblico (licenze.wsgi_api, insieme al ponte dell'assistente AI): è la sola
parte raggiungibile da internet, il gestionale resta nella rete dell'ufficio. Legge e scrive lo
stesso database del gestionale: le licenze emesse lì valgono subito qui.

Regole:
- una licenza copre N PC («postazioni» della licenza, più gli eventuali posti aggiunti): il PC in
  più rispetto a N viene rifiutato con l'elenco dei PC attivi, e il rifiuto finisce nel registro;
- riattivare lo stesso PC (stessa impronta, almeno 2 componenti su 3) non consuma un posto;
- liberare un PC è sempre possibile (dal PC stesso o da un altro, per il trasferimento); quello che
  ha un limite sono le attivazioni di PC nuovi: in 30 giorni al massimo N + 2 (i primi N più due
  trasferimenti), così un posto non si può far «girare» tra più PC; oltre serve l'assistenza;
- i rinnovi fanno parte della stessa catena di licenza: i PC attivati restano validi;
- limiti di richieste per indirizzo e per licenza, contro chi prova a indovinare i codici;
- il server conserva solo hash delle impronte, il nome del PC e l'indirizzo dell'ultima richiesta.
"""

from __future__ import annotations

import ipaddress
import json
import logging
import re
import secrets
import sqlite3
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

from licenze import archivio
from sicur_license import impronta
from sicur_license.certificato import (
    ABBONAMENTO,
    ATTIVA,
    PERPETUA,
    REVOCATA,
    Certificato,
    ErroreCertificato,
    emetti,
    leggi_certificato,
)
from sicur_license.cliente import (
    ALTRO_PC,
    CODICE_ERRATO,
    LICENZA_REVOCATA,
    LICENZA_SCADUTA,
    PC_LIBERATO,
    POSTI_ESAURITI,
    SALE,
    TROPPE_RICHIESTE,
    TROPPI_TRASFERIMENTI,
)
from sicurcantiere import licenza

VALIDITA_CERTIFICATO = timedelta(days=14)
VALIDITA_OFFLINE = timedelta(days=90)
TRASFERIMENTI_MESE = 2
FINESTRA_TRASFERIMENTI = timedelta(days=30)
LIMITE_IP = (60, 600)            # richieste per indirizzo in 10 minuti
LIMITE_ERRORI_IP = (10, 3600)    # codici sbagliati per indirizzo in un'ora
LIMITE_LICENZA = (30, 3600)      # richieste per licenza in un'ora
FINESTRA_CLONE = timedelta(minutes=10)
CONSERVAZIONE_REGISTRO = timedelta(days=365)
NON_INCLUSO = "non_incluso"
NOMI_PROGRAMMI = {"psc": "SicurCantiere PSC", "pos": "SicurCantiere POS", "pimus": "SicurCantiere PiMUS"}

_IMPRONTA = re.compile(r"^[0-9a-f]{64}$|^$")
log = logging.getLogger(__name__)


def adesso() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Rifiuto(Exception):
    stato: int
    codice: str
    messaggio: str
    dati: dict = field(default_factory=dict)


def _data(giorno: str | None) -> str:
    return date.fromisoformat(giorno).strftime("%d/%m/%Y") if giorno else ""


# --- licenze e catene di rinnovo ---

def catena(conn: sqlite3.Connection, riga) -> tuple[int, sqlite3.Row]:
    """(id della prima licenza della catena, licenza in vigore: l'ultimo rinnovo)."""
    radice, visti = riga, {riga["id"]}
    while radice["rinnovo_di"] and radice["rinnovo_di"] not in visti:
        precedente = conn.execute("SELECT * FROM licenze WHERE id = ?", (radice["rinnovo_di"],)).fetchone()
        if precedente is None:
            break
        visti.add(precedente["id"])
        radice = precedente
    attuale = radice
    while True:  # i rinnovi successivi, fino all'ultimo
        successiva = conn.execute("SELECT * FROM licenze WHERE rinnovo_di = ? ORDER BY id DESC LIMIT 1",
                                  (attuale["id"],)).fetchone()
        if successiva is None or successiva["id"] in visti:
            break
        visti.add(successiva["id"])
        attuale = successiva
    return radice["id"], attuale


def dati_catena(conn: sqlite3.Connection, radice_id: int) -> sqlite3.Row:
    riga = conn.execute("SELECT * FROM catene_licenza WHERE radice_id = ?", (radice_id,)).fetchone()
    if riga is None:
        conn.execute("INSERT INTO catene_licenza (radice_id, sale) VALUES (?, ?)",
                     (radice_id, "licenza:" + secrets.token_hex(16)))
        riga = conn.execute("SELECT * FROM catene_licenza WHERE radice_id = ?", (radice_id,)).fetchone()
    return riga


def trova(conn: sqlite3.Connection, codice: str) -> tuple[int, sqlite3.Row, sqlite3.Row] | None:
    """(radice, licenza in vigore, dati della catena) per un codice di licenza, o None."""
    riga = conn.execute("SELECT * FROM licenze WHERE codice = ?", (impronta.normalizza_codice(codice),)).fetchone()
    if riga is None:
        return None
    radice, attuale = catena(conn, riga)
    return radice, attuale, dati_catena(conn, radice)


def posti(attuale: sqlite3.Row, dati: sqlite3.Row) -> int:
    return max(int(attuale["postazioni"] or 1), 1) + int(dati["posti_extra"] or 0)


def stato_licenza(attuale: sqlite3.Row, oggi: date) -> str:
    if attuale["stato"] == "annullata":
        return REVOCATA
    if attuale["scadenza"] and date.fromisoformat(attuale["scadenza"]) < oggi:
        return "scaduta"
    return ATTIVA


def prodotti(attuale: sqlite3.Row) -> frozenset[str]:
    return licenza.PIANI.get(attuale["piano"], ("", frozenset()))[1]


def pc_attivi(conn: sqlite3.Connection, radice: int) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM pc_licenza WHERE radice_id = ? AND stato = 'attivo' ORDER BY attivato, id",
                        (radice,)).fetchall()


def _impronte_pc(pc: sqlite3.Row) -> list[str]:
    return [pc["impronta_sistema"], pc["impronta_hardware"], pc["impronta_nome"]]


def nuove_attivazioni(conn: sqlite3.Connection, radice: int, ora: datetime) -> int:
    return conn.execute("SELECT COUNT(*) FROM eventi_licenza WHERE radice_id = ? AND evento = 'attivazione' "
                        "AND esito = 'nuovo_pc' AND quando >= ?",
                        (radice, (ora - FINESTRA_TRASFERIMENTI).isoformat())).fetchone()[0]


def trasferimenti_rimasti(conn, radice: int, attuale, dati, ora: datetime) -> int:
    massimo = posti(attuale, dati) + TRASFERIMENTI_MESE + int(dati["trasferimenti_extra"] or 0)
    return max(massimo - nuove_attivazioni(conn, radice, ora), 0)


def elenco(conn, radice: int, impronte: list[str] | None = None) -> list[dict]:
    return [{"id": p["codice_pc"], "nome": p["nome"] or "PC senza nome", "attivato": p["attivato"][:10],
             "ultimo_uso": p["ultimo_uso"][:10], "offline": bool(p["offline"]),
             "questo": bool(impronte) and impronta.stesso_pc(_impronte_pc(p), impronte)}
            for p in pc_attivi(conn, radice)]


# --- registro e limiti ---

def registra(conn, evento: str, esito: str = "", radice: int | None = None, codice_pc: str = "", ip: str = "",
             dettagli: str = "", ora: datetime | None = None) -> None:
    conn.execute("INSERT INTO eventi_licenza (quando, radice_id, codice_pc, evento, esito, ip, dettagli) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?)",
                 ((ora or adesso()).isoformat(), radice, codice_pc, evento, esito, ip, dettagli[:500]))


def _limite(conn, chiave: str, limite: tuple[int, int], ora: datetime, conta: bool = True) -> bool:
    """True se `chiave` ha superato il limite (richieste, secondi); registra la richiesta."""
    numero, secondi = limite
    istante = ora.timestamp()
    conn.execute("DELETE FROM limiti_richieste WHERE quando < ?", (istante - 3600,))
    recenti = conn.execute("SELECT COUNT(*) FROM limiti_richieste WHERE chiave = ? AND quando > ?",
                           (chiave, istante - secondi)).fetchone()[0]
    if conta:
        conn.execute("INSERT INTO limiti_richieste (chiave, quando) VALUES (?, ?)", (chiave, istante))
    return recenti >= numero


def indirizzo_noto(ip: str) -> bool:
    """False se l'indirizzo è quello del server stesso (tunnel che non indica il programma che si collega):
    i limiti per indirizzo allora non si applicano, altrimenti bloccherebbero tutti i clienti insieme."""
    try:
        return not ipaddress.ip_address(ip).is_loopback
    except ValueError:
        return False


def pulizia(conn, ora: datetime) -> None:
    """Il registro si conserva un anno (minimizzazione dei dati)."""
    conn.execute("DELETE FROM eventi_licenza WHERE quando < ?", ((ora - CONSERVAZIONE_REGISTRO).isoformat(),))


def _troppe() -> Rifiuto:
    return Rifiuto(429, TROPPE_RICHIESTE, "Troppe richieste in poco tempo: riprova tra qualche minuto.")


# --- controlli sui dati ricevuti ---

def _testo(dati: dict, nome: str, massimo: int = 200) -> str:
    valore = dati.get(nome, "")
    if not isinstance(valore, str) or len(valore) > massimo:
        raise Rifiuto(400, "richiesta", "Richiesta non valida.")
    return valore.strip()


def _impronte(dati: dict) -> list[str]:
    valore = dati.get("impronte")
    if (not isinstance(valore, list) or len(valore) != 3
            or not all(isinstance(v, str) and _IMPRONTA.match(v) for v in valore)):
        raise Rifiuto(400, "richiesta", "Impronta del PC non valida.")
    return list(valore)


def _codice_e_catena(conn, dati: dict, ip: str, ora: datetime):
    if indirizzo_noto(ip) and _limite(conn, f"errori:{ip}", LIMITE_ERRORI_IP, ora, conta=False):
        raise _troppe()
    codice = _testo(dati, "codice", 4000)
    trovata = trova(conn, codice) if codice else None
    if trovata is None:
        if indirizzo_noto(ip):
            _limite(conn, f"errori:{ip}", LIMITE_ERRORI_IP, ora)
        registra(conn, "codice_errato", ip=ip, ora=ora)
        raise Rifiuto(404, CODICE_ERRATO, "Il codice di licenza non è valido: controlla di averlo copiato per intero.")
    radice, attuale, catena_ = trovata
    if _limite(conn, f"licenza:{radice}", LIMITE_LICENZA, ora):
        raise _troppe()
    return radice, attuale, catena_


def _sale(dati: dict, catena_) -> None:
    if _testo(dati, "sale") != catena_["sale"]:
        # prima richiesta del programma: gli si comunica il sale della licenza (vedi sicur_license.cliente)
        raise Rifiuto(409, SALE, "Impronta del PC da ricalcolare.", {"sale": catena_["sale"]})


def _controlla_licenza(attuale, programma: str, ora: datetime) -> None:
    stato = stato_licenza(attuale, ora.date())
    if stato == REVOCATA:
        raise Rifiuto(403, LICENZA_REVOCATA, "La licenza è stata disattivata: contatta l'assistenza di SicurCantiere.")
    if stato == "scaduta":
        raise Rifiuto(403, LICENZA_SCADUTA, f"La licenza è scaduta il {_data(attuale['scadenza'])}: rinnovala per "
                                            "attivare altri PC.")
    if programma and programma not in prodotti(attuale):
        nome = NOMI_PROGRAMMI.get(programma, programma)
        raise Rifiuto(403, NON_INCLUSO, f"Questa licenza non comprende {nome}. Puoi aggiungerlo contattando "
                                        "SicurCantiere.")


def _certificato(conn, attuale, pc, ora: datetime, offline: bool = False) -> str:
    cliente = conn.execute("SELECT nome FROM clienti WHERE id = ?", (attuale["cliente_id"],)).fetchone()
    scadenza = date.fromisoformat(attuale["scadenza"]) if attuale["scadenza"] else None
    stato = REVOCATA if stato_licenza(attuale, ora.date()) == REVOCATA else ATTIVA
    radice = pc["radice_id"]
    c = Certificato(
        licenza=attuale["codice_licenza"], cliente=cliente["nome"] if cliente else "", prodotti=prodotti(attuale),
        tipo=ABBONAMENTO if scadenza else PERPETUA, pc=pc["codice_pc"], impronte=tuple(_impronte_pc(pc)),
        sale=pc["sale"], emesso=ora, valido_fino=ora + (VALIDITA_OFFLINE if offline else VALIDITA_CERTIFICATO),
        scadenza_licenza=scadenza, aggiornamenti_fino=scadenza,
        posti=posti(attuale, dati_catena(conn, radice)), stato=stato, offline=offline)
    privata, autorizzazione = archivio.chiave_servizio(ora)
    return emetti(c, privata, autorizzazione)


def _stessa_rete(a: str, b: str) -> bool:
    try:
        ia, ib = ipaddress.ip_address(a), ipaddress.ip_address(b)
    except ValueError:
        return a == b
    if ia.version != ib.version:
        return False
    prefisso = 16 if ia.version == 4 else 48
    return ipaddress.ip_network(f"{a}/{prefisso}", strict=False) == ipaddress.ip_network(f"{b}/{prefisso}",
                                                                                      strict=False)


# --- azioni ---

def attiva(conn, dati: dict, ip: str = "", ora: datetime | None = None, offline: bool = False) -> dict:
    ora = ora or adesso()
    radice, attuale, catena_ = _codice_e_catena(conn, dati, ip, ora)
    programma = _testo(dati, "programma", 20)
    impronte = _impronte(dati)
    if offline:
        sale = _testo(dati, "sale")
        if not sale:
            raise Rifiuto(400, "richiesta", "Richiesta di attivazione offline incompleta.")
    else:
        _sale(dati, catena_)
        sale = catena_["sale"]
    if sum(1 for v in impronte if v) < impronta.MINIMO_UGUALI:
        raise Rifiuto(400, "richiesta", "Impronta del PC incompleta: contatta l'assistenza.")
    try:
        _controlla_licenza(attuale, programma, ora)
    except Rifiuto as r:
        registra(conn, "attivazione", r.codice, radice, ip=ip, ora=ora)
        raise
    nome = _testo(dati, "nome_pc", 200)[:64]
    versione = _testo(dati, "versione", 40)
    attivi = pc_attivi(conn, radice)
    stesso = next((p for p in attivi if p["sale"] == sale and impronta.stesso_pc(_impronte_pc(p), impronte)), None)
    if stesso is not None:
        # stesso PC (anche con un componente cambiato): si aggiornano le impronte, nessun posto in più
        conn.execute("UPDATE pc_licenza SET impronta_sistema = ?, impronta_hardware = ?, impronta_nome = ?, "
                     "nome = ?, programma = ?, versione = ?, ultimo_uso = ?, ultimo_ip = ?, "
                     "offline = ? WHERE id = ?",
                     (*impronte, nome or stesso["nome"], programma, versione, ora.isoformat(), ip, int(offline),
                      stesso["id"]))
        registra(conn, "attivazione", "stesso_pc", radice, stesso["codice_pc"], ip, nome, ora)
        pc = conn.execute("SELECT * FROM pc_licenza WHERE id = ?", (stesso["id"],)).fetchone()
        return {"certificato": _certificato(conn, attuale, pc, ora, offline)}
    massimo = posti(attuale, catena_)
    if len(attivi) >= massimo:
        registra(conn, "attivazione", POSTI_ESAURITI, radice, ip=ip, dettagli=nome, ora=ora)
        raise Rifiuto(409, POSTI_ESAURITI,
                      f"La licenza è già attiva su {len(attivi)} PC su {massimo}. Per usarla su questo PC disattivane "
                      "uno, oppure aggiungi un posto alla licenza.",
                      {"pc": elenco(conn, radice, impronte), "posti": massimo, "attivi": len(attivi),
                       "trasferimenti_rimasti": trasferimenti_rimasti(conn, radice, attuale, catena_, ora)})
    if not offline and trasferimenti_rimasti(conn, radice, attuale, catena_, ora) <= 0:
        registra(conn, "attivazione", TROPPI_TRASFERIMENTI, radice, ip=ip, dettagli=nome, ora=ora)
        raise Rifiuto(429, TROPPI_TRASFERIMENTI,
                      "Negli ultimi 30 giorni la licenza è già stata spostata su altri PC il numero massimo di volte. "
                      "Per attivarla su questo PC contatta l'assistenza di SicurCantiere.")
    codice_pc = "PC-" + secrets.token_hex(6).upper()
    conn.execute("INSERT INTO pc_licenza (codice_pc, radice_id, sale, impronta_sistema, impronta_hardware, "
                 "impronta_nome, nome, programma, versione, attivato, ultimo_uso, ultimo_ip, offline) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (codice_pc, radice, sale, *impronte, nome, programma, versione, ora.isoformat(), ora.isoformat(),
                  ip, int(offline)))
    registra(conn, "attivazione", "nuovo_pc", radice, codice_pc, ip, nome + (" (offline)" if offline else ""), ora)
    pc = conn.execute("SELECT * FROM pc_licenza WHERE codice_pc = ?", (codice_pc,)).fetchone()
    return {"certificato": _certificato(conn, attuale, pc, ora, offline)}


def _pc_del_certificato(conn, dati: dict, ip: str, ora: datetime):
    """(certificato, PC sul server, impronte ricevute) dopo i controlli di firma e impronta."""
    try:
        cert = leggi_certificato(_testo(dati, "certificato", 20000), archivio.radice_pubblica())
    except ErroreCertificato as e:
        raise Rifiuto(400, "certificato", "Certificato di licenza non valido: attiva di nuovo il programma.") from e
    impronte = _impronte(dati)
    pc = conn.execute("SELECT * FROM pc_licenza WHERE codice_pc = ?", (cert.pc,)).fetchone()
    if pc is None or pc["stato"] != "attivo":
        raise Rifiuto(410, PC_LIBERATO, "Questo PC è stato disattivato dalla licenza: per usarlo di nuovo attiva la "
                                        "licenza con il tuo codice.")
    if _limite(conn, f"licenza:{pc['radice_id']}", LIMITE_LICENZA, ora):
        raise _troppe()
    if cert.sale != pc["sale"] or not impronta.stesso_pc(_impronte_pc(pc), impronte):
        registra(conn, "convalida", ALTRO_PC, pc["radice_id"], pc["codice_pc"], ip, ora=ora)
        raise Rifiuto(403, ALTRO_PC, "Il certificato di licenza appartiene a un altro PC: attiva la licenza su questo "
                                     "PC con il tuo codice.")
    return cert, pc, impronte


def convalida(conn, dati: dict, ip: str = "", ora: datetime | None = None) -> dict:
    ora = ora or adesso()
    _, pc, impronte = _pc_del_certificato(conn, dati, ip, ora)
    attuale = catena(conn, conn.execute("SELECT * FROM licenze WHERE id = ?", (pc["radice_id"],)).fetchone())[1]
    sospetto = pc["sospetto"]
    ultimo = datetime.fromisoformat(pc["ultimo_uso"])
    if indirizzo_noto(pc["ultimo_ip"]) and indirizzo_noto(ip) and not _stessa_rete(pc["ultimo_ip"], ip) and ora - ultimo < FINESTRA_CLONE:
        # stesso PC da due reti lontane quasi insieme: probabile copia della macchina virtuale
        sospetto = f"{ora:%d/%m/%Y %H:%M}: in uso da {pc['ultimo_ip']} e {ip} a pochi minuti di distanza"
        registra(conn, "sospetto_clone", "", pc["radice_id"], pc["codice_pc"], ip, sospetto, ora)
    conn.execute("UPDATE pc_licenza SET impronta_sistema = ?, impronta_hardware = ?, impronta_nome = ?, "
                 "ultimo_uso = ?, ultimo_ip = ?, versione = ?, offline = 0, sospetto = ? WHERE id = ?",
                 (*impronte, ora.isoformat(), ip, _testo(dati, "versione", 40) or pc["versione"], sospetto, pc["id"]))
    pc = conn.execute("SELECT * FROM pc_licenza WHERE id = ?", (pc["id"],)).fetchone()
    testo = _certificato(conn, attuale, pc, ora)
    if stato_licenza(attuale, ora.date()) == REVOCATA:
        registra(conn, "convalida", LICENZA_REVOCATA, pc["radice_id"], pc["codice_pc"], ip, ora=ora)
        raise Rifiuto(403, LICENZA_REVOCATA, "La licenza è stata disattivata: contatta l'assistenza di SicurCantiere.",
                      {"certificato": testo})
    registra(conn, "convalida", "ok", pc["radice_id"], pc["codice_pc"], ip, ora=ora)
    return {"certificato": testo}


def _disattiva_pc(conn, pc, motivo: str, ora: datetime) -> None:
    conn.execute("UPDATE pc_licenza SET stato = 'disattivato', disattivato = ?, motivo = ? WHERE id = ?",
                 (ora.isoformat(), motivo, pc["id"]))


def disattiva(conn, dati: dict, ip: str = "", ora: datetime | None = None) -> dict:
    ora = ora or adesso()
    _, pc, _ = _pc_del_certificato(conn, dati, ip, ora)
    _disattiva_pc(conn, pc, "disattivato dal PC", ora)
    registra(conn, "disattivazione", "dal_pc", pc["radice_id"], pc["codice_pc"], ip, pc["nome"], ora)
    return {"ok": True}


def elenco_pc(conn, dati: dict, ip: str = "", ora: datetime | None = None) -> dict:
    ora = ora or adesso()
    radice, attuale, catena_ = _codice_e_catena(conn, dati, ip, ora)
    _sale(dati, catena_)
    attivi = elenco(conn, radice, _impronte(dati))
    return {"pc": attivi, "posti": posti(attuale, catena_), "attivi": len(attivi),
            "trasferimenti_rimasti": trasferimenti_rimasti(conn, radice, attuale, catena_, ora)}


def libera(conn, dati: dict, ip: str = "", ora: datetime | None = None) -> dict:
    """Disattiva un PC della licenza da un altro PC (trasferimento self-service)."""
    ora = ora or adesso()
    radice, attuale, catena_ = _codice_e_catena(conn, dati, ip, ora)
    _sale(dati, catena_)
    impronte = _impronte(dati)
    pc = conn.execute("SELECT * FROM pc_licenza WHERE codice_pc = ? AND radice_id = ? AND stato = 'attivo'",
                      (_testo(dati, "pc", 40), radice)).fetchone()
    if pc is None:
        raise Rifiuto(404, "pc", "Il PC indicato non è attivo su questa licenza.")
    _disattiva_pc(conn, pc, f"liberato da {_testo(dati, 'nome_pc', 200)[:64] or 'un altro PC'}", ora)
    registra(conn, "disattivazione", "trasferimento", radice, pc["codice_pc"], ip, pc["nome"], ora)
    return {"ok": True, "questo": impronta.stesso_pc(_impronte_pc(pc), impronte),
            "trasferimenti_rimasti": trasferimenti_rimasti(conn, radice, attuale, catena_, ora)}


def attiva_offline(conn, testo_richiesta: str, ora: datetime | None = None) -> str:
    """Certificato per un file di richiesta offline (lo usa il gestionale, non è su internet)."""
    try:
        richiesta = json.loads(testo_richiesta)
    except ValueError as e:
        raise Rifiuto(400, "richiesta", "Il file non è una richiesta di attivazione di SicurCantiere.") from e
    if not isinstance(richiesta, dict) or richiesta.get("tipo") != "richiesta_attivazione_offline":
        raise Rifiuto(400, "richiesta", "Il file non è una richiesta di attivazione di SicurCantiere.")
    return attiva(conn, richiesta, ip="gestionale", ora=ora, offline=True)["certificato"]


# --- servizio web ---

AZIONI = {"attiva": attiva, "convalida": convalida, "disattiva": disattiva, "pc": elenco_pc, "libera": libera}


def blueprint() -> Blueprint:
    bp = Blueprint("attivazioni", __name__)

    @bp.post("/api/licenze/<azione>")
    def richiesta_licenza(azione: str):
        funzione = AZIONI.get(azione)
        if funzione is None:
            return jsonify({"errore": "richiesta", "messaggio": "Richiesta non valida."}), 404
        dati = request.get_json(silent=True)
        ip = request.remote_addr or ""
        conn = archivio.connessione()
        try:
            conn.execute("BEGIN IMMEDIATE")  # una richiesta alla volta per licenza: niente posti contati due volte
            ora = adesso()
            if indirizzo_noto(ip) and _limite(conn, f"ip:{ip}", LIMITE_IP, ora):
                raise _troppe()
            if not isinstance(dati, dict):
                raise Rifiuto(400, "richiesta", "Richiesta non valida.")
            risposta = funzione(conn, dati, ip, ora)
            pulizia(conn, ora)
            conn.commit()
            return jsonify(risposta)
        except Rifiuto as r:
            conn.commit()  # il registro dei rifiuti e i limiti restano
            return jsonify({"errore": r.codice, "messaggio": r.messaggio, **r.dati}), r.stato
        except Exception:  # nessun dettaglio tecnico al programma del cliente
            conn.rollback()
            log.exception("Errore del server delle attivazioni (%s)", azione)
            return jsonify({"errore": "interno", "messaggio": "Il server delle licenze non ha potuto rispondere: "
                                                              "riprova più tardi."}), 500
        finally:
            conn.close()

    return bp
