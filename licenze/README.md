# Gestionale delle licenze SicurCantiere

Pagina web per gestire **clienti, licenze, rinnovi, pagamenti e scadenze**:
- gira su un server dell'ufficio, per esempio una macchina virtuale Ubuntu sul NAS;
- si apre dal browser, anche da fuori ufficio, senza installare niente sui PC.

Qui si **firmano le licenze**: la chiave privata resta solo sul server. I programmi dei clienti
contengono la chiave pubblica e verificano il codice da soli, senza collegarsi al server. Se il
gestionale non è raggiungibile, i programmi continuano quindi a funzionare.

## 1. Preparare la macchina virtuale

Va bene una VM **Ubuntu Server 22.04 o 24.04** (sul NAS dell'ufficio) oppure un container
Debian 12 su Proxmox. Bastano 1 CPU, 1 GB di RAM e 10 GB di disco.

- **Indirizzo fisso nella rete dell'ufficio** (per esempio `192.168.1.50`): si imposta nel router
  (DHCP statico/prenotazione per la VM) oppure in Ubuntu con netplan.
- **Avvio automatico** della VM quando si accende il NAS (opzione nelle impostazioni della VM).
- In installazione di Ubuntu spuntare **OpenSSH server**, per collegarsi dal PC con
  `ssh utente@192.168.1.50`.

## 2. Accesso da internet: dominio e router

Per aprire il gestionale da fuori ufficio servono tre cose.

1. **Un nome a dominio**, per esempio `licenze.tuodominio.it`:
   - se c'è già un dominio, si aggiunge un record DNS di tipo **A** con l'IP pubblico
     dell'ufficio;
   - se l'IP pubblico cambia (linee di casa e piccoli uffici), serve un DNS dinamico. Lo
     gestiscono molti router (Impostazioni > DDNS) oppure il NAS stesso: per esempio Synology
     *DDNS* o QNAP *myQNAPcloud*. Si può usare anche un servizio come DuckDNS. In questo caso si
     crea un CNAME `licenze.tuodominio.it` che punta al nome DDNS, oppure si usa direttamente il
     nome DDNS.
2. **Inoltro delle porte sul router** verso l'IP della VM:
   - TCP **443** (HTTPS);
   - TCP **80**, che serve solo a ottenere e rinnovare il certificato;
   - **nessun'altra porta**: SSH e l'interfaccia del NAS restano chiuse verso internet.
3. **Controllo del collegamento.** Alcuni operatori (soprattutto 4G/5G e FWA) non danno un IP
   pubblico (CGNAT): in quel caso l'inoltro delle porte non funziona. Si vede confrontando l'IP
   WAN del router con quello mostrato da un sito come «mio ip». Se sono diversi c'è il CGNAT, e
   le soluzioni sono due:
   - chiedere all'operatore un IP pubblico;
   - usare *Cloudflare Tunnel*, che non richiede porte aperte (vedi la sezione 7).

## 3. Installare il gestionale

Collegati alla VM (console o `ssh`):

```bash
sudo apt update && sudo apt full-upgrade -y && sudo apt install -y git
git clone https://github.com/antoniogisondi/sicurcantiere.git
cd sicurcantiere
git checkout claude/dazzling-pasteur-upt4ur   # finché il lavoro non è sul ramo principale
sudo bash licenze/installa.sh licenze.tuodominio.it
```

Lo script:
- installa Python e gli aggiornamenti di sicurezza automatici di Ubuntu;
- crea l'utente di servizio e **genera la chiave di firma**;
- installa **Caddy**, che ottiene da solo il certificato HTTPS valido (Let's Encrypt) e lo
  rinnova;
- avvia il gestionale, che ascolta solo dietro Caddy e non è raggiungibile direttamente;
- attiva il firewall (`ufw`), che lascia passare solo SSH e le porte 80/443;
- chiede nome e password del primo utente (almeno 10 caratteri: meglio una frase lunga).

Alla fine il gestionale è su `https://licenze.tuodominio.it`, da qualsiasi PC o telefono.

Per usarlo **solo nella rete dell'ufficio** si lancia lo script senza dominio
(`sudo bash licenze/installa.sh`). Si apre su `https://IP:8443`, con un certificato interno che il
browser chiede di accettare una volta.

Se il repository è privato, `git clone` chiede l'accesso a GitHub. In alternativa si copia la
cartella del repository sulla VM, per esempio con `scp -r sicurcantiere utente@192.168.1.50:`.

## 4. Tre cose da fare subito

1. **Attivare la verifica in due passaggi.** Va fatto per ogni utente, in *Impostazioni >
   Verifica in due passaggi*:
   - si inquadra il QR code con un'app di autenticazione (Google Authenticator, Microsoft
     Authenticator, Aegis…);
   - si conferma con il primo codice.

   Da quel momento per entrare servono la password **e** il codice del telefono. Finché non è
   attiva, il gestionale lo ricorda in ogni pagina. Se il telefono va perso, dalla VM si
   disattiva con `togli-2fa` (vedi la sezione 6).
2. **Copiare la chiave privata in un posto sicuro.**
   - Il file è `/var/lib/sicurcantiere-licenze/chiave_privata.pem` e si copia sul PC con
     `scp`. Va messo su una chiavetta in cassaforte o in un gestore di password, mai per email.
   - Se va persa, le licenze già vendute continuano a funzionare, ma non se ne possono più
     emettere di nuove senza distribuire una nuova versione del programma.
3. **Mandare la chiave pubblica per il programma.**
   - Si trova nella pagina *Impostazioni*.
   - Va inserita in `sicurcantiere/licenza.py` (`CHIAVE_PUBBLICA`). Da quella versione in poi i
     programmi chiedono la licenza.
   - Prima di pubblicarla, emettere una licenza *senza scadenza* per chi usa già il programma.

## 5. Copie di sicurezza

- **Dal NAS**: copia (snapshot/backup) della VM ogni giorno, conservandone almeno 14. Sui NAS
  Synology si usa *Virtual Machine Manager > Protezione*, sui QNAP *Virtualization Station >
  Snapshot/Backup*. Meglio se una copia va anche fuori dal NAS (disco USB o cloud).
- **Solo i dati**: sono tutti in `/var/lib/sicurcantiere-licenze` (database `licenze.db` e
  chiave). Per esempio:
  ```bash
  sudo tar czf licenze-$(date +%F).tgz -C /var/lib sicurcantiere-licenze
  ```
  L'archivio contiene la chiave privata, quindi va custodito con la stessa cura.

## 6. Sicurezza e manutenzione

Dato che il gestionale è raggiungibile da internet:

- **Protezioni del gestionale:**
  - accesso con password e codice del telefono;
  - dopo 5 tentativi sbagliati su un nome utente (o 20 dallo stesso indirizzo) l'accesso si
    blocca per 15 minuti;
  - la sessione dura al massimo 8 ore;
  - il traffico è sempre cifrato (HTTPS).
- **Utenti.** Si aggiungono o si cambia loro la password dalla VM:
  ```bash
  sudo runuser -u sclicenze -- env SICURCANTIERE_LICENZE_DATI=/var/lib/sicurcantiere-licenze \
      PYTHONPATH=/opt/sicurcantiere-licenze/codice /opt/sicurcantiere-licenze/venv/bin/python -m licenze crea-utente NOME
  ```
  Con `togli-2fa NOME` al posto di `crea-utente NOME` si disattiva la verifica in due passaggi.
  Serve quando un telefono va perso.
- **Ubuntu** installa da solo gli aggiornamenti di sicurezza. Ogni tanto conviene un
  `sudo apt full-upgrade` e un riavvio.
- **Controlli in caso di problemi:**
  - `systemctl status sicurcantiere-licenze caddy`;
  - `journalctl -u caddy`, per gli errori del certificato (di solito DNS o porte non inoltrate).

## 7. In alternativa: senza aprire porte (Cloudflare Tunnel)

Serve se il router non permette l'inoltro delle porte (CGNAT) o se non si vogliono aprire.

1. Il dominio va gestito da Cloudflare (piano gratuito).
2. Si installa il gestionale **senza dominio** (`sudo bash licenze/installa.sh`).
3. Si installa `cloudflared` sulla VM e si crea un tunnel che porta `licenze.tuodominio.it` a
   `https://localhost:8443`, con l'opzione *No TLS Verify* (il certificato interno è
   autofirmato).
