#!/usr/bin/env bash
# Installa o aggiorna il gestionale delle licenze SicurCantiere su Debian 12 (container LXC di Proxmox).
# Da eseguire come root dalla cartella principale del repository:  bash licenze/installa.sh
# Si può rilanciare per aggiornare: dati, chiave e utenti restano.
set -euo pipefail

APP=/opt/sicurcantiere-licenze
DATI=/var/lib/sicurcantiere-licenze
UTENTE=sclicenze
PORTA=8443

if [ "$(id -u)" -ne 0 ]; then echo "Eseguire come root."; exit 1; fi
if [ ! -f licenze/app.py ] || [ ! -f sicurcantiere/licenza.py ]; then
    echo "Eseguire dalla cartella principale del repository (quella con licenze/ e sicurcantiere/)."; exit 1
fi

echo "== Pacchetti di sistema"
apt-get update -qq
apt-get install -y -qq python3 python3-venv openssl >/dev/null

echo "== Utente di servizio e cartelle"
id "$UTENTE" >/dev/null 2>&1 || useradd --system --home "$APP" --shell /usr/sbin/nologin "$UTENTE"
mkdir -p "$APP/codice/sicurcantiere" "$DATI"
cp -r licenze "$APP/codice/"
cp sicurcantiere/__init__.py sicurcantiere/licenza.py "$APP/codice/sicurcantiere/"
chown -R root:root "$APP/codice"
chown "$UTENTE:$UTENTE" "$DATI"
chmod 700 "$DATI"

echo "== Ambiente Python"
[ -d "$APP/venv" ] || python3 -m venv "$APP/venv"
"$APP/venv/bin/pip" install -q --upgrade pip
"$APP/venv/bin/pip" install -q -r licenze/requirements.txt

# Comandi del gestionale come utente di servizio (vedi licenze/__main__.py).
esegui() {
    runuser -u "$UTENTE" -- env SICURCANTIERE_LICENZE_DATI="$DATI" PYTHONPATH="$APP/codice" \
        "$APP/venv/bin/python" -m licenze "$@"
}

echo "== Certificato HTTPS per la rete interna"
if [ ! -f "$DATI/certificato.pem" ]; then
    openssl req -x509 -newkey rsa:2048 -nodes -days 3650 -subj "/CN=$(hostname)" \
        -keyout "$DATI/certificato.key" -out "$DATI/certificato.pem" 2>/dev/null
    chown "$UTENTE:$UTENTE" "$DATI"/certificato.*
    chmod 600 "$DATI/certificato.key"
fi

echo "== Chiave di firma delle licenze"
if [ ! -f "$DATI/chiave_privata.pem" ]; then
    esegui genera-chiave
    NUOVA_CHIAVE=1
else
    echo "Chiave già presente (non viene toccata)."
    NUOVA_CHIAVE=0
fi

echo "== Servizio"
cat > /etc/systemd/system/sicurcantiere-licenze.service <<UNIT
[Unit]
Description=Gestionale licenze SicurCantiere
After=network.target

[Service]
User=$UTENTE
Group=$UTENTE
Environment=SICURCANTIERE_LICENZE_DATI=$DATI
Environment=PYTHONPATH=$APP/codice
ExecStart=$APP/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:$PORTA \\
    --certfile $DATI/certificato.pem --keyfile $DATI/certificato.key licenze.wsgi:app
Restart=on-failure
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$DATI

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now sicurcantiere-licenze
systemctl restart sicurcantiere-licenze

if ! runuser -u "$UTENTE" -- env SICURCANTIERE_LICENZE_DATI="$DATI" PYTHONPATH="$APP/codice" \
        "$APP/venv/bin/python" -c "from licenze import archivio; import sys; \
sys.exit(0 if archivio.connessione().execute('SELECT COUNT(*) FROM utenti').fetchone()[0] else 1)"; then
    echo "== Primo utente del gestionale"
    read -r -p "Nome utente: " NOME
    esegui crea-utente "$NOME"
fi

IP=$(hostname -I | awk '{print $1}')
echo
echo "Fatto. Gestionale: https://$IP:$PORTA  (al primo accesso il browser avvisa del certificato: è normale)"
if [ "$NUOVA_CHIAVE" = 1 ]; then
    echo "IMPORTANTE: copia $DATI/chiave_privata.pem in un posto sicuro e manda solo la chiave pubblica."
fi
