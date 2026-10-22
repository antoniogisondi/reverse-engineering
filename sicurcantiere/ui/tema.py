"""Tema grafico: colori, caratteri, foglio di stile Qt e delegati che disegnano i badge.

Deriva dal design «SicurCantiere» (foglio di stile in risorse/tema/sicurcantiere.qss, i
segnaposto @nome sono sostituiti qui). Un solo modello per tema chiaro e scuro e per i tre
programmi: cambia solo il colore d'identità.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QPointF, QRectF, QSize, QStandardPaths, Qt, QTimer
from PySide6.QtGui import (QColor, QFont, QFontDatabase, QFontMetrics, QIcon, QPainter, QPalette, QPen,
                           QSyntaxHighlighter, QTextCharFormat)
from PySide6.QtWidgets import (QApplication, QComboBox, QCompleter, QLineEdit, QStyle, QStyledItemDelegate,
                               QStyleOptionViewItem, QWidget)

RISORSE = Path(__file__).resolve().parent.parent / "risorse"
FOGLIO = RISORSE / "tema" / "sicurcantiere.qss"
CARTELLA_CARATTERI = RISORSE / "font"

NEUTRI = {
    "chiaro": {
        "bg": "#EEF1F4", "surface": "#FFFFFF", "surface2": "#F6F8FA",
        "line": "#D7DDE3", "line2": "#B9C3CD",
        "tx": "#17202A", "tx2": "#45515E", "tx3": "#5A6672",
        "err": "#B42318", "err_bg": "#FDECEA",
        "warn": "#9A4500", "warn_bg": "#FFF2DC",
        "ok": "#1E6B34", "ok_bg": "#E2F3E6",
        "ai": "#5B3BB5", "ai_bg": "#F3EFFD", "ai_line": "#C9B9F2",
        "r4t": "#8F1A13",
    },
    "scuro": {
        "bg": "#11161C", "surface": "#192028", "surface2": "#1F2731",
        "line": "#2C3641", "line2": "#405060",
        "tx": "#E5EAF0", "tx2": "#B4BEC9", "tx3": "#99A5B1",
        "err": "#FF8F86", "err_bg": "#3B1E1C",
        "warn": "#FFB866", "warn_bg": "#382915",
        "ok": "#83D69E", "ok_bg": "#173223",
        "ai": "#C5B3FF", "ai_bg": "#272040", "ai_line": "#4C3D80",
        "r4t": "#FF9E96",
    },
}

# acc = colore d'identità (logo, icona), acc_s = pulsanti e testo, sel = selezione
PROGRAMMI = {
    "pos": {
        "chiaro": {"acc": "#2E86C1", "acc_s": "#1C6597", "acc_s_hover": "#165580", "acc_soft": "#E6F1F9",
                   "sel": "#D6E7F4", "acc_tx": "#FFFFFF"},
        "scuro": {"acc": "#2E86C1", "acc_s": "#5DA9DD", "acc_s_hover": "#7BBBE5", "acc_soft": "#1A3245",
                  "sel": "#1F3D57", "acc_tx": "#0A1520"},
    },
    "psc": {
        "chiaro": {"acc": "#E8792B", "acc_s": "#A44C0C", "acc_s_hover": "#8A3F09", "acc_soft": "#FDEEE2",
                   "sel": "#F9DEC8", "acc_tx": "#FFFFFF"},
        "scuro": {"acc": "#E8792B", "acc_s": "#F0A061", "acc_s_hover": "#F4B57F", "acc_soft": "#3A2717",
                  "sel": "#4A2F19", "acc_tx": "#1A0E05"},
    },
    "pimus": {
        "chiaro": {"acc": "#2E9C8F", "acc_s": "#17695F", "acc_s_hover": "#11564E", "acc_soft": "#E1F3F0",
                   "sel": "#C8E8E3", "acc_tx": "#FFFFFF"},
        "scuro": {"acc": "#2E9C8F", "acc_s": "#5CC4B6", "acc_s_hover": "#7AD1C5", "acc_soft": "#14332F",
                  "sel": "#1B4540", "acc_tx": "#06201C"},
    },
}

# Livelli P x D: (nome, sfondo, testo). 1-2 basso, 3-4 medio, 6-8 alto, 9-16 molto alto.
LIVELLI_RISCHIO = {
    "chiaro": [("Basso", "#DCF0E0", "#1B5E2B"), ("Medio", "#FDEFB2", "#674B00"),
               ("Alto", "#FFDCC0", "#863300"), ("Molto alto", "#F7D2CF", "#8F1A13")],
    "scuro": [("Basso", "#1C3B27", "#9FE3B3"), ("Medio", "#3A3213", "#F3D671"),
              ("Alto", "#45290F", "#FFB57D"), ("Molto alto", "#4B1D1B", "#FF9E96")],
}

# Classi delle valutazioni specifiche: (sfondo, testo)
CLASSI_VALUTAZIONE = {
    "chiaro": {"verde": ("#DCF0E0", "#1B5E2B"), "giallo": ("#FDEFB2", "#674B00"),
               "rosso": ("#F7D2CF", "#8F1A13"), "viola": ("#E9DDFB", "#5A2A9C")},
    "scuro": {"verde": ("#1C3B27", "#9FE3B3"), "giallo": ("#3A3213", "#F3D671"),
              "rosso": ("#4B1D1B", "#FF9E96"), "viola": ("#33224D", "#D3B8FF")},
}

CARATTERE, CARATTERE_MONO = "Ubuntu", "Ubuntu Mono"
RISERVA, RISERVA_MONO = "Segoe UI", "Consolas"

_corrente = {"tema": "chiaro", "programma": "pos", "sans": RISERVA, "mono": RISERVA_MONO}


@dataclass(frozen=True)
class Colori:
    """Colori usati dal codice (icone e testi disegnati a mano); `mappa` li ha tutti."""
    mappa: dict

    def __getitem__(self, chiave: str) -> str:
        return self.mappa[chiave]

    @property
    def icone(self) -> str:
        return self.mappa["tx2"]

    @property
    def primario_testo(self) -> str:
        return self.mappa["tx2"]

    @property
    def testo_debole(self) -> str:
        return self.mappa["tx3"]

    @property
    def accento(self) -> str:
        return self.mappa["acc_s"]


def colori(scuro: bool = False, programma: str | None = None) -> Colori:
    tema = "scuro" if scuro else "chiaro"
    c = dict(NEUTRI[tema])
    c.update(PROGRAMMI[programma or _corrente["programma"]][tema])
    return Colori(c)


def correnti() -> Colori:
    """Colori del tema e del programma applicati in questo momento."""
    return colori(_corrente["tema"] == "scuro")


def livello(prodotto: int) -> int:
    """Indice 0-3 del livello per un prodotto P x D (1-16)."""
    return 0 if prodotto <= 2 else 1 if prodotto <= 4 else 2 if prodotto <= 8 else 3


# --- caratteri ---

def carica_caratteri(cartella: Path = CARTELLA_CARATTERI) -> None:
    """Ubuntu e Ubuntu Mono inclusi nel programma (Ubuntu Font Licence); in mancanza Segoe UI e Consolas."""
    famiglie: set[str] = set()
    if cartella.is_dir():
        for f in sorted(cartella.glob("*.ttf")):
            ident = QFontDatabase.addApplicationFont(str(f))
            if ident != -1:
                famiglie.update(QFontDatabase.applicationFontFamilies(ident))
    _corrente["sans"] = CARATTERE if CARATTERE in famiglie else RISERVA
    _corrente["mono"] = CARATTERE_MONO if CARATTERE_MONO in famiglie else RISERVA_MONO


def carattere_mono() -> str:
    return _corrente["mono"]


# --- foglio di stile ---

def _icone_spunta(c: dict) -> dict[str, str]:
    """Spunta, punto e trattino delle caselle nel colore del tema (QSS vuole un'immagine)."""
    base = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
                or Path.home() / ".cache")
    cartella = base / "sicurcantiere_icone"
    cartella.mkdir(parents=True, exist_ok=True)
    colore, freccia, spenta = c["acc_tx"], c["tx2"], c["tx3"]
    forme = {
        "check": (colore, f'<path d="M3.5 8.2l3 3L12.5 5" fill="none" stroke="{colore}" stroke-width="2" '
                          'stroke-linecap="round" stroke-linejoin="round"/>'),
        "dash": (colore, f'<path d="M4 8h8" stroke="{colore}" stroke-width="2" stroke-linecap="round"/>'),
        "dot": (colore, f'<circle cx="8" cy="8" r="3" fill="{colore}"/>'),
        # freccia dei menù a tendina: senza, con il foglio di stile il campo sembra una casella di testo
        "arrow": (freccia, f'<path d="M4 6l4 4 4-4" fill="none" stroke="{freccia}" stroke-width="1.8" '
                           'stroke-linecap="round" stroke-linejoin="round"/>'),
        "arrow_off": (spenta, f'<path d="M4 6l4 4 4-4" fill="none" stroke="{spenta}" stroke-width="1.8" '
                              'stroke-linecap="round" stroke-linejoin="round"/>'),
    }
    percorsi = {}
    for nome, (tinta, corpo) in forme.items():
        f = cartella / f"{nome}_{tinta.lstrip('#')}.svg"
        if not f.exists():
            f.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
                         f"{corpo}</svg>", encoding="utf-8")
        percorsi[f"icon_{nome}"] = f.as_posix()
    return percorsi


