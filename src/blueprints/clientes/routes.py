"""Rotas completas de gestão de clientes com CRM integrado."""

from flask import jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, desc, asc, func
import re

from src.blueprints.clientes import clientes_bp
from src.database import DBConnectionHendler
from src.models import (
    Cliente, Loja, Pedido, Interacao, Atendimento, CampanhaRecebida,
    CupomCliente, ProdutoFavorito, PreferenciaCliente
)

db_handler = DBConnectionHendler()


def validar_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_cpf_cnpj(cpf_cnpj):
    """Validação básica de CPF/CNPJ"""
    if not cpf_cnpj:
        return True
    # Remove caracteres especiais
    apenas_numeros = re.sub(r'\D', '', cpf_cnpj)
    return len(apenas_numeros) in [11, 14]  # CPF tem 11, CNPJ tem 14


def formatar_resposta_erro(mensagem, codigo=400):
    """Formata resposta de erro padrão"""
    return jsonify({'erro': mensagem, 'codigo': codigo}), codigo


def formatar_resposta_sucesso(dados=None, mensagem='Sucesso', codigo=200):
    """Formata resposta de sucesso padrão"""
    resposta = {'mensagem': mensagem}
    if dados is not None:
        resposta['dados'] = dados
    return jsonify(resposta), codigo


# ============================================================================
# LISTAR CLIENTES COM FILTROS, PAGINAÇÃO E PESQUISA
# ============================================================================

