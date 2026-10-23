# Gestionale delle licenze SicurCantiere

Applicazione web per gestire **clienti, licenze, rinnovi, pagamenti e scadenze**:
- gira su un server dell'ufficio, per esempio una macchina virtuale Ubuntu sul NAS;
- si apre dal browser, anche da fuori ufficio, senza installare nulla sui PC.

Qui si **firmano le licenze**: la chiave privata resta solo sul server. I programmi dei clienti
contengono la chiave pubblica e verificano il codice da soli, senza collegarsi al server. Anche se il
gestionale non è raggiungibile, quindi, i programmi continuano a funzionare.

## 1. Preparare la macchina virtuale

È sufficiente una VM **Ubuntu Server 22.04 o 24.04** (sul NAS dell'ufficio) oppure un container
Debian 12 su Proxmox. Bastano 1 CPU, 1 GB di RAM e 10 GB di disco.

- **Indirizzo fisso nella rete dell'ufficio** (per esempio `192.168.1.50`): si imposta nel router
  (DHCP statico/prenotazione per la VM) oppure in Ubuntu con netplan.
- **Avvio automatico** della VM quando si accende il NAS (opzione nelle impostazioni della VM).
- Durante l'installazione di Ubuntu selezionare **OpenSSH server**, per collegarsi dal PC con
  `ssh utente@192.168.1.50`.

## 2. Accesso da internet: dominio e router

Per aprire il gestionale da fuori ufficio servono tre cose.

1. **Un nome a dominio**, per esempio `licenze.tuodominio.it`:
   - se si dispone già di un dominio, si aggiunge un record DNS di tipo **A** con l'IP pubblico
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

Collegarsi alla VM (console o `ssh`):

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
- chiede nome e password del primo utente (almeno 10 caratteri; è consigliata una frase lunga).

Alla fine il gestionale è su `https://licenze.tuodominio.it`, da qualsiasi PC o telefono.

Per usarlo **solo nella rete dell'ufficio** si lancia lo script senza dominio
(`sudo bash licenze/installa.sh`). Si apre su `https://IP:8443`, con un certificato interno che il
browser chiede di accettare una volta.

Se il repository è privato, `git clone` chiede l'accesso a GitHub. In alternativa si copia la
cartella del repository sulla VM, per esempio con `scp -r sicurcantiere utente@192.168.1.50:`.

## 4. Operazioni da eseguire subito

1. **Attivare la verifica in due passaggi.** Va fatto per ogni utente, in *Impostazioni >
   Verifica in due passaggi*:
   - si inquadra il QR code con un'app di autenticazione (Google Authenticator, Microsoft
     Authenticator, Aegis...);
   - si conferma con il primo codice.

   Da quel momento per accedere servono la password **e** il codice del telefono. Finché non è
   attiva, il gestionale lo ricorda in ogni pagina. Se il telefono va perso, dalla VM si
   disattiva con `togli-2fa` (vedi la sezione 6).
2. **Copiare la chiave privata in un posto sicuro.**
   - Il file è `/var/lib/sicurcantiere-licenze/chiave_privata.pem` e si copia sul PC con
     `scp`. Va messo su una chiavetta in cassaforte o in un gestore di password, mai per email.
   - Se va persa, le licenze già vendute continuano a funzionare, ma non se ne possono più
     emettere di nuove senza distribuire una nuova versione del programma.
3. **Inserire la chiave pubblica nel programma.**
   - Si trova nella pagina *Impostazioni*.
   - Va inserita in `sicurcantiere/licenza.py` (`CHIAVE_PUBBLICA`). Da quella versione in poi i
     programmi chiedono la licenza.
   - Prima di pubblicarla, emettere una licenza *senza scadenza* per chi usa già il programma.

## 5. Copie di sicurezza

- **Dal NAS**: copia (snapshot/backup) della VM ogni giorno, conservandone almeno 14. Sui NAS
  Synology si usa *Virtual Machine Manager > Protezione*, sui QNAP *Virtualization Station >
  Snapshot/Backup*. È consigliabile conservare una copia anche fuori dal NAS (disco USB o cloud).
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
  - dopo 5 tentativi errati su un nome utente (o 20 dallo stesso indirizzo) l'accesso si
    blocca per 15 minuti;
  - la sessione dura al massimo 8 ore;
  - il traffico è sempre cifrato (HTTPS).