def foglio_di_stile(scuro: bool = False, programma: str | None = None) -> str:
    valori = dict(colori(scuro, programma).mappa)
    valori.update(_icone_spunta(valori))
    valori["font"], valori["mono"] = _corrente["sans"], _corrente["mono"]
    modello = re.sub(r"/\*.*?\*/", "", FOGLIO.read_text(encoding="utf-8"), flags=re.S)

    def sostituisci(m: re.Match) -> str:
        if m.group(1) not in valori:
            raise KeyError(f"Segnaposto @{m.group(1)} senza valore nel tema")
        return valori[m.group(1)]

    return re.sub(r"@([a-z0-9_]+)", sostituisci, modello)


def applica(app: QApplication, scuro: bool = False, programma: str | None = None) -> Colori:
    """Applica tema e colore del programma a tutta l'applicazione."""
    _corrente["tema"] = "scuro" if scuro else "chiaro"
    if programma:
        _corrente["programma"] = programma
    if _corrente["sans"] == RISERVA:
        carica_caratteri()
    app.setStyle("Fusion")
    c = colori(scuro)
    p = QPalette()
    for ruolo, chiave in ((QPalette.ColorRole.Window, "bg"), (QPalette.ColorRole.Base, "surface"),
                          (QPalette.ColorRole.AlternateBase, "surface2"), (QPalette.ColorRole.Text, "tx"),
                          (QPalette.ColorRole.WindowText, "tx"), (QPalette.ColorRole.ButtonText, "tx"),
                          (QPalette.ColorRole.Button, "surface"), (QPalette.ColorRole.Highlight, "sel"),
                          (QPalette.ColorRole.HighlightedText, "tx"), (QPalette.ColorRole.PlaceholderText, "tx3"),
                          (QPalette.ColorRole.ToolTipBase, "tx"), (QPalette.ColorRole.ToolTipText, "surface"),
                          (QPalette.ColorRole.Link, "acc_s")):
        p.setColor(ruolo, QColor(c[chiave]))
    for ruolo in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText, QPalette.ColorRole.ButtonText):
        p.setColor(QPalette.ColorGroup.Disabled, ruolo, QColor(c["tx3"]))
    app.setPalette(p)
    carattere = QFont(_corrente["sans"])
    carattere.setPixelSize(13)
    app.setFont(carattere)
    app.setStyleSheet(foglio_di_stile(scuro))
    if not hasattr(app, "_filtro_tendine"):
        app._filtro_tendine = _FiltroTendine(app)
        app.installEventFilter(app._filtro_tendine)
    return c


