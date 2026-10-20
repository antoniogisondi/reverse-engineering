"""Rischi specifici (rumore, vibrazioni, movimentazione manuale) generati da macchine e attrezzi.

Servono a due cose:
- completare le schede dell'archivio a cui mancano (AGGIUNTE, applicate al caricamento);
- riconoscere i rischi specifici di una macchina o di un attrezzo inserito a mano con un nome
  che non è nell'archivio (PAROLE), così la fase in cui viene usato li presenta comunque.

Testi scritti per SicurCantiere a partire dal D.Lgs. 81/2008 (Titolo VI e Allegato XXXIII per la
movimentazione manuale dei carichi; Titolo VIII Capi II e III per rumore e vibrazioni, con i
valori di azione e limite degli artt. 189 e 201). Se una macchina non espone a un rischio
(per esempio è silenziata o non vibra), il rischio si elimina dalla fase e la valutazione
specifica ne dà conto.
"""

from __future__ import annotations

from typing import Any

from sicurcantiere.archivio_dati.base import r

RUMORE = "rumore"
MANO_BRACCIO = "mano_braccio"
CORPO_INTERO = "corpo_intero"
CARICHI = "carichi"

RISCHI: dict[str, dict[str, Any]] = {
    RUMORE: r(
        "Rumore", 3, 2,
        "Valutazione dell'esposizione (Titolo VIII, Capo II); macchina marcata CE con silenziatori e carter "
        "efficienti e manutenzione regolare; segnalazione e delimitazione delle zone oltre 85 dB(A); "
        "otoprotettori a disposizione oltre 80 dB(A) e obbligatori oltre 85 dB(A); rotazione degli addetti.",
        "Otoprotettori"),
    MANO_BRACCIO: r(
        "Vibrazioni al sistema mano-braccio", 3, 2,
        "Valutazione dell'esposizione (Titolo VIII, Capo III: valore d'azione 2,5 m/s², limite 5 m/s²); "
        "utensili a basse vibrazioni e in buono stato, con impugnature ammortizzate; utensile lasciato "
        "lavorare senza forzare la presa; pause e rotazione degli addetti; mani calde e asciutte.",
        "Guanti antivibrazioni"),
    CORPO_INTERO: r(
        "Vibrazioni al corpo intero", 2, 2,
        "Valutazione dell'esposizione (Titolo VIII, Capo III: valore d'azione 0,5 m/s², limite 1 m/s²); "
        "sedile ammortizzato regolato sul peso dell'operatore; sospensioni e pneumatici efficienti; "
        "piste livellate e velocità moderata sui terreni sconnessi; pause durante la giornata.",
        "Calzature di sicurezza"),
    CARICHI: r(
        "Movimentazione manuale dei carichi", 3, 2,
        "Valutazione secondo l'Allegato XXXIII e le norme ISO 11228; elementi pesanti movimentati con "
        "mezzi meccanici o da due persone; carico tenuto vicino al corpo, schiena dritta e senza "
        "torsioni; percorsi sgombri; formazione e informazione (art. 169).",
        "Guanti, calzature di sicurezza"),
}

# Schede dell'archivio a cui mancano rischi specifici tipici della macchina o dell'attrezzo.
AGGIUNTE: dict[str, tuple[str, ...]] = {
    "Escavatore": (CORPO_INTERO,),
    "Pala meccanica": (CORPO_INTERO,),
    "Autocarro": (RUMORE, CORPO_INTERO),
    "Autobetoniera": (RUMORE,),
    "Autopompa per calcestruzzo": (RUMORE,),
    "Autogru": (RUMORE,),
    "Vibrofinitrice": (RUMORE, CORPO_INTERO),
    "Autocarro con gru": (RUMORE, CORPO_INTERO),
    "Autocarro con cestello": (RUMORE,),
    "Escavatore con pinza demolitrice": (CORPO_INTERO,),
    "Carrello elevatore": (RUMORE, CORPO_INTERO),
    "Spazzatrice stradale": (CORPO_INTERO,),
    "Autobotte": (RUMORE, CORPO_INTERO),
    "Spanditrice di emulsione bituminosa": (RUMORE,),
    "Betoniera a bicchiere": (RUMORE, CARICHI),
    "Trapano elettrico": (RUMORE, MANO_BRACCIO),
    "Impastatrice": (RUMORE,),
    "Ponteggio metallico fisso": (CARICHI,),
    "Trabattello": (CARICHI,),
    "Casseforme": (CARICHI,),
    "Armatura delle pareti di scavo (blindaggio)": (CARICHI,),
    "Ponte su cavalletti": (CARICHI,),
}

# Parole chiave (minuscole) nel nome di una macchina o di un attrezzo fuori archivio.
PAROLE: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("escavat", "pala ", "pala meccanica", "ruspa", "bulldozer", "apripista", "grader", "livellatrice",
      "dumper", "autocarr", "camion", "rullo", "trattore", "terna", "minipala", "bobcat",
      "carrello elevatore", "muletto", "sollevatore telescopico", "finitrice", "fresa stradale",
      "scarificatrice", "spazzatrice"), (RUMORE, CORPO_INTERO)),
    (("martell", "demolitore", "smerigliatrice", "flex", "flessibile", "mola", "trapano", "tassellatore",
      "perforatore", "motosega", "decespugliatore", "levigatrice", "vibratore", "piastra vibrante",
      "costipatore", "frattazzatrice", "scanalatrice", "tagliasfalto", "carotatrice", "troncatrice",
      "scalpellatore", "sega a disco", "motoperforatrice", "trivella"), (RUMORE, MANO_BRACCIO)),
    (("betoniera", "compressore", "gruppo elettrogeno", "generatore", "pompa per calcestruzzo",
      "autopompa", "idropulitrice", "sabbiatrice", "intonacatrice", "impastatrice", "sega circolare",
      "taglierina", "cesoia", "sparachiodi", "autogru", "piegaferri", "tagliaferri"), (RUMORE,)),
    (("ponteggio", "trabattello", "casseform", "puntell", "parapett", "carriola", "blindaggio",
      "cavallett"), (CARICHI,)),
)


def chiavi_da_nome(nome: str) -> list[str]:
    """Rischi specifici riconosciuti dal nome della macchina o dell'attrezzo, senza ripetizioni."""
    testo = f" {nome.lower()} "
    chiavi: list[str] = []
    for parole, rischi in PAROLE:
        if any(p in testo for p in parole):
            chiavi += [k for k in rischi if k not in chiavi]
    return chiavi


def applica_aggiunte(attrezzature: dict[str, dict[str, Any]]) -> None:
    """Completa le schede dell'archivio con i rischi specifici mancanti."""
    for nome, chiavi in AGGIUNTE.items():
        scheda = attrezzature.get(nome)
        if scheda is None:
            continue
        presenti = {x["descrizione"].lower() for x in scheda["rischi"]}
        for k in chiavi:
            if RISCHI[k]["descrizione"].lower() not in presenti:
                scheda["rischi"].append(dict(RISCHI[k]))
