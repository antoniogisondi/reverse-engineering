"""Diagramma di Gantt del cronoprogramma come immagine per i documenti (PSC).

Stesso aspetto del Gantt del programma: una riga per fase raggruppata per lavorazione, barre colorate per
impresa, periodi di interferenza in rosso, fine settimana in grigio; sotto, l'affollamento (lavoratori
presenti) e la pericolosità (rischio massimo) giorno per giorno, poi la legenda delle imprese. Con molte
fasi il diagramma si divide in più pagine con la stessa scala dei tempi.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sicurcantiere import analisi
from sicurcantiere.documenti.immagini import applicazione as _applicazione
from sicurcantiere.documenti.immagini import png

DPI = 220
LARGHEZZA_CM = 26.0  # A4 orizzontale con margini di 1,8 cm
RIGHE_PER_PAGINA = 20
MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]


def _px(cm: float) -> int:
    return round(cm / 2.54 * DPI)


def _righe(fasi: list[dict[str, Any]]) -> list[tuple[str, dict[str, Any] | None]]:
    """Righe del diagramma: intestazione di ogni lavorazione, poi le sue fasi."""
    righe: list[tuple[str, dict[str, Any] | None]] = []
    corrente = object()
    for f in fasi:
        if f.get("lavorazione") and f["lavorazione"] != corrente:
            righe.append((f["lavorazione"], None))
        corrente = f.get("lavorazione")
        righe.append((f"{f['codice']} {f['descrizione']}".strip(), f))
    return righe


def immagini(fasi: list[dict[str, Any]], imprese: dict[int, str], livelli: dict[int, int]) -> list[bytes]:
    """PNG del diagramma, una per pagina; nessuna immagine se mancano le date."""
    periodo = analisi.periodo_lavori(fasi)
    if not periodo:
        return []
    _applicazione()
    righe = _righe(fasi)
    pagine = [righe[i:i + RIGHE_PER_PAGINA] for i in range(0, len(righe), RIGHE_PER_PAGINA)] or [[]]
    contesto = {
        "periodo": periodo,
        "imprese": imprese,
        "interferenze": analisi.interferenze(fasi, livelli),
        "giornate": analisi.andamento(fasi, livelli),
        "fasi": fasi,
    }
    return [_disegna(pagina, contesto, n + 1, len(pagine)) for n, pagina in enumerate(pagine)]


def _disegna(righe: list[tuple[str, dict[str, Any] | None]], ctx: dict[str, Any], pagina: int, totale: int) -> bytes:
    from PySide6.QtCore import QPointF, QRectF, Qt
    from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen

    from sicurcantiere.ui.gantt import (
        COLORE_AFFOLLAMENTO,
        COLORE_INTERFERENZA,
        COLORE_SENZA_IMPRESA,
        COLORI_IMPRESE,
        colore_livello,
    )

    inizio, fine = ctx["periodo"]
    origine = inizio - timedelta(days=inizio.weekday())
    giorni = (fine - origine).days + 1
    giorni += (7 - giorni % 7) % 7  # fino alla domenica

    larghezza = _px(LARGHEZZA_CM)
    etichette, colonna_zona, colonna_data, colonna_gg = _px(5.4), _px(1.15), _px(1.55), _px(0.95)
    x_date = etichette + colonna_zona
    x0 = x_date + 2 * colonna_data + colonna_gg
    passo = (larghezza - x0 - _px(0.1)) / giorni
    riga_h, testa_h, grafico_h = _px(0.52), _px(0.95), _px(1.05)
    legenda_h = _px(0.9)
    altezza = testa_h + max(len(righe), 1) * riga_h + _px(0.25) + 2 * (grafico_h + _px(0.15)) + legenda_h

    immagine = QImage(larghezza, altezza, QImage.Format.Format_ARGB32)
    immagine.setDotsPerMeterX(round(DPI / 0.0254))
    immagine.setDotsPerMeterY(round(DPI / 0.0254))
    immagine.fill(QColor("#FFFFFF"))
    p = QPainter(immagine)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    def carattere(punti: float, grassetto: bool = False) -> QFont:
        f = QFont("Ubuntu")
        f.setStyleHint(QFont.StyleHint.SansSerif)
        f.setPixelSize(max(1, round(punti / 72 * DPI)))
        f.setBold(grassetto)
        return f

    inchiostro, testo2, testo3 = QColor("#17202A"), QColor("#45515E"), QColor("#6B7785")
    linea, linea_forte, tinta = QColor("#D7DDE3"), QColor("#B9C3CD"), QColor("#FDEEE2")
    accento = QColor("#A44C0C")
    fine_settimana = QColor("#F2F4F6")
    ordine_imprese = sorted(ctx["imprese"])

    def colore_impresa(impresa_id):
        if not impresa_id:
            return COLORE_SENZA_IMPRESA
        indice = ordine_imprese.index(impresa_id) if impresa_id in ordine_imprese else impresa_id
        return COLORI_IMPRESE[indice % len(COLORI_IMPRESE)]

    def x(giorno: date) -> float:
        return x0 + (giorno - origine).days * passo

    fondo_righe = testa_h + max(len(righe), 1) * riga_h

    # --- intestazione: colonne, mesi e settimane ---
    p.fillRect(QRectF(0, 0, larghezza, testa_h), tinta)
    p.setFont(carattere(6.5, True))
    p.setPen(accento)
    centro = Qt.AlignmentFlag.AlignCenter
    sinistra = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    p.drawText(QRectF(_px(0.15), 0, etichette, testa_h), sinistra,
               "Lavorazione / fase" + (f"   (pagina {pagina} di {totale})" if totale > 1 else ""))
    p.drawText(QRectF(etichette, 0, colonna_zona, testa_h), centro, "Zona")
    for i, titolo in enumerate(("Inizio", "Fine")):
        p.drawText(QRectF(x_date + i * colonna_data, 0, colonna_data, testa_h), centro, titolo)
    p.drawText(QRectF(x_date + 2 * colonna_data, 0, colonna_gg, testa_h), centro, "gg lav.")
    meta = testa_h / 2
    for g in range(giorni):
        giorno = origine + timedelta(days=g)
        xg = x(giorno)
        if giorno.weekday() >= 5 and passo >= _px(0.08):
            p.fillRect(QRectF(xg, testa_h, passo, fondo_righe - testa_h), fine_settimana)
        if giorno.day == 1 or g == 0:
            p.setPen(QPen(linea_forte, 2))
            p.drawLine(QPointF(xg, 0), QPointF(xg, fondo_righe))
            p.setPen(accento)
            p.setFont(carattere(6.5, True))
            p.drawText(QRectF(xg + _px(0.06), 0, _px(3), meta), sinistra, f"{MESI[giorno.month - 1]} {giorno.year}")
        if giorno.weekday() == 0:
            p.setPen(QPen(linea, 1))
            p.drawLine(QPointF(xg, meta), QPointF(xg, fondo_righe))
            if 7 * passo >= _px(0.75):
                p.setPen(testo3)
                p.setFont(carattere(5.5))
                p.drawText(QRectF(xg + _px(0.04), meta, 7 * passo, meta), sinistra, giorno.strftime("%d/%m"))
    p.setPen(QPen(accento, 3))
    p.drawLine(QPointF(0, 0), QPointF(larghezza, 0))
    p.setPen(QPen(linea_forte, 2))
    p.drawLine(QPointF(0, testa_h), QPointF(larghezza, testa_h))

    # --- righe ---
    periodi_interferenza: dict[int, list[tuple[date, date]]] = {}
    for i in ctx["interferenze"]:
        for f in (i.fase_a, i.fase_b):
            periodi_interferenza.setdefault(f["id"], []).append((i.inizio, i.fine))
    for r, (etichetta, f) in enumerate(righe):
        y = testa_h + r * riga_h
        rett = QRectF(_px(0.15), y, etichette - _px(0.25), riga_h)
        if f is None:  # intestazione della lavorazione
            p.fillRect(QRectF(0, y, x0, riga_h), QColor("#F4F6F8"))
            p.setFont(carattere(6.5, True))
            p.setPen(inchiostro)
            p.drawText(rett, sinistra, p.fontMetrics().elidedText(etichetta, Qt.TextElideMode.ElideRight,
                                                                   int(rett.width())))
        else:
            p.setFont(carattere(6.3))
            p.setPen(inchiostro)
            rientro = QRectF(rett.x() + _px(0.25), y, rett.width() - _px(0.25), riga_h)
            p.drawText(rientro, sinistra, p.fontMetrics().elidedText(etichetta, Qt.TextElideMode.ElideRight,
                                                                      int(rientro.width())))
            da, a = analisi.data(f["data_inizio"]), analisi.data(f["data_fine"])
            p.setFont(carattere(6))
            p.setPen(testo2)
            zona = str(f.get("zona") or "")
            p.drawText(QRectF(etichette, y, colonna_zona, riga_h), centro,
                       p.fontMetrics().elidedText(zona, Qt.TextElideMode.ElideRight, colonna_zona - _px(0.1)))
            for i, d in enumerate((da, a)):
                p.drawText(QRectF(x_date + i * colonna_data, y, colonna_data, riga_h), centro,
                           d.strftime("%d/%m/%y") if d else "—")
            if da and a and a >= da:
                p.drawText(QRectF(x_date + 2 * colonna_data, y, colonna_gg, riga_h), centro,
                           str(analisi.giorni_lavorativi(da, a)))
                barra = QRectF(x(da), y + riga_h * 0.22, ((a - da).days + 1) * passo, riga_h * 0.56)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(colore_impresa(f.get("impresa_id")))
                p.drawRoundedRect(barra, _px(0.05), _px(0.05))
                for i_da, i_a in periodi_interferenza.get(f["id"], []):
                    zona = QRectF(x(i_da), barra.y() - _px(0.03), ((i_a - i_da).days + 1) * passo,
                                  barra.height() + _px(0.06))
                    rosso = QColor(COLORE_INTERFERENZA)
                    rosso.setAlpha(110)
                    p.setBrush(rosso)
                    p.setPen(QPen(COLORE_INTERFERENZA, 3))
                    p.drawRoundedRect(zona, _px(0.04), _px(0.04))
        p.setPen(QPen(linea, 1))
        p.drawLine(QPointF(0, y + riga_h), QPointF(larghezza, y + riga_h))
    p.setPen(QPen(linea_forte, 2))
    for xc in (etichette, x_date, x_date + colonna_data, x_date + 2 * colonna_data, x0):
        p.drawLine(QPointF(xc, 0), QPointF(xc, fondo_righe))

    # --- affollamento e pericolosità ---
    giornate = ctx["giornate"]
    massimo = max((g.lavoratori for g in giornate), default=0)
    y_graf = fondo_righe + _px(0.25)
    for n, titolo in enumerate((f"Affollamento: lavoratori presenti (massimo {massimo})",
                                "Pericolosità: rischio massimo P × D del giorno")):
        y = y_graf + n * (grafico_h + _px(0.15))
        p.setPen(QPen(linea_forte, 2))
        p.drawLine(QPointF(x0, y + grafico_h), QPointF(larghezza, y + grafico_h))
        p.setPen(QPen(linea, 1))
        p.drawLine(QPointF(x0, y), QPointF(larghezza, y))
        p.setFont(carattere(6, True))
        p.setPen(testo2)
        p.drawText(QRectF(_px(0.15), y, x0 - _px(0.3), grafico_h),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap, titolo)
        p.setPen(Qt.PenStyle.NoPen)
        for g in giornate:
            if n == 0 and massimo:
                h = (grafico_h - _px(0.1)) * g.lavoratori / massimo
                p.setBrush(COLORE_AFFOLLAMENTO)
            elif n == 1 and g.pericolosita:
                h = (grafico_h - _px(0.1)) * g.pericolosita / 16
                p.setBrush(colore_livello(g.pericolosita))
            else:
                continue
            p.drawRect(QRectF(x(g.giorno), y + grafico_h - h, max(passo, 1.0), h))

    # --- legenda ---
    y = altezza - legenda_h + _px(0.25)
    xl = float(_px(0.15))
    p.setFont(carattere(6.5))
    metriche = p.fontMetrics()
    voci = []
    usate = {f.get("impresa_id") for _, f in righe if f is not None}
    for impresa_id in ordine_imprese:
        if impresa_id in usate:
            voci.append((ctx["imprese"].get(impresa_id) or f"Impresa {impresa_id}", colore_impresa(impresa_id), False))
    if any(not i for i in usate):
        voci.append(("Impresa da definire", COLORE_SENZA_IMPRESA, False))
    voci.append(("Interferenza tra imprese", COLORE_INTERFERENZA, True))
    for nome, colore, interferenza in voci:
        campione = QRectF(xl, y, _px(0.6), _px(0.3))
        if interferenza:
            rosso = QColor(colore)
            rosso.setAlpha(110)
            p.setBrush(rosso)
            p.setPen(QPen(colore, 3))
        else:
            p.setBrush(colore)
            p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(campione, _px(0.05), _px(0.05))
        p.setPen(inchiostro)
        p.drawText(QPointF(xl + _px(0.75), y + _px(0.26)), nome)
        xl += _px(0.75) + metriche.horizontalAdvance(nome) + _px(0.5)
        if xl > larghezza - _px(4):
            break
    p.end()
    return png(immagine)