@clientes_bp.route('', methods=['GET'])
@jwt_required()
def listar_clientes():
    """
    Lista clientes com filtros, paginação e pesquisa.

    Query params:
    - pagina: número da página (padrão: 1)
    - por_pagina: itens por página (padrão: 20, máximo: 100)
    - pesquisa: busca por nome, email, telefone ou CPF
    - status: filtro por status (novo, ativo, vip, inativo)
    - origem: filtro por origem do cliente
    - cidade: filtro por cidade
    - ordenar_por: campo para ordenação (nome, data_criacao, valor_total_gasto)
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
        origem = request.args.get('origem', '').strip()
        cidade = request.args.get('cidade', '').strip()
        ordenar_por = request.args.get('ordenar_por', 'data_criacao')
        ordem = request.args.get('ordem', 'desc')
        ativo_apenas = request.args.get('ativo_apenas', 'true').lower() == 'true'

        # Query base
        query = session.query(Cliente).filter_by(loja_id=claims['loja_id'])

        # Apenas clientes ativos por padrão
        if ativo_apenas:
            query = query.filter_by(ativo=True)

        # Pesquisa
        if pesquisa:
            query = query.filter(or_(
                Cliente.nome.ilike(f'%{pesquisa}%'),
                Cliente.email.ilike(f'%{pesquisa}%'),
                Cliente.telefone.ilike(f'%{pesquisa}%'),
                Cliente.cpf_cnpj.ilike(f'%{pesquisa}%')
            ))

        # Filtros
        if status and status in ['novo', 'ativo', 'vip', 'inativo']:
            query = query.filter_by(status=status)

        if origem and origem in ['direto', 'indicacao', 'redes_sociais', 'google', 'publicidade', 'evento', 'outro']:
            query = query.filter_by(origem=origem)

        if cidade:
            query = query.filter(Cliente.cidade.ilike(f'%{cidade}%'))

        # Ordenação
        ordem_obj = desc if ordem == 'desc' else asc
        if ordenar_por == 'nome':
            query = query.order_by(ordem_obj(Cliente.nome))
        elif ordenar_por == 'valor_total_gasto':
            query = query.order_by(ordem_obj(Cliente.valor_total_gasto))
        else:
            query = query.order_by(ordem_obj(Cliente.data_criacao))

        # Total
        total = query.count()

        # Paginação
        offset = (pagina - 1) * por_pagina
        clientes = query.offset(offset).limit(por_pagina).all()

        # Montar resposta
        dados = {
            'clientes': [c.to_dict() for c in clientes],
            'paginacao': {
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'total_paginas': (total + por_pagina - 1) // por_pagina
            },
            'filtros_aplicados': {
                'pesquisa': pesquisa,
                'status': status,
                'origem': origem,
                'cidade': cidade,
            }
        }

        return jsonify(dados), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao listar clientes: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# CRIAR CLIENTE
# ============================================================================

@clientes_bp.route('', methods=['POST'])
@jwt_required()
def criar_cliente():
    """Cria um novo cliente com validação completa"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        dados = request.get_json() or {}

        # Validações obrigatórias
        if not dados.get('nome'):
            return formatar_resposta_erro('Nome é obrigatório')
        if not dados.get('email'):
            return formatar_resposta_erro('Email é obrigatório')
        if not validar_email(dados['email']):
            return formatar_resposta_erro('Email inválido')

        # Validação de email único
        existe_email = session.query(Cliente).filter_by(
            loja_id=claims['loja_id'],
            email=dados['email'].lower()
        ).first()
        if existe_email:
            return formatar_resposta_erro('Este email já está cadastrado')

        # Validação de CPF/CNPJ
        if dados.get('cpf_cnpj'):
            if not validar_cpf_cnpj(dados['cpf_cnpj']):
                return formatar_resposta_erro('CPF/CNPJ inválido')
            existe_cpf = session.query(Cliente).filter_by(
                cpf_cnpj=dados['cpf_cnpj']
            ).first()
            if existe_cpf:
                return formatar_resposta_erro('Este CPF/CNPJ já está cadastrado')

        # Criar cliente
        cliente = Cliente(
            loja_id=claims['loja_id'],
            nome=dados.get('nome').strip(),
            email=dados.get('email').lower().strip(),
            telefone=dados.get('telefone', '').strip(),
            cpf_cnpj=dados.get('cpf_cnpj', '').strip() if dados.get('cpf_cnpj') else None,
            endereco=dados.get('endereco'),
            numero=dados.get('numero'),
            complemento=dados.get('complemento'),
            cidade=dados.get('cidade'),
            estado=dados.get('estado'),
            cep=dados.get('cep'),
            genero=dados.get('genero'),
            data_nascimento=datetime.fromisoformat(dados['data_nascimento']) if dados.get('data_nascimento') else None,
            tamanho_roupa=dados.get('tamanho_roupa'),
            tamanho_calcado=dados.get('tamanho_calcado'),
            cores_preferidas=dados.get('cores_preferidas', []),
            estilos_preferidos=dados.get('estilos_preferidos', []),
            status=dados.get('status', 'novo'),
            origem=dados.get('origem', 'direto'),
            observacoes_internas=dados.get('observacoes_internas'),
            tags=dados.get('tags', []),
        )

        session.add(cliente)
        session.commit()

        # Criar preferências padrão
        preferencias = PreferenciaCliente(cliente_id=cliente.id)
        session.add(preferencias)
        session.commit()

        return formatar_resposta_sucesso(
            cliente.to_dict(include_details=True),
            'Cliente criado com sucesso',
            201
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao criar cliente: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# OBTER DETALHES DO CLIENTE
# ============================================================================

@clientes_bp.route('/<int:cliente_id>', methods=['GET'])
@jwt_required()
def obter_cliente(cliente_id):
    """Obtém detalhes completos do cliente com linha do tempo"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        cliente = session.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.loja_id == claims['loja_id']
        ).first()

        if not cliente:
            return formatar_resposta_erro('Cliente não encontrado', 404)

        # Dados completos do cliente
        dados = {
            'cliente': cliente.to_dict(include_details=True),
            'preferencias': cliente.preferencias.to_dict() if cliente.preferencias else None,
            'produtos_favoritos': [p.to_dict() for p in cliente.produtos_favoritos] if cliente.produtos_favoritos else [],
            'historico': {
                'pedidos': [p.to_dict() for p in cliente.pedidos[-10:]] if cliente.pedidos else [],
                'interacoes': [i.to_dict() for i in cliente.interacoes[-20:]] if cliente.interacoes else [],
                'atendimentos': [a.to_dict() for a in cliente.atendimentos[-10:]] if cliente.atendimentos else [],
                'campanhas': [c.to_dict() for c in cliente.campanhas_recebidas[-10:]] if cliente.campanhas_recebidas else [],
            },
            'indicadores': {
                'total_pedidos': len(cliente.pedidos) if cliente.pedidos else 0,
                'total_interacoes': len(cliente.interacoes) if cliente.interacoes else 0,
                'total_atendimentos': len(cliente.atendimentos) if cliente.atendimentos else 0,
                'campanhas_recebidas': len(cliente.campanhas_recebidas) if cliente.campanhas_recebidas else 0,
                'cupons_disponveis': len([c for c in cliente.cupons if not c.utilizado]) if cliente.cupons else 0,
                'cupons_utilizados': cliente.cupons_utilizados,
            }
        }

        return jsonify(dados), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao obter cliente: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# ATUALIZAR CLIENTE
# ============================================================================

@clientes_bp.route('/<int:cliente_id>', methods=['PUT'])
@jwt_required()
def atualizar_cliente(cliente_id):
    """Atualiza dados do cliente com validação"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        cliente = session.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.loja_id == claims['loja_id']
        ).first()

        if not cliente:
            return formatar_resposta_erro('Cliente não encontrado', 404)

        dados = request.get_json() or {}

        # Atualizar campos
        if 'nome' in dados:
            if not dados['nome'].strip():
                return formatar_resposta_erro('Nome não pode ser vazio')
            cliente.nome = dados['nome'].strip()

        if 'email' in dados:
            novo_email = dados['email'].lower().strip()
            if not validar_email(novo_email):
                return formatar_resposta_erro('Email inválido')
            # Verificar se outro cliente já usa este email
            existe = session.query(Cliente).filter(
                Cliente.id != cliente_id,
                Cliente.email == novo_email,
                Cliente.loja_id == claims['loja_id']
            ).first()
            if existe:
                return formatar_resposta_erro('Este email já está cadastrado')
            cliente.email = novo_email

        if 'telefone' in dados:
            cliente.telefone = dados['telefone'].strip()

        if 'endereco' in dados:
            cliente.endereco = dados['endereco']

        if 'numero' in dados:
            cliente.numero = dados['numero']

        if 'complemento' in dados:
            cliente.complemento = dados['complemento']

        if 'cidade' in dados:
            cliente.cidade = dados['cidade']

        if 'estado' in dados:
            cliente.estado = dados['estado']

        if 'cep' in dados:
            cliente.cep = dados['cep']

        if 'genero' in dados:
            cliente.genero = dados['genero']

        if 'data_nascimento' in dados:
            cliente.data_nascimento = datetime.fromisoformat(dados['data_nascimento']) if dados['data_nascimento'] else None

        if 'tamanho_roupa' in dados:
            cliente.tamanho_roupa = dados['tamanho_roupa']

        if 'tamanho_calcado' in dados:
            cliente.tamanho_calcado = dados['tamanho_calcado']

        if 'cores_preferidas' in dados:
            cliente.cores_preferidas = dados['cores_preferidas']

        if 'estilos_preferidos' in dados:
            cliente.estilos_preferidos = dados['estilos_preferidos']

        if 'status' in dados:
            cliente.status = dados['status']

        if 'origem' in dados:
            cliente.origem = dados['origem']

        if 'observacoes_internas' in dados:
            cliente.observacoes_internas = dados['observacoes_internas']

        if 'tags' in dados:
            cliente.tags = dados['tags']

        if 'ativo' in dados:
            cliente.ativo = dados['ativo']

        cliente.data_atualizacao = datetime.utcnow()
        session.commit()

        return formatar_resposta_sucesso(
            cliente.to_dict(include_details=True),
            'Cliente atualizado com sucesso'
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao atualizar cliente: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# DELETAR CLIENTE
# ============================================================================

@clientes_bp.route('/<int:cliente_id>', methods=['DELETE'])
@jwt_required()
def deletar_cliente(cliente_id):
    """Deleta um cliente (soft delete - apenas marca como inativo)"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        cliente = session.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.loja_id == claims['loja_id']
        ).first()

        if not cliente:
            return formatar_resposta_erro('Cliente não encontrado', 404)

        # Soft delete
        cliente.ativo = False
        session.commit()

        return formatar_resposta_sucesso(
            None,
            'Cliente deletado com sucesso'
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao deletar cliente: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# ADICIONAR INTERAÇÃO
# ============================================================================

@clientes_bp.route('/<int:cliente_id>/interacoes', methods=['POST'])
@jwt_required()
def criar_interacao(cliente_id):
    """Registra uma interação com o cliente"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        cliente = session.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.loja_id == claims['loja_id']
        ).first()

        if not cliente:
            return formatar_resposta_erro('Cliente não encontrado', 404)

        dados = request.get_json() or {}

        if not dados.get('tipo'):
            return formatar_resposta_erro('Tipo de interação é obrigatório')

        interacao = Interacao(
            cliente_id=cliente_id,
            loja_id=claims['loja_id'],
            tipo=dados['tipo'],
            assunto=dados.get('assunto'),
            descricao=dados.get('descricao'),
            resultado=dados.get('resultado', 'bem_sucedida'),
            data_proximo_contato=datetime.fromisoformat(dados['data_proximo_contato']) if dados.get('data_proximo_contato') else None,
        )

        cliente.data_ultimo_contato = datetime.utcnow()
        session.add(interacao)
        session.commit()

        return formatar_resposta_sucesso(
            interacao.to_dict(),
            'Interação registrada com sucesso',
            201
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao registrar interação: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# ADICIONAR PRODUTO FAVORITO
# ============================================================================

@clientes_bp.route('/<int:cliente_id>/produtos-favoritos/<int:produto_id>', methods=['POST'])
@jwt_required()
def adicionar_produto_favorito(cliente_id, produto_id):
    """Adiciona um produto à lista de favoritos do cliente"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        cliente = session.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.loja_id == claims['loja_id']
        ).first()

        if not cliente:
            return formatar_resposta_erro('Cliente não encontrado', 404)

        # Verificar se produto já é favorito
        existe = session.query(ProdutoFavorito).filter_by(
            cliente_id=cliente_id,
            produto_id=produto_id
        ).first()

        if existe:
            return formatar_resposta_erro('Este produto já está nos favoritos')

        favorito = ProdutoFavorito(
            cliente_id=cliente_id,
            produto_id=produto_id
        )

        session.add(favorito)
        session.commit()

        return formatar_resposta_sucesso(
            favorito.to_dict(),
            'Produto adicionado aos favoritos',
            201
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao adicionar favorito: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# REMOVER PRODUTO FAVORITO
# ============================================================================

@clientes_bp.route('/<int:cliente_id>/produtos-favoritos/<int:produto_id>', methods=['DELETE'])
@jwt_required()
def remover_produto_favorito(cliente_id, produto_id):
    """Remove um produto da lista de favoritos do cliente"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        cliente = session.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.loja_id == claims['loja_id']
        ).first()

        if not cliente:
            return formatar_resposta_erro('Cliente não encontrado', 404)

        favorito = session.query(ProdutoFavorito).filter_by(
            cliente_id=cliente_id,
            produto_id=produto_id
        ).first()

        if not favorito:
            return formatar_resposta_erro('Produto não encontrado nos favoritos', 404)

        session.delete(favorito)
        session.commit()

        return formatar_resposta_sucesso(
            None,
            'Produto removido dos favoritos'
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao remover favorito: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# ESTATÍSTICAS DO CLIENTE
# ============================================================================

@clientes_bp.route('/<int:cliente_id>/estatisticas', methods=['GET'])
@jwt_required()
def obter_estatisticas_cliente(cliente_id):
    """Obtém estatísticas detalhadas do cliente"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        cliente = session.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.loja_id == claims['loja_id']
        ).first()

        if not cliente:
            return formatar_resposta_erro('Cliente não encontrado', 404)

        # Calcular métricas
        pedidos = cliente.pedidos or []
        pedidos_confirmados = [p for p in pedidos if p.status in ['confirmado', 'enviado', 'entregue']]

        # Análise de período
        hoje = datetime.utcnow().date()
        um_mes_atras = (datetime.utcnow() - timedelta(days=30)).date()
        tres_meses_atras = (datetime.utcnow() - timedelta(days=90)).date()
        um_ano_atras = (datetime.utcnow() - timedelta(days=365)).date()

        pedidos_30_dias = [p for p in pedidos_confirmados if p.data_pedido.date() >= um_mes_atras]
        pedidos_90_dias = [p for p in pedidos_confirmados if p.data_pedido.date() >= tres_meses_atras]
        pedidos_ano = [p for p in pedidos_confirmados if p.data_pedido.date() >= um_ano_atras]

        estatisticas = {
            'cliente_id': cliente.id,
            'metricas_gerais': {
                'total_pedidos': len(pedidos_confirmados),
                'valor_total_gasto': sum(p.valor_total for p in pedidos_confirmados),
                'ticket_medio': cliente.ticket_medio or 0,
                'frequencia_compras': cliente.frequencia_compras or 0,
                'ultima_compra': cliente.ultima_compra.isoformat() if cliente.ultima_compra else None,
            },
            'ultimos_30_dias': {
                'total_pedidos': len(pedidos_30_dias),
                'valor_total': sum(p.valor_total for p in pedidos_30_dias),
            },
            'ultimos_90_dias': {
                'total_pedidos': len(pedidos_90_dias),
                'valor_total': sum(p.valor_total for p in pedidos_90_dias),
            },
            'ultimo_ano': {
                'total_pedidos': len(pedidos_ano),
                'valor_total': sum(p.valor_total for p in pedidos_ano),
            },
            'fidelidade': {
                'nivel': cliente.nivel_fidelidade,
                'pontos': cliente.pontos_fidelidade,
                'cupons_disponiveis': len([c for c in cliente.cupons if not c.utilizado]) if cliente.cupons else 0,
            },
            'produtos_favoritos': len(cliente.produtos_favoritos) if cliente.produtos_favoritos else 0,
            'status': (cliente.status.value if hasattr(cliente.status, 'value') else cliente.status) if cliente.status else None,
        }

        return jsonify(estatisticas), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao obter estatísticas: {str(e)}', 500)
    finally:
        db_handler.remove_session()
