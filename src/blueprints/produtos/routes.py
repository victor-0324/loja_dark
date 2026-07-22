"""Rotas completas de gestão de produtos com estoque."""

from flask import jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from datetime import datetime
from sqlalchemy import or_, desc, asc

from src.blueprints.produtos import produtos_bp
from src.database import DBConnectionHendler
from src.models import Produto

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


# ============================================================================
# LISTAR PRODUTOS
# ============================================================================

@produtos_bp.route('', methods=['GET'])
@jwt_required()
def listar_produtos():
    """
    Lista produtos com filtros, paginação e pesquisa.
    
    Query params:
    - pagina: número da página (padrão: 1)
    - por_pagina: itens por página (padrão: 20, máximo: 100)
    - pesquisa: busca por nome, SKU ou descrição
    - categoria: filtro por categoria
    - apenas_estoque: apenas produtos com estoque (true/false)
    - apenas_ativos: apenas produtos ativos (true/false)
    - ordenar_por: nome, preco, estoque, data_criacao
    - ordem: asc ou desc
    """
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        # Parâmetros
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = min(request.args.get('por_pagina', 20, type=int), 100)
        pesquisa = request.args.get('pesquisa', '').strip()
        categoria = request.args.get('categoria', '').strip()
        apenas_estoque = request.args.get('apenas_estoque', 'false').lower() == 'true'
        apenas_ativos = request.args.get('apenas_ativos', 'true').lower() == 'true'
        ordenar_por = request.args.get('ordenar_por', 'data_criacao')
        ordem = request.args.get('ordem', 'desc')

        # Query base
        query = session.query(Produto).filter_by(loja_id=claims['loja_id'])

        # Filtrar por status
        if apenas_ativos:
            query = query.filter_by(ativo=True)

        # Pesquisa
        if pesquisa:
            query = query.filter(or_(
                Produto.nome.ilike(f'%{pesquisa}%'),
                Produto.sku.ilike(f'%{pesquisa}%'),
                Produto.descricao.ilike(f'%{pesquisa}%')
            ))

        # Filtro de categoria
        if categoria:
            query = query.filter(Produto.categoria.ilike(f'%{categoria}%'))

        # Filtro de estoque
        if apenas_estoque:
            query = query.filter(Produto.estoque_total > 0)

        # Ordenação
        ordem_obj = desc if ordem == 'desc' else asc
        if ordenar_por == 'nome':
            query = query.order_by(ordem_obj(Produto.nome))
        elif ordenar_por == 'preco':
            query = query.order_by(ordem_obj(Produto.preco))
        elif ordenar_por == 'estoque':
            query = query.order_by(ordem_obj(Produto.estoque_total))
        else:
            query = query.order_by(ordem_obj(Produto.data_criacao))

        # Total
        total = query.count()

        # Paginação
        offset = (pagina - 1) * por_pagina
        produtos = query.offset(offset).limit(por_pagina).all()

        # Montar resposta
        dados = {
            'produtos': [p.to_dict(include_estoque=True) for p in produtos],
            'paginacao': {
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'total_paginas': (total + por_pagina - 1) // por_pagina
            }
        }

        return jsonify(dados), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao listar produtos: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# CRIAR PRODUTO
# ============================================================================

