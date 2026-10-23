"""Server pubblico: ponte dell'assistente AI incluso nella licenza (SicurCantiere AI) e attivazioni dei PC.

Le attivazioni (limite di PC, certificati, trasferimenti) sono in licenze/attivazioni.py.

I programmi dei clienti non hanno chiavi dei fornitori AI: mandano qui la richiesta con il codice di
licenza. Il server verifica la licenza, controlla il credito del mese, inoltra la richiesta al
fornitore con le chiavi dell'ufficio e registra il consumo.

È un'applicazione separata dal gestionale (licenze.wsgi_api:app) perché è l'unica parte raggiungibile da
internet: il gestionale resta nella rete dell'ufficio o su Tailscale.

Motori (configurati in /etc/sicurcantiere-licenze/ai.env, vedi README):
- standard: DeepSeek o un servizio compatibile (anche ospitato in Europa), per tutti i piani;
- avanzato: Claude, solo nel piano Studio; consuma più crediti per token.

Crediti: token in ingresso e in uscita per il moltiplicatore del motore. Quota mensile per piano,
tetto giornaliero di sicurezza e ricariche extra (che non scadono) aggiunte dal gestionale.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import date, datetime

from flask import Flask, jsonify, request

from licenze import archivio
from sicurcantiere import ai, licenza

QUOTE_MENSILI = {"pos": 1_500_000, "psc": 1_500_000, "pimus": 1_500_000, "completo": 3_000_000, "studio": 8_000_000}
TETTO_GIORNALIERO = 0.30  # quota del mese utilizzabile in un giorno (contro abusi e codici condivisi)
RICHIESTE_AL_MINUTO = 30
MOLTIPLICATORI = {ai.STANDARD: 1, ai.AVANZATO: 8}
PIANI_AVANZATO = {"studio"}
MAX_TESTO = 150_000  # caratteri di una richiesta
MAX_SCHEMA = 60_000


@dataclass(frozen=True)
class Motore:
    fornitore: str
    modello: str
    chiave: str
    url: str
    sede: str


def motori() -> dict[str, Motore | None]:
    """Motori configurati con le variabili d'ambiente del servizio (None se manca la chiave)."""
    env = os.environ.get
    standard = Motore(ai.DEEPSEEK, env("SICURCANTIERE_AI_STANDARD_MODELLO", "deepseek-v4-pro"),
                      env("SICURCANTIERE_AI_STANDARD_CHIAVE", ""), env("SICURCANTIERE_AI_STANDARD_URL", ""),
                      env("SICURCANTIERE_AI_STANDARD_SEDE", "DeepSeek, con trattamento dei dati in Cina"))
    avanzato = Motore(ai.ANTHROPIC, env("SICURCANTIERE_AI_AVANZATO_MODELLO", "claude-sonnet-5-5"),
                      env("SICURCANTIERE_AI_AVANZATO_CHIAVE", ""), "",
                      env("SICURCANTIERE_AI_AVANZATO_SEDE", "Anthropic (Claude), con trattamento dei dati negli "
                                                            "Stati Uniti"))
    return {ai.STANDARD: standard if standard.chiave else None, ai.AVANZATO: avanzato if avanzato.chiave else None}


def mese(giorno: date) -> str:
    return giorno.isoformat()[:7]


def situazione(conn, cliente_id: int, piano: str, oggi: date | None = None) -> dict[str, int]:
    """Credito AI del cliente: quota del mese, usato nel mese e oggi, ricariche, residuo."""
    oggi = oggi or date.today()
    quota = QUOTE_MENSILI.get(piano, QUOTE_MENSILI["pos"])
    per_mese = dict(conn.execute("SELECT substr(data, 1, 7), SUM(crediti) FROM consumi_ai WHERE cliente_id = ? "
                                 "GROUP BY substr(data, 1, 7)", (cliente_id,)).fetchall())
    usati_mese = per_mese.get(mese(oggi), 0) or 0
    usati_oggi = conn.execute("SELECT COALESCE(SUM(crediti), 0) FROM consumi_ai WHERE cliente_id = ? AND data = ?",
                              (cliente_id, oggi.isoformat())).fetchone()[0]
    ricariche = conn.execute("SELECT COALESCE(SUM(crediti), 0) FROM ricariche_ai WHERE cliente_id = ?",
                             (cliente_id,)).fetchone()[0]
    # le ricariche coprono quello che ogni mese ha superato la quota
    extra_usati = sum(max(0, (v or 0) - quota) for m, v in per_mese.items())
    extra = max(0, ricariche - extra_usati)
    residuo = max(0, quota - usati_mese) + extra
    return {"quota": quota, "usati_mese": usati_mese, "usati_oggi": usati_oggi, "extra": extra,
            "residuo": residuo, "tetto_oggi": int(quota * TETTO_GIORNALIERO) + extra}


def _errore(messaggio: str, stato: int):
    return jsonify({"errore": messaggio}), stato


