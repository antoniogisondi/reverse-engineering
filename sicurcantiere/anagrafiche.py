"""Ruoli, tipologie d'impresa e figure della sicurezza, con i compiti previsti dal D.Lgs. 81/2008."""

from __future__ import annotations

from typing import Any

from sicurcantiere.repository import Repository

COMMITTENTE = "Committente"
RESPONSABILE_LAVORI = "Responsabile dei lavori"
CSP = "Coordinatore per la progettazione (CSP)"
CSE = "Coordinatore per l'esecuzione (CSE)"

# Soggetti del cantiere (lato committente).
RUOLI_SOGGETTI = [
    COMMITTENTE,
    RESPONSABILE_LAVORI,
    CSP,
    CSE,
    "Progettista",
    "Progettista delle strutture",
    "Progettista degli impianti",
    "Direttore dei lavori",
    "Direttore operativo",
    "Ispettore di cantiere",
    "Collaudatore",
    "Geologo",
    "Responsabile unico del progetto (RUP)",
]

AUTONOMO = "Lavoratore autonomo"
TIPI_IMPRESA = [
    "Affidataria",
    "Affidataria ed esecutrice",
    "Esecutrice",
    "Subappaltatrice",
    AUTONOMO,
    "Nolo a caldo / fornitura con posa in opera",
]
FORME_GIURIDICHE = [
    "Ditta individuale", "S.n.c.", "S.a.s.", "S.r.l.", "S.r.l. semplificata", "S.r.l. unipersonale",
    "S.p.A.", "Società cooperativa", "Consorzio", "Rete d'impresa",
]
CCNL = [
    "Edilizia - industria", "Edilizia - artigianato", "Edilizia - cooperative", "Edilizia - PMI",
    "Metalmeccanico - industria", "Metalmeccanico - artigianato (impianti)", "Legno e arredamento",
    "Lapidei", "Laterizi e manufatti in cemento", "Nessun dipendente",
]

# Figure della sicurezza dell'impresa: ruolo -> compiti (sintesi degli articoli del D.Lgs. 81/2008).
FIGURE_IMPRESA: dict[str, str] = {
    "Dirigente": "Attua le direttive del datore di lavoro organizzando l'attività e vigilando su di essa, "
                 "secondo i poteri conferiti (artt. 2 e 18).",
    "Direttore tecnico di cantiere": "Dirige tecnicamente i lavori dell'impresa, garantisce l'attuazione del POS e "
                                     "mantiene i rapporti con il coordinatore per l'esecuzione (Allegato XV 3.2.1).",
    "Capocantiere": "Organizza le squadre in cantiere, fa applicare le misure del PSC e del POS e segnala al "
                    "direttore tecnico le situazioni di pericolo.",
    "Preposto": "Sovrintende all'attività dei lavoratori, verifica l'osservanza delle disposizioni e l'uso dei DPI, "
                "interviene sui comportamenti non conformi e, se necessario, interrompe l'attività (art. 19).",
    "Preposto al montaggio dei ponteggi": "Dirige e sorveglia il montaggio, la trasformazione e lo smontaggio dei "
                                          "ponteggi secondo il PiMUS (art. 136).",
    "RSPP": "Individua e valuta i rischi, elabora le misure di prevenzione e le procedure, propone i programmi di "
            "informazione e formazione e partecipa alla riunione periodica (art. 33).",
    "ASPP": "Collabora con il responsabile del servizio di prevenzione e protezione nei compiti dell'art. 33.",
    "Medico competente": "Collabora alla valutazione dei rischi, programma ed effettua la sorveglianza sanitaria, "
                         "esprime i giudizi di idoneità alla mansione e custodisce le cartelle sanitarie (artt. 25 e 41).",
    "RLS": "Rappresenta i lavoratori per la sicurezza: è consultato sulla valutazione dei rischi, riceve il PSC e "
           "il POS, accede ai luoghi di lavoro e formula proposte (artt. 47-50 e 102).",
    "RLST": "Rappresentante territoriale dei lavoratori per la sicurezza, con le attribuzioni dell'art. 50 "
            "(art. 48).",
    "Addetto al primo soccorso": "Presta il primo soccorso all'infortunato, conosce i presidi sanitari del cantiere "
                                 "e attiva il soccorso esterno (artt. 18 c. 1 lett. b e 45, D.M. 388/2003).",
    "Addetto antincendio ed evacuazione": "Interviene sui principi d'incendio con i mezzi disponibili, guida "
                                          "l'evacuazione e chiama i Vigili del fuoco (artt. 18 c. 1 lett. b e 46).",
    "Addetto alla gestione delle emergenze": "Coordina le procedure di emergenza del cantiere e i rapporti con i "
                                             "soccorsi esterni (art. 43).",
}
RSPP = "RSPP"
DATORE = "Datore di lavoro"
COMPITI_DATORE = ("Valuta i rischi e redige il POS, nomina RSPP e medico competente, designa gli addetti alle "
                  "emergenze, fornisce DPI e attrezzature conformi e cura informazione e formazione "
                  "(artt. 17, 18 e 96).")

