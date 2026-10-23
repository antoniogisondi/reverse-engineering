"""Licenze dei programmi SicurCantiere: modulo comune a tutti i programmi della suite e al server.

Come funziona, in breve:

1. il cliente inserisce il codice di licenza (chiave di attivazione);
2. il programma calcola l'impronta del PC (`impronta`): tre hash, mai i dati dell'hardware in chiaro;
3. il server delle licenze controlla licenza, scadenza, revoca e posti liberi e restituisce un
   certificato firmato (`certificato`), valido pochi giorni e legato a quel PC;
4. il programma conserva il certificato cifrato (`custodia`), lo verifica a ogni avvio senza
   internet e lo rinnova in sottofondo (`cliente`);
5. `stato` decide cosa si può fare: tutto, oppure sola lettura (aprire, stampare, esportare in PDF)
   con il motivo e cosa fare. I dati dell'utente non si bloccano mai.

Firme a due livelli: la chiave radice (quella del gestionale, che i programmi conoscono già) firma
ogni tanto una chiave di servizio; il server pubblico ha solo la chiave di servizio e con quella
firma i certificati. Se il server venisse violato basta sostituire la chiave di servizio.

Nessuna dipendenza da Qt né da librerie compilate: la verifica usa l'Ed25519 in Python puro.
"""

from sicur_license.certificato import Certificato, ErroreCertificato, leggi_certificato
from sicur_license.stato import Esito, valuta

__all__ = ["Certificato", "ErroreCertificato", "Esito", "leggi_certificato", "valuta"]