class _FiltroTendine(QObject):
    """Menù a tendina più facili da usare in tutto il programma.

    Nei campi in cui si può anche scrivere: un clic sul campo vuoto apre l'elenco e, scrivendo,
    compaiono le voci che contengono il testo (non solo quelle che iniziano così).
    """

    def eventFilter(self, oggetto, evento):
        tipo = evento.type()
        if tipo == QEvent.Type.Polish and isinstance(oggetto, QComboBox) and oggetto.isEditable():
            completamento = oggetto.completer()
            if completamento is not None:
                completamento.setFilterMode(Qt.MatchFlag.MatchContains)
                completamento.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                completamento.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        elif (tipo == QEvent.Type.MouseButtonRelease and isinstance(oggetto, QLineEdit)
              and isinstance(oggetto.parent(), QComboBox)):
            tendina = oggetto.parent()
            if not oggetto.text() and tendina.count() > 1 and tendina.isEnabled():
                QTimer.singleShot(0, tendina.showPopup)
        return False


def disegna_freccia(painter: QPainter, rettangolo, colore: str) -> None:
    """Piccola freccia a destra di una cella che si sceglie da un elenco."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    penna = QPen(QColor(colore), 1.6)
    penna.setCapStyle(Qt.PenCapStyle.RoundCap)
    penna.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(penna)
    x, y = rettangolo.right() - 14, rettangolo.center().y()
    painter.drawPolyline([QPointF(x - 4, y - 2), QPointF(x, y + 2), QPointF(x + 4, y - 2)])
    painter.restore()


def _ripolisci(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def imposta_stato(widget: QWidget, stato: str | None) -> None:
    """Stato di un campo o di una tessera: "error", "warning" o None."""
    if widget.property("state") != (stato or ""):
        widget.setProperty("state", stato or "")
        _ripolisci(widget)


def imposta_variante(widget: QWidget, variante: str) -> QWidget:
    """Variante di pulsante: "primary", "ai", "quiet", "danger"."""
    widget.setProperty("variant", variante)
    _ripolisci(widget)
    return widget


# --- delegati: parti di cella che il foglio di stile non sa disegnare ---

def _badge(painter: QPainter, rect: QRectF, testo: str, sfondo: str, colore: str, prefisso: str = "") -> None:
    carattere = QFont(painter.font())
    carattere.setPixelSize(12)
    carattere.setWeight(QFont.Weight.DemiBold)
    fm = QFontMetrics(carattere)
    mono = QFont(_corrente["mono"])
    mono.setPixelSize(12)
    mono.setWeight(QFont.Weight.DemiBold)
    fmm = QFontMetrics(mono)
    spazio = 6 if prefisso else 0
    w = fmm.horizontalAdvance(prefisso) + spazio + fm.horizontalAdvance(testo) + 16
    r = QRectF(rect.left() + 8, rect.center().y() - 11, w, 22)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(sfondo))
    painter.drawRoundedRect(r, 4, 4)
    painter.setPen(QPen(QColor(colore)))
    x = r.left() + 8
    if prefisso:
        painter.setFont(mono)
        painter.drawText(QRectF(x, r.top(), w, 22), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         prefisso)
        x += fmm.horizontalAdvance(prefisso) + spazio
    painter.setFont(carattere)
    painter.drawText(QRectF(x, r.top(), w, 22), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, testo)


class _DelegatoBadge(QStyledItemDelegate):
    def _sfondo(self, painter: QPainter, option: QStyleOptionViewItem, index) -> QStyleOptionViewItem:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""
        stile = opt.widget.style() if opt.widget else QApplication.style()
        stile.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, opt.widget)
        return opt


class DelegatoLivello(_DelegatoBadge):
    """Colonna del livello P x D: il testo della cella è il prodotto; vuoto = «Non presente»."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        opt = self._sfondo(painter, option, index)
        valore = str(index.data(Qt.ItemDataRole.DisplayRole) or "").strip()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = correnti()
        if not valore.isdigit() or not int(valore):
            _badge(painter, QRectF(opt.rect), "Non presente", c["surface2"], c["tx3"])
        else:
            nome, sfondo, testo = LIVELLI_RISCHIO[_corrente["tema"]][livello(int(valore))]
            _badge(painter, QRectF(opt.rect), nome, sfondo, testo, prefisso=valore)
        painter.restore()

    def sizeHint(self, option, index) -> QSize:
        return QSize(130, 32)


