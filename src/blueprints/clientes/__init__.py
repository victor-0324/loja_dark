"""Blueprint de clientes"""
from flask import Blueprint

clientes_bp = Blueprint('clientes', __name__)

from src.blueprints.clientes import routes  # noqa: F401
