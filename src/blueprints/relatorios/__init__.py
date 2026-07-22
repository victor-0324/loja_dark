"""Blueprint de relatórios e análises"""
from flask import Blueprint

relatorios_bp = Blueprint('relatorios', __name__)

# Importar rotas para registrar
from src.blueprints.relatorios import routes  # noqa: F401
