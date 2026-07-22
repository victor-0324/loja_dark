"""Rotas completas de gestão de pedidos com rastreamento e integração."""

from flask import jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from datetime import datetime, timedelta
from sqlalchemy import or_, desc, asc

from src.blueprints.pedidos import pedidos_bp
from src.database import DBConnectionHendler
from src.models import Pedido, ItemPedido, Cliente, Produto, HistoricoStatusPedido, StatusPedido

db_handler = DBConnectionHendler()


def formatar_resposta_erro(mensagem, codigo=400):
    """Formata resposta de erro padrão"""
    return jsonify({'erro': mensagem, 'codigo': codigo}), codigo


def formatar_resposta_sucesso(dados=None, mensagem='Sucesso', codigo=200):
    """Formata resposta de sucesso padrão"""
    resposta = {'mensagem': mensagem}
    if dados is not None:
        resposta['dados'] = dados
    return jsonify(resposta), codigo


def gerar_numero_pedido(loja_id, session):
    """Gera um número de pedido único"""
    ano_atual = datetime.utcnow().year
    numero_sequencial = session.query(Pedido).filter(
        Pedido.loja_id == loja_id,
        Pedido.numero_pedido.like(f'PED-{ano_atual}%')
    ).count() + 1
    return f'PED-{ano_atual}-{numero_sequencial:05d}'


def registrar_mudanca_status(pedido, status_novo, session, motivo='', observacoes=''):
    """Registra mudança de status do pedido"""
    historico = HistoricoStatusPedido(
        pedido_id=pedido.id,
        status_anterior=pedido.status,
        status_novo=status_novo,
        motivo=motivo,
        observacoes=observacoes
    )
    session.add(historico)


# ============================================================================
# LISTAR PEDIDOS
# ============================================================================

@pedidos_bp.route('', methods=['GET'])
@jwt_required()
def listar_pedidos():
    """
    Lista pedidos com filtros, paginação e pesquisa.
    
    Query params:
    - pagina: número da página (padrão: 1)
    - por_pagina: itens por página (padrão: 20, máximo: 100)
    - pesquisa: busca por número do pedido, email ou CPF do cliente
    - status: filtro por status
    - metodo_pagamento: filtro por método
    - data_inicio: filtro por data (YYYY-MM-DD)
    - data_fim: filtro por data (YYYY-MM-DD)
    - ordenar_por: numero_pedido, data_pedido, valor_total
    - ordem: asc ou desc
    """
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        # Parâmetros
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = min(request.args.get('por_pagina', 20, type=int), 100)
        pesquisa = request.args.get('pesquisa', '').strip()
        status = request.args.get('status', '').strip()
        metodo_pagamento = request.args.get('metodo_pagamento', '').strip()
        data_inicio = request.args.get('data_inicio', '').strip()
        data_fim = request.args.get('data_fim', '').strip()
        ordenar_por = request.args.get('ordenar_por', 'data_pedido')
        ordem = request.args.get('ordem', 'desc')

        # Query base
        query = session.query(Pedido).filter_by(loja_id=claims['loja_id'])

        # Pesquisa
        if pesquisa:
            query = query.join(Cliente).filter(or_(
                Pedido.numero_pedido.ilike(f'%{pesquisa}%'),
                Cliente.email.ilike(f'%{pesquisa}%'),
                Cliente.cpf_cnpj.ilike(f'%{pesquisa}%'),
                Pedido.codigo_rastreamento.ilike(f'%{pesquisa}%')
            ))

        # Filtros
        if status and status in StatusPedido.TODOS:
            query = query.filter_by(status=status)

        if metodo_pagamento:
            query = query.filter_by(metodo_pagamento=metodo_pagamento)

        # Filtro de data
        if data_inicio:
            data_inicio_obj = datetime.fromisoformat(data_inicio)
            query = query.filter(Pedido.data_pedido >= data_inicio_obj)

        if data_fim:
            data_fim_obj = datetime.fromisoformat(data_fim) + timedelta(days=1)
            query = query.filter(Pedido.data_pedido < data_fim_obj)

        # Ordenação
        ordem_obj = desc if ordem == 'desc' else asc
        if ordenar_por == 'numero_pedido':
            query = query.order_by(ordem_obj(Pedido.numero_pedido))
        elif ordenar_por == 'valor_total':
            query = query.order_by(ordem_obj(Pedido.valor_total))
        else:
            query = query.order_by(ordem_obj(Pedido.data_pedido))

        # Total
        total = query.count()

        # Paginação
        offset = (pagina - 1) * por_pagina
        pedidos = query.offset(offset).limit(por_pagina).all()

        # Montar resposta
        dados = {
            'pedidos': [p.to_dict() for p in pedidos],
            'paginacao': {
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'total_paginas': (total + por_pagina - 1) // por_pagina
            }
        }

        return jsonify(dados), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao listar pedidos: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# CRIAR PEDIDO
