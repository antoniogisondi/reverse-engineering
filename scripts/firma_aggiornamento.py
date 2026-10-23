"""Firma l'installatore pubblicato con la chiave degli aggiornamenti (usato dal workflow di pubblicazione).

La chiave privata arriva dal segreto SICURCANTIERE_FIRMA_AGGIORNAMENTI di GitHub (32 byte in base64,
creata sulla VM con «python -m licenze chiave-aggiornamenti»). Crea «SicurCantiere-setup.exe.firma»
accanto all'installatore e la verifica subito con la chiave pubblica scritta nel programma, così una
chiave sbagliata blocca la pubblicazione invece di produrre aggiornamenti che i clienti rifiuterebbero.

Uso: python scripts/firma_aggiornamento.py dist/SicurCantiere-x.y.z-setup.exe
"""

import base64
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sicurcantiere import __version__, aggiornamenti  # noqa: E402


def main(argv: list[str]) -> int:
    installatore = Path(argv[0])
    segreto = os.environ.get("SICURCANTIERE_FIRMA_AGGIORNAMENTI", "").strip()
    pubblica = aggiornamenti.chiave_aggiornamenti()
    if not segreto:
        if pubblica:
            print("ERRORE: il programma verifica la firma degli aggiornamenti ma manca il segreto "
                  "SICURCANTIERE_FIRMA_AGGIORNAMENTI: i clienti non potrebbero installare questa versione.")
            return 1
        print("Firma degli aggiornamenti non ancora configurata: installatore pubblicato senza firma.")
        return 0
    testo = aggiornamenti.firma_installatore(installatore, __version__, base64.b64decode(segreto))
    destinazione = installatore.with_name(aggiornamenti.NOME_FIRMA)
    destinazione.write_text(testo, encoding="utf-8")
    if pubblica:
        aggiornamenti.verifica_installatore(installatore, __version__, testo)  # chiave giusta?
    print(f"Firma creata: {destinazione}" + ("" if pubblica else " (il programma non la verifica ancora)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
