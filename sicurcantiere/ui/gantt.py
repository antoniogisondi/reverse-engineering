"""Diagramma di Gantt delle fasi con grafici di affollamento e pericolosità.

Le barre sono colorate per impresa; i periodi di interferenza sono
tratteggiati in rosso. Le barre si possono trascinare per spostare la fase
o, prendendole dal bordo destro, per cambiarne la durata.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QToolTip, QWidget

from sicurcantiere import analisi

ALTEZZA_RIGA = 40  # due righe: fase e impresa
ALTEZZA_INTESTAZIONE = 44  # mese, settimane e l'etichetta «oggi»
ALTEZZA_GRAFICO = 60
ALTEZZA_LEGENDA = 30
LARGHEZZA_ETICHETTE = 300
MARGINE_BORDO = 6  # pixel sensibili sul bordo destro della barra

ZOOM = {"Giorni": 18, "Settimane": 6, "Mesi": 2}
ZOOM_PREDEFINITO = "Settimane"
MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]

COLORI_IMPRESE = [QColor(c) for c in (
    "#3B6EA8", "#2E9C8F", "#7A5BA6", "#5E8C31", "#8C6239", "#C2558F", "#5C6F82", "#2F4F9E",
)]
COLORE_SENZA_IMPRESA = QColor("#9AA5B1")
COLORE_INTERFERENZA = QColor("#D93B30")
COLORE_OGGI = QColor("#E8792B")
COLORE_FINE_SETTIMANA = QColor(128, 128, 128, 30)
# Colori per classe di rischio: basso, medio, alto, molto alto.
COLORI_PERICOLOSITA = [(9, QColor("#C0392B")), (6, QColor("#E67E22")), (3, QColor("#F1C40F")),
                       (1, QColor("#27AE60"))]


def _colore_tema(chiave: str) -> QColor:
    from sicurcantiere.ui import tema

    return QColor(tema.correnti()[chiave])


def colore_livello(livello: int) -> QColor:
    for soglia, colore in COLORI_PERICOLOSITA:
        if livello >= soglia:
            return colore
    return QColor(0, 0, 0, 0)


class Gantt(QWidget):
    # id della fase, nuova data di inizio, nuova data di fine (ISO)
    fase_modificata = Signal(int, str, str)
    fase_cliccata = Signal(int)

    def __init__(self, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.fasi: list[dict[str, Any]] = []
        self.imprese: dict[int, str] = {}
        self.interferenze: list[analisi.Interferenza] = []
        self.giornate: list[analisi.Giornata] = []
        self.periodo: tuple[date, date] | None = None
        self.pixel_giorno = ZOOM[ZOOM_PREDEFINITO]
        self.oggi = date.today()
        self._trascinamento: dict[str, Any] | None = None
        self.selezionata: int | None = None
        self.setMouseTracking(True)
        self.setMinimumHeight(ALTEZZA_INTESTAZIONE + ALTEZZA_RIGA)

    # --- dati ---

    def imposta_fasi(self, fasi: list[dict[str, Any]], livelli: dict[int, int],
                     imprese: dict[int, str] | None = None) -> None:
        self.fasi = fasi
        self.imprese = imprese or {}
        self.periodo = analisi.periodo_lavori(fasi)
        self.interferenze = analisi.interferenze(fasi, livelli)
        self.giornate = analisi.andamento(fasi, livelli)
        self._ridimensiona()

    def seleziona(self, id_: int | None) -> None:
        if id_ != self.selezionata:
            self.selezionata = id_
            self.update()

    def imposta_zoom(self, nome: str) -> None:
        self.pixel_giorno = ZOOM[nome]
        self._ridimensiona()

    def _ridimensiona(self) -> None:
        self.updateGeometry()
        self.resize(self.sizeHint())
        self.update()

    def colore_impresa(self, impresa_id: int | None) -> QColor:
        if not impresa_id:
            return COLORE_SENZA_IMPRESA
        ordine = sorted(self.imprese)
        indice = ordine.index(impresa_id) if impresa_id in ordine else impresa_id
        # la prima impresa (di solito l'affidataria) nel colore del programma, le altre in colori distinti
        tavolozza = [_colore_tema("acc_s")] + [c for c in COLORI_IMPRESE if c.name().upper() != "#2E9C8F"]
        return tavolozza[indice % len(tavolozza)]

    # --- geometria ---

    def _origine(self) -> date:
        inizio = self.periodo[0]
        if self.pixel_giorno <= ZOOM["Mesi"]:
            return inizio.replace(day=1)
        return inizio - timedelta(days=inizio.weekday())

    def _giorni(self) -> int:
        if not self.periodo:
            return 0
        # Margine a destra per poter allungare le fasi trascinando.
        return (self.periodo[1] - self._origine()).days + 15

    def _x(self, giorno: date) -> float:
        return LARGHEZZA_ETICHETTE + (giorno - self._origine()).days * self.pixel_giorno

    def _y_righe(self) -> int:
        return ALTEZZA_INTESTAZIONE

    def _y_grafici(self) -> int:
        return ALTEZZA_INTESTAZIONE + max(len(self.fasi), 1) * ALTEZZA_RIGA + 6

    def _rett_barra(self, r: int, inizio: date, fine: date) -> QRectF:
        y = self._y_righe() + r * ALTEZZA_RIGA
        return QRectF(self._x(inizio), y + 10, ((fine - inizio).days + 1) * self.pixel_giorno,
                      ALTEZZA_RIGA - 20)

    def _date(self, f: dict[str, Any]) -> tuple[date | None, date | None]:
        if self._trascinamento and self._trascinamento["id"] == f["id"]:
            return self._trascinamento["anteprima"]
        return analisi.data(f["data_inizio"]), analisi.data(f["data_fine"])

    def sizeHint(self) -> QSize:
        if not self.periodo:
            return QSize(LARGHEZZA_ETICHETTE + 400, ALTEZZA_INTESTAZIONE + ALTEZZA_RIGA * 2)
        return QSize(
            int(LARGHEZZA_ETICHETTE + self._giorni() * self.pixel_giorno + 20),
            self._y_grafici() + 2 * (ALTEZZA_GRAFICO + 6) + ALTEZZA_LEGENDA + 4,
        )

    # --- disegno ---

    def paintEvent(self, _evento) -> None:
        p = QPainter(self)
        p.fillRect(self.rect(), self.palette().base())
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        testo = self.palette().text().color()
        if not self.periodo:
            p.setPen(testo)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                       "Inserisci le date delle fasi per visualizzare il cronoprogramma.")
            return
        self._disegna_griglia(p, testo)
        self._disegna_fasi(p, testo)
        self._disegna_oggi(p)
        self._disegna_grafici(p, testo)
        self._disegna_legenda(p, testo)

    def _disegna_griglia(self, p: QPainter, testo: QColor) -> None:
        griglia = QPen(self.palette().mid().color())
        debole = self.palette().placeholderText().color()
        origine = self._origine()
        fondo = self.height() - ALTEZZA_LEGENDA
        for g in range(self._giorni()):
            giorno = origine + timedelta(days=g)
            x = self._x(giorno)
            if giorno.weekday() >= 5 and self.pixel_giorno > ZOOM["Mesi"]:
                p.fillRect(QRectF(x, ALTEZZA_INTESTAZIONE, self.pixel_giorno, fondo - ALTEZZA_INTESTAZIONE),
                           COLORE_FINE_SETTIMANA)
            if giorno.day == 1 or g == 0:
                # Riga superiore: mese e anno.
                p.setPen(griglia)
                p.drawLine(QPointF(x, 0), QPointF(x, fondo))
                p.setPen(testo)
                p.drawText(QRectF(x + 3, 0, 120, 16), Qt.AlignmentFlag.AlignVCenter,
                           f"{MESI[giorno.month - 1]} {giorno.year}")
            # Riga inferiore: giorni o settimane.
            if self.pixel_giorno >= ZOOM["Giorni"]:
                p.setPen(debole)
                p.drawText(QRectF(x, 16, self.pixel_giorno, 14), Qt.AlignmentFlag.AlignCenter, str(giorno.day))
            elif self.pixel_giorno >= ZOOM["Settimane"] and giorno.weekday() == 0:
                p.setPen(griglia)
                p.drawLine(QPointF(x, 16), QPointF(x, fondo))
                p.setPen(debole)
                p.drawText(QRectF(x + 2, 16, 7 * self.pixel_giorno, 14), Qt.AlignmentFlag.AlignVCenter,
                           giorno.strftime("%d/%m"))
        p.setPen(griglia)
        p.drawLine(QPointF(0, ALTEZZA_INTESTAZIONE), QPointF(self.width(), ALTEZZA_INTESTAZIONE))

    def _disegna_fasi(self, p: QPainter, testo: QColor) -> None:
        griglia = QPen(self.palette().mid().color())
        periodi_interferenza: dict[int, list[tuple[date, date]]] = {}
        for i in self.interferenze:
            for f in (i.fase_a, i.fase_b):
                periodi_interferenza.setdefault(f["id"], []).append((i.inizio, i.fine))
        debole = self.palette().placeholderText().color()
        for r, f in enumerate(self.fasi):
            y = self._y_righe() + r * ALTEZZA_RIGA
            if f["id"] == self.selezionata:
                p.fillRect(QRectF(0, y, self.width(), ALTEZZA_RIGA), _colore_tema("sel"))
                p.fillRect(QRectF(0, y, 3, ALTEZZA_RIGA), _colore_tema("acc_s"))
            p.setPen(griglia)
            p.drawLine(QPointF(0, y + ALTEZZA_RIGA), QPointF(self.width(), y + ALTEZZA_RIGA))
            # nome della fase sopra, impresa sotto (più piccola)
            carattere = p.font()
            grassetto = QFont(carattere)
            grassetto.setBold(f["id"] == self.selezionata)
            p.setFont(grassetto)
            p.setPen(testo)
            etichetta = f"{f['codice']} {f['descrizione']}".strip()
            larghezza = LARGHEZZA_ETICHETTE - 16
            p.drawText(QRectF(10, y + 3, larghezza, 18), Qt.AlignmentFlag.AlignVCenter,
                       p.fontMetrics().elidedText(etichetta, Qt.TextElideMode.ElideRight, larghezza))
            piccolo = QFont(carattere)
            piccolo.setPointSizeF(max(6.5, carattere.pointSizeF() - 1.5))
            p.setFont(piccolo)
            p.setPen(debole)
            impresa = self.imprese.get(f.get("impresa_id")) if f.get("impresa_id") else "impresa da definire"
            p.drawText(QRectF(10, y + 20, larghezza, 16), Qt.AlignmentFlag.AlignVCenter,
                       p.fontMetrics().elidedText(impresa or "", Qt.TextElideMode.ElideRight, larghezza))
            p.setFont(carattere)
            inizio, fine = self._date(f)
            if not (inizio and fine) or fine < inizio:
                continue
            barra = self._rett_barra(r, inizio, fine)
            colore = self.colore_impresa(f.get("impresa_id"))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(colore)
            p.drawRoundedRect(barra, 4, 4)
            # Periodi di interferenza: tratteggio rosso sopra la barra.
            for da, a in periodi_interferenza.get(f["id"], []):
                if self._trascinamento and self._trascinamento["id"] == f["id"]:
                    break
                zona = self._rett_barra(r, da, a)
                p.setBrush(QBrush(COLORE_INTERFERENZA, Qt.BrushStyle.BDiagPattern))
                p.setPen(QPen(COLORE_INTERFERENZA, 1.5))
                p.drawRoundedRect(zona, 3, 3)
            if self._trascinamento and self._trascinamento["id"] == f["id"]:
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.setPen(QPen(COLORE_OGGI, 2, Qt.PenStyle.DashLine))
                p.drawRoundedRect(barra.adjusted(-2, -2, 2, 2), 4, 4)

    def _disegna_oggi(self, p: QPainter) -> None:
        origine = self._origine()
        if not (origine <= self.oggi <= origine + timedelta(days=self._giorni())):
            return
        x = self._x(self.oggi) + self.pixel_giorno / 2
        p.setPen(QPen(COLORE_OGGI, 1.5, Qt.PenStyle.DashLine))
        p.drawLine(QPointF(x, ALTEZZA_INTESTAZIONE - 12), QPointF(x, self.height() - ALTEZZA_LEGENDA))
        # «oggi» nella riga delle date, senza coprire le barre delle fasi
        carattere = QFont(p.font())
        carattere.setBold(True)
        p.setFont(carattere)
        p.setPen(COLORE_OGGI)
        p.drawText(QRectF(x - 20, ALTEZZA_INTESTAZIONE - 14, 40, 13), Qt.AlignmentFlag.AlignCenter, "oggi")
        carattere.setBold(False)
        p.setFont(carattere)

    def _disegna_grafici(self, p: QPainter, testo: QColor) -> None:
        y0 = self._y_grafici()
        massimo = max((g.lavoratori for g in self.giornate), default=0)
        self._etichetta_grafico(p, testo, y0, f"Affollamento (massimo {massimo} lavoratori)")
        self._etichetta_grafico(p, testo, y0 + ALTEZZA_GRAFICO + 6, "Pericolosità (rischio massimo)")
        p.setPen(Qt.PenStyle.NoPen)
        for g in self.giornate:
            x = self._x(g.giorno)
            if massimo:
                h = (ALTEZZA_GRAFICO - 4) * g.lavoratori / massimo
                tinta = _colore_tema("acc_s")
                tinta.setAlpha(255 if g.lavoratori == massimo else 110)  # il picco più scuro
                p.setBrush(tinta)
                p.drawRect(QRectF(x, y0 + ALTEZZA_GRAFICO - h, self.pixel_giorno, h))
            if g.pericolosita:
                h = (ALTEZZA_GRAFICO - 4) * g.pericolosita / 16
                yb = y0 + 2 * ALTEZZA_GRAFICO + 6
                p.setBrush(colore_livello(g.pericolosita))
                p.drawRect(QRectF(x, yb - h, self.pixel_giorno, h))

    def _etichetta_grafico(self, p: QPainter, testo: QColor, y: float, etichetta: str) -> None:
        p.setPen(QPen(self.palette().mid().color()))
        p.drawLine(QPointF(0, y), QPointF(self.width(), y))
        p.drawLine(QPointF(LARGHEZZA_ETICHETTE, y + ALTEZZA_GRAFICO), QPointF(self.width(), y + ALTEZZA_GRAFICO))
        p.setPen(testo)
        p.drawText(QRectF(6, y, LARGHEZZA_ETICHETTE - 12, ALTEZZA_GRAFICO),
                   Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap, etichetta)

    def _disegna_legenda(self, p: QPainter, testo: QColor) -> None:
        y = self.height() - ALTEZZA_LEGENDA + 8
        x = 6.0
        voci: list[tuple[str, QBrush, QPen]] = []
        usate = {f.get("impresa_id") for f in self.fasi}
        for impresa_id in sorted(i for i in usate if i):
            colore = self.colore_impresa(impresa_id)
            voci.append((self.imprese.get(impresa_id, f"Impresa {impresa_id}"), QBrush(colore), QPen(Qt.PenStyle.NoPen)))
        if None in usate or 0 in usate:
            voci.append(("Impresa da definire", QBrush(COLORE_SENZA_IMPRESA), QPen(Qt.PenStyle.NoPen)))
        voci.append(("Interferenza", QBrush(COLORE_INTERFERENZA, Qt.BrushStyle.BDiagPattern),
                     QPen(COLORE_INTERFERENZA, 1.5)))
        metriche = p.fontMetrics()
        for nome, pennello, penna in voci:
            p.setPen(penna)
            p.setBrush(pennello)
            p.drawRoundedRect(QRectF(x, y + 2, 22, 12), 3, 3)
            p.setPen(testo)
            p.drawText(QPointF(x + 28, y + 12), nome)
            x += 28 + metriche.horizontalAdvance(nome) + 18
        p.setPen(QPen(COLORE_OGGI, 2, Qt.PenStyle.DashLine))
        p.drawLine(QPointF(x + 4, y), QPointF(x + 4, y + 16))
        p.setPen(testo)
        p.drawText(QPointF(x + 12, y + 12), "Oggi")

    # --- interazione ---

    def _fase_in(self, pos: QPointF) -> tuple[dict[str, Any], QRectF, bool] | None:
        """Fase sotto il puntatore, rettangolo della barra e se si è sul bordo destro."""
        if not self.periodo:
            return None
        r = int((pos.y() - self._y_righe()) // ALTEZZA_RIGA)
        if not (0 <= r < len(self.fasi)) or pos.y() < self._y_righe():
            return None
        f = self.fasi[r]
        inizio, fine = analisi.data(f["data_inizio"]), analisi.data(f["data_fine"])
        if not (inizio and fine):
            return None
        barra = self._rett_barra(r, inizio, fine)
        if barra.adjusted(-2, -4, MARGINE_BORDO, 4).contains(pos):
            return f, barra, pos.x() >= barra.right() - MARGINE_BORDO
        return None

    def _riga_in(self, pos: QPointF) -> dict[str, Any] | None:
        r = int((pos.y() - self._y_righe()) // ALTEZZA_RIGA)
        if pos.y() < self._y_righe() or not (0 <= r < len(self.fasi)):
            return None
        return self.fasi[r]

    def mousePressEvent(self, evento) -> None:
        riga = self._riga_in(evento.position()) if self.periodo else None
        if riga is not None and evento.button() == Qt.MouseButton.LeftButton:
            self.seleziona(riga["id"])
            self.fase_cliccata.emit(riga["id"])
        trovata = self._fase_in(evento.position())
        if evento.button() != Qt.MouseButton.LeftButton or trovata is None:
            return super().mousePressEvent(evento)
        f, _, bordo = trovata
        inizio, fine = analisi.data(f["data_inizio"]), analisi.data(f["data_fine"])
        self._trascinamento = {
            "id": f["id"], "modo": "durata" if bordo else "sposta", "x0": evento.position().x(),
            "originale": (inizio, fine), "anteprima": (inizio, fine),
        }
        self.setCursor(Qt.CursorShape.SizeHorCursor if bordo else Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, evento) -> None:
        t = self._trascinamento
        if t is None:
            trovata = self._fase_in(evento.position())
            if trovata is None:
                self.unsetCursor()
            else:
                self.setCursor(Qt.CursorShape.SizeHorCursor if trovata[2] else Qt.CursorShape.OpenHandCursor)
            return
        giorni = round((evento.position().x() - t["x0"]) / self.pixel_giorno)
        inizio, fine = t["originale"]
        if t["modo"] == "sposta":
            t["anteprima"] = (inizio + timedelta(days=giorni), fine + timedelta(days=giorni))
        else:
            t["anteprima"] = (inizio, max(inizio, fine + timedelta(days=giorni)))
        da, a = t["anteprima"]
        QToolTip.showText(evento.globalPosition().toPoint(),
                          f"{da:%d/%m/%Y} - {a:%d/%m/%Y} ({analisi.giorni_lavorativi(da, a)} giorni lavorativi)", self)
        self.update()

    def mouseReleaseEvent(self, evento) -> None:
        t = self._trascinamento
        self._trascinamento = None
        self.unsetCursor()
        if t is None:
            return super().mouseReleaseEvent(evento)
        self.update()
        if t["anteprima"] != t["originale"]:
            da, a = t["anteprima"]
            self.fase_modificata.emit(t["id"], da.isoformat(), a.isoformat())

    def event(self, evento) -> bool:
        if evento.type() == QEvent.Type.ToolTip and self._trascinamento is None:
            trovata = self._fase_in(QPointF(evento.pos()))
            if trovata is None:
                QToolTip.hideText()
            else:
                f = trovata[0]
                inizio, fine = analisi.data(f["data_inizio"]), analisi.data(f["data_fine"])
                QToolTip.showText(evento.globalPos(), (
                    f"<b>{f['codice']} {f['descrizione']}</b><br>"
                    f"Impresa: {self.imprese.get(f.get('impresa_id'), 'da definire')}<br>"
                    f"{inizio:%d/%m/%Y} - {fine:%d/%m/%Y} "
                    f"({analisi.giorni_lavorativi(inizio, fine)} giorni lavorativi)<br>"
                    f"Squadra: {f.get('lavoratori') or 0} lavoratori<br>"
                    "<i>Trascina la barra per spostare la fase, il bordo destro per cambiarne la durata</i>"
                ), self)
            return True
        return super().event(evento)
