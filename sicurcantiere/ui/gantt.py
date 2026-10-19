"""Diagramma di Gantt delle fasi con grafici di affollamento e pericolosità."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from sicurcantiere import analisi

ALTEZZA_RIGA = 22
ALTEZZA_INTESTAZIONE = 28
ALTEZZA_GRAFICO = 60
LARGHEZZA_ETICHETTE = 260
PIXEL_GIORNO = 6

COLORE_BARRA = QColor("#4F81BD")
COLORE_INTERFERENZA = QColor("#C0504D")
COLORE_AFFOLLAMENTO = QColor("#8064A2")
COLORE_GRIGLIA = QColor("#D0D0D0")
COLORE_FINE_SETTIMANA = QColor(0, 0, 0, 18)
# Colori per classe di rischio: basso, medio, alto, molto alto.
COLORI_PERICOLOSITA = [(9, QColor("#C0392B")), (6, QColor("#E67E22")), (3, QColor("#F1C40F")),
                       (1, QColor("#27AE60"))]


def colore_livello(livello: int) -> QColor:
    for soglia, colore in COLORI_PERICOLOSITA:
        if livello >= soglia:
            return colore
    return QColor(0, 0, 0, 0)


class Gantt(QWidget):
    def __init__(self, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.fasi: list[dict[str, Any]] = []
        self.interferenti: set[int] = set()
        self.giornate: list[analisi.Giornata] = []
        self.periodo = None
        self.setMinimumHeight(ALTEZZA_INTESTAZIONE + ALTEZZA_RIGA)

    def imposta_fasi(self, fasi: list[dict[str, Any]], livelli: dict[int, int]) -> None:
        self.fasi = fasi
        self.periodo = analisi.periodo_lavori(fasi)
        self.interferenti = {
            f["id"] for i in analisi.interferenze(fasi, livelli) for f in (i.fase_a, i.fase_b)
        }
        self.giornate = analisi.andamento(fasi, livelli)
        self.updateGeometry()
        self.resize(self.sizeHint())
        self.update()

    def _giorni(self) -> int:
        if not self.periodo:
            return 0
        return (self.periodo[1] - self._origine()).days + 1

    def _origine(self):
        inizio = self.periodo[0]
        return inizio - timedelta(days=inizio.weekday())

    def _altezza_righe(self) -> int:
        return ALTEZZA_INTESTAZIONE + max(len(self.fasi), 1) * ALTEZZA_RIGA

    def sizeHint(self) -> QSize:
        return QSize(
            LARGHEZZA_ETICHETTE + self._giorni() * PIXEL_GIORNO + 20,
            self._altezza_righe() + (2 * ALTEZZA_GRAFICO + 12 if self.periodo else 0) + 4,
        )

    def paintEvent(self, _evento) -> None:
        p = QPainter(self)
        p.fillRect(self.rect(), self.palette().base())
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        testo = self.palette().text().color()
        if not self.periodo:
            p.setPen(testo)
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                       "Inserire le date delle fasi per vedere il cronoprogramma")
            return

        origine = self._origine()
        giorni = self._giorni()
        altezza = self.height()

        # Fine settimana e settimane
        for g in range(giorni):
            giorno = origine + timedelta(days=g)
            x = LARGHEZZA_ETICHETTE + g * PIXEL_GIORNO
            if giorno.weekday() >= 5:
                p.fillRect(QRectF(x, ALTEZZA_INTESTAZIONE, PIXEL_GIORNO, altezza), COLORE_FINE_SETTIMANA)
            if giorno.weekday() == 0:
                p.setPen(QPen(COLORE_GRIGLIA))
                p.drawLine(x, ALTEZZA_INTESTAZIONE - 6, x, altezza)
                p.setPen(testo)
                p.drawText(QRectF(x + 2, 4, 7 * PIXEL_GIORNO, 18),
                           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                           giorno.strftime("%d/%m"))

        # Righe delle fasi
        for r, f in enumerate(self.fasi):
            y = ALTEZZA_INTESTAZIONE + r * ALTEZZA_RIGA
            p.setPen(QPen(COLORE_GRIGLIA))
            p.drawLine(0, y, self.width(), y)
            p.setPen(testo)
            etichetta = f"{f['codice']} {f['descrizione']}".strip()
            p.drawText(QRectF(4, y, LARGHEZZA_ETICHETTE - 8, ALTEZZA_RIGA),
                       Qt.AlignmentFlag.AlignVCenter,
                       p.fontMetrics().elidedText(etichetta, Qt.TextElideMode.ElideRight,
                                                  LARGHEZZA_ETICHETTE - 8))
            inizio, fine = analisi.data(f["data_inizio"]), analisi.data(f["data_fine"])
            if not (inizio and fine) or fine < inizio:
                continue
            x = LARGHEZZA_ETICHETTE + (inizio - origine).days * PIXEL_GIORNO
            larghezza = ((fine - inizio).days + 1) * PIXEL_GIORNO
            colore = COLORE_INTERFERENZA if f["id"] in self.interferenti else COLORE_BARRA
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(colore)
            p.drawRoundedRect(QRectF(x, y + 4, larghezza, ALTEZZA_RIGA - 8), 3, 3)

        # Grafici di affollamento e pericolosità
        y0 = self._altezza_righe() + 6
        massimo = max((g.lavoratori for g in self.giornate), default=0)
        self._etichetta_grafico(p, testo, y0, f"Affollamento (max {massimo} lavoratori)")
        self._etichetta_grafico(p, testo, y0 + ALTEZZA_GRAFICO + 6, "Pericolosità (rischio massimo)")
        p.setPen(Qt.PenStyle.NoPen)
        for g in self.giornate:
            x = LARGHEZZA_ETICHETTE + (g.giorno - origine).days * PIXEL_GIORNO
            if massimo:
                h = (ALTEZZA_GRAFICO - 4) * g.lavoratori / massimo
                p.setBrush(COLORE_AFFOLLAMENTO)
                p.drawRect(QRectF(x, y0 + ALTEZZA_GRAFICO - h, PIXEL_GIORNO, h))
            if g.pericolosita:
                h = (ALTEZZA_GRAFICO - 4) * g.pericolosita / 16
                yb = y0 + 2 * ALTEZZA_GRAFICO + 6
                p.setBrush(colore_livello(g.pericolosita))
                p.drawRect(QRectF(x, yb - h, PIXEL_GIORNO, h))

    def _etichetta_grafico(self, p: QPainter, testo: QColor, y: float, etichetta: str) -> None:
        p.setPen(QPen(COLORE_GRIGLIA))
        p.drawLine(0, int(y), self.width(), int(y))
        p.drawLine(LARGHEZZA_ETICHETTE, int(y + ALTEZZA_GRAFICO), self.width(), int(y + ALTEZZA_GRAFICO))
        p.setPen(testo)
        p.drawText(QRectF(4, y, LARGHEZZA_ETICHETTE - 8, ALTEZZA_GRAFICO),
                   Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap, etichetta)
