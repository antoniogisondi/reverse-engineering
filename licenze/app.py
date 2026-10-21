"""Gestionale web delle licenze SicurCantiere: clienti, licenze, rinnovi, pagamenti e scadenze.

Gira sul server dell'ufficio e si può aprire anche da internet: chi lo apre dal browser deve
accedere con nome, password e (se attivata) il codice dell'app di autenticazione; dopo troppi
tentativi sbagliati l'accesso si blocca per un po'. Qui si firmano le licenze con la chiave
privata, che non lascia mai il server; i programmi dei clienti verificano il codice senza
collegarsi a niente.
"""

from __future__ import annotations

import csv
import io
import os
import secrets
import time
from datetime import date, timedelta
from functools import wraps

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from licenze import archivio, totp
from sicurcantiere import licenza

GIORNI_AVVISO = 30
BLOCCO_SECONDI = 15 * 60
TENTATIVI_UTENTE = 5  # tentativi sbagliati per nome utente prima del blocco
TENTATIVI_IP = 20  # tentativi sbagliati dallo stesso indirizzo prima del blocco
METODI_PAGAMENTO = ("Bonifico", "Carta", "PayPal", "Contanti", "Altro")


def crea_app(https: bool = True) -> Flask:
    """https=False solo per le prove in locale (python -m licenze prova)."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = archivio.segreto_sessione()
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
    app.config["SESSION_COOKIE_SECURE"] = https
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    if os.environ.get("SICURCANTIERE_LICENZE_PROXY") == "1":
        # Dietro Caddy (accesso da internet): l'indirizzo del visitatore arriva in X-Forwarded-For.
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    @app.context_processor
    def comuni():
        return {"piani": licenza.PIANI, "token": _token(), "oggi": date.today().isoformat(),
                "utente": session.get("utente"), "con_2fa": session.get("2fa", False)}

    @app.template_filter("data")
    def data_it(valore):
        if not valore:
            return "senza scadenza"
        anno, mese, giorno = str(valore)[:10].split("-")
        return f"{giorno}/{mese}/{anno}"

    @app.template_filter("euro")
    def euro(valore):
        return f"{float(valore or 0):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

    @app.before_request
    def controlli():
        atteso = session.get("token")
        if request.method == "POST" and (not atteso or not secrets.compare_digest(request.form.get("token", ""), atteso)):
            abort(400, "Modulo scaduto: ricaricare la pagina.")
        if request.endpoint not in ("accesso", "static") and not session.get("utente"):
            return redirect(url_for("accesso", prossima=request.path))
        return None

    @app.after_request
    def intestazioni(risposta):
        risposta.headers.setdefault("Content-Security-Policy",
                                    "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                                    "frame-ancestors 'none'; form-action 'self'; base-uri 'none'")
        risposta.headers.setdefault("X-Frame-Options", "DENY")
        risposta.headers.setdefault("X-Content-Type-Options", "nosniff")
        risposta.headers.setdefault("Referrer-Policy", "no-referrer")
        if request.endpoint != "static":
            risposta.headers.setdefault("Cache-Control", "no-store")
        return risposta

    _rotte(app)
    return app


def _token() -> str:
    if "token" not in session:
        session["token"] = secrets.token_urlsafe(24)
    return session["token"]


def _db():
    return archivio.connessione()


def _stato_licenza(riga) -> str:
    if riga["stato"] != "attiva":
        return riga["stato"]
    if riga["scadenza"] and riga["scadenza"] < date.today().isoformat():
        return "scaduta"
    if riga["scadenza"] and riga["scadenza"] <= (date.today() + timedelta(days=GIORNI_AVVISO)).isoformat():
        return "in scadenza"
    return "attiva"


def _nuovo_identificativo(conn) -> str:
    anno = date.today().year
    n = conn.execute("SELECT COUNT(*) FROM licenze WHERE codice_licenza LIKE ?", (f"SC-{anno}-%",)).fetchone()[0]
    return f"SC-{anno}-{n + 1:04d}"


def emetti(conn, cliente_id: int, piano: str, scadenza: date | None, postazioni: int, prezzo: float,
           note: str = "", rinnovo_di: int | None = None) -> int:
    """Crea e firma una licenza; restituisce l'id della riga."""
    cliente = conn.execute("SELECT * FROM clienti WHERE id = ?", (cliente_id,)).fetchone()
    if cliente is None or piano not in licenza.PIANI:
        abort(400, "Cliente o piano non validi.")
    identificativo = _nuovo_identificativo(conn)
    dati = licenza.Licenza(id=identificativo, cliente=cliente["nome"], piano=piano, emessa=date.today(),
                           scadenza=scadenza, postazioni=postazioni)
    codice = licenza.firma(dati, archivio.chiave_privata())
    cur = conn.execute(
        "INSERT INTO licenze (codice_licenza, cliente_id, piano, emessa, scadenza, postazioni, prezzo, codice, "
        "rinnovo_di, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (identificativo, cliente_id, piano, dati.emessa.isoformat(), scadenza.isoformat() if scadenza else None,
         postazioni, prezzo, codice, rinnovo_di, note))
    conn.commit()
    return cur.lastrowid