# Figure che l'Allegato XV punto 3.2.1 lett. a) chiede di indicare nel POS.
FIGURE_OBBLIGATORIE: list[tuple[tuple[str, ...], str, bool]] = [
    # (ruoli che soddisfano il requisito, descrizione, errore se manca)
    ((RSPP,), "il responsabile del servizio di prevenzione e protezione", True),
    (("RLS", "RLST"), "il rappresentante dei lavoratori per la sicurezza (aziendale o territoriale)", True),
    (("Addetto al primo soccorso",), "gli addetti al primo soccorso", True),
    (("Addetto antincendio ed evacuazione", "Addetto alla gestione delle emergenze"),
     "gli addetti antincendio, evacuazione e gestione delle emergenze", True),
    (("Medico competente",), "il medico competente, ove previsto", False),
    (("Direttore tecnico di cantiere",), "il direttore tecnico di cantiere", False),
    (("Capocantiere", "Preposto"), "il capocantiere o il preposto", False),
]


def soggetti(repo: Repository) -> list[dict[str, Any]]:
    """Soggetti del cantiere; se il committente è anche responsabile dei lavori lo aggiunge con quel ruolo."""
    elenco = repo.elenco("soggetti")
    if not repo.cantiere().get("committente_rl"):
        return elenco
    risultato = [s for s in elenco if s["ruolo"] != RESPONSABILE_LAVORI]
    posizione = next((i + 1 for i, s in enumerate(risultato) if s["ruolo"] == COMMITTENTE), len(risultato))
    for s in reversed([s for s in elenco if s["ruolo"] == COMMITTENTE]):
        risultato.insert(posizione, {**s, "ruolo": RESPONSABILE_LAVORI,
                                     "nota": "Il committente svolge anche il ruolo di responsabile dei lavori."})
    return risultato


def figure(repo: Repository, impresa: dict[str, Any]) -> list[dict[str, Any]]:
    """Figure della sicurezza dell'impresa, compreso il datore di lavoro come RSPP se ne svolge i compiti."""
    elenco = repo.elenco("figure", impresa_id=impresa["id"])
    if impresa.get("rspp_datore") and impresa.get("datore_lavoro", "").strip():
        elenco = [f for f in elenco if f["ruolo"] != RSPP]
        elenco.insert(0, {"id": None, "impresa_id": impresa["id"], "ruolo": RSPP, "nome": impresa["datore_lavoro"],
                          "qualifica": "Datore di lavoro", "codice_fiscale": "", "telefono": impresa["telefono"],
                          "email": impresa["email"], "formazione": "", "formazione_scadenza": None,
                          "nota": "I compiti del servizio di prevenzione e protezione sono svolti direttamente "
                                  "dal datore di lavoro (art. 34)."})
    return elenco


def compiti(ruolo: str) -> str:
    return COMPITI_DATORE if ruolo == DATORE else FIGURE_IMPRESA.get(ruolo, "")


def sede(impresa: dict[str, Any]) -> str:
    comune = " ".join(v for v in (impresa.get("cap", ""), impresa.get("comune", "")) if v)
    if impresa.get("provincia"):
        comune += f" ({impresa['provincia']})"
    return ", ".join(v for v in (impresa["indirizzo"], comune.strip()) if v)
