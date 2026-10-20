"""Fasi di lavoro delle categorie «Opere edili in copertura» (CO) e «Opere edili in facciata» (FA).

Le fasi sostituiscono, con maggiore dettaglio, le voci generiche NC.06, RI.04, RS.03 e RI.05 di
``archivio.py``. Testi redatti per SicurCantiere con parole proprie; vanno sempre verificati e
adattati dal coordinatore al cantiere specifico.

Fonti consultate (solo come riferimento tecnico, nessun testo riprodotto):
- D.Lgs. 81/2008: artt. 105-117 (lavori in quota, priorità delle protezioni collettive, scale,
  sistemi anticaduta, lavori su funi), artt. 122-138 e Allegato XVIII (ponteggi e opere
  provvisionali), art. 148 (lavori speciali su lucernari, tetti e coperture) e interpello
  n. 6/2019 sul suo rapporto con l'art. 111; Titolo IX (agenti chimici e cancerogeni, silice
  cristallina respirabile nell'Allegato XLII dopo il D.Lgs. 44/2020); Allegato IX (distanze dalle
  linee elettriche).
- INAIL, «Esecuzione in sicurezza dei lavori in copertura. Misure di prevenzione e protezione»
  (2017) e manuale della collana Cantieri sui parapetti di sommità dei ponteggi.
- Regione Toscana, D.P.G.R. 18/12/2013 n. 75/R e D.G.R. 178/2014 (elaborato tecnico della
  copertura); analoghe disposizioni di altre regioni sulle misure preventive in copertura.
- Norme tecniche: UNI EN 795:2012 e UNI 11578:2015 (dispositivi di ancoraggio), UNI 11560
  (sistemi di ancoraggio permanenti in copertura), UNI EN 13374 (parapetti provvisori),
  UNI EN 1263-1/2 (reti di sicurezza), UNI 11235 (coperture a verde), UNI/TR 11715 (cappotto),
  UNI EN 1504 (protezione e riparazione del calcestruzzo).
- Reg. (UE) 2020/1149 (restrizione REACH sui diisocianati: formazione obbligatoria degli
  utilizzatori professionali); monografie IARC sulle emissioni di bitume nei lavori di copertura.
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import ATTREZZO, DPI_BASE, EDILIZIA, TUTTE, fase, r

COPERTURA = "Opere edili in copertura"
FACCIATA = "Opere edili in facciata"

NC_RI = ("Nuove costruzioni", "Ristrutturazioni")
RI_RS = ("Ristrutturazioni", "Restauri")

MANCANTI = {
    "Taglierina a filo caldo per pannelli isolanti": (
        ATTREZZO, "Taglio preciso dei pannelli in EPS e XPS del cappotto senza produzione di polvere; "
                  "genera rischi propri (ustioni, fumi di decomposizione del polistirene)."),
}

# DPI ricorrenti
DPI_ANTICADUTA = DPI_BASE + ", imbracatura, cordino con assorbitore"
DPI_RETRATTILE = DPI_BASE + ", imbracatura, dispositivo retrattile"
DPI_SOTTOGOLA = "Casco con sottogola, calzature di sicurezza, guanti, imbracatura, cordino con assorbitore"

# ---------------------------------------------------------------------------------------------
# Rischi riusati
# ---------------------------------------------------------------------------------------------

_CADUTA_BORDO = r(
    "Caduta dall'alto dal bordo della copertura", 3, 4,
    "Protezione collettiva su tutto il perimetro prima di salire sulla copertura (art. 111): ponteggio "
    "perimetrale con parapetto di sommità, montanti oltre l'ultimo impalcato per almeno 1,20 m e "
    "ultimo impalcato in prossimità della linea di gronda, oppure parapetti provvisori UNI EN 13374 "
    "di classe adeguata alla pendenza della falda; dove la protezione collettiva non basta, imbracatura "
    "collegata a linea vita provvisoria o ancoraggi verificati (art. 115); addetti formati e addestrati "
    "all'uso dei DPI di terza categoria (art. 77 c. 5).",
    DPI_ANTICADUTA)

_CADUTA_ATTRAVERSO = r(
    "Caduta dall'alto attraverso la copertura o le aperture", 2, 4,
    "Prima dei lavori accertare la resistenza della struttura e del manto (art. 148); chiudere o "
    "proteggere botole, aperture e vani lucernario con parapetti o coperture fissate e resistenti; reti "
    "di sicurezza UNI EN 1263 o sottopalchi sotto le zone di lavoro; camminare solo su tavole o andatoie "
    "poggiate sulle strutture portanti.",
    DPI_ANTICADUTA)

_CADUTA_FRAGILE = r(
    "Caduta dall'alto per sfondamento di lastre fragili e lucernari", 3, 4,
    "Considerare fragili, fino a prova contraria, lastre in fibrocemento, policarbonato, vetroresina e "
    "lucernari (art. 148); vietato camminarvi sopra: transito solo su andatoie larghe almeno 60 cm "
    "poggiate sugli arcarecci, protezione dei lucernari con griglie o reti fissate e sottostante rete di "
    "sicurezza UNI EN 1263-1 su tutta la zona di lavoro; segnalazione delle superfici non portanti; "
    "imbracatura collegata a linea vita provvisoria quando la protezione collettiva non è completa.",
    DPI_ANTICADUTA)

_CADUTA_MATERIALE = r(
    "Caduta di materiale dall'alto o a livello", 3, 3,
    "Materiali in copertura depositati in piccole quantità, su piani orizzontali e trattenuti contro lo "
    "scivolamento e il vento; tavola fermapiede o mantovana parasassi sul ponteggio; area sottostante "
    "delimitata e interdetta durante i lavori e il sollevamento dei carichi; attrezzi legati o in "
    "apposite borse; nessun lancio di materiali dall'alto.")

_CADUTA_MATERIALE_FACCIATA = r(
    "Caduta di materiale dall'alto o a livello", 3, 3,
    "Ponteggio con tavola fermapiede, teli o reti di facciata e mantovana parasassi sui percorsi "
    "pedonali; delimitazione e segnalazione dell'area a terra, con passaggi coperti per gli accessi "
    "all'edificio; materiali e attrezzi trattenuti sugli impalcati, mai depositati sui bordi; secchi e "
    "sacchi sollevati con argano e ganci con chiusura di sicurezza.")

_CADUTA_PONTEGGIO = r(
    "Caduta dall'alto dal ponteggio", 2, 4,
    "Lavorare solo da impalcati completi con parapetto e fermapiede; impalcato a non più di 20 cm dalla "
    "facciata (art. 138), con mensole o tavole di sporgenza quando lo spessore del rivestimento o del "
    "cappotto aumenta la distanza; nessuna modifica del ponteggio da parte degli addetti: le "
    "trasformazioni le esegue la squadra di montaggio secondo il PiMUS; salita e discesa solo dalle "
    "scale interne del ponteggio.")

_VENTO = r(
    "Microclima: vento, pioggia, ghiaccio e caldo in quota", 3, 2,
    "Consultare le previsioni meteo; sospendere i lavori in copertura con vento forte, pioggia, neve, "
    "ghiaccio o brina e nelle ore più calde in estate; pause all'ombra e acqua a disposizione; "
    "indumenti adeguati alla stagione.",
    DPI_BASE + ", copricapo, indumenti impermeabili")

_SOLE = r(
    "Microclima: esposizione al sole e al caldo", 3, 2,
    "Programmare le lavorazioni più faticose nelle ore fresche; pause all'ombra; acqua a disposizione; "
    "attenzione al calore riflesso da lamiere e superfici chiare; protezione della pelle dai raggi UV.",
    DPI_BASE + ", copricapo, crema protettiva")

_MMC = r(
    "Movimentazione manuale dei carichi", 3, 2,
    "Sollevare in quota con gru, argano o sollevatore e non a mano; carichi oltre 25 kg movimentati in due "
    "o con ausili; pallet scaricati vicino al punto di posa; formazione sulla corretta movimentazione "
    "(art. 169 e Allegato XXXIII).")

_POSTURE = r(
    "Posture incongrue", 3, 2,
    "Alternare le attività; pause programmate; piani di lavoro alla giusta altezza; ginocchiere per "
    "il lavoro in ginocchio sulla falda o sul piano di posa.",
    DPI_BASE + ", ginocchiere")

_TAGLI = r(
    "Punture, tagli e abrasioni", 3, 2,
    "Guanti antitaglio nella manipolazione di lamiere, profili e bordi taglienti; sbavare i tagli; "
    "riporre gli sfridi in contenitori; attrezzi con impugnature integre.",
    DPI_BASE + ", guanti antitaglio")

_SCIVOLAMENTI = r(
    "Scivolamenti e cadute a livello", 3, 2,
    "Superfici di lavoro sgombre da sfridi, teli e imballi; non lavorare su superfici bagnate o con "
    "brina; calzature con suola antiscivolo; percorsi definiti sugli impalcati e in copertura.")

_POLVERI_SILICE = r(
    "Polveri e fibre (silice cristallina respirabile)", 3, 3,
    "Taglio di tegole, laterizi, pietra e lastre ceramiche preferibilmente a umido o con utensili dotati "
    "di aspirazione; tagli fuori dalle zone frequentate e sottovento; pulizia con aspiratore e non a "
    "secco; la lavorazione rientra nell'Allegato XLII (Titolo IX, Capo II): valutazione dell'esposizione "
    "e sorveglianza sanitaria.",
    DPI_BASE + ", facciale filtrante FFP3, occhiali protettivi")

_CEMENTO = r(
    "Rischio chimico (malte, collanti e prodotti a base cementizia)", 3, 2,
    "Consultare le schede di sicurezza; evitare il contatto con la pelle per il potere alcalino e "
    "sensibilizzante del cemento; impasto in zona ventilata versando la polvere con cautela; lavaggio "
    "immediato degli schizzi e acqua pulita a disposizione per gli occhi.",
    DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi, maschera antipolvere")

_SCHIZZI = r(
    "Getti e schizzi", 3, 2,
    "Proteggere gli occhi nelle lavorazioni sopra la testa e nella proiezione dell'impasto; non dirigere "
    "il getto verso altre persone; acqua pulita a disposizione per il lavaggio oculare.",
    DPI_BASE + ", occhiali a maschera")

_ELETTRICO_LINEE = r(
    "Elettrocuzione per vicinanza a linee elettriche aeree", 1, 4,
    "Verificare prima dei lavori la presenza di linee aeree, cavi e conduttori sulla facciata o sopra la "
    "copertura; rispettare le distanze dell'Allegato IX (art. 117) o chiedere al gestore la messa fuori "
    "tensione o la protezione dei conduttori.")

_INTERFERENZA_STRADA = r(
    "Investimento da mezzi in manovra", 2, 4,
    "Area di lavoro a terra delimitata e separata dal traffico; segnaletica temporanea secondo il D.M. "
    "10/07/2002 quando si occupa la sede stradale; moviere durante le manovre e le operazioni di "
    "sollevamento; indumenti ad alta visibilità.")

_URTI_CARICHI = r(
    "Urti, colpi, impatti e compressioni durante il sollevamento", 2, 3,
    "Carichi imbracati con accessori idonei e verificati; nessuno sotto il carico sospeso; guida del "
    "carico con funi o aste nell'avvicinamento al punto di posa; segnalatore che comunica con il "
    "gruista quando il carico esce dalla sua vista.")

_INCENDIO_CALDO = r(
    "Incendio ed esplosione", 2, 4,
    "Permesso di lavoro a caldo; rimozione o protezione dei materiali combustibili (isolanti, legno, "
    "teli); bombole di GPL lontane dalla fiamma, in posizione verticale e protette dal sole, in quantità "
    "minima in copertura; estintore a portata di mano; controllo dell'area per almeno un'ora dopo la fine "
    "della fiamma.",
    DPI_BASE + ", indumenti protettivi")

_BIOLOGICO_GUANO = r(
    "Rischio biologico (guano di volatili, nidi di insetti)", 2, 2,
    "Ispezionare prima la zona; inumidire il guano prima di rimuoverlo, senza spazzare a secco; "
    "attenzione a nidi di vespe e calabroni; igiene delle mani e cassetta di pronto soccorso; "
    "segnalare al medico competente eventuali allergie.",
    DPI_BASE + ", facciale filtrante FFP3, tuta monouso")

# ---------------------------------------------------------------------------------------------
# Opere edili in copertura
# ---------------------------------------------------------------------------------------------

_LEGNO = "Coperture in legno"
_MANTI = "Manti di copertura"
_IMPERM = "Isolamento e impermeabilizzazione di coperture piane"
_COMPL = "Lattonerie e coperture a verde"
_ANCORAGGI = "Sistemi di ancoraggio permanenti"
_MANUT = "Manutenzione delle coperture"

_CO = [
    fase("CO.01", COPERTURA, _LEGNO, "Montaggio della grossa orditura in legno",
         "Sollevamento con gru e posa delle travi principali in legno massiccio o lamellare (colmo, "
         "arcarecci, puntoni, capriate) sulle murature o sui cordoli, con fissaggio mediante staffe "
         "metalliche, viti strutturali o barre resinate. Le travi sono guidate a destinazione con funi e "
         "fissate prima di sganciarle; le capriate restano controventate fino al completamento.",
         "Addetto al montaggio della grossa orditura in legno", 45, EDILIZIA,
         ["Gru a torre", "Autogru", "Sega circolare", "Avvitatore elettrico", "Trapano elettrico",
          "Ponteggio metallico fisso", "Trabattello", "Utensili manuali"], [
             r("Caduta dall'alto dal bordo e dalle travi in montaggio", 3, 4,
               "Ponteggio perimetrale con parapetto di sommità prima di iniziare; dall'interno lavorare da "
               "trabattelli o ponti su cavalletti e, dove manca un piano di calpestio, reti di sicurezza "
               "UNI EN 1263 sotto la zona di posa; nessuno cammina sulle travi: chi deve operare in quota "
               "sulla struttura si aggancia a ancoraggi provvisori verificati (art. 115).",
               DPI_ANTICADUTA),
             _URTI_CARICHI,
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Montaggio secondo il progetto e la sequenza indicata dal fornitore; travi e capriate "
               "sganciate dalla gru solo dopo il fissaggio definitivo o provvisorio; controventi e "
               "puntelli provvisori fino al completamento dell'orditura.",
               DPI_SOTTOGOLA),
             _CADUTA_MATERIALE, _VENTO,
             r("Polveri e fibre (polvere di legno)", 2, 2,
               "Tagli e lavorazioni del legno preferibilmente a terra con aspirazione; non soffiare la "
               "segatura; la polvere di legno duro è cancerogena (Allegato XLII).",
               DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
         ]),
    fase("CO.02", COPERTURA, _LEGNO, "Posa della piccola orditura in legno",
         "Posa e chiodatura o avvitatura di travetti, morali, correntini e listelli sulla grossa orditura "
         "secondo gli interassi di progetto, con taglio a misura degli elementi. Il lavoro si svolge in "
         "pendenza sulla falda: la piccola orditura non costituisce piano di calpestio finché non è "
         "coperta dal tavolato.",
         "Addetto alla posa della piccola orditura in legno", 55, EDILIZIA,
         ["Gru a torre", "Sega circolare", "Pistola sparachiodi", "Avvitatore elettrico",
          "Ponteggio metallico fisso", "Rete di sicurezza anticaduta", "Linea vita provvisoria",
          "Utensili manuali"], [
             _CADUTA_BORDO,
             r("Caduta dall'alto tra gli elementi dell'orditura", 3, 4,
               "Reti di sicurezza o sottopalco sotto la falda in costruzione (art. 148); camminamenti con "
               "tavole fissate trasversalmente sui travetti; aggancio dell'imbracatura alla linea vita "
               "provvisoria o al colmo con ancoraggi verificati.",
               DPI_ANTICADUTA),
             _CADUTA_MATERIALE, _POSTURE, _VENTO,
             r("Urti, colpi, impatti e compressioni", 2, 2,
               "Movimentare listelli e travetti in fasci legati; attenzione agli altri addetti "
               "nella rotazione degli elementi lunghi; martelli e chiodatrici usati lontano dalle mani.",
               DPI_BASE + ", occhiali protettivi"),
         ]),
    fase("CO.03", COPERTURA, _LEGNO, "Posa di tavolato, barriera al vapore e isolamento termico",
         "Posa del tavolato o dei pannelli in OSB sulla piccola orditura, stesura della barriera al vapore, "
         "posa dei pannelli isolanti (fibra di legno, lana di roccia o poliuretano), del telo "
         "impermeabile traspirante e della listellatura di ventilazione. Il tavolato completato diventa "
         "il piano di lavoro per le fasi successive.",
         "Addetto alla posa del tavolato e dell'isolamento di copertura", 45, EDILIZIA,
         ["Gru a torre", "Sega circolare", "Pistola sparachiodi", "Avvitatore elettrico",
          "Ponteggio metallico fisso", "Linea vita provvisoria", "Utensili manuali"], [
             _CADUTA_BORDO,
             r("Scivolamenti e cadute a livello sulla falda", 3, 3,
               "Non camminare sui teli e sui pannelli lisci con superficie bagnata o con brina; fissare "
               "subito i teli; listelli fermapiede provvisori sulla falda nelle pendenze elevate.",
               DPI_ANTICADUTA),
             r("Polveri e fibre (fibre minerali e di legno)", 3, 2,
               "Tagliare i pannelli con lame affilate o seghe con aspirazione e non a strappo; "
               "maniche lunghe; non soffiare la polvere; pulizia a umido o con aspiratore.",
               DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
             r("Caduta di materiale dall'alto o a livello", 3, 3,
               "Pannelli e rotoli sollevati in pacchi legati e depositati su supporti orizzontali, "
               "zavorrati contro il vento; area sottostante interdetta durante il sollevamento."),
             _VENTO, _MMC,
         ]),
    fase("CO.04", COPERTURA, _MANTI, "Smontaggio del manto esistente in tegole o coppi",
         "Rimozione a mano del manto di copertura esistente, con cernita e accatastamento degli elementi "
         "recuperabili e calo a terra dei materiali di risulta con montacarichi, gru o canale di scarico. "
         "Prima dei lavori si verifica lo stato dell'orditura e la presenza di materiali contenenti "
         "amianto, che vanno gestiti a parte da impresa iscritta all'Albo gestori ambientali.",
         "Addetto allo smontaggio del manto di copertura", 75, RI_RS,
         ["Ponteggio metallico fisso", "Linea vita provvisoria", "Andatoie e passerelle",
          "Argano a bandiera", "Autocarro con gru", "Utensili manuali"], [
             _CADUTA_BORDO,
             r("Caduta dall'alto per cedimento dell'orditura esistente", 3, 4,
               "Verifica preventiva della struttura lignea e dei solai sottotetto (art. 148); in caso di "
               "dubbio sottopalco o reti e camminamenti su tavole poggiate sulle travi sane; procedere per "
               "campi senza accumulare macerie sulla falda.",
               DPI_ANTICADUTA),
             r("Polveri e fibre", 3, 2,
               "Inumidire il manto e i detriti prima della rimozione; calo dei detriti con canale chiuso "
               "o in contenitori, mai per lancio; se si riscontrano materiali sospetti di contenere amianto "
               "sospendere il lavoro e far analizzare il campione.",
               DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
             _CADUTA_MATERIALE, _MMC, _BIOLOGICO_GUANO,
         ]),
    fase("CO.05", COPERTURA, _MANTI, "Posa del manto di copertura in tegole o coppi",
         "Distribuzione dei pacchi di tegole sulla falda in modo da non sovraccaricarla, posa degli "
         "elementi su listelli o su malta, fissaggio con ganci o chiodi secondo la zona di vento, taglio "
         "dei pezzi speciali e formazione del colmo ventilato e dei compluvi. Sui tetti esistenti si "
         "riutilizzano dove possibile i coppi recuperati.",
         "Addetto alla posa del manto in tegole e coppi", 50, EDILIZIA,
         ["Ponteggio metallico fisso", "Linea vita provvisoria", "Argano a bandiera", "Gru a torre",
          "Smerigliatrice angolare", "Utensili manuali"], [
             _CADUTA_BORDO,
             r("Scivolamenti e cadute a livello sulla falda", 3, 3,
               "Non camminare su tegole bagnate o con muschio; percorsi su listelli o tavole fermapiede; "
               "procedere dalla gronda verso il colmo mantenendosi agganciati alla linea vita.",
               DPI_ANTICADUTA),
             _CADUTA_MATERIALE, _POLVERI_SILICE, _MMC, _POSTURE, _SOLE,
         ]),
    fase("CO.06", COPERTURA, _MANTI, "Posa di coperture in lamiera grecata e pannelli sandwich",
         "Sollevamento dei pacchi di lamiere o pannelli sandwich su capannoni o edifici, posa dei singoli "
         "elementi sugli arcarecci in acciaio, legno o calcestruzzo e fissaggio con viti autoperforanti e "
         "cappellotti, con formazione di sormonte, colmi e raccordi. I tagli si eseguono con cesoie o "
         "roditrici: la smerigliatrice danneggia il rivestimento e produce scintille sul pannello.",
         "Addetto alla posa di coperture in lamiera e pannelli sandwich", 30, NC_RI,
         ["Autogru", "Sollevatore telescopico", "Piattaforma di lavoro elevabile",
          "Cesoia elettrica per lamiere", "Avvitatore elettrico", "Parapetto provvisorio",
          "Rete di sicurezza anticaduta", "Linea vita provvisoria", "Utensili manuali"], [
             _CADUTA_BORDO,
             r("Caduta dall'alto tra gli arcarecci e dal bordo di posa", 3, 4,
               "Reti di sicurezza UNI EN 1263-1 sotto l'intera campata in lavorazione, montate prima della "
               "posa; avanzamento dal bordo protetto con pannelli già fissati come piano di lavoro; "
               "imbracatura agganciata a linea vita provvisoria tesa lungo il colmo o gli arcarecci.",
               DPI_ANTICADUTA),
             r("Caduta di pannelli per effetto del vento", 2, 4,
               "Non sollevare né posare con vento oltre i limiti fissati dal fornitore e dall'autogru; "
               "pannelli sciolti fissati subito o zavorrati; pacchi in copertura legati alla struttura.",
               DPI_SOTTOGOLA),
             _URTI_CARICHI, _TAGLI, _SOLE, _SCIVOLAMENTI,
         ]),
    fase("CO.07", COPERTURA, _MANTI, "Rifacimento di coperture di capannoni con lastre fragili e lucernari",
         "Sostituzione di lastre di copertura e lucernari su capannoni industriali o agricoli esistenti, "
         "smontando gli elementi vecchi per campi e posando subito i nuovi pannelli. È il lavoro in "
         "copertura con il maggior numero di infortuni mortali per sfondamento: la copertura esistente si "
         "considera non calpestabile finché non è provato il contrario. Le lastre in cemento-amianto sono "
         "rimosse da impresa iscritta all'Albo con piano di lavoro (art. 256), non in questa fase.",
         "Addetto al rifacimento di coperture con lastre fragili", 45, ("Ristrutturazioni",),
         ["Piattaforma di lavoro elevabile", "Autogru", "Andatoie e passerelle",
          "Rete di sicurezza anticaduta", "Linea vita provvisoria", "Parapetto provvisorio",
          "Cesoia elettrica per lamiere", "Avvitatore elettrico", "Utensili manuali"], [
             _CADUTA_FRAGILE, _CADUTA_BORDO,
             r("Caduta di materiale dall'alto o a livello all'interno del capannone", 3, 3,
               "Sgomberare o interdire l'area interna sottostante; coordinarsi con l'attività produttiva "
               "che resta in esercizio; reti di sicurezza o teli di contenimento sotto la zona di lavoro."),
             _TAGLI, _SOLE,
             r("Polveri e fibre", 2, 3,
               "Prima dei lavori accertare con analisi l'assenza di amianto nelle lastre e nelle "
               "guarnizioni; smontaggio senza rotture; pulizia dello sporco accumulato a umido.",
               DPI_BASE + ", facciale filtrante FFP3"),
         ]),
    fase("CO.08", COPERTURA, _IMPERM, "Posa di barriera al vapore e isolamento termico su coperture piane",
         "Pulizia e primerizzazione del solaio o del massetto delle pendenze, stesura della barriera al "
         "vapore e posa a secco, incollata o fissata meccanicamente dei pannelli isolanti (EPS, XPS, "
         "poliuretano, lana di roccia). I materiali sono sollevati in copertura con gru o argano e "
         "distribuiti per non sovraccaricare il solaio.",
         "Addetto all'isolamento termico di coperture piane", 40, NC_RI,
         ["Gru a torre", "Argano a bandiera", "Parapetto provvisorio", "Avvitatore elettrico",
          "Utensili manuali"], [
             _CADUTA_BORDO, _CADUTA_ATTRAVERSO,
             r("Rischio chimico (primer e adesivi)", 2, 2,
               "Consultare le schede di sicurezza; primer a solvente usati all'aperto, lontano da fiamme, "
               "con contenitori chiusi quando non in uso; evitare il contatto con la pelle.",
               DPI_BASE + ", guanti in lattice o nitrile, maschera con filtro specifico"),
             r("Caduta di materiale dall'alto o a livello (pannelli e rotoli sollevati dal vento)", 3, 3,
               "Pannelli e rotoli zavorrati o legati; non lavorare con vento forte; area a terra lungo il "
               "perimetro delimitata."),
             _POSTURE, _SOLE,
         ]),
    fase("CO.09", COPERTURA, _IMPERM, "Impermeabilizzazione di coperture piane con guaine bituminose a caldo",
         "Posa di membrane bituminose prefabbricate in uno o due strati, saldate a fiamma con cannello a "
         "GPL sul piano di posa primerizzato, con sormonte longitudinali e di testa, risvolti sui muretti, "
         "raccordi ai bocchettoni e protezione finale con ardesia, vernice riflettente o zavorra.",
         "Addetto all'impermeabilizzazione con guaine bituminose a caldo", 40, TUTTE,
         ["Cannello a gas", "Argano a bandiera", "Autocarro con gru", "Parapetto provvisorio",
          "Utensili manuali"], [
             _CADUTA_BORDO, _INCENDIO_CALDO,
             r("Ustioni", 3, 3,
               "Fiamma diretta solo verso la membrana, mai verso persone, bombole o materiali; cannello "
               "spento e appoggiato sull'apposito supporto quando non in uso; maniche lunghe e guanti "
               "resistenti al calore; attenzione al bitume fuso nei risvolti.",
               DPI_BASE + ", indumenti protettivi, ghette per saldatura"),
             r("Rischio chimico (fumi di bitume e primer)", 3, 2,
               "Le emissioni del bitume nei lavori di copertura sono classificate dall'IARC come "
               "probabilmente cancerogene: non surriscaldare la membrana, lavorare sopravvento, ridurre "
               "il numero degli esposti; primer a base acqua dove possibile.",
               DPI_BASE + ", maschera con filtro specifico"),
             _MMC, _POSTURE, _SOLE,
         ]),
    fase("CO.10", COPERTURA, _IMPERM, "Impermeabilizzazione di coperture con prodotti liquidi",
         "Preparazione e pulizia del supporto, applicazione di primer e stesura a rullo, spatola o "
         "spruzzo di membrane liquide (poliuretaniche, poliuree, acriliche o cementizie elastiche), con "
         "eventuale armatura in tessuto nei punti critici. Il prodotto bicomponente si miscela in "
         "copertura nella quantità che si riesce ad applicare entro il tempo di lavorabilità.",
         "Addetto all'impermeabilizzazione con prodotti liquidi", 45, TUTTE,
         ["Impastatrice", "Pistola a spruzzo (airless)", "Idropulitrice", "Parapetto provvisorio",
          "Utensili manuali"], [
             _CADUTA_BORDO,
             r("Rischio chimico (diisocianati, solventi e resine)", 3, 3,
               "Uso dei prodotti con diisocianati solo dopo la formazione obbligatoria prevista dal Reg. "
               "(UE) 2020/1149; consultare le schede di sicurezza; applicazione all'aperto, sopravvento, "
               "con contenitori chiusi; sorveglianza sanitaria per i sensibilizzanti respiratori e cutanei.",
               DPI_BASE + ", guanti in lattice o nitrile, maschera con filtro specifico, occhiali a maschera, "
                          "tuta monouso"),
             r("Incendio ed esplosione", 1, 4,
               "Prodotti a solvente lontani da fiamme e fonti di calore; vietato fumare; nessuna "
               "lavorazione a caldo in contemporanea; estintore in copertura.",
               DPI_BASE),
             _SCIVOLAMENTI, _POSTURE, _SOLE,
         ]),
    fase("CO.11", COPERTURA, _COMPL, "Posa di lattonerie: canali di gronda, pluviali e scossaline",
         "Montaggio delle cicogne di sostegno, posa dei canali di gronda in rame, acciaio, alluminio o "
         "lamiera preverniciata, giunzione per rivettatura, incollaggio o stagnatura, e posa di "
         "scossaline, converse e discendenti pluviali fissati alla facciata con collari. Il lavoro si "
         "svolge dall'ultimo impalcato del ponteggio o da piattaforma elevabile, mai dalla falda o da scala.",
         "Addetto alla posa delle lattonerie", 50, EDILIZIA,
         ["Ponteggio metallico fisso", "Piattaforma di lavoro elevabile", "Cesoia elettrica per lamiere",
          "Trapano elettrico", "Cannello a gas", "Utensili manuali"], [
             r("Caduta dall'alto dal ponteggio o dalla linea di gronda", 2, 4,
               "Lavorare dall'impalcato di gronda del ponteggio con parapetto completo o dal cestello della "
               "PLE agganciati al punto di ancoraggio; vietato sporgersi oltre il parapetto o salire sul "
               "canale e sulle cicogne; pluviali lungo la facciata posati dagli impalcati sottostanti.",
               DPI_ANTICADUTA),
             _TAGLI,
             r("Ustioni", 2, 2,
               "Stagnatura con saldatore o cannello su appoggio stabile; pezzi caldi lasciati raffreddare "
               "prima della manipolazione; distanza da teli, guaine e materiali combustibili.",
               DPI_BASE + ", guanti per saldatura"),
             r("Rischio chimico (fumi di stagnatura e disossidanti)", 2, 2,
               "Disossidanti in contenitori chiusi; lavorare all'aperto sopravvento rispetto ai fumi; "
               "consultare le schede di sicurezza.",
               DPI_BASE + ", maschera con filtro specifico"),
             _CADUTA_MATERIALE_FACCIATA,
         ]),
    fase("CO.12", COPERTURA, _COMPL, "Realizzazione di coperture a verde",
         "Su un'impermeabilizzazione antiradice verificata, posa dello strato di protezione, del drenaggio "
         "e del filtro, distribuzione del substrato colturale sollevato in big bag con gru o soffiato da "
         "autocarro, e messa a dimora di sedum, erbacee o arbusti con il relativo impianto di "
         "irrigazione, secondo la UNI 11235. Il carico del substrato bagnato deve essere compatibile con "
         "la portata del solaio.",
         "Addetto alla realizzazione di coperture a verde", 35, NC_RI,
         ["Gru a torre", "Autogru", "Parapetto provvisorio", "Utensili manuali"], [
             _CADUTA_BORDO, _URTI_CARICHI,
             r("Crollo o ribaltamento di strutture per sovraccarico del solaio", 1, 4,
               "Distribuire il substrato secondo il piano di carico indicato dal progettista, senza "
               "accumulare big bag in un solo punto; scaricare i sacchi direttamente sulle zone portanti.",
               DPI_BASE),
             r("Polveri e fibre (substrato e materiali drenanti)", 3, 2,
               "Inumidire il substrato durante lo scarico e la stesa; lavorare sopravvento.",
               DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
             _MMC, _POSTURE, _SOLE,
         ]),
    fase("CO.13", COPERTURA, _ANCORAGGI, "Installazione di dispositivi di ancoraggio e linee vita permanenti",
         "Posa dei dispositivi di ancoraggio di tipo A (puntuali) e di tipo C (linee flessibili "
         "orizzontali) conformi alla UNI 11578 e alla UNI EN 795, secondo l'elaborato tecnico della "
         "copertura previsto dalla normativa regionale: fissaggio con ancoranti chimici o meccanici alla "
         "struttura portante, tesatura della fune, cartellonistica all'accesso. Al termine l'installatore "
         "rilascia la dichiarazione di corretta installazione con la documentazione fotografica dei "
         "fissaggi e il manuale d'uso e manutenzione.",
         "Addetto all'installazione di dispositivi di ancoraggio permanenti", 35, TUTTE,
         ["Martello perforatore (tassellatore)", "Avvitatore elettrico", "Linea vita provvisoria",
          "Parapetto provvisorio", "Piattaforma di lavoro elevabile", "Utensili manuali"], [
             r("Caduta dall'alto durante l'installazione (ancoraggi definitivi non ancora disponibili)", 3, 4,
               "I dispositivi in posa non si usano finché non sono completi e collaudati: durante "
               "l'installazione proteggersi con ponteggio o parapetti provvisori, con PLE o con linea "
               "vita provvisoria su ancoraggi verificati; accesso alla copertura da percorso protetto; "
               "squadra di almeno due persone con procedura di recupero in caso di caduta.",
               DPI_ANTICADUTA),
             r("Ancoraggio non idoneo per fissaggio errato alla struttura", 2, 4,
               "Fissare solo sugli elementi portanti indicati dal progettista, con ancoranti e coppie di "
               "serraggio del fabbricante; rispettare i tempi di indurimento delle resine; prova di "
               "carico dove prevista e documentazione dei fissaggi prima della chiusura del manto.",
               DPI_ANTICADUTA),
             r("Rischio chimico (ancoranti chimici)", 2, 2,
               "Consultare le schede di sicurezza delle resine; evitare il contatto con la pelle; "
               "cartucce usate raccolte e smaltite.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
             _CADUTA_MATERIALE, _VENTO,
         ]),
    fase("CO.14", COPERTURA, _MANUT, "Pulizia di coperture, canali di gronda e pluviali",
         "Rimozione a mano di foglie, muschio, detriti e nidi dalle falde, dai canali di gronda, dai "
         "bocchettoni e dai pluviali, con eventuale lavaggio a bassa pressione e disostruzione dei "
         "discendenti. Sono lavori brevi ma frequenti, da svolgere seguendo le istruzioni del fascicolo "
         "dell'opera e dell'elaborato tecnico della copertura, usando i dispositivi permanenti presenti.",
         "Addetto alla pulizia e manutenzione delle coperture", 80, EDILIZIA,
         ["Piattaforma di lavoro elevabile", "Scala a mano", "Idropulitrice", "Linea vita provvisoria",
          "Utensili manuali"], [
             r("Caduta dall'alto dal bordo della copertura", 3, 4,
               "Accesso dai percorsi previsti dall'elaborato tecnico della copertura; aggancio continuo ai "
               "dispositivi permanenti (verificati e con revisione periodica in corso di validità) o, in "
               "loro assenza, lavoro dalla PLE; scale a mano solo per l'accesso, vincolate e sporgenti "
               "almeno 1 m oltre il piano di arrivo (art. 113); mai lavorare dalla scala sul canale.",
               DPI_ANTICADUTA),
             _CADUTA_FRAGILE, _BIOLOGICO_GUANO,
             r("Scivolamenti e cadute a livello sulla falda", 3, 3,
               "Non salire su falde bagnate, ghiacciate o ricoperte di muschio; calzature antiscivolo; "
               "procedere agganciati alla linea vita.",
               DPI_ANTICADUTA),
             _CADUTA_MATERIALE,
         ]),
    fase("CO.15", COPERTURA, _MANUT, "Ripassatura del manto e riparazioni puntuali della copertura",
         "Interventi localizzati di manutenzione: sostituzione di tegole, coppi o lastre rotte, "
         "riposizionamento degli elementi scivolati, ripristino di colmi e di malte, riparazione di "
         "guaine e sigillatura di raccordi e scossaline. L'estensione ridotta non giustifica la rinuncia "
         "alle protezioni: si valuta caso per caso tra ponteggio, parapetti, PLE e dispositivi permanenti.",
         "Addetto alla ripassatura e riparazione delle coperture", 70, RI_RS,
         ["Piattaforma di lavoro elevabile", "Ponteggio metallico fisso", "Linea vita provvisoria",
          "Andatoie e passerelle", "Cannello a gas", "Utensili manuali"], [
             _CADUTA_BORDO, _CADUTA_ATTRAVERSO,
             _CADUTA_MATERIALE, _POSTURE, _VENTO,
             r("Ustioni", 2, 2,
               "Riparazioni a fiamma solo da addetti formati, con estintore a portata di mano e lontano "
               "da materiali combustibili del sottotetto; controllo dell'area al termine.",
               DPI_BASE + ", indumenti protettivi"),
         ]),
]

# ---------------------------------------------------------------------------------------------
# Opere edili in facciata
# ---------------------------------------------------------------------------------------------

_INTONACI = "Intonaci esterni"
_CAPPOTTO = "Isolamento termico a cappotto"
_RIVEST = "Rivestimenti e facciate ventilate"
_FINITURE = "Finiture e ripristini di facciata"
_PULIZIA = "Pulizia e interventi puntuali in facciata"

_FA = [
    fase("FA.01", FACCIATA, _INTONACI, "Intonaco esterno tradizionale eseguito a mano",
         "Preparazione del supporto con bagnatura e posa di paraspigoli e guide, applicazione a cazzuola "
         "del rinzaffo, dell'arriccio tirato a staggia e dello strato di finitura a frattazzo, con malte "
         "di calce o bastarde confezionate in cantiere. La malta è portata agli impalcati con argano o "
         "montacarichi.",
         "Addetto all'esecuzione di intonaci esterni tradizionali", 60, EDILIZIA,
         ["Betoniera a bicchiere", "Argano a bandiera", "Ponteggio metallico fisso", "Utensili manuali"], [
             _CADUTA_PONTEGGIO, _CADUTA_MATERIALE_FACCIATA, _CEMENTO, _SCHIZZI, _MMC,
             r("Movimenti ripetitivi degli arti superiori", 3, 2,
               "Alternare l'applicazione con le altre attività; pause; attrezzi leggeri e ben "
               "bilanciati; impalcato all'altezza che evita di lavorare con le braccia sopra le spalle.",
               DPI_BASE),
         ]),
    fase("FA.02", FACCIATA, _INTONACI, "Intonaco esterno premiscelato applicato a macchina",
         "Alimentazione dell'intonacatrice con premiscelato da silo o da sacchi, proiezione dell'impasto "
         "sulla parete con lancia, staggiatura e frattazzatura, con eventuale rete di armatura nelle zone "
         "di discontinuità del supporto. Le tubazioni dell'impasto salgono lungo il ponteggio e sono "
         "fissate per non intralciare i passaggi.",
         "Addetto all'esecuzione di intonaci premiscelati a macchina", 45, EDILIZIA,
         ["Intonacatrice", "Ponteggio metallico fisso", "Utensili manuali"], [
             _CADUTA_PONTEGGIO, _CADUTA_MATERIALE_FACCIATA,
             r("Getti e schizzi (proiezione dell'impasto e tubazioni in pressione)", 3, 2,
               "Lancia mai diretta verso persone; prima di aprire o disostruire la tubazione arrestare la "
               "macchina e scaricare la pressione; comunicazione costante tra l'addetto alla lancia e "
               "quello alla macchina.",
               DPI_BASE + ", occhiali a maschera"),
             r("Polveri e fibre (caricamento del premiscelato)", 3, 2,
               "Aprire i sacchi con cautela nella tramoggia; silo con filtro sullo sfiato; pulizia a "
               "umido della zona di caricamento.",
               DPI_BASE + ", facciale filtrante FFP2"),
             _CEMENTO, _MMC,
             r("Scivolamenti e cadute a livello", 3, 2,
               "Tubazioni fissate ai montanti e non stese sugli impalcati; rimozione degli sfridi di malta "
               "dagli impalcati a fine giornata."),
         ]),
    fase("FA.03", FACCIATA, _CAPPOTTO, "Preparazione del supporto e posa del profilo di partenza del cappotto",
         "Verifica della planarità e della consistenza del supporto, rimozione delle parti incoerenti, "
         "trattamento con primer consolidante, smontaggio di davanzali, pluviali e apparecchi in "
         "facciata, e fissaggio con tasselli del profilo di partenza in alluminio alla quota di zoccolatura, "
         "secondo la UNI/TR 11715. Si verifica che il ponteggio consenta lo spessore del sistema.",
         "Addetto alla preparazione del supporto per il cappotto termico", 55, ("Ristrutturazioni",
                                                                               "Nuove costruzioni"),
         ["Ponteggio metallico fisso", "Martello perforatore (tassellatore)", "Smerigliatrice angolare",
          "Idropulitrice", "Utensili manuali"], [
             _CADUTA_PONTEGGIO, _CADUTA_MATERIALE_FACCIATA,
             r("Polveri e fibre", 3, 2,
               "Rimozione dei vecchi intonaci e foratura con utensili dotati di aspirazione; bagnatura "
               "delle superfici; prima di intervenire su vecchie pitture o rivestimenti verificare "
               "l'eventuale presenza di piombo o amianto.",
               DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
             _ELETTRICO_LINEE,
             r("Rischio chimico (primer consolidanti)", 2, 2,
               "Consultare le schede di sicurezza; applicazione a rullo o pennello e non a spruzzo vicino "
               "alle finestre aperte degli occupanti; contenitori chiusi.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
         ]),
    fase("FA.04", FACCIATA, _CAPPOTTO, "Incollaggio e tassellatura dei pannelli isolanti del cappotto",
         "Applicazione del collante sul pannello a cordolo perimetrale e punti o a tutta superficie, posa "
         "dei pannelli in EPS, lana di roccia o fibra di legno a giunti sfalsati dal basso verso l'alto, "
         "taglio a misura attorno alle aperture e, a collante indurito, tassellatura meccanica secondo lo "
         "schema del progetto. Le fasce tagliafuoco tra i piani si realizzano dove previste dal progetto "
         "antincendio della facciata.",
         "Addetto alla posa dei pannelli isolanti del cappotto", 45, ("Ristrutturazioni", "Nuove costruzioni"),
         ["Ponteggio metallico fisso", "Impastatrice", "Taglierina a filo caldo per pannelli isolanti",
          "Martello perforatore (tassellatore)", "Argano a bandiera", "Utensili manuali"], [
             _CADUTA_PONTEGGIO, _CADUTA_MATERIALE_FACCIATA, _CEMENTO,
             r("Incendio ed esplosione (pannelli isolanti combustibili)", 2, 4,
               "Nessuna lavorazione a caldo, fiamma o smerigliatura vicino ai pannelli posati o stoccati; "
               "deposito dei pannelli lontano da fonti di innesco e non sotto il ponteggio; teli del "
               "ponteggio di tipo non propagante; vietato fumare; estintori sui piani di lavoro.",
               DPI_BASE),
             r("Polveri e fibre (taglio dei pannelli)", 3, 2,
               "Tagliare con lama o filo caldo invece che con disco; per la lana di roccia maniche lunghe "
               "e taglio con lama; raccolta degli sfridi in sacchi chiusi.",
               DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
             _MMC, _POSTURE,
         ]),
    fase("FA.05", FACCIATA, _CAPPOTTO, "Rasatura armata e finitura del cappotto",
         "Applicazione dei profili paraspigolo, rompigoccia e di raccordo ai serramenti, stesura del "
         "primo strato di rasante con annegamento della rete in fibra di vetro, secondo strato di "
         "rasatura e, dopo la stagionatura, applicazione del fondo e del rivestimento a spessore "
         "(acrilico, silossanico o ai silicati) a frattazzo.",
         "Addetto alla rasatura e finitura del cappotto", 55, ("Ristrutturazioni", "Nuove costruzioni"),
         ["Ponteggio metallico fisso", "Impastatrice", "Intonacatrice", "Utensili manuali"], [
             _CADUTA_PONTEGGIO, _CADUTA_MATERIALE_FACCIATA, _CEMENTO, _SCHIZZI,
             r("Rischio chimico (fondi e rivestimenti di finitura)", 2, 2,
               "Consultare le schede di sicurezza; prodotti all'acqua preferiti; protezione della pelle "
               "nella manipolazione dei rivestimenti ai silicati, fortemente alcalini.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
             r("Movimenti ripetitivi degli arti superiori", 3, 2,
               "Rotazione degli addetti tra stesura, annegamento della rete e finitura; pause; frattazzi "
               "leggeri e impalcato all'altezza corretta.",
               DPI_BASE),
             _SOLE,
         ]),
    fase("FA.06", FACCIATA, _RIVEST, "Rivestimento di facciata in lastre di pietra o ceramica",
         "Posa di lastre di pietra naturale, ricomposta o di ceramica sulla facciata con adesivi "
         "cementizi ad alte prestazioni e, oltre le dimensioni e le altezze indicate dal progetto, con "
         "ancoraggi meccanici in acciaio inox (perni, staffe, grappe) inseriti nel supporto. Le lastre si "
         "tagliano a umido a terra e si sollevano agli impalcati con argano o gru.",
         "Addetto alla posa di rivestimenti di facciata in pietra o ceramica", 45, EDILIZIA,
         ["Ponteggio metallico fisso", "Argano a bandiera", "Taglierina elettrica per piastrelle",
          "Smerigliatrice angolare", "Martello perforatore (tassellatore)", "Impastatrice",
          "Utensili manuali"], [
             _CADUTA_PONTEGGIO,
             r("Caduta di materiale dall'alto o a livello (lastre in posa)", 3, 4,
               "Lastre sostenute fino alla presa dell'adesivo o all'inserimento dell'ancoraggio; "
               "ancoraggi meccanici dove previsti dal progetto, mai omessi; area a terra interdetta e "
               "mantovana parasassi; lastre sugli impalcati in quantità limitata, su appoggi stabili.",
               DPI_BASE),
             _POLVERI_SILICE, _CEMENTO, _MMC, _TAGLI,
         ]),
    fase("FA.07", FACCIATA, _RIVEST, "Facciata ventilata: sottostruttura e isolamento",
         "Tracciamento e foratura della parete, fissaggio delle staffe in alluminio o acciaio con "
         "tasselli verificati per il supporto, montaggio dei montanti verticali e dei traversi, posa dei "
         "pannelli isolanti in lana minerale fissati con tasselli e del telo antivento, lasciando "
         "l'intercapedine di ventilazione prevista.",
         "Addetto al montaggio della sottostruttura di facciate ventilate", 40, NC_RI,
         ["Ponteggio metallico fisso", "Piattaforma di lavoro elevabile",
          "Martello perforatore (tassellatore)", "Avvitatore elettrico", "Cesoia elettrica per lamiere",
          "Utensili manuali"], [
             _CADUTA_PONTEGGIO, _CADUTA_MATERIALE_FACCIATA, _TAGLI,
             r("Polveri e fibre (foratura e lana minerale)", 3, 2,
               "Foratura con aspirazione; taglio della lana minerale con lama; maniche lunghe e pulizia "
               "con aspiratore.",
               DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
             _ELETTRICO_LINEE,
             r("Rumore", 3, 2,
               "Programmare le forature più lunghe; utensili con basso livello di emissione; "
               "otoprotettori nelle lavorazioni prolungate secondo la valutazione del rumore.",
               DPI_BASE + ", otoprotettori"),
         ]),
    fase("FA.08", FACCIATA, _RIVEST, "Facciata ventilata: montaggio delle lastre di rivestimento",
         "Taglio a misura e montaggio sulla sottostruttura delle lastre di rivestimento (gres porcellanato, "
         "laminato HPL, fibrocemento, alluminio o pietra) con ganci, clip, rivetti o ancoraggi a "
         "scomparsa secondo il sistema del fabbricante, con regolazione dei giunti e posa dei profili di "
         "chiusura su spigoli e aperture.",
         "Addetto al montaggio delle lastre di facciate ventilate", 40, NC_RI,
         ["Ponteggio metallico fisso", "Piattaforma di lavoro elevabile", "Sollevatore telescopico",
          "Taglierina elettrica per piastrelle", "Avvitatore elettrico", "Utensili manuali"], [
             _CADUTA_PONTEGGIO,
             r("Caduta di materiale dall'alto o a livello (lastre di grande formato)", 3, 4,
               "Lastre trasportate e posate in due con ventose manuali o sollevatori; ogni lastra "
               "bloccata in tutti i suoi agganci prima di lasciarla; non lavorare con vento forte; area a "
               "terra interdetta.",
               DPI_BASE),
             _POLVERI_SILICE, _MMC, _TAGLI,
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "Attenzione alle mani tra lastra e sottostruttura nell'aggancio; spigoli delle lastre "
               "protetti durante la movimentazione.",
               DPI_BASE + ", guanti antitaglio"),
         ]),
    fase("FA.09", FACCIATA, _FINITURE, "Pitturazione di facciata",
         "Lavaggio e preparazione delle superfici, stuccatura delle lesioni, applicazione di fissativo e "
         "di due mani di pittura (acrilica, silossanica, ai silicati o alla calce) a rullo, pennello o "
         "spruzzo airless, con protezione di serramenti, balconi e veicoli parcheggiati con teli e nastri.",
         "Addetto alla pitturazione di facciate", 55, EDILIZIA,
         ["Ponteggio metallico fisso", "Piattaforma di lavoro elevabile", "Pistola a spruzzo (airless)",
          "Idropulitrice", "Utensili manuali"], [
             _CADUTA_PONTEGGIO,
             r("Rischio chimico (pitture, fissativi e solventi)", 3, 2,
               "Consultare le schede di sicurezza; prodotti all'acqua preferiti; con lo spruzzo protezione "
               "delle vie respiratorie e teli sul ponteggio per contenere la nebbia verso le persone "
               "vicine e le finestre aperte; contenitori chiusi a fine lavoro.",
               DPI_BASE + ", maschera con filtro specifico, occhiali protettivi, guanti in lattice o nitrile"),
             _CADUTA_MATERIALE_FACCIATA, _SCHIZZI,
             r("Movimenti ripetitivi degli arti superiori", 3, 2,
               "Rulli con prolunga e attrezzi leggeri; alternanza tra preparazione e pitturazione; pause.",
               DPI_BASE),
         ]),
    fase("FA.10", FACCIATA, _FINITURE, "Ripristino di frontalini, balconi e cornicioni in calcestruzzo",
         "Battitura e asportazione del calcestruzzo degradato fino al sano, pulizia dei ferri d'armatura "
         "dalla ruggine con spazzolatura o sabbiatura, applicazione di passivante e ricostruzione con "
         "malta tissotropica fibrorinforzata (UNI EN 1504-3), seguita da rasatura e protezione "
         "superficiale. Si lavora sopra spazi spesso aperti al pubblico, con il rischio di distacco di "
         "frammenti durante la demolizione.",
         "Addetto al ripristino di frontalini e cornicioni in calcestruzzo", 65, RI_RS,
         ["Ponteggio metallico fisso", "Piattaforma di lavoro elevabile", "Martello demolitore",
          "Smerigliatrice angolare", "Impastatrice", "Idropulitrice", "Utensili manuali"], [
             _CADUTA_PONTEGGIO,
             r("Caduta di materiale dall'alto o a livello (frammenti di calcestruzzo)", 3, 3,
               "Teli e reti sul ponteggio, mantovana parasassi e impalcato di protezione sopra marciapiedi e "
               "ingressi; area a terra interdetta durante la demolizione; detriti raccolti in contenitori "
               "sugli impalcati, mai lasciati cadere.",
               DPI_BASE),
             r("Crollo o ribaltamento di strutture (parti di balconi e cornicioni)", 2, 4,
               "Prima di demolire valutare con il tecnico lo stato delle parti a sbalzo e dei ferri; "
               "puntellare gli sbalzi molto degradati; demolire per piccole porzioni senza sovraccaricare "
               "le solette.",
               DPI_BASE),
             r("Proiezione di schegge e frammenti", 3, 2,
               "Occhiali o visiera nella battitura e nella spazzolatura dei ferri; nessuno di fronte alla "
               "zona di demolizione.",
               DPI_BASE + ", occhiali a maschera"),
             _POLVERI_SILICE, _CEMENTO,
         ]),
    fase("FA.11", FACCIATA, _FINITURE, "Sigillatura di giunti di facciata e serramenti",
         "Rimozione dei vecchi sigillanti, pulizia e primerizzazione dei bordi del giunto, inserimento "
         "del fondo giunto in polietilene ed estrusione del sigillante poliuretanico, siliconico o ibrido "
         "con pistola, rifinitura con spatola. Si lavora in genere da piattaforma elevabile o da ponteggio, "
         "lungo giunti di dilatazione, pannelli prefabbricati e perimetri dei serramenti.",
         "Addetto alla sigillatura di giunti e serramenti in facciata", 60, TUTTE,
         ["Piattaforma di lavoro elevabile", "Ponteggio metallico fisso", "Utensili manuali"], [
             r("Caduta dall'alto dal cestello o dal ponteggio", 2, 4,
               "Dal cestello della PLE imbracatura con cordino corto agganciato al punto di ancoraggio, "
               "senza sporgersi né salire sui parapetti; dal ponteggio solo da impalcati completi.",
               DPI_ANTICADUTA),
             r("Rischio chimico (primer, sigillanti e solventi di pulizia)", 2, 2,
               "Consultare le schede di sicurezza; per i sigillanti poliuretanici con diisocianati liberi "
               "formazione secondo il Reg. (UE) 2020/1149; solventi in contenitori chiusi e lontani da "
               "fiamme.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
             _TAGLI, _CADUTA_MATERIALE_FACCIATA, _POSTURE,
         ]),
    fase("FA.12", FACCIATA, _PULIZIA, "Pulizia delle facciate mediante idrolavaggio",
         "Lavaggio delle superfici di facciata con acqua in pressione, fredda o calda, ed eventuali "
         "detergenti specifici, procedendo dall'alto verso il basso, con pressione regolata in base alla "
         "delicatezza del materiale. Prima del lavaggio si sigillano le aperture e si proteggono le "
         "parti elettriche in facciata; le acque di lavaggio sono raccolte e non disperse.",
         "Addetto alla pulizia delle facciate con idrolavaggio", 70, TUTTE,
         ["Idropulitrice", "Ponteggio metallico fisso", "Piattaforma di lavoro elevabile",
          "Utensili manuali"], [
             _CADUTA_PONTEGGIO,
             r("Getti e schizzi", 3, 3,
               "Lancia impugnata con due mani e mai diretta verso persone o verso il proprio corpo; nessuno "
               "nella zona di rimbalzo; attenzione al contraccolpo all'apertura del getto.",
               DPI_BASE + ", visiera protettiva, indumenti impermeabili"),
             r("Elettrocuzione", 2, 4,
               "Sezionare o proteggere con teli impermeabili prese, corpi illuminanti, insegne e quadri in "
               "facciata; non dirigere il getto verso linee e apparecchi elettrici; apparecchi alimentati "
               "da quadro con differenziale.",
               DPI_BASE + ", stivali di sicurezza"),
             r("Rischio chimico (detergenti)", 2, 2,
               "Usare i detergenti alle diluizioni indicate; consultare le schede di sicurezza; non "
               "miscelare prodotti diversi.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali a maschera"),
             r("Scivolamenti e cadute a livello", 3, 2,
               "Impalcati e aree a terra bagnati: calzature antiscivolo, rimozione dei ristagni, area a "
               "terra delimitata.",
               DPI_BASE + ", stivali di sicurezza"),
             _MMC,
         ]),
    fase("FA.13", FACCIATA, _PULIZIA, "Pulizia delle facciate mediante sabbiatura",
         "Rimozione di pitture, croste e sporco dalle superfici in muratura, pietra o calcestruzzo con "
         "getto di abrasivo a secco o a umido (microsabbiatura nei restauri), all'interno di un ponteggio "
         "interamente schermato con teli per contenere polveri e abrasivo. Si usano abrasivi privi di "
         "silice cristallina e si recupera il materiale proiettato.",
         "Addetto alla pulizia delle facciate con sabbiatura", 60, ("Ristrutturazioni", "Restauri",
                                                                    "Opere infrastrutturali"),
         ["Sabbiatrice", "Motocompressore", "Aspiratore con filtro HEPA", "Ponteggio metallico fisso",
          "Utensili manuali"], [
             _CADUTA_PONTEGGIO,
             r("Polveri e fibre (abrasivo e materiale asportato)", 4, 3,
               "Abrasivi privi di silice cristallina; preferire la sabbiatura a umido; ponteggio "
               "chiuso con teli e aspirazione; verificare prima l'eventuale presenza di piombo o amianto "
               "nelle pitture da rimuovere; sorveglianza sanitaria degli addetti.",
               DPI_BASE + ", autorespiratore, tuta monouso"),
             r("Proiezione di schegge e frammenti (getto abrasivo)", 3, 3,
               "Ugello mai diretto verso persone; comando a uomo presente sulla lancia; nessun altro "
               "addetto all'interno della zona schermata durante il getto.",
               DPI_BASE + ", autorespiratore, indumenti protettivi"),
             r("Rumore", 4, 2,
               "Valutazione dell'esposizione; compressore lontano dalla zona di lavoro; rotazione degli "
               "addetti; otoprotettori compatibili con il casco di sabbiatura.",
               DPI_BASE + ", cuffie antirumore"),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Teli integri su tutta la facciata; area a terra interdetta; raccolta dell'abrasivo "
               "accumulato sugli impalcati per non sovraccaricarli."),
         ]),
    fase("FA.14", FACCIATA, _PULIZIA, "Lavori puntuali in facciata da piattaforma di lavoro elevabile",
         "Interventi localizzati sulla facciata senza ponteggio: ispezioni, piccoli ripristini, "
         "fissaggio o rimozione di elementi, posa di staffe e pluviali, eseguiti dal cestello di una PLE "
         "condotta da operatore abilitato. La macchina è posizionata su area a terra delimitata, spesso "
         "su suolo pubblico.",
         "Addetto ai lavori in facciata da piattaforma di lavoro elevabile", 60, TUTTE,
         ["Piattaforma di lavoro elevabile", "Autocarro con cestello", "Trapano elettrico",
          "Utensili manuali"], [
             r("Caduta dall'alto dal cestello", 2, 4,
               "Imbracatura con cordino di trattenuta corto agganciato al punto di ancoraggio del "
               "cestello; non sporgersi, non salire sui parapetti e non uscire dal cestello in quota sui "
               "balconi o sulle coperture; formazione e abilitazione dell'operatore (Accordo Stato-Regioni "
               "sulle attrezzature, art. 73 c. 5).",
               DPI_ANTICADUTA),
             r("Urti, colpi, impatti e compressioni contro cornicioni e sporgenze", 2, 4,
               "Avvicinarsi lentamente alla facciata; attenzione a balconi, cornicioni, insegne e rami "
               "sopra il cestello; nessuna parte del corpo fuori dal parapetto durante i movimenti; "
               "operatore a terra in grado di riportare a terra il cestello in emergenza.",
               DPI_SOTTOGOLA),
             _ELETTRICO_LINEE, _INTERFERENZA_STRADA,
             r("Caduta di materiale dall'alto o a livello", 3, 3,
               "Area sotto il cestello delimitata e segnalata; attrezzi e materiali trattenuti nel "
               "cestello; nessun deposito sul parapetto."),
         ]),
    fase("FA.15", FACCIATA, _PULIZIA, "Messa in sicurezza di parti pericolanti di facciata",
         "Intervento, spesso urgente, per eliminare il pericolo di distacco di intonaci, cornici, "
         "frontalini, rivestimenti o elementi decorativi: battitura delle superfici, rimozione controllata "
         "delle parti instabili e loro calo a terra, applicazione di reti di contenimento fissate alla "
         "muratura dove le parti non possono essere rimosse. Si opera da PLE o da ponteggio, con l'area "
         "a terra interdetta prima di cominciare.",
         "Addetto alla messa in sicurezza di parti pericolanti di facciata", 75, RI_RS,
         ["Piattaforma di lavoro elevabile", "Autocarro con cestello", "Ponteggio metallico fisso",
          "Martello demolitore", "Martello perforatore (tassellatore)", "Utensili manuali"], [
             r("Caduta di materiale dall'alto o a livello (distacchi improvvisi)", 4, 3,
               "Interdire l'area a terra con transenne e, se serve, ordinanza sulla viabilità prima di "
               "salire; procedere dall'alto verso il basso; staccare i pezzi a mano o con attrezzi leggeri "
               "trattenendoli e calandoli in contenitori; nessuno sotto la zona di intervento.",
               DPI_SOTTOGOLA),
             r("Caduta dall'alto", 2, 4,
               "Lavoro dal cestello con imbracatura agganciata al punto di ancoraggio o da ponteggio "
               "completo; mai da scale appoggiate alla facciata degradata.",
               DPI_ANTICADUTA),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Prima dell'intervento sopralluogo con il tecnico per valutare elementi a sbalzo e "
               "decorazioni pesanti; puntellare ciò che non si rimuove subito; non appoggiare il cestello "
               "agli elementi da mettere in sicurezza.",
               DPI_SOTTOGOLA),
             r("Proiezione di schegge e frammenti", 3, 2,
               "Visiera o occhiali durante la battitura; procedere con colpi leggeri e controllati.",
               DPI_BASE + ", occhiali a maschera"),
             _INTERFERENZA_STRADA,
             r("Polveri e fibre", 3, 2,
               "Bagnare le parti da rimuovere; verificare la natura di rivestimenti e lastre prima di "
               "romperli (possibile amianto in pannelli e frontalini di vecchi edifici).",
               DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
         ]),
]

LAVORAZIONI = _CO + _FA
