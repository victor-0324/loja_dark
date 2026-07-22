"""
Extensões Flask: JWT, CORS, Cache, etc.
Inicializadas sem app (para application factory pattern).
"""

from flask_jwt_extended import JWTManager
from flask_cors import CORS


# JWT Extended
jwt = JWTManager()

# CORS
cors = CORS()


def init_extensions(app):
    """Inicializa todas as extensões com a aplicação"""
    jwt.init_app(app)
    cors.init_app(app, origins=app.config.get('CORS_ORIGINS', ['*']))
