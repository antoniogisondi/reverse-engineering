"""Sostanze e miscele pericolose: classificazione dalle indicazioni di pericolo (frasi H).

Dai codici H riportati nella scheda di dati di sicurezza (sezione 2) si
ricavano i pittogrammi (Regolamento CLP 1272/2008) e le categorie di pericolo
rilevanti per la valutazione del rischio chimico (Titolo IX del D.Lgs.
81/2008), con le relative misure. Il risultato orienta la valutazione ma non
la sostituisce.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Indicazioni di pericolo (Regolamento CLP, Allegato III).
FRASI_H: dict[str, str] = {
    "H200": "Esplosivo instabile",
    "H201": "Esplosivo; pericolo di esplosione di massa",
    "H202": "Esplosivo; grave pericolo di proiezione",
    "H203": "Esplosivo; pericolo di incendio, di spostamento d'aria o di proiezione",
    "H204": "Pericolo di incendio o di proiezione",
    "H205": "Pericolo di esplosione di massa in caso d'incendio",
    "H220": "Gas altamente infiammabile",
    "H221": "Gas infiammabile",
    "H222": "Aerosol altamente infiammabile",
    "H223": "Aerosol infiammabile",
    "H224": "Liquido e vapori altamente infiammabili",
    "H225": "Liquido e vapori facilmente infiammabili",
    "H226": "Liquido e vapori infiammabili",
    "H228": "Solido infiammabile",
    "H229": "Contenitore pressurizzato: può scoppiare se riscaldato",
    "H240": "Rischio di esplosione per riscaldamento",
    "H241": "Rischio d'incendio o di esplosione per riscaldamento",
    "H242": "Rischio d'incendio per riscaldamento",
    "H250": "Spontaneamente infiammabile all'aria",
    "H251": "Autoriscaldante; può infiammarsi",
    "H252": "Autoriscaldante in grandi quantità; può infiammarsi",
    "H260": "A contatto con l'acqua libera gas infiammabili che possono infiammarsi spontaneamente",
    "H261": "A contatto con l'acqua libera gas infiammabili",
    "H270": "Può provocare o aggravare un incendio; comburente",
    "H271": "Può provocare un incendio o un'esplosione; molto comburente",
    "H272": "Può aggravare un incendio; comburente",
    "H280": "Contiene gas sotto pressione; può esplodere se riscaldato",
    "H281": "Contiene gas refrigerato; può provocare ustioni o lesioni criogeniche",
    "H290": "Può essere corrosivo per i metalli",
    "H300": "Letale se ingerito",
    "H301": "Tossico se ingerito",
    "H302": "Nocivo se ingerito",
    "H304": "Può essere letale in caso di ingestione e di penetrazione nelle vie respiratorie",
    "H310": "Letale per contatto con la pelle",
    "H311": "Tossico per contatto con la pelle",
    "H312": "Nocivo per contatto con la pelle",
    "H314": "Provoca gravi ustioni cutanee e gravi lesioni oculari",
    "H315": "Provoca irritazione cutanea",
    "H317": "Può provocare una reazione allergica cutanea",
    "H318": "Provoca gravi lesioni oculari",
    "H319": "Provoca grave irritazione oculare",
    "H330": "Letale se inalato",
    "H331": "Tossico se inalato",
    "H332": "Nocivo se inalato",
    "H334": "Può provocare sintomi allergici o asmatici o difficoltà respiratorie se inalato",
    "H335": "Può irritare le vie respiratorie",
    "H336": "Può provocare sonnolenza o vertigini",
    "H340": "Può provocare alterazioni genetiche",
    "H341": "Sospettato di provocare alterazioni genetiche",
    "H350": "Può provocare il cancro",
    "H350i": "Può provocare il cancro se inalato",
    "H351": "Sospettato di provocare il cancro",
    "H360": "Può nuocere alla fertilità o al feto",
    "H361": "Sospettato di nuocere alla fertilità o al feto",
    "H362": "Può essere nocivo per i lattanti allattati al seno",
    "H370": "Provoca danni agli organi",
    "H371": "Può provocare danni agli organi",
    "H372": "Provoca danni agli organi in caso di esposizione prolungata o ripetuta",
    "H373": "Può provocare danni agli organi in caso di esposizione prolungata o ripetuta",
    "H400": "Molto tossico per gli organismi acquatici",
    "H410": "Molto tossico per gli organismi acquatici con effetti di lunga durata",
    "H411": "Tossico per gli organismi acquatici con effetti di lunga durata",
    "H412": "Nocivo per gli organismi acquatici con effetti di lunga durata",
    "H413": "Può essere nocivo per gli organismi acquatici con effetti di lunga durata",
    "H420": "Nuoce alla salute pubblica e all'ambiente distruggendo l'ozono dello strato superiore dell'atmosfera",
    "EUH066": "L'esposizione ripetuta può provocare secchezza e screpolature della pelle",
    "EUH204": "Contiene isocianati. Può provocare una reazione allergica",
    "EUH208": "Contiene una sostanza sensibilizzante. Può provocare una reazione allergica",
}

PITTOGRAMMI: dict[str, str] = {
    "GHS01": "Esplosivo",
    "GHS02": "Infiammabile",
    "GHS03": "Comburente",
    "GHS04": "Gas sotto pressione",
    "GHS05": "Corrosivo",
    "GHS06": "Tossicità acuta",
    "GHS07": "Nocivo / irritante",
    "GHS08": "Pericolo per la salute",
    "GHS09": "Pericolo per l'ambiente",
}

_PITTOGRAMMA_DA_CODICE: dict[str, str] = {}
for _p, _codici in {
    "GHS01": "H200 H201 H202 H203 H204 H240 H241",
    "GHS02": "H220 H221 H222 H223 H224 H225 H226 H228 H241 H242 H250 H251 H252 H260 H261",
    "GHS03": "H270 H271 H272",
    "GHS04": "H280 H281",
    "GHS05": "H290 H314 H318",
    "GHS06": "H300 H301 H310 H311 H330 H331",
    "GHS07": "H302 H312 H315 H317 H319 H332 H335 H336",
    "GHS08": "H304 H334 H340 H341 H350 H351 H360 H361 H370 H371 H372 H373",
    "GHS09": "H400 H410 H411",
}.items():
    for _c in _codici.split():
        _PITTOGRAMMA_DA_CODICE.setdefault(_c, _p)

# Niente \b finale: nei PDF il codice è spesso attaccato al testo che segue ("H318Provoca").
_RE_CODICE = re.compile(r"\b(EUH\s?\d{3}|H\s?\d{3}(?:i|[FfDd]{1,2})?)(?![0-9])")


def codici_h(testo: str) -> list[str]:
    """Estrae i codici H ed EUH da un testo, normalizzati e senza doppioni, nell'ordine trovato."""
    visti: dict[str, None] = {}
    for grezzo in _RE_CODICE.findall(testo or ""):
        codice = grezzo.replace(" ", "")
        if codice.startswith("EUH"):
            visti.setdefault(codice.upper(), None)
        else:
            numero, suffisso = codice[:4], codice[4:]
            # Le lettere hanno significato solo per H350i e H360/H361 (F, D, f, d):
            # negli altri casi sono testo attaccato al codice (es. "H318Danni").
            if numero == "H350" and suffisso == "i":
                codice = "H350i"
            elif numero in ("H360", "H361") and suffisso:
                codice = numero + suffisso
            else:
                codice = numero
            visti.setdefault(codice, None)
    return list(visti)


