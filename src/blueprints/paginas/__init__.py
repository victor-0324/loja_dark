"""Blueprint de páginas HTML (dashboard, clientes, produtos, pedidos, etc)"""
from flask import Blueprint

paginas_bp = Blueprint('paginas', __name__)

# Importar rotas para registrar
from src.blueprints.paginas import routes  # noqa: F401
