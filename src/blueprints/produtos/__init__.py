"""Blueprint de produtos"""
from flask import Blueprint

produtos_bp = Blueprint('produtos', __name__)

from src.blueprints.produtos import routes  # noqa: F401
