#!/usr/bin/env bash
# Installa o aggiorna il gestionale delle licenze SicurCantiere su Ubuntu Server 22.04/24.04 o Debian 12
# (macchina virtuale sul NAS, container LXC di Proxmox...). Da eseguire come root dalla cartella
# principale del repository:
#
#   bash licenze/installa.sh                          solo rete dell'ufficio: https://IP:8443
#   bash licenze/installa.sh licenze.tuodominio.it    anche da internet: https://licenze.tuodominio.it
#
# Con il dominio installa Caddy, che ottiene da solo il certificato HTTPS (Let's Encrypt) e lo
# rinnova; il gestionale ascolta solo in locale dietro Caddy. Il dominio scelto viene ricordato:
# per aggiornare basta rilanciare lo script senza argomenti. Dati, chiave e utenti restano.
set -euo pipefail

APP=/opt/sicurcantiere-licenze
DATI=/var/lib/sicurcantiere-licenze
CONF=/etc/sicurcantiere-licenze
UTENTE=sclicenze
PORTA=8443          # solo rete interna
PORTA_LOCALE=8000   # dietro Caddy
PORTA_AI=8100       # server ponte dell'assistente AI (solo in locale: si pubblica con Tailscale Funnel)

if [ "$(id -u)" -ne 0 ]; then echo "Eseguire come root (sudo bash licenze/installa.sh)."; exit 1; fi
if [ ! -f licenze/app.py ] || [ ! -f sicurcantiere/licenza.py ]; then
    echo "Eseguire dalla cartella principale del repository (quella con licenze/ e sicurcantiere/)."; exit 1
fi
. /etc/os-release
case "${ID:-}" in
    ubuntu|debian) ;;
    *) echo "Sistema non previsto (${PRETTY_NAME:-sconosciuto}): servono Ubuntu o Debian."; exit 1 ;;
esac

mkdir -p "$CONF"
DOMINIO="${1:-${DOMINIO:-}}"
if [ -z "$DOMINIO" ] && [ -f "$CONF/dominio" ]; then DOMINIO=$(cat "$CONF/dominio"); fi
if [ -n "$DOMINIO" ]; then
    if ! [[ "$DOMINIO" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}$ ]]; then
        echo "Dominio non valido: $DOMINIO (esempio: licenze.tuodominio.it)"; exit 1
    fi
    echo "$DOMINIO" > "$CONF/dominio"
fi

echo "== Pacchetti di sistema (${PRETTY_NAME})"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-venv openssl unattended-upgrades >/dev/null
# Aggiornamenti di sicurezza automatici del sistema.
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'APT'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT

echo "== Utente di servizio e cartelle"
id "$UTENTE" >/dev/null 2>&1 || useradd --system --home "$APP" --shell /usr/sbin/nologin "$UTENTE"
rm -rf "$APP/codice"
mkdir -p "$APP/codice/sicurcantiere" "$DATI"
cp -r licenze "$APP/codice/"
rm -rf "$APP/codice/licenze/__pycache__"
cp sicurcantiere/__init__.py sicurcantiere/licenza.py sicurcantiere/ed25519.py sicurcantiere/ai.py \
    "$APP/codice/sicurcantiere/"
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

echo "== Chiave di firma delle licenze"
if [ ! -f "$DATI/chiave_privata.pem" ]; then
    esegui genera-chiave
    NUOVA_CHIAVE=1
else
    echo "Chiave già presente (non viene toccata)."
    NUOVA_CHIAVE=0
fi

if [ -n "$DOMINIO" ]; then
    echo "== Caddy (HTTPS con certificato Let's Encrypt per $DOMINIO)"
    if [ ! -f /etc/apt/sources.list.d/caddy-stable.list ]; then
        # Archivio ufficiale di Caddy: versione aggiornata anche su Ubuntu 22.04, che non lo ha.
        apt-get install -y -qq curl gnupg >/dev/null
        curl -fsSL https://dl.cloudsmith.io/public/caddy/stable/gpg.key \
            | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
        curl -fsSL https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt \
            > /etc/apt/sources.list.d/caddy-stable.list
        apt-get update -qq
    fi
    apt-get install -y -qq caddy >/dev/null
    cat > /etc/caddy/Caddyfile <<CADDY
# Gestionale licenze SicurCantiere (scritto da licenze/installa.sh)
$DOMINIO {
    encode gzip
    header Strict-Transport-Security "max-age=31536000"
    header -Server
    reverse_proxy 127.0.0.1:$PORTA_LOCALE
}
CADDY
    systemctl enable caddy >/dev/null 2>&1
    systemctl reload-or-restart caddy
    ASCOLTO="--bind 127.0.0.1:$PORTA_LOCALE"
    PROXY=1
else
    echo "== Certificato HTTPS per la rete interna"
    if [ ! -f "$DATI/certificato.pem" ]; then
        openssl req -x509 -newkey rsa:2048 -nodes -days 3650 -subj "/CN=$(hostname)" \
            -keyout "$DATI/certificato.key" -out "$DATI/certificato.pem" 2>/dev/null
        chown "$UTENTE:$UTENTE" "$DATI"/certificato.*
        chmod 600 "$DATI/certificato.key"
    fi
    ASCOLTO="--bind 0.0.0.0:$PORTA --certfile $DATI/certificato.pem --keyfile $DATI/certificato.key"
    PROXY=0
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
Environment=SICURCANTIERE_LICENZE_PROXY=$PROXY
Environment=PYTHONPATH=$APP/codice
ExecStart=$APP/venv/bin/gunicorn --workers 2 $ASCOLTO licenze.wsgi:app
Restart=on-failure
NoNewPrivileges=true
PrivateTmp=true
PrivateDevices=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectControlGroups=true
ReadWritePaths=$DATI
WorkingDirectory=$DATI
Environment=HOME=$DATI

