"""Strutture comuni ai metodi di valutazione dei rischi specifici."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

VERDE, GIALLO, ROSSO, VIOLA = "verde", "giallo", "rosso", "viola"
COLORI = {VERDE: "#27AE60", GIALLO: "#E6A23C", ROSSO: "#D93B30", VIOLA: "#7D3C98"}


@dataclass(frozen=True)
class Campo:
    chiave: str
    etichetta: str
    tipo: str = "numero"  # numero | scelta | testo
    minimo: float = 0
    massimo: float = 1000
    decimali: int = 0
    suffisso: str = ""
    scelte: tuple[tuple[str, str], ...] = ()
    predefinito: Any = 0
    aiuto: str = ""


@dataclass(frozen=True)
class Esito:
    indice: float | None
    indice_testo: str
    classe: str
    colore: str  # VERDE, GIALLO, ROSSO, VIOLA
    dettagli: list[tuple[str, str]] = field(default_factory=list)
    intestazioni_compiti: list[str] = field(default_factory=list)
    righe_compiti: list[list[str]] = field(default_factory=list)
    misure: list[str] = field(default_factory=list)
    note: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Metodo:
    chiave: str
    nome: str
    norma: str
    descrizione: str
    campi: tuple[Campo, ...]
    colonne_compiti: tuple[Campo, ...] = ()
    min_compiti: int = 0
    calcola: Callable[[dict[str, Any]], Esito] | None = None

    def dati_predefiniti(self) -> dict[str, Any]:
        dati: dict[str, Any] = {c.chiave: c.predefinito for c in self.campi}
        if self.colonne_compiti:
            dati["compiti"] = [self.compito_predefinito() for _ in range(max(self.min_compiti, 1))]
        return dati

    def compito_predefinito(self) -> dict[str, Any]:
        return {c.chiave: c.predefinito for c in self.colonne_compiti}

    def normalizza(self, dati: dict[str, Any]) -> dict[str, Any]:
        """Completa i dati mancanti con i valori predefiniti e riporta i numeri nei limiti."""
        risultato = {c.chiave: _valore(c, dati.get(c.chiave)) for c in self.campi}
        if self.colonne_compiti:
            compiti = dati.get("compiti")
            if not isinstance(compiti, list):
                # Dati di un altro metodo o valutazione nuova: compiti di esempio.
                compiti = self.dati_predefiniti()["compiti"]
            risultato["compiti"] = [
                {c.chiave: _valore(c, compito.get(c.chiave)) for c in self.colonne_compiti}
                for compito in compiti
                if isinstance(compito, dict)
            ]
        return risultato

    def esegui(self, dati: dict[str, Any]) -> Esito:
        assert self.calcola is not None
        return self.calcola(self.normalizza(dati))


def _valore(campo: Campo, valore: Any) -> Any:
    if campo.tipo == "numero":
        try:
            numero = float(valore)
        except (TypeError, ValueError):
            numero = float(campo.predefinito)
        return min(max(numero, campo.minimo), campo.massimo)
    if campo.tipo == "scelta":
        validi = [v for v, _ in campo.scelte]
        return valore if valore in validi else campo.predefinito
    return "" if valore is None else str(valore)


def interpola(tabella: list[tuple[float, float]], x: float) -> float:
    """Interpolazione lineare su una tabella (x crescente); fuori intervallo: valori estremi."""
    if x <= tabella[0][0]:
        return tabella[0][1]
    for (x0, y0), (x1, y1) in zip(tabella, tabella[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tabella[-1][1]


def numero_it(valore: float, decimali: int = 2) -> str:
    return f"{valore:.{decimali}f}".replace(".", ",")
