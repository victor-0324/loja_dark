from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float,
    Table, JSON, Enum
)
from sqlalchemy.orm import relationship
import enum
from src.database import Base


class StatusCliente(str, enum.Enum):
    """Status do cliente"""
    NOVO = "novo"
    ATIVO = "ativo"
    VIP = "vip"
    INATIVO = "inativo"


class OrigemCliente(str, enum.Enum):
    """Origem de aquisição do cliente"""
    DIRETO = "direto"
    INDICACAO = "indicacao"
    REDES_SOCIAIS = "redes_sociais"
    GOOGLE = "google"
    PUBLICIDADE = "publicidade"
    EVENTO = "evento"
    OUTRO = "outro"


class EstiloPreferido(str, enum.Enum):
    """Estilos de roupas preferidos"""
    CASUAL = "casual"
    FORMAL = "formal"
    DESPORTIVO = "desportivo"
    VINTAGE = "vintage"
    MINIMALISTA = "minimalista"
    BOHO = "boho"
    CLASSICO = "classico"
    MODERNO = "moderno"


class Cliente(Base):
    """Modelo de Cliente - CRM completo para loja de roupas"""
    __tablename__ = 'clientes'

    # IDs
    id = Column(Integer, primary_key=True, autoincrement=True)
    loja_id = Column(Integer, ForeignKey('lojas.id'), nullable=False)

    # Dados básicos
    nome = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    telefone = Column(String(20), index=True)
    cpf_cnpj = Column(String(20), unique=True)

    # Endereço
    endereco = Column(Text)
    numero = Column(String(10))
    complemento = Column(String(255))
    cidade = Column(String(100), index=True)
    estado = Column(String(2))
    cep = Column(String(10))

    # Dados pessoais
    genero = Column(String(20))  # M, F, Outro
    data_nascimento = Column(DateTime)
    
    # Preferências de compra
    tamanho_roupa = Column(String(10))  # P, M, G, GG
    tamanho_calcado = Column(String(5))  # 33-47
    cores_preferidas = Column(JSON)  # Lista de cores: ["preto", "azul", "rosa"]
    estilos_preferidos = Column(JSON)  # Lista de estilos: ["casual", "formal"]
    
    # Indicadores comerciais
    ticket_medio = Column(Float, default=0)
    valor_total_gasto = Column(Float, default=0)
    frequencia_compras = Column(Integer, default=0)  # Número de compras
    ultima_compra = Column(DateTime)
    data_primeira_compra = Column(DateTime)
    
    # Status e origem
    status = Column(Enum(StatusCliente), default=StatusCliente.NOVO, index=True)
    origem = Column(Enum(OrigemCliente), default=OrigemCliente.DIRETO)

    # Programa de fidelidade
    pontos_fidelidade = Column(Integer, default=0)
    nivel_fidelidade = Column(String(50), default="Bronze")  # Bronze, Prata, Ouro, Platina
    cupons_utilizados = Column(Integer, default=0)

    # Observações e tags
    observacoes_internas = Column(Text)
    tags = Column(JSON)  # Lista de tags customizadas
    
    # Status do cliente
    ativo = Column(Boolean, default=True, index=True)
    
    # Controle de datas
    data_criacao = Column(DateTime, default=datetime.utcnow, index=True)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_ultimo_contato = Column(DateTime)

    # Relacionamentos
    loja = relationship('Loja', back_populates='clientes')
    pedidos = relationship('Pedido', back_populates='cliente', cascade='all, delete-orphan', lazy='joined')
    preferencias = relationship('PreferenciaCliente', back_populates='cliente', uselist=False, cascade='all, delete-orphan')
    produtos_favoritos = relationship('ProdutoFavorito', back_populates='cliente', cascade='all, delete-orphan', lazy='joined')
    interacoes = relationship('Interacao', back_populates='cliente', cascade='all, delete-orphan', lazy='joined')
    atendimentos = relationship('Atendimento', back_populates='cliente', cascade='all, delete-orphan', lazy='joined')
    campanhas_recebidas = relationship('CampanhaRecebida', back_populates='cliente', cascade='all, delete-orphan', lazy='joined')
    cupons = relationship('CupomCliente', back_populates='cliente', cascade='all, delete-orphan', lazy='joined')

    def __repr__(self):
        return f'<Cliente {self.nome} ({self.email})>'

    def to_dict(self, include_details=False):
        """Converte cliente para dicionário"""
        dados = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'cpf_cnpj': self.cpf_cnpj,
            'cidade': self.cidade,
            'estado': self.estado,
            'status': (self.status.value if hasattr(self.status, 'value') else self.status) if self.status else None,
            'origem': (self.origem.value if hasattr(self.origem, 'value') else self.origem) if self.origem else None,
            'ativo': self.ativo,
            'ticket_medio': float(self.ticket_medio) if self.ticket_medio else 0,
            'valor_total_gasto': float(self.valor_total_gasto) if self.valor_total_gasto else 0,
            'frequencia_compras': self.frequencia_compras,
            'ultima_compra': self.ultima_compra.isoformat() if self.ultima_compra else None,
            'data_primeira_compra': self.data_primeira_compra.isoformat() if self.data_primeira_compra else None,
            'nivel_fidelidade': self.nivel_fidelidade,
            'pontos_fidelidade': self.pontos_fidelidade,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
        }

        if include_details:
            dados.update({
                'endereco': self.endereco,
                'numero': self.numero,
                'complemento': self.complemento,
                'cep': self.cep,
                'genero': self.genero,
                'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
                'tamanho_roupa': self.tamanho_roupa,
                'tamanho_calcado': self.tamanho_calcado,
                'cores_preferidas': self.cores_preferidas or [],
                'estilos_preferidos': self.estilos_preferidos or [],
                'observacoes_internas': self.observacoes_internas,
                'tags': self.tags or [],
                'cupons_utilizados': self.cupons_utilizados,
                'data_ultimo_contato': self.data_ultimo_contato.isoformat() if self.data_ultimo_contato else None,
                'pedidos_count': len(self.pedidos) if self.pedidos else 0,
                'produtos_favoritos_count': len(self.produtos_favoritos) if self.produtos_favoritos else 0,
                'interacoes_count': len(self.interacoes) if self.interacoes else 0,
            })

        return dados

    def calcular_metricas(self):
        """Recalcula métricas do cliente baseado em seus pedidos"""
        if not self.pedidos:
            return

        pedidos_confirmados = [p for p in self.pedidos if p.status in ['confirmado', 'enviado', 'entregue']]
        
        if pedidos_confirmados:
            self.frequencia_compras = len(pedidos_confirmados)
            self.valor_total_gasto = sum(p.valor_total for p in pedidos_confirmados)
            self.ticket_medio = self.valor_total_gasto / len(pedidos_confirmados)
            self.ultima_compra = max(p.data_pedido for p in pedidos_confirmados)
            if not self.data_primeira_compra:
                self.data_primeira_compra = min(p.data_pedido for p in pedidos_confirmados)
            
            # Determinar status baseado em métricas
            if self.valor_total_gasto > 5000:
                self.status = StatusCliente.VIP
                self.nivel_fidelidade = "Platina"
            elif self.valor_total_gasto > 2000:
                self.nivel_fidelidade = "Ouro"
            elif self.valor_total_gasto > 1000:
                self.nivel_fidelidade = "Prata"
            else:
                self.nivel_fidelidade = "Bronze"


