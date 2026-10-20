import json
from types import SimpleNamespace

import pytest

from sicurcantiere.ai import ANTHROPIC, DEEPSEEK, OPENAI, URL_DEEPSEEK, AssistenteAI, ErroreAI, schema_metodo
from sicurcantiere.valutazioni import METODI


class ClientOpenAIFinto:
    """Simula client.chat.completions.create (OpenAI) registrando la richiesta."""

    def __init__(self, risposta, finish_reason="stop", refusal=None):
        self.risposta = risposta
        self.finish_reason = finish_reason
        self.refusal = refusal
        self.richieste = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.richieste.append(kwargs)
        testo = self.risposta if isinstance(self.risposta, str) else json.dumps(self.risposta)
        messaggio = SimpleNamespace(content=testo, refusal=self.refusal)
        return SimpleNamespace(choices=[SimpleNamespace(finish_reason=self.finish_reason, message=messaggio)])


class ClientFinto:
    """Simula client.beta.messages.create (Anthropic) registrando la richiesta."""

    def __init__(self, risposta, stop_reason="end_turn"):
        self.risposta = risposta
        self.stop_reason = stop_reason
        self.richieste = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.richieste.append(kwargs)
        testo = self.risposta if isinstance(self.risposta, str) else json.dumps(self.risposta)
        return SimpleNamespace(stop_reason=self.stop_reason,
                               content=[SimpleNamespace(type="text", text=testo)])


def test_schema_metodo_strutturato():
    schema = schema_metodo(METODI["niosh_composto"])
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])
    compito = schema["properties"]["compiti"]["items"]
    assert compito["properties"]["presa"]["enum"] == ["buona", "discreta", "scarsa"]
    assert compito["additionalProperties"] is False


def test_compila_valutazione_openai():
    client = ClientOpenAIFinto({
        "titolo": "Sacchi di cemento", "mansione": "Manovale", "lavoratori": "M18-45", "durata": "lunga",
        "peso": 25, "h": 45, "v": 10, "d": 90, "a": 45, "frequenza": 1.5, "presa": "scarsa",
        "ipotesi": ["Altezza di presa stimata: sacchi a terra"],
    })
    ai = AssistenteAI(fornitore=OPENAI, client=client)
    esito = ai.compila_valutazione(METODI["niosh"], "Il manovale carica sacchi da 25 kg in betoniera")
    assert esito.titolo == "Sacchi di cemento" and esito.dati["peso"] == 25
    assert esito.ipotesi == ["Altezza di presa stimata: sacchi a terra"]
    richiesta = client.richieste[0]
    assert richiesta["model"] == "gpt-5.5"
    formato = richiesta["response_format"]
    assert formato["type"] == "json_schema" and formato["json_schema"]["strict"] is True
    assert richiesta["messages"][0]["role"] == "system"
    assert "sacchi da 25 kg" in richiesta["messages"][1]["content"]
    # Il risultato è utilizzabile dal metodo.
    assert METODI["niosh"].esegui(esito.dati).indice > 1


def test_compila_valutazione_claude():
    client = ClientFinto({"titolo": "T", "mansione": "M", "lavoratori": "F18-45", "durata": "breve",
                          "peso": 5, "h": 25, "v": 75, "d": 25, "a": 0, "frequenza": 1, "presa": "buona",
                          "ipotesi": []})
    ai = AssistenteAI(fornitore=ANTHROPIC, client=client)
    esito = ai.compila_valutazione(METODI["niosh"], "Sollevamento di scatole leggere")
    assert esito.dati["lavoratori"] == "F18-45"
    richiesta = client.richieste[0]
    assert richiesta["model"] == "claude-opus-5-5" and richiesta["fallbacks"] == "default"
    assert richiesta["output_config"]["format"]["type"] == "json_schema"


def test_compila_valori_fuori_limite_normalizzati():
    client = ClientOpenAIFinto({"titolo": "", "mansione": "", "lavoratori": "sconosciuto", "durata": "lunga",
                          "peso": 500, "h": 30, "v": 75, "d": 30, "a": 0, "frequenza": 1,
                          "presa": "buona", "ipotesi": []})
    esito = AssistenteAI(client=client).compila_valutazione(METODI["niosh"], "x")
    assert esito.dati["peso"] == 100 and esito.dati["lavoratori"] == "M18-45"


