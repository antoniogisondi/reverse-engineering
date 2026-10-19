"""Esposizione a vibrazioni meccaniche (Titolo VIII, Capo III del D.Lgs. 81/2008, artt. 199-205).

Esposizione giornaliera normalizzata a 8 ore:
    A(8) = radice( somma ai^2 x Ti / 480 min )
con ai accelerazione ponderata in frequenza dell'attrezzatura o del mezzo:
- sistema mano-braccio (HAV): valore totale ahv; valore d'azione 2,5 m/s^2, limite 5 m/s^2
  (20 m/s^2 su periodi brevi);
- corpo intero (WBV): valore dell'asse dominante (1,4 awx, 1,4 awy, awz); valore d'azione
  0,5 m/s^2, limite 1,0 m/s^2 (1,5 m/s^2 su periodi brevi).
"""

from __future__ import annotations

import math
from typing import Any

from sicurcantiere.valutazioni.base import GIALLO, ROSSO, VERDE, VIOLA, Campo, Esito, Metodo, numero_it

T0 = 480.0
# sistema -> (valore d'azione, valore limite, limite su periodi brevi)
SOGLIE = {"hav": (2.5, 5.0, 20.0), "wbv": (0.5, 1.0, 1.5)}
SCELTE_SISTEMA = (("hav", "Sistema mano-braccio (HAV)"), ("wbv", "Corpo intero (WBV)"))


def a8(compiti: list[dict[str, Any]]) -> float:
    return math.sqrt(sum(c["accelerazione"] ** 2 * c["durata"] / T0 for c in compiti if c["durata"] > 0))


def classe(valore: float, sistema: str) -> tuple[str, str]:
    azione, limite, _ = SOGLIE[sistema]
    if valore > limite:
        return "Superato il valore limite di esposizione", VIOLA
    if valore > azione:
        return "Superiore al valore d'azione", ROSSO
    if valore > azione * 0.8:
        return "Inferiore al valore d'azione, ma vicino", GIALLO
    return "Inferiore al valore d'azione", VERDE


MISURE_COMUNI = {
    VERDE: ["Nessun obbligo specifico oltre alla valutazione; ripeterla se cambiano attrezzature o tempi."],
    GIALLO: ["Esposizione vicina al valore d'azione: mantenere manutenzione delle attrezzature e "
             "controllo dei tempi di utilizzo; informare i lavoratori (art. 184)."],
    ROSSO: [
        "Programma di misure tecniche e organizzative per ridurre l'esposizione (art. 203 c. 1).",
        "Sorveglianza sanitaria dei lavoratori esposti (art. 204).",
        "Informazione e formazione sui rischi delle vibrazioni e sull'uso corretto delle attrezzature (art. 184).",
    ],
    VIOLA: [
        "Misure immediate per riportare l'esposizione al di sotto del valore limite; individuarne le cause "
        "e adeguare le misure (art. 203 c. 2).",
        "Sorveglianza sanitaria dei lavoratori esposti (art. 204).",
    ],
}
MISURE_SISTEMA = {
    "hav": [
        "Utensili a bassa emissione di vibrazioni, impugnature antivibranti, manutenzione di utensili e inserti.",
        "Rotazione tra gli addetti e pause per limitare il tempo di impugnatura; guanti antivibrazione "
        "certificati (UNI EN ISO 10819) e mani mantenute calde.",
    ],
    "wbv": [
        "Sedili ammortizzati e regolati sul peso del conducente; manutenzione delle sospensioni del mezzo.",
        "Percorsi di cantiere livellati, velocità moderata, rotazione dei conducenti.",
    ],
}


