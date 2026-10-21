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
AUTONOMO_SUB = "Lavoratore autonomo subaffidatario"
TIPI_IMPRESA = [
    "Affidataria",
    "Affidataria ed esecutrice",
    "Esecutrice",
    "Subappaltatrice",
    AUTONOMO,
    AUTONOMO_SUB,
    "Nolo a caldo / fornitura con posa in opera",
]


def autonomo(impresa_o_tipo: dict[str, Any] | str) -> bool:
    tipo = impresa_o_tipo if isinstance(impresa_o_tipo, str) else impresa_o_tipo.get("tipo", "")
    return tipo.startswith(AUTONOMO)


def affidataria(impresa: dict[str, Any]) -> bool:
    return impresa.get("tipo", "").startswith("Affidataria")
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
    "Assistente di cantiere": "Coadiuva il direttore tecnico e il capocantiere nel controllo delle lavorazioni e "
                              "nella verifica dell'applicazione delle misure di sicurezza.",
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
    "Addetto antincendio": "Interviene sui principi d'incendio con i mezzi disponibili e chiama i Vigili del "
                           "fuoco (artt. 18 c. 1 lett. b e 46, D.M. 2 settembre 2021).",
    "Addetto antincendio ed evacuazione": "Interviene sui principi d'incendio con i mezzi disponibili, guida "
                                          "l'evacuazione e chiama i Vigili del fuoco (artt. 18 c. 1 lett. b e 46).",
    "Addetto all'evacuazione": "Guida i lavoratori verso il punto di raccolta, verifica che nessuno resti nelle "
                               "aree evacuate e ne riferisce al responsabile dell'emergenza (art. 43).",
    "Addetto alla gestione delle emergenze": "Coordina le procedure di emergenza del cantiere e i rapporti con i "
                                             "soccorsi esterni (art. 43).",
}
RSPP = "RSPP"
DATORE = "Datore di lavoro"
COMPITI_DATORE = ("Valuta i rischi e redige il POS, nomina RSPP e medico competente, designa gli addetti alle "
                  "emergenze, fornisce DPI e attrezzature conformi e cura informazione e formazione "
                  "(artt. 17, 18 e 96).")

PRIMO_SOCCORSO = "Addetto al primo soccorso"
ANTINCENDIO = "Addetto antincendio ed evacuazione"
DIRETTORE_TECNICO = "Direttore tecnico di cantiere"
CAPOCANTIERE = "Capocantiere"
PREPOSTO = "Preposto"
MEDICO = "Medico competente"

# Figure che l'Allegato XV punto 3.2.1 lett. a) chiede di indicare nel POS.
FIGURE_OBBLIGATORIE: list[tuple[tuple[str, ...], str, bool]] = [
    # (ruoli che soddisfano il requisito, descrizione, errore se manca)
    ((RSPP,), "il responsabile del servizio di prevenzione e protezione (o la spunta «il datore di lavoro "
              "svolge direttamente i compiti di RSPP»)", True),
    (("RLS", "RLST"), "il rappresentante dei lavoratori per la sicurezza: aziendale (RLS) o, se non eletto, "
                      "territoriale (RLST)", True),
    ((PRIMO_SOCCORSO,), "gli addetti al primo soccorso (o il datore di lavoro, che può svolgerne i compiti "
                        "fino a cinque lavoratori)", True),
    ((ANTINCENDIO, "Addetto antincendio", "Addetto alla gestione delle emergenze"),
     "gli addetti antincendio ed evacuazione (o il datore di lavoro, che può svolgerne i compiti fino a "
     "cinque lavoratori)", True),
    ((PREPOSTO,), "il preposto (obbligatorio dal D.L. 146/2021, art. 18 c. 1 lett. b-bis): un lavoratore "
                  "designato oppure il datore di lavoro, spuntandolo sopra", True),
    ((MEDICO,), "il medico competente, oppure dichiararlo non presente se la sorveglianza sanitaria non è "
                "prevista", False),
    ((DIRETTORE_TECNICO,), "il direttore tecnico di cantiere, oppure dichiararlo non presente", False),
    ((CAPOCANTIERE,), "il capocantiere, oppure dichiararlo non presente", False),
]