@produtos_bp.route('', methods=['POST'])
@jwt_required()
def criar_produto():
    """Cria um novo produto"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        dados = request.get_json() or {}

        # Validações
        if not dados.get('nome'):
            return formatar_resposta_erro('Nome é obrigatório')
        if not dados.get('sku'):
            return formatar_resposta_erro('SKU é obrigatório')
        if not dados.get('categoria'):
            return formatar_resposta_erro('Categoria é obrigatória')
        if dados.get('preco') is None or dados['preco'] < 0:
            return formatar_resposta_erro('Preço válido é obrigatório')

        # Verificar SKU único
        existe_sku = session.query(Produto).filter_by(
            sku=dados['sku'],
            loja_id=claims['loja_id']
        ).first()
        if existe_sku:
            return formatar_resposta_erro('Este SKU já existe')

        produto = Produto(
            loja_id=claims['loja_id'],
            nome=dados['nome'].strip(),
            sku=dados['sku'].strip().upper(),
            categoria=dados['categoria'].strip(),
            descricao=dados.get('descricao'),
            preco=float(dados['preco']),
            preco_original=float(dados['preco_original']) if dados.get('preco_original') else None,
            preco_custo=float(dados['preco_custo']) if dados.get('preco_custo') else None,
            estoque_total=int(dados.get('estoque_total', 0)),
            estoque_minimo=int(dados.get('estoque_minimo', 5)),
            subcategoria=dados.get('subcategoria'),
            colecao=dados.get('colecao'),
            tamanhos_disponiveis=dados.get('tamanhos_disponiveis', []),
            cores_disponiveis=dados.get('cores_disponiveis', []),
            material=dados.get('material'),
            imagem_principal_url=dados.get('imagem_principal_url'),
            imagens_urls=dados.get('imagens_urls', []),
            codigo_barras=dados.get('codigo_barras'),
            peso=float(dados['peso']) if dados.get('peso') else None,
            dimensoes=dados.get('dimensoes'),
            meta_descricao=dados.get('meta_descricao'),
            tags_busca=dados.get('tags_busca', []),
            ativo=dados.get('ativo', True),
            destaque=dados.get('destaque', False),
        )

        # Calcular margem de lucro
        if produto.preco_custo and produto.preco > 0:
            produto.margem_lucro = ((produto.preco - produto.preco_custo) / produto.preco) * 100

        session.add(produto)
        session.commit()

        return formatar_resposta_sucesso(
            produto.to_dict_completo(),
            'Produto criado com sucesso',
            201
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao criar produto: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# OBTER DETALHES DO PRODUTO
# ============================================================================

@produtos_bp.route('/<int:produto_id>', methods=['GET'])
@jwt_required()
def obter_produto(produto_id):
    """Obtém detalhes completos de um produto"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        produto = session.query(Produto).filter(
            Produto.id == produto_id,
            Produto.loja_id == claims['loja_id']
        ).first()

        if not produto:
            return formatar_resposta_erro('Produto não encontrado', 404)

        return jsonify(produto.to_dict_completo()), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao obter produto: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# ATUALIZAR PRODUTO
# ============================================================================

@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
@jwt_required()
def atualizar_produto(produto_id):
    """Atualiza dados de um produto"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        produto = session.query(Produto).filter(
            Produto.id == produto_id,
            Produto.loja_id == claims['loja_id']
        ).first()

        if not produto:
            return formatar_resposta_erro('Produto não encontrado', 404)

        dados = request.get_json() or {}

        # Atualizar campos
        if 'nome' in dados:
            produto.nome = dados['nome'].strip()
        if 'descricao' in dados:
            produto.descricao = dados['descricao']
        if 'preco' in dados:
            produto.preco = float(dados['preco'])
        if 'preco_original' in dados:
            produto.preco_original = float(dados['preco_original']) if dados['preco_original'] else None
        if 'preco_custo' in dados:
            produto.preco_custo = float(dados['preco_custo']) if dados['preco_custo'] else None
        if 'categoria' in dados:
            produto.categoria = dados['categoria']
        if 'subcategoria' in dados:
            produto.subcategoria = dados['subcategoria']
        if 'colecao' in dados:
            produto.colecao = dados['colecao']
        if 'estoque_total' in dados:
            produto.estoque_total = int(dados['estoque_total'])
        if 'estoque_minimo' in dados:
            produto.estoque_minimo = int(dados['estoque_minimo'])
        if 'tamanhos_disponiveis' in dados:
            produto.tamanhos_disponiveis = dados['tamanhos_disponiveis']
        if 'cores_disponiveis' in dados:
            produto.cores_disponiveis = dados['cores_disponiveis']
        if 'material' in dados:
            produto.material = dados['material']
        if 'imagem_principal_url' in dados:
            produto.imagem_principal_url = dados['imagem_principal_url']
        if 'imagens_urls' in dados:
            produto.imagens_urls = dados['imagens_urls']
        if 'ativo' in dados:
            produto.ativo = dados['ativo']
        if 'destaque' in dados:
            produto.destaque = dados['destaque']
        if 'promocao' in dados:
            produto.promocao = dados['promocao']

        # Recalcular margem de lucro
        if produto.preco_custo and produto.preco > 0:
            produto.margem_lucro = ((produto.preco - produto.preco_custo) / produto.preco) * 100

        produto.data_atualizacao = datetime.utcnow()
        session.commit()

        return formatar_resposta_sucesso(
            produto.to_dict_completo(),
            'Produto atualizado com sucesso'
        )

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao atualizar produto: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# DELETAR PRODUTO
# ============================================================================

@produtos_bp.route('/<int:produto_id>', methods=['DELETE'])
@jwt_required()
def deletar_produto(produto_id):
    """Deleta um produto (soft delete)"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        produto = session.query(Produto).filter(
            Produto.id == produto_id,
            Produto.loja_id == claims['loja_id']
        ).first()

        if not produto:
            return formatar_resposta_erro('Produto não encontrado', 404)

        # Soft delete
        produto.ativo = False
        session.commit()

        return formatar_resposta_sucesso(None, 'Produto deletado com sucesso')

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao deletar produto: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# ATUALIZAR ESTOQUE
# ============================================================================

