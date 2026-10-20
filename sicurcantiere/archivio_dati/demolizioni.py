"""Fasi di lavoro delle categorie «Demolizioni e rimozioni» e «Bonifiche».

Testi scritti per questo progetto. Fonti consultate (solo come riferimento, nessun testo copiato):
- D.Lgs. 81/2008: Titolo IV Capo I (artt. 91 c. 2-bis, 100, 104 c. 4-bis), Capo II Sezione VIII
  (artt. 150-155: rafforzamento, ordine delle demolizioni, misure di sicurezza, convogliamento del
  materiale, sbarramento della zona, demolizione per rovesciamento), Allegato IX (distanze dalle
  linee elettriche), Titolo IX Capi I-III (agenti chimici, cancerogeni, amianto: artt. 246-261),
  Titolo XI (atmosfere esplosive);
- D.M. 6/9/1994 (metodologie tecniche per la bonifica dell'amianto e restituibilità degli ambienti),
  D.M. 20/8/1999 (prodotti incapsulanti), D.P.R. 8/8/1994 (formazione degli addetti alla bonifica),
  Legge 177/2012 e D.M. Difesa 11/5/2015 n. 82 (albo delle imprese di bonifica da ordigni bellici),
  D.Lgs. 152/2006 Parte IV (rifiuti, Titolo V bonifica dei siti contaminati), D.P.R. 120/2017
  (terre e rocce da scavo), D.P.R. 177/2011 (ambienti confinati), Reg. UE 2024/573 (gas fluorurati);
- testo degli artt. 150-155 e 104 c. 4-bis verificato su brocardi.it, tussl.it e certifico.com; gli
  altri riferimenti sono riportati da conoscenze normative senza riscontro puntuale online e vanno
  verificati (vedi il riepilogo dei dubbi nella documentazione del progetto).
I contenuti vanno sempre verificati e adattati dal coordinatore al cantiere specifico.
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import ATTREZZO, DPI_BASE, EDILIZIA, OPERA, TUTTE, fase, r

DEM = "Demolizioni e rimozioni"
BON = "Bonifiche (amianto, ordigni bellici, siti contaminati)"

MANCANTI: dict[str, tuple[str, str]] = {
    "Canale di scarico delle macerie": (
        OPERA, "Condotto a tronchi raccordati per far scendere le macerie dai piani senza gettarle "
               "dall'alto, con sbocco a non più di 2 m dal piano di raccolta (art. 153)."),
    "Estrattore d'aria con filtro assoluto HEPA (depressore)": (
        ATTREZZO,
        "Mantiene in depressione l'area confinata nella bonifica dell'amianto friabile e filtra l'aria "
        "espulsa (D.M. 6/9/1994); il ventilatore estrattore del catalogo non ha filtrazione assoluta."),
    "Nebulizzatore a bassa pressione": (
        ATTREZZO, "Serve a bagnare i materiali con acqua o incapsulante senza disperdere fibre: il D.M. "
                  "6/9/1994 esclude getti ad alta pressione sui materiali contenenti amianto."),
    "Rilevatore di masse metalliche (magnetometro)": (
        ATTREZZO, "Strumento indispensabile per la ricerca di ordigni bellici in superficie e, con "
                  "sonda in foro, in profondità."),
}

# --- DPI ricorrenti ---
_DPI_POLVERI = DPI_BASE + ", facciale filtrante FFP3, occhiali protettivi"
_DPI_QUOTA = "Casco con sottogola, calzature di sicurezza, guanti, imbracatura, cordino con assorbitore"
_DPI_AMIANTO_C = ("Casco, calzature di sicurezza, guanti in lattice o nitrile, tuta monouso, "
                  "facciale filtrante FFP3")
_DPI_AMIANTO_C_QUOTA = _DPI_AMIANTO_C + ", imbracatura, cordino con assorbitore"
_DPI_AMIANTO_F = ("Calzature di sicurezza, guanti in lattice o nitrile, tuta monouso, maschera con filtro "
                  "specifico (pieno facciale con filtro P3 o elettrorespiratore a ventilazione assistita)")

# --- Rischi ricorrenti ---
_CROLLO = r("Crollo o ribaltamento di strutture", 2, 4,
            "Verifica preliminare della stabilità e rinforzi o puntellamenti dove serve (art. 150); "
            "sequenza stabilita nel programma delle demolizioni inserito nel POS (art. 151), dall'alto "
            "verso il basso e senza indebolire le strutture portanti o adiacenti; lavori sorvegliati da "
            "un preposto; sospensione immediata in caso di lesioni o cedimenti imprevisti.")
_CADUTA_MAT = r("Caduta di materiale dall'alto o a livello", 3, 3,
                "Zona sottostante sbarrata e vietata a sosta e transito (art. 154); materiale mai gettato "
                "dall'alto ma calato o convogliato in canali chiusi (art. 153); elementi pesanti calati con "
                "mezzi di sollevamento; accesso allo sbocco del canale solo a scarico sospeso.")
_POLVERI = r("Polveri e fibre", 3, 2,
             "Bagnatura continua delle murature e delle macerie (art. 153 c. 5); utensili con aspirazione "
             "alla fonte dove possibile; locali chiusi ventilati e separati dalle zone abitate con teli; "
             "polveri di silice cristallina trattate come agente cancerogeno (Titolo IX Capo II).",
             _DPI_POLVERI)
_AMIANTO_IMPREVISTO = r("Esposizione ad amianto (ritrovamento imprevisto)", 1, 4,
                        "Ricerca preventiva dei materiali contenenti amianto prima dei lavori (art. 248), con "
                        "campionamenti in caso di dubbio; se si trova materiale sospetto, fermare i lavori, "
                        "bagnarlo, delimitare la zona e affidare la rimozione a impresa iscritta all'Albo "
                        "gestori ambientali (cat. 10) con piano di lavoro (art. 256).",
                        DPI_BASE + ", facciale filtrante FFP3")
_MMC = r("Movimentazione manuale dei carichi", 3, 2,
         "Uso di carriole, carrelli e mezzi di sollevamento; carichi frazionati e sollevati in due oltre i "
         "limiti della valutazione (Titolo VI, ISO 11228-1); formazione sulle corrette posture.")
_PUNTURE = r("Punture, tagli e abrasioni", 3, 2,
             "Rimuovere o ribattere chiodi e spigoli taglienti appena scoperti; non afferrare a mani nude "
             "frammenti di vetro, lamiera o ferro; guanti adatti al materiale trattato.",
             DPI_BASE + ", guanti antitaglio")
_PROIEZIONE = r("Proiezione di schegge e frammenti", 3, 2,
                "Lavorare con l'utensile orientato lontano dal corpo e dai colleghi; schermi o teli verso "
                "le zone di passaggio; occhiali sempre indossati durante la demolizione.",
                DPI_BASE + ", occhiali protettivi")
_INVESTIMENTO = r("Investimento da mezzi in manovra", 2, 4,
                  "Addetti a terra fuori dal raggio d'azione del mezzo e in contatto visivo con l'operatore; "
                  "percorsi pedonali separati; moviere nelle manovre in retromarcia.")
_SCIVOLAMENTI = r("Scivolamenti e cadute a livello", 3, 2,
                  "Rimozione frequente delle macerie dai percorsi; illuminazione adeguata; aperture nei solai "
                  "protette o chiuse con tavolati fissati.")
_CADUTA_ALTO = r("Caduta dall'alto", 2, 4,
                 "Ponteggi o ponti di servizio indipendenti dall'opera da demolire (art. 152); aperture e "
                 "bordi protetti con parapetti; dove non è possibile, imbracatura agganciata a punti sicuri.",
                 _DPI_QUOTA)
_CADUTA_COPERTURA = r("Caduta dall'alto dal bordo e attraverso la copertura", 3, 4,
                      "Ponteggio perimetrale con parapetto oltre la linea di gronda o parapetti provvisori; "
                      "camminamenti su andatoie ripartitrici e mai sugli elementi da rimuovere; reti "
                      "anticaduta o tavolato sotto le zone non portanti; linea vita provvisoria con "
                      "imbracatura; nessun lavoro con vento forte, pioggia o ghiaccio.", _DPI_QUOTA)
_MICROCLIMA_TETTO = r("Microclima", 2, 2,
                      "Programmare il lavoro in copertura nelle ore meno calde; pause all'ombra e acqua a "
                      "disposizione; sospendere con temperature o vento eccessivi.",
                      _DPI_QUOTA + ", copricapo")
_ELETTRO_IMPIANTI = r("Elettrocuzione", 2, 4,
                      "Distacco delle utenze da parte degli enti gestori prima dei lavori; verifica "
                      "dell'assenza di tensione su linee e quadri prima del taglio; individuazione delle "
                      "linee che restano in servizio per il cantiere.", DPI_BASE + ", guanti dielettrici")

# =====================================================================================
# DEMOLIZIONI E RIMOZIONI
# =====================================================================================

_G_MECC = "Demolizione di edifici con mezzi meccanici"
_G_MAN = "Demolizioni manuali di strutture e murature"
_G_COP = "Rimozione di coperture"
_G_FIN = "Rimozione di finiture, serramenti e impianti"
_G_MAC = "Gestione delle macerie e dei rifiuti da demolizione"

_DEMOLIZIONI = [
    fase("DM.01", DEM, _G_MECC, "Operazioni preliminari e messa in sicurezza dell'edificio da demolire",
         "Sopralluogo e verifica dello stato di conservazione delle strutture, distacco e bonifica delle "
         "utenze (gas, elettricità, acqua, fognatura) da parte degli enti gestori e ricerca dei materiali "
         "pericolosi, primo tra tutti l'amianto. In base all'esito si eseguono rinforzi e puntellamenti, si "
         "redige il programma delle demolizioni e si delimita l'area di rispetto attorno al fabbricato.",
         "Addetto alla messa in sicurezza preliminare dell'edificio da demolire", 50, TUTTE,
         ["Puntelli metallici", "Trapano elettrico", "Scala a mano", "Utensili manuali", "Autocarro"], [
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Accesso all'edificio solo dopo la verifica di stabilità di un tecnico (art. 150); percorsi "
               "interni scelti sulle parti ritenute sicure; puntelli posati partendo dai piani più bassi e su "
               "appoggi stabili, senza rimuovere alcun elemento strutturale in questa fase."),
             r("Incendio ed esplosione", 1, 4,
               "Conferma scritta del distacco e della bonifica della rete gas prima di qualunque lavoro; "
               "nessuna fiamma libera finché non è verificata l'assenza di gas e di serbatoi o bombole "
               "dimenticate."),
             _ELETTRO_IMPIANTI, _AMIANTO_IMPREVISTO,
             r("Rischio biologico", 2, 2,
               "Edifici abbandonati: rimozione con pala e sacchi del guano e delle carcasse dopo averli "
               "inumiditi; attenzione a siringhe e rifiuti; vaccinazione antitetanica in regola.",
               DPI_BASE + ", facciale filtrante FFP3, tuta monouso"),
             _SCIVOLAMENTI,
         ]),
    fase("DM.02", DEM, _G_MECC, "Demolizione totale di edifici con escavatore e pinza demolitrice",
         "Abbattimento del fabbricato con escavatore munito di pinza demolitrice, anche a braccio lungo per gli "
         "edifici più alti, procedendo per piani dall'alto verso il basso secondo il programma delle "
         "demolizioni. Le macerie sono fatte cadere verso l'interno del sedime, bagnate di continuo e separate "
         "per tipologia; un addetto a terra assiste l'operatore e cura la nebulizzazione.",
         "Addetto alla demolizione meccanica di edifici", 20, TUTTE,
         ["Escavatore con pinza demolitrice", "Escavatore", "Autocarro", "Idropulitrice", "Utensili manuali"], [
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Sequenza del programma delle demolizioni (art. 151) che evita parti a sbalzo o pareti isolate "
               "instabili; mezzo posizionato a distanza maggiore dell'altezza della parte in demolizione e "
               "mai sopra solai o macerie instabili; rovesciamento per trazione o spinta ammesso solo per "
               "parti alte non più di 5 m (art. 155)."),
             r("Caduta di materiale dall'alto o a livello", 3, 4,
               "Area di rispetto sbarrata e vietata a chiunque (art. 154), dimensionata sull'altezza "
               "dell'edificio e sulla portata del braccio; addetto a terra fuori da questa area durante "
               "l'azione della pinza; protezioni verso strade ed edifici confinanti."),
             _POLVERI, _INVESTIMENTO, _AMIANTO_IMPREVISTO,
             r("Elettrocuzione", 1, 4,
               "Linee aeree individuate in anticipo e messe fuori tensione o rispettando le distanze "
               "dell'Allegato IX, tenendo conto della massima estensione del braccio."),
         ]),
    fase("DM.03", DEM, _G_MECC, "Demolizione di strutture in calcestruzzo armato con martello demolitore",
         "Frantumazione con escavatore munito di martello idraulico di platee, fondazioni, muri di sostegno e "
         "altre strutture massicce in c.a. o muratura. I ferri d'armatura vengono tagliati con cesoia o "
         "cannello e i blocchi ridotti a dimensioni trasportabili; dove necessario si interviene a terra con "
         "martelli demolitori portatili.",
         "Addetto alla demolizione di strutture in c.a. con mezzi meccanici", 25, TUTTE,
         ["Escavatore con martello demolitore", "Martello demolitore", "Cannello ossiacetilenico",
          "Autocarro", "Utensili manuali"], [
             _PROIEZIONE, _POLVERI, _INVESTIMENTO,
             r("Seppellimento e sprofondamento", 2, 4,
               "Nella demolizione di fondazioni e strutture interrate, pareti dello scavo profilate con "
               "inclinazione stabile o armate; nessun addetto nello scavo mentre opera il mezzo; macerie "
               "depositate lontano dal ciglio."),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Muri di sostegno e contrafforti demoliti solo dopo aver verificato la spinta del terreno "
               "retrostante; procedere per tratti senza scalzare le strutture adiacenti da conservare."),
             r("Rumore", 4, 2,
               "Addetti a terra lontani dal martello in azione; rotazione dei turni; avviso preventivo ai "
               "vicini e rispetto degli orari comunali per le attività rumorose.",
               DPI_BASE + ", otoprotettori"),
         ]),
    fase("DM.04", DEM, _G_MAN, "Demolizione manuale di murature portanti",
         "Smantellamento a mano o con piccoli utensili di murature in pietra, mattoni o blocchi, procedendo per "
         "corsi orizzontali dall'alto e lavorando da ponteggi o ponti indipendenti dal muro. Prima si scaricano "
         "e puntellano solai, architravi e strutture che vi appoggiano; le macerie scendono dai piani con il "
         "canale di scarico.",
         "Addetto alla demolizione manuale di murature portanti", 60, EDILIZIA,
         ["Martello demolitore", "Martello perforatore (tassellatore)", "Puntelli metallici",
          "Ponteggio metallico fisso", "Ponte su cavalletti", "Canale di scarico delle macerie",
          "Utensili manuali"], [
             _CROLLO,
             r("Caduta dall'alto", 2, 4,
               "Vietato lavorare in piedi sopra i muri in demolizione; per muri più alti di 2 m usare ponteggi "
               "o ponti indipendenti dall'opera (art. 152); aperture nei solai e vani prospicienti il vuoto "
               "protetti con parapetti.", _DPI_QUOTA),
             _CADUTA_MAT, _POLVERI, _PROIEZIONE, _MMC,
         ]),
    fase("DM.05", DEM, _G_MAN, "Demolizione di tramezzi e partizioni interne",
         "Abbattimento di tramezzi in laterizio, cartongesso o blocchi leggeri non portanti, dopo aver "
         "verificato che non sostengano solai o carichi e che non contengano impianti ancora attivi. Si "
         "procede dall'alto verso il basso con mazza, scalpello o martello leggero e si allontanano le "
         "macerie ad ogni avanzamento.",
         "Addetto alla demolizione di tramezzi", 65, EDILIZIA,
         ["Martello demolitore", "Ponte su cavalletti", "Trabattello", "Canale di scarico delle macerie",
          "Utensili manuali"], [
             r("Crollo o ribaltamento di strutture", 2, 3,
               "Verificare con il tecnico che la parete non sia portante e che non vi gravino travi o solai "
               "inflessi; non abbattere ampie porzioni per rovesciamento ma a piccoli tratti dall'alto."),
             _ELETTRO_IMPIANTI, _POLVERI, _PROIEZIONE, _MMC, _SCIVOLAMENTI,
         ]),
    fase("DM.06", DEM, _G_MAN, "Demolizione di solai e strutture orizzontali",
         "Demolizione di solai in latero-cemento, in legno o in putrelle e tavelloni, di balconi e pianerottoli, "
         "previa puntellatura delle parti da conservare e interdizione dei piani sottostanti. Si rimuovono "
         "prima pavimenti e massetti per alleggerire il solaio, poi si procede per campi dal centro verso gli "
         "appoggi, lavorando da posizioni stabili.",
         "Addetto alla demolizione di solai", 55, EDILIZIA,
         ["Martello demolitore", "Smerigliatrice angolare", "Puntelli metallici", "Ponteggio metallico fisso",
          "Rete di sicurezza anticaduta", "Andatoie e passerelle", "Canale di scarico delle macerie",
          "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Addetti mai sulla parte di solaio in demolizione: si lavora da tavolati o passerelle "
               "appoggiate a strutture integre o dal ponteggio, con imbracatura agganciata a punti "
               "indipendenti; reti o impalcati sotto il campo da demolire; bordi aperti con parapetti.",
               _DPI_QUOTA),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Puntellamento del solaio e delle strutture contigue (art. 150); nessun accumulo di macerie "
               "sul solaio; piano sottostante sgombro e interdetto; sequenza stabilita nel programma delle "
               "demolizioni."),
             _CADUTA_MAT, _POLVERI, _PROIEZIONE,
         ]),
    fase("DM.07", DEM, _G_COP, "Rimozione di manti di copertura in tegole e coppi",
         "Smontaggio a mano di tegole, coppi e listelli, con accatastamento ordinato su bancali per il "
         "recupero degli elementi integri e discesa a terra con argano, montacarichi o gru. Si procede per "
         "fasce dalla linea di colmo verso la gronda, senza caricare la copertura con cumuli di materiale.",
         "Addetto alla rimozione di manti di copertura in laterizio", 65, EDILIZIA,
         ["Ponteggio metallico fisso", "Linea vita provvisoria", "Andatoie e passerelle", "Argano a bandiera",
          "Autocarro con gru", "Utensili manuali"], [
             _CADUTA_COPERTURA, _CADUTA_MAT, _MMC, _MICROCLIMA_TETTO,
             r("Posture incongrue", 3, 2,
               "Alternare le posizioni di lavoro; ginocchiere nel lavoro a falda; pause programmate.",
               _DPI_QUOTA + ", ginocchiere"),
             r("Polveri e fibre", 2, 2,
               "Bagnare il sottomanto e i detriti; verificare prima la presenza di guaine o sottocoppi "
               "contenenti amianto.", _DPI_QUOTA + ", facciale filtrante FFP2"),
         ]),
    fase("DM.08", DEM, _G_COP, "Rimozione di manti di copertura in lamiera",
         "Smontaggio di lastre in lamiera grecata, pannelli sandwich e lattonerie, svitando o tagliando i "
         "fissaggi e calando le lastre a terra con mezzi di sollevamento. Va accertato prima che le lastre "
         "non siano in cemento-amianto e che gli arcarecci sottostanti reggano il peso degli addetti.",
         "Addetto alla rimozione di manti di copertura in lamiera", 60, TUTTE,
         ["Piattaforma di lavoro elevabile", "Ponteggio metallico fisso", "Linea vita provvisoria",
          "Rete di sicurezza anticaduta", "Avvitatore elettrico", "Cesoia elettrica per lamiere",
          "Autogru", "Utensili manuali"], [
             _CADUTA_COPERTURA,
             r("Punture, tagli e abrasioni", 3, 3,
               "Afferrare le lastre solo con guanti antitaglio e, per le grandi dimensioni, in due; "
               "rimuovere o piegare subito i bordi e le viti sporgenti.",
               _DPI_QUOTA + ", guanti antitaglio"),
             r("Caduta di materiale dall'alto o a livello", 3, 3,
               "Lastre imbracate in pacchi legati e guidate con funi; non lasciare lastre slegate in "
               "copertura con vento; area sottostante interdetta."),
             r("Microclima", 2, 2,
               "Le lamiere al sole raggiungono temperature elevate: lavori nelle ore fresche, pause e acqua; "
               "sospendere con vento forte che rende ingovernabili le lastre.", _DPI_QUOTA + ", copricapo"),
         ]),
    fase("DM.09", DEM, _G_COP, "Rimozione della grossa e piccola orditura di tetti in legno",
         "Smontaggio di tavolati, listelli e travetti (piccola orditura) e successivamente di arcarecci, "
         "puntoni e capriate (grossa orditura), dopo aver rimosso il manto. Gli elementi principali sono "
         "imbracati e sostenuti con la gru prima di tagliarne gli appoggi, quindi calati a terra; si "
         "verificano in anticipo marcescenze e trattamenti preservanti tossici.",
         "Addetto alla rimozione dell'orditura lignea di copertura", 60, EDILIZIA,
         ["Gru a torre", "Autogru", "Motosega", "Sega circolare", "Ponteggio metallico fisso",
          "Linea vita provvisoria", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Mai camminare su travetti o tavolati non verificati; lavorare dal ponteggio, da piattaforme o "
               "da impalcati sottostanti; imbracatura sempre agganciata alla linea vita o a elementi stabili "
               "non destinati alla rimozione.", _DPI_QUOTA),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Capriate e travi imbracate e in tiro sulla gru prima del taglio degli appoggi; controventare "
               "le capriate restanti; ordine di smontaggio deciso nel programma delle demolizioni."),
             _CADUTA_MAT, _PUNTURE, _MMC,
             r("Rischio chimico", 2, 2,
               "Il legno vecchio può essere impregnato di preservanti (creosoto, sali, pentaclorofenolo): "
               "evitare il taglio a secco prolungato, raccogliere la segatura e gestire il legno trattato "
               "come rifiuto separato.", _DPI_QUOTA + ", facciale filtrante FFP2"),
         ]),
    fase("DM.10", DEM, _G_FIN, "Rimozione di pavimenti, sottofondi e massetti",
         "Demolizione di pavimenti in ceramica, pietra, legno o resilienti e dei relativi massetti e "
         "sottofondi, con martello demolitore e attrezzi manuali, fino al solaio. Prima si verifica che "
         "non vi siano piastrelle vinil-amianto o colle contenenti amianto e si individuano impianti a "
         "pavimento ancora in servizio.",
         "Addetto alla rimozione di pavimenti e massetti", 65, EDILIZIA,
         ["Martello demolitore", "Martello demolitore pneumatico", "Motocompressore",
          "Canale di scarico delle macerie", "Utensili manuali"], [
             _POLVERI, _PROIEZIONE, _AMIANTO_IMPREVISTO,
             r("Posture incongrue", 3, 2,
               "Utensili a manico lungo per il distacco; alternanza con attività in piedi; ginocchiere nei "
               "lavori a terra.", DPI_BASE + ", ginocchiere"),
             r("Crollo o ribaltamento di strutture", 1, 4,
               "Non accumulare macerie su solai vecchi o degradati; non scalpellare oltre il sottofondo per "
               "non danneggiare i travetti del solaio."),
             _MMC,
         ]),
    fase("DM.11", DEM, _G_FIN, "Rimozione di intonaci e rivestimenti",
         "Spicconatura di intonaci interni ed esterni fino al vivo della muratura e rimozione di "
         "rivestimenti in piastrelle, lastre o pannelli, lavorando da ponteggio, trabattello o ponte su "
         "cavalletti. Le superfici vengono bagnate prima del distacco e i detriti raccolti ad ogni "
         "avanzamento.",
         "Addetto alla rimozione di intonaci e rivestimenti", 70, EDILIZIA,
         ["Martello perforatore (tassellatore)", "Martello demolitore", "Ponteggio metallico fisso",
          "Trabattello", "Ponte su cavalletti", "Canale di scarico delle macerie", "Utensili manuali"], [
             r("Caduta di materiale dall'alto o a livello", 3, 2,
               "Area sottostante il ponteggio sbarrata; teli o reti sul ponteggio di facciata; distacco a "
               "piccole porzioni partendo dall'alto."),
             _POLVERI, _PROIEZIONE,
             r("Posture incongrue", 3, 2,
               "Piano di lavoro a un'altezza che eviti braccia sopra le spalle; pause e rotazione.",
               DPI_BASE + ", occhiali protettivi"),
             r("Movimenti ripetitivi degli arti superiori", 3, 2,
               "Utensili leggeri e bilanciati; alternanza tra spicconatura e raccolta dei detriti."),
         ]),
    fase("DM.12", DEM, _G_FIN, "Rimozione di controsoffitti",
         "Smontaggio di controsoffitti in pannelli, doghe metalliche, cartongesso o arelle con intonaco, e "
         "delle relative orditure di sostegno. In anticipo si accerta il tipo di materiale (amianto, fibre "
         "artificiali vetrose) e si scollegano corpi illuminanti e impianti incassati.",
         "Addetto alla rimozione di controsoffitti", 65, EDILIZIA,
         ["Trabattello", "Ponte su cavalletti", "Scala doppia", "Aspiratore con filtro HEPA",
          "Utensili manuali"], [
             r("Caduta di materiale dall'alto o a livello", 3, 3,
               "Mai lavorare sotto porzioni già staccate dagli appoggi; smontare per campi piccoli, "
               "sostenendo i pannelli prima di sganciarli; area sottostante interdetta ad altri."),
             r("Polveri e fibre", 3, 2,
               "Fibre artificiali vetrose: rimuovere i materassini senza strapparli, chiuderli in sacchi e "
               "aspirare con filtro HEPA; per controsoffitti contenenti amianto si applica il Titolo IX "
               "Capo III con impresa abilitata.", DPI_BASE + ", facciale filtrante FFP3, tuta monouso, "
                                                           "occhiali a maschera"),
             _ELETTRO_IMPIANTI,
             r("Caduta dall'alto", 2, 3,
               "Trabattello con ruote bloccate e parapetti; scale doppie solo per brevi interventi e con "
               "catena di trattenuta; non salire sui ripiani più alti.", DPI_BASE),
             r("Posture incongrue", 3, 2,
               "Lavoro con braccia alzate: piano di lavoro portato alla giusta altezza; pause frequenti."),
         ]),
    fase("DM.13", DEM, _G_FIN, "Rimozione di serramenti e opere in ferro",
         "Smontaggio di infissi interni ed esterni, tapparelle, cassonetti, ringhiere, inferriate, cancelli e "
         "scale metalliche, con rimozione di vetri, taglio degli ancoraggi e calo a terra. Le parti pesanti "
         "sono sostenute prima del taglio e i vetri smontati e accatastati per primi.",
         "Addetto alla rimozione di serramenti e opere in ferro", 70, EDILIZIA,
         ["Smerigliatrice angolare", "Cannello ossiacetilenico", "Martello perforatore (tassellatore)",
          "Trabattello", "Ponteggio metallico fisso", "Autocarro con gru", "Utensili manuali"], [
             r("Punture, tagli e abrasioni", 3, 3,
               "Vetri rimossi per primi o protetti con pellicola; maneggiare lastre e profili con guanti "
               "antitaglio; contenitori dedicati per i frammenti.", DPI_BASE + ", guanti antitaglio"),
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "Ante, cancelli e ringhiere sostenuti o imbracati prima di tagliare cerniere e zanche; "
               "movimentazione in due o con mezzi di sollevamento."),
             r("Caduta dall'alto", 2, 4,
               "Rimuovere i parapetti di balconi e scale solo dopo aver installato parapetti provvisori; "
               "nella rimozione di finestre ai piani alti lavorare dall'interno con imbracatura agganciata.",
               _DPI_QUOTA),
             r("Incendio ed esplosione", 2, 3,
               "Tagli a caldo con permesso di lavoro, lontano da materiali infiammabili; estintore a portata "
               "di mano e controllo dell'area al termine.", DPI_BASE + ", schermo per saldatura"),
             r("Rischio chimico", 2, 2,
               "Vernici al piombo su vecchie opere in ferro: preferire il taglio a freddo e non riscaldare le "
               "superfici verniciate; lavare le mani prima di mangiare.", DPI_BASE + ", facciale filtrante FFP3"),
             _MMC,
         ]),
    fase("DM.14", DEM, _G_FIN, "Rimozione di impianti elettrici, idrici, termici e sanitari",
         "Smontaggio di sanitari, radiatori, caldaie, tubazioni, canalizzazioni, quadri e linee elettriche, "
         "previa messa fuori servizio e svuotamento degli impianti. I gas refrigeranti dei condizionatori sono "
         "recuperati da tecnico certificato (Reg. UE 2024/573, D.P.R. 146/2018) e le coibentazioni sospette "
         "sono analizzate prima di toccarle.",
         "Addetto alla rimozione di impianti tecnologici", 70, EDILIZIA,
         ["Smerigliatrice angolare", "Cannello ossiacetilenico", "Trapano elettrico", "Trabattello",
          "Scala doppia", "Utensili manuali"], [
             _ELETTRO_IMPIANTI,
             r("Incendio ed esplosione", 1, 4,
               "Tubazioni gas scollegate e bonificate dall'ente o da impresa abilitata prima del taglio; "
               "serbatoi di gasolio svuotati; preferire il taglio a freddo sulle tubazioni di combustibile."),
             r("Getti e schizzi", 2, 2,
               "Impianti idrici e termici chiusi e svuotati prima dello smontaggio; scarico dell'acqua "
               "residua nei punti bassi con recipienti.", DPI_BASE + ", occhiali protettivi"),
             _AMIANTO_IMPREVISTO,
             r("Rischio biologico", 2, 2,
               "Scarichi e sanitari: lavare e disinfettare prima dello smontaggio, chiudere gli scarichi "
               "aperti; guanti impermeabili e igiene delle mani.", DPI_BASE + ", guanti in lattice o nitrile"),
             _MMC, _PUNTURE,
         ]),
    fase("DM.15", DEM, _G_MAC, "Carico e trasporto delle macerie",
         "Raccolta delle macerie ai piani e loro discesa con canale di scarico o montacarichi, carico su "
         "autocarro con pala, miniescavatore o a mano e trasporto agli impianti di recupero o smaltimento "
         "con formulario. Il cassone viene coperto o bagnato per evitare la dispersione di polveri lungo il "
         "percorso.",
         "Addetto al carico e trasporto delle macerie", 40, TUTTE,
         ["Pala meccanica", "Minipala (skid loader)", "Miniescavatore", "Autocarro", "Dumper",
          "Montacarichi a cremagliera", "Canale di scarico delle macerie", "Utensili manuali"], [
             _INVESTIMENTO,
             r("Caduta di materiale dall'alto o a livello", 3, 3,
               "Sosta vietata allo sbocco del canale durante lo scarico (art. 154 c. 2); canale chiuso con "
               "sbocco a non più di 2 m dal cassone (art. 153); nessuno vicino al cassone durante il carico "
               "con la benna."),
             r("Polveri e fibre", 3, 2,
               "Bagnatura delle macerie e della viabilità di cantiere; cassoni coperti con teloni durante il "
               "trasporto; pulizia delle ruote prima dell'uscita su strada.", _DPI_POLVERI),
             _MMC, _PUNTURE,
         ]),
    fase("DM.16", DEM, _G_MAC, "Deposito temporaneo, selezione e gestione dei rifiuti da demolizione",
         "Separazione delle macerie per codice EER (calcestruzzo, laterizi, metalli, legno, plastica, "
         "rifiuti pericolosi) e loro deposito temporaneo in cassoni o aree distinte ed etichettate, nei "
         "limiti dell'art. 185-bis del D.Lgs. 152/2006. Il mezzo con pinza selezionatrice separa le frazioni "
         "più grandi; gli addetti a terra separano a mano i materiali minuti solo a mezzo fermo.",
         "Addetto alla gestione dei rifiuti da demolizione", 45, TUTTE,
         ["Escavatore con pinza demolitrice", "Miniescavatore", "Autocarro con gru", "Utensili manuali"], [
             _INVESTIMENTO, _PUNTURE, _MMC,
             r("Rischio chimico", 2, 3,
               "Rifiuti pericolosi (oli, vernici, guaine catramose, materiali isolanti) tenuti separati in "
               "contenitori chiusi ed etichettati, su superficie impermeabile; schede di sicurezza o analisi "
               "per i rifiuti non noti.", DPI_BASE + ", guanti in lattice o nitrile"),
             r("Polveri e fibre", 2, 2,
               "Cumuli bagnati o coperti con teli; non selezionare a mano materiale polveroso a secco.",
               DPI_BASE + ", facciale filtrante FFP2"),
             r("Crollo o ribaltamento di strutture", 2, 3,
               "Cumuli di altezza limitata e con scarpa naturale stabile; vietato salire sui cumuli o "
               "prelevare materiale alla loro base."),
         ]),
]

# =====================================================================================
# BONIFICHE
# =====================================================================================

_G_CAM = "Organizzazione del cantiere di bonifica dell'amianto"
_G_COMP = "Bonifica di materiali compatti contenenti amianto"
_G_FRI = "Bonifica di materiali friabili contenenti amianto"
_G_BOB = "Bonifica da ordigni bellici"
_G_SITI = "Bonifica di siti contaminati"

_INFO_AMIANTO = ("lavoratori formati secondo il D.P.R. 8/8/1994 e l'art. 258, idonei alla sorveglianza "
                 "sanitaria e iscritti nel registro degli esposti (art. 243)")

_AMIANTO_COMPATTO = r("Esposizione ad amianto", 3, 4,
                      "Lavoro secondo il piano di lavoro approvato (art. 256) e il D.M. 6/9/1994; materiale "
                      "trattato con incapsulante prima di ogni manipolazione; vietati utensili ad alta velocità "
                      "(flessibili, seghe, trapani) e getti in pressione; elementi rimossi interi senza "
                      "rotture; monitoraggio delle fibre aerodisperse sotto il valore limite di 0,1 ff/cm³ "
                      "(art. 254); " + _INFO_AMIANTO + "; decontaminazione all'uscita.",
                      _DPI_AMIANTO_C_QUOTA)
_AMIANTO_FRIABILE = r("Esposizione ad amianto", 3, 4,
                      "Lavori solo in area confinata in depressione con unità di decontaminazione a quattro "
                      "stadi (D.M. 6/9/1994); materiale imbibito a fondo prima della rimozione e raccolto "
                      "subito in sacchi; turni con durata limitata dal tipo di DPI; ingresso e uscita solo "
                      "attraverso l'unità di decontaminazione con doccia; " + _INFO_AMIANTO + ".",
                      _DPI_AMIANTO_F)
_MICROCLIMA_TUTA = r("Microclima", 3, 2,
                     "Tuta monouso e respiratore aumentano il carico termico: turni brevi, pause in zona "
                     "pulita con acqua a disposizione, lavori in copertura nelle ore fresche.", _DPI_AMIANTO_C)
_CADUTA_FRAGILE = r("Caduta dall'alto dal bordo e attraverso la copertura", 3, 4,
                    "Le lastre in cemento-amianto non reggono il peso di una persona: mai camminarvi sopra, "
                    "ma usare andatoie ripartitrici o piattaforme elevabili; reti anticaduta o impalcato "
                    "sotto la copertura; ponteggio o parapetti al bordo; linea vita con imbracatura e "
                    "dispositivo retrattile.", _DPI_AMIANTO_C_QUOTA)

_BONIFICHE = [
    fase("BO.01", BON, _G_CAM, "Allestimento del cantiere di bonifica dell'amianto",
         "Dopo la notifica (art. 250) e la presentazione del piano di lavoro all'organo di vigilanza almeno 30 "
         "giorni prima dell'inizio (art. 256), si delimita e segnala la zona di lavoro, si installa l'unità "
         "di decontaminazione e si predispone l'area di deposito dei rifiuti. L'impresa deve essere iscritta "
         "all'Albo nazionale gestori ambientali, categoria 10 (A per i compatti, B per i friabili).",
         "Addetto all'allestimento del cantiere di bonifica dell'amianto", 45, TUTTE,
         ["Unità di decontaminazione (amianto)", "Autocarro con gru", "Trapano elettrico",
          "Utensili manuali"], [
             r("Esposizione ad amianto", 2, 4,
               "Nessuna manipolazione dei materiali in questa fase; delimitazione con cartelli di pericolo "
               "e divieto di accesso ai non addetti; unità di decontaminazione installata e collaudata "
               "prima dell'inizio della rimozione, con scarico delle acque di doccia filtrato.",
               DPI_BASE + ", facciale filtrante FFP3"),
             _MMC, _INVESTIMENTO,
             r("Elettrocuzione", 1, 4,
               "Alimentazione dell'unità di decontaminazione e dei boiler da quadro di cantiere con "
               "differenziale; cavi protetti dall'acqua e dal passaggio dei mezzi."),
         ]),
    fase("BO.02", BON, _G_CAM, "Confezionamento, deposito e trasporto dei rifiuti contenenti amianto",
         "I materiali rimossi vengono chiusi in doppio involucro di polietilene o in big-bag, etichettati con "
         "la «a» dell'amianto e il codice EER (17 06 05* per i compatti, 17 06 01* per gli isolanti), "
         "depositati in area recintata e coperta e trasportati a discarica autorizzata con formulario e in "
         "regime ADR. I sacchi vengono puliti con aspirazione HEPA o panni umidi prima dell'uscita dall'area.",
         "Addetto al confezionamento e trasporto dei rifiuti contenenti amianto", 40, TUTTE,
         ["Autocarro con gru", "Carrello elevatore", "Aspiratore con filtro HEPA", "Utensili manuali"], [
             r("Esposizione ad amianto", 2, 4,
               "Imballi integri, chiusi e sovrapposti senza strisciare; lacerazioni subito riparate con "
               "nastro o sovraimballo; vietato comprimere o rompere il materiale per ridurne il volume.",
               _DPI_AMIANTO_C),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Pallet stabili e reggiati; sollevamento con forche o imbracature idonee; nessuno sotto il "
               "carico sospeso."),
             _MMC, _INVESTIMENTO,
         ]),
    fase("BO.03", BON, _G_COMP, "Rimozione di coperture in cemento-amianto",
         "Le lastre vengono trattate su entrambe le facce con incapsulante del tipo D (D.M. 20/8/1999) a "
         "bassa pressione, smontate intere svitando o tranciando i ganci di fissaggio senza romperle e calate "
         "a terra su bancali. I canali di gronda, spesso pieni di materiale sbriciolato, vengono puliti a umido "
         "o con aspiratore HEPA; a fine lavoro si ispeziona e incapsula la struttura sottostante.",
         "Addetto alla rimozione di coperture in cemento-amianto", 55, TUTTE,
         ["Nebulizzatore a bassa pressione", "Piattaforma di lavoro elevabile", "Ponteggio metallico fisso",
          "Rete di sicurezza anticaduta", "Linea vita provvisoria", "Andatoie e passerelle",
          "Aspiratore con filtro HEPA", "Autogru", "Unità di decontaminazione (amianto)",
          "Utensili manuali"], [
             _AMIANTO_COMPATTO, _CADUTA_FRAGILE,
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Pacchi di lastre avvolti nel polietilene e imbracati con fasce, calati con la gru senza urti; "
               "area sottostante interdetta; non lanciare né far scivolare le lastre."),
             _MICROCLIMA_TUTA,
             r("Scivolamenti e cadute a livello", 3, 3,
               "Superfici bagnate dall'incapsulante molto scivolose: procedere sui camminamenti con calzature "
               "a suola antiscivolo; non lavorare con pioggia o vento.", _DPI_AMIANTO_C_QUOTA),
         ]),
    fase("BO.04", BON, _G_COMP, "Rimozione di canne fumarie, serbatoi e manufatti in cemento-amianto",
         "Smontaggio di canne fumarie, comignoli, serbatoi d'acqua e pannelli in cemento-amianto, previa "
         "bagnatura con incapsulante ed eventuale svuotamento. I tratti di canna si separano dai giunti "
         "senza spaccarli, procedendo dall'alto e calandoli imbracati; i serbatoi in sottotetto o nei "
         "locali vengono avvolti nel polietilene prima di essere spostati.",
         "Addetto alla rimozione di manufatti in cemento-amianto", 60, EDILIZIA,
         ["Nebulizzatore a bassa pressione", "Aspiratore con filtro HEPA", "Ponteggio metallico fisso",
          "Trabattello", "Argano a bandiera", "Unità di decontaminazione (amianto)", "Utensili manuali"], [
             _AMIANTO_COMPATTO,
             r("Caduta dall'alto", 2, 4,
               "Canne fumarie esterne smontate dal ponteggio o da piattaforma, mai appoggiandosi alla canna; "
               "in copertura parapetti o linea vita.", _DPI_AMIANTO_C_QUOTA),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Tronchi di canna imbracati prima di staccare il giunto; calo con argano; zona sottostante "
               "sbarrata."),
             r("Movimentazione manuale dei carichi", 3, 2,
               "Serbatoi movimentati in due o con mezzi di sollevamento; percorsi sgombri; peso stimato "
               "prima dello spostamento.", _DPI_AMIANTO_C),
             r("Ambienti confinati o sospetti di inquinamento", 1, 3,
               "Sottotetti e cavedi ristretti: ventilazione, illuminazione, sorveglianza dall'esterno da "
               "parte di un collega e via di uscita libera.", _DPI_AMIANTO_C),
         ]),
    fase("BO.05", BON, _G_COMP, "Incapsulamento di coperture in cemento-amianto",
         "Pulizia a umido della superficie con spazzole morbide e raccolta dei residui, quindi applicazione "
         "a pennello o con pompa airless di più strati di prodotto incapsulante del tipo previsto dal D.M. "
         "20/8/1999 (tipo A per le superfici esterne a vista), con colori diversi tra le mani per controllare "
         "la copertura. Al termine si documenta lo spessore applicato e si avvia il programma di controllo "
         "periodico.",
         "Addetto all'incapsulamento di coperture in cemento-amianto", 50, TUTTE,
         ["Pistola a spruzzo (airless)", "Nebulizzatore a bassa pressione", "Aspiratore con filtro HEPA",
          "Piattaforma di lavoro elevabile", "Rete di sicurezza anticaduta", "Linea vita provvisoria",
          "Andatoie e passerelle", "Unità di decontaminazione (amianto)", "Utensili manuali"], [
             r("Esposizione ad amianto", 2, 4,
               "Vietate idropulitrici, spazzole metalliche e abrasivi: pulizia solo a umido e a bassa "
               "pressione con raccolta e filtraggio delle acque; applicazione secondo il piano di lavoro; "
               + _INFO_AMIANTO + ".", _DPI_AMIANTO_C_QUOTA),
             _CADUTA_FRAGILE,
             r("Rischio chimico", 2, 2,
               "Prodotti incapsulanti usati secondo scheda di sicurezza; nebulizzazione con il vento a "
               "favore e lontano da prese d'aria degli edifici; occhiali contro gli schizzi.",
               _DPI_AMIANTO_C_QUOTA + ", occhiali a maschera"),
             _MICROCLIMA_TUTA,
         ]),
    fase("BO.06", BON, _G_COMP, "Sovracopertura (confinamento) di coperture in cemento-amianto",
         "Posa di una nuova copertura in lamiera o pannelli sopra le lastre esistenti, lasciate in opera dopo "
         "il trattamento con incapsulante. I fissaggi vanno ancorati alla struttura portante attraverso le "
         "lastre con fori eseguiti a bassa velocità e con aspirazione, oppure con staffe che evitano di "
         "forarle; occorre prima verificare che la struttura regga il carico aggiunto.",
         "Addetto alla sovracopertura di coperture in cemento-amianto", 45, TUTTE,
         ["Nebulizzatore a bassa pressione", "Avvitatore elettrico", "Trapano elettrico",
          "Aspiratore con filtro HEPA", "Autogru", "Piattaforma di lavoro elevabile",
          "Rete di sicurezza anticaduta", "Linea vita provvisoria", "Andatoie e passerelle",
          "Unità di decontaminazione (amianto)"], [
             r("Esposizione ad amianto", 2, 4,
               "Lastre incapsulate prima della posa; fori sulle lastre limitati al minimo, eseguiti a bassa "
               "velocità su superficie bagnata e con aspirazione HEPA alla punta; detriti raccolti come "
               "rifiuto contenente amianto; " + _INFO_AMIANTO + ".", _DPI_AMIANTO_C_QUOTA),
             _CADUTA_FRAGILE,
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Pacchi di lamiere appoggiati solo in corrispondenza della struttura portante e legati contro "
               "il vento; calo e sollevamento guidati con funi; zona sottostante interdetta."),
             r("Punture, tagli e abrasioni", 3, 2,
               "Lamiere afferrate con guanti antitaglio; bordi tagliati ripiegati o protetti.",
               _DPI_QUOTA + ", guanti antitaglio"),
             _MICROCLIMA_TUTA,
         ]),
    fase("BO.07", BON, _G_FRI, "Allestimento del confinamento statico e dinamico",
         "Rimozione degli arredi o loro protezione, sigillatura di aperture e impianti di ventilazione e "
         "rivestimento di pareti e pavimenti con teli di polietilene in più strati (confinamento statico). "
         "Si collegano l'unità di decontaminazione e gli estrattori con filtro assoluto che tengono l'area in "
         "depressione con un numero adeguato di ricambi d'aria orari (confinamento dinamico), e si verifica la "
         "tenuta con fumogeni e manometro prima di iniziare.",
         "Addetto all'allestimento del confinamento per la bonifica dell'amianto friabile", 55, EDILIZIA,
         ["Estrattore d'aria con filtro assoluto HEPA (depressore)", "Unità di decontaminazione (amianto)",
          "Aspiratore con filtro HEPA", "Trabattello", "Scala doppia", "Pistola sparachiodi",
          "Utensili manuali"], [
             r("Esposizione ad amianto", 2, 4,
               "Materiali friabili non toccati durante la posa dei teli; eventuali parti danneggiate "
               "nebulizzate con incapsulante; dopo il collaudo l'accesso avviene solo attraverso l'unità "
               "di decontaminazione; " + _INFO_AMIANTO + ".", _DPI_AMIANTO_F),
             r("Caduta dall'alto", 2, 3,
               "Trabattelli con parapetti e ruote bloccate; scale doppie solo per brevi interventi; teli "
               "sul pavimento fissati per non scivolare.", "Casco, calzature di sicurezza, guanti, tuta monouso"),
             r("Incendio ed esplosione", 1, 3,
               "Il polietilene è combustibile: vietate fiamme libere e lavori a caldo nell'area confinata; "
               "estintori e vie di esodo segnalate e mantenute apribili dall'interno.",
               "Casco, calzature di sicurezza, guanti, tuta monouso"),
             r("Elettrocuzione", 1, 4,
               "Impianti dell'area messi fuori tensione; estrattori e illuminazione alimentati da quadro di "
               "cantiere con differenziale e con apparecchi a protezione IP adatta al lavaggio."),
         ]),
    fase("BO.08", BON, _G_FRI, "Rimozione di materiali friabili contenenti amianto in area confinata",
         "Rimozione a umido di coibentazioni di tubazioni e caldaie, intonaci e rivestimenti a spruzzo "
         "(floccati), cartoni e pannelli isolanti, dopo averli imbibiti a fondo con acqua e tensioattivo o "
         "incapsulante. Il materiale viene staccato con raschietti e spatole, insaccato subito nell'area e "
         "fatto uscire dopo la pulizia dei sacchi attraverso il tunnel o la chiusa dei materiali; per le "
         "tubazioni si può usare il metodo glove-bag.",
         "Addetto alla rimozione di materiali friabili contenenti amianto", 70, EDILIZIA,
         ["Nebulizzatore a bassa pressione", "Aspiratore con filtro HEPA",
          "Estrattore d'aria con filtro assoluto HEPA (depressore)", "Unità di decontaminazione (amianto)",
          "Trabattello", "Utensili manuali"], [
             _AMIANTO_FRIABILE,
             r("Microclima", 3, 3,
               "Ambiente umido e chiuso con DPI integrali: turni di durata limitata, pause fuori dall'area "
               "dopo la decontaminazione, acqua disponibile; attenzione ai segni di colpo di calore.",
               _DPI_AMIANTO_F),
             r("Scivolamenti e cadute a livello", 3, 2,
               "Pavimento bagnato e coperto di teli: rimozione continua dei detriti, sacchi allontanati "
               "subito, illuminazione adeguata.", _DPI_AMIANTO_F),
             r("Posture incongrue", 3, 2,
               "Lavori su tubazioni e a soffitto: piani di lavoro all'altezza giusta e rotazione degli "
               "addetti.", _DPI_AMIANTO_F),
             r("Elettrocuzione", 1, 4,
               "Nessuna parte d'impianto in tensione nell'area; utensili elettrici a bassissima tensione di "
               "sicurezza o con doppio isolamento adatti agli ambienti bagnati.", _DPI_AMIANTO_F),
         ]),
    fase("BO.09", BON, _G_FRI, "Pulizia finale, smantellamento del confinamento e restituibilità",
         "Pulizia a umido e con aspiratore HEPA di tutte le superfici, applicazione di un fissativo sulle "
         "superfici bonificate e rimozione progressiva del primo strato di teli, smaltiti come rifiuto "
         "contenente amianto. L'area resta confinata fino alla certificazione di restituibilità della ASL "
         "prevista dal D.M. 6/9/1994 (ispezione visiva e campionamento aggressivo dell'aria con analisi in "
         "microscopia elettronica, limite di 2 fibre/litro); solo dopo si smontano estrattori e unità di "
         "decontaminazione.",
         "Addetto alla pulizia finale e allo smantellamento del confinamento", 60, EDILIZIA,
         ["Aspiratore con filtro HEPA", "Nebulizzatore a bassa pressione",
          "Estrattore d'aria con filtro assoluto HEPA (depressore)", "Unità di decontaminazione (amianto)",
          "Trabattello", "Utensili manuali"], [
             r("Esposizione ad amianto", 2, 4,
               "Nessuna pulizia a secco né con aria compressa; teli staccati arrotolandoli verso l'interno "
               "dopo la nebulizzazione; depressione mantenuta fino al rilascio della restituibilità; "
               + _INFO_AMIANTO + ".", _DPI_AMIANTO_F),
             r("Caduta dall'alto", 2, 3,
               "Trabattelli per la pulizia delle parti alte; vietato salire su arredi o tubazioni.",
               _DPI_AMIANTO_F + ", casco"),
             _MMC,
             r("Rischio chimico", 2, 2,
               "Fissativi e prodotti di pulizia usati secondo scheda di sicurezza; ricambio d'aria garantito "
               "dagli estrattori.", _DPI_AMIANTO_F),
         ]),
    fase("BO.10", BON, _G_BOB, "Bonifica superficiale da ordigni bellici",
         "Ricerca di ordigni residuati bellici nello strato superficiale del terreno con rilevatore di masse "
         "metalliche, per strisce parallele delimitate da picchetti, dopo il taglio della vegetazione. È "
         "eseguita solo da impresa specializzata iscritta all'albo del Ministero della Difesa (art. 104 "
         "c. 4-bis, D.M. 82/2015) con personale brevettato, secondo le prescrizioni dell'autorità militare "
         "competente, quando il coordinatore ne valuta la necessità (art. 91 c. 2-bis).",
         "Addetto alla bonifica superficiale da ordigni bellici", 45, ("Nuove costruzioni", "Opere infrastrutturali"),
         ["Rilevatore di masse metalliche (magnetometro)", "Decespugliatore a motore", "Miniescavatore",
          "Utensili manuali"], [
             r("Incendio ed esplosione", 2, 4,
               "Ricerca e scoprimento delle anomalie solo da rastrellatori brevettati, a mano e con cautela, "
               "senza colpire il terreno con attrezzi; ordigno trovato lasciato dov'è, area sgombrata e "
               "segnalata e intervento richiesto all'autorità militare per il disinnesco; nessun altro "
               "lavoro nell'area fino al verbale di bonifica."),
             r("Rischio biologico", 2, 2,
               "Indumenti chiusi e a maniche lunghe contro zecche e insetti; repellenti; controllo della pelle "
               "a fine turno.", DPI_BASE + ", stivali di sicurezza"),
             r("Microclima", 3, 2,
               "Lavoro all'aperto e prolungato: pause, acqua e zone d'ombra; sospensione con temporali.",
               DPI_BASE + ", copricapo"),
             r("Posture incongrue", 3, 2,
               "Strumento con bracci regolabili; alternanza tra ricerca e scoprimento delle anomalie."),
             r("Scivolamenti e cadute a livello", 2, 2,
               "Percorsi e strisce di ricerca liberati dalla vegetazione; calzature con suola profonda su "
               "terreni sconnessi.", DPI_BASE + ", stivali di sicurezza"),
         ]),
    fase("BO.11", BON, _G_BOB, "Bonifica profonda da ordigni bellici",
         "Ricerca in profondità mediante perforazioni disposte a maglia regolare, in cui si cala la sonda del "
         "magnetometro, oppure per scavi successivi a strati sempre preceduti dal controllo strumentale del "
         "fondo. Le perforazioni non devono mai attraversare uno strato non ancora verificato; l'attività è "
         "riservata a impresa specializzata iscritta all'albo e segue le regole tecniche dell'autorità "
         "militare competente.",
         "Addetto alla bonifica profonda da ordigni bellici", 40, ("Nuove costruzioni", "Opere infrastrutturali"),
         ["Sonda di perforazione (micropali, tiranti, sondaggi)", "Rilevatore di masse metalliche (magnetometro)",
          "Escavatore", "Autocarro", "Utensili manuali"], [
             r("Incendio ed esplosione", 2, 4,
               "Avanzamento della perforazione o dello scavo solo per tratti già verificati dalla sonda; "
               "arresto immediato su ogni anomalia, scoprimento manuale da parte di personale brevettato; "
               "area di rispetto sgombra durante lo scavo delle anomalie; ordigni segnalati all'autorità "
               "militare."),
             r("Seppellimento e sprofondamento", 2, 4,
               "Scavi delle anomalie con pareti inclinate o armate oltre 1,50 m (art. 119); nessun addetto "
               "nello scavo durante l'azione del mezzo; materiale di scavo lontano dal ciglio."),
             _INVESTIMENTO,
             r("Rumore", 3, 2,
               "Addetti alla sonda e alla lettura dei dati lontani dalla macchina perforatrice quando non "
               "necessari; rotazione.", DPI_BASE + ", otoprotettori"),
             _MMC,
         ]),
    fase("BO.12", BON, _G_SITI, "Scavo e rimozione di terreni contaminati",
         "Scavo selettivo dei terreni inquinati secondo il progetto operativo di bonifica approvato (art. 242 "
         "D.Lgs. 152/2006), con separazione per tipo di contaminazione, deposito su teli impermeabili e "
         "coperti e carico su mezzi a tenuta per lo smaltimento o il trattamento. L'avanzamento è guidato da "
         "campionamenti del fondo e delle pareti dello scavo e dal monitoraggio dell'aria; mezzi e addetti si "
         "decontaminano all'uscita dall'area.",
         "Addetto allo scavo e alla rimozione di terreni contaminati", 25, ("Ristrutturazioni", "Opere infrastrutturali", "Nuove costruzioni"),
         ["Escavatore", "Pala meccanica", "Autocarro", "Rilevatore multigas", "Idropulitrice",
          "Pompa sommersa", "Utensili manuali"], [
             r("Rischio chimico", 3, 3,
               "Valutazione del rischio sugli inquinanti individuati dalla caratterizzazione (Titolo IX Capi I "
               "e II); cabine dei mezzi chiuse e pressurizzate con filtri; monitoraggio di vapori e polveri "
               "con soglie di intervento; zona pulita, zona sporca e lavaggio di mezzi e stivali all'uscita; "
               "divieto di mangiare e fumare nell'area.",
               DPI_BASE + ", maschera con filtro specifico, tuta monouso, guanti in lattice o nitrile, "
                          "stivali di sicurezza"),
             r("Polveri e fibre", 3, 2,
               "Bagnatura dei fronti e dei cumuli; teli di copertura sui depositi e sui cassoni; sospensione "
               "con vento forte.", DPI_BASE + ", facciale filtrante FFP3"),
             r("Seppellimento e sprofondamento", 2, 4,
               "Pareti dello scavo profilate con pendenza stabile o armate (art. 118-119); accesso al fondo "
               "scavo solo per i campionamenti, con scala e a mezzo fermo."),
             r("Ambienti confinati o sospetti di inquinamento", 2, 4,
               "Scavi profondi e pozzetti possono accumulare gas e vapori: misura con rilevatore multigas "
               "prima dell'accesso, ventilazione, sorvegliante all'esterno; per gli spazi confinati veri e "
               "propri si applica il D.P.R. 177/2011.", DPI_BASE + ", maschera con filtro specifico"),
             _INVESTIMENTO,
         ]),
    fase("BO.13", BON, _G_SITI, "Rimozione di serbatoi interrati",
         "Svuotamento del serbatoio dai residui con autospurgo, bonifica interna, degassificazione o "
         "inertizzazione e misura dell'atmosfera fino all'attestazione di assenza di gas (gas-free) da parte "
         "di tecnico abilitato. Si scopre poi il serbatoio, lo si scollega dalle tubazioni, lo si imbraca e "
         "lo si estrae con la gru per avviarlo a smaltimento; si campionano fondo e pareti dello scavo per "
         "verificare eventuali contaminazioni del terreno.",
         "Addetto alla rimozione di serbatoi interrati", 35, ("Ristrutturazioni", "Opere infrastrutturali", "Nuove costruzioni"),
         ["Autospurgo", "Rilevatore multigas", "Ventilatore estrattore", "Escavatore", "Autogru",
          "Autocarro", "Utensili manuali"], [
             r("Incendio ed esplosione", 2, 4,
               "Nessun taglio o lavoro a caldo prima dell'attestazione gas-free; zona classificata secondo il "
               "Titolo XI durante svuotamento e degassificazione, con attrezzature adatte e messa a terra; "
               "taglio a freddo delle tubazioni; estintori presenti."),
             r("Ambienti confinati o sospetti di inquinamento", 2, 4,
               "Ingresso nel serbatoio evitato privilegiando la pulizia dall'esterno; se indispensabile, "
               "solo da impresa qualificata secondo il D.P.R. 177/2011 con permesso di lavoro, misura continua "
               "dell'atmosfera, ventilazione forzata, imbracatura di recupero e sorvegliante esterno con "
               "procedura di emergenza.", DPI_BASE + ", autorespiratore, imbracatura"),
             r("Rischio chimico", 3, 3,
               "Residui di idrocarburi e fanghi maneggiati in sistema chiuso con autospurgo; contenimento di "
               "sversamenti con materiali assorbenti; lavaggio della pelle in caso di contatto.",
               DPI_BASE + ", maschera con filtro specifico, guanti in lattice o nitrile, tuta monouso"),
             r("Seppellimento e sprofondamento", 2, 4,
               "Scavo attorno al serbatoio con pareti inclinate o armate; nessuno nello scavo durante "
               "il sollevamento e l'estrazione."),
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Serbatoio imbracato in punti verificati e sollevato con gru di portata adeguata; addetti "
               "fuori dal raggio di caduta, guida del carico con funi."),
         ]),
]

LAVORAZIONI = _DEMOLIZIONI + _BONIFICHE
