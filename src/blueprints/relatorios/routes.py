"""Rotas de relatórios e análises"""

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import func

from src.blueprints.relatorios import relatorios_bp
from src.database import DBConnectionHendler
from src.models import Cliente, Pedido, Produto, ItemPedido

db_handler = DBConnectionHendler()


@relatorios_bp.route('/resumo', methods=['GET'])
@jwt_required()
def resumo():
    """Retorna resumo de vendas e métricas principais"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        # Períodos
        hoje = datetime.utcnow().date()
        data_mes = datetime(hoje.year, hoje.month, 1)
        data_ano = datetime(hoje.year, 1, 1)
        data_30_dias = datetime.utcnow() - timedelta(days=30)

        # Totais
        total_clientes = session.query(Cliente).filter_by(
            loja_id=claims['loja_id']
        ).count()

        total_pedidos = session.query(Pedido).filter_by(
            loja_id=claims['loja_id']
        ).count()

        # Vendas
        todas_vendas = session.query(func.sum(Pedido.valor_total)).filter_by(
            loja_id=claims['loja_id']
        ).scalar() or 0

        vendas_mes = session.query(func.sum(Pedido.valor_total)).filter(
            Pedido.loja_id == claims['loja_id'],
            Pedido.data_pedido >= data_mes
        ).scalar() or 0

        vendas_ano = session.query(func.sum(Pedido.valor_total)).filter(
            Pedido.loja_id == claims['loja_id'],
            Pedido.data_pedido >= data_ano
        ).scalar() or 0

        vendas_30_dias = session.query(func.sum(Pedido.valor_total)).filter(
            Pedido.loja_id == claims['loja_id'],
            Pedido.data_pedido >= data_30_dias
        ).scalar() or 0

        # Produto mais vendido
        produto_mais_vendido = session.query(
            Produto.nome,
            func.sum(ItemPedido.quantidade).label('total_vendido')
        ).join(
            ItemPedido
        ).filter(
            Produto.loja_id == claims['loja_id']
        ).group_by(Produto.id).order_by(
            func.sum(ItemPedido.quantidade).desc()
        ).first()

        # Cliente que mais gastou
        cliente_maior_gasto = session.query(
            Cliente.nome,
            func.sum(Pedido.valor_total).label('total_gasto')
        ).join(
            Pedido
        ).filter(
            Cliente.loja_id == claims['loja_id']
        ).group_by(Cliente.id).order_by(
            func.sum(Pedido.valor_total).desc()
        ).first()

        resumo = {
            'clientes': {
                'total': total_clientes
            },
            'pedidos': {
                'total': total_pedidos
            },
            'vendas': {
                'total': float(todas_vendas),
                'mes': float(vendas_mes),
                'ano': float(vendas_ano),
                'ultimos_30_dias': float(vendas_30_dias)
            },
            'produto_mais_vendido': {
                'nome': produto_mais_vendido[0] if produto_mais_vendido else None,
                'quantidade': int(produto_mais_vendido[1]) if produto_mais_vendido else 0
            } if produto_mais_vendido else None,
            'cliente_maior_gasto': {
                'nome': cliente_maior_gasto[0] if cliente_maior_gasto else None,
                'valor_total': float(cliente_maior_gasto[1]) if cliente_maior_gasto else 0
            } if cliente_maior_gasto else None
        }

        return jsonify(resumo), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        db_handler.remove_session()


@relatorios_bp.route('/vendas-por-periodo', methods=['GET'])
@jwt_required()
def vendas_por_periodo():
    """Vendas agrupadas por período (dia, semana, mês)"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        periodo = request.args.get('periodo', 'mes')  # dia, semana, mês

        # Últimos 12 meses
        data_inicio = datetime.utcnow() - timedelta(days=365)

        pedidos = session.query(Pedido).filter(
            Pedido.loja_id == claims['loja_id'],
            Pedido.data_pedido >= data_inicio
        ).all()

        # Agrupar por período
        dados = {}
        for pedido in pedidos:
            if periodo == 'dia':
                chave = pedido.data_pedido.strftime('%Y-%m-%d')
            elif periodo == 'semana':
                chave = pedido.data_pedido.strftime('%Y-W%W')
            else:  # mês
                chave = pedido.data_pedido.strftime('%Y-%m')

            if chave not in dados:
                dados[chave] = 0
            dados[chave] += pedido.valor_total

        return jsonify({
            'periodo': periodo,
            'dados': sorted(dados.items())
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        db_handler.remove_session()


@relatorios_bp.route('/produtos-populares', methods=['GET'])
@jwt_required()
def produtos_populares():
    """Produtos mais vendidos"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        limite = request.args.get('limite', 10, type=int)

        produtos = session.query(
            Produto.id,
            Produto.nome,
            func.sum(ItemPedido.quantidade).label('total_vendido'),
            func.sum(ItemPedido.quantidade * ItemPedido.preco_unitario).label('valor_total')
        ).join(
            ItemPedido
        ).filter(
            Produto.loja_id == claims['loja_id']
        ).group_by(Produto.id).order_by(
            func.sum(ItemPedido.quantidade).desc()
        ).limit(limite).all()

        return jsonify({
            'produtos': [
                {
                    'id': p[0],
                    'nome': p[1],
                    'total_vendido': int(p[2]),
                    'valor_total': float(p[3])
                }
                for p in produtos
            ]
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        db_handler.remove_session()


@relatorios_bp.route('/clientes-vip', methods=['GET'])
@jwt_required()
def clientes_vip():
    """Clientes com maior valor de compras"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        limite = request.args.get('limite', 10, type=int)

        clientes = session.query(
            Cliente.id,
            Cliente.nome,
            Cliente.email,
            func.count(Pedido.id).label('total_pedidos'),
            func.sum(Pedido.valor_total).label('valor_total')
        ).outerjoin(
            Pedido
        ).filter(
            Cliente.loja_id == claims['loja_id']
        ).group_by(Cliente.id).order_by(
            func.sum(Pedido.valor_total).desc()
        ).limit(limite).all()

        return jsonify({
            'clientes': [
                {
                    'id': c[0],
                    'nome': c[1],
                    'email': c[2],
                    'total_pedidos': int(c[3]),
                    'valor_total': float(c[4])
                }
                for c in clientes if c[4]
            ]
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        db_handler.remove_session()


@relatorios_bp.route('/estoque', methods=['GET'])
@jwt_required()
def relatorio_estoque():
    """Relatório de estoque"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        produtos = session.query(Produto).filter_by(
            loja_id=claims['loja_id'],
            ativo=True
        ).all()

        return jsonify({
            'total_produtos': len(produtos),
            'estoque_total_unidades': sum(p.estoque_total for p in produtos),
            'estoque_baixo': [
                p.to_dict(include_estoque=True)
                for p in produtos if p.estoque_baixo
            ],
            'sem_estoque': [
                p.to_dict(include_estoque=True)
                for p in produtos if not p.em_estoque
            ]
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        db_handler.remove_session()