- **Utenti.** Gli utenti si aggiungono, e la loro password si cambia, dalla VM:
  ```bash
  sudo runuser -u sclicenze -- env SICURCANTIERE_LICENZE_DATI=/var/lib/sicurcantiere-licenze \
      PYTHONPATH=/opt/sicurcantiere-licenze/codice /opt/sicurcantiere-licenze/venv/bin/python -m licenze crea-utente NOME
  ```
  Con `togli-2fa NOME` al posto di `crea-utente NOME` si disattiva la verifica in due passaggi.
  Serve quando un telefono va perso.
- **Ubuntu** installa da solo gli aggiornamenti di sicurezza. Periodicamente è opportuno
  eseguire `sudo apt full-upgrade` e riavviare.
- **Controlli in caso di problemi:**
  - `systemctl status sicurcantiere-licenze caddy`;
  - `journalctl -u caddy`, per gli errori del certificato (di solito DNS o porte non inoltrate).

## 7. In alternativa: senza aprire porte (Cloudflare Tunnel)

È utile se il router non consente l'inoltro delle porte (CGNAT) o se non si vogliono aprire porte.

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

## Assistente AI incluso nelle licenze (server ponte)

Con il gestionale si installa un secondo servizio, `sicurcantiere-licenze-ai`: il **server ponte**
dell'assistente AI.
- **Come funziona**: i programmi dei clienti non hanno chiavi dei fornitori AI. Mandano la richiesta
  al server insieme al codice di licenza. Il server controlla licenza e credito, la inoltra al
  fornitore con le chiavi dell'ufficio e registra il consumo.
- **Cosa è pubblico**: il ponte è l'unica parte raggiungibile da internet. Il gestionale resta
  privato.

### Attivazione

1. **Chiavi dei fornitori**:
   ```bash
   sudo nano /etc/sicurcantiere-licenze/ai.env
   ```
   - `SICURCANTIERE_AI_STANDARD_CHIAVE`: chiave DeepSeek (motore Standard, tutti i piani);
   - `SICURCANTIERE_AI_AVANZATO_CHIAVE`: chiave Anthropic (motore Avanzato con Claude, solo piano
     Studio).

   Poi riavviare il servizio:
   ```bash
   sudo systemctl restart sicurcantiere-licenze-ai
   ```
   Il file è leggibile solo da root e le chiavi non lasciano mai il server.
2. **Pubblicarlo su internet con Tailscale Funnel**: nessun dominio da acquistare e nessuna porta da
   aprire sul router.
   ```bash
   sudo tailscale funnel --bg 8100
   tailscale funnel status
   ```
   - La prima volta Tailscale chiede di abilitare Funnel con un link: aprirlo e confermare.
   - L'indirizzo mostrato (`https://vm-sicurcantiere.<nome>.ts.net`) va inserito nel programma
     (`SERVER_AI` in `sicurcantiere/ai.py`). Da quella versione i clienti con licenza hanno
     l'assistente senza chiavi.
   - Funnel pubblica solo la porta 8100 del ponte: il gestionale sulla 8443 resta visibile solo a
     chi è nella rete Tailscale.
3. **Prova**:
   ```bash
   curl -s -X POST https://vm-sicurcantiere.<nome>.ts.net/api/ai/stato -H 'Content-Type: application/json' -d '{"licenza":"SC1-..."}'
   ```

### Quote e ricariche

| Piano | Crediti al mese | Motori |
| --- | --- | --- |
| POS, PSC, PiMUS | 1,5 milioni | Standard |
| Completo | 3 milioni | Standard |
| Studio | 8 milioni (per tutte le postazioni) | Standard e Avanzato |

- **Crediti**: un credito corrisponde a un token con il motore Standard; con l'Avanzato (Claude)
  ogni token vale 8 crediti.
- **Rinnovo della quota**: la quota si rinnova il primo giorno di ogni mese ed è calcolata per cliente.
- **Tetto giornaliero**: per prevenire gli abusi, in un giorno si può usare al massimo il 30%
  della quota mensile.
- **Ricariche**: si aggiungono dalla scheda del cliente (*Aggiungi la ricarica*), non scadono e si
  usano dopo la quota del mese.
- **Consumi**: per mese e per motore, nella scheda del cliente. Il totale del mese è nel
  cruscotto.
- **Credito esaurito o licenza scaduta**: l'assistente si ferma, ma il resto del programma continua a
  funzionare.

## Come funziona una licenza

- **Emissione.** Nella scheda del cliente si sceglie *Emetti una licenza*: piano (POS, PSC,
  PiMUS, Completo, Studio), scadenza, postazioni e prezzo. Il gestionale crea e firma il codice
  `SC1-...` e prepara il testo dell'email da inviare al cliente.