class DelegatoGravita(_DelegatoBadge):
    """Interferenze: gravità nel riquadro colorato del rischio e, sotto, lo stato della prescrizione
    (testo della cella «gravità|stato»)."""

    COLORI_STATO = {"da scrivere": "warn", "generica": "tx3", "scritta": "ok"}

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        opt = self._sfondo(painter, option, index)
        gravita, _, stato = str(index.data(Qt.ItemDataRole.DisplayRole) or "").partition("|")
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = correnti()
        alto = QRectF(opt.rect.left(), opt.rect.top() + 2, opt.rect.width(), opt.rect.height() / 2)
        if gravita.isdigit() and int(gravita):
            nome, sfondo, testo = LIVELLI_RISCHIO[_corrente["tema"]][livello(int(gravita))]
            _badge(painter, alto, nome, sfondo, testo, prefisso=gravita)
        carattere = QFont(painter.font())
        carattere.setPixelSize(12)
        carattere.setWeight(QFont.Weight.DemiBold)
        painter.setFont(carattere)
        painter.setPen(QColor(c[self.COLORI_STATO.get(stato, "tx3")]))
        painter.drawText(QRectF(opt.rect.left() + 16, opt.rect.center().y() + 2, opt.rect.width() - 16,
                                opt.rect.height() / 2 - 4), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         stato)
        painter.restore()

    def sizeHint(self, option, index) -> QSize:
        return QSize(150, 52)


