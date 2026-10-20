"""Fasi di lavoro delle categorie «Opere edili interne» (OI) e «Ripristini e restauri» (RR).

Le fasi sostituiscono, con maggiore dettaglio, le voci generiche NC.09, NC.10, NC.11, NC.12
(opere interne) e RI.03, RS.01, RS.02, RS.03 (consolidamenti e restauri) di archivio.py.

Testi redatti da zero per questo progetto. Fonti consultate come riferimento (non copiate):
- D.Lgs. 81/2008: Titolo IV (artt. 113 scale, 122 ponteggi e opere provvisionali, 140 ponti su
  cavalletti, 146 difesa delle aperture, 150-151 demolizioni e rafforzamenti), Titolo VI e
  Allegato XXXIII (movimentazione manuale dei carichi, norme ISO 11228), Titolo VIII (rumore,
  vibrazioni, radiazioni ottiche), Titolo IX Capo I (agenti chimici, artt. 221-232) e Capo II
  (cancerogeni: Allegato XLII voci «polveri di legno duro» e «silice cristallina respirabile»
  introdotta dal D.Lgs. 44/2020, valori limite dell'Allegato XLIII).
- Regolamento REACH (CE) 1907/2006, Allegato XVII: voce 47 (cromo VI nei cementi) e voce 74
  (diisocianati, Reg. UE 2020/1149: formazione obbligatoria dal 24/08/2023).
- D.Lgs. 161/2006 (limiti dei COV in pitture e vernici); D.M. 02/09/2021 e 03/09/2021 (gestione
  delle emergenze e prevenzione incendi nei luoghi di lavoro).
- INAIL-Formedil, monografia sull'esposizione a silice cristallina respirabile nei cantieri (2024).
- Norme tecniche: UNI EN 13813 (materiali per massetti), UNI EN 998-1 (malte per intonaci, tipo R
  da risanamento), UNI 11424 (sistemi in cartongesso), UNI 11493-1 (piastrellature ceramiche),
  UNI 11673-1 (posa dei serramenti), UNI EN 1504 (protezione e riparazione del calcestruzzo,
  parti 3 e 7), UNI EN 1004-1 (trabattelli), UNI EN 131 (scale), UNI 11182 (materiali lapidei,
  forme di alterazione), UNI 11161 e UNI 11138 (manufatti lignei).
- D.M. 17/01/2018 (NTC, cap. 8 costruzioni esistenti) e Circolare n. 7/2019; CNR-DT 200 R1/2013
  (FRP); CNR-DT 215/2018 (FRCM); Direttiva P.C.M. 09/02/2011 (Linee guida per la valutazione e
  riduzione del rischio sismico del patrimonio culturale); D.Lgs. 42/2004 (art. 29, restauro).
- Documentazione tecnica pubblica di produttori di sistemi di rinforzo e di ripristino (schede
  tecniche di malte R4, passivanti, sistemi FRP/FRCM) per le sequenze operative.

Contenuti da verificare e adattare dal coordinatore al cantiere specifico.
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import DPI_BASE, EDILIZIA, fase, r

# Attrezzature necessarie non ancora presenti nel CATALOGO di base.py: nome -> (tipo, motivo).
MANCANTI: dict[str, tuple[str, str]] = {
    "Pompa pneumatica per massetti": (
        "Attrezzo", "Miscelatrice-trasportatrice ad aria compressa per sabbia e cemento, usata per i massetti "
        "tradizionali pompati ai piani; ha rischi propri (tubazioni in pressione, colpo di frusta, rumore)."),
    "Sollevatore per lastre (alzapannelli)": (
        "Attrezzo", "Sollevatore manuale a manovella per posizionare a soffitto le lastre di cartongesso: "
        "riduce la movimentazione manuale sopra la testa nei controsoffitti."),
    "Sollevatore a ventose per lastre e vetri": (
        "Attrezzo", "Telaio o carrello con ventose a vuoto per movimentare vetrate, serramenti di grandi "
        "dimensioni e lastre ceramiche di grande formato; rischio proprio di distacco del carico."),
    "Levigatrice per pareti con aspirazione (giraffa)": (
        "Attrezzo", "Levigatrice a disco con asta telescopica collegata ad aspiratore, per carteggiare rasature "
        "e stuccature su pareti e soffitti riducendo le polveri."),
    "Idrodemolitrice (robot ad acqua ad alta pressione)": (
        "Macchina", "Robot radiocomandato che asporta il calcestruzzo degradato con getto d'acqua ad altissima "
        "pressione; ha rischi propri (getto, rumore elevato, tubazioni) da trattare nella sua scheda."),
    "Macchina insufflatrice per isolanti sfusi": (
        "Macchina", "Macchina che sfibra e insuffla nelle intercapedini fiocchi di cellulosa, lana minerale "
        "o granuli isolanti; serve per gli isolamenti interni ad insufflaggio."),
}

C_OI = "Opere edili interne"
C_RR = "Ripristini e restauri"

ED = EDILIZIA
RIS_RES = ("Ristrutturazioni", "Restauri")
NC_RIS = ("Nuove costruzioni", "Ristrutturazioni")
RIS_INF = ("Ristrutturazioni", "Opere infrastrutturali")
RIS_INF_RES = ("Ristrutturazioni", "Opere infrastrutturali", "Restauri")

# DPI ricorrenti (nomi di anagrafiche.CATALOGO_DPI).
DPI_INT = "Calzature di sicurezza, guanti, indumenti protettivi"
DPI_CASCO = "Casco, calzature di sicurezza, guanti, indumenti protettivi"

# ---------------------------------------------------------------------------------------------
# Rischi riusati
# ---------------------------------------------------------------------------------------------

_CADUTA_INTERNI = r(
    "Caduta dall'alto", 2, 3,
    "Lavori in quota su trabattelli conformi a UNI EN 1004-1, con ruote bloccate, piano completo e parapetti, "
    "o su ponti su cavalletti alti non più di 2 m, con tavole accostate e fissate e senza aggiunte "
    "sovrapposte (art. 140); scale doppie conformi a UNI EN 131 solo per lavori brevi (art. 113); vani "
    "scala, cavedi e aperture nei solai chiusi o protetti con parapetto (art. 146).",
    DPI_CASCO)
_CADUTA_PONTEGGIO = r(
    "Caduta dall'alto", 2, 4,
    "Lavori oltre 2 m solo da ponteggio, trabattello o piattaforma (art. 122) con parapetti e tavole "
    "fermapiede; aperture e bordi protetti; dove le protezioni collettive sono rimosse per esigenze "
    "operative, imbracatura agganciata a punto di ancoraggio idoneo.",
    DPI_BASE + ", imbracatura, cordino con assorbitore")
_MMC_SACCHI = r(
    "Movimentazione manuale dei carichi", 3, 2,
    "Sacchi di premiscelato da 25 kg al massimo, sollevati dal piano con montacarichi o carrello e depositati "
    "su bancali vicino al punto d'impiego; carichi oltre i limiti dell'Allegato XXXIII (ISO 11228-1) "
    "movimentati in due o con ausili; formazione sulle corrette posture (art. 169).",
    DPI_INT)
_MMC_ELEMENTI = r(
    "Movimentazione manuale dei carichi", 3, 3,
    "Elementi pesanti o ingombranti trasportati in due o con carrelli e sollevatori; percorsi interni sgombri; "
    "pesi indicati sugli imballi; valutazione secondo l'Allegato XXXIII e ISO 11228-1 per le operazioni "
    "ripetute; formazione dei lavoratori (art. 169).",
    DPI_INT)
_CEMENTO = r(
    "Rischio chimico: contatto con malte e boiacche cementizie", 3, 2,
    "Prodotti con cromo VI ridotto (REACH, Allegato XVII voce 47) e schede di sicurezza in cantiere "
    "(art. 223); evitare il contatto con la pelle e lavare subito gli schizzi; guanti in nitrile resistenti "
    "agli alcali sostituiti se bagnati all'interno; acqua pulita per il lavaggio degli occhi.",
    DPI_INT + ", guanti in lattice o nitrile, occhiali protettivi, crema protettiva")
_SCHIZZI_MALTA = r(
    "Getti e schizzi", 3, 2,
    "Proteggere gli occhi nei lavori sopra la testa e durante lo spruzzo; non dirigere la lancia verso le "
    "persone; zona di lavoro sgombra da non addetti; lavaggio oculare disponibile.",
    DPI_INT + ", occhiali a maschera")
_SILICE_TAGLIO = r(
    "Polveri e fibre: silice cristallina respirabile", 3, 3,
    "Valutare l'esposizione come agente cancerogeno (Allegato XLII; valore limite 0,1 mg/m3 dell'Allegato "
    "XLIII); tagli e levigature ad umido o con utensili ad aspirazione collegati ad aspiratore di classe H; "
    "pulizia dei locali con aspiratore o a umido, mai con scopa o aria compressa; registro degli esposti "
    "dove previsto.",
    DPI_INT + ", facciale filtrante FFP3, occhiali protettivi")
_POSTURE_GINOCCHIO = r(
    "Posture incongrue", 4, 2,
    "Lavoro prolungato in ginocchio o chinati: alternare i compiti e fare pause; attrezzi con manici lunghi "
    "dove possibile; materiali posizionati all'altezza della vita e non a terra.",
    DPI_INT + ", ginocchiere")
_POSTURE_SOFFITTO = r(
    "Posture incongrue", 3, 2,
    "Lavoro con braccia sopra le spalle: piano del trabattello regolato in modo da lavorare all'altezza "
    "del petto; prolunghe per gli attrezzi; rotazione dei compiti e pause frequenti.",
    DPI_INT)
_SCIVOLAMENTI = r(
    "Scivolamenti e cadute a livello", 3, 2,
    "Pavimenti sgombri da sfridi, sacchi e cavi; materiali stoccati fuori dai percorsi; illuminazione "
    "artificiale adeguata nei locali bui; superfici bagnate o fresche segnalate e interdette.",
    DPI_INT)
_URTI_INTERNI = r(
    "Urti, colpi, impatti e compressioni", 2, 2,
    "Spazi di lavoro sufficienti e ordinati; elementi lunghi trasportati in due tenendoli bassi; attenzione "
    "a spigoli di profili e tubi sporgenti; illuminazione adeguata.",
    DPI_INT)
_TAGLI_PROFILI = r(
    "Punture, tagli e abrasioni", 3, 2,
    "Bordi di profili metallici, lamiere e lastre tagliate maneggiati con guanti antitaglio; sfridi raccolti "
    "subito in contenitori; lame dei cutter a scomparsa e sostituite quando consumate.",
    DPI_INT + ", guanti antitaglio")
_ELETTRO_ESISTENTI = r(
    "Elettrocuzione", 2, 4,
    "Prima di forare, tagliare o rimuovere elementi in edifici esistenti individuare le linee sotto traccia "
    "con rilevatore e schemi d'impianto; sezionare e bloccare i circuiti interessati; utensili e prolunghe "
    "alimentati da quadro di cantiere con differenziale.",
    DPI_INT)
_MICROCLIMA_INTERNI = r(
    "Microclima", 2, 2,
    "Locali chiusi e poco ventilati: aerazione naturale o forzata, pause in ambiente fresco nei mesi caldi, "
    "acqua potabile disponibile; d'inverno locali riscaldati o pause in baracca.",
    DPI_INT)
_INCENDIO_SOLVENTI = r(
    "Incendio ed esplosione", 2, 4,
    "Vapori di solventi e prodotti infiammabili: nessuna fiamma libera, lavorazione a caldo o fumo nei "
    "locali; solo le quantità necessarie alla giornata, in recipienti chiusi ed etichettati; estintore a "
    "portata di mano; stracci e carte imbevuti raccolti in contenitori metallici chiusi.",
    DPI_INT)
_RESINE_EPOSSIDICHE = r(
    "Rischio chimico: resine epossidiche e indurenti", 3, 3,
    "Prodotti sensibilizzanti per la pelle (H317): consultare le schede di sicurezza e valutare il rischio "
    "(art. 223); mescolare e applicare evitando ogni contatto cutaneo; guanti in nitrile cambiati spesso e "
    "maniche chiuse; locali ventilati; sorveglianza sanitaria se il rischio non è irrilevante (art. 229); "
    "allontanare dalla lavorazione chi ha già manifestato dermatiti.",
    DPI_INT + ", guanti in lattice o nitrile, occhiali a maschera, tuta monouso")
_CROLLO_ESISTENTI = r(
    "Crollo o ribaltamento di strutture", 2, 4,
    "Verifica preliminare dello stato della struttura da parte del progettista o del direttore dei lavori; "
    "puntellamenti e rafforzamenti prima di intervenire su elementi deteriorati (art. 150); procedere per "
    "tratti limitati secondo la sequenza del progetto; non accumulare materiali sui solai da consolidare; "
    "interrompere e avvisare in caso di lesioni o cedimenti nuovi.",
    DPI_CASCO)
_CADUTA_MATERIALE = r(
    "Caduta di materiale dall'alto o a livello", 2, 3,
    "Zona sottostante delimitata e interdetta; materiale demolito raccolto sul piano di lavoro o convogliato "
    "a terra con canali (art. 153); tavole fermapiede sui piani di lavoro; attrezzi non lasciati sui bordi.",
    DPI_BASE)
_POLVERI_DEMOLIZIONE = r(
    "Polveri e fibre", 3, 3,
    "Bagnare le superfici prima e durante la rimozione; utensili con aspirazione alla fonte; zona di lavoro "
    "confinata con teli verso i locali in uso; verificare che i materiali non contengano amianto prima di "
    "intervenire; per la silice cristallina, valutazione come agente cancerogeno (Allegato XLII).",
    DPI_BASE + ", facciale filtrante FFP3, occhiali protettivi")
_PROIEZIONE = r(
    "Proiezione di schegge e frammenti", 3, 2,
    "Occhiali o visiera durante scalpellature e demolizioni manuali; scalpelli con testa non sbavata; "
    "schermi o teli verso le zone di passaggio; non addetti fuori dal raggio di proiezione.",
    DPI_BASE + ", occhiali protettivi, visiera protettiva")


# ---------------------------------------------------------------------------------------------
# Opere edili interne
# ---------------------------------------------------------------------------------------------

_MASSETTI = "Massetti e sottofondi"
_INTONACI = "Intonaci, rasature e controsoffitti"
_PAVIMENTI = "Pavimenti e rivestimenti"
_SERRAMENTI = "Serramenti e opere in ferro"
_FINITURE = "Pitturazioni e isolamenti interni"

_OPERE_INTERNE = [
    # --- Massetti e sottofondi ---
    fase("OI.01", C_OI, _MASSETTI, "Realizzazione di sottofondi alleggeriti",
         "Getto di sottofondi a bassa densità per coprire gli impianti a pavimento e ridurre i carichi sul solaio, "
         "con calcestruzzo cellulare, impasti di cemento e perle di polistirene o argilla espansa. L'impasto è "
         "preparato in betoniera o in impastatrice al piano e pompato ai locali con tubazioni flessibili; si "
         "stende e si livella a staggia fra le fasce di riferimento.",
         "Addetto alla realizzazione di sottofondi alleggeriti", 40, ED,
         ["Betoniera a bicchiere", "Impastatrice", "Pompa per malte e iniezioni", "Montacarichi a cremagliera",
          "Utensili manuali"],
         [_MMC_SACCHI, _CEMENTO, _POSTURE_GINOCCHIO, _SCIVOLAMENTI,
          r("Polveri e fibre", 2, 2,
            "Svuotare i sacchi di cemento e inerti leggeri senza scuoterli, in posizione sopravvento o con "
            "aspirazione; non aprire i sacchi di perle di polistirene all'aperto con vento.",
            DPI_INT + ", facciale filtrante FFP2"),
          r("Urti, colpi, impatti e compressioni", 2, 2,
            "Tubazioni della pompa stese lungo percorsi protetti e fissate nei cambi di piano; scollegarle solo "
            "dopo aver scaricato la pressione; comunicazione a vista o via radio tra chi pompa e chi getta.",
            DPI_INT + ", occhiali protettivi")]),
    fase("OI.02", C_OI, _MASSETTI, "Realizzazione di massetti tradizionali in sabbia e cemento",
         "Formazione del massetto di allettamento o di finitura con sabbia e cemento a consistenza di terra umida, "
         "su strato separatore e con fascia perimetrale comprimibile. Il materiale è confezionato a piè d'opera e "
         "trasportato ai piani con pompa pneumatica o a mano; si tira a staggia sulle guide e si liscia a "
         "frattazzo, anche con frattazzatrice; giunti secondo progetto e UNI EN 13813 per il materiale.",
         "Addetto alla realizzazione di massetti tradizionali", 45, ED,
         ["Pompa pneumatica per massetti", "Motocompressore", "Frattazzatrice meccanica", "Betoniera a bicchiere",
          "Utensili manuali"],
         [_MMC_SACCHI, _CEMENTO, _POSTURE_GINOCCHIO,
          r("Investimento da mezzi in manovra", 2, 4,
            "Cumulo di sabbia e postazione della pompa in area recintata fuori dalla viabilità; scarico degli "
            "autocarri guidato da un addetto a terra; indumenti ad alta visibilità per chi lavora all'esterno.",
            DPI_BASE),
          r("Getti e schizzi", 2, 3,
            "Tubazione della pompa pneumatica ancorata al punto di scarico, con diffusore o «cassa di scarico»; "
            "nessuno davanti allo sbocco durante l'espulsione; aprire i raccordi solo a macchina ferma e tubo "
            "scaricato.",
            DPI_INT + ", occhiali a maschera"),
          _SCIVOLAMENTI]),
    fase("OI.03", C_OI, _MASSETTI, "Realizzazione di massetti autolivellanti pompati",
         "Getto di massetti fluidi a base cementizia o di anidrite, anche sopra impianti radianti, preparati da "
         "silo o con impastatrice in continuo e pompati nei locali. Dopo la verifica delle quote con livello "
         "laser e la sigillatura dei perimetri, il getto è distribuito per campi e passato con barra "
         "frangibolle; gli addetti si muovono sul getto fresco con suole chiodate.",
         "Addetto alla realizzazione di massetti autolivellanti", 30, ED,
         ["Impastatrice", "Pompa per malte e iniezioni", "Utensili manuali"],
         [_CEMENTO, _SCHIZZI_MALTA,
          r("Scivolamenti e cadute a livello", 3, 2,
            "Suole chiodate fissate bene alle calzature; percorsi sui tubi radianti con passerelle; locali "
            "appena gettati interdetti con nastro e cartello fino alla pedonabilità.",
            DPI_INT + ", stivali di sicurezza"),
          r("Radiazioni ottiche", 1, 2,
            "Livello laser rotante di classe adeguata (2 o 2M) installato fuori dall'altezza degli occhi; non "
            "guardare il raggio; cartello di avvertimento nel locale.",
            DPI_INT),
          r("Posture incongrue", 3, 2,
            "Barra frangibolle e racle a manico lungo per lavorare in piedi; rotazione tra chi guida la "
            "tubazione e chi distribuisce il getto.",
            DPI_INT)]),

    # --- Intonaci, rasature e controsoffitti ---
    fase("OI.04", C_OI, _INTONACI, "Intonaci interni tradizionali eseguiti a mano",
         "Esecuzione di intonaci interni a più strati (rinzaffo, arriccio e finitura) con malte di calce, "
         "cemento o premiscelati, applicati a cazzuola su pareti e soffitti. Si predispongono fasce e paraspigoli, "
         "si tira a staggia e si rifinisce a frattazzo; la malta è confezionata in betoniera al piano.",
         "Addetto alla formazione di intonaci interni tradizionali", 60, ED,
         ["Betoniera a bicchiere", "Ponte su cavalletti", "Trabattello", "Utensili manuali"],
         [_CADUTA_INTERNI, _MMC_SACCHI, _CEMENTO, _SCHIZZI_MALTA, _POSTURE_SOFFITTO, _SCIVOLAMENTI]),
    fase("OI.05", C_OI, _INTONACI, "Intonaci interni eseguiti a macchina",
         "Applicazione a spruzzo di intonaci premiscelati di gesso, calce o calce-cemento con intonacatrice "
         "alimentata da sacchi o da silo, su pareti e soffitti preparati con paraspigoli e reti nei punti critici. "
         "Dopo lo spruzzo il materiale è livellato con staggia ad H e rifinito; la macchina e le tubazioni si "
         "lavano a fine turno.",
         "Addetto alla formazione di intonaci interni a macchina", 45, ED,
         ["Intonacatrice", "Trabattello", "Ponte su cavalletti", "Montacarichi a cremagliera", "Utensili manuali"],
         [_CADUTA_INTERNI, _MMC_SACCHI, _CEMENTO,
          r("Getti e schizzi", 3, 2,
            "Lancia orientata solo verso la parete; protezione degli occhi anche per chi livella; tubazioni "
            "srotolate senza pieghe; in caso di intasamento fermare la macchina e scaricare la pressione prima "
            "di aprire i raccordi (istruzioni del fabbricante).",
            DPI_INT + ", occhiali a maschera"),
          r("Polveri e fibre", 3, 2,
            "Caricamento della tramoggia senza scuotere i sacchi, con l'apertura rivolta verso la bocca di "
            "carico; locali ventilati; pulizia a umido delle zone di carico.",
            DPI_INT + ", facciale filtrante FFP2"),
          _POSTURE_SOFFITTO]),
    fase("OI.06", C_OI, _INTONACI, "Rasature, stuccature e carteggiature interne",
         "Stesura a spatola di rasanti in gesso o cementizi su intonaci, calcestruzzo e lastre di cartongesso, "
         "con eventuale annegamento di rete in fibra di vetro, stuccatura dei giunti e dei fori. A essiccazione "
         "avvenuta le superfici sono carteggiate a mano o con levigatrice a braccio collegata ad aspiratore.",
         "Addetto alla rasatura e stuccatura delle superfici interne", 65, ED,
         ["Levigatrice per pareti con aspirazione (giraffa)", "Aspiratore con filtro HEPA", "Impastatrice",
          "Trabattello", "Scala doppia", "Utensili manuali"],
         [_CADUTA_INTERNI,
          r("Polveri e fibre", 3, 2,
            "Carteggiatura con utensili collegati ad aspiratore; per i rasanti cementizi contenenti quarzo, "
            "valutazione della silice cristallina respirabile (Allegato XLII); locali ventilati e porte chiuse "
            "verso le zone finite; pulizia con aspiratore e non a secco.",
            DPI_INT + ", facciale filtrante FFP2, occhiali protettivi"),
          _POSTURE_SOFFITTO,
          r("Movimenti ripetitivi degli arti superiori", 3, 2,
            "Alternare rasatura, carteggiatura e preparazione dell'impasto; spatole leggere con impugnatura "
            "ergonomica; pause brevi e frequenti.",
            DPI_INT),
          r("Rischio chimico", 2, 2,
            "Rasanti cementizi irritanti per pelle e occhi: guanti in nitrile, protezione degli occhi durante la "
            "stesura a soffitto, lavaggio immediato degli schizzi; schede di sicurezza a disposizione.",
            DPI_INT + ", guanti in lattice o nitrile, occhiali protettivi")]),
    fase("OI.07", C_OI, _INTONACI, "Controsoffitti in lastre di cartongesso o a pannelli ispezionabili",
         "Tracciatura e fissaggio al solaio di pendini e orditura metallica, quindi posa di lastre di cartongesso "
         "avvitate (con stuccatura dei giunti) oppure di pannelli in fibra minerale, metallo o gesso appoggiati "
         "su profili a vista, secondo UNI 11424 e le istruzioni del sistema. Si coordinano i passaggi degli "
         "impianti e i botole d'ispezione.",
         "Addetto alla posa di controsoffitti", 50, ED,
         ["Sollevatore per lastre (alzapannelli)", "Martello perforatore (tassellatore)", "Avvitatore elettrico",
          "Pistola sparachiodi", "Trabattello", "Ponte su cavalletti", "Utensili manuali"],
         [_CADUTA_INTERNI, _POSTURE_SOFFITTO, _TAGLI_PROFILI,
          r("Caduta di materiale dall'alto o a livello", 2, 3,
            "Lastre tenute in posizione con l'alzapannelli fino all'avvitatura completa; nessuno sotto il "
            "pannello in sollevamento; tasselli idonei al solaio e al carico, provati a campione; pannelli e "
            "profili non lasciati appoggiati sui piani dei trabattelli in movimento.",
            DPI_CASCO + ", occhiali protettivi"),
          r("Movimentazione manuale dei carichi", 3, 2,
            "Lastre (da 20 a 35 kg secondo formato e spessore) trasportate in due, di costa, con carrello porta "
            "lastre; sollevamento a soffitto solo con alzapannelli o in due operatori.",
            DPI_INT),
          r("Polveri e fibre", 2, 2,
            "Taglio delle lastre con cutter per incisione e rottura, non con utensili a disco; pannelli in fibra "
            "minerale maneggiati con guanti e maniche lunghe; forature a soffitto con aspirazione.",
            DPI_INT + ", facciale filtrante FFP2, occhiali protettivi"),
          _ELETTRO_ESISTENTI]),

    # --- Pavimenti e rivestimenti ---
    fase("OI.08", C_OI, _PAVIMENTI, "Posa di pavimenti e rivestimenti in ceramica e gres",
         "Posa a colla di piastrelle e lastre in ceramica e gres porcellanato su massetti e pareti preparati, con "
         "adesivi cementizi stesi a spatola dentata, distanziatori e livellatori, secondo UNI 11493-1. I tagli "
         "si eseguono con taglierina manuale o elettrica ad acqua; seguono la stuccatura delle fughe e la pulizia "
         "finale.",
         "Addetto alla posa di pavimenti e rivestimenti in ceramica", 50, ED,
         ["Taglierina elettrica per piastrelle", "Smerigliatrice angolare", "Impastatrice",
          "Sollevatore a ventose per lastre e vetri", "Utensili manuali"],
         [_POSTURE_GINOCCHIO, _CEMENTO, _SILICE_TAGLIO,
          r("Movimentazione manuale dei carichi", 3, 3,
            "Scatole e sacchi depositati vicino al punto di posa con carrelli; lastre di grande formato "
            "movimentate con telai a ventose e in due o più addetti, tenute in verticale; pesi letti sugli "
            "imballi (Allegato XXXIII).",
            DPI_INT),
          r("Punture, tagli e abrasioni", 3, 2,
            "Spigoli delle piastrelle tagliate e delle lastre rotte maneggiati con guanti antitaglio; sfridi "
            "raccolti subito in contenitori rigidi.",
            DPI_INT + ", guanti antitaglio"),
          r("Rischio chimico", 2, 2,
            "Stucchi epossidici e detergenti acidi per la pulizia dei residui: schede di sicurezza, diluizioni "
            "indicate dal fabbricante, guanti in nitrile e protezione degli occhi, locali aerati; non mescolare "
            "detergenti acidi con prodotti a base di cloro.",
            DPI_INT + ", guanti in lattice o nitrile, occhiali protettivi")]),
    fase("OI.09", C_OI, _PAVIMENTI, "Posa, levigatura e finitura di pavimenti in legno",
         "Posa di parquet incollato su massetto con adesivi poliuretanici o silanici, flottante su materassino, o "
         "inchiodato su magatelli; i listoni si tagliano a misura con sega. Per i pavimenti grezzi seguono la "
         "levigatura con levigatrice a nastro e bordatrice, la stuccatura e la verniciatura o oliatura in più "
         "mani.",
         "Addetto alla posa e finitura di pavimenti in legno", 45, ED,
         ["Levigatrice per pavimenti", "Sega circolare", "Aspiratore con filtro HEPA", "Pistola sparachiodi",
          "Utensili manuali"],
         [_POSTURE_GINOCCHIO,
          r("Polveri e fibre: polveri di legno duro", 3, 3,
            "Le polveri di legno duro (rovere, faggio, essenze tropicali) sono cancerogene (Allegato XLII; valore "
            "limite 2 mg/m3 dell'Allegato XLIII): levigatrici con sacco e aspirazione efficienti, aspiratore di "
            "classe H per la pulizia, nessun uso di scope o aria compressa; registro degli esposti dove previsto.",
            DPI_INT + ", facciale filtrante FFP3"),
          r("Rischio chimico", 3, 2,
            "Adesivi bicomponenti, vernici e stucchi: preferire prodotti all'acqua e a basso contenuto di COV "
            "(D.Lgs. 161/2006); per i prodotti con diisocianati, formazione obbligatoria degli utilizzatori "
            "(REACH, Allegato XVII voce 74); locali ventilati durante e dopo l'applicazione.",
            DPI_INT + ", guanti in lattice o nitrile, maschera con filtro specifico"),
          r("Incendio ed esplosione", 2, 4,
            "Polvere fine di levigatura e vapori di vernici: svuotare spesso i sacchi in contenitori metallici "
            "chiusi; stracci imbevuti d'olio stesi ad asciugare o chiusi in contenitori con acqua per evitare "
            "l'autocombustione; nessuna fiamma o fonte di innesco; estintore nel locale.",
            DPI_INT),
          r("Movimenti ripetitivi degli arti superiori", 2, 2,
            "Alternare posa, taglio e preparazione; martelli e battitoi leggeri e con impugnatura antiscivolo; "
            "pause programmate.",
            DPI_INT)]),
    fase("OI.10", C_OI, _PAVIMENTI, "Realizzazione di pavimenti e rivestimenti in resina",
         "Preparazione meccanica del supporto con levigatura o pallinatura e aspirazione, quindi applicazione di "
         "primer, eventuali strati con spolvero di quarzo, rasature autolivellanti e finiture protettive a base di "
         "resine epossidiche, poliuretaniche o cementizie-resinose. I componenti si miscelano con trapano a "
         "frusta e si stendono a spatola, racla e rullo.",
         "Addetto alla realizzazione di pavimenti in resina", 40, ED,
         ["Levigatrice per pavimenti", "Aspiratore con filtro HEPA", "Impastatrice", "Ventilatore estrattore",
          "Utensili manuali"],
         [_RESINE_EPOSSIDICHE,
          r("Rischio chimico: diisocianati nelle resine poliuretaniche", 2, 3,
            "Gli utilizzatori di prodotti con diisocianati devono avere la formazione prevista dal REACH "
            "(Allegato XVII voce 74, Reg. UE 2020/1149) prima dell'uso; applicazione a rullo o racla, non a "
            "spruzzo, salvo protezione respiratoria adeguata; ventilazione forzata dei locali.",
            DPI_INT + ", guanti in lattice o nitrile, maschera con filtro specifico, tuta monouso"),
          _SILICE_TAGLIO, _INCENDIO_SOLVENTI,
          r("Ambienti confinati o sospetti di inquinamento", 1, 4,
            "In locali interrati o senza aperture (vani tecnici, vasche) verificare la ventilazione e misurare "
            "l'atmosfera prima e durante l'applicazione di prodotti a solvente; se il luogo rientra fra gli "
            "ambienti confinati, procedure e qualificazione del D.P.R. 177/2011.",
            DPI_INT + ", maschera con filtro specifico"),
          _POSTURE_GINOCCHIO]),
    fase("OI.11", C_OI, _PAVIMENTI, "Posa e levigatura di pavimenti in pietra naturale e marmo",
         "Posa di lastre di marmo, granito o pietra su letto di malta o con adesivi, previa formazione dei piani e "
         "taglio delle lastre con sega ad acqua. A presa avvenuta il pavimento è levigato a umido con mole "
         "diamantate di grana decrescente, stuccato e quindi lucidato o cristallizzato con prodotti specifici; "
         "i fanghi di levigatura vengono aspirati e smaltiti.",
         "Addetto alla posa e levigatura di pavimenti in pietra", 45, ED,
         ["Levigatrice per pavimenti", "Sega a disco per murature e calcestruzzo", "Smerigliatrice angolare",
          "Sollevatore a ventose per lastre e vetri", "Utensili manuali"],
         [_MMC_ELEMENTI, _POSTURE_GINOCCHIO, _SILICE_TAGLIO,
          r("Scivolamenti e cadute a livello", 3, 2,
            "Fanghi di levigatura rimossi con aspiraliquidi man mano; calzature con suola antiscivolo o stivali; "
            "locale in lavorazione interdetto ai non addetti.",
            DPI_INT + ", stivali di sicurezza"),
          r("Elettrocuzione", 2, 4,
            "Lavoro con acqua: macchine con grado di protezione adeguato, alimentate da quadro con differenziale "
            "da 30 mA; cavi sollevati dal pavimento bagnato e mai trascinati nel fango; prese e spine IP67.",
            DPI_INT + ", stivali di sicurezza"),
          r("Rischio chimico", 2, 2,
            "Prodotti per la lucidatura e la cristallizzazione (acido ossalico, fluosilicati, cere a solvente): "
            "schede di sicurezza, dosi del fabbricante, guanti in nitrile e occhiali, locali aerati.",
            DPI_INT + ", guanti in lattice o nitrile, occhiali a maschera")]),

    # --- Serramenti e opere in ferro ---
    fase("OI.12", C_OI, _SERRAMENTI, "Posa di serramenti interni ed esterni, soglie e davanzali",
         "Posa di soglie e davanzali in pietra o metallo su malta o adesivo, poi di controtelai, finestre, "
         "portefinestre e porte interne fissati con tasselli o zanche, sigillati con nastri, schiume "
         "poliuretaniche e sigillanti secondo UNI 11673-1. Gli elementi pesanti e le vetrate sono scaricati "
         "con autocarro con gru e movimentati con sollevatori a ventose.",
         "Addetto alla posa di serramenti", 30, ED,
         ["Autocarro con gru", "Sollevatore a ventose per lastre e vetri", "Martello perforatore (tassellatore)",
          "Avvitatore elettrico", "Smerigliatrice angolare", "Scala doppia", "Utensili manuali"],
         [_MMC_ELEMENTI,
          r("Caduta dall'alto", 2, 4,
            "Posa da davanzali e portefinestre ai piani: vano protetto da parapetto provvisorio o ponteggio "
            "esterno fino al fissaggio del serramento; se la protezione va rimossa, imbracatura agganciata a "
            "punto di ancoraggio interno idoneo; mai sporgersi oltre il vano.",
            DPI_CASCO + ", imbracatura, cordino con assorbitore"),
          r("Caduta di materiale dall'alto o a livello", 2, 3,
            "Serramenti e vetrate depositati in verticale su cavalletti o rastrelliere e legati; ante e vetri "
            "tenuti fermi fino al fissaggio; area esterna sottostante interdetta durante la posa ai piani.",
            DPI_CASCO),
          r("Rischio chimico", 2, 2,
            "Schiume poliuretaniche monocomponenti con diisocianati: formazione REACH degli addetti (Allegato "
            "XVII voce 74), uso con locali aerati e guanti in nitrile; sigillanti e primer secondo scheda di "
            "sicurezza.",
            DPI_INT + ", guanti in lattice o nitrile, occhiali protettivi"),
          _TAGLI_PROFILI,
          r("Urti, colpi, impatti e compressioni", 2, 3,
            "Mani lontane dal battente durante la regolazione delle ante; vetri e ante manovrati in due; "
            "ventose controllate prima di ogni sollevamento (indicatore di vuoto).",
            DPI_INT)]),
    fase("OI.13", C_OI, _SERRAMENTI, "Posa di opere in ferro: ringhiere, parapetti e cancelli",
         "Montaggio di ringhiere di scale e balconi, parapetti, grate e cancelli prefabbricati in officina, con "
         "fissaggio mediante tasselli chimici o meccanici, piastre saldate o zanche murate. Si eseguono in opera "
         "piccoli adattamenti con taglio e saldatura e il ritocco della protezione anticorrosiva.",
         "Addetto alla posa di opere in ferro", 40, ED,
         ["Autocarro con gru", "Saldatrice", "Smerigliatrice angolare", "Martello perforatore (tassellatore)",
          "Trabattello", "Utensili manuali"],
         [r("Caduta dall'alto", 3, 4,
            "Il parapetto definitivo sostituisce quello provvisorio: smontare la protezione provvisoria solo per "
            "il tratto in lavoro e rimontarla a fine turno (art. 146); su balconi e rampe senza protezione "
            "imbracatura agganciata a punto di ancoraggio idoneo; i parapetti posati vanno resi stabili prima "
            "di appoggiarvisi.",
            DPI_CASCO + ", imbracatura, cordino con assorbitore"),
          _MMC_ELEMENTI,
          r("Incendio ed esplosione", 2, 3,
            "Saldature e tagli in edifici con materiali combustibili: permesso di lavoro a caldo, rimozione o "
            "protezione con teli ignifughi dei materiali vicini, estintore a portata, controllo della zona per "
            "almeno 30 minuti dopo la fine.",
            DPI_INT),
          r("Radiazioni ottiche", 2, 2,
            "Schermi o tende intorno alla postazione di saldatura per proteggere gli altri lavoratori; nessuno "
            "guardi l'arco senza filtro adeguato (Titolo VIII, Capo V).",
            DPI_INT + ", schermo per saldatura, guanti per saldatura"),
          r("Rischio chimico", 2, 2,
            "Fumi di saldatura e vernici antiruggine: saldare in punti ventilati o con aspirazione localizzata; "
            "vernici a basso contenuto di COV applicate a pennello; schede di sicurezza.",
            DPI_INT + ", maschera con filtro specifico"),
          _TAGLI_PROFILI]),

    # --- Pitturazioni e isolamenti interni ---
    fase("OI.14", C_OI, _FINITURE, "Pitturazioni interne di pareti e soffitti",
         "Protezione di pavimenti e serramenti con teli e nastri, stuccatura delle imperfezioni, applicazione di "
         "fissativo e di due o più mani di pittura lavabile, traspirante o ai silicati, a rullo, pennello o con "
         "pistola airless. A fine giornata si lavano gli attrezzi raccogliendo le acque di lavaggio.",
         "Addetto alle pitturazioni interne", 70, ED,
         ["Pistola a spruzzo (airless)", "Trabattello", "Ponte su cavalletti", "Scala doppia", "Utensili manuali"],
         [_CADUTA_INTERNI, _POSTURE_SOFFITTO,
          r("Rischio chimico", 2, 2,
            "Pitture all'acqua a basso contenuto di COV (D.Lgs. 161/2006); con pitture ai silicati o alla calce "
            "(alcaline) protezione di occhi e pelle; spruzzo solo in locali ventilati e con facciale filtrante; "
            "schede di sicurezza in cantiere.",
            DPI_INT + ", guanti in lattice o nitrile, occhiali protettivi, facciale filtrante FFP2"),
          r("Getti e schizzi", 2, 2,
            "Spruzzo e lavori a soffitto con occhiali a maschera; non dirigere mai la pistola airless verso il "
            "corpo; sicura inserita a ogni pausa.",
            DPI_INT + ", occhiali a maschera"),
          r("Movimenti ripetitivi degli arti superiori", 3, 2,
            "Rulli con prolunga, alternanza tra rullo, pennello e preparazione; pause brevi e frequenti.",
            DPI_INT),
          r("Scivolamenti e cadute a livello", 2, 2,
            "Teli di protezione fissati a terra con nastro per evitare pieghe; latte e secchi fuori dai "
            "passaggi; schizzi di pittura sul pavimento puliti subito.",
            DPI_INT)]),
    fase("OI.15", C_OI, _FINITURE, "Verniciature interne di opere in legno e in metallo",
         "Preparazione di porte, infissi, ringhiere e opere metalliche con carteggiatura, sgrassaggio e "
         "spazzolatura, quindi applicazione di fondi, antiruggine, impregnanti e smalti a solvente o all'acqua a "
         "pennello, rullo o spruzzo. Gli elementi smontabili si verniciano in un locale dedicato e ventilato.",
         "Addetto alle verniciature interne", 60, ED,
         ["Pistola a spruzzo (airless)", "Smerigliatrice angolare", "Ventilatore estrattore", "Scala doppia",
          "Utensili manuali"],
         [r("Rischio chimico", 3, 3,
            "Smalti, diluenti e sverniciatori: valutazione del rischio con le schede di sicurezza (art. 223); "
            "preferire prodotti all'acqua; ventilazione forzata con estrattore verso l'esterno; recipienti "
            "chiusi quando non in uso; vietato mangiare e fumare nella zona.",
            DPI_INT + ", guanti in lattice o nitrile, maschera con filtro specifico, occhiali protettivi"),
          _INCENDIO_SOLVENTI,
          r("Polveri e fibre", 2, 3,
            "Prima di carteggiare vecchie vernici verificare la presenza di piombo; in tal caso sverniciatura a "
            "umido o chimica, aspirazione con filtro HEPA e pulizia accurata; nelle altre carteggiature "
            "utensili con aspirazione.",
            DPI_INT + ", facciale filtrante FFP3"),
          r("Ambienti confinati o sospetti di inquinamento", 1, 4,
            "Verniciature in locali piccoli e senza aperture (cavedi, vani interrati): ventilazione forzata "
            "continua, controllo dell'atmosfera, un secondo addetto all'esterno; procedure del D.P.R. 177/2011 "
            "se il luogo è un ambiente confinato.",
            DPI_INT + ", maschera con filtro specifico"),
          _CADUTA_INTERNI]),
    fase("OI.16", C_OI, _FINITURE, "Isolamenti termici e acustici interni",
         "Posa di contropareti e isolamenti a cappotto interno con pannelli in lana minerale, fibra di legno, "
         "polistirene o polistirene estruso, incollati o inseriti in orditura metallica, di materassini "
         "anticalpestio sotto i massetti e di fasce desolidarizzanti. Nelle intercapedini esistenti l'isolante "
         "sfuso può essere insufflato con macchina attraverso fori praticati nella muratura.",
         "Addetto alla posa di isolamenti interni", 40, ED,
         ["Macchina insufflatrice per isolanti sfusi", "Avvitatore elettrico", "Martello perforatore (tassellatore)",
          "Trabattello", "Utensili manuali"],
         [r("Polveri e fibre", 3, 2,
            "Pannelli in lana minerale tagliati con coltello e non con utensili veloci; insufflaggio con "
            "fori sigillati e locale chiuso ai non addetti; guanti e indumenti a maniche lunghe per le fibre "
            "irritanti; pulizia con aspiratore.",
            DPI_INT + ", facciale filtrante FFP2, occhiali protettivi, tuta monouso"),
          _CADUTA_INTERNI,
          r("Incendio ed esplosione", 2, 3,
            "Isolanti combustibili (polistireni, fibre vegetali) depositati lontano da lavorazioni a caldo e "
            "fonti di calore; nessuna saldatura o taglio a fiamma vicino ai pannelli già posati e non protetti; "
            "estintore nel piano.",
            DPI_INT),
          r("Rischio chimico", 2, 2,
            "Collanti e schiume per pannelli (anche a base di diisocianati): schede di sicurezza, formazione REACH "
            "per i prodotti con diisocianati, guanti in nitrile, locali aerati.",
            DPI_INT + ", guanti in lattice o nitrile"),
          _ELETTRO_ESISTENTI, _URTI_INTERNI]),
]


# ---------------------------------------------------------------------------------------------
# Ripristini e restauri
# ---------------------------------------------------------------------------------------------

_CA = "Ripristino di strutture in calcestruzzo armato"
_COMPOSITI = "Rinforzi strutturali con materiali compositi"
_MURATURE = "Consolidamento delle murature"
_SOLAI = "Consolidamento dei solai"
_SISMICO = "Interventi di miglioramento sismico"
_CONSERVATIVO = "Risanamento e restauro conservativo"

_RIPRISTINI = [
    # --- Ripristino di strutture in calcestruzzo armato ---
    fase("RR.01", C_RR, _CA, "Rimozione del calcestruzzo ammalorato mediante scalpellatura",
         "Battitura delle superfici per individuare le parti distaccate e rimozione del copriferro degradato con "
         "martelli demolitori leggeri e scalpelli, fino al calcestruzzo sano e oltre le armature corrose, come "
         "previsto dalla UNI EN 1504 e dal progetto. Le macerie sono raccolte sul piano di lavoro e calate a "
         "terra; travi, pilastri e frontalini di balconi si lavorano da ponteggio o piattaforma.",
         "Addetto alla rimozione del calcestruzzo ammalorato", 75, RIS_INF_RES,
         ["Martello demolitore", "Martello perforatore (tassellatore)", "Aspiratore con filtro HEPA",
          "Ponteggio metallico fisso", "Piattaforma di lavoro elevabile", "Utensili manuali"],
         [_CROLLO_ESISTENTI, _CADUTA_PONTEGGIO, _CADUTA_MATERIALE, _PROIEZIONE, _POLVERI_DEMOLIZIONE,
          r("Posture incongrue", 3, 2,
            "Scalpellature all'intradosso di solai e travi: piano di lavoro regolato all'altezza giusta, "
            "martelli leggeri sostenuti con le due mani, rotazione degli addetti e pause.",
            DPI_BASE)]),
    fase("RR.02", C_RR, _CA, "Idrodemolizione del calcestruzzo degradato",
         "Asportazione selettiva del calcestruzzo degradato con getto d'acqua ad altissima pressione emesso da "
         "robot radiocomandato o, per piccole superfici, da lancia manuale. L'area è delimitata e protetta con "
         "schermi; le acque di lavorazione e i fanghi sono raccolti, decantati e smaltiti come rifiuto.",
         "Addetto all'idrodemolizione", 40, RIS_INF,
         ["Idrodemolitrice (robot ad acqua ad alta pressione)", "Idropulitrice", "Pompa sommersa",
          "Piattaforma di lavoro elevabile", "Utensili manuali"],
         [r("Getti e schizzi", 2, 4,
            "Zona di lavoro recintata e segnalata con un raggio indicato dal fabbricante (di norma non meno di "
            "10 m); nessuno nell'area durante il getto, operatore dietro schermo o a distanza con radiocomando; "
            "pannelli di protezione sul lato opposto di solette e pareti, che il getto può forare; arresto della "
            "pompa prima di qualsiasi intervento.",
            DPI_BASE + ", visiera protettiva, indumenti impermeabili"),
          r("Proiezione di schegge e frammenti", 3, 3,
            "Schermi in lamiera o reti fitte intorno alla zona di getto; protezione di finestre e passaggi "
            "adiacenti; nessuno nel cono di proiezione.",
            DPI_BASE + ", visiera protettiva"),
          r("Rumore", 4, 3,
            "Livelli molto elevati: valutazione dell'esposizione (Titolo VIII, Capo II), area segnalata con "
            "obbligo di otoprotettori, operatore alla massima distanza consentita, lavori programmati in orari "
            "con meno addetti presenti.",
            DPI_BASE + ", cuffie antirumore"),
          r("Scivolamenti e cadute a livello", 3, 2,
            "Acqua e fanghi convogliati e pompati via con continuità; tubazioni ad alta pressione stese lungo "
            "percorsi segnalati; calzature con suola antiscivolo.",
            DPI_BASE + ", stivali di sicurezza"),
          r("Elettrocuzione", 1, 4,
            "Prima del getto individuare e disattivare linee elettriche annegate o vicine; prolunghe e quadri "
            "protetti dagli spruzzi e sollevati dal suolo bagnato.",
            DPI_BASE),
          _CROLLO_ESISTENTI]),
    fase("RR.03", C_RR, _CA, "Trattamento delle armature e ricostruzione con malte tixotropiche",
         "Pulizia delle armature dalla ruggine con spazzolatura meccanica o sabbiatura, eventuale integrazione "
         "delle barre ridotte di sezione, applicazione a pennello di boiacca passivante (UNI EN 1504-7). Dopo la "
         "saturazione del supporto si ricostruisce la sezione con malta cementizia fibrorinforzata tixotropica di "
         "classe R4 (UNI EN 1504-3), a cazzuola o a spruzzo, e si completa con rasatura protettiva.",
         "Addetto al ripristino del calcestruzzo armato", 60, RIS_INF_RES,
         ["Sabbiatrice", "Smerigliatrice angolare", "Impastatrice", "Intonacatrice", "Ponteggio metallico fisso",
          "Utensili manuali"],
         [_CADUTA_PONTEGGIO, _CEMENTO, _SCHIZZI_MALTA,
          r("Polveri e fibre", 3, 3,
            "Sabbiatura con abrasivi privi di silice libera, zona confinata con teli e aspirazione; addetto alla "
            "sabbiatura con casco a ventilazione o protezione respiratoria adeguata; altri lavoratori fuori "
            "dalla zona; pulizia con aspiratore.",
            DPI_BASE + ", facciale filtrante FFP3, occhiali a maschera"),
          r("Rischio chimico", 2, 2,
            "Passivanti e inibitori di corrosione: schede di sicurezza, applicazione a pennello con guanti in "
            "nitrile; primer e rasanti a base polimerica in locali o zone ventilate.",
            DPI_BASE + ", guanti in lattice o nitrile"),
          _MMC_SACCHI, _POSTURE_SOFFITTO]),

    # --- Rinforzi strutturali con materiali compositi ---
    fase("RR.04", C_RR, _COMPOSITI, "Rinforzo strutturale con sistemi FRP",
         "Rinforzo a flessione, taglio o confinamento di travi, pilastri e nodi con tessuti o lamine in fibra di "
         "carbonio, vetro o aramide incollati con resine epossidiche, secondo CNR-DT 200 R1/2013 e i sistemi "
         "qualificati. Il supporto è risanato, levigato e con spigoli arrotondati; si applicano primer, stucco "
         "epossidico, resina di impregnazione e tessuto, rullato per eliminare l'aria; eventuali connettori e "
         "spolvero di quarzo completano il sistema.",
         "Addetto al rinforzo strutturale con FRP", 35, RIS_INF_RES,
         ["Smerigliatrice angolare", "Aspiratore con filtro HEPA", "Impastatrice", "Trabattello",
          "Piattaforma di lavoro elevabile", "Utensili manuali"],
         [_RESINE_EPOSSIDICHE, _SILICE_TAGLIO, _CADUTA_PONTEGGIO,
          r("Polveri e fibre", 2, 2,
            "Tessuti e lamine tagliati con forbici o cutter, non con utensili a disco; le fibre di vetro e "
            "carbonio sono irritanti: maniche lunghe, guanti e raccolta degli sfridi in sacchi chiusi.",
            DPI_INT + ", occhiali protettivi, tuta monouso"),
          _POSTURE_SOFFITTO,
          r("Incendio ed esplosione", 1, 3,
            "Resine e solventi per la pulizia degli attrezzi conservati chiusi, lontani da fonti di calore; "
            "nessuna lavorazione a caldo sulle zone rinforzate (le resine si degradano con il calore); "
            "estintore vicino.",
            DPI_INT)]),
    fase("RR.05", C_RR, _COMPOSITI, "Rinforzo di murature e volte con sistemi FRCM e CRM",
         "Rinforzo di pareti, archi e volte in muratura con reti in fibra di vetro, basalto, carbonio o acciaio "
         "annegate in matrici inorganiche a base di calce o cemento, secondo CNR-DT 215/2018 e i sistemi "
         "qualificati. Si rimuove l'intonaco, si irruvidisce e satura il supporto, si stende la malta, si "
         "posiziona la rete e si inseriscono i connettori in fori sigillati con malta o resina.",
         "Addetto al rinforzo con sistemi FRCM", 45, RIS_RES,
         ["Martello perforatore (tassellatore)", "Martello demolitore", "Impastatrice", "Intonacatrice",
          "Ponteggio metallico fisso", "Trabattello", "Utensili manuali"],
         [_CADUTA_PONTEGGIO, _POLVERI_DEMOLIZIONE, _CEMENTO, _SCHIZZI_MALTA,
          r("Crollo o ribaltamento di strutture", 2, 4,
            "Volte e archi da rinforzare all'estradosso: centinature o puntellamenti all'intradosso quando "
            "richiesti dal progetto; rimozione dei riempimenti per settori simmetrici; camminamenti su tavole "
            "per ripartire i carichi; nessun deposito di materiale sulla volta.",
            DPI_CASCO),
          r("Punture, tagli e abrasioni", 2, 2,
            "Reti tagliate con cesoie e maneggiate con guanti; estremità di connettori e reti metalliche "
            "protette per evitare urti e punture.",
            DPI_INT + ", guanti antitaglio")]),

    # --- Consolidamento delle murature ---
    fase("RR.06", C_RR, _MURATURE, "Consolidamento di murature con iniezioni di miscele leganti",
         "Rimozione dell'intonaco, stuccatura dei giunti e delle lesioni, esecuzione di fori a quinconce con "
         "trapano a rotazione, inserimento e sigillatura di boccagli e lavaggio con acqua. La miscela a base di "
         "calce idraulica o legante compatibile è iniettata con pompa a bassa pressione dal basso verso l'alto, "
         "controllando la fuoriuscita dai fori adiacenti.",
         "Addetto al consolidamento di murature con iniezioni", 55, RIS_RES,
         ["Pompa per malte e iniezioni", "Impastatrice", "Trapano elettrico", "Martello perforatore (tassellatore)",
          "Ponteggio metallico fisso", "Utensili manuali"],
         [_CADUTA_PONTEGGIO,
          r("Getti e schizzi", 3, 2,
            "Pressione di iniezione contenuta nei valori di progetto e controllata con manometro; tubi e raccordi "
            "verificati prima di ogni ciclo; boccagli ben sigillati; mai guardare nei fori in pressione.",
            DPI_BASE + ", occhiali a maschera, guanti in lattice o nitrile"),
          _CEMENTO, _POLVERI_DEMOLIZIONE,
          r("Crollo o ribaltamento di strutture", 2, 4,
            "Murature molto degradate o lesionate puntellate prima di forare e iniettare; iniezioni per fasce "
            "orizzontali successive, rispettando i tempi di presa fra una fascia e la successiva per non "
            "caricare la parete con miscela fresca.",
            DPI_CASCO),
          _VIBRAZIONI := r(
            "Vibrazioni al sistema mano-braccio", 2, 2,
            "Fori di piccolo diametro a rotazione senza percussione sulle murature storiche; utensili con "
            "impugnature antivibranti; rotazione degli addetti nelle perforazioni prolungate (Titolo VIII, "
            "Capo III).",
            DPI_BASE + ", guanti antivibrazioni")]),
    fase("RR.07", C_RR, _MURATURE, "Consolidamento di murature con la tecnica del cuci-scuci",
         "Sostituzione per piccoli tratti alternati delle porzioni di muratura lesionate o degradate: puntellamento "
         "della parete, demolizione manuale di un cantiere di muratura, pulizia e bagnatura, ricostruzione con "
         "elementi e malta compatibili ben ammorsati, forzatura con cunei prima di procedere al tratto adiacente.",
         "Addetto al consolidamento di murature con cuci-scuci", 65, RIS_RES,
         ["Martello demolitore", "Betoniera a bicchiere", "Puntelli metallici", "Ponteggio metallico fisso",
          "Utensili manuali"],
         [r("Crollo o ribaltamento di strutture", 2, 4,
            "Puntellamento di architravi, solai e parete prima della demolizione (art. 150); tratti di dimensioni "
            "e sequenza alternata fissate dal progetto; non aprire un tratto finché l'adiacente non ha fatto "
            "presa ed è stato forzato; sorveglianza continua di lesioni e fessurimetri.",
            DPI_CASCO),
          _CADUTA_MATERIALE, _PROIEZIONE, _POLVERI_DEMOLIZIONE, _MMC_ELEMENTI, _CADUTA_PONTEGGIO]),
    fase("RR.08", C_RR, _MURATURE, "Consolidamento di murature con intonaco armato",
         "Placcaggio di pareti in muratura su una o due facce con rete in acciaio o in materiale composito "
         "collegata da connettori passanti o ancorati chimicamente e successivo getto a spruzzo o a mano di "
         "betoncino o malta strutturale. Si rimuove l'intonaco esistente, si scarnificano i giunti, si eseguono "
         "le perforazioni, si posano reti e connettori e si applica la malta in più strati.",
         "Addetto al consolidamento con intonaco armato", 55, RIS_RES,
         ["Martello demolitore", "Martello perforatore (tassellatore)", "Intonacatrice", "Impastatrice",
          "Tagliaferri", "Ponteggio metallico fisso", "Utensili manuali"],
         [_CADUTA_PONTEGGIO, _POLVERI_DEMOLIZIONE, _CEMENTO, _SCHIZZI_MALTA,
          r("Punture, tagli e abrasioni", 3, 2,
            "Reti elettrosaldate e spezzoni di connettori maneggiati con guanti antitaglio; estremità sporgenti "
            "dei ferri protette con cappellotti o piegate; sfridi raccolti subito.",
            DPI_BASE + ", guanti antitaglio"),
          r("Rischio chimico", 2, 2,
            "Ancoranti chimici in cartuccia (resine vinilestere o epossidiche): schede di sicurezza, guanti in "
            "nitrile, nessun contatto con la pelle, smaltimento delle cartucce come rifiuto.",
            DPI_BASE + ", guanti in lattice o nitrile"),
          _MMC_SACCHI]),

    # --- Consolidamento dei solai ---
    fase("RR.09", C_RR, _SOLAI, "Consolidamento di solai in legno con soletta collaborante",
         "Rimozione di pavimento e massetto fino al tavolato, verifica delle travi, puntellamento del solaio e "
         "posa di connettori metallici avvitati o incollati nelle travi. Si stendono telo protettivo e rete "
         "elettrosaldata e si getta una soletta sottile in calcestruzzo, anche alleggerito, collegata alle "
         "murature perimetrali con ancoraggi.",
         "Addetto al consolidamento di solai in legno", 50, RIS_RES,
         ["Puntelli metallici", "Avvitatore elettrico", "Trapano elettrico", "Martello perforatore (tassellatore)",
          "Pompa per malte e iniezioni", "Tagliaferri", "Utensili manuali"],
         [r("Crollo o ribaltamento di strutture", 2, 4,
            "Puntellamento dall'intradosso prima di rimuovere i pavimenti e fino a maturazione della soletta; "
            "travi marcescenti o attaccate da insetti segnalate al direttore dei lavori prima di caricarle; "
            "macerie e materiali portati via subito e non accumulati sul solaio.",
            DPI_CASCO),
          r("Caduta dall'alto", 2, 4,
            "Aperture e tratti di tavolato rimossi chiusi con tavole fissate o protetti con parapetto (art. 146); "
            "camminare solo su tavole d'appoggio che scaricano sulle travi.",
            DPI_CASCO),
          r("Polveri e fibre: polveri di legno duro", 2, 3,
            "Forature e tagli sulle travi in legno duro con aspirazione alla fonte; pulizia con aspiratore; "
            "valutazione dell'esposizione ad agente cancerogeno (Allegato XLII).",
            DPI_CASCO + ", facciale filtrante FFP3"),
          _CEMENTO, _MMC_SACCHI, _POSTURE_GINOCCHIO]),
    fase("RR.10", C_RR, _SOLAI, "Consolidamento di solai in latero-cemento",
         "Intervento su solai in latero-cemento con travetti degradati o insufficienti: puntellamento, eventuale "
         "messa in sicurezza dell'intradosso contro lo sfondellamento, ripristino dei travetti e getto di soletta "
         "collaborante armata, collegata con connettori inghisati nei travetti e nei cordoli. Il calcestruzzo è "
         "fornito con autobetoniera e pompato al piano.",
         "Addetto al consolidamento di solai in latero-cemento", 45, RIS_RES,
         ["Puntelli metallici", "Martello perforatore (tassellatore)", "Autobetoniera",
          "Autopompa per calcestruzzo", "Vibratore per calcestruzzo", "Tagliaferri", "Utensili manuali"],
         [r("Crollo o ribaltamento di strutture", 2, 4,
            "Puntelli su basi stabili e solai sottostanti verificati; nessun accumulo di calcestruzzo o materiali "
            "in un solo punto durante il getto; tempi di disarmo stabiliti dal direttore dei lavori.",
            DPI_CASCO),
          r("Caduta di materiale dall'alto o a livello", 3, 3,
            "Pignatte che possono sfondellare durante la foratura: lavori all'intradosso solo con zona "
            "sottostante interdetta o protetta da reti e tavolati; nessuno sotto il solaio durante le forature "
            "dall'alto.",
            DPI_CASCO + ", occhiali protettivi"),
          _CADUTA_INTERNI, _CEMENTO, _POLVERI_DEMOLIZIONE,
          r("Getti e schizzi", 2, 2,
            "Tubazione terminale della pompa guidata da un addetto in posizione stabile; comunicazione con "
            "l'operatore della pompa; protezione degli occhi durante il getto e la vibrazione.",
            DPI_CASCO + ", occhiali protettivi")]),

    # --- Interventi di miglioramento sismico ---
    fase("RR.11", C_RR, _SISMICO, "Inserimento di catene e tiranti metallici",
         "Collegamento di pareti contrapposte o di pareti e solai con catene in barre o trefoli d'acciaio inseriti "
         "in fori passanti eseguiti con carotatrice o in tracce, e ancorati a piastre o capochiave esterni. Si "
         "eseguono le perforazioni lunghe, l'inserimento e la giunzione delle barre, la posa dei capochiave in "
         "nicchie e la messa in tensione controllata con chiave dinamometrica, secondo NTC 2018 cap. 8.",
         "Addetto all'inserimento di catene e tiranti", 50, RIS_RES,
         ["Carotatrice", "Martello perforatore (tassellatore)", "Saldatrice", "Ponteggio metallico fisso",
          "Piattaforma di lavoro elevabile", "Utensili manuali"],
         [_CADUTA_PONTEGGIO,
          r("Movimentazione manuale dei carichi", 3, 3,
            "Barre lunghe e capochiave movimentati in più addetti o con argani e paranchi; percorsi interni "
            "liberi; barre ricevute in spezzoni e giuntate in opera dove il percorso è stretto.",
            DPI_BASE),
          r("Urti, colpi, impatti e compressioni", 2, 3,
            "Durante la tesatura nessuno davanti ai capochiave e lungo l'asse della catena; tesatura per gradi "
            "con chiave dinamometrica; filettature e dadi controllati prima del tiro.",
            DPI_BASE + ", occhiali protettivi"),
          _POLVERI_DEMOLIZIONE, _ELETTRO_ESISTENTI,
          r("Incendio ed esplosione", 1, 3,
            "Saldature e tagli vicino a orditure lignee: permesso di lavoro a caldo, protezione con teli "
            "ignifughi, estintore e controllo della zona dopo il lavoro.",
            DPI_BASE)]),
    fase("RR.12", C_RR, _SISMICO, "Realizzazione di cerchiature di aperture in murature portanti",
         "Apertura o allargamento di vani in murature portanti con inserimento di telaio metallico (cerchiatura) "
         "che ripristina rigidezza e resistenza della parete. Si puntella la muratura, si inseriscono e si "
         "inghisano i profilati dell'architrave in fasi successive, si taglia la muratura con sega a disco o a "
         "filo, si completano montanti e traverso inferiore, si saldano o bullonano i nodi e si sigillano gli "
         "interstizi con malta espansiva.",
         "Addetto alla realizzazione di cerchiature", 50, RIS_RES,
         ["Puntelli metallici", "Sega a disco per murature e calcestruzzo", "Sega a filo diamantato",
          "Martello demolitore", "Saldatrice", "Martello perforatore (tassellatore)", "Utensili manuali"],
         [r("Crollo o ribaltamento di strutture", 3, 4,
            "Puntelli e travi di ripartizione sopra e sotto il vano, dimensionati dal progettista, prima di ogni "
            "taglio (art. 150); inserimento dell'architrave da un lato alla volta; nessuno sotto la muratura "
            "non sostenuta; rimozione dei puntelli solo dopo la presa della malta di sigillatura.",
            DPI_CASCO),
          _CADUTA_MATERIALE, _PROIEZIONE, _POLVERI_DEMOLIZIONE,
          r("Movimentazione manuale dei carichi", 3, 3,
            "Profilati in acciaio sollevati con argani, paranchi o sollevatori e posizionati con l'aiuto di "
            "cavalletti; mai sostenere a braccia un profilo durante il fissaggio.",
            DPI_CASCO),
          r("Radiazioni ottiche", 2, 2,
            "Saldature in opera schermate verso gli altri lavoratori; filtri adeguati per il saldatore "
            "(Titolo VIII, Capo V).",
            DPI_CASCO + ", schermo per saldatura, guanti per saldatura"),
          _ELETTRO_ESISTENTI]),

    # --- Risanamento e restauro conservativo ---
    fase("RR.13", C_RR, _CONSERVATIVO, "Risanamento di murature umide con barriera chimica e intonaci deumidificanti",
         "Contro l'umidità di risalita si esegue alla base della parete una serie di fori inclinati in cui si "
         "iniettano o si lasciano assorbire per gravità prodotti idrofobizzanti (silani, silossani, creme) che "
         "formano una barriera. Si rimuove l'intonaco salinizzato fino a circa 50 cm oltre la zona umida, si "
         "puliscono i giunti e si applicano rinzaffo antisale e intonaco macroporoso deumidificante (UNI EN 998-1, "
         "tipo R).",
         "Addetto al risanamento delle murature umide", 55, RIS_RES,
         ["Trapano elettrico", "Martello demolitore", "Pompa per malte e iniezioni", "Intonacatrice",
          "Aspiratore con filtro HEPA", "Utensili manuali"],
         [r("Rischio chimico", 3, 2,
            "Prodotti a base di silani e silossani, talvolta in solvente: schede di sicurezza, ventilazione dei "
            "locali, guanti in nitrile e protezione degli occhi; sacche e taniche chiuse; nessuna fiamma.",
            DPI_INT + ", guanti in lattice o nitrile, occhiali a maschera, maschera con filtro specifico"),
          _POLVERI_DEMOLIZIONE, _POSTURE_GINOCCHIO, _CEMENTO, _ELETTRO_ESISTENTI,
          r("Rischio biologico", 2, 2,
            "Murature umide con muffe o in locali interrati e cantine: bagnare prima della rimozione, ventilare, "
            "evitare il contatto con la pelle, lavarsi prima di mangiare; segnalare al medico competente "
            "eventuali allergie.",
            DPI_INT + ", facciale filtrante FFP2")]),
    fase("RR.14", C_RR, _CONSERVATIVO, "Pulitura di superfici lapidee e intonaci storici",
         "Rimozione di depositi, croste nere, vecchie vernici e patine biologiche da paramenti in pietra, "
         "laterizio e intonaci storici, con metodi graduali scelti dopo prove su campioni e mappatura del degrado "
         "(UNI 11182): acqua nebulizzata, impacchi assorbenti, biocidi, microsabbiatura a bassa pressione, "
         "bisturi e spazzolini. Gli interventi su beni tutelati sono eseguiti da restauratori (D.Lgs. 42/2004, "
         "art. 29) secondo le indicazioni della Soprintendenza.",
         "Addetto alla pulitura di superfici lapidee e intonaci storici", 75, ("Restauri", "Ristrutturazioni"),
         ["Sabbiatrice", "Idropulitrice", "Aspiratore con filtro HEPA", "Ponteggio metallico fisso", "Trabattello",
          "Utensili manuali"],
         [_CADUTA_PONTEGGIO,
          r("Rischio chimico", 3, 2,
            "Impacchi con sali o solventi, biocidi e sverniciatori: preparazione secondo scheda tecnica e scheda di "
            "sicurezza, quantità minime, locali o zone di ponteggio ventilate, contenitori etichettati; biocidi "
            "registrati e impiegati come da etichetta.",
            DPI_BASE + ", guanti in lattice o nitrile, maschera con filtro specifico, occhiali a maschera"),
          r("Polveri e fibre", 3, 3,
            "Microsabbiatura con abrasivi privi di silice libera e in zona confinata da teli; aspirazione delle "
            "polveri; vecchie pitture verificate per piombo prima della rimozione; addetti esterni alla zona "
            "durante l'abrasione.",
            DPI_BASE + ", facciale filtrante FFP3, occhiali a maschera, tuta monouso"),
          r("Rischio biologico", 2, 2,
            "Guano di piccioni, muschi e patine biologiche: inumidire prima di rimuovere, nessuna spazzolatura a "
            "secco, lavaggio delle mani e dei DPI; vaccinazione antitetanica secondo il medico competente.",
            DPI_BASE + ", facciale filtrante FFP3, guanti in lattice o nitrile"),
          r("Movimenti ripetitivi degli arti superiori", 3, 2,
            "Puliture a bisturi e spazzolino per molte ore: alternanza di compiti, pause programmate, piano di "
            "lavoro all'altezza giusta e strumenti con impugnature ergonomiche.",
            DPI_BASE),
          r("Microclima", 2, 2,
            "Lavoro prolungato sul ponteggio esposto: teli di schermatura, pause, acqua disponibile, indumenti "
            "adeguati alla stagione.",
            DPI_BASE + ", indumenti per il freddo")]),
    fase("RR.15", C_RR, _CONSERVATIVO, "Consolidamento e stuccatura di superfici lapidee e intonaci storici",
         "Preconsolidamento delle parti in distacco con velinature, consolidamento della materia disgregata con "
         "silicato di etile, nanocalci o resine applicati a pennello, a spruzzo o per impregnazione, riadesione "
         "degli intonaci staccati con iniezioni di malte idrauliche premiscelate. Seguono le stuccature e le "
         "integrazioni con malte di calce e inerti selezionati, e l'eventuale protettivo idrorepellente.",
         "Addetto al consolidamento e alla stuccatura di superfici storiche", 80, ("Restauri",),
         ["Pompa per malte e iniezioni", "Aspiratore con filtro HEPA", "Ponteggio metallico fisso", "Trabattello",
          "Utensili manuali"],
         [_CADUTA_PONTEGGIO,
          r("Rischio chimico", 3, 3,
            "Silicato di etile e resine in solvente sviluppano vapori infiammabili e nocivi: schede di sicurezza, "
            "applicazione a basso impatto (pennello, siringa), ventilazione, maschera con filtri per vapori "
            "organici, guanti in nitrile; sorveglianza sanitaria se il rischio non è irrilevante (art. 229).",
            DPI_BASE + ", maschera con filtro specifico, guanti in lattice o nitrile, occhiali protettivi"),
          _INCENDIO_SOLVENTI,
          r("Rischio chimico: calce e malte idrauliche", 2, 2,
            "Calce e malte di calce alcaline: guanti in nitrile, protezione degli occhi durante le iniezioni, "
            "lavaggio immediato degli schizzi.",
            DPI_BASE + ", guanti in lattice o nitrile, occhiali a maschera"),
          r("Posture incongrue", 3, 2,
            "Interventi minuti e prolungati: piani di lavoro regolati alla quota della superficie, sedute o "
            "appoggi stabili sul ponteggio, pause e alternanza dei compiti.",
            DPI_BASE)]),
    fase("RR.16", C_RR, _CONSERVATIVO, "Restauro e consolidamento di elementi lignei",
         "Intervento su travi, capriate, solai e manufatti lignei storici (UNI 11138, UNI 11161): puntellamento, "
         "rimozione delle parti marcescenti, disinfestazione da insetti e funghi con prodotti biocidi, "
         "consolidamento con resine, protesi in legno o in resina armata con barre, ripristino dei collegamenti "
         "con staffe e piastre metalliche e trattamento protettivo finale.",
         "Addetto al restauro di elementi lignei", 70, RIS_RES,
         ["Puntelli metallici", "Sega circolare", "Trapano elettrico", "Motosega", "Aspiratore con filtro HEPA",
          "Ponteggio metallico fisso", "Utensili manuali"],
         [_CROLLO_ESISTENTI, _CADUTA_PONTEGGIO,
          r("Rischio chimico", 3, 3,
            "Biocidi antitarlo e antifungini e resine epossidiche: prodotti registrati usati come da etichetta e "
            "scheda di sicurezza; applicazione a pennello o iniezione, spruzzo solo con locale evacuato e "
            "ventilato; tempi di rientro indicati dal fabbricante; guanti in nitrile e tuta.",
            DPI_BASE + ", maschera con filtro specifico, guanti in lattice o nitrile, tuta monouso"),
          r("Polveri e fibre: polveri di legno duro", 3, 3,
            "Tagli e asportazioni su essenze dure (quercia, castagno) con aspirazione alla fonte; vecchi legni "
            "trattati con preservanti (creosoto, pentaclorofenolo) gestiti come potenzialmente pericolosi; "
            "pulizia con aspiratore di classe H (Allegato XLII).",
            DPI_BASE + ", facciale filtrante FFP3"),
          r("Movimentazione manuale dei carichi", 3, 3,
            "Travi e protesi movimentate con paranchi, argani o sollevatori; elementi lunghi trasportati in più "
            "addetti con presa coordinata (Allegato XXXIII).",
            DPI_BASE),
          r("Incendio ed esplosione", 2, 3,
            "Segatura e trucioli rimossi spesso; solventi e resine lontani da fonti di calore; nessuna lavorazione "
            "a caldo senza permesso, protezione delle orditure e controllo dopo il lavoro.",
            DPI_BASE)]),
]

LAVORAZIONI = _OPERE_INTERNE + _RIPRISTINI
