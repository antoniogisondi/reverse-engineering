"""Valutazioni dei rischi specifici richieste dai rischi delle lavorazioni.

Quando una lavorazione (o una sua macchina o attrezzatura) presenta un rischio che va
valutato con un metodo specifico - movimentazione manuale dei carichi (Titolo VI e
Allegato XXXIII), movimenti ripetitivi, rumore (Titolo VIII Capo II), vibrazioni (Titolo VIII
Capo III) - ogni fase con quel rischio deve essere coperta da una valutazione. Anche le
macchine e gli attrezzi portano i loro rischi specifici nella fase in cui sono usati: quelli
dell'archivio con la loro scheda, quelli inseriti a mano riconosciuti dal nome. `sincronizza`
crea le valutazioni mancanti e aggiunge le fasi scoperte, così nessuna fase resta fuori anche
se chi compila se ne dimentica. Le valutazioni create sono vuote: i parametri vanno inseriti
dall'utente, e fino ad allora documenti e controlli le segnalano come da eseguire.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sicurcantiere.repository import Repository


@dataclass(frozen=True)
class Gruppo:
    chiave: str
    titolo: str
    parole: tuple[str, ...]  # parole chiave (minuscole) nella descrizione del rischio
    metodi: tuple[str, ...]  # metodi che valutano il rischio
    predefinito: str


GRUPPI: tuple[Gruppo, ...] = (
    Gruppo("mmc", "Movimentazione manuale dei carichi",
           ("movimentazione manuale", "sollevamento manuale", "trasporto manuale", "traino e spinta",
            "traino o spinta", "spinta e traino"),
           ("niosh", "niosh_composto", "traino_spinta", "trasporto"), "niosh"),
    Gruppo("ocra", "Movimenti ripetitivi degli arti superiori",
           ("movimenti ripetitivi", "sovraccarico biomeccanico"), ("ocra",), "ocra"),
    Gruppo("rumore", "Esposizione al rumore", ("rumore",), ("rumore",), "rumore"),
    Gruppo("vibrazioni", "Esposizione alle vibrazioni", ("vibrazion",), ("vibrazioni",), "vibrazioni"),
)


def gruppo_rischio(descrizione: str) -> Gruppo | None:
    testo = descrizione.lower()
    return next((g for g in GRUPPI if any(p in testo for p in g.parole)), None)


def gruppo_metodo(metodo: str) -> Gruppo | None:
    return next((g for g in GRUPPI if metodo in g.metodi), None)


def _tipo(descrizione: str) -> tuple[str, str] | None:
    """Gruppo del rischio e, per le vibrazioni, il distretto (mano-braccio o corpo intero)."""
    g = gruppo_rischio(descrizione)
    if g is None:
        return None
    testo = descrizione.lower()
    return g.chiave, "mano" if "mano" in testo else "corpo" if "corpo" in testo else ""


def rischi_attesi(nome: str) -> list[dict[str, Any]]:
    """Rischi specifici di una macchina o di un attrezzo: dalla scheda dell'archivio o dal nome."""
    from sicurcantiere.archivio import ATTREZZATURE
    from sicurcantiere.archivio_dati import rischi_specifici

    scheda = ATTREZZATURE.get(nome)
    if scheda is not None:
        return [x for x in scheda["rischi"] if _tipo(x["descrizione"])]
    return [dict(rischi_specifici.RISCHI[k]) for k in rischi_specifici.chiavi_da_nome(nome)]


def completa_rischi_attrezzature(repo: Repository) -> list[str]:
    """Aggiunge alle fasi i rischi specifici delle loro macchine e attrezzi che mancano."""
    messaggi = []
    for a in repo.elenco("attrezzature"):
        presenti = {_tipo(x["descrizione"]) for x in repo.elenco("rischi", fase_id=a["fase_id"])
                    if x["fonte"] == a["nome"]}
        for rischio in rischi_attesi(a["nome"]):
            if _tipo(rischio["descrizione"]) not in presenti:
                repo.inserisci("rischi", fase_id=a["fase_id"], fonte=a["nome"],
                               **{k: rischio[k] for k in ("descrizione", "probabilita", "danno", "misure", "dpi")})
                presenti.add(_tipo(rischio["descrizione"]))
                messaggi.append(f"{a['nome']}: aggiunto il rischio «{rischio['descrizione']}».")
    return messaggi