def base(codice: str) -> str:
    """Codice senza le lettere delle varianti (H360FD -> H360), salvo H350i che è una frase propria."""
    if codice == "H350i" or codice.startswith("EUH"):
        return codice
    return codice[:4]


def descrizione(codice: str) -> str:
    return FRASI_H.get(codice) or FRASI_H.get(base(codice), "Indicazione di pericolo da verificare sulla scheda "
                                                           "di dati di sicurezza")


def pittogrammi(codici: list[str]) -> list[str]:
    """Pittogrammi GHS richiesti dai codici, con le regole di precedenza del CLP (art. 26)."""
    basi = {base(c) for c in codici}
    risultato = {_PITTOGRAMMA_DA_CODICE[b] for b in basi if b in _PITTOGRAMMA_DA_CODICE}
    if "H350i" in codici:
        risultato.add("GHS08")
    if "GHS07" in risultato:
        da_ghs07 = {b for b in basi if _PITTOGRAMMA_DA_CODICE.get(b) == "GHS07"}
        if "GHS06" in risultato:
            da_ghs07 = set()
        if "GHS05" in risultato:
            da_ghs07 -= {"H315", "H319"}
        if "H334" in basi:
            da_ghs07 -= {"H315", "H317", "H319"}
        if not da_ghs07:
            risultato.discard("GHS07")
    return sorted(risultato)