def test_suggerisci_rischi_e_testi():
    client = ClientOpenAIFinto({"rischi": [
        {"descrizione": "Ribaltamento della piattaforma", "probabilita": 7, "danno": 4,
         "misure": "Stabilizzatori", "dpi": "Imbracatura"},
        {"descrizione": "  ", "probabilita": 1, "danno": 1, "misure": "", "dpi": ""},
    ]})
    rischi = AssistenteAI(client=client).suggerisci_rischi("Lavori in quota", ["PLE"], [])
    assert len(rischi) == 1 and rischi[0]["probabilita"] == 4
    client = ClientOpenAIFinto({"rischi": [
        {"descrizione": "Rumore", "probabilita": 3, "danno": 2, "misure": "Otoprotettori", "dpi": "",
         "fonte": "martello demolitore"},
        {"descrizione": "Polveri", "probabilita": 3, "danno": 2, "misure": "Bagnare", "dpi": "", "fonte": "boh"},
    ]})
    rischi = AssistenteAI(client=client).suggerisci_rischi("Demolizioni", ["Martello demolitore"], [])
    assert [r["fonte"] for r in rischi] == ["Martello demolitore", ""]
    assert "Vibrazioni al sistema mano-braccio" in json.dumps(client.richieste[0], ensure_ascii=False)
    testo = AssistenteAI(client=ClientOpenAIFinto({"testo": "Il cantiere è recintato."})).scrivi_sezione(
        "Organizzazione", "Scuola a Bari")
    assert testo == "Il cantiere è recintato."


def test_errori():
    with pytest.raises(ErroreAI, match="non ha potuto"):
        AssistenteAI(client=ClientOpenAIFinto({}, refusal="no")).scrivi_sezione("x", "y")
    with pytest.raises(ErroreAI, match="troncata"):
        AssistenteAI(client=ClientOpenAIFinto({}, finish_reason="length")).scrivi_sezione("x", "y")
    with pytest.raises(ErroreAI, match="non leggibile"):
        AssistenteAI(fornitore=OPENAI, client=ClientOpenAIFinto("non json")).scrivi_sezione("x", "y")
    with pytest.raises(ErroreAI, match="non ha potuto"):
        AssistenteAI(fornitore=ANTHROPIC, client=ClientFinto({}, stop_reason="refusal")).scrivi_sezione("x", "y")
    with pytest.raises(ErroreAI, match="troncata"):
        AssistenteAI(fornitore=ANTHROPIC, client=ClientFinto({}, stop_reason="max_tokens")).scrivi_sezione("x", "y")


def test_errore_chiave_openai_mancante(monkeypatch):
    # Senza chiave l'SDK OpenAI solleva un errore: deve diventare un messaggio comprensibile.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ErroreAI, match="non configurato|non valida"):
        AssistenteAI(fornitore=OPENAI).scrivi_sezione("x", "y")


def test_deepseek(monkeypatch):
    # DeepSeek è il predefinito: senza chiave un messaggio chiaro, con la chiave l'indirizzo DeepSeek.
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "chiave-openai-da-non-usare")
    assert AssistenteAI().fornitore == DEEPSEEK
    with pytest.raises(ErroreAI, match="DEEPSEEK_API_KEY"):
        AssistenteAI().scrivi_sezione("x", "y")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-prova")
    client = AssistenteAI().client
    assert str(client.base_url).startswith(URL_DEEPSEEK) and client.api_key == "sk-prova"

    finto = ClientOpenAIFinto({"testo": "Bozza della sezione"})
    assert AssistenteAI(client=finto).scrivi_sezione("Area", "Cantiere") == "Bozza della sezione"
    richiesta = finto.richieste[0]
    assert richiesta["model"] == "deepseek-flash" and richiesta["response_format"] == {"type": "json_object"}
    assert "json" in richiesta["messages"][0]["content"] and "json" in richiesta["messages"][1]["content"]
    # Modalità JSON senza schema garantito: le proprietà mancanti sono un errore comprensibile.
    with pytest.raises(ErroreAI, match="incompleta"):
        AssistenteAI(client=ClientOpenAIFinto({"altro": 1})).scrivi_sezione("x", "y")
    vuoto = ClientOpenAIFinto("")
    with pytest.raises(ErroreAI, match="vuota"):
        AssistenteAI(client=vuoto).scrivi_sezione("x", "y")
    assert len(vuoto.richieste) == 2  # un secondo tentativo prima di arrendersi


def test_estrai_sds():
    client = ClientOpenAIFinto({"nome": "Cemento", "produttore": "Alfa spa", "codici_h": "H315, H318",
                                "avvertenza": "Pericolo", "data_revisione": "2024-03-15", "stato_fisico": "polvere",
                                "dpi": "Guanti", "misure": "Evitare polveri", "conservazione": "Luogo asciutto"})
    dati = AssistenteAI(client=client).estrai_sds("SEZIONE 1 ... SEZIONE 16")
    assert dati["produttore"] == "Alfa spa" and dati["codici_h"] == "H315, H318"
    assert "SEZIONE 1" in client.richieste[0]["messages"][1]["content"]
