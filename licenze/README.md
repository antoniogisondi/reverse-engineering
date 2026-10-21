# Gestionale delle licenze SicurCantiere

Pagina web interna per gestire **clienti, licenze, rinnovi, pagamenti e scadenze**. Gira sul
server Proxmox dell'ufficio e si apre dal browser di qualsiasi PC della rete, senza installare
niente sui PC.

Qui si **firmano le licenze**: la chiave privata resta solo sul server. I programmi dei clienti
contengono la chiave pubblica e verificano il codice da soli, senza collegarsi al server: il
gestionale non va quindi esposto su internet.

## 1. Creare il container su Proxmox

1. **Scaricare il modello Debian 12.** Nell'interfaccia di Proxmox: nodo > `local` >
   *CT Templates* > *Templates* > `debian-12-standard` > *Download*.
2. **Creare il container.** In alto a destra *Create CT*:
   - *General*: hostname `sicurcantiere-licenze`, una password di root robusta, lasciare
     spuntato *Unprivileged container*.
   - *Template*: `debian-12-standard`.
   - *Disks*: 8 GB.
   - *CPU*: 1 core. *Memory*: 512 MB (swap 512 MB).
   - *Network*: IPv4 **statico** nella rete dell'ufficio (per esempio `192.168.1.50/24`, con il
     gateway del router), così l'indirizzo non cambia.
   - *DNS*: quelli predefiniti.
   - Alla fine spuntare *Start after created*.
3. **Avvio automatico.** Container > *Options* > *Start at boot* = Yes.

## 2. Installare il gestionale

Dalla *Console* del container, come root:

```bash
apt update && apt full-upgrade -y && apt install -y git
git clone https://github.com/antoniogisondi/sicurcantiere.git
cd sicurcantiere
git checkout claude/dazzling-pasteur-upt4ur   # finché il lavoro non è sul ramo principale
bash licenze/installa.sh
```

Lo script:
- installa Python;
- crea l'utente di servizio e un certificato HTTPS per la rete interna;
- **genera la chiave di firma**;
- avvia il servizio;
- chiede nome e password del primo utente (almeno 10 caratteri).

Alla fine stampa l'indirizzo, per esempio `https://192.168.1.50:8443`. Al primo accesso il browser
avvisa che il certificato non è riconosciuto: è normale per un server interno. Va accettato
una volta per PC.

Se il repository è privato, `git clone` chiede l'accesso a GitHub. In alternativa si può
copiare la cartella del repository nel container (per esempio con `scp`).

## 3. Due cose da fare subito

1. **Copiare la chiave privata in un posto sicuro.** Il file è
   `/var/lib/sicurcantiere-licenze/chiave_privata.pem`. Va messo su una chiavetta in cassaforte o
   in un gestore di password, mai per email. Se va persa, le licenze già vendute continuano a
   funzionare, ma non se ne possono più emettere di nuove senza distribuire una nuova versione
   del programma.
2. **Mandare la chiave pubblica per il programma.** Si trova nella pagina *Impostazioni* del
   gestionale, oppure si ottiene con:
   ```bash
   runuser -u sclicenze -- env SICURCANTIERE_LICENZE_DATI=/var/lib/sicurcantiere-licenze \
       PYTHONPATH=/opt/sicurcantiere-licenze/codice /opt/sicurcantiere-licenze/venv/bin/python -m licenze chiave-pubblica
   ```
   Va inserita in `sicurcantiere/licenza.py` (`CHIAVE_PUBBLICA`). Da quella versione in poi i
   programmi chiedono la licenza. Prima di pubblicarla, emettere una licenza *senza scadenza*
   per chi usa già il programma.

## 4. Copie di sicurezza

In Proxmox: *Datacenter* > *Backup* > *Add*:
- container `sicurcantiere-licenze`;
- ogni giorno, per esempio alle 21:00;
- modalità *Snapshot*;
- conservare almeno 14 copie.

Meglio se le copie vanno su un disco diverso da quello del server.

## 5. Accesso e sicurezza

- Il gestionale va usato **solo dalla rete dell'ufficio**: non aprire porte sul router. Da fuori
  si usa una VPN (per esempio WireGuard o Tailscale).
- Facoltativo: firewall di Proxmox sul container, che consenta la porta 8443 solo dalla rete
  dell'ufficio.
- Altri utenti si aggiungono con lo stesso comando di sopra, sostituendo `chiave-pubblica`
  con `crea-utente NOME`. Lo stesso comando, con un nome esistente, ne cambia la password.

## 6. Aggiornare il gestionale

```bash
cd sicurcantiere && git pull && bash licenze/installa.sh
```

Dati, chiave e utenti restano.

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
