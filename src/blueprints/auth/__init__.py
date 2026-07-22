"""Blueprint de autenticação"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# Importar rotas para registrar
from src.blueprints.auth import routes  # noqa: F401
