"""Valutazioni dei rischi specifici con metodi normati."""

from sicurcantiere.valutazioni.base import COLORI, Campo, Esito, Metodo
from sicurcantiere.valutazioni.niosh import NIOSH_COMPOSTO, NIOSH_SEMPLICE
from sicurcantiere.valutazioni.ocra import OCRA
from sicurcantiere.valutazioni.rumore import RUMORE
from sicurcantiere.valutazioni.traino_spinta import TRAINO_SPINTA
from sicurcantiere.valutazioni.trasporto import TRASPORTO
from sicurcantiere.valutazioni.vibrazioni import VIBRAZIONI

METODI: dict[str, Metodo] = {m.chiave: m for m in (NIOSH_SEMPLICE, NIOSH_COMPOSTO, TRAINO_SPINTA, TRASPORTO, OCRA,
                                                  RUMORE, VIBRAZIONI)}

__all__ = ["COLORI", "Campo", "Esito", "METODI", "Metodo"]