def calcola(dati: dict[str, Any]) -> Esito:
    sistema = dati["sistema"]
    compiti = [c for c in dati["compiti"] if c["durata"] > 0]
    if not compiti:
        return Esito(None, "-", "Dati insufficienti", GIALLO, note=["Inserire almeno un'attrezzatura con la durata."])
    azione, limite, limite_breve = SOGLIE[sistema]
    valore = a8(compiti)
    nome, colore = classe(valore, sistema)

    totale = sum(c["accelerazione"] ** 2 * c["durata"] for c in compiti)
    righe = []
    contributi = []
    for c in compiti:
        parziale = math.sqrt(c["accelerazione"] ** 2 * c["durata"] / T0)
        quota = c["accelerazione"] ** 2 * c["durata"] / totale * 100 if totale else 0
        contributi.append((quota, c))
        # Tempo che da solo porterebbe al valore d'azione (in minuti).
        tempo_azione = T0 * (azione / c["accelerazione"]) ** 2 if c["accelerazione"] > 0 else 0
        righe.append([c["nome"] or "Attrezzatura", numero_it(c["accelerazione"], 1), numero_it(c["durata"], 0),
                      numero_it(parziale, 2), numero_it(quota, 0) + "%", numero_it(min(tempo_azione, 9999), 0)])
    contributi.sort(key=lambda x: x[0], reverse=True)

    dettagli = [
        ("Sistema", dict(SCELTE_SISTEMA)[sistema]),
        ("Esposizione giornaliera A(8)", f"{numero_it(valore, 2)} m/s²"),
        ("Valore d'azione", f"{numero_it(azione, 1)} m/s²"),
        ("Valore limite", f"{numero_it(limite, 1)} m/s²"),
        ("Attrezzatura con il contributo maggiore", f"{contributi[0][1]['nome'] or 'Attrezzatura'} "
                                                    f"({numero_it(contributi[0][0], 0)}%)"),
    ]
    note = []
    brevi = [c["nome"] or "Attrezzatura" for c in compiti if c["accelerazione"] > limite_breve]
    if brevi:
        note.append(f"Accelerazione oltre il limite per periodi brevi ({numero_it(limite_breve, 1)} m/s²): "
                    + ", ".join(brevi) + ".")
    misure = list(MISURE_COMUNI[colore])
    if colore in (ROSSO, VIOLA, GIALLO):
        misure.insert(0, f"Intervenire prima su «{contributi[0][1]['nome'] or 'Attrezzatura'}», che determina il "
                         f"{numero_it(contributi[0][0], 0)}% dell'esposizione; l'ultima colonna della tabella "
                         "indica i minuti di utilizzo che da soli porterebbero al valore d'azione.")
        misure += MISURE_SISTEMA[sistema]
    return Esito(valore, f"{numero_it(valore, 2)} m/s²", nome, colore, dettagli,
                 ["Attrezzatura / mezzo", "a m/s²", "Durata min", "A(8) parziale", "Contributo",
                  "Minuti al valore d'azione"], righe, misure, note)


VIBRAZIONI = Metodo(
    chiave="vibrazioni",
    nome="Esposizione a vibrazioni (mano-braccio o corpo intero)",
    norma="D.Lgs. 81/2008, Titolo VIII Capo III - UNI EN ISO 5349, UNI ISO 2631",
    descrizione=(
        "L'esposizione giornaliera A(8) si calcola dalle accelerazioni ponderate delle attrezzature "
        "(sistema mano-braccio) o dei mezzi (corpo intero) e dai rispettivi tempi di effettiva "
        "esposizione, riferiti a 8 ore. Il risultato si confronta con i valori dell'art. 201 del "
        "D.Lgs. 81/2008: per il sistema mano-braccio valore d'azione 2,5 m/s² e valore limite 5 m/s²; "
        "per il corpo intero valore d'azione 0,5 m/s² e valore limite 1,0 m/s². Le accelerazioni "
        "derivano da misure, dalle dichiarazioni del fabbricante o da banche dati riconosciute."
    ),
    campi=(
        Campo("sistema", "Tipo di esposizione", "scelta", scelte=SCELTE_SISTEMA, predefinito="hav"),
    ),
    colonne_compiti=(
        Campo("nome", "Attrezzatura / mezzo", "testo", predefinito=""),
        Campo("accelerazione", "Accelerazione", minimo=0, massimo=50, decimali=1, suffisso=" m/s²",
              predefinito=5, aiuto="ahv per il mano-braccio; asse dominante per il corpo intero."),
        Campo("durata", "Esposizione effettiva", minimo=0, massimo=720, suffisso=" min", predefinito=60,
              aiuto="Tempo in cui l'utensile è effettivamente in funzione, non la durata del compito."),
    ),
    min_compiti=1,
    calcola=calcola,
)
