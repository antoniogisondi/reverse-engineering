"""Elenco ordinato delle pagine mostrate nella barra laterale."""

from __future__ import annotations

from sicurcantiere.ui.pagine import (
    Pagina,
    PaginaCosti,
    PaginaDatiGenerali,
    PaginaDocumenti,
    PaginaFascicolo,
    PaginaFasi,
    PaginaImprese,
    PaginaInterferenze,
    PaginaRelazione,
    PaginaSoggetti,
)
from sicurcantiere.ui.ponteggi import PaginaPonteggi
from sicurcantiere.ui.valutazioni import PaginaValutazioni

PAGINE: list[type[Pagina]] = [
    PaginaDatiGenerali,
    PaginaSoggetti,
    PaginaImprese,
    PaginaFasi,
    PaginaInterferenze,
    PaginaValutazioni,
    PaginaPonteggi,
    PaginaCosti,
    PaginaRelazione,
    PaginaFascicolo,
    PaginaDocumenti,
]
