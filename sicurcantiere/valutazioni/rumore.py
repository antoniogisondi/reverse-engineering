"""Esposizione al rumore (Titolo VIII, Capo II del D.Lgs. 81/2008, artt. 187-198).

Livello di esposizione giornaliera:
    LEX,8h = 10 log10( somma (Ti / 480 min) 10^(LAeq,i / 10) )
confrontato con i valori dell'art. 189:
    inferiori di azione  80 dB(A)  e 135 dB(C) di picco
    superiori di azione  85 dB(A)  e 137 dB(C)
    limite di esposizione 87 dB(A) e 140 dB(C), tenendo conto dell'attenuazione dei DPI.

L'attenuazione dei protettori auricolari è stimata con il metodo semplificato
SNR della UNI EN 458 per livelli misurati in dB(A): L'A = LA - (SNR - 7).
"""

from __future__ import annotations

import math
from typing import Any

from sicurcantiere.valutazioni.base import GIALLO, ROSSO, VERDE, VIOLA, Campo, Esito, Metodo, numero_it

T0 = 480.0  # minuti in 8 ore
INFERIORE, SUPERIORE, LIMITE = 80.0, 85.0, 87.0
PICCO_INFERIORE, PICCO_SUPERIORE, PICCO_LIMITE = 135.0, 137.0, 140.0
CORREZIONE_SNR = 7.0


def lex(compiti: list[dict[str, Any]], attenuazione: float = 0.0) -> float:
    """LEX,8h in dB(A); con attenuazione si ottiene il livello effettivo con i DPI."""
    energia = sum(c["durata"] / T0 * 10 ** ((c["laeq"] - attenuazione) / 10) for c in compiti if c["durata"] > 0)
    return 10 * math.log10(energia) if energia > 0 else 0.0


def classe(livello: float, picco: float) -> tuple[str, str]:
    if livello > LIMITE or picco > PICCO_LIMITE:
        return "Superato il valore limite di esposizione", VIOLA
    if livello > SUPERIORE or picco > PICCO_SUPERIORE:
        return "Superiore al valore superiore di azione", ROSSO
    if livello > INFERIORE or picco > PICCO_INFERIORE:
        return "Tra il valore inferiore e il valore superiore di azione", GIALLO
    return "Inferiore al valore inferiore di azione", VERDE


MISURE = {
    VERDE: [
        "Nessun obbligo specifico oltre alla valutazione; ripeterla se cambiano attrezzature o tempi (art. 190).",
    ],
    GIALLO: [
        "Mettere a disposizione dei lavoratori i protettori auricolari (art. 193 c. 1 lett. a).",
        "Informazione e formazione sui rischi del rumore e sull'uso dei DPI uditivi (art. 195).",
        "Sorveglianza sanitaria su richiesta del lavoratore o se il medico competente ne conferma "
        "l'opportunità (art. 196 c. 2).",
    ],
    ROSSO: [
        "Programma di misure tecniche e organizzative per ridurre l'esposizione (art. 192 c. 2).",
        "Segnalare e delimitare le aree con rumore oltre il valore superiore di azione (art. 192 c. 3).",
        "Uso obbligatorio dei protettori auricolari, con verifica dell'efficacia (art. 193 c. 1 lett. c e d).",
        "Sorveglianza sanitaria dei lavoratori esposti (art. 196 c. 1); informazione e formazione (art. 195).",
    ],
    VIOLA: [
        "Misure immediate per riportare l'esposizione al di sotto del valore limite; individuarne le cause "
        "e adeguare le misure di protezione (art. 194).",
        "Verificare la scelta dei protettori auricolari: l'attenuazione stimata non è sufficiente.",
        "Sorveglianza sanitaria dei lavoratori esposti (art. 196 c. 1).",
    ],
}


