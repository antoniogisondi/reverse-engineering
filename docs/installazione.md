# Installare SicurCantiere su Windows

1. Scaricare `SicurCantiere-<versione>-setup.exe` dalla pagina della versione (sezione *Assets*).
2. Fare doppio clic sul file. Il programma non ha una firma digitale a pagamento, quindi
   Windows può mostrare «Windows ha protetto il PC»: fare clic su **Ulteriori informazioni**
   e poi su **Esegui comunque**.
3. Seguire l'installazione: lasciare spuntati «Crea le icone sul desktop» e «Apri i file dei
   cantieri con doppio clic». Si possono installare tutti i programmi (POS, PSC, PiMUS) o solo
   il POS.
4. Alla fine si apre **SicurCantiere POS**.

## Primo POS

1. *File > Nuovo cantiere...* e scegliere dove salvare il cantiere (file `.spo`): i dati si salvano da soli
   a ogni modifica; il pulsante **Salva** (Ctrl+S) conferma anche il campo in modifica.
2. Compilare le pagine dall'alto in basso: Cantiere, Committente e CSE, Impresa e lavoratori,
   Lavorazioni e rischi (pulsante **Importa da archivio...**), Valutazioni specifiche.
3. Nella pagina **POS e controlli** correggere gli errori segnalati e premere **Genera POS**:
   il programma crea il file Word, da rileggere e firmare.

Le valutazioni dei rischi specifici (movimentazione dei carichi, rumore, vibrazioni...) vengono
create da sole in base ai rischi delle lavorazioni e restano «da eseguire» finché non se ne
inseriscono i parametri.

## Assistente AI (facoltativo)

Serve una chiave API di DeepSeek (platform.deepseek.com). Inserirla in
*Strumenti > Impostazioni assistente AI*. La chiave resta solo su questo computer: non va
scritta in email o chat.

## Dove sono i dati

- I cantieri: nei file `.spo` salvati dove si è scelto.
- Le copie di sicurezza automatiche (ultime 5 per cantiere):
  `%APPDATA%\SicurCantiere\copie di sicurezza`.
- L'archivio personale di anagrafiche e lavorazioni: `%APPDATA%\SicurCantiere\archivio.db`.

Per aggiornare il programma basta installare la versione nuova sopra quella vecchia: cantieri e
archivio restano.