class DelegatoControllo(QStyledItemDelegate):
    """Voce «da sistemare»: etichetta Errore/Avviso, pagina, messaggio e «Vai alla pagina» a destra
    (dati della voce in UserRole + 1: livello, pagina, messaggio)."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        dati = index.data(Qt.ItemDataRole.UserRole + 1)
        if not dati:
            return super().paint(painter, option, index)
        livello_, pagina, messaggio = dati
        c = correnti()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(option.rect)
        if option.state & QStyle.StateFlag.State_MouseOver:
            painter.fillRect(r, QColor(c["surface2"]))
        errore = livello_.lower().startswith("err")
        nome = "Errore" if errore else "Avviso"
        sfondo, colore = (c["err_bg"], c["err"]) if errore else (c["warn_bg"], c["warn"])
        badge = QRectF(r.left(), r.top(), 92, r.height())
        _badge(painter, badge, nome, sfondo, colore)
        carattere = QFont(painter.font())
        carattere.setPixelSize(13)
        painter.setFont(carattere)
        fm = QFontMetrics(carattere)
        painter.setPen(QColor(c["tx2"]))
        x = r.left() + 96
        larghezza_pagina = 170
        painter.drawText(QRectF(x, r.top(), larghezza_pagina, r.height()), Qt.AlignmentFlag.AlignVCenter,
                         fm.elidedText(pagina, Qt.TextElideMode.ElideRight, larghezza_pagina - 8))
        link = "Vai alla pagina"
        larghezza_link = fm.horizontalAdvance(link) + 12
        painter.setPen(QColor(c["acc_s"]))
        painter.drawText(QRectF(r.right() - larghezza_link, r.top(), larghezza_link, r.height()),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, link)
        painter.setPen(QColor(c["tx"]))
        spazio = r.width() - (x - r.left()) - larghezza_pagina - larghezza_link - 12
        painter.drawText(QRectF(x + larghezza_pagina, r.top(), max(40.0, spazio), r.height()),
                         Qt.AlignmentFlag.AlignVCenter,
                         fm.elidedText(messaggio, Qt.TextElideMode.ElideRight, int(max(40.0, spazio))))
        painter.restore()

    def sizeHint(self, option, index) -> QSize:
        return QSize(400, 36)


class DelegatoStruttura(_DelegatoBadge):
    """Vista Struttura: per i rischi, livello nel riquadro colorato e valutazione in un secondo riquadro
    (UserRole = (livello, (testo, colore) o None)); per le altre righe il testo normale."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        dati = index.data(Qt.ItemDataRole.UserRole)
        if not dati:
            return super().paint(painter, option, index)
        opt = self._sfondo(painter, option, index)
        livello_, valutazione = dati
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        nome, sfondo, testo = LIVELLI_RISCHIO[_corrente["tema"]][livello(int(livello_))]
        rett = QRectF(opt.rect)
        _badge(painter, rett, nome, sfondo, testo, prefisso=str(livello_))
        if valutazione:
            esito, colore = valutazione
            c = correnti()
            sfondo_v, testo_v = {"verde": (c["ok_bg"], c["ok"]), "giallo": (c["warn_bg"], c["warn"])}.get(
                str(colore).lower(), (c["err_bg"], c["err"]))
            _badge(painter, QRectF(rett.left() + 120, rett.top(), rett.width() - 120, rett.height()),
                   f"valutazione: {esito}", sfondo_v, testo_v)
        painter.restore()