def calcola(dati: dict[str, Any]) -> Esito:
    compiti = [c for c in dati["compiti"] if c["durata"] > 0]
    if not compiti:
        return Esito(None, "-", "Dati insufficienti", GIALLO, note=["Inserire almeno un'attività con la durata."])
    attenuazione = max(dati["snr"] - CORREZIONE_SNR, 0.0) if dati["snr"] > 0 else 0.0
    livello = lex(compiti)
    picco = max(c["picco"] for c in compiti)
    protetto = lex(compiti, attenuazione)
    picco_protetto = picco - attenuazione

    # Classe per gli obblighi: livelli senza DPI; per il valore limite contano i DPI (art. 189 c. 2).
    nome, colore = classe(livello, picco)
    if colore == VIOLA and attenuazione and protetto <= LIMITE and picco_protetto <= PICCO_LIMITE:
        nome, colore = "Superiore al valore superiore di azione (limite rispettato con i DPI)", ROSSO

    energia_totale = sum(c["durata"] / T0 * 10 ** (c["laeq"] / 10) for c in compiti)
    righe = []
    contributi = []
    for c in compiti:
        energia = c["durata"] / T0 * 10 ** (c["laeq"] / 10)
        quota = energia / energia_totale * 100 if energia_totale else 0
        contributi.append((quota, c))
        righe.append([c["nome"] or "Attività", numero_it(c["laeq"], 1), numero_it(c["picco"], 0),
                      numero_it(c["durata"], 0), numero_it(quota, 0) + "%"])
    contributi.sort(key=lambda x: x[0], reverse=True)

    dettagli = [
        ("Durata complessiva delle attività", f"{numero_it(sum(c['durata'] for c in compiti), 0)} min"),
        ("Livello di esposizione giornaliera LEX,8h", f"{numero_it(livello, 1)} dB(A)"),
        ("Livello di picco massimo", f"{numero_it(picco, 0)} dB(C)"),
    ]
    if attenuazione:
        dettagli += [
            ("Attenuazione stimata dei DPI (SNR - 7)", f"{numero_it(attenuazione, 0)} dB"),
            ("LEX,8h effettivo con i DPI", f"{numero_it(protetto, 1)} dB(A)"),
        ]
    dettagli.append(("Attività con il contributo maggiore", f"{contributi[0][1]['nome'] or 'Attività'} "
                                                           f"({numero_it(contributi[0][0], 0)}%)"))

    misure = list(MISURE[colore])
    if colore != VERDE:
        misure.insert(0, f"Intervenire prima sull'attività «{contributi[0][1]['nome'] or 'Attività'}», che "
                         f"produce il {numero_it(contributi[0][0], 0)}% dell'energia sonora giornaliera: "
                         "attrezzature meno rumorose, manutenzione, schermature, riduzione dei tempi.")
    note = []
    if attenuazione:
        if protetto < 65:
            note.append("Livello con i DPI inferiore a 65 dB(A): possibile iperprotezione, che riduce la "
                        "percezione dei segnali di pericolo (UNI EN 458).")
        elif protetto <= 80:
            note.append("Protezione dei DPI adeguata: livello effettivo tra 65 e 80 dB(A) (UNI EN 458).")
        else:
            note.append("Protezione dei DPI insufficiente: livello effettivo oltre 80 dB(A).")
    return Esito(livello, f"{numero_it(livello, 1)} dB(A)", nome, colore, dettagli,
                 ["Attività", "LAeq dB(A)", "Picco dB(C)", "Durata min", "Contributo"], righe, misure, note)


RUMORE = Metodo(
    chiave="rumore",
    nome="Esposizione al rumore (LEX,8h)",
    norma="D.Lgs. 81/2008, Titolo VIII Capo II - UNI 9432",
    descrizione=(
        "Il livello di esposizione giornaliera al rumore LEX,8h si calcola sommando l'energia sonora "
        "delle attività svolte nel turno, ciascuna con il proprio livello equivalente LAeq e la propria "
        "durata, riferita a 8 ore. Il risultato si confronta con i valori dell'art. 189 del D.Lgs. "
        "81/2008: 80 dB(A) valore inferiore di azione, 85 dB(A) valore superiore di azione, 87 dB(A) "
        "valore limite, che si verifica tenendo conto dell'attenuazione dei protettori auricolari; per il "
        "picco rispettivamente 135, 137 e 140 dB(C). I livelli delle attività derivano da misure o da "
        "banche dati riconosciute."
    ),
    campi=(
        Campo("snr", "SNR dei protettori auricolari (0 se non usati)", minimo=0, massimo=40, suffisso=" dB",
              predefinito=0, aiuto="Valore SNR riportato sulla confezione o nella nota informativa del DPI."),
    ),
    colonne_compiti=(
        Campo("nome", "Attività / attrezzatura", "testo", predefinito=""),
        Campo("laeq", "LAeq", minimo=0, massimo=140, decimali=1, suffisso=" dB(A)", predefinito=85),
        Campo("picco", "Picco", minimo=0, massimo=160, suffisso=" dB(C)", predefinito=120),
        Campo("durata", "Durata nel turno", minimo=0, massimo=720, suffisso=" min", predefinito=120),
    ),
    min_compiti=1,
    calcola=calcola,
)