def crea_api() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 2 * MAX_TESTO
    # Il servizio ascolta solo in locale (127.0.0.1) e arriva da internet tramite Tailscale Funnel o un
    # tunnel: l'indirizzo vero del programma che si collega è in X-Forwarded-For.
    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    from licenze.attivazioni import blueprint

    app.register_blueprint(blueprint())  # attivazioni dei PC: /api/licenze/...

    def licenza_valida(conn, codice: str):
        """(riga della licenza nel registro, licenza) oppure una risposta di errore."""
        try:
            dati = licenza.leggi(codice or "", archivio.chiave_pubblica())
        except licenza.ErroreLicenza:
            return None, _errore("Codice di licenza non valido.", 403)
        riga = conn.execute("SELECT * FROM licenze WHERE codice = ?", ("".join((codice or "").split()),)).fetchone()
        if riga is None or riga["stato"] == "annullata":
            return None, _errore("Licenza non attiva per l'assistente AI: contatta l'assistenza SicurCantiere.", 403)
        if dati.scaduta():
            return None, _errore("Licenza scaduta: l'assistente AI incluso tornerà disponibile con il rinnovo. "
                                 "Le altre funzioni del programma restano disponibili.", 403)
        return (riga, dati), None

    @app.post("/api/ai/stato")
    def stato():
        conn = archivio.connessione()
        trovata, errore = licenza_valida(conn, (request.get_json(silent=True) or {}).get("licenza", ""))
        if errore:
            return errore
        riga, dati = trovata
        configurati = motori()
        return jsonify({"credito": situazione(conn, riga["cliente_id"], dati.piano),
                        "motori": {k: {"sede": m.sede, "disponibile": k != ai.AVANZATO or dati.piano in PIANI_AVANZATO}
                                   for k, m in configurati.items() if m}})

    @app.post("/api/ai/richiesta")
    def richiesta():
        dati_richiesta = request.get_json(silent=True) or {}
        testo, schema = dati_richiesta.get("testo"), dati_richiesta.get("schema")
        nome_motore = dati_richiesta.get("motore") or ai.STANDARD
        if not isinstance(testo, str) or not isinstance(schema, dict) or nome_motore not in MOLTIPLICATORI:
            return _errore("Richiesta non valida.", 400)
        if len(testo) > MAX_TESTO or len(json.dumps(schema)) > MAX_SCHEMA:
            return _errore("Richiesta troppo lunga: dividi il testo in parti più brevi.", 413)
        conn = archivio.connessione()
        trovata, errore = licenza_valida(conn, dati_richiesta.get("licenza", ""))
        if errore:
            return errore
        riga, dati = trovata
        motore = motori()[nome_motore]
        if nome_motore == ai.AVANZATO and dati.piano not in PIANI_AVANZATO:
            return _errore("Il motore avanzato (Claude) è incluso solo nel piano Studio: usa il motore Standard.", 403)
        if motore is None:
            return _errore("Il servizio SicurCantiere AI non è al momento disponibile: riprova più tardi.", 503)
        cliente = riga["cliente_id"]
        recenti = conn.execute("SELECT COUNT(*) FROM consumi_ai WHERE cliente_id = ? AND istante > ?",
                               (cliente, time.time() - 60)).fetchone()[0]
        if recenti >= RICHIESTE_AL_MINUTO:
            return _errore("Troppe richieste in poco tempo: riprova tra un minuto.", 429)
        credito = situazione(conn, cliente, dati.piano)
        if credito["residuo"] <= 0:
            return _errore("Credito AI del mese esaurito: tornerà disponibile il primo giorno del mese prossimo, oppure "
                           "puoi acquistare una ricarica. Le altre funzioni del programma restano disponibili.", 402)
        if credito["usati_oggi"] >= credito["tetto_oggi"]:
            return _errore("Hai raggiunto il limite giornaliero dell'assistente AI (30% del credito mensile): "
                           "tornerà disponibile domani.", 429)

        massimo = os.environ.get(f"SICURCANTIERE_AI_{nome_motore.upper()}_MAX_TOKEN", "")
        assistente = ai.AssistenteAI(fornitore=motore.fornitore, api_key=motore.chiave, modello=motore.modello,
                                     url=motore.url or None, max_token=int(massimo) if massimo.isdigit() else None)
        troncata = False
        try:
            contenuto = assistente.richiesta_grezza(testo, schema)
        except ai.RispostaTroncata as e:
            contenuto, troncata = e.parziale, True  # il programma divide il testo o recupera la parte valida
            app.logger.warning("Risposta troncata (motore %s, token in uscita %s): valutare "
                               "SICURCANTIERE_AI_%s_MAX_TOKEN", nome_motore, assistente.uso[1], nome_motore.upper())
        except ai.ErroreAI as e:
            app.logger.warning("Errore del fornitore AI: %s", e)
            return _errore("Il servizio SicurCantiere AI non ha potuto rispondere: riprova tra qualche minuto.", 502)
        entrata, uscita = assistente.uso
        crediti = (entrata + uscita) * MOLTIPLICATORI[nome_motore]
        adesso = datetime.now()
        conn.execute("INSERT INTO consumi_ai (cliente_id, licenza_id, data, istante, motore, token_ingresso, "
                     "token_uscita, crediti) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     (cliente, riga["id"], adesso.date().isoformat(), time.time(), nome_motore, entrata, uscita,
                      crediti))
        conn.commit()
        return jsonify({"contenuto": contenuto, "troncata": troncata, "uso": [entrata, uscita],
                        "credito": situazione(conn, cliente, dati.piano)})

    @app.errorhandler(413)
    def troppo_grande(_):
        return _errore("Richiesta troppo lunga: dividi il testo in parti più brevi.", 413)

    return app