4. Si può aggiungere *Cloudflare Access*, che chiede un codice via email prima ancora di
   mostrare la pagina.

La verifica in due passaggi del gestionale va attivata comunque.

## 8. Aggiornare il gestionale

```bash
cd sicurcantiere && git pull && sudo bash licenze/installa.sh
```

Il dominio scelto all'installazione viene ricordato. Dati, chiave e utenti restano.

## Come funziona una licenza

- **Emissione.** Nella scheda del cliente si sceglie *Emetti una licenza*: piano (POS, PSC,
  PiMUS, Completo, Studio), scadenza, postazioni e prezzo. Il gestionale crea e firma il codice
  `SC1-...` e prepara il testo dell'email da mandare al cliente.
- **Attivazione.** Il cliente incolla il codice in *Aiuto > Licenza*.
- **Rinnovo.** *Rinnova per un anno* emette un nuovo codice: la nuova scadenza parte dalla
  vecchia, oppure da oggi se è già passata.
- **Scadenza.** Il programma continua a funzionare, ma non propone gli aggiornamenti pubblicati
  dopo la scadenza e segnala il rinnovo.
- **Senza licenza.** C'è la prova di 30 giorni con un solo cantiere.
- **Annullamento.** Una licenza segnata come annullata resta tale solo nel registro: un codice
  già consegnato non si può revocare a distanza, perché il programma non si collega al server.
