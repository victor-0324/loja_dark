"""
Application factory da SaaS VendeMais.
"""

import os
from flask import Flask, jsonify, redirect, request, url_for

from src.blueprints import register_blueprints
from src.config import ProductionConfig, config_by_name
from src.database import Base, DBConnectionHendler
from src.extensions import jwt, cors


def _requisicao_quer_html():
    """Detecta se a requisição veio de navegação de página (navegador) e não de uma chamada fetch/AJAX."""
    aceita = request.headers.get('Accept', '')
    return 'text/html' in aceita and not request.path.startswith('/api')


def create_app(config_name=None):
    """Cria e configura a instância Flask (application factory)."""
    app = Flask(__name__)

    # Carregar configuração
    config_name = config_name or os.getenv('APP_ENV')
    config_cls = config_by_name.get(config_name, config_by_name['default'])

    if config_cls is ProductionConfig:
        config_cls.validar()

    app.config.from_object(config_cls)


    # Extensões
    jwt.init_app(app)
    # cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    cors.init_app(
            app,
            origins=app.config['CORS_ORIGINS'],
            supports_credentials=True
        )

    @jwt.unauthorized_loader
    def token_ausente(motivo):
        if _requisicao_quer_html():
            return redirect(url_for('auth.login_page'))

        return jsonify({
            'erro': 'Não autorizado',
            'motivo': motivo
        }), 401

    @jwt.invalid_token_loader
    def token_invalido(motivo):
        if _requisicao_quer_html():
            return redirect(url_for('auth.login_page'))

        return jsonify({'erro': motivo}), 401

    @jwt.expired_token_loader
    def token_expirado(header, payload):
        if _requisicao_quer_html():
            return redirect(url_for('auth.login_page'))
        return jsonify({'erro': 'Token expirado', 'codigo': 401}), 401

    # Garante que todos os models sejam importados (registra em Base.metadata)
    from src import models  # noqa: F401

    # Conectar banco de dados
    db_handler = DBConnectionHendler(config_cls)
    with app.app_context():
        try:
            Base.metadata.create_all(bind=db_handler.get_engine())
            if app.config['DEBUG']:
                app.logger.info("✅ Banco sincronizado com sucesso.")
        except Exception as e:
            app.logger.error(f"❌ Erro ao sincronizar banco: {e}")

    # Libera a sessão do SQLAlchemy ao fim de cada request
    @app.teardown_appcontext
    def remover_sessao(exception=None):
        db_handler.remove_session()

    # Registrar blueprints
    register_blueprints(app)

    # Error handlers
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'erro': 'Não autorizado', 'codigo': 401}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'erro': 'Acesso proibido', 'codigo': 403}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'erro': 'Endpoint não encontrado', 'codigo': 404}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'erro': 'Erro interno do servidor', 'codigo': 500}), 500

    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'version': '2.0.0'}), 200

    # Root
    @app.route('/api', methods=['GET'])
    def api_root():
        return jsonify({
            'nome': 'VendeMais API',
            'versao': '2.0.0',
            'endpoints': {
                'clientes': '/api/clientes',
                'produtos': '/api/produtos',
                'pedidos': '/api/pedidos',
                'relatorios': '/api/relatorios',
            }
        }), 200

    return app
