"""Punto di ingresso del programma compilato (Nuitka): l'edizione dipende dal nome dell'eseguibile
(«SicurCantiere PSC.exe», «SicurCantiere POS.exe», «SicurCantiere PiMUS.exe»), altrimenti dal primo
argomento (psc, pos, pimus)."""

from sicurcantiere.app import main_da_eseguibile

raise SystemExit(main_da_eseguibile())