@dataclass(frozen=True)
class Categoria:
    nome: str
    grave: bool  # richiede attenzione prioritaria
    misure: tuple[str, ...]


def _ha(codici: list[str], *cercati: str) -> bool:
    basi = {base(c) for c in codici} | set(codici)
    return any(c in basi for c in cercati)


def categorie(codici: list[str]) -> list[Categoria]:
    """Categorie di pericolo rilevanti per la valutazione, dalla più grave."""
    if not codici:
        return []
    risultato: list[Categoria] = []
    if _ha(codici, "H340", "H350", "H350i"):
        risultato.append(Categoria("Cancerogeno o mutageno", True, (
            "Applicare il Titolo IX, Capo II, del D.Lgs. 81/2008: sostituzione con prodotti meno pericolosi "
            "se tecnicamente possibile, sistemi chiusi, riduzione al minimo degli esposti.",
            "Registro di esposizione e sorveglianza sanitaria dei lavoratori esposti.",
        )))
    if _ha(codici, "H360", "H362"):
        risultato.append(Categoria("Tossico per la riproduzione", True, (
            "Valutazione specifica dell'esposizione; tutela delle lavoratrici in gravidanza e in allattamento "
            "(D.Lgs. 151/2001).",
            "Valutare la sostituzione del prodotto.",
        )))
    if _ha(codici, "H300", "H301", "H310", "H311", "H330", "H331", "H370", "H372"):
        risultato.append(Categoria("Tossicità elevata (acuta o per organi bersaglio)", True, (
            "Ridurre al minimo quantità e tempi di esposizione; aerazione o aspirazione localizzata.",
            "DPI adeguati alla via di esposizione indicata nella sezione 8 della scheda.",
        )))
    if _ha(codici, "H341", "H351", "H361"):
        risultato.append(Categoria("Sospetto cancerogeno, mutageno o tossico per la riproduzione", False, (
            "Ridurre al minimo l'esposizione e valutarne con attenzione l'entità.",
        )))
    if _ha(codici, "H317", "H334", "EUH204", "EUH208"):
        risultato.append(Categoria("Sensibilizzante", False, (
            "Evitare il contatto cutaneo e l'inalazione; guanti idonei al prodotto.",
            "Sorveglianza sanitaria dei lavoratori esposti; attenzione ai lavoratori già sensibilizzati.",
        )))
    if _ha(codici, "H314", "H318"):
        risultato.append(Categoria("Corrosivo", False, (
            "Occhiali a tenuta o visiera, guanti e indumenti resistenti al prodotto.",
            "Acqua per il lavaggio di occhi e pelle disponibile vicino al punto di utilizzo.",
        )))
    if _ha(codici, "H302", "H312", "H315", "H319", "H332", "H335", "H336", "H371", "H373", "H304", "EUH066"):
        risultato.append(Categoria("Nocivo o irritante", False, (
            "Evitare il contatto con pelle e occhi; lavarsi le mani dopo l'uso; non mangiare né bere durante l'uso.",
            "Garantire la ventilazione dei locali.",
        )))
    if _ha(codici, "H200", "H201", "H202", "H203", "H204", "H205", "H240", "H241", "H270", "H271", "H272"):
        risultato.append(Categoria("Esplosivo o comburente", True, (
            "Conservare lontano da fonti di calore e da materiali combustibili; quantità minime in cantiere.",
        )))
    if _ha(codici, "H220", "H221", "H222", "H223", "H224", "H225", "H226", "H228", "H229", "H242", "H250",
           "H251", "H252", "H260", "H261", "H280"):
        risultato.append(Categoria("Infiammabile o sotto pressione", False, (
            "Stoccaggio in area ventilata, lontano da fiamme libere e lavorazioni a caldo; divieto di fumo.",
            "Estintore adeguato vicino al deposito; considerare il prodotto nella valutazione del rischio incendio.",
        )))
    if _ha(codici, "H400", "H410", "H411", "H412", "H413"):
        risultato.append(Categoria("Pericoloso per l'ambiente", False, (
            "Evitare dispersioni nel terreno e negli scarichi; materiale assorbente per gli sversamenti; "
            "smaltire residui e contenitori come rifiuti pericolosi.",
        )))
    return sorted(risultato, key=lambda c: not c.grave)


def elenco_codici(testo: str) -> str:
    """Codici in forma normalizzata per il salvataggio ('H315, H317, H318')."""
    return ", ".join(codici_h(testo))
