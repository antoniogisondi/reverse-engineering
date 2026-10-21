"""Assistente AI per velocizzare la compilazione.

L'assistente propone valori e testi; non salva nulla da solo: è sempre
l'utente a confermare e il professionista resta responsabile della
valutazione. Le risposte sono vincolate a uno schema JSON (structured
outputs), così possono essere inserite direttamente nei campi.

Fornitori supportati:
- DeepSeek, predefinito: chiave nelle impostazioni o variabile DEEPSEEK_API_KEY. L'API è
  compatibile con OpenAI ma accetta solo la modalità JSON (non lo schema rigido): lo schema
  viene descritto nelle istruzioni e la risposta controllata dal programma;
- OpenAI (ChatGPT): chiave nelle impostazioni o variabile OPENAI_API_KEY;
- Claude (Anthropic): chiave nelle impostazioni, variabile ANTHROPIC_API_KEY o
  profilo `ant auth login`.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from sicurcantiere.valutazioni.base import Campo, Metodo

OPENAI, ANTHROPIC, DEEPSEEK = "openai", "anthropic", "deepseek"
FORNITORE_PREDEFINITO = DEEPSEEK
VARIABILI_AMBIENTE = {DEEPSEEK: "DEEPSEEK_API_KEY", OPENAI: "OPENAI_API_KEY", ANTHROPIC: "ANTHROPIC_API_KEY"}
URL_DEEPSEEK = "https://api.deepseek.com"


@dataclass(frozen=True)
class Fornitore:
    nome: str
    modello_predefinito: str
    modelli: tuple[tuple[str, str], ...]


FORNITORI: dict[str, Fornitore] = {
    DEEPSEEK: Fornitore("DeepSeek", "deepseek-flash", (
        ("deepseek-flash", "DeepSeek V4.1 Flash"),
        ("deepseek-v4-pro", "DeepSeek V4 Pro (più accurato, più lento)"),
    )),
    OPENAI: Fornitore("OpenAI (ChatGPT)", "gpt-5.5", (
        ("gpt-5.5", "GPT-5.5"),
        ("gpt-5.4-mini", "GPT-5.4 mini (più rapido ed economico)"),
    )),
    ANTHROPIC: Fornitore("Claude (Anthropic)", "claude-opus-5-5", (
        ("claude-opus-5-5", "Claude Opus 5.5"),
        ("claude-sonnet-5-5", "Claude Sonnet 5.5 (più rapido ed economico)"),
        ("claude-haiku-5-5", "Claude Haiku 5.5 (il più economico)"),
    )),
}
# Claude: fallback lato server in caso di rifiuto da parte dei classificatori di sicurezza.
BETA_FALLBACK = "server-side-fallback-2026-07-01"
MAX_TOKEN = 16000

SISTEMA = (
    "Sei l'assistente di SicurCantiere, un programma per coordinatori della sicurezza e tecnici "
    "che redigono PSC, POS, PiMUS e valutazioni dei rischi nei cantieri italiani secondo il "
    "D.Lgs. 81/2008 e le norme tecniche (UNI ISO 11228-1, UNI ISO 11228-3, ecc.).\n"
    "Rispondi sempre in italiano, con linguaggio tecnico ma chiaro, adatto a un documento di "
    "sicurezza. Quando i dati forniti non bastano, scegli valori realistici e prudenti per un "
    "cantiere edile e dichiara ogni ipotesi in modo esplicito: le tue proposte saranno verificate "
    "da un professionista prima dell'uso. Non citare articoli di legge di cui non sei certo."
)


class ErroreAI(Exception):
    """Errore comprensibile all'utente durante una richiesta all'assistente."""


@dataclass(frozen=True)
class Compilazione:
    titolo: str
    mansione: str
    dati: dict[str, Any]
    ipotesi: list[str]


TIPI_ATTREZZATURA = ("Macchina", "Attrezzo", "Opera provvisionale")

# Descrizioni dei rischi specifici riconosciute dalle valutazioni automatiche.
RISCHI_SPECIFICI = ("Movimentazione manuale dei carichi", "Movimenti ripetitivi degli arti superiori", "Rumore",
                    "Vibrazioni al sistema mano-braccio", "Vibrazioni al corpo intero")


def _schema_campo(campo: Campo) -> dict[str, Any]:
    if campo.tipo == "numero":
        return {"type": "number", "description": f"{campo.etichetta} ({campo.suffisso.strip() or 'valore'})"}
    if campo.tipo == "scelta":
        return {"type": "string", "enum": [v for v, _ in campo.scelte], "description": campo.etichetta}
    return {"type": "string", "description": campo.etichetta}


def _oggetto(proprieta: dict[str, Any]) -> dict[str, Any]:
    return {"type": "object", "properties": proprieta, "required": list(proprieta),
            "additionalProperties": False}


def schema_metodo(metodo: Metodo) -> dict[str, Any]:
    proprieta: dict[str, Any] = {
        "titolo": {"type": "string", "description": "Titolo breve della valutazione"},
        "mansione": {"type": "string", "description": "Mansione o gruppo omogeneo di lavoratori"},
    }
    proprieta.update({c.chiave: _schema_campo(c) for c in metodo.campi})
    if metodo.colonne_compiti:
        proprieta["compiti"] = {
            "type": "array",
            "items": _oggetto({c.chiave: _schema_campo(c) for c in metodo.colonne_compiti}),
        }
    proprieta["ipotesi"] = {"type": "array", "items": {"type": "string"},
                            "description": "Ipotesi e stime fatte per i dati mancanti"}
    return _oggetto(proprieta)


def _descrivi_campi(campi: tuple[Campo, ...]) -> str:
    righe = []
    for c in campi:
        riga = f"- {c.chiave}: {c.etichetta}"
        if c.suffisso.strip():
            riga += f" [{c.suffisso.strip()}]"
        if c.scelte:
            riga += "; valori ammessi: " + ", ".join(f"{v} = {e}" for v, e in c.scelte)
        if c.aiuto:
            riga += f". {c.aiuto}"
        righe.append(riga)
    return "\n".join(righe)


class AssistenteAI:
    def __init__(self, fornitore: str = FORNITORE_PREDEFINITO, client: Any = None,
                 api_key: str | None = None, modello: str | None = None):
        if fornitore not in FORNITORI:
            fornitore = FORNITORE_PREDEFINITO
        self.fornitore = fornitore
        self._client = client
        self.api_key = api_key or None
        self.modello = modello or FORNITORI[fornitore].modello_predefinito

    @property
    def client(self) -> Any:
        if self._client is None:
            if self.fornitore == DEEPSEEK:
                import openai

                chiave = self.api_key or os.environ.get(VARIABILI_AMBIENTE[DEEPSEEK], "")
                if not chiave:
                    raise ErroreAI("Chiave API DeepSeek mancante: inserirla in Strumenti > Impostazioni "
                                   "assistente AI oppure nella variabile d'ambiente DEEPSEEK_API_KEY.")
                self._client = openai.OpenAI(api_key=chiave, base_url=URL_DEEPSEEK)
            elif self.fornitore == OPENAI:
                import openai

                self._client = openai.OpenAI(api_key=self.api_key) if self.api_key else openai.OpenAI()
            else:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else anthropic.Anthropic()
        return self._client

    def _richiesta(self, testo: str, schema: dict[str, Any]) -> dict[str, Any]:
        if self.fornitore == DEEPSEEK:
            testo_risposta = self._richiesta_deepseek(testo, schema)
        elif self.fornitore == OPENAI:
            testo_risposta = self._richiesta_openai(testo, schema)
        else:
            testo_risposta = self._richiesta_anthropic(testo, schema)
        try:
            dati = json.loads(testo_risposta)
        except json.JSONDecodeError as e:
            raise ErroreAI("Risposta dell'assistente non leggibile.") from e
        if not isinstance(dati, dict):
            raise ErroreAI("Risposta dell'assistente non leggibile.")
        mancanti = [k for k in schema.get("required", []) if k not in dati]
        if mancanti:
            # Solo in modalità JSON (DeepSeek) lo schema non è garantito dal servizio.
            raise ErroreAI("Risposta dell'assistente incompleta (mancano: " + ", ".join(mancanti) + "): riprovare.")
        return dati

    def _richiesta_deepseek(self, testo: str, schema: dict[str, Any]) -> str:
        istruzioni = (SISTEMA + "\n\nRispondi esclusivamente con un oggetto json valido, senza testo prima o "
                      "dopo, che rispetti questo schema JSON (tutte le proprietà sono obbligatorie):\n"
                      + json.dumps(schema, ensure_ascii=False))
        for _ in range(2):  # il servizio può restituire raramente un contenuto vuoto
            contenuto = self._richiesta_openai(testo + "\n\nRispondi in formato json.", schema, sistema=istruzioni,
                                               modalita_json=True, nome="DeepSeek")
            if contenuto.strip():
                return contenuto
        raise ErroreAI("L'assistente DeepSeek ha restituito una risposta vuota: riprovare.")

    def _richiesta_openai(self, testo: str, schema: dict[str, Any], sistema: str = SISTEMA,
                          modalita_json: bool = False, nome: str = "OpenAI") -> str:
        import openai

        formato = {"type": "json_object"} if modalita_json else {
            "type": "json_schema", "json_schema": {"name": "risposta", "schema": schema, "strict": True}}
        limite = {"max_tokens": 8000} if modalita_json else {"max_completion_tokens": MAX_TOKEN}
        try:
            risposta = self.client.chat.completions.create(
                model=self.modello,
                messages=[{"role": "system", "content": sistema}, {"role": "user", "content": testo}],
                response_format=formato,
                **limite,
            )
        except openai.AuthenticationError as e:
            raise ErroreAI(f"Chiave API {nome} non valida o mancante: controllare Strumenti > "
                           "Impostazioni assistente AI.") from e
        except openai.PermissionDeniedError as e:
            raise ErroreAI("La chiave API non ha i permessi per questo modello.") from e
        except openai.NotFoundError as e:
            raise ErroreAI(f"Modello «{self.modello}» non disponibile per questa chiave: "
                           "sceglierne un altro nelle impostazioni.") from e
        except openai.RateLimitError as e:
            raise ErroreAI(f"Limite di richieste o credito esaurito sull'account {nome}: "
                           "riprovare più tardi o controllare il piano.") from e
        except openai.APIConnectionError as e:
            raise ErroreAI("Impossibile contattare il servizio: controllare la connessione a internet.") from e
        except openai.APIStatusError as e:
            raise ErroreAI(f"Errore del servizio AI ({e.status_code}): {e.message}") from e
        except openai.OpenAIError as e:
            # Es. nessuna chiave configurata.
            raise ErroreAI(f"Assistente AI non configurato: {e}") from e

        scelta = risposta.choices[0]
        if getattr(scelta.message, "refusal", None):
            raise ErroreAI("L'assistente non ha potuto rispondere a questa richiesta.")
        if scelta.finish_reason == "length":
            raise ErroreAI("La risposta è stata troncata: provare con una descrizione più breve.")
        return scelta.message.content or ""

    def _richiesta_anthropic(self, testo: str, schema: dict[str, Any]) -> str:
        import anthropic

        try:
            risposta = self.client.beta.messages.create(
                model=self.modello,
                max_tokens=MAX_TOKEN,
                betas=[BETA_FALLBACK],
                fallbacks="default",
                system=SISTEMA,
                messages=[{"role": "user", "content": testo}],
                output_config={"effort": "medium", "format": {"type": "json_schema", "schema": schema}},
            )
        except anthropic.AuthenticationError as e:
            raise ErroreAI("Chiave API Anthropic non valida o mancante: controllare Strumenti > "
                           "Impostazioni assistente AI.") from e
        except anthropic.PermissionDeniedError as e:
            raise ErroreAI("La chiave API non ha i permessi per questo modello.") from e
        except anthropic.RateLimitError as e:
            raise ErroreAI("Troppe richieste in poco tempo: riprovare tra qualche istante.") from e
        except anthropic.APIConnectionError as e:
            raise ErroreAI("Impossibile contattare il servizio: controllare la connessione a internet.") from e
        except anthropic.APIStatusError as e:
            raise ErroreAI(f"Errore del servizio AI ({e.status_code}): {e.message}") from e
        except anthropic.AnthropicError as e:
            raise ErroreAI(f"Assistente AI non configurato: {e}") from e

        if risposta.stop_reason == "refusal":
            raise ErroreAI("L'assistente non ha potuto rispondere a questa richiesta.")
        if risposta.stop_reason == "max_tokens":
            raise ErroreAI("La risposta è stata troncata: provare con una descrizione più breve.")
        return next((b.text for b in risposta.content if b.type == "text"), "")

    # --- funzioni offerte al programma ---

    def compila_valutazione(self, metodo: Metodo, descrizione: str) -> Compilazione:
        testo = (
            f"Metodo di valutazione: {metodo.nome} ({metodo.norma}).\n{metodo.descrizione}\n\n"
            f"Parametri generali da compilare:\n{_descrivi_campi(metodo.campi)}\n"
        )
        if metodo.colonne_compiti:
            testo += (
                "\nElenco dei compiti: per ciascun compito distinto compilare:\n"
                f"{_descrivi_campi(metodo.colonne_compiti)}\n"
            )
        testo += (
            "\nRicava i parametri dalla descrizione dell'attività riportata sotto. Usa le unità "
            "indicate. Per ogni valore stimato o non dichiarato aggiungi una voce in 'ipotesi'.\n\n"
            f"<descrizione>\n{descrizione.strip()}\n</descrizione>"
        )
        risposta = self._richiesta(testo, schema_metodo(metodo))
        ipotesi = [str(i) for i in risposta.pop("ipotesi", []) or []]
        titolo = str(risposta.pop("titolo", "") or "")
        mansione = str(risposta.pop("mansione", "") or "")
        return Compilazione(titolo, mansione, metodo.normalizza(risposta), ipotesi)

    def suggerisci_rischi(self, lavorazione: str, attrezzature: list[str],
                          esistenti: list[str]) -> list[dict[str, Any]]:
        livello = {"type": "integer", "enum": [1, 2, 3, 4]}
        schema = _oggetto({"rischi": {"type": "array", "items": _oggetto({
            "descrizione": {"type": "string"},
            "probabilita": {**livello, "description": "Probabilità P da 1 (improbabile) a 4 (molto probabile)"},
            "danno": {**livello, "description": "Danno D da 1 (lieve) a 4 (gravissimo)"},
            "misure": {"type": "string", "description": "Misure di prevenzione e protezione"},
            "dpi": {"type": "string", "description": "DPI separati da virgola"},
            "fonte": {"type": "string", "description": "Macchina o attrezzatura da cui deriva il rischio, "
                                                       "scritta come nell'elenco; vuoto se deriva dalla lavorazione"},
        })}})
        testo = (
            "Individua i rischi della seguente lavorazione di cantiere che non sono già presenti "
            "nell'elenco esistente. Per ciascuno indica probabilità e danno (matrice 4x4), misure "
            "di prevenzione e protezione concrete e i DPI.\n"
            "Considera sia la lavorazione sia ciascuna macchina e attrezzatura indicata, e non "
            "tralasciare i rischi specifici che richiedono una valutazione dedicata: movimentazione "
            "manuale dei carichi (Titolo VI), movimenti ripetitivi degli arti superiori, rumore e "
            "vibrazioni (Titolo VIII, Capi II e III). Per questi usa esattamente una di queste "
            f"descrizioni: {'; '.join(RISCHI_SPECIFICI)}. Nel campo fonte indica la macchina o "
            "l'attrezzatura che genera il rischio (un rischio per ciascuna, per esempio rumore "
            "dell'escavatore e rumore del martello demolitore), oppure lascialo vuoto se il rischio "
            "deriva dalla lavorazione.\n\n"
            f"<lavorazione>{lavorazione.strip()}</lavorazione>\n"
            f"<attrezzature>{', '.join(attrezzature) or 'non indicate'}</attrezzature>\n"
            f"<rischi_esistenti>{'; '.join(esistenti) or 'nessuno'}</rischi_esistenti>"
        )
        rischi = self._richiesta(testo, schema).get("rischi") or []
        nomi = {a.lower(): a for a in attrezzature}
        validi = []
        for r in rischi:
            if not isinstance(r, dict) or not str(r.get("descrizione", "")).strip():
                continue
            validi.append({
                "descrizione": str(r["descrizione"]).strip(),
                "probabilita": min(max(int(r.get("probabilita", 2)), 1), 4),
                "danno": min(max(int(r.get("danno", 2)), 1), 4),
                "misure": str(r.get("misure", "")).strip(),
                "dpi": str(r.get("dpi", "")).strip(),
                "fonte": nomi.get(str(r.get("fonte", "") or "").strip().lower(), ""),
            })
        return validi

    def _schema_attrezzatura(self) -> dict[str, Any]:
        livello = {"type": "integer", "enum": [1, 2, 3, 4]}
        elenco = {"type": "array", "items": {"type": "string"}}
        return _oggetto({
            "nome": {"type": "string"},
            "tipo": {"type": "string", "enum": list(TIPI_ATTREZZATURA)},
            "descrizione": {"type": "string", "description": "Cos'è e a cosa serve, una o due frasi"},
            "prima": {**elenco, "description": "Misure prima dell'uso"},
            "durante": {**elenco, "description": "Misure durante l'uso"},
            "dopo": {**elenco, "description": "Misure dopo l'uso"},
            "dpi": {"type": "string", "description": "DPI dell'operatore separati da virgola"},
            "rischi": {"type": "array", "items": _oggetto({
                "descrizione": {"type": "string"},
                "probabilita": {**livello, "description": "Probabilità P da 1 (improbabile) a 4 (molto probabile)"},
                "danno": {**livello, "description": "Danno D da 1 (lieve) a 4 (gravissimo)"},
                "misure": {"type": "string"},
                "dpi": {"type": "string"},
            })},
        })

    @staticmethod
    def _attrezzatura_valida(a: Any) -> dict[str, Any] | None:
        if not isinstance(a, dict) or not str(a.get("nome", "")).strip():
            return None
        elenco = lambda k: [str(x).strip() for x in a.get(k) or [] if str(x).strip()]  # noqa: E731
        rischi = []
        for r in a.get("rischi") or []:
            if isinstance(r, dict) and str(r.get("descrizione", "")).strip():
                rischi.append({
                    "descrizione": str(r["descrizione"]).strip(),
                    "probabilita": min(max(int(r.get("probabilita", 2)), 1), 4),
                    "danno": min(max(int(r.get("danno", 2)), 1), 4),
                    "misure": str(r.get("misure", "")).strip(),
                    "dpi": str(r.get("dpi", "")).strip(),
                })
        tipo = str(a.get("tipo", ""))
        return {
            "nome": str(a["nome"]).strip(),
            "tipo": tipo if tipo in TIPI_ATTREZZATURA else TIPI_ATTREZZATURA[1],
            "descrizione": str(a.get("descrizione", "")).strip(),
            "prima": elenco("prima"), "durante": elenco("durante"), "dopo": elenco("dopo"),
            "dpi": str(a.get("dpi", "")).strip(),
            "rischi": rischi,
        }

    _ISTRUZIONI_ATTREZZATURE = (
        "Per ogni macchina, attrezzo o opera provvisionale indica i rischi per chi la usa e per chi "
        "lavora vicino, con probabilità e danno (matrice 4x4), misure e DPI, e le misure prima, "
        "durante e dopo l'uso. Non tralasciare i rischi specifici che richiedono una valutazione "
        "dedicata (rumore, vibrazioni, movimentazione manuale dei carichi, movimenti ripetitivi): "
        "per questi usa esattamente una di queste descrizioni: {specifici}. Indica anche gli altri "
        "rischi pertinenti (elettrico, investimento, ribaltamento, tagli, proiezione di schegge, "
        "polveri, incendio...)."
    )

    def suggerisci_attrezzature(self, lavorazione: str, dettaglio: str, esistenti: list[str],
                                catalogo: list[str]) -> list[dict[str, Any]]:
        """Macchine, attrezzi e opere provvisionali che servono alla lavorazione, con i loro rischi."""
        schema = _oggetto({"attrezzature": {"type": "array", "items": self._schema_attrezzatura()}})
        testo = (
            "Indica le macchine, gli attrezzi e le opere provvisionali che servono per eseguire la "
            "seguente lavorazione di cantiere e che non sono già nell'elenco esistente. Quando "
            "corrispondono, usa i nomi del catalogo esattamente come scritti.\n"
            + self._ISTRUZIONI_ATTREZZATURE.format(specifici="; ".join(RISCHI_SPECIFICI)) + "\n\n"
            f"<lavorazione>{lavorazione.strip()}</lavorazione>\n"
            f"<descrizione>{dettaglio.strip() or 'non indicata'}</descrizione>\n"
            f"<esistenti>{'; '.join(esistenti) or 'nessuna'}</esistenti>\n"
            f"<catalogo>{'; '.join(catalogo)}</catalogo>"
        )
        proposte = self._richiesta(testo, schema).get("attrezzature") or []
        nomi = {n.lower(): n for n in catalogo}
        gia = {n.lower() for n in esistenti}
        validi = []
        for a in proposte:
            a = self._attrezzatura_valida(a)
            if a is None or a["nome"].lower() in gia:
                continue
            a["nome"] = nomi.get(a["nome"].lower(), a["nome"])
            gia.add(a["nome"].lower())
            validi.append(a)
        return validi

    def completa_attrezzatura(self, nome: str, tipo: str, lavorazione: str,
                              rischi_esistenti: list[str]) -> dict[str, Any]:
        """Scheda d'uso e rischi (compresi quelli specifici) di una macchina o di un attrezzo."""
        testo = (
            "Compila la scheda d'uso della seguente attrezzatura impiegata in cantiere e indica i "
            "rischi che non sono già nell'elenco esistente.\n"
            + self._ISTRUZIONI_ATTREZZATURE.format(specifici="; ".join(RISCHI_SPECIFICI)) + "\n\n"
            f"<attrezzatura>{nome.strip()} ({tipo})</attrezzatura>\n"
            f"<lavorazione>{lavorazione.strip() or 'non indicata'}</lavorazione>\n"
            f"<rischi_esistenti>{'; '.join(rischi_esistenti) or 'nessuno'}</rischi_esistenti>"
        )
        a = self._attrezzatura_valida({"nome": nome, **self._richiesta(testo, self._schema_attrezzatura())})
        a["nome"] = nome
        presenti = {x.lower() for x in rischi_esistenti}
        a["rischi"] = [r for r in a["rischi"] if r["descrizione"].lower() not in presenti]
        return a

    def scrivi_sezione(self, sezione: str, contesto: str, testo_attuale: str = "") -> str:
        schema = _oggetto({"testo": {"type": "string", "description": "Testo della sezione, in paragrafi"}})
        richiesta = (
            f"Scrivi la sezione «{sezione}» di un documento di sicurezza per il cantiere descritto. "
            "Usa paragrafi brevi, senza titoli né elenchi puntati in markdown, adatti a un documento "
            "Word. Dove mancano dati specifici, scrivi tra parentesi quadre cosa va completato, "
            "per esempio [indicare il numero di telefono].\n\n"
            f"<cantiere>\n{contesto.strip()}\n</cantiere>"
        )
        if testo_attuale.strip():
            richiesta += f"\n\n<testo_attuale>\n{testo_attuale.strip()}\n</testo_attuale>\n" \
                         "Migliora e completa il testo attuale mantenendone le informazioni."
        return str(self._richiesta(richiesta, schema).get("testo", "")).strip()

    def analizza_psc(self, testo: str, avanzamento=None) -> Any:
        """Legge un PSC (testo già ripulito) a parti e ne unisce i dati: una sola lettura per documento."""
        from sicurcantiere import importa_psc

        pezzi = importa_psc.parti(testo)
        parziali = []
        for n, pezzo in enumerate(pezzi, 1):
            if avanzamento:
                avanzamento(n, len(pezzi))
            parziali.append(self._richiesta(importa_psc.ISTRUZIONI.format(n=n, totale=len(pezzi), testo=pezzo),
                                            importa_psc.SCHEMA))
        return importa_psc.unisci(parziali)

    def estrai_sds(self, testo_scheda: str) -> dict[str, Any]:
        """Dati principali di una scheda di dati di sicurezza, dal suo testo."""
        campi = {
            "nome": "Nome commerciale del prodotto (sezione 1)",
            "produttore": "Fornitore o produttore (sezione 1)",
            "codici_h": "Indicazioni di pericolo H ed EUH della miscela (sezione 2), separate da virgola, solo i codici",
            "avvertenza": "Avvertenza della sezione 2: Pericolo, Attenzione o vuoto",
            "data_revisione": "Data di revisione della scheda in formato AAAA-MM-GG, vuoto se assente",
            "stato_fisico": "Stato fisico (sezione 9): liquido, solido, polvere, pasta, gas, aerosol",
            "dpi": "DPI raccomandati nella sezione 8 (occhi, mani, pelle, vie respiratorie), in breve",
            "misure": "Principali misure di manipolazione sicura (sezione 7), in breve",
            "conservazione": "Condizioni di stoccaggio (sezione 7), in breve",
        }
        schema = _oggetto({k: {"type": "string", "description": v} for k, v in campi.items()})
        richiesta = (
            "Estrai i dati seguenti dalla scheda di dati di sicurezza riportata sotto. Riporta i "
            "valori come scritti nella scheda, senza inventare: se un dato manca lascia il campo vuoto.\n\n"
            f"<scheda>\n{testo_scheda.strip()}\n</scheda>"
        )
        risposta = self._richiesta(richiesta, schema)
        return {k: str(risposta.get(k, "") or "").strip() for k in campi}
