"""Comandi del gestionale delle licenze.

    python -m licenze genera-chiave     crea la chiave di firma (una volta sola) e stampa la pubblica
    python -m licenze crea-utente NOME  crea o aggiorna un utente (chiede la password)
    python -m licenze chiave-pubblica   stampa la chiave pubblica da inserire nel programma
    python -m licenze prova             avvia il gestionale in locale su http://127.0.0.1:8080 (solo prove)
"""

from __future__ import annotations

import getpass
import sys

from licenze import archivio


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "aiuto"):
        print(__doc__)
        return 0
    comando = argv[0]
    if comando == "genera-chiave":
        try:
            pubblica = archivio.genera_chiave()
        except FileExistsError as e:
            print(e)
            return 1
        print("Chiave di firma creata. Chiave pubblica da inserire nel programma:\n")
        print(pubblica)
        print("\nCopia subito chiave_privata.pem in un posto sicuro (vedi README).")
        return 0
    if comando == "chiave-pubblica":
        print(archivio.chiave_pubblica())
        return 0
    if comando == "crea-utente" and len(argv) == 2:
        from licenze.app import crea_utente

        password = getpass.getpass("Password: ")
        if len(password) < 10 or password != getpass.getpass("Ripeti la password: "):
            print("Password troppo corta (almeno 10 caratteri) o diversa.")
            return 1
        crea_utente(argv[1], password)
        print(f"Utente {argv[1]} pronto.")
        return 0
    if comando == "prova":
        from licenze.app import crea_app

        crea_app().run(host="127.0.0.1", port=8080)
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
