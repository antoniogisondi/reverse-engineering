"""Valutazioni dei rischi specifici con metodi normati."""

from sicurcantiere.valutazioni.base import COLORI, Campo, Esito, Metodo
from sicurcantiere.valutazioni.niosh import NIOSH_COMPOSTO, NIOSH_SEMPLICE
from sicurcantiere.valutazioni.ocra import OCRA

METODI: dict[str, Metodo] = {m.chiave: m for m in (NIOSH_SEMPLICE, NIOSH_COMPOSTO, OCRA)}

__all__ = ["COLORI", "Campo", "Esito", "METODI", "Metodo"]