def da_eseguire(repo: Repository, valutazione_id: int) -> bool:
    """Vero se i parametri della valutazione non sono mai stati inseriti."""
    return not repo.dati_valutazione(valutazione_id)


def rischi_specifici(repo: Repository) -> dict[str, dict[int, list[dict[str, Any]]]]:
    """Per ogni gruppo, le fasi che presentano il rischio con i rischi corrispondenti."""
    esito: dict[str, dict[int, list[dict[str, Any]]]] = {}
    for r in repo.elenco("rischi"):
        g = gruppo_rischio(r["descrizione"])
        if g is not None:
            esito.setdefault(g.chiave, {}).setdefault(r["fase_id"], []).append(r)
    return esito


def _copertura(repo: Repository, valutazioni: list[dict[str, Any]],
               fasi: dict[int, list[dict[str, Any]]]) -> dict[int, set[int]]:
    copertura = {v["id"]: set(repo.fasi_valutazione(v["id"])) for v in valutazioni}
    for fase, rischi in fasi.items():
        for r in rischi:
            if r["valutazione_id"] in copertura:
                copertura[r["valutazione_id"]].add(fase)
    return copertura


def fasi_scoperte(repo: Repository) -> dict[str, list[int]]:
    """Fasi con un rischio specifico non coperte da alcuna valutazione del metodo giusto."""
    valutazioni = repo.elenco("valutazioni")
    esito = {}
    for chiave, fasi in rischi_specifici(repo).items():
        g = next(x for x in GRUPPI if x.chiave == chiave)
        copertura = _copertura(repo, [v for v in valutazioni if v["metodo"] in g.metodi], fasi)
        coperte = set().union(*copertura.values()) if copertura else set()
        scoperte = sorted(f for f in fasi if f not in coperte)
        if scoperte:
            esito[chiave] = scoperte
    return esito


def sincronizza(repo: Repository) -> list[str]:
    """Completa i rischi specifici delle attrezzature, crea le valutazioni mancanti e collega le
    fasi scoperte; restituisce cosa è stato fatto."""
    messaggi = completa_rischi_attrezzature(repo)
    for chiave, fasi in rischi_specifici(repo).items():
        g = next(x for x in GRUPPI if x.chiave == chiave)
        valutazioni = [v for v in repo.elenco("valutazioni") if v["metodo"] in g.metodi]
        copertura = _copertura(repo, valutazioni, fasi)
        coperte = set().union(*copertura.values()) if copertura else set()
        scoperte = sorted(f for f in fasi if f not in coperte)
        if scoperte:
            if valutazioni:
                destinazione = valutazioni[0]["id"]
                titolo = valutazioni[0]["titolo"] or g.titolo
                messaggi.append(f"«{titolo}»: aggiunte {len(scoperte)} lavorazioni con lo stesso rischio.")
            else:
                imprese = {repo.leggi("fasi", f)["impresa_id"] for f in scoperte}
                destinazione = repo.inserisci("valutazioni", metodo=g.predefinito, titolo=g.titolo,
                                              impresa_id=imprese.pop() if len(imprese) == 1 else None)
                copertura[destinazione] = set()
                messaggi.append(f"Creata la valutazione «{g.titolo}» per {len(scoperte)} lavorazioni: "
                                "inserire i parametri.")
            copertura[destinazione] |= set(scoperte)
            repo.salva_fasi_valutazione(destinazione, copertura[destinazione])
        # Ogni rischio rimanda alla valutazione che copre la sua fase.
        for fase, rischi in fasi.items():
            v = next((v for v, c in copertura.items() if fase in c), None)
            for r in rischi:
                if r["valutazione_id"] not in copertura and v is not None:
                    repo.aggiorna("rischi", r["id"], valutazione_id=v)
    return messaggi
