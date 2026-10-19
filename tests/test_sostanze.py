import pytest

from sicurcantiere import sds, sostanze


def test_codici_h():
    testo = "Indicazioni: H315 Provoca irritazione. H317, H318Danni H360FD EUH 208 H350i h999 H2O"
    assert sostanze.codici_h(testo) == ["H315", "H317", "H318", "H360FD", "EUH208", "H350i"]
    assert sostanze.elenco_codici("H315,H315 H319") == "H315, H319"
    assert sostanze.descrizione("H360FD") == sostanze.FRASI_H["H360"]
    assert "cancro se inalato" in sostanze.descrizione("H350i")


def test_pittogrammi_e_precedenze():
    assert sostanze.pittogrammi(["H225", "H319"]) == ["GHS02", "GHS07"]
    # GHS06 esclude GHS07
    assert sostanze.pittogrammi(["H301", "H302"]) == ["GHS06"]
    # GHS05 esclude GHS07 per irritazione cutanea/oculare, non per altri motivi
    assert sostanze.pittogrammi(["H318", "H315"]) == ["GHS05"]
    assert sostanze.pittogrammi(["H318", "H335"]) == ["GHS05", "GHS07"]
    # sensibilizzante respiratorio: GHS08, niente GHS07 per sensibilizzazione cutanea
    assert sostanze.pittogrammi(["H334", "H317"]) == ["GHS08"]
    assert sostanze.pittogrammi(["H350i"]) == ["GHS08"]
    assert sostanze.pittogrammi([]) == []


def test_categorie():
    cemento = sostanze.categorie(["H315", "H317", "H318", "H335"])
    nomi = [c.nome for c in cemento]
    assert nomi == ["Sensibilizzante", "Corrosivo", "Nocivo o irritante"]
    cancerogeno = sostanze.categorie(["H350", "H225"])
    assert cancerogeno[0].nome == "Cancerogeno o mutageno" and cancerogeno[0].grave
    assert any("Titolo IX, Capo II" in m for m in cancerogeno[0].misure)
    assert sostanze.categorie([]) == []


def _pdf(percorso, righe):
    """Scrive un PDF di testo minimale (font standard Helvetica).

    Non usa Qt: in modalità offscreen su Windows Qt non trova i caratteri e
    produrrebbe pagine vuote, mentre qui il PDF è lo stesso su ogni sistema.
    """
    def testo_pdf(riga):
        return riga.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    flusso = "BT /F1 11 Tf 14 TL 50 800 Td " + " ".join(f"({testo_pdf(r)}) Tj T*" for r in righe) + " ET"
    contenuto = flusso.encode("cp1252")
    oggetti = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(contenuto)).encode() + b" >>\nstream\n" + contenuto + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    dati = bytearray(b"%PDF-1.4\n")
    posizioni = []
    for n, oggetto in enumerate(oggetti, start=1):
        posizioni.append(len(dati))
        dati += f"{n} 0 obj\n".encode() + oggetto + b"\nendobj\n"
    xref = len(dati)
    dati += f"xref\n0 {len(oggetti) + 1}\n0000000000 65535 f \n".encode()
    dati += b"".join(f"{p:010d} 00000 n \n".encode() for p in posizioni)
    dati += f"trailer\n<< /Size {len(oggetti) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    percorso.write_bytes(bytes(dati))


def test_lettura_sds_pdf(tmp_path):
    f = tmp_path / "scheda.pdf"
    _pdf(f, [
        "SCHEDA DI DATI DI SICUREZZA",
        "SEZIONE 1: Identificazione",
        "Nome commerciale: Cemento Portland CEM II 42,5",
        "Data di revisione: 15/03/2024",
        "SEZIONE 2: Identificazione dei pericoli",
        "Avvertenza: Pericolo",
        "H315 Provoca irritazione cutanea. H317 Puo provocare una reazione allergica cutanea.",
        "H318 Provoca gravi lesioni oculari. H335 Puo irritare le vie respiratorie.",
    ])
    dati, testo = sds.leggi_pdf(f)
    assert dati.codici_h == ["H315", "H317", "H318", "H335"]
    assert dati.avvertenza == "Pericolo"
    assert dati.data_revisione == "2024-03-15"
    assert dati.nome.startswith("Cemento Portland")
    assert "SEZIONE 2" in testo


def test_pdf_senza_testo(tmp_path):
    f = tmp_path / "vuoto.pdf"
    _pdf(f, [])
    with pytest.raises(sds.ErroreSDS, match="testo leggibile"):
        sds.leggi_pdf(f)
    with pytest.raises(sds.ErroreSDS):
        sds.leggi_pdf(tmp_path / "manca.pdf")
