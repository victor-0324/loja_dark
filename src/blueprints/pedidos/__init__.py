"""Blueprint de pedidos"""
from flask import Blueprint

pedidos_bp = Blueprint('pedidos', __name__)

from src.blueprints.pedidos import routes  # noqa: F401
