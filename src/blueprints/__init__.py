"""
Registro de todos os blueprints da aplicação.
"""

from flask import Blueprint


def register_blueprints(app):
    """Registra todos os blueprints na aplicação"""
    
    # Importar blueprints
    from src.blueprints.auth import auth_bp
    from src.blueprints.clientes import clientes_bp
    from src.blueprints.produtos import produtos_bp
    from src.blueprints.pedidos import pedidos_bp
    from src.blueprints.paginas import paginas_bp
    from src.blueprints.relatorios import relatorios_bp
    
    # Registrar blueprints
    app.register_blueprint(paginas_bp)  # Sem prefixo (home, dashboard)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(clientes_bp, url_prefix='/api/clientes')
    app.register_blueprint(produtos_bp, url_prefix='/api/produtos')
    app.register_blueprint(pedidos_bp, url_prefix='/api/pedidos')
    app.register_blueprint(relatorios_bp, url_prefix='/api/relatorios')