[Install]
WantedBy=multi-user.target
UNIT

echo "== Server ponte dell'assistente AI"
if [ ! -f "$CONF/ai.env" ]; then
    cat > "$CONF/ai.env" <<'AIENV'
# Chiavi dei fornitori AI per l'assistente incluso nelle licenze (SicurCantiere AI).
# Dopo ogni modifica: sudo systemctl restart sicurcantiere-licenze-ai
#
# Motore standard (tutti i piani): DeepSeek o un servizio compatibile, anche ospitato in Europa
# (in quel caso indicare l'indirizzo, il modello e la sede del trattamento).
SICURCANTIERE_AI_STANDARD_CHIAVE=
SICURCANTIERE_AI_STANDARD_MODELLO=deepseek-flash
SICURCANTIERE_AI_STANDARD_URL=
SICURCANTIERE_AI_STANDARD_SEDE=DeepSeek, con trattamento dei dati in Cina
# Lunghezza massima delle risposte (token): i modelli che «ragionano» prima di rispondere ne usano
# molti. Se il fornitore rifiuta il valore, provare 16000 (vuoto = 8000).
SICURCANTIERE_AI_STANDARD_MAX_TOKEN=32000
#
# Motore avanzato (solo piano Studio): Claude di Anthropic.
SICURCANTIERE_AI_AVANZATO_CHIAVE=
SICURCANTIERE_AI_AVANZATO_MODELLO=claude-sonnet-5-5
AIENV
fi
chown root:root "$CONF/ai.env"
chmod 600 "$CONF/ai.env"
cat > /etc/systemd/system/sicurcantiere-licenze-ai.service <<UNIT
[Unit]
Description=Server ponte dell'assistente AI SicurCantiere
After=network.target

[Service]
User=$UTENTE
Group=$UTENTE
Environment=SICURCANTIERE_LICENZE_DATI=$DATI
Environment=PYTHONPATH=$APP/codice
EnvironmentFile=$CONF/ai.env
ExecStart=$APP/venv/bin/gunicorn --workers 3 --timeout 320 --bind 127.0.0.1:$PORTA_AI licenze.wsgi_api:app
Restart=on-failure
NoNewPrivileges=true
PrivateTmp=true
PrivateDevices=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectControlGroups=true
ReadWritePaths=$DATI
WorkingDirectory=$DATI
Environment=HOME=$DATI

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now sicurcantiere-licenze sicurcantiere-licenze-ai
systemctl restart sicurcantiere-licenze sicurcantiere-licenze-ai

if [ -n "$DOMINIO" ] && command -v ufw >/dev/null 2>&1; then
    echo "== Firewall: aperte solo SSH (rete interna) e le porte web 80/443"
    ufw allow OpenSSH >/dev/null
    ufw allow 80/tcp >/dev/null
    ufw allow 443/tcp >/dev/null
    ufw delete allow $PORTA/tcp >/dev/null 2>&1 || true
    ufw --force enable >/dev/null
fi

if ! runuser -u "$UTENTE" -- env SICURCANTIERE_LICENZE_DATI="$DATI" PYTHONPATH="$APP/codice" \
        "$APP/venv/bin/python" -c "from licenze import archivio; import sys; \
sys.exit(0 if archivio.connessione().execute('SELECT COUNT(*) FROM utenti').fetchone()[0] else 1)"; then
    echo "== Primo utente del gestionale"
    read -r -p "Nome utente: " NOME
    esegui crea-utente "$NOME"
fi

echo
if [ -n "$DOMINIO" ]; then
    echo "Fatto. Gestionale: https://$DOMINIO"
    echo "Se non si apre: il dominio deve puntare all'IP pubblico dell'ufficio e il router deve inoltrare"
    echo "le porte 80 e 443 a questa macchina ($(hostname -I | awk '{print $1}')). Controllo: journalctl -u caddy"
    echo "Al primo accesso attivare subito la verifica in due passaggi (Impostazioni)."
else
    echo "Fatto. Gestionale: https://$(hostname -I | awk '{print $1}'):$PORTA  (al primo accesso il browser avvisa del certificato: è normale)"
fi
echo
echo "Assistente AI incluso nelle licenze:"
echo " 1. inserire le chiavi dei fornitori in $CONF/ai.env (sudo nano $CONF/ai.env)"
echo "    e riavviare: sudo systemctl restart sicurcantiere-licenze-ai"
echo " 2. renderlo raggiungibile dai programmi dei clienti (una volta sola):"
echo "    sudo tailscale funnel --bg $PORTA_AI"
echo "    poi mandare l'indirizzo https://...ts.net mostrato da: tailscale funnel status"
if [ "$NUOVA_CHIAVE" = 1 ]; then
    echo "IMPORTANTE: copia $DATI/chiave_privata.pem in un posto sicuro e manda solo la chiave pubblica."
fi