- **Attivazione.** Il cliente incolla il codice in *Aiuto > Licenza...*.
- **Rinnovo.** *Rinnova per un anno* emette un nuovo codice: la nuova scadenza decorre dalla
  precedente, oppure da oggi se è già passata.
- **Scadenza.** Il programma continua a funzionare, ma non propone gli aggiornamenti pubblicati
  dopo la scadenza e segnala il rinnovo.
- **Senza licenza.** Il programma funziona in prova per 30 giorni, con un solo cantiere.
- **Annullamento.** Una licenza segnata come annullata resta tale solo nel registro: un codice
  già consegnato non si può revocare a distanza, perché il programma non si collega al server.

## Attivazioni dei PC (limite di postazioni)

Il server pubblico (lo stesso del ponte AI, porta 8100 pubblicata con Tailscale Funnel) controlla
su quanti PC è attiva ogni licenza. I programmi lo useranno dalla versione che contiene le nuove
finestre di attivazione; fino ad allora resta valido quanto descritto sopra.

- **Postazioni.** Una licenza per N postazioni si attiva su N PC. Il PC in più (con 1 postazione
  il secondo, con 3 il quarto, e così via) viene rifiutato: il programma mostra «La licenza è già
  attiva su N PC su N» con l'elenco dei PC (nome e ultimo utilizzo) e permette di disattivarne uno.
  Ogni rifiuto resta nel registro (`eventi_licenza`, esito `posti_esauriti`): serve a capire chi ha
  bisogno di più postazioni o chi prova a condividere il codice.
- **Stesso PC.** Reinstallare il programma o Windows, cambiare il disco o il nome del PC non
  consuma un posto: il PC è riconosciuto se coincidono 2 dei 3 elementi dell'impronta (codice di
  Windows, scheda madre, nome). Al server arrivano solo hash, mai i dati del PC.
- **Trasferimenti.** Liberare un PC è sempre possibile; in 30 giorni si possono attivare al massimo
  N PC nuovi più 2, così un posto non si fa «girare» tra più PC. Oltre il limite il cliente deve
  contattare l'assistenza.
- **Rinnovi.** Il codice nuovo del rinnovo appartiene alla stessa licenza: i PC già attivati
  restano validi, senza riattivarli.
- **Certificato.** A ogni avvio il programma rinnova in sottofondo il proprio certificato, valido
  14 giorni: senza internet il programma funziona fino alla fine del certificato, poi passa in sola
  lettura (i documenti già fatti si aprono, si stampano e si esportano sempre).
- **Annullamento.** Con le attivazioni, una licenza annullata nel gestionale si blocca davvero: al
  primo collegamento il programma passa in sola lettura.
- **Macchine virtuali copiate.** Se lo stesso PC si collega da due reti lontane a pochi minuti di
  distanza, il PC viene segnato come sospetto (colonna `sospetto`) e l'evento va nel registro.
- **Limiti contro i tentativi.** 10 codici sbagliati in un'ora dallo stesso indirizzo bloccano
  quell'indirizzo per un'ora; ogni licenza ha al massimo 30 richieste l'ora.

Comandi utili sulla VM (nella cartella del codice, con l'utente del servizio):

```bash
python -m licenze pc SC-2026-0012                     # PC attivi della licenza
python -m licenze attivazione-offline richiesta.json  # cliente senza internet: crea richiesta.attivazione
python -m licenze chiave-servizio                     # nuova chiave di servizio (vedi sotto)
```

**Attivazione senza internet.** Il cliente salva dal programma il file di richiesta e lo manda
all'assistenza; il comando sopra crea il file di attivazione da rimandargli. Vale 90 giorni (un file
offline non si può revocare), poi serve un nuovo file o un collegamento.

**Chiavi.** La chiave delle licenze (`chiave_privata.pem`, la «radice») firma ogni 6 mesi una chiave
di servizio (`servizio.json`), con cui il server firma i certificati dei PC. Sulla VM attuale la
chiave di servizio si rinnova da sola. Se il server delle attivazioni andrà su una macchina diversa
dal gestionale, su quella si copia **solo** `servizio.json` (da rinnovare con il comando sopra
almeno ogni 6 mesi), mai `chiave_privata.pem`: così, anche se il server pubblico venisse violato,
la chiave delle licenze resta al sicuro.

**Trasloco sul server Proxmox.** Basta reinstallare con `installa.sh` sulla nuova macchina e copiare
la cartella `/var/lib/sicurcantiere-licenze` (database, chiavi): PC attivati, registro e licenze
passano così come sono. Se cambia l'indirizzo pubblico, va aggiornato nel programma prima di
spegnere la VM vecchia.
