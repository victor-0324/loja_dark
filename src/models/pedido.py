from datetime import datetime
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean, JSON
)
from sqlalchemy.orm import relationship
from src.database import Base


class StatusPedido:
    """Constantes de status de pedido"""
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    PROCESSANDO = "processando"
    DESPACHADO = "despachado"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"
    DEVOLVIDO = "devolvido"

    TODOS = [PENDENTE, CONFIRMADO, PROCESSANDO, DESPACHADO, ENVIADO, ENTREGUE, CANCELADO, DEVOLVIDO]


class MetodoPagamento:
    """Métodos de pagamento disponíveis"""
    CREDITO = "credito"
    DEBITO = "debito"
    PIX = "pix"
    BOLETO = "boleto"
    TRANSFERENCIA = "transferencia"
    DINHEIRO = "dinheiro"

    TODOS = [CREDITO, DEBITO, PIX, BOLETO, TRANSFERENCIA, DINHEIRO]


class Pedido(Base):
    """Modelo de Pedido - vendas com rastreamento completo"""
    __tablename__ = 'pedidos'

    # IDs
    id = Column(Integer, primary_key=True, autoincrement=True)
    loja_id = Column(Integer, ForeignKey('lojas.id'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    
    # Identificação
    numero_pedido = Column(String(50), unique=True, nullable=False, index=True)  # PED-2024-0001
    codigo_rastreamento = Column(String(100), unique=True)
    referencia_externa = Column(String(100))  # ID de plataforma externa (Shopify, Woo, etc)
    
    # Valores
    subtotal = Column(Float, nullable=False)
    desconto = Column(Float, default=0)
    taxa_envio = Column(Float, default=0)
    taxa_servico = Column(Float, default=0)  # Taxa de serviço/embalagem
    valor_total = Column(Float, nullable=False)
    
    # Aplicação de cupom/desconto
    cupom_codigo = Column(String(50))
    cupom_desconto = Column(Float, default=0)
    
    # Status
    status = Column(String(50), default=StatusPedido.PENDENTE, index=True)
    motivo_cancelamento = Column(String(255))
    
    # Pagamento
    metodo_pagamento = Column(String(50))
    status_pagamento = Column(String(50), default="pendente")  # pendente, processando, aprovado, reprovado, reembolsado
    data_pagamento = Column(DateTime)
    numero_transacao = Column(String(100))
    
    # Endereço de entrega
    endereco_entrega = Column(Text)
    numero_entrega = Column(String(10))
    complemento_entrega = Column(String(255))
    cidade_entrega = Column(String(100))
    estado_entrega = Column(String(2))
    cep_entrega = Column(String(10))
    
    # Transportadora
    transportadora = Column(String(100))  # Correios, Sedex, Loggi, Jadlog, etc
    tipo_envio = Column(String(50))  # normal, expresso, agendado
    
    # Datas importantes
    data_pedido = Column(DateTime, default=datetime.utcnow, index=True)
    data_confirmacao = Column(DateTime)
    data_processamento = Column(DateTime)
    data_despacho = Column(DateTime)
    data_envio = Column(DateTime)
    data_entrega_prevista = Column(DateTime)
    data_entrega_realizada = Column(DateTime)
    
    # Observações
    observacoes = Column(Text)
    observacoes_internas = Column(Text)
    
    # Informações adicionais
    cliente_observacoes = Column(String(255))  # Observações do cliente no checkout
    presente = Column(Boolean, default=False)
    msg_presente = Column(Text)  # Mensagem para presente
    
    # Devolução
    devolvido = Column(Boolean, default=False)
    data_devolucao = Column(DateTime)
    motivo_devolucao = Column(String(255))
    valor_reembolso = Column(Float)
    
    data_criacao = Column(DateTime, default=datetime.utcnow, index=True)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    loja = relationship('Loja', back_populates='pedidos')
    cliente = relationship('Cliente', back_populates='pedidos')
    itens = relationship('ItemPedido', back_populates='pedido', cascade='all, delete-orphan', lazy='joined')
    historico_status = relationship('HistoricoStatusPedido', back_populates='pedido', cascade='all, delete-orphan', lazy='joined')

    def __repr__(self):
        return f'<Pedido {self.numero_pedido}>'

    def to_dict(self, include_items=True):
        """Converte pedido para dicionário"""
        dados = {
            'id': self.id,
            'numero_pedido': self.numero_pedido,
            'codigo_rastreamento': self.codigo_rastreamento,
            'status': self.status,
            'status_pagamento': self.status_pagamento,
            'subtotal': float(self.subtotal),
            'desconto': float(self.desconto),
            'taxa_envio': float(self.taxa_envio),
            'taxa_servico': float(self.taxa_servico),
            'valor_total': float(self.valor_total),
            'metodo_pagamento': self.metodo_pagamento,
            'data_pedido': self.data_pedido.isoformat() if self.data_pedido else None,
            'data_entrega_prevista': self.data_entrega_prevista.isoformat() if self.data_entrega_prevista else None,
            'data_entrega_realizada': self.data_entrega_realizada.isoformat() if self.data_entrega_realizada else None,
            'cliente_id': self.cliente_id,
            'transportadora': self.transportadora,
            'observacoes': self.observacoes,
        }

        if include_items:
            dados['itens'] = [item.to_dict() for item in self.itens] if self.itens else []
            dados['total_itens'] = len(self.itens) if self.itens else 0

        return dados

    def to_dict_completo(self):
        """Retorna dicionário com todos os dados do pedido"""
        dados = self.to_dict(include_items=True)
        dados.update({
            'loja_id': self.loja_id,
            'referencia_externa': self.referencia_externa,
            'cupom_codigo': self.cupom_codigo,
            'cupom_desconto': float(self.cupom_desconto) if self.cupom_desconto else 0,
            'data_confirmacao': self.data_confirmacao.isoformat() if self.data_confirmacao else None,
            'data_processamento': self.data_processamento.isoformat() if self.data_processamento else None,
            'data_despacho': self.data_despacho.isoformat() if self.data_despacho else None,
            'data_envio': self.data_envio.isoformat() if self.data_envio else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'endereco_entrega': self.endereco_entrega,
            'numero_entrega': self.numero_entrega,
            'complemento_entrega': self.complemento_entrega,
            'cidade_entrega': self.cidade_entrega,
            'estado_entrega': self.estado_entrega,
            'cep_entrega': self.cep_entrega,
            'tipo_envio': self.tipo_envio,
            'cliente_observacoes': self.cliente_observacoes,
            'presente': self.presente,
            'msg_presente': self.msg_presente,
            'devolvido': self.devolvido,
            'data_devolucao': self.data_devolucao.isoformat() if self.data_devolucao else None,
            'motivo_devolucao': self.motivo_devolucao,
            'valor_reembolso': float(self.valor_reembolso) if self.valor_reembolso else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
        })
        return dados

    def pode_ser_cancelado(self):
        """Verifica se pedido pode ser cancelado"""
        return self.status in [StatusPedido.PENDENTE, StatusPedido.CONFIRMADO]

    def pode_ser_devolvido(self):
        """Verifica se pedido pode ser devolvido"""
        return self.status == StatusPedido.ENTREGUE and not self.devolvido


class ItemPedido(Base):
    """Modelo de Item do Pedido - linha individual do pedido"""
    __tablename__ = 'itens_pedido'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), nullable=False)
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    
    # Dados do produto no momento da venda
    produto_nome = Column(String(255), nullable=False)
    produto_sku = Column(String(100))
    
    # Atributos do item
    tamanho = Column(String(10))
    cor = Column(String(50))
    
    # Quantidade e preço
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    desconto_item = Column(Float, default=0)
    
    # Estoque
    estoque_reservado = Column(Boolean, default=False)
    
    data_criacao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    pedido = relationship('Pedido', back_populates='itens')
    produto = relationship('Produto', back_populates='itens_pedido', lazy='joined')

    def __repr__(self):
        return f'<ItemPedido pedido_id={self.pedido_id} produto_id={self.produto_id}>'

    @property
    def subtotal(self):
        """Subtotal do item = (quantidade * preço) - desconto"""
        return (self.quantidade * self.preco_unitario) - self.desconto_item

    def to_dict(self):
        """Converte item para dicionário"""
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'produto_id': self.produto_id,
            'produto_nome': self.produto_nome,
            'produto_sku': self.produto_sku,
            'tamanho': self.tamanho,
            'cor': self.cor,
            'quantidade': self.quantidade,
            'preco_unitario': float(self.preco_unitario),
            'desconto_item': float(self.desconto_item),
            'subtotal': float(self.subtotal),
        }


class HistoricoStatusPedido(Base):
    """Histórico de mudanças de status do pedido"""
    __tablename__ = 'historico_status_pedidos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    
    status_anterior = Column(String(50))
    status_novo = Column(String(50), nullable=False)
    motivo = Column(String(255))
    observacoes = Column(Text)
    data_alteracao = Column(DateTime, default=datetime.utcnow, index=True)

    pedido = relationship('Pedido', back_populates='historico_status')
    usuario = relationship('Usuario')

    def __repr__(self):
        return f'<HistoricoStatusPedido pedido_id={self.pedido_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'status_anterior': self.status_anterior,
            'status_novo': self.status_novo,
            'motivo': self.motivo,
            'observacoes': self.observacoes,
            'data_alteracao': self.data_alteracao.isoformat() if self.data_alteracao else None,
        }