# ============================================================================

@pedidos_bp.route('', methods=['POST'])
@jwt_required()
def criar_pedido():
    """Cria um novo pedido"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        dados = request.get_json() or {}

        # Validações
        if not dados.get('cliente_id'):
            return formatar_resposta_erro('Cliente é obrigatório')
        if not dados.get('itens') or len(dados['itens']) == 0:
            return formatar_resposta_erro('Pedido deve ter pelo menos um item')

        # Verificar cliente
        cliente = session.query(Cliente).filter_by(
            id=dados['cliente_id'],
            loja_id=claims['loja_id']
        ).first()
        if not cliente:
            return formatar_resposta_erro('Cliente não encontrado')

        # Criar pedido
        numero_pedido = gerar_numero_pedido(claims['loja_id'], session)
        
        subtotal = 0
        itens_pedido = []

        # Processar itens
        for item_dados in dados['itens']:
            produto = session.query(Produto).filter_by(
                id=item_dados['produto_id'],
                loja_id=claims['loja_id']
            ).first()
            if not produto:
                return formatar_resposta_erro(f'Produto {item_dados["produto_id"]} não encontrado')

            quantidade = int(item_dados.get('quantidade', 1))
            if quantidade <= 0:
                return formatar_resposta_erro('Quantidade deve ser maior que 0')

            if quantidade > produto.estoque_disponivel:
                return formatar_resposta_erro(f'Estoque insuficiente para {produto.nome}')

            preco_unitario = float(item_dados.get('preco_unitario', produto.preco))
            desconto_item = float(item_dados.get('desconto_item', 0))

            item = ItemPedido(
                produto_id=produto.id,
                produto_nome=produto.nome,
                produto_sku=produto.sku,
                tamanho=item_dados.get('tamanho'),
                cor=item_dados.get('cor'),
                quantidade=quantidade,
                preco_unitario=preco_unitario,
                desconto_item=desconto_item
            )

            itens_pedido.append(item)
            subtotal += item.subtotal

            # Reservar estoque
            produto.estoque_reservado += quantidade

        # Calcular totais
        desconto = float(dados.get('desconto', 0))
        taxa_envio = float(dados.get('taxa_envio', 0))
        taxa_servico = float(dados.get('taxa_servico', 0))
        valor_total = subtotal - desconto + taxa_envio + taxa_servico

        # Criar pedido
        pedido = Pedido(
            loja_id=claims['loja_id'],
            cliente_id=cliente.id,
            numero_pedido=numero_pedido,
            subtotal=subtotal,
            desconto=desconto,
            taxa_envio=taxa_envio,
            taxa_servico=taxa_servico,
            valor_total=valor_total,
            status=StatusPedido.PENDENTE,
            metodo_pagamento=dados.get('metodo_pagamento'),
            status_pagamento='pendente',
            endereco_entrega=dados.get('endereco_entrega') or cliente.endereco,
            numero_entrega=dados.get('numero_entrega') or cliente.numero,
            complemento_entrega=dados.get('complemento_entrega') or cliente.complemento,
            cidade_entrega=dados.get('cidade_entrega') or cliente.cidade,
            estado_entrega=dados.get('estado_entrega') or cliente.estado,
            cep_entrega=dados.get('cep_entrega') or cliente.cep,
            transportadora=dados.get('transportadora'),
            tipo_envio=dados.get('tipo_envio', 'normal'),
            cupom_codigo=dados.get('cupom_codigo'),
            observacoes=dados.get('observacoes'),
            presente=dados.get('presente', False),
            msg_presente=dados.get('msg_presente'),
        )

        for item in itens_pedido:
            pedido.itens.append(item)

        session.add(pedido)
        session.flush()  # garante que pedido.id já existe antes de registrar o histórico

        # Registrar no histórico
        registrar_mudanca_status(pedido, StatusPedido.PENDENTE, session, 'Pedido criado')

        # Atualizar dados do cliente
        if not cliente.data_primeira_compra:
            cliente.data_primeira_compra = datetime.utcnow()

        session.commit()

        return formatar_resposta_sucesso(
            pedido.to_dict(),
            'Pedido criado com sucesso',
            201
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao criar pedido: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# OBTER DETALHES DO PEDIDO
# ============================================================================

@pedidos_bp.route('/<int:pedido_id>', methods=['GET'])
@jwt_required()
def obter_pedido(pedido_id):
    """Obtém detalhes completos de um pedido"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        pedido = session.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.loja_id == claims['loja_id']
        ).first()

        if not pedido:
            return formatar_resposta_erro('Pedido não encontrado', 404)

        dados = pedido.to_dict_completo()
        dados['historico_status'] = [h.to_dict() for h in pedido.historico_status]

        return jsonify(dados), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao obter pedido: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# ATUALIZAR STATUS DO PEDIDO