@produtos_bp.route('/<int:produto_id>/estoque', methods=['PATCH'])
@jwt_required()
def atualizar_estoque(produto_id):
    """Atualiza o estoque de um produto"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        produto = session.query(Produto).filter(
            Produto.id == produto_id,
            Produto.loja_id == claims['loja_id']
        ).first()

        if not produto:
            return formatar_resposta_erro('Produto não encontrado', 404)

        dados = request.get_json() or {}

        if 'quantidade' not in dados:
            return formatar_resposta_erro('Quantidade é obrigatória')

        operacao = dados.get('operacao', 'atualizar')  # atualizar, adicionar, remover
        quantidade = int(dados['quantidade'])

        if operacao == 'atualizar':
            produto.estoque_total = quantidade
        elif operacao == 'adicionar':
            produto.estoque_total += quantidade
        elif operacao == 'remover':
            if quantidade > produto.estoque_total:
                return formatar_resposta_erro('Quantidade insuficiente em estoque')
            produto.estoque_total -= quantidade

        produto.data_atualizacao = datetime.utcnow()
        session.commit()

        return formatar_resposta_sucesso({
            'produto_id': produto.id,
            'estoque_total': produto.estoque_total,
            'estoque_disponivel': produto.estoque_disponivel,
        }, 'Estoque atualizado com sucesso')

    except Exception as e:
        session.rollback()
        return formatar_resposta_erro(f'Erro ao atualizar estoque: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# LISTAR CATEGORIAS
# ============================================================================

@produtos_bp.route('/categorias', methods=['GET'])
@jwt_required()
def listar_categorias():
    """Lista todas as categorias de produtos da loja"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        # Obter categorias únicas
        categorias = session.query(Produto.categoria)\
            .filter_by(loja_id=claims['loja_id'], ativo=True)\
            .distinct()\
            .all()

        categorias = [c[0] for c in categorias if c[0]]

        return jsonify({
            'categorias': categorias,
            'total': len(categorias)
        }), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao listar categorias: {str(e)}', 500)
    finally:
        db_handler.remove_session()


# ============================================================================
# PRODUTOS COM ESTOQUE BAIXO
# ============================================================================

@produtos_bp.route('/estoque-baixo', methods=['GET'])
@jwt_required()
def produtos_estoque_baixo():
    """Lista produtos com estoque abaixo do mínimo"""
    claims = get_jwt()
    session = db_handler.get_session()

    try:
        produtos = session.query(Produto).filter(
            Produto.loja_id == claims['loja_id'],
            Produto.ativo == True,
            Produto.estoque_total < Produto.estoque_minimo
        ).order_by(desc(Produto.estoque_minimo - Produto.estoque_total)).all()

        return jsonify({
            'produtos': [p.to_dict(include_estoque=True) for p in produtos],
            'total': len(produtos)
        }), 200

    except Exception as e:
        return formatar_resposta_erro(f'Erro ao listar produtos: {str(e)}', 500)
    finally:
        db_handler.remove_session()