def _bloccato(conn, nome: str, ip: str) -> bool:
    dal = time.time() - BLOCCO_SECONDI
    conn.execute("DELETE FROM accessi_falliti WHERE quando < ?", (dal,))
    per_nome = conn.execute("SELECT COUNT(*) FROM accessi_falliti WHERE nome = ?", (nome,)).fetchone()[0]
    per_ip = conn.execute("SELECT COUNT(*) FROM accessi_falliti WHERE ip = ?", (ip,)).fetchone()[0]
    return per_nome >= TENTATIVI_UTENTE or per_ip >= TENTATIVI_IP


def _controlla_accesso(conn, nome: str, password: str, codice: str):
    """Riga dell'utente se nome, password e (se attivato) codice dell'app sono giusti."""
    utente = conn.execute("SELECT * FROM utenti WHERE nome = ?", (nome,)).fetchone()
    if utente is None or not check_password_hash(utente["password"], password):
        return None
    if utente["totp"]:
        contatore = totp.verifica(utente["totp"], codice, utente["totp_ultimo"])
        if contatore is None:
            return None
        conn.execute("UPDATE utenti SET totp_ultimo = ? WHERE id = ?", (contatore, utente["id"]))
    return utente


def _rotte(app: Flask) -> None:
    @app.route("/accesso", methods=["GET", "POST"])
    def accesso():
        if request.method == "POST":
            conn = _db()
            nome, ip = request.form.get("nome", "").strip(), request.remote_addr or ""
            if _bloccato(conn, nome, ip):
                conn.commit()
                flash("Troppi tentativi sbagliati: riprovare tra 15 minuti.", "errore")
                return render_template("accesso.html"), 429
            utente = _controlla_accesso(conn, nome, request.form.get("password", ""), request.form.get("codice", ""))
            if utente is None:
                conn.execute("INSERT INTO accessi_falliti (nome, ip, quando) VALUES (?, ?, ?)", (nome, ip, time.time()))
                conn.commit()
                flash("Nome, password o codice non corretti.", "errore")
                return render_template("accesso.html")
            conn.execute("DELETE FROM accessi_falliti WHERE nome = ?", (nome,))
            conn.commit()
            session.clear()
            session["utente"] = utente["nome"]
            session["2fa"] = bool(utente["totp"])
            session["token"] = secrets.token_urlsafe(24)
            session.permanent = True
            prossima = request.args.get("prossima", "")
            return redirect(prossima if prossima.startswith("/") and not prossima.startswith("//")
                            else url_for("cruscotto"))
        return render_template("accesso.html")

    @app.route("/esci", methods=["POST"])
    def esci():
        session.clear()
        return redirect(url_for("accesso"))

    @app.route("/")
    def cruscotto():
        conn = _db()
        oggi = date.today()
        righe = conn.execute(
            "SELECT l.*, c.nome AS cliente FROM licenze l JOIN clienti c ON c.id = l.cliente_id "
            "WHERE l.stato = 'attiva' AND l.scadenza IS NOT NULL AND l.scadenza <= ? ORDER BY l.scadenza",
            ((oggi + timedelta(days=GIORNI_AVVISO)).isoformat(),)).fetchall()
        in_scadenza = [r for r in righe if r["scadenza"] >= oggi.isoformat()]
        scadute = [r for r in righe if r["scadenza"] < oggi.isoformat()]
        numeri = {
            "clienti": conn.execute("SELECT COUNT(*) FROM clienti").fetchone()[0],
            "attive": conn.execute("SELECT COUNT(*) FROM licenze WHERE stato = 'attiva' AND "
                                   "(scadenza IS NULL OR scadenza >= ?)", (oggi.isoformat(),)).fetchone()[0],
            "incassato": conn.execute("SELECT COALESCE(SUM(importo), 0) FROM pagamenti WHERE data >= ?",
                                      (f"{oggi.year}-01-01",)).fetchone()[0],
        }
        recenti = conn.execute("SELECT l.*, c.nome AS cliente FROM licenze l JOIN clienti c ON c.id = l.cliente_id "
                               "ORDER BY l.id DESC LIMIT 8").fetchall()
        return render_template("cruscotto.html", in_scadenza=in_scadenza, scadute=scadute, numeri=numeri,
                               recenti=recenti, anno=oggi.year)

    @app.route("/clienti")
    def clienti():
        cerca = request.args.get("cerca", "").strip()
        filtro = f"%{cerca}%"
        righe = _db().execute(
            "SELECT c.*, (SELECT MAX(scadenza) FROM licenze WHERE cliente_id = c.id AND stato = 'attiva') AS scadenza, "
            "(SELECT COUNT(*) FROM licenze WHERE cliente_id = c.id) AS n_licenze FROM clienti c "
            "WHERE c.nome LIKE ? OR c.email LIKE ? OR c.partita_iva LIKE ? ORDER BY c.nome",
            (filtro, filtro, filtro)).fetchall()
        return render_template("clienti.html", clienti=righe, cerca=cerca)

    campi_cliente = ("nome", "tipo", "partita_iva", "codice_fiscale", "email", "pec", "telefono", "indirizzo",
                     "codice_sdi", "note")

    @app.route("/clienti/nuovo", methods=["GET", "POST"])
    @app.route("/clienti/<int:id_>/modifica", methods=["GET", "POST"])
    def modifica_cliente(id_: int | None = None):
        conn = _db()
        cliente = conn.execute("SELECT * FROM clienti WHERE id = ?", (id_,)).fetchone() if id_ else None
        if id_ and cliente is None:
            abort(404)
        if request.method == "POST":
            valori = {k: request.form.get(k, "").strip() for k in campi_cliente}
            if not valori["nome"]:
                flash("Indicare il nome o la ragione sociale.", "errore")
                return render_template("cliente_modifica.html", cliente=valori)
            if id_:
                conn.execute(f"UPDATE clienti SET {', '.join(f'{k} = ?' for k in campi_cliente)} WHERE id = ?",
                             (*valori.values(), id_))
            else:
                id_ = conn.execute(f"INSERT INTO clienti ({', '.join(campi_cliente)}) VALUES "
                                   f"({', '.join('?' for _ in campi_cliente)})", tuple(valori.values())).lastrowid
            conn.commit()
            flash("Cliente salvato.", "ok")
            return redirect(url_for("cliente", id_=id_))
        return render_template("cliente_modifica.html", cliente=cliente or {k: "" for k in campi_cliente})

    @app.route("/clienti/<int:id_>")
    def cliente(id_: int):
        conn = _db()
        c = conn.execute("SELECT * FROM clienti WHERE id = ?", (id_,)).fetchone()
        if c is None:
            abort(404)
        licenze_ = conn.execute("SELECT * FROM licenze WHERE cliente_id = ? ORDER BY id DESC", (id_,)).fetchall()
        pagamenti = conn.execute("SELECT p.*, l.codice_licenza FROM pagamenti p LEFT JOIN licenze l "
                                 "ON l.id = p.licenza_id WHERE p.cliente_id = ? ORDER BY p.data DESC",
                                 (id_,)).fetchall()
        return render_template("cliente.html", cliente=c, licenze=licenze_, pagamenti=pagamenti,
                               stato=_stato_licenza, metodi=METODI_PAGAMENTO)

    @app.route("/clienti/<int:id_>/licenza", methods=["POST"])
    def nuova_licenza(id_: int):
        f = request.form
        scadenza = None if f.get("senza_scadenza") else date.fromisoformat(f.get("scadenza") or
                                                                        (date.today() + timedelta(days=365)).isoformat())
        conn = _db()
        nuova = emetti(conn, id_, f.get("piano", "pos"), scadenza, int(f.get("postazioni") or 1),
                       float((f.get("prezzo") or "0").replace(",", ".")), f.get("note", ""))
        flash("Licenza emessa: copia il codice e mandalo al cliente.", "ok")
        return redirect(url_for("dettaglio_licenza", id_=nuova))

    @app.route("/licenze/<int:id_>")
    def dettaglio_licenza(id_: int):
        conn = _db()
        l = conn.execute("SELECT l.*, c.nome AS cliente, c.email FROM licenze l JOIN clienti c ON c.id = l.cliente_id "
                         "WHERE l.id = ?", (id_,)).fetchone()
        if l is None:
            abort(404)
        precedente = conn.execute("SELECT id, codice_licenza FROM licenze WHERE id = ?", (l["rinnovo_di"],)).fetchone()
        successiva = conn.execute("SELECT id, codice_licenza FROM licenze WHERE rinnovo_di = ?", (id_,)).fetchone()
        return render_template("licenza.html", l=l, stato=_stato_licenza(l), precedente=precedente,
                               successiva=successiva, nome_piano=licenza.PIANI[l["piano"]][0])

    @app.route("/licenze/<int:id_>/rinnova", methods=["POST"])
    def rinnova(id_: int):
        conn = _db()
        vecchia = conn.execute("SELECT * FROM licenze WHERE id = ?", (id_,)).fetchone()
        if vecchia is None:
            abort(404)
        base = max(date.fromisoformat(vecchia["scadenza"]) if vecchia["scadenza"] else date.today(), date.today())
        piano = request.form.get("piano") or vecchia["piano"]
        nuova = emetti(conn, vecchia["cliente_id"], piano, base + timedelta(days=365), vecchia["postazioni"],
                       float((request.form.get("prezzo") or vecchia["prezzo"] or 0)), rinnovo_di=id_)
        conn.execute("UPDATE licenze SET stato = 'rinnovata' WHERE id = ?", (id_,))
        conn.commit()
        flash("Rinnovo emesso: manda al cliente il nuovo codice.", "ok")
        return redirect(url_for("dettaglio_licenza", id_=nuova))

    @app.route("/licenze/<int:id_>/annulla", methods=["POST"])
    def annulla(id_: int):
        conn = _db()
        conn.execute("UPDATE licenze SET stato = 'annullata' WHERE id = ?", (id_,))
        conn.commit()
        flash("Licenza segnata come annullata (solo nel registro: un codice già consegnato resta valido "
              "fino alla scadenza).", "ok")
        return redirect(url_for("dettaglio_licenza", id_=id_))

    @app.route("/clienti/<int:id_>/pagamento", methods=["POST"])
    def nuovo_pagamento(id_: int):
        f = request.form
        conn = _db()
        conn.execute("INSERT INTO pagamenti (cliente_id, licenza_id, data, importo, metodo, fattura, note) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (id_, int(f["licenza_id"]) if f.get("licenza_id") else None, f.get("data") or date.today().isoformat(),
                      float((f.get("importo") or "0").replace(",", ".")), f.get("metodo", ""), f.get("fattura", ""),
                      f.get("note", "")))
        conn.commit()
        flash("Pagamento registrato.", "ok")
        return redirect(url_for("cliente", id_=id_))

    @app.route("/esporta.csv")
    def esporta():
        conn = _db()
        uscita = io.StringIO()
        scrittore = csv.writer(uscita, delimiter=";")
        scrittore.writerow(["Licenza", "Cliente", "Email", "Partita IVA", "Piano", "Emessa", "Scadenza", "Postazioni",
                            "Prezzo", "Stato"])
        for r in conn.execute("SELECT l.*, c.nome AS cliente, c.email, c.partita_iva FROM licenze l "
                              "JOIN clienti c ON c.id = l.cliente_id ORDER BY l.id"):
            scrittore.writerow([r["codice_licenza"], r["cliente"], r["email"], r["partita_iva"], r["piano"],
                                r["emessa"], r["scadenza"] or "", r["postazioni"], r["prezzo"], _stato_licenza(r)])
        return Response("﻿" + uscita.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=licenze.csv"})

    @app.route("/impostazioni")
    def impostazioni():
        return render_template("impostazioni.html", chiave=archivio.chiave_pubblica(),
                               cartella=archivio.cartella_dati())

    @app.route("/impostazioni/due-passaggi", methods=["GET", "POST"])
    def due_passaggi():
        """Attiva la verifica in due passaggi: QR code per l'app, poi conferma con il primo codice."""
        conn = _db()
        utente = conn.execute("SELECT * FROM utenti WHERE nome = ?", (session["utente"],)).fetchone()
        if request.method == "POST":
            if request.form.get("azione") == "disattiva":
                if not check_password_hash(utente["password"], request.form.get("password", "")):
                    flash("Password non corretta.", "errore")
                    return redirect(url_for("due_passaggi"))
                conn.execute("UPDATE utenti SET totp = '', totp_ultimo = 0 WHERE id = ?", (utente["id"],))
                conn.commit()
                session["2fa"] = False
                flash("Verifica in due passaggi disattivata.", "ok")
                return redirect(url_for("impostazioni"))
            segreto = session.get("totp_nuovo", "")
            contatore = totp.verifica(segreto, request.form.get("codice", ""))
            if contatore is None:
                flash("Codice non corretto: controllare l'ora del telefono e riprovare.", "errore")
                return redirect(url_for("due_passaggi"))
            conn.execute("UPDATE utenti SET totp = ?, totp_ultimo = ? WHERE id = ?", (segreto, contatore, utente["id"]))
            conn.commit()
            session.pop("totp_nuovo", None)
            session["2fa"] = True
            flash("Verifica in due passaggi attivata: d'ora in poi all'accesso serve il codice dell'app.", "ok")
            return redirect(url_for("impostazioni"))
        if utente["totp"]:
            return render_template("due_passaggi.html", attiva=True)
        segreto = session.get("totp_nuovo") or totp.nuovo_segreto()
        session["totp_nuovo"] = segreto
        return render_template("due_passaggi.html", attiva=False, segreto=segreto,
                               qr=_qr(totp.indirizzo(segreto, utente["nome"])))


def _qr(testo: str) -> str:
    """QR code come immagine data: (vuoto se manca la libreria: resta il codice da scrivere a mano)."""
    try:
        import segno
    except ImportError:
        return ""
    return segno.make(testo, error="m").svg_data_uri(scale=5, border=2)


def crea_utente(nome: str, password: str) -> None:
    conn = archivio.connessione()
    conn.execute("INSERT INTO utenti (nome, password) VALUES (?, ?) ON CONFLICT(nome) DO UPDATE SET "
                 "password = excluded.password", (nome, generate_password_hash(password)))
    conn.commit()