class PreferenciaCliente(Base):
    """Preferências detalhadas do cliente"""
    __tablename__ = 'preferencias_clientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False, unique=True)
    
    # Preferências de comunicação
    email_marketing = Column(Boolean, default=True)
    sms_marketing = Column(Boolean, default=False)
    whatsapp_marketing = Column(Boolean, default=False)
    notificacoes_push = Column(Boolean, default=True)
    
    # Frequência de contato
    frequencia_comunicacao = Column(String(50), default="semanal")  # diaria, semanal, quinzenal, mensal
    
    # Dia da semana preferido para contato
    dias_preferenciais = Column(JSON)  # [1,2,3,4,5] = Seg a Sex
    
    # Horários
    horario_inicio = Column(String(5))  # "09:00"
    horario_fim = Column(String(5))  # "18:00"
    
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = relationship('Cliente', back_populates='preferencias')

    def __repr__(self):
        return f'<PreferenciaCliente cliente_id={self.cliente_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'email_marketing': self.email_marketing,
            'sms_marketing': self.sms_marketing,
            'whatsapp_marketing': self.whatsapp_marketing,
            'notificacoes_push': self.notificacoes_push,
            'frequencia_comunicacao': self.frequencia_comunicacao,
            'dias_preferenciais': self.dias_preferenciais or [],
            'horario_inicio': self.horario_inicio,
            'horario_fim': self.horario_fim,
        }


class ProdutoFavorito(Base):
    """Produtos favoritos do cliente"""
    __tablename__ = 'produtos_favoritos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    data_adicao = Column(DateTime, default=datetime.utcnow)

    cliente = relationship('Cliente', back_populates='produtos_favoritos')
    produto = relationship('Produto', lazy='joined')

    def __repr__(self):
        return f'<ProdutoFavorito cliente_id={self.cliente_id} produto_id={self.produto_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'produto_id': self.produto_id,
            'produto': self.produto.to_dict() if self.produto else None,
            'data_adicao': self.data_adicao.isoformat() if self.data_adicao else None,
        }


