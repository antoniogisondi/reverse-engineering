"""Genera le icone (.ico e .png) dei programmi SicurCantiere.

Dal logo della suite (casco e ingranaggio, intero e ridotto in alto) si ricava l'icona di ogni
programma, con sotto un'etichetta nel colore del programma e la sigla (PSC, POS, PiMUS); nei formati
piccoli, dove la scritta non si leggerebbe, resta solo la fascia colorata. Le icone vanno
in assets/ (eseguibili) e in sicurcantiere/risorse/logo/ (finestre del programma); il logo senza
etichetta resta per l'installatore e per i file dei cantieri.

Uso: python scripts/genera_icona.py
"""

import os
import struct
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE))

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QFontDatabase, QImage, QImageReader, QPainter, QPainterPath  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

LOGO = RADICE / "sicurcantiere" / "risorse" / "logo" / "sicurcantiere.ico"
CARATTERE = RADICE / "sicurcantiere" / "risorse" / "font" / "Ubuntu-Bold.ttf"
LATI = (16, 24, 32, 48, 64, 128, 256)
# colori scuri dei documenti di ciascun programma: con la scritta bianca restano leggibili
PROGRAMMI = {"psc": ("PSC", "#C25E16"), "pos": ("POS", "#1C6597"), "pimus": ("PiMUS", "#1F8577")}


def _immagini_logo() -> dict[int, QImage]:
    lettore = QImageReader(str(LOGO))
    immagini = {}
    for n in range(lettore.imageCount()):
        lettore.jumpToImage(n)
        immagine = lettore.read().convertToFormat(QImage.Format.Format_ARGB32)
        immagini[immagine.width()] = immagine
    return immagini


def _logo(lato: int, immagini: dict[int, QImage]) -> QImage:
    if lato in immagini:
        return immagini[lato].copy()
    piu_grande = immagini[max(immagini)]
    return piu_grande.scaled(lato, lato, Qt.AspectRatioMode.KeepAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)


def icona_programma(lato: int, sigla: str, colore: str, immagini: dict[int, QImage], famiglia: str) -> QImage:
    """Logo intero (casco e ingranaggio) ridotto in alto, con sotto l'etichetta del programma."""
    immagine = QImage(lato, lato, QImage.Format.Format_ARGB32)
    immagine.fill(Qt.GlobalColor.transparent)
    grande = lato >= 48
    lato_logo = round(lato * (0.70 if grande else 0.76))
    logo = _logo(lato_logo, immagini)
    p = QPainter(immagine)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    p.drawImage((lato - lato_logo) // 2, 0, logo)
    if grande:
        altezza = lato * 0.27
        larghezza = lato * (0.96 if len(sigla) > 3 else 0.78)
        rett = QRectF((lato - larghezza) / 2, lato - altezza - lato * 0.01, larghezza, altezza)
        percorso = QPainterPath()
        percorso.addRoundedRect(rett, altezza * 0.28, altezza * 0.28)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(colore))
        p.drawPath(percorso)
        carattere = QFont(famiglia)
        carattere.setBold(True)
        carattere.setPixelSize(round(altezza * (0.66 if len(sigla) > 3 else 0.72)))
        p.setFont(carattere)
        p.setPen(QColor("white"))
        p.drawText(rett, Qt.AlignmentFlag.AlignCenter, sigla)
    else:
        # formati piccoli: fascia colorata sotto il logo, la sigla non si leggerebbe
        altezza = max(2.0, lato - lato_logo - 1.0)
        rett = QRectF(lato * 0.1, lato - altezza, lato * 0.8, altezza)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(colore))
        p.drawRoundedRect(rett, altezza * 0.35, altezza * 0.35)
    p.end()
    return immagine


def _png(immagine: QImage) -> bytes:
    dati = QByteArray()
    buffer = QBuffer(dati)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    immagine.save(buffer, "PNG")
    buffer.close()
    return bytes(dati)


def salva_ico(immagini: list[QImage], percorso: Path) -> None:
    """File .ico con tutti i formati (Qt ne scriverebbe uno solo); ogni formato è un PNG."""
    blocchi = [_png(i) for i in immagini]
    testa = struct.pack("<HHH", 0, 1, len(immagini))
    posizione = 6 + 16 * len(immagini)
    voci = b""
    for immagine, blocco in zip(immagini, blocchi):
        lato = immagine.width()
        voci += struct.pack("<BBBBHHII", lato % 256, lato % 256, 0, 0, 1, 32, len(blocco), posizione)
        posizione += len(blocco)
    percorso.write_bytes(testa + voci + b"".join(blocchi))


def main() -> None:
    app = QApplication([])  # noqa: F841 - necessario per QPainter e caratteri
    ident = QFontDatabase.addApplicationFont(str(CARATTERE))
    famiglie = QFontDatabase.applicationFontFamilies(ident) if ident != -1 else []
    famiglia = famiglie[0] if famiglie else "Segoe UI"
    immagini = _immagini_logo()
    assets = RADICE / "assets"
    assets.mkdir(exist_ok=True)
    cartella_logo = LOGO.parent
    for chiave, (sigla, colore) in PROGRAMMI.items():
        formati = [icona_programma(lato, sigla, colore, immagini, famiglia) for lato in LATI]
        for cartella in (assets, cartella_logo):
            salva_ico(formati, cartella / f"sicurcantiere-{chiave}.ico")
            formati[-1].save(str(cartella / f"sicurcantiere-{chiave}.png"), "PNG")
    # logo senza etichetta: installatore e icona dei file dei cantieri
    salva_ico([_logo(lato, immagini) for lato in LATI], assets / "sicurcantiere.ico")
    print(f"Icone salvate in {assets} e {cartella_logo}")


if __name__ == "__main__":
    main()