# Ruoli che il datore di lavoro può svolgere di persona (oltre a quello di RSPP, art. 34).
RUOLI_DATORE = [PRIMO_SOCCORSO, ANTINCENDIO, DIRETTORE_TECNICO, CAPOCANTIERE, PREPOSTO]
NOTE_RUOLI_DATORE = {
    PRIMO_SOCCORSO: "I compiti di primo soccorso sono svolti direttamente dal datore di lavoro (art. 34 c. 1-bis).",
    ANTINCENDIO: "I compiti di prevenzione incendi ed evacuazione sono svolti direttamente dal datore di lavoro "
                 "(art. 34 c. 1-bis).",
}
LIMITE_ART_34 = 5  # lavoratori oltre i quali il datore non può fare da addetto al primo soccorso e antincendio

# Figure che un'impresa può non avere: dichiarate non presenti non danno più avvisi e il POS lo riporta.
FIGURE_FACOLTATIVE = {
    DIRETTORE_TECNICO: "Il ruolo non è previsto nell'organizzazione dell'impresa per questo cantiere: la "
                       "direzione dei lavori dell'impresa è svolta dal datore di lavoro.",
    CAPOCANTIERE: "Non è presente un capocantiere: l'organizzazione delle squadre è curata dal datore di lavoro "
                  "o dal preposto.",
    MEDICO: "La sorveglianza sanitaria non è prevista per le mansioni svolte (art. 41): il medico competente "
            "non è nominato.",
}


def ruolo_riconosciuto(ruolo: str) -> str:
    """Ruolo con il nome usato dal programma anche se scritto a mano in un altro modo.

    Per esempio «addetto primo soccorso» o «Capo cantiere» valgono come le voci dell'elenco.
    """
    r = " ".join(ruolo.lower().replace("'", " ").split())
    if not r:
        return ""
    for nome in (*FIGURE_IMPRESA, RSPP):
        if r == nome.lower().replace("'", " "):
            return nome
    regole = [(("soccorso",), PRIMO_SOCCORSO), (("antincendio", "incendi", "evacuazione", "emergenz"), ANTINCENDIO),
              (("direttore tecnico", "direzione tecnica"), DIRETTORE_TECNICO),
              (("capocantiere", "capo cantiere"), CAPOCANTIERE), (("montaggio", "ponteggi"), ""),
              (("preposto",), PREPOSTO), (("medico",), MEDICO), (("rspp", "responsabile del servizio"), RSPP),
              (("rlst", "territoriale"), "RLST"), (("rls", "rappresentante dei lavoratori"), "RLS")]
    for parole, nome in regole:
        if any(p in r for p in parole):
            return nome or ruolo
    return ruolo


def _elenco(testo: str | None) -> list[str]:
    return [v.strip() for v in (testo or "").split(";") if v.strip()]


def ruoli_datore(impresa: dict[str, Any]) -> list[str]:
    return [r for r in _elenco(impresa.get("ruoli_datore")) if r in RUOLI_DATORE]


def figure_non_presenti(impresa: dict[str, Any]) -> list[tuple[str, str]]:
    """Figure dichiarate non presenti, con la motivazione (quella scritta o la frase predefinita)."""
    nota = (impresa.get("figure_motivazione") or "").strip()
    return [(r, nota or FIGURE_FACOLTATIVE[r]) for r in _elenco(impresa.get("figure_non_presenti"))
            if r in FIGURE_FACOLTATIVE]


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
    """Figure della sicurezza dell'impresa, compresi i ruoli svolti di persona dal datore di lavoro.

    Una stessa persona può avere più ruoli (per esempio capocantiere e addetto al primo soccorso):
    basta una riga per ruolo con lo stesso nominativo.
    """
    elenco = repo.elenco("figure", impresa_id=impresa["id"])
    datore = (impresa.get("datore_lavoro") or "").strip()
    if not datore:
        return elenco

    def del_datore(ruolo: str, nota: str) -> dict[str, Any]:
        return {"id": None, "impresa_id": impresa["id"], "ruolo": ruolo, "nome": datore,
                "qualifica": "Datore di lavoro", "codice_fiscale": "", "telefono": impresa.get("telefono", ""),
                "email": impresa.get("email", ""), "formazione": "", "formazione_scadenza": None, "nota": nota}

    aggiunte = []
    if impresa.get("rspp_datore"):
        elenco = [f for f in elenco if f["ruolo"] != RSPP]
        aggiunte.append(del_datore(RSPP, "I compiti del servizio di prevenzione e protezione sono svolti "
                                         "direttamente dal datore di lavoro (art. 34)."))
    for ruolo in ruoli_datore(impresa):
        if not any(f["ruolo"] == ruolo and f["nome"].strip() == datore for f in elenco):
            aggiunte.append(del_datore(ruolo, NOTE_RUOLI_DATORE.get(ruolo, "Ruolo svolto dal datore di lavoro.")))
    return aggiunte + elenco