# ============================================================================

@pedidos_bp.route('/<int:pedido_id>/status', methods=['PATCH'])
@jwt_required()
def atualizar_status_pedido(pedido_id):
    """Atualiza o status de um pedido"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        pedido = session.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.loja_id == claims['loja_id']
        ).first()

        if not pedido:
            return formatar_resposta_erro('Pedido não encontrado', 404)

        dados = request.get_json() or {}
        novo_status = dados.get('status')
        motivo = dados.get('motivo', '')

        if not novo_status or novo_status not in StatusPedido.TODOS:
            return formatar_resposta_erro('Status inválido')

        # Validar transição de status
        if pedido.status == StatusPedido.CANCELADO:
            return formatar_resposta_erro('Pedido cancelado não pode ser alterado')

        status_anterior = pedido.status
        pedido.status = novo_status

        # Atualizar datas conforme o status
        if novo_status == StatusPedido.CONFIRMADO:
            pedido.data_confirmacao = datetime.utcnow()
        elif novo_status == StatusPedido.PROCESSANDO:
            pedido.data_processamento = datetime.utcnow()
        elif novo_status == StatusPedido.DESPACHADO or novo_status == StatusPedido.ENVIADO:
            pedido.data_despacho = datetime.utcnow()
            pedido.data_envio = datetime.utcnow()
        elif novo_status == StatusPedido.ENTREGUE:
            pedido.data_entrega_realizada = datetime.utcnow()
        elif novo_status == StatusPedido.CANCELADO:
            pedido.motivo_cancelamento = dados.get('motivo', '')
            # Liberar estoque
            for item in pedido.itens:
                produto = item.produto
                produto.estoque_reservado = max(0, produto.estoque_reservado - item.quantidade)

        # Registrar mudança
        registrar_mudanca_status(pedido, novo_status, session, motivo, dados.get('observacoes', ''))

        session.commit()

        return formatar_resposta_sucesso(
            pedido.to_dict(),
            'Status do pedido atualizado com sucesso'
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao atualizar status: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# CONFIRMAR PAGAMENTO
# ============================================================================

@pedidos_bp.route('/<int:pedido_id>/pagamento', methods=['PATCH'])
@jwt_required()
def confirmar_pagamento(pedido_id):
    """Confirma o pagamento de um pedido"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        pedido = session.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.loja_id == claims['loja_id']
        ).first()

        if not pedido:
            return formatar_resposta_erro('Pedido não encontrado', 404)

        dados = request.get_json() or {}

        pedido.status_pagamento = dados.get('status_pagamento', 'aprovado')
        pedido.data_pagamento = datetime.utcnow()
        pedido.numero_transacao = dados.get('numero_transacao')

        # Se aprovado, mover para confirmado
        if pedido.status_pagamento == 'aprovado':
            if pedido.status == StatusPedido.PENDENTE:
                pedido.status = StatusPedido.CONFIRMADO
                pedido.data_confirmacao = datetime.utcnow()
                registrar_mudanca_status(pedido, StatusPedido.CONFIRMADO, session, 'Pagamento aprovado')

        session.commit()

        return formatar_resposta_sucesso(
            pedido.to_dict(),
            'Pagamento registrado com sucesso'
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao registrar pagamento: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# CANCELAR PEDIDO
# ============================================================================

@pedidos_bp.route('/<int:pedido_id>/cancelar', methods=['POST'])
@jwt_required()
def cancelar_pedido(pedido_id):
    """Cancela um pedido"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        pedido = session.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.loja_id == claims['loja_id']
        ).first()

        if not pedido:
            return formatar_resposta_erro('Pedido não encontrado', 404)

        if not pedido.pode_ser_cancelado():
            return formatar_resposta_erro('Pedido não pode ser cancelado neste status')

        dados = request.get_json() or {}
        motivo = dados.get('motivo', 'Cancelado pelo sistema')

        # Liberar estoque
        for item in pedido.itens:
            produto = item.produto
            produto.estoque_reservado = max(0, produto.estoque_reservado - item.quantidade)

        pedido.status = StatusPedido.CANCELADO
        pedido.motivo_cancelamento = motivo

        registrar_mudanca_status(pedido, StatusPedido.CANCELADO, session, motivo)

        session.commit()

        return formatar_resposta_sucesso(
            pedido.to_dict(),
            'Pedido cancelado com sucesso'
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao cancelar pedido: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# DEVOLUÇÃO DE PEDIDO
# ============================================================================

@pedidos_bp.route('/<int:pedido_id>/devolucao', methods=['POST'])
@jwt_required()
def registrar_devolucao(pedido_id):
    """Registra uma devolução de pedido"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        pedido = session.query(Pedido).filter(
            Pedido.id == pedido_id,
            Pedido.loja_id == claims['loja_id']
        ).first()

        if not pedido:
            return formatar_resposta_erro('Pedido não encontrado', 404)

        if not pedido.pode_ser_devolvido():
            return formatar_resposta_erro('Pedido não pode ser devolvido neste status')

        dados = request.get_json() or {}

        pedido.devolvido = True
        pedido.data_devolucao = datetime.utcnow()
        pedido.motivo_devolucao = dados.get('motivo', '')
        pedido.valor_reembolso = dados.get('valor_reembolso', pedido.valor_total)
        pedido.status = StatusPedido.DEVOLVIDO

        registrar_mudanca_status(pedido, StatusPedido.DEVOLVIDO, session, 'Devolução registrada')

        session.commit()

        return formatar_resposta_sucesso(
            pedido.to_dict(),
            'Devolução registrada com sucesso'
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao registrar devolução: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# ESTATÍSTICAS DE PEDIDOS
# ============================================================================

@pedidos_bp.route('/estatisticas/resumo', methods=['GET'])
@jwt_required()
def estatisticas_pedidos():
    """Retorna estatísticas gerais de pedidos"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        # Períodos
        hoje = datetime.utcnow().date()
        inicio_mes = (hoje.year, hoje.month, 1)
        data_mes = datetime(inicio_mes[0], inicio_mes[1], inicio_mes[2])
        data_ano = datetime(hoje.year, 1, 1)

        # Queries
        total_geral = session.query(Pedido).filter_by(loja_id=claims['loja_id']).count()
        total_mes = session.query(Pedido).filter(
            Pedido.loja_id == claims['loja_id'],
            Pedido.data_pedido >= data_mes
        ).count()
        total_ano = session.query(Pedido).filter(
            Pedido.loja_id == claims['loja_id'],
            Pedido.data_pedido >= data_ano
        ).count()

        # Por status
        por_status = {}
        for status in StatusPedido.TODOS:
            por_status[status] = session.query(Pedido).filter_by(
                loja_id=claims['loja_id'],
                status=status
            ).count()

        # Valores
        valor_total = sum(p.valor_total for p in session.query(Pedido).filter_by(
            loja_id=claims['loja_id']
        ).all())
        valor_mes = sum(p.valor_total for p in session.query(Pedido).filter(
            Pedido.loja_id == claims['loja_id'],
            Pedido.data_pedido >= data_mes
        ).all())

        estatisticas = {
            'total_pedidos': {
                'geral': total_geral,
                'mes': total_mes,
                'ano': total_ano,
            },
            'por_status': por_status,
            'valores': {
                'valor_total': valor_total,
                'valor_mes': valor_mes,
            }
        }

        return jsonify(estatisticas), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao obter estatísticas: {str(e)}', 500)
    finally:
        db_handler.remove_session()
