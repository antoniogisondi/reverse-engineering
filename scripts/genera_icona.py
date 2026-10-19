"""Genera assets/sicurcantiere.ico e .png dall'icona vettoriale del programma.

Uso: python scripts/genera_icona.py
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE))

from PySide6.QtWidgets import QApplication  # noqa: E402

from sicurcantiere.ui.icone import immagine_applicazione  # noqa: E402


def main() -> None:
    app = QApplication([])  # noqa: F841 - necessario per QPixmap
    cartella = RADICE / "assets"
    cartella.mkdir(exist_ok=True)
    immagine = immagine_applicazione(256)
    if not immagine.save(str(cartella / "sicurcantiere.png"), "PNG"):
        raise SystemExit("Impossibile salvare il PNG")
    if not immagine.save(str(cartella / "sicurcantiere.ico"), "ICO"):
        raise SystemExit("Formato ICO non disponibile in questa installazione di Qt")
    print(f"Icone salvate in {cartella}")


if __name__ == "__main__":
    main()
