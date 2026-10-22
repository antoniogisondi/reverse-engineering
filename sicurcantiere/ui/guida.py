"""Guida rapida del programma (menu Aiuto)."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout, QWidget

GUIDA = """
<h2>Come si compila un {documento}</h2>
<ol>
<li><b>Nuovo cantiere</b> (Ctrl+N): scegli dove salvare il file. I dati vengono salvati automaticamente
a ogni modifica; <i>Salva</i> (Ctrl+S) registra anche il campo in cui stai scrivendo.</li>
<li><b>Compila le pagine dall'alto in basso</b>, seguendo i numeri nella barra a sinistra. Il numero
rosso o arancione accanto a una pagina indica quanti problemi restano da risolvere; la spunta verde indica
che la pagina è completa.</li>
<li>Nelle lavorazioni usa <b>Importa dall'archivio...</b>: ogni fase porta con sé macchine, attrezzi,
rischi, misure e DPI, che puoi modificare. Se un rischio non è presente, spunta «Non presente» e indica
la motivazione.</li>
<li>Le <b>valutazioni dei rischi specifici</b> (carichi, rumore, vibrazioni, movimenti ripetitivi) vengono
create automaticamente in base ai rischi: restano «Da eseguire» finché non ne inserisci i parametri.</li>
<li>Nell'ultima pagina risolvi le segnalazioni dei <b>controlli</b>: con un doppio clic su una riga apri
la pagina da correggere. Poi premi <b>Genera</b> (Ctrl+P) e rileggi il documento in Word prima di
firmarlo.</li>
</ol>
<h3>Dove sono i dati</h3>
<ul>
<li>I cantieri si trovano nei file che hai salvato (anche in una cartella di rete).</li>
<li>Copie di sicurezza automatiche, create a ogni apertura (le ultime 5 per ciascun cantiere):
<code>%APPDATA%\\SicurCantiere\\copie di sicurezza</code>.</li>
<li>Archivio personale di anagrafiche e lavorazioni: <code>%APPDATA%\\SicurCantiere\\archivio.db</code>.</li>
</ul>
<h3>Assistente AI</h3>
<p>È incluso nella licenza, senza chiavi né account, con un credito mensile che dipende dal piano.
È disattivato per impostazione predefinita: puoi attivarlo da <i>Strumenti &gt; Impostazioni assistente
AI</i>, dove trovi quali dati vengono inviati e il credito disponibile. Non è disponibile durante la prova
gratuita. Verifica sempre le sue proposte.</p>
<h3>Aggiornamenti</h3>
<p>Il programma verifica automaticamente la disponibilità di nuove versioni e le segnala in basso a
destra; puoi verificarla anche da <i>Aiuto &gt; Controlla aggiornamenti</i>. Cantieri e archivio vengono
conservati con l'aggiornamento.</p>
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
