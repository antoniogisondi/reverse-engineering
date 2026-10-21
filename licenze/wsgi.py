"""Punto di ingresso per gunicorn: gunicorn licenze.wsgi:app"""

from licenze.app import crea_app

app = crea_app()
