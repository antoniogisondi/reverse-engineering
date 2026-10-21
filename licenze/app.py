"""Gestionale web delle licenze SicurCantiere: clienti, licenze, rinnovi, pagamenti e scadenze.

Gira sul server dell'ufficio ed è pensato per la rete interna: chi lo apre dal browser deve
accedere con nome e password. Qui si firmano le licenze con la chiave privata, che non lascia
mai il server; i programmi dei clienti verificano il codice senza collegarsi a niente.
"""

from __future__ import annotations

import csv
import io
import secrets
from datetime import date, timedelta
from functools import wraps

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from licenze import archivio
from sicurcantiere import licenza

GIORNI_AVVISO = 30
METODI_PAGAMENTO = ("Bonifico", "Carta", "PayPal", "Contanti", "Altro")


def crea_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = archivio.segreto_sessione()
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)

    @app.context_processor
    def comuni():
        return {"piani": licenza.PIANI, "token": _token(), "oggi": date.today().isoformat(),
                "utente": session.get("utente")}

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


def _rotte(app: Flask) -> None:
    @app.route("/accesso", methods=["GET", "POST"])
    def accesso():
        if request.method == "POST":
            conn = _db()
            utente = conn.execute("SELECT * FROM utenti WHERE nome = ?", (request.form.get("nome", ""),)).fetchone()
            if utente and check_password_hash(utente["password"], request.form.get("password", "")):
                session.clear()
                session["utente"] = utente["nome"]
                session["token"] = secrets.token_urlsafe(24)
                session.permanent = True
                prossima = request.args.get("prossima", "")
                return redirect(prossima if prossima.startswith("/") and not prossima.startswith("//")
                                else url_for("cruscotto"))
            flash("Nome o password non corretti.", "errore")
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


def crea_utente(nome: str, password: str) -> None:
    conn = archivio.connessione()
    conn.execute("INSERT INTO utenti (nome, password) VALUES (?, ?) ON CONFLICT(nome) DO UPDATE SET "
                 "password = excluded.password", (nome, generate_password_hash(password)))
    conn.commit()
