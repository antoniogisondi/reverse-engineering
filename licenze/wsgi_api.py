"""Punto di ingresso del server ponte AI per gunicorn: gunicorn licenze.wsgi_api:app

È l'unica parte del gestionale da rendere raggiungibile da internet (vedi README).
"""

from licenze.api import crea_api

app = crea_api()
