"""Attrezzi dell'archivio (parte A): utensili per forare, demolire, tagliare e costipare,
lavorazione del ferro d'armatura, saldatura del polietilene e cannello ossiacetilenico.

Testi scritti da zero per questo progetto. Fonti consultate (solo come riferimento):
- D.Lgs. 81/2008: Titolo III (artt. 70-73, Allegato V), Titolo VIII, Capi II (rumore, artt.
  187-198) e III (vibrazioni, artt. 199-205), Titolo IX, Capi I e II (agenti chimici e
  cancerogeni; silice cristallina respirabile in Allegato XLII dal D.Lgs. 44/2020).
- INAIL e Portale Agenti Fisici (banche dati rumore e vibrazioni, consultate per gli ordini di
  grandezza, senza riportarne i valori); opuscolo AUSL Bologna «Silice libera cristallina»
  (2022); schede NIS (Network Italiano Silice) sulla perforazione e sul taglio.
- Indicazioni generali sull'uso dell'acetilene (procedura Università di Parma; articoli
  PuntoSicuro sull'acetilene) e circolare del Ministero del lavoro n. 17/1984 sui dispositivi contro il ritorno
  di fiamma.
- Norme di prodotto: CEI EN 62841 (utensili elettrici portatili), UNI EN ISO 11148 (utensili
  pneumatici), UNI EN 15895 (utensili a cartuccia), UNI EN ISO 19432-1 (troncatrici a motore),
  UNI EN 13862 (seghe da pavimento), UNI EN 15027 (seghe da parete e a filo), UNI EN 12348 (carotatrici
  su supporto), UNI EN 500-4 (macchine per la compattazione), UNI EN 12649 (vibratori e lisciatrici
  per calcestruzzo), UNI 10520/10521 e UNI 9737 (saldatura del polietilene), UNI EN ISO 5172 e
  UNI EN ISO 5175 (cannelli e dispositivi di sicurezza per gas).
Le misure vanno sempre adattate alle istruzioni del fabbricante dell'attrezzo usato.
NOTA: le ricerche in rete sono state interrotte dal limite di utilizzo durante la redazione; non
tutte le fonti elencate sono state rilette per intero e diversi riferimenti sono citati da
conoscenze normative. Prima dell'uso professionale vedere docs/verifiche-archivio.md.
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import ATTREZZO, DPI_BASE, attrezzatura, r, scheda

# --- Rischi ricorrenti, scritti in forma parametrica per restare specifici --------------------

_ELETTROCUZIONE = r(
    "Elettrocuzione", 1, 4,
    "Utensile marcato CE a doppio isolamento (classe II) o collegato a terra; alimentazione da quadro "
    "di cantiere conforme (CEI EN 61439-4) con interruttore differenziale da 30 mA; cavi per posa mobile "
    "(H07RN-F o equivalenti) integri, sollevati da terra e lontani da acqua e spigoli; controllo "
    "visivo di cavo e spina prima dell'uso (art. 80 e art. 71, comma 4, D.Lgs. 81/2008).")


def _rumore(p: int, d: int, nota: str) -> dict:
    return r("Rumore", p, d,
             f"{nota} Valutazione del rumore secondo il Titolo VIII, Capo II, D.Lgs. 81/2008 con "
             "riferimento ai dati del fabbricante; sopra 80 dB(A) informazione e DPI a disposizione, "
             "sopra 85 dB(A) uso obbligatorio degli otoprotettori, segnaletica e sorveglianza sanitaria; "
             "turnazione degli addetti e distanza dagli altri posti di lavoro.",
             DPI_BASE + ", otoprotettori")


def _vibrazioni_mb(p: int, d: int, nota: str) -> dict:
    return r("Vibrazioni al sistema mano-braccio", p, d,
             f"{nota} Valutazione dell'esposizione (artt. 199-205 D.Lgs. 81/2008: valore d'azione "
             "2,5 m/s² e limite 5 m/s² riferiti a 8 ore) sulla base del valore dichiarato dal "
             "fabbricante; utensili con impugnature antivibranti; pause e rotazione degli addetti; "
             "manutenzione di utensili e inserti; sorveglianza sanitaria oltre il valore d'azione.",
             DPI_BASE + ", guanti antivibrazioni")


def _silice(p: int, d: int, nota: str) -> dict:
    return r("Polveri e fibre: silice cristallina respirabile", p, d,
             f"{nota} Il lavoro rientra tra quelli dell'Allegato XLII (Titolo IX, Capo II, D.Lgs. "
             "81/2008, valore limite 0,1 mg/m³): abbattimento alla fonte con acqua o aspirazione "
             "collegata all'utensile (aspiratore di classe M o H); niente pulizia a secco o con aria "
             "compressa; area delimitata e altri lavoratori lontani; registro degli esposti e "
             "sorveglianza sanitaria secondo la valutazione.",
             DPI_BASE + ", facciale filtrante FFP3, occhiali protettivi")


def _proiezione(p: int, d: int, nota: str) -> dict:
    return r("Proiezione di schegge e frammenti", p, d, nota, DPI_BASE + ", occhiali protettivi")


_ELETTRICO_PRIMA = [
    "verificare integrità di involucro, cavo e spina e la marcatura CE",
    "alimentare da quadro di cantiere con differenziale da 30 mA, con cavo sollevato da terra",
]
_ELETTRICO_DOPO = [
    "staccare la spina prima di pulire o cambiare l'inserto",
    "riporre l'utensile pulito e segnalare guasti o danni al preposto",
]

# --- Schede ------------------------------------------------------------------------------------

ATTREZZATURE = {
    "Martello perforatore (tassellatore)": attrezzatura(
        ATTREZZO,
        rischi=[
            _ELETTROCUZIONE,
            r("Contatto con impianti nascosti (cavi elettrici, tubazioni)", 2, 4,
              "Esame degli schemi degli impianti e ricerca con rilevatore prima di forare; nessuna "
              "foratura in corrispondenza di tracce verticali e orizzontali di impianti; impianti "
              "sezionati quando non se ne conosce il percorso.", DPI_BASE),
            r("Urti, colpi, impatti e compressioni: contraccolpo per bloccaggio della punta", 2, 3,
              "Utensile con frizione di sicurezza o arresto elettronico al bloccaggio (CEI EN 62841-2-6); "
              "impugnatura laterale sempre montata e presa salda con due mani; posizione stabile, mai "
              "su scale a mano in equilibrio precario; punte affilate e adatte al materiale.", DPI_BASE),
            _vibrazioni_mb(3, 2, "Uso della sola rotazione quando la percussione non serve; non "
                           "premere oltre quanto indicato dal fabbricante."),
            _rumore(3, 2, "Utensile di modello a bassa emissione."),
            _silice(3, 3, "Fori in calcestruzzo, laterizio e pietra con utensile dotato di "
                    "aspirazione integrata o cuffia collegata all'aspiratore."),
            _proiezione(2, 2, "Fermare l'utensile prima di estrarre la punta da fori profondi; "
                        "non lavorare sopra la testa senza occhiali; tenere lontane altre persone."),
        ],
        scheda_uso=scheda(
            "Utensile elettrico portatile con meccanismo a percussione pneumatica, per forare "
            "calcestruzzo, murature e pietra e posare tasselli; può avere la funzione di sola "
            "scalpellatura.",
            _ELETTRICO_PRIMA + [
                "controllare che la frizione di sicurezza funzioni e che l'impugnatura laterale sia serrata",
                "scegliere punta e attacco (SDS) adatti al materiale e al diametro del foro",
                "individuare con il rilevatore cavi e tubazioni nella zona da forare",
                "collegare l'aspirazione o la cuffia raccoglipolvere",
            ],
            [
                "tenere l'utensile con due mani e il corpo fuori dalla traiettoria in caso di bloccaggio",
                "lavorare da posizione stabile (trabattello o ponte su cavalletti, non scala in equilibrio)",
                "lasciare lavorare l'utensile senza forzare e fare pause per limitare le vibrazioni",
                "non toccare la punta subito dopo l'uso: è molto calda",
                "non soffiare la polvere dal foro: usare la pompetta o l'aspiratore",
            ],
            _ELETTRICO_DOPO + ["pulire e ingrassare l'attacco della punta come indicato dal fabbricante"],
            ["casco", "occhiali protettivi", "otoprotettori", "facciale filtrante FFP3", "guanti antivibrazioni",
             "calzature di sicurezza"]),
    ),
    "Martello demolitore pneumatico": attrezzatura(
        ATTREZZO,
        rischi=[
            _vibrazioni_mb(4, 3, "Utensile pneumatico con impugnature sospese o sistema antivibrante "
                           "(UNI EN ISO 11148-4); pressione d'esercizio quella indicata dal fabbricante; "
                           "turni brevi con pause programmate."),
            _rumore(4, 3, "Silenziatore sullo scarico dell'aria e cappottatura del martello; "
                    "compressore silenziato e posto lontano dagli addetti."),
            _silice(4, 3, "Bagnatura continua della superficie con nebulizzazione d'acqua durante "
                    "la demolizione di calcestruzzo, murature e pietra."),
            _proiezione(3, 2, "Schermi o teli per proteggere i passaggi e le persone vicine; area "
                        "delimitata; utensile (punta o scalpello) integro, con il fermo montato."),
            r("Urti, colpi, impatti e compressioni: colpo di frusta del tubo dell'aria", 2, 3,
              "Tubi e raccordi idonei alla pressione, con dispositivi anti-frusta (fermatubo a cavo) "
              "sui giunti; chiudere l'aria e scaricare la pressione prima di staccare il tubo o "
              "cambiare la punta; tubo protetto dal passaggio di mezzi.", DPI_BASE),
            r("Movimentazione manuale dei carichi e posture incongrue", 3, 2,
              "Scelta di un martello di peso adatto al lavoro; lavoro su superfici orizzontali con "
              "schiena eretta; per pareti e soffitti usare utensili più leggeri o mezzi meccanici; "
              "non sollevare il martello incastrato facendo leva con il corpo.", DPI_BASE),
            r("Caduta del martello sul piede e rottura dello scalpello", 2, 2,
              "Fermo dell'utensile efficiente; scalpelli sostituiti se usurati o deformati; non usare "
              "il martello come leva.", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Martello a percussione alimentato ad aria compressa da un motocompressore, per la "
            "demolizione di pavimentazioni, calcestruzzi e murature.",
            [
                "verificare tubi, raccordi rapidi e fermatubo anti-frusta sui giunti",
                "controllare il fermo della punta e lo stato dello scalpello",
                "verificare il silenziatore e le impugnature antivibranti",
                "delimitare l'area e predisporre l'acqua per la bagnatura",
                "accertarsi dell'assenza di sottoservizi sotto la pavimentazione da rompere",
            ],
            [
                "tenere il martello con entrambe le mani, gambe divaricate e piedi lontani dalla punta",
                "bagnare costantemente la zona di lavoro",
                "non azionare il martello a vuoto né con la punta sollevata",
                "procedere a piccoli tratti dal bordo, evitando che la punta resti incastrata",
                "rispettare le pause programmate per vibrazioni e rumore",
            ],
            [
                "chiudere l'aria al compressore e scaricare la pressione prima di staccare il tubo",
                "riporre il martello pulito, con i tubi avvolti e protetti",
                "segnalare perdite d'aria, vibrazioni anomale o danni",
            ],
            ["casco", "occhiali protettivi", "otoprotettori", "facciale filtrante FFP3", "guanti antivibrazioni",
             "calzature di sicurezza", "indumenti ad alta visibilità"]),
    ),
    "Avvitatore elettrico": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Urti, colpi, impatti e compressioni: contraccolpo e torsione del polso", 2, 2,
              "Regolare la coppia (frizione) in base alla vite; impugnatura salda e polso allineato; "
              "impugnatura ausiliaria per gli avvitatori a impulsi di potenza elevata (CEI EN 62841-2-2).",
              DPI_BASE),
            r("Punture, tagli e abrasioni", 2, 1,
              "Inserti integri e ben bloccati nel mandrino; non tenere il pezzo con la mano nella "
              "traiettoria della vite; lamiere e profili fissati prima dell'avvitatura.",
              DPI_BASE),
            r("Elettrocuzione", 1, 3,
              "Preferire gli avvitatori a batteria; per quelli a cavo, doppio isolamento e quadro con "
              "differenziale da 30 mA; prima di avvitare in pareti e controsoffitti verificare il "
              "passaggio di cavi elettrici.", DPI_BASE),
            r("Incendio ed esplosione: batterie al litio", 1, 3,
              "Usare solo batterie e caricabatterie del fabbricante; ricarica in luogo asciutto e "
              "aerato, lontano da materiali infiammabili; non usare batterie cadute, deformate o "
              "surriscaldate.", DPI_BASE),
            r("Movimenti ripetitivi degli arti superiori", 2, 2,
              "Alternare le mansioni nelle avvitature in serie (cartongesso, pannelli); utensile "
              "leggero e bilanciato; per il lavoro a soffitto usare prolunghe o posizioni rialzate "
              "stabili.", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Utensile portatile, a batteria o a cavo, per avvitare e svitare viti e bulloni, anche "
            "a impulsi; usato nel montaggio di cartongessi, serramenti, carpenterie e impianti.",
            [
                "verificare l'integrità dell'utensile, della batteria o del cavo",
                "scegliere l'inserto adatto alla testa della vite e bloccarlo nel mandrino",
                "regolare la coppia in base al materiale e al tipo di vite",
            ],
            [
                "tenere l'utensile allineato alla vite e il polso dritto",
                "non tenere la mano dietro il pezzo nella traiettoria della vite",
                "non lavorare da scale in equilibrio precario",
                "fare pause nelle avvitature in serie",
            ],
            [
                "togliere la batteria o la spina prima di cambiare l'inserto",
                "ricaricare le batterie lontano da materiali infiammabili",
                "riporre l'utensile pulito e segnalare i malfunzionamenti",
            ],
            ["guanti", "occhiali protettivi", "calzature di sicurezza", "casco"]),
    ),
    "Pistola sparachiodi": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Urti, colpi, impatti e compressioni: lancio del chiodo e colpo accidentale", 2, 4,
              "Utensile con dispositivo che impedisce lo sparo se la canna non è premuta sul pezzo "
              "(UNI EN 15895 per quelli a cartuccia, UNI EN ISO 11148-13 per quelli pneumatici); sparare "
              "sempre perpendicolarmente al supporto; non su materiali troppo duri, fragili o sottili, né "
              "vicino ai bordi; nessuno dietro la parete o il pannello; mai puntare verso persone; uso "
              "riservato a lavoratori formati e addestrati (art. 73).", DPI_BASE + ", occhiali protettivi"),
            _proiezione(3, 3, "Cuffia paraschegge montata; verificare che il supporto non sia "
                        "cavo o con inerti duri affioranti; tenere gli altri lavoratori a distanza."),
            _rumore(3, 2, "Sparo impulsivo con picco elevato: limitare il numero di fissaggi per "
                    "addetto e usare cariche minime sufficienti."),
            r("Incendio ed esplosione: cartucce e cartucce di gas", 1, 3,
              "Cartucce scelte per colore e potenza come indica il fabbricante, conservate nella "
              "custodia originale lontano da calore e fiamme; cartucce inesplose rimosse con l'utensile "
              "puntato contro il supporto e smaltite come rifiuto; per gli utensili a gas, cartucce "
              "conservate in luogo fresco e mai esposte al sole.", DPI_BASE),
            r("Movimentazione manuale dei carichi e posture incongrue", 2, 1,
              "Usare prolunghe per i fissaggi a soffitto; alternare i fissaggi a terra e in quota.",
              DPI_BASE),
        ],
        scheda_uso=scheda(
            "Utensile per fissare chiodi e perni su calcestruzzo, acciaio e legno, azionato da "
            "cartucce esplosive, da gas o da aria compressa.",
            [
                "verificare la presenza del libretto e la formazione dell'operatore",
                "controllare la sicura di contatto, la cuffia paraschegge e la pulizia della canna",
                "provare il supporto con un fissaggio di prova e scegliere chiodo e cartuccia idonei",
                "accertarsi che dietro la superficie non ci siano persone, impianti o vuoti",
            ],
            [
                "appoggiare la canna perpendicolare e premuta sul supporto prima di sparare",
                "non sparare vicino a bordi, fori o fissaggi precedenti",
                "non puntare mai l'utensile verso persone né portarlo con il dito sul grilletto",
                "in caso di mancato sparo attendere qualche secondo tenendo l'utensile in posizione",
                "non lasciare l'utensile carico incustodito",
            ],
            [
                "scaricare l'utensile (cartucce, caricatore o aria) prima di riporlo",
                "riporre utensile e cartucce nella custodia chiusa, al riparo da calore",
                "pulire la canna e il pistone come indica il fabbricante",
            ],
            ["occhiali protettivi", "otoprotettori", "casco", "guanti", "calzature di sicurezza"]),
    ),
    "Scanalatrice per murature": attrezzatura(
        ATTREZZO,
        rischi=[
            _silice(4, 3, "Scanalatrice con cuffia chiusa e attacco per aspiratore di classe M o "
                    "superiore, sempre collegato durante il taglio."),
            r("Punture, tagli e abrasioni: contatto con i dischi", 2, 3,
              "Cuffia di protezione dei dischi integra; dischi diamantati adatti al materiale e alla "
              "velocità dell'utensile, ben serrati; avviamento con i dischi staccati dal muro; attesa "
              "dell'arresto prima di appoggiare l'utensile (CEI EN 62841).", DPI_BASE + ", guanti antitaglio"),
            r("Urti, colpi, impatti e compressioni: contraccolpo", 2, 3,
              "Impugnatura con due mani; avanzamento regolare senza inclinare la macchina nella "
              "traccia; utensile con limitatore di coppia o frizione; non tagliare a soffitto senza "
              "posizione stabile.", DPI_BASE),
            r("Contatto con impianti nascosti (cavi elettrici, tubazioni)", 2, 4,
              "Tracciare le scanalature dopo aver verificato con rilevatore e schemi il percorso degli "
              "impianti esistenti; impianti sezionati nella zona di lavoro.", DPI_BASE),
            _rumore(3, 2, "Utensile a bassa emissione e lavoro in locali con porte chiuse verso le "
                    "zone dove operano altri."),
            _vibrazioni_mb(2, 2, "Dischi equilibrati e in buono stato."),
        ],
        scheda_uso=scheda(
            "Utensile elettrico portatile a doppio disco diamantato per aprire tracce nelle murature, "
            "destinate al passaggio di tubazioni e impianti.",
            _ELETTRICO_PRIMA + [
                "verificare dischi, cuffia e regolazione di larghezza e profondità della traccia",
                "collegare l'aspiratore con filtro adatto alle polveri silicee",
                "individuare e sezionare gli impianti presenti nella zona",
            ],
            [
                "avviare l'utensile prima di appoggiarlo al muro e procedere senza forzare",
                "tenere sempre l'utensile con due mani",
                "tenere fuori dal locale chi non lavora o non indossa i DPI",
                "attendere l'arresto dei dischi prima di posare l'utensile",
            ],
            _ELETTRICO_DOPO + ["svuotare l'aspiratore con sacco chiuso, senza sollevare polvere"],
            ["facciale filtrante FFP3", "occhiali a maschera", "otoprotettori", "guanti antitaglio",
             "calzature di sicurezza", "casco"]),
    ),
    "Sega a disco per murature e calcestruzzo": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Urti, colpi, impatti e compressioni: contraccolpo del disco", 2, 4,
              "Troncatrice conforme (UNI EN ISO 19432-1 se a motore, CEI EN 62841 se elettrica) con cuffia "
              "regolabile; tagliare con la parte inferiore del disco, mai con il settore superiore; "
              "pezzo fermo e sostenuto in modo che il taglio non si chiuda sul disco; due mani e "
              "corpo fuori dal piano del disco.", DPI_BASE),
            r("Punture, tagli e abrasioni: rottura del disco", 2, 4,
              "Dischi diamantati adatti al materiale e con velocità massima non inferiore a quella "
              "dell'albero; montaggio con flange e senso di rotazione corretti; dischi danneggiati "
              "scartati; non usare il disco per tagli laterali o curvi.", DPI_BASE + ", schermo facciale"),
            _silice(4, 3, "Taglio esclusivamente a umido con il kit acqua della macchina "
                    "regolato per tenere bagnato il disco."),
            _rumore(4, 3, "Macchina con marmitta efficiente."),
            _vibrazioni_mb(3, 2, "Impugnature antivibranti integre e disco ben centrato."),
            r("Inalazione di gas di scarico (motore a scoppio)", 2, 3,
              "Le troncatrici a motore non vanno usate in locali chiusi o in scavi senza ventilazione: "
              "in ambienti chiusi usare modelli elettrici; rifornimento a motore spento e freddo, "
              "lontano da fiamme (rischio incendio dei vapori di benzina).", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Troncatrice portatile a disco diamantato, con motore a scoppio o elettrico, per tagliare "
            "blocchi, murature, cordoli, tubi e lastre di calcestruzzo.",
            [
                "verificare disco, flange, cuffia e il collegamento dell'acqua",
                "controllare impugnature, comandi e arresto del motore",
                "posizionare e bloccare il pezzo in modo che il taglio resti aperto",
                "delimitare la zona di taglio e allontanare le persone",
                "per i modelli a scoppio, fare il rifornimento a motore spento, lontano dal taglio",
            ],
            [
                "avviare la macchina a terra, ben appoggiata, con il disco libero",
                "tenere la macchina con due mani e il corpo a lato del piano del disco",
                "usare la parte inferiore del disco e non forzare l'avanzamento",
                "tagliare sempre con l'acqua attiva",
                "non sollevare la macchina sopra le spalle",
            ],
            [
                "spegnere e attendere l'arresto del disco prima di posarla",
                "pulire la macchina e il filtro dell'aria e controllare il disco",
                "raccogliere i fanghi di taglio senza scaricarli in caditoie",
            ],
            ["facciale filtrante FFP3", "schermo facciale", "occhiali protettivi", "otoprotettori",
             "guanti antivibrazioni", "calzature di sicurezza", "indumenti impermeabili", "casco"]),
    ),
    "Tagliasfalto a disco": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Punture, tagli e abrasioni: contatto con il disco", 2, 4,
              "Macchina conforme a UNI EN 13862 con carter del disco sempre montato e chiuso; disco "
              "abbassato solo con la macchina in posizione di taglio; non sostare davanti o di lato "
              "al disco; arresto prima di ogni spostamento.", DPI_BASE),
            _silice(3, 3, "Taglio a umido con serbatoio o alimentazione d'acqua efficiente; per "
                    "sottofondi e pavimentazioni in calcestruzzo il rischio aumenta."),
            _rumore(4, 3, "Marmitta e cofani integri."),
            r("Vibrazioni al sistema mano-braccio", 2, 2,
              "Manubrio con supporti antivibranti; guida della macchina senza spinte eccessive; "
              "pause nelle lavorazioni lunghe (artt. 199-205 D.Lgs. 81/2008).",
              DPI_BASE + ", guanti antivibrazioni"),
            r("Inalazione di gas di scarico (motore a scoppio)", 2, 2,
              "Uso all'aperto o in ambienti ben ventilati; operatore sopravvento; motore spento nelle "
              "pause; rifornimento a motore freddo, lontano da fiamme.", DPI_BASE),
            r("Investimento da mezzi in manovra", 2, 4,
              "Area di taglio delimitata e segnalata secondo il D.M. 10 luglio 2002 quando si lavora su "
              "strade aperte al traffico; movieri; indumenti ad alta visibilità.", DPI_BASE),
            r("Contatto con sottoservizi", 1, 4,
              "Profondità di taglio regolata in base allo spessore della pavimentazione; verifica "
              "preventiva dei sottoservizi superficiali (cavi di illuminazione, semafori).", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Macchina a spinta con motore e disco diamantato, condotta da terra, per il taglio di "
            "pavimentazioni bituminose e in calcestruzzo prima di scavi e ripristini.",
            [
                "verificare carter del disco, comandi, freno e arresto d'emergenza",
                "riempire il serbatoio dell'acqua e controllare il getto sul disco",
                "tracciare la linea di taglio e verificare l'assenza di sottoservizi superficiali",
                "delimitare e segnalare l'area, anche verso il traffico",
            ],
            [
                "abbassare il disco gradualmente e avanzare a velocità costante",
                "non lasciare la macchina in moto senza sorveglianza",
                "tenere le persone lontane dal disco e dal getto di fanghi",
                "spegnere il motore nelle pause e durante il rifornimento",
            ],
            [
                "sollevare il disco e spegnere la macchina prima di spostarla",
                "pulire la macchina e raccogliere i fanghi di taglio",
                "controllare l'usura del disco e annotare le anomalie",
            ],
            ["otoprotettori", "facciale filtrante FFP3", "occhiali protettivi", "guanti antivibrazioni",
             "calzature di sicurezza", "indumenti ad alta visibilità"]),
    ),
    "Carotatrice": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Elettrocuzione: lavoro a umido con utensile elettrico", 2, 4,
              "Carotatrice conforme a CEI EN 62841-3-6 (o UNI EN 12348 se su supporto) alimentata tramite "
              "dispositivo differenziale portatile (PRCD) o trasformatore di isolamento come indica il "
              "fabbricante; anello di raccolta dell'acqua all'imbocco del foro; cavi e quadro lontani dall'acqua.",
              DPI_BASE),
            r("Urti, colpi, impatti e compressioni: rotazione della macchina al bloccaggio della corona", 2, 3,
              "Fori sopra i diametri indicati dal fabbricante sempre con la macchina fissata al "
              "supporto (tassello o ventosa) e la colonna ben ancorata; frizione di sicurezza "
              "efficiente; avanzamento graduale.", DPI_BASE),
            r("Caduta di materiale dall'alto o a livello: carota e frammenti", 2, 3,
              "Nei fori su solai e pareti, area sottostante o retrostante delimitata e presidiata; "
              "carota trattenuta o raccolta; verifica preventiva che il foro non intercetti armature "
              "principali o impianti.", DPI_BASE),
            _rumore(3, 2, "Lavoro a umido e corona in buono stato."),
            r("Movimentazione manuale dei carichi", 2, 2,
              "Trasporto di motore e colonna separatamente o con carrello; corone pesanti montate in "
              "due.", DPI_BASE),
            r("Scivolamenti e cadute a livello", 2, 2,
              "Raccogliere l'acqua con aspiratore per liquidi o anello di raccolta; non lasciare fanghi "
              "sui percorsi.", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Macchina elettrica con corona diamantata, a mano o su colonna, per praticare fori "
            "cilindrici e prelevare carote in calcestruzzo, murature e pietra, di norma a umido.",
            _ELETTRICO_PRIMA + [
                "verificare il PRCD o il trasformatore e la frizione di sicurezza",
                "fissare la colonna al supporto e verificarne la stabilità",
                "verificare cosa c'è dietro o sotto il foro e delimitare la zona",
                "collegare l'acqua e predisporre la raccolta",
            ],
            [
                "avviare l'acqua prima della rotazione e mantenerla per tutto il foro",
                "avanzare con gradualità senza forzare la corona",
                "tenere mani e indumenti lontani dalla corona in rotazione",
                "fermare la macchina se la corona si blocca, senza tentare di liberarla in moto",
            ],
            _ELETTRICO_DOPO + ["raccogliere acqua e fanghi e asciugare il pavimento"],
            ["occhiali protettivi", "otoprotettori", "guanti", "stivali di sicurezza", "casco",
             "indumenti impermeabili"]),
    ),
    "Sega a filo diamantato": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Urti, colpi, impatti e compressioni: rottura del filo e frustata", 2, 4,
              "Macchina conforme a UNI EN 15027 con protezioni sul percorso del filo e sulle pulegge; "
              "filo integro e giunti eseguiti con il morsetto prescritto; zona di pericolo nel piano "
              "del filo delimitata e interdetta durante il taglio; comando a distanza.", DPI_BASE),
            r("Crollo o ribaltamento di strutture: caduta del blocco tagliato", 2, 4,
              "Sequenza di taglio definita in un piano; blocchi imbracati o sostenuti prima "
              "dell'ultimo taglio; puntellature della struttura residua; mezzi di sollevamento "
              "idonei al peso dei blocchi.", DPI_BASE),
            r("Cesoiamenti e stritolamenti: pulegge e volano", 2, 3,
              "Carter sulle pulegge di rinvio e sul volano; nessun intervento con la macchina in moto; "
              "regolazioni a macchina ferma e sezionata.", DPI_BASE),
            _silice(2, 3, "Taglio sempre raffreddato ad acqua."),
            _rumore(3, 2, "Centralina idraulica o motore posti lontano dagli addetti."),
            r("Elettrocuzione", 1, 4,
              "Centralina e quadri di alimentazione protetti contro getti d'acqua; differenziale; "
              "cavi lontani dal circuito dell'acqua di raffreddamento.", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Impianto con motore (elettrico o idraulico), volano e pulegge che fa scorrere un filo "
            "diamantato chiuso ad anello attorno all'elemento, per tagliare calcestruzzo armato e "
            "pietra di grande spessore.",
            [
                "pianificare la sequenza di taglio e il sostegno dei blocchi",
                "verificare filo, giunti, pulegge, carter e fissaggio della macchina",
                "delimitare la zona di pericolo nel piano del filo",
                "collegare e verificare l'acqua di raffreddamento",
                "accertarsi che l'operatore sia formato sull'uso della macchina",
            ],
            [
                "comandare la macchina dalla postazione protetta o a distanza",
                "non attraversare la zona del filo durante il taglio",
                "controllare tensione e velocità del filo",
                "fermare il taglio se il filo vibra o slitta in modo anomalo",
            ],
            [
                "sezionare la macchina prima di smontare il filo",
                "controllare l'usura del filo e dei giunti",
                "raccogliere acqua e fanghi di taglio",
            ],
            ["casco", "occhiali protettivi", "otoprotettori", "guanti", "stivali di sicurezza",
             "indumenti impermeabili"]),
    ),
    "Piastra vibrante": attrezzatura(
        ATTREZZO,
        rischi=[
            _vibrazioni_mb(3, 2, "Piastra con timone su supporti antivibranti (UNI EN 500-4); guida "
                           "senza premere sul timone."),
            _rumore(3, 2, "Motore con marmitta e cofani integri."),
            r("Inalazione di gas di scarico (motore a scoppio)", 2, 3,
              "Mai usarla a motore acceso in scavi stretti, trincee o locali chiusi senza ventilazione "
              "forzata; in tali casi preferire modelli elettrici; operatore sopravvento.", DPI_BASE),
            r("Urti, colpi, impatti e compressioni: schiacciamento dei piedi", 2, 3,
              "Guidare la piastra camminando di lato o dietro il timone, mai davanti nella "
              "retromarcia (piastre reversibili); comando di arresto a uomo presente efficiente.",
              DPI_BASE),
            r("Polveri e fibre", 2, 2,
              "Inumidire il materiale da compattare quando è asciutto e polveroso.",
              DPI_BASE + ", maschera antipolvere"),
            r("Movimentazione manuale dei carichi", 2, 2,
              "Sollevare la piastra solo dal punto di aggancio con un mezzo di sollevamento o in due; "
              "carico e scarico con rampe o sponda idraulica.", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Macchina a spinta con piastra vibrante azionata da motore, per la compattazione di "
            "rinterri, sottofondi e pavimentazioni in masselli.",
            [
                "verificare comandi, timone antivibrante e arresto del motore",
                "controllare protezioni della cinghia e livelli",
                "verificare la ventilazione se si lavora in scavo",
                "delimitare l'area e accertarsi che il fondo sia stabile",
            ],
            [
                "guidare la piastra dal timone senza mettersi davanti",
                "tenersi lontani dai bordi degli scavi non armati",
                "spegnere il motore nelle pause e durante il rifornimento",
                "fare pause per limitare rumore e vibrazioni",
            ],
            [
                "spegnere il motore e chiudere il rubinetto del carburante",
                "pulire la piastra e controllare viti e supporti",
            ],
            ["otoprotettori", "guanti antivibrazioni", "calzature di sicurezza", "maschera antipolvere",
             "indumenti ad alta visibilità", "casco"]),
    ),
    "Costipatore a percussione": attrezzatura(
        ATTREZZO,
        rischi=[
            _vibrazioni_mb(4, 2, "Costipatore con impugnatura antivibrante (UNI EN 500-4); usare la "
                           "macchina il tempo strettamente necessario con pause frequenti."),
            r("Vibrazioni al corpo intero", 2, 2,
              "Non appoggiarsi con il corpo sulla macchina; turnazione degli addetti (artt. 199-205 "
              "D.Lgs. 81/2008).", DPI_BASE),
            _rumore(4, 2, "Motore con marmitta efficiente."),
            r("Inalazione di gas di scarico (motore a scoppio)", 3, 3,
              "Il costipatore lavora spesso in trincea: controllare la ventilazione, usare un "
              "aspiratore o modelli elettrici o a batteria; nessun addetto fermo nello scavo con il "
              "motore acceso.", DPI_BASE),
            r("Urti, colpi, impatti e compressioni: ribaltamento e schiacciamento dei piedi", 2, 3,
              "Guidare dalla maniglia mantenendo i piedi lontani dal piede battente; non lasciare la "
              "macchina accesa in piedi da sola; carico e scarico con mezzi idonei.", DPI_BASE),
            r("Posture incongrue", 2, 2,
              "Avanzare camminando dietro la macchina; non piegarsi sul manico.", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Macchina a motore con piede battente (detta anche «rana» o «pestello»), per compattare "
            "terreni in spazi ristretti, attorno a tubazioni e nei rinterri di trincea.",
            [
                "verificare impugnatura, comandi, soffietto e livello dell'olio",
                "controllare che lo scavo sia armato e ventilato se si lavora in trincea",
                "verificare l'assenza di persone nella zona di lavoro",
            ],
            [
                "tenere la maniglia con due mani e i piedi lontani dal piede battente",
                "procedere dietro la macchina senza spingerla",
                "fare pause frequenti e alternare gli addetti",
                "spegnere il motore nelle soste",
            ],
            [
                "spegnere il motore e trasportare la macchina in posizione verticale come da libretto",
                "pulire il piede e controllare viti e soffietto",
            ],
            ["otoprotettori", "guanti antivibrazioni", "calzature di sicurezza", "casco",
             "indumenti ad alta visibilità"]),
    ),
    "Vibratore per calcestruzzo": attrezzatura(
        ATTREZZO,
        rischi=[
            _ELETTROCUZIONE,
            r("Vibrazioni al sistema mano-braccio", 2, 2,
              "Tenere il tubo flessibile e non l'ago; non trattenere l'ago con le mani; motore o "
              "convertitore appoggiato e non tenuto in mano; alternare gli addetti (UNI EN 12649, artt. "
              "199-205 D.Lgs. 81/2008).", DPI_BASE + ", guanti antivibrazioni"),
            r("Getti e schizzi di calcestruzzo", 3, 2,
              "Immergere e sfilare l'ago lentamente, senza farlo vibrare in aria; occhiali durante il "
              "getto; lavare subito la pelle (il cemento fresco è alcalino e irritante).",
              DPI_BASE + ", occhiali protettivi, guanti in lattice o nitrile"),
            r("Rischio chimico: dermatite da cemento", 2, 2,
              "Guanti impermeabili con polsino, abiti puliti e stivali; non far entrare impasto negli "
              "stivali; cemento a basso contenuto di cromo VI (Regolamento REACH).",
              DPI_BASE + ", guanti in lattice o nitrile"),
            r("Caduta dall'alto", 2, 4,
              "Vibrazione eseguita da impalcati o passerelle con parapetto lungo casseri di pilastri "
              "e pareti; nessun lavoro in equilibrio sui casseri.", DPI_BASE),
            _rumore(2, 2, "Convertitore lontano dall'operatore."),
        ],
        scheda_uso=scheda(
            "Vibratore a immersione (ago vibrante con tubo flessibile e motore o convertitore "
            "elettrico) per compattare il calcestruzzo fresco nei getti.",
            _ELETTRICO_PRIMA + [
                "verificare l'integrità del tubo flessibile e del collegamento all'ago",
                "predisporre passerelle o impalcati per raggiungere il getto",
            ],
            [
                "immergere l'ago verticalmente e sfilarlo lentamente",
                "non far funzionare l'ago fuori dal getto",
                "impugnare il tubo e non l'ago, con il convertitore appoggiato",
                "non trascinare il vibratore tirando il cavo o il tubo",
            ],
            ["lavare l'ago e il tubo a vibratore spento e scollegato"] + _ELETTRICO_DOPO,
            ["guanti in lattice o nitrile", "stivali di sicurezza", "occhiali protettivi", "casco",
             "guanti antivibrazioni"]),
    ),
    "Frattazzatrice meccanica": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Cesoiamenti e stritolamenti: contatto con le pale rotanti", 2, 3,
              "Macchina conforme a UNI EN 12649 con anello di protezione attorno alle pale e comando a "
              "uomo presente che arresta il motore al rilascio del manubrio; nessuno vicino durante la "
              "lisciatura; cambio delle pale a motore spento.", DPI_BASE),
            r("Urti, colpi, impatti e compressioni: rotazione del manubrio", 2, 3,
              "Impugnare il manubrio con entrambe le mani; avviare a bassa velocità con le pale piane; "
              "arresto automatico efficiente se l'operatore perde la presa.", DPI_BASE),
            _vibrazioni_mb(2, 2, "Manubrio con supporti antivibranti."),
            _rumore(3, 2, "Motore con marmitta efficiente."),
            r("Inalazione di gas di scarico (motore a scoppio)", 3, 3,
              "La lisciatura avviene spesso in locali al chiuso: ventilazione forzata o modelli "
              "elettrici; operatore sopravvento; rifornimento all'esterno a motore freddo.", DPI_BASE),
            r("Scivolamenti e cadute a livello", 2, 2,
              "Camminare sul getto con calzature adatte; ostacoli e ferri d'attesa protetti o rimossi.",
              DPI_BASE),
        ],
        scheda_uso=scheda(
            "Macchina a pale rotanti (detta anche «elicottero») con motore e manubrio di guida, per "
            "la frattazzatura e la lisciatura delle pavimentazioni in calcestruzzo.",
            [
                "verificare anello di protezione, pale e arresto a uomo presente",
                "assicurare la ventilazione se si lavora al chiuso",
                "allontanare dal getto le persone non addette",
            ],
            [
                "avviare a bassa velocità e tenere il manubrio con due mani",
                "non avvicinare piedi e mani all'anello di protezione",
                "spegnere il motore prima di regolare o sostituire le pale",
                "fare pause per limitare vibrazioni e rumore",
            ],
            [
                "spegnere e pulire la macchina dai residui di calcestruzzo",
                "sollevarla con mezzi idonei o in due, dai punti indicati",
            ],
            ["stivali di sicurezza", "otoprotettori", "guanti antivibrazioni", "occhiali protettivi"]),
    ),
    "Piegaferri": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Cesoiamenti e stritolamenti: mani tra perni e barra", 2, 4,
              "Macchina marcata CE (o adeguata all'Allegato V D.Lgs. 81/2008 se antecedente) con "
              "pedale protetto contro l'azionamento accidentale e pulsante di arresto d'emergenza; "
              "mani lontane dal piatto in rotazione; riposizionare la barra solo a piatto fermo.",
              DPI_BASE),
            r("Urti, colpi, impatti e compressioni: movimento della barra", 3, 2,
              "Area di rotazione della barra libera e delimitata; barre lunghe sostenute da cavalletti "
              "o rulliere; un solo operatore ai comandi.", DPI_BASE),
            _ELETTROCUZIONE,
            r("Movimentazione manuale dei carichi", 3, 2,
              "Fasci di barre movimentati con la gru e accessori idonei; barre lunghe portate in due; "
              "banco della macchina all'altezza corretta.", DPI_BASE),
            r("Punture, tagli e abrasioni", 3, 1,
              "Guanti in tutte le manipolazioni; estremità delle barre accatastate con il lato tagliato "
              "verso l'esterno protette o segnalate.", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Macchina elettrica con piatto rotante e perni per piegare barre e staffe d'armatura del "
            "calcestruzzo.",
            _ELETTRICO_PRIMA + [
                "verificare il pedale protetto, l'arresto d'emergenza e i perni",
                "posizionare la macchina in piano, sotto tettoia di protezione se nel raggio della gru",
                "predisporre cavalletti o rulliere per le barre lunghe",
            ],
            [
                "non superare il diametro massimo di barra indicato dal fabbricante",
                "tenere le mani lontane dal piatto e dai perni durante la piegatura",
                "non lasciare il pedale in posizione di comando quando si posiziona la barra",
                "tenere libera l'area di rotazione della barra",
            ],
            ["pulire il piatto da residui e ruggine"] + _ELETTRICO_DOPO,
            ["guanti", "calzature di sicurezza", "casco", "occhiali protettivi"]),
    ),
    "Tagliaferri": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Cesoiamenti e stritolamenti: zona delle lame", 2, 4,
              "Macchina marcata CE (o adeguata all'Allegato V D.Lgs. 81/2008) con protezione sulla "
              "zona di taglio che lascia passare solo la barra, pedale protetto e arresto d'emergenza; "
              "mani ad almeno 20 cm dalle lame; più barre tagliate insieme solo se ammesso dal "
              "fabbricante.", DPI_BASE),
            _proiezione(3, 2, "Spezzoni corti trattenuti o raccolti da un contenitore; nessuno "
                        "davanti all'uscita del pezzo tagliato."),
            _ELETTROCUZIONE,
            r("Movimentazione manuale dei carichi", 3, 2,
              "Fasci di barre movimentati con mezzi meccanici; barre lunghe sostenute da rulliere.",
              DPI_BASE),
            _rumore(2, 2, "Lame affilate e macchina manutenuta."),
        ],
        scheda_uso=scheda(
            "Cesoia elettrica da banco con lame azionate da motore per il taglio a misura delle barre "
            "d'armatura; esistono anche cesoie portatili idrauliche o elettriche per tagli in opera.",
            _ELETTRICO_PRIMA + [
                "verificare lame, protezione della zona di taglio, pedale e arresto d'emergenza",
                "posizionare la macchina in piano e protetta dalla caduta di materiali",
            ],
            [
                "inserire la barra a fondo tra le lame e tenere le mani lontane",
                "non tagliare barre di diametro superiore a quello indicato",
                "non tagliare spezzoni troppo corti senza un sistema di trattenuta",
                "tenere le persone lontane dall'uscita dei pezzi",
            ],
            ["rimuovere gli spezzoni e pulire la zona di taglio"] + _ELETTRICO_DOPO,
            ["guanti", "occhiali protettivi", "calzature di sicurezza", "casco"]),
    ),
    "Saldatrice per polietilene": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Ustioni: contatto con il termoelemento", 3, 2,
              "Termoelemento (oltre 200 °C nella saldatura testa a testa) riposto sempre nel suo "
              "supporto; non toccarlo né appoggiarlo a terra; guanti adatti al calore; tubo saldato "
              "lasciato raffreddare sotto pressione nei tempi previsti dalla UNI 10520.",
              DPI_BASE + ", guanti per saldatura"),
            r("Cesoiamenti e stritolamenti: chiusura delle ganasce", 2, 3,
              "Mani fuori dalle ganasce e dalla zona di accostamento durante i movimenti del carrello "
              "idraulico; un solo operatore ai comandi; fresatrice (pialla) azionata solo inserita "
              "tra i tubi, con la protezione e il microinterruttore efficienti.", DPI_BASE),
            r("Elettrocuzione", 2, 4,
              "Macchina alimentata da quadro o gruppo elettrogeno con differenziale e messa a terra "
              "secondo il fabbricante; cavi integri lontani dall'acqua dello scavo; saldatrici per "
              "elettrofusione (UNI 10521) con cavi dei raccordi integri.", DPI_BASE),
            r("Rischio chimico: fumi di polietilene surriscaldato", 1, 2,
              "Non superare la temperatura prescritta; lavorare in zona aerata o sopravvento, in "
              "particolare in pozzetti e scavi profondi (Titolo IX D.Lgs. 81/2008).", DPI_BASE),
            r("Posture incongrue e lavoro in scavo", 2, 3,
              "Saldatura preferibilmente fuori dallo scavo; se in trincea, scavo armato o con pareti a "
              "scarpa e spazio sufficiente attorno alla macchina; saldatore qualificato (UNI 9737).",
              DPI_BASE),
        ],
        scheda_uso=scheda(
            "Attrezzatura per la giunzione di tubi in polietilene di reti gas e acqua, per fusione "
            "testa a testa con termoelemento e carrello idraulico o per elettrofusione dei raccordi.",
            [
                "verificare che il saldatore sia qualificato e conosca la procedura di saldatura",
                "controllare cavi, termoelemento, fresatrice, centralina e messa a terra",
                "posizionare la macchina su base stabile e asciutta, al riparo da pioggia e vento",
                "verificare che la temperatura del termoelemento sia quella prescritta",
            ],
            [
                "riporre il termoelemento nel suo supporto dopo ogni uso",
                "tenere le mani fuori dalle ganasce durante l'accostamento",
                "azionare la fresatrice solo inserita tra i tubi",
                "rispettare i tempi di raffreddamento senza muovere il giunto",
            ],
            [
                "scollegare l'alimentazione e lasciare raffreddare il termoelemento nel supporto",
                "pulire le piastre e riporre la macchina nella cassa",
                "registrare i parametri della saldatura e segnalare le anomalie",
            ],
            ["guanti per saldatura", "occhiali protettivi", "calzature di sicurezza", "casco"]),
    ),
    "Cannello ossiacetilenico": attrezzatura(
        ATTREZZO,
        rischi=[
            r("Incendio ed esplosione: bombole, tubi e ritorno di fiamma", 2, 4,
              "Riduttori di pressione con manometri e dispositivi contro il ritorno di fiamma su "
              "entrambi i gas, all'uscita dei riduttori e al cannello (UNI EN ISO 5175); cannello conforme "
              "a UNI EN ISO 5172; tubi colorati e integri (rosso acetilene, blu ossigeno) con fascette; "
              "pressione dell'acetilene non oltre 1,5 bar; mai olio o grasso sui raccordi "
              "dell'ossigeno; ricerca delle perdite con acqua saponata.", DPI_BASE),
            r("Incendio dei materiali vicini", 3, 3,
              "Lavoro a caldo autorizzato dal preposto; allontanare o coprire con teli ignifughi i "
              "materiali combustibili; estintore a portata di mano; sorveglianza della zona per "
              "almeno 30 minuti dopo la fine (Allegato IV punto 4, D.Lgs. 81/2008).", DPI_BASE),
            r("Ustioni", 3, 2,
              "Indumenti in cotone o ignifughi senza tasche aperte, ghette e guanti per saldatura; "
              "pezzi caldi segnalati; non appoggiare il cannello acceso.",
              DPI_BASE + ", guanti per saldatura, ghette per saldatura"),
            r("Radiazioni ottiche", 3, 2,
              "Occhiali o schermo con filtri di grado adatto alla fiamma e al lavoro (UNI EN 169); "
              "schermi per proteggere chi lavora vicino (Titolo VIII, Capo V, D.Lgs. 81/2008).",
              DPI_BASE + ", schermo per saldatura"),
            r("Rischio chimico: fumi di taglio e saldatura", 3, 3,
              "Aspirazione localizzata o lavoro all'aperto sopravvento; attenzione a vernici, zincature "
              "e piombo sui pezzi; in locali ristretti ventilazione forzata e mai ossigeno per "
              "«rinfrescare» l'aria (Titolo IX D.Lgs. 81/2008).",
              DPI_BASE + ", maschera con filtro specifico"),
            r("Urti, colpi, impatti e compressioni: caduta delle bombole", 2, 3,
              "Bombole in posizione verticale sul carrello e fissate con catena; cappellotto montato "
              "durante il trasporto; movimentazione con carrello, mai rotolandole o sollevandole "
              "dalla valvola.", DPI_BASE),
        ],
        scheda_uso=scheda(
            "Attrezzatura per saldatura, brasatura e taglio a fiamma dei metalli, con bombole di "
            "ossigeno e acetilene, riduttori, tubi e cannello.",
            [
                "verificare bombole, riduttori, valvole antiritorno, tubi e fascette",
                "fissare le bombole sul carrello, lontane da fonti di calore e dalla zona dei lavori",
                "allontanare i materiali combustibili e predisporre l'estintore",
                "cercare le perdite con acqua saponata, mai con la fiamma",
            ],
            [
                "aprire lentamente le valvole delle bombole e regolare le pressioni di lavoro",
                "accendere con l'accenditore apposito, aprendo prima l'acetilene",
                "non avvolgere i tubi attorno al corpo né farli passare su spigoli o pezzi caldi",
                "in caso di ritorno di fiamma chiudere subito il cannello e le valvole delle bombole",
                "non lavorare su recipienti che abbiano contenuto sostanze infiammabili senza bonifica",
            ],
            [
                "spegnere chiudendo prima l'acetilene, poi chiudere le bombole e scaricare i tubi",
                "riporre le bombole in luogo aerato, con cappellotto, separando piene e vuote",
                "controllare la zona dopo la fine dei lavori per individuare focolai",
            ],
            ["schermo per saldatura", "guanti per saldatura", "grembiule per saldatura", "ghette per saldatura",
             "calzature di sicurezza", "maschera con filtro specifico"]),
    ),
}
