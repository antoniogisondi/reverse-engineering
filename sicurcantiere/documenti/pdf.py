"""Conversione dei documenti Word in PDF, per l'anteprima nel programma e per l'invio.

Si usa Microsoft Word, quasi sempre presente negli studi, tramite PowerShell (nessuna libreria da
installare); in alternativa LibreOffice, se installato. Senza nessuno dei due la conversione non è
disponibile e il programma apre il documento in Word come prima.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class ConversioneNonDisponibile(Exception):
    pass


def _libreoffice() -> str | None:
    for nome in ("soffice", "libreoffice"):
        trovato = shutil.which(nome)
        if trovato:
            return trovato
    if os.name == "nt":
        for base in (os.environ.get("ProgramFiles", r"C:\Program Files"),
                     os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")):
            candidato = Path(base) / "LibreOffice" / "program" / "soffice.exe"
            if candidato.is_file():
                return str(candidato)
    return None


def _con_word(docx: Path, pdf: Path, attesa: int) -> bool:
    if os.name != "nt":
        return False
    def stringa(percorso: Path) -> str:  # stringa PowerShell tra apici (l'apice si raddoppia)
        return "'" + str(percorso).replace("'", "''") + "'"

    comando = (
        "$ErrorActionPreference='Stop';"
        "$w=New-Object -ComObject Word.Application;$w.Visible=$false;$w.DisplayAlerts=0;"
        f"try{{$d=$w.Documents.Open({stringa(docx)},$false,$true);"
        f"$d.ExportAsFixedFormat({stringa(pdf)},17);$d.Close(0)}}finally{{$w.Quit()}}"
    )
    try:
        esito = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", comando],
                               capture_output=True, timeout=attesa,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.TimeoutExpired):
        return False
    return esito.returncode == 0 and pdf.is_file()


def _con_libreoffice(docx: Path, pdf: Path, attesa: int) -> bool:
    programma = _libreoffice()
    if not programma:
        return False
    with tempfile.TemporaryDirectory() as cartella:
        try:
            subprocess.run([programma, "--headless", "--convert-to", "pdf", "--outdir", cartella, str(docx)],
                           capture_output=True, timeout=attesa,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except (OSError, subprocess.TimeoutExpired):
            return False
        prodotto = Path(cartella) / (docx.stem + ".pdf")
        if not prodotto.is_file():
            return False
        shutil.move(str(prodotto), pdf)
    return True


def disponibile() -> bool:
    return os.name == "nt" or _libreoffice() is not None


def converti(docx: str | Path, pdf: str | Path | None = None, attesa: int = 180) -> Path:
    """Crea il PDF del documento Word (accanto, se non si indica dove) e ne restituisce il percorso."""
    docx = Path(docx).resolve()
    pdf = Path(pdf).resolve() if pdf else docx.with_suffix(".pdf")
    if pdf.exists():
        pdf.unlink()
    if _con_word(docx, pdf, attesa) or _con_libreoffice(docx, pdf, attesa):
        return pdf
    raise ConversioneNonDisponibile(
        "Per creare il PDF serve Microsoft Word oppure LibreOffice installato su questo computer.")


def converti_dati(contenuto: bytes, nome: str = "documento") -> bytes:
    """PDF di un documento Word dato come contenuto (per le composizioni salvate nel cantiere)."""
    with tempfile.TemporaryDirectory() as cartella:
        docx = Path(cartella) / f"{nome}.docx"
        docx.write_bytes(contenuto)
        return converti(docx).read_bytes()
