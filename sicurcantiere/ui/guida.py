"""Guida rapida del programma (menu Aiuto)."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout, QWidget

GUIDA = """
<h2>Come si compila un {documento}</h2>
<ol>
<li><b>Nuovo cantiere</b> (Ctrl+N): scegli dove salvare il file. I dati si salvano da soli a ogni
modifica; <i>Salva</i> (Ctrl+S) conferma anche il campo in cui stai scrivendo.</li>
<li><b>Compila le pagine dall'alto in basso</b>, seguendo i numeri nella barra a sinistra. Il numero
rosso o arancio accanto a una pagina dice quanti problemi restano; la spunta verde che è completa.</li>
<li>Nelle lavorazioni usa <b>Importa da archivio...</b>: ogni fase porta con sé macchine, attrezzi,
rischi, misure e DPI, che puoi modificare. Un rischio che non c'è si spunta «Non presente» con la
motivazione.</li>
<li>Le <b>valutazioni dei rischi specifici</b> (carichi, rumore, vibrazioni, movimenti ripetitivi) si
creano da sole in base ai rischi: restano «Da eseguire» finché non inserisci i parametri.</li>
<li>Nell'ultima pagina correggi i <b>controlli</b>: un doppio clic su una riga porta alla pagina da
correggere. Poi premi <b>Genera</b> (Ctrl+P) e rileggi il documento in Word prima di firmarlo.</li>
</ol>
<h3>Dove sono i dati</h3>
<ul>
<li>I cantieri sono nei file che hai salvato (anche su una cartella di rete).</li>
<li>Copie di sicurezza automatiche, fatte a ogni apertura (le ultime 5 per cantiere):
<code>%APPDATA%\\SicurCantiere\\copie di sicurezza</code>.</li>
<li>Archivio personale di anagrafiche e lavorazioni: <code>%APPDATA%\\SicurCantiere\\archivio.db</code>.</li>
</ul>
<h3>Assistente AI</h3>
<p>È spento di serie. Si attiva da <i>Strumenti &gt; Impostazioni assistente AI</i>, dove è spiegato
quali dati vengono inviati e a quale fornitore. Le sue proposte vanno sempre verificate.</p>
<h3>Aggiornamenti</h3>
<p>Il programma controlla da solo le nuove versioni e le segnala in basso a destra; si può controllare
anche da <i>Aiuto &gt; Controlla aggiornamenti</i>. Cantieri e archivio restano dopo l'aggiornamento.</p>
"""


class DialogoGuida(QDialog):
    def __init__(self, documento: str, genitore: QWidget | None = None):
        super().__init__(genitore)
        self.setWindowTitle("Guida rapida")
        self.resize(640, 620)
        testo = QTextBrowser()
        testo.setOpenExternalLinks(True)
        testo.setHtml(GUIDA.format(documento=documento))
        pulsanti = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        pulsanti.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(testo)
        layout.addWidget(pulsanti)