class DelegatoRisultato(_DelegatoBadge):
    """Risultato di una valutazione: testo «classe|indice|esito», vuoto = «Da eseguire»."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        opt = self._sfondo(painter, option, index)
        parti = str(index.data(Qt.ItemDataRole.DisplayRole) or "").split("|")
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = correnti()
        if len(parti) != 3 or parti[0] not in CLASSI_VALUTAZIONE["chiaro"]:
            _badge(painter, QRectF(opt.rect), "Da eseguire", c["warn_bg"], c["warn"])
        else:
            sfondo, testo = CLASSI_VALUTAZIONE[_corrente["tema"]][parti[0]]
            _badge(painter, QRectF(opt.rect), parti[2], sfondo, testo, prefisso=parti[1])
        painter.restore()


class DelegatoStato(_DelegatoBadge):
    """Stato scritto come etichetta colorata: `colori` associa al testo della cella le chiavi dei colori
    (sfondo, testo) del tema, per esempio {"Bozza": ("warn_bg", "warn")}."""

    def __init__(self, colori: dict[str, tuple[str, str]], genitore=None):
        super().__init__(genitore)
        self.colori = colori

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        opt = self._sfondo(painter, option, index)
        testo = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        if not testo:
            return
        c = correnti()
        sfondo, colore = self.colori.get(testo, ("surface2", "tx2"))
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        _badge(painter, QRectF(opt.rect), testo, c[sfondo], c[colore])
        painter.restore()

    def sizeHint(self, option, index) -> QSize:
        return QSize(110, 32)


class DelegatoNavigazione(QStyledItemDelegate):
    """Voce della barra laterale: cerchio numerato (o spunta), nome, contatore dei problemi.

    Dati della voce: DisplayRole = nome; UserRole = numero; UserRole + 1 = stato ("done",
    "error", "warning" o None); UserRole + 2 = numero di problemi.
    """

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        testo = opt.text
        opt.text = ""
        opt.icon = QIcon()
        stile = opt.widget.style() if opt.widget else QApplication.style()
        stile.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, opt.widget)

        c = correnti()
        selezionata = bool(opt.state & QStyle.StateFlag.State_Selected)
        attiva = bool(opt.state & QStyle.StateFlag.State_Enabled)
        numero = index.data(Qt.ItemDataRole.UserRole) or 0
        stato = index.data(Qt.ItemDataRole.UserRole + 1)
        problemi = index.data(Qt.ItemDataRole.UserRole + 2) or 0

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not attiva:
            painter.setOpacity(0.4)
        r = QRectF(opt.rect)
        cerchio = QRectF(r.left() + 10, r.center().y() - 12, 24, 24)
        if selezionata:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(c["acc_s"]))
            colore = c["acc_tx"]
        elif stato == "done":
            painter.setPen(QPen(QColor(c["ok"]), 1.5))
            painter.setBrush(QColor(c["ok_bg"]))
            colore = c["ok"]
        else:
            painter.setPen(QPen(QColor(c["line2"]), 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            colore = c["tx2"]
        painter.drawEllipse(cerchio.adjusted(0.75, 0.75, -0.75, -0.75))

        f = QFont(painter.font())
        f.setPixelSize(12)
        f.setWeight(QFont.Weight.DemiBold)
        painter.setFont(f)
        painter.setPen(QPen(QColor(colore), 2.2))
        if stato == "done" and not selezionata:
            cx, cy = cerchio.center().x(), cerchio.center().y()
            painter.drawPolyline([QPointF(cx - 5, cy + 0.5), QPointF(cx - 1.5, cy + 4), QPointF(cx + 5, cy - 3.5)])
        else:
            painter.drawText(cerchio, Qt.AlignmentFlag.AlignCenter, str(numero))

        f2 = QFont(painter.font())
        f2.setPixelSize(13)
        f2.setWeight(QFont.Weight.DemiBold if selezionata else QFont.Weight.Normal)
        painter.setFont(f2)
        painter.setPen(QColor(c["tx"]))
        con_contatore = stato in ("error", "warning") and problemi
        riserva = 34 if con_contatore else 8
        area = QRectF(cerchio.right() + 10, r.top(), r.right() - cerchio.right() - 10 - riserva, r.height())
        painter.drawText(area, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         QFontMetrics(f2).elidedText(testo, Qt.TextElideMode.ElideRight, int(area.width())))

        if con_contatore:
            sfondo, colore2 = (c["err_bg"], c["err"]) if stato == "error" else (c["warn_bg"], c["warn"])
            f3 = QFont(painter.font())
            f3.setPixelSize(11)
            f3.setWeight(QFont.Weight.DemiBold)
            painter.setFont(f3)
            w = QFontMetrics(f3).horizontalAdvance(str(problemi)) + 14
            pillola = QRectF(r.right() - w - 10, r.center().y() - 9, w, 18)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(sfondo))
            painter.drawRoundedRect(pillola, 9, 9)
            painter.setPen(QColor(colore2))
            painter.drawText(pillola, Qt.AlignmentFlag.AlignCenter, str(problemi))
        painter.restore()

    def sizeHint(self, option, index) -> QSize:
        return QSize(216, 42)


# --- impaginazione ricorrente ---

def stile_modulo(modulo) -> None:
    """Modulo con le etichette sopra i campi, piccole e in grassetto (QFormLayout)."""
    from PySide6.QtWidgets import QFormLayout, QLabel

    modulo.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
    modulo.setVerticalSpacing(10)
    for riga in range(modulo.rowCount()):
        voce = modulo.itemAt(riga, QFormLayout.ItemRole.LabelRole)
        etichetta = voce.widget() if voce is not None else None
        if isinstance(etichetta, QLabel) and not etichetta.objectName():
            etichetta.setObjectName("fieldLabel")


def cornice(titolo: str, contenuto, margini: tuple[int, int, int, int] = (14, 12, 14, 14)):
    """Riquadro con intestazione (titolo a sinistra) e il contenuto sotto; restituisce il riquadro.

    `contenuto` è un widget o un layout. Il layout dell'intestazione è `riquadro.intestazione`,
    per aggiungere pulsanti o note a destra del titolo.
    """
    from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLayout, QVBoxLayout

    riquadro = QFrame()
    riquadro.setObjectName("card")
    testa = QFrame()
    testa.setObjectName("cardHeader")
    riquadro.intestazione = QHBoxLayout(testa)
    riquadro.intestazione.setContentsMargins(14, 6, 12, 6)
    etichetta = QLabel(titolo)
    etichetta.setObjectName("cardTitle")
    riquadro.intestazione.addWidget(etichetta)
    riquadro.intestazione.addStretch()
    corpo = QVBoxLayout()
    corpo.setContentsMargins(*margini)
    if isinstance(contenuto, QLayout):
        corpo.addLayout(contenuto)
    else:
        corpo.addWidget(contenuto)
    layout = QVBoxLayout(riquadro)
    layout.setContentsMargins(1, 1, 1, 1)
    layout.setSpacing(0)
    layout.addWidget(testa)
    layout.addLayout(corpo, 1)
    return riquadro


def campo_con_etichetta(etichetta: str, campo):
    """Etichetta sopra il campo, per le griglie di campi."""
    from PySide6.QtWidgets import QLabel, QVBoxLayout

    colonna = QVBoxLayout()
    colonna.setSpacing(4)
    e = QLabel(etichetta)
    e.setObjectName("fieldLabel")
    e.setBuddy(campo)
    colonna.addWidget(e)
    colonna.addWidget(campo)
    return colonna


def numero_vuoto(campo, suggerimento: str = "") -> None:
    """Campo numerico che a zero appare vuoto (o con un suggerimento in grigio), allineato a destra:
    uno 0 scritto in partenza sembra un dato inserito."""
    campo.setSpecialValueText(suggerimento or " ")
    campo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def segna(*_args) -> None:
        vuoto = campo.value() == campo.minimum()
        if campo.property("vuoto") != vuoto:
            campo.setProperty("vuoto", vuoto)
            campo.style().unpolish(campo)
            campo.style().polish(campo)

    campo.valueChanged.connect(segna)
    segna()


class EvidenziaSpazi(QSyntaxHighlighter):
    """Evidenzia in giallo gli spazi da riempire scritti con i trattini bassi («attestato del ____»), come i
    dati da completare della bozza."""

    MODELLO = re.compile(r"_{2,}|\w_(?=\s|$)")

    def highlightBlock(self, testo: str) -> None:  # noqa: N802 - nome di Qt
        formato = QTextCharFormat()
        c = correnti()
        formato.setBackground(QColor("#FFE58A" if _corrente["tema"] == "chiaro" else "#5A4A00"))
        formato.setForeground(QColor(c["tx"]))
        for m in self.MODELLO.finditer(testo):
            self.setFormat(m.start(), m.end() - m.start(), formato)


def evidenzia_spazi(editor) -> None:
    editor._evidenzia = EvidenziaSpazi(editor.document())