class Interacao(Base):
    """Histórico de interações com cliente"""
    __tablename__ = 'interacoes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    loja_id = Column(Integer, ForeignKey('lojas.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    
    tipo = Column(String(50), nullable=False)  # email, telefone, chat, presencialmente, redes_sociais
    assunto = Column(String(255))
    descricao = Column(Text)
    resultado = Column(String(50))  # bem_sucedida, pendente, falha, agendada
    data_interacao = Column(DateTime, default=datetime.utcnow, index=True)
    data_proximo_contato = Column(DateTime)

    cliente = relationship('Cliente', back_populates='interacoes')
    loja = relationship('Loja')
    usuario = relationship('Usuario')

    def __repr__(self):
        return f'<Interacao cliente_id={self.cliente_id} tipo={self.tipo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'tipo': self.tipo,
            'assunto': self.assunto,
            'descricao': self.descricao,
            'resultado': self.resultado,
            'data_interacao': self.data_interacao.isoformat() if self.data_interacao else None,
            'data_proximo_contato': self.data_proximo_contato.isoformat() if self.data_proximo_contato else None,
        }


class Atendimento(Base):
    """Histórico de atendimentos ao cliente"""
    __tablename__ = 'atendimentos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    loja_id = Column(Integer, ForeignKey('lojas.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    
    tipo = Column(String(50), nullable=False)  # vendas, suporte, reclamacao, duvida, retorno
    assunto = Column(String(255))
    descricao = Column(Text)
    status = Column(String(50), default="aberto")  # aberto, resolvido, cancelado
    prioridade = Column(String(20), default="normal")  # baixa, normal, alta, critica
    data_abertura = Column(DateTime, default=datetime.utcnow, index=True)
    data_fechamento = Column(DateTime)
    notas = Column(Text)

    cliente = relationship('Cliente', back_populates='atendimentos')
    loja = relationship('Loja')
    usuario = relationship('Usuario')

    def __repr__(self):
        return f'<Atendimento cliente_id={self.cliente_id} tipo={self.tipo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'tipo': self.tipo,
            'assunto': self.assunto,
            'descricao': self.descricao,
            'status': self.status,
            'prioridade': self.prioridade,
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'data_fechamento': self.data_fechamento.isoformat() if self.data_fechamento else None,
        }


class CampanhaRecebida(Base):
    """Histórico de campanhas recebidas pelo cliente"""
    __tablename__ = 'campanhas_recebidas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    loja_id = Column(Integer, ForeignKey('lojas.id'), nullable=False)
    
    nome_campanha = Column(String(255))
    tipo = Column(String(50))  # email, sms, push, whatsapp
    assunto = Column(String(255))
    data_envio = Column(DateTime, default=datetime.utcnow)
    data_abertura = Column(DateTime)
    data_clique = Column(DateTime)
    convertida = Column(Boolean, default=False)
    data_conversao = Column(DateTime)

    cliente = relationship('Cliente', back_populates='campanhas_recebidas')
    loja = relationship('Loja')

    def __repr__(self):
        return f'<CampanhaRecebida cliente_id={self.cliente_id} campanha={self.nome_campanha}>'

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nome_campanha': self.nome_campanha,
            'tipo': self.tipo,
            'assunto': self.assunto,
            'data_envio': self.data_envio.isoformat() if self.data_envio else None,
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'data_clique': self.data_clique.isoformat() if self.data_clique else None,
            'convertida': self.convertida,
            'data_conversao': self.data_conversao.isoformat() if self.data_conversao else None,
        }


class CupomCliente(Base):
    """Cupons utilizados e disponíveis do cliente"""
    __tablename__ = 'cupons_clientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    loja_id = Column(Integer, ForeignKey('lojas.id'), nullable=False)
    
    codigo = Column(String(50), unique=True)
    descricao = Column(String(255))
    desconto_percentual = Column(Float, default=0)  # Desconto em %
    desconto_fixo = Column(Float, default=0)  # Desconto em valor fixo
    valor_minimo = Column(Float, default=0)  # Valor mínimo de compra
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_expiracao = Column(DateTime)
    utilizado = Column(Boolean, default=False)
    data_utilizacao = Column(DateTime)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), nullable=True)

    cliente = relationship('Cliente', back_populates='cupons')
    loja = relationship('Loja')
    pedido = relationship('Pedido')

    def __repr__(self):
        return f'<CupomCliente cliente_id={self.cliente_id} codigo={self.codigo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'desconto_percentual': float(self.desconto_percentual) if self.desconto_percentual else 0,
            'desconto_fixo': float(self.desconto_fixo) if self.desconto_fixo else 0,
            'valor_minimo': float(self.valor_minimo) if self.valor_minimo else 0,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_expiracao': self.data_expiracao.isoformat() if self.data_expiracao else None,
            'utilizado': self.utilizado,
            'data_utilizacao': self.data_utilizacao.isoformat() if self.data_utilizacao else None,
        }