def compiti(ruolo: str) -> str:
    return COMPITI_DATORE if ruolo == DATORE else FIGURE_IMPRESA.get(ruolo, "")


def sede(impresa: dict[str, Any]) -> str:
    comune = " ".join(v for v in (impresa.get("cap", ""), impresa.get("comune", "")) if v)
    if impresa.get("provincia"):
        comune += f" ({impresa['provincia']})"
    return ", ".join(v for v in (impresa["indirizzo"], comune.strip()) if v)


# Qualifiche e mansioni più comuni in edilizia (elenco modificabile nel campo).
MANSIONI = [
    "Operaio comune", "Operaio qualificato", "Operaio specializzato", "Operaio edile", "Capo squadra",
    "Manovale", "Muratore", "Carpentiere", "Ferraiolo", "Gruista", "Escavatorista", "Autista",
    "Ponteggiatore", "Elettricista", "Idraulico", "Impiantista termoidraulico", "Pittore", "Cartongessista",
    "Piastrellista", "Pavimentatore", "Intonacatore", "Impermeabilizzatore", "Lattoniere", "Saldatore",
    "Fabbro", "Serramentista", "Asfaltista", "Stradino", "Tecnico di cantiere", "Impiegato tecnico",
    "Apprendista",
]

# Dispositivi di protezione individuale per parte del corpo protetta (Allegato VIII D.Lgs. 81/2008).
CATALOGO_DPI: dict[str, list[str]] = {
    "Protezione della testa": ["casco", "casco con sottogola", "copricapo"],
    "Protezione dell'udito": ["otoprotettori", "cuffie antirumore", "inserti auricolari"],
    "Protezione degli occhi e del viso": ["occhiali protettivi", "occhiali a maschera", "schermo facciale",
                                          "visiera protettiva", "schermo per saldatura"],
    "Protezione delle vie respiratorie": ["maschera antipolvere", "facciale filtrante FFP2", "facciale filtrante FFP3",
                                          "maschera con filtro specifico", "autorespiratore"],
    "Protezione delle mani e delle braccia": ["guanti", "guanti antitaglio", "guanti antivibrazioni",
                                              "guanti in lattice o nitrile", "guanti dielettrici",
                                              "guanti per saldatura"],
    "Protezione dei piedi e delle gambe": ["calzature di sicurezza", "stivali di sicurezza", "ginocchiere",
                                           "ghette per saldatura"],
    "Protezione della pelle": ["crema protettiva"],
    "Protezione del tronco e dell'addome": ["grembiule per saldatura", "grembiule in cuoio"],
    "Protezione dell'intero corpo": ["attrezzatura anticaduta", "imbracatura", "cordino con assorbitore",
                                     "dispositivo retrattile", "giubbotto di salvataggio"],
    "Indumenti di protezione": ["indumenti protettivi", "indumenti ad alta visibilità", "tuta monouso",
                                "indumenti impermeabili", "indumenti per il freddo"],
}

# Informazione, formazione e addestramento: campo del lavoratore -> descrizione.
FORMAZIONE = [
    ("form_base", "Formazione generale e informazione di base (artt. 36 e 37)"),
    ("form_specifica", "Rischi specifici della mansione"),
    ("form_cantiere", "Rischi del cantiere contenuti in PSC e POS"),
    ("form_dpi3", "Uso dei DPI di terza categoria, con addestramento (art. 77 c. 5)"),
]


def nominativo(lavoratore: dict[str, Any]) -> str:
    return " ".join(v for v in (lavoratore.get("nome", ""), lavoratore.get("cognome", "")) if v).strip()


def formazione_lavoratore(lavoratore: dict[str, Any]) -> list[str]:
    voci = [testo for campo, testo in FORMAZIONE if lavoratore.get(campo)]
    if lavoratore.get("formazione", "").strip():
        voci.append(lavoratore["formazione"].strip())
    return voci


def dpi_lavoratore(lavoratore: dict[str, Any]) -> list[str]:
    import re

    return [v.strip() for v in re.split(r";|,|\n", lavoratore.get("dpi", "")) if v.strip()]
