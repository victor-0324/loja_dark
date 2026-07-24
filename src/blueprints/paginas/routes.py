"""Rotas de páginas HTML (dashboard, etc)"""

from flask import render_template, redirect, url_for, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from src.blueprints.paginas import paginas_bp
from src.database import DBConnectionHendler
from src.models import Cliente, Pedido, Produto
db_handler = DBConnectionHendler()


# Página inicial / Login
@paginas_bp.route('/', methods=['GET'])
def index():
    """Página inicial"""
    return render_template('index.html')


# Dashboard
@paginas_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """Dashboard da loja"""

    claims = get_jwt()
    session = db_handler.get_session()

    try:
        # Dados para o dashboard
        total_clientes = session.query(Cliente).filter_by(loja_id=claims['loja_id']).count()
        total_produtos = session.query(Produto).filter_by(loja_id=claims['loja_id'], ativo=True).count()
        total_pedidos = session.query(Pedido).filter_by(loja_id=claims['loja_id']).count()
        valor_total_vendas = sum(p.valor_total for p in session.query(Pedido).filter_by(loja_id=claims['loja_id']).all())

        return render_template(
            'dashboard.html',
            total_clientes=total_clientes,
            total_produtos=total_produtos,
            total_pedidos=total_pedidos,
            valor_total_vendas=valor_total_vendas,
            active='dashboard'
        )

    finally:
        db_handler.remove_session()


# Clientes
@paginas_bp.route('/clientes', methods=['GET'])
@jwt_required()
def clientes():
    """Página de clientes"""
    return render_template('clientes.html', active='clientes')


# Detalhes do cliente
@paginas_bp.route('/cliente/<int:cliente_id>', methods=['GET'])
@jwt_required()
def detalhes_cliente(cliente_id):
    """Página de detalhes do cliente"""

    return render_template('cliente_detalhes.html', cliente_id=cliente_id, active='clientes')


# Produtos
@paginas_bp.route('/produtos', methods=['GET'])
@jwt_required()
def produtos():
    """Página de produtos"""
    return render_template('produtos.html', active='produtos')


# Pedidos
@paginas_bp.route('/pedidos', methods=['GET'])
@jwt_required()
def pedidos():
    """Página de pedidos"""
    return render_template('pedidos.html', active='pedidos')


# Relatórios
@paginas_bp.route('/relatorios', methods=['GET'])
@jwt_required()
def relatorios():
    """Página de relatórios"""
    return render_template('relatorios.html', active='relatorios')


# Configurações
@paginas_bp.route('/configuracoes', methods=['GET'])
@jwt_required()
def configuracoes():
    """Página de configurações"""
    return render_template('configuracoes.html', active='configuracoes')
