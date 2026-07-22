from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from src.database import Base


class Loja(Base):
    """Modelo de Loja - representa um cliente do SaaS"""
    __tablename__ = 'lojas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identificação
    nome = Column(String(255), nullable=False, unique=True, index=True)
    slug = Column(String(255), unique=True)  # Para URL amigável
    email = Column(String(255), nullable=False, unique=True, index=True)
    telefone = Column(String(20))
    
    # Endereço
    endereco = Column(Text)
    numero = Column(String(10))
    complemento = Column(String(255))
    cidade = Column(String(100))
    estado = Column(String(2))
    cep = Column(String(10))
    
    # Branding
    logo_url = Column(String(500))
    banner_url = Column(String(500))
    cor_primaria = Column(String(7), default='#FF1493')  # Rosa elétrico
    cor_secundaria = Column(String(7), default='#0099FF')  # Azul elétrico
    cor_sucesso = Column(String(7), default='#00CC88')
    cor_alerta = Column(String(7), default='#FFB800')
    cor_erro = Column(String(7), default='#FF4444')
    
    # Documentos
    cnpj = Column(String(20), unique=True)
    inscricao_estadual = Column(String(20))
    razao_social = Column(String(255))
    
    # Contato adicional
    whatsapp = Column(String(20))
    instagram = Column(String(100))
    facebook = Column(String(100))
    site = Column(String(255))
    
    # Configurações
    horario_abertura = Column(String(5))  # HH:MM
    horario_fechamento = Column(String(5))  # HH:MM
    dias_funcionamento = Column(JSON)  # [1,2,3,4,5,6] = Seg a Sab
    
    # Opções de envio
    frete_padrao = Column(String(50))  # normal, expresso, agendado
    valor_frete_padrao = Column(Float, default=0)
    oferece_frete_gratis = Column(Boolean, default=False)
    valor_minimo_frete_gratis = Column(Float, default=0)
    
    # Política
    prazo_devolucao_dias = Column(Integer, default=30)
    permite_devolucao = Column(Boolean, default=True)
    taxa_reembolso_percentual = Column(Float, default=100)
    
    # Configurações de notificação
    notificar_novo_pedido = Column(Boolean, default=True)
    notificar_pagamento = Column(Boolean, default=True)
    notificar_estoque_baixo = Column(Boolean, default=True)
    
    # Status
    ativo = Column(Boolean, default=True, index=True)
    plano = Column(String(50), default="basico")  # basico, profissional, premium
    
    # Estatísticas
    total_vendas = Column(Float, default=0)
    total_pedidos = Column(Integer, default=0)
    total_clientes = Column(Integer, default=0)
    
    data_criacao = Column(DateTime, default=datetime.utcnow, index=True)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_cancelamento = Column(DateTime)

    # Relacionamentos
    usuarios = relationship('Usuario', back_populates='loja', cascade='all, delete-orphan')
    produtos = relationship('Produto', back_populates='loja', cascade='all, delete-orphan')
    clientes = relationship('Cliente', back_populates='loja', cascade='all, delete-orphan')
    pedidos = relationship('Pedido', back_populates='loja', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Loja {self.nome}>'

    def to_dict(self):
        """Converte loja para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'slug': self.slug,
            'email': self.email,
            'telefone': self.telefone,
            'logo_url': self.logo_url,
            'cor_primaria': self.cor_primaria,
            'cor_secundaria': self.cor_secundaria,
            'ativo': self.ativo,
            'plano': self.plano,
            'total_vendas': float(self.total_vendas),
            'total_pedidos': self.total_pedidos,
            'total_clientes': self.total_clientes,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
        }

    def to_dict_completo(self):
        """Retorna dicionário com todos os dados da loja"""
        dados = self.to_dict()
        dados.update({
            'endereco': self.endereco,
            'numero': self.numero,
            'complemento': self.complemento,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'cnpj': self.cnpj,
            'inscricao_estadual': self.inscricao_estadual,
            'razao_social': self.razao_social,
            'whatsapp': self.whatsapp,
            'instagram': self.instagram,
            'facebook': self.facebook,
            'site': self.site,
            'horario_abertura': self.horario_abertura,
            'horario_fechamento': self.horario_fechamento,
            'dias_funcionamento': self.dias_funcionamento or [],
            'valor_frete_padrao': float(self.valor_frete_padrao) if self.valor_frete_padrao else 0,
            'oferece_frete_gratis': self.oferece_frete_gratis,
            'valor_minimo_frete_gratis': float(self.valor_minimo_frete_gratis) if self.valor_minimo_frete_gratis else 0,
            'prazo_devolucao_dias': self.prazo_devolucao_dias,
            'permite_devolucao': self.permite_devolucao,
            'taxa_reembolso_percentual': float(self.taxa_reembolso_percentual),
            'banner_url': self.banner_url,
            'cor_sucesso': self.cor_sucesso,
            'cor_alerta': self.cor_alerta,
            'cor_erro': self.cor_erro,
        })
        return dados


class Usuario(Base):
    """Modelo de Usuário - gerenciadores da loja"""
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    loja_id = Column(Integer, ForeignKey('lojas.id'), nullable=False)
    
    # Autenticação
    email = Column(String(255), nullable=False, unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    
    # Dados pessoais
    nome = Column(String(255), nullable=False)
    telefone = Column(String(20))
    avatar_url = Column(String(500))
    
    # Permissões e papéis
    eh_admin = Column(Boolean, default=False)
    eh_gerente = Column(Boolean, default=False)
    permissoes = Column(JSON)  # Lista de permissões customizadas
    
    # Status
    ativo = Column(Boolean, default=True, index=True)
    verificado = Column(Boolean, default=False)
    
    # Segurança
    ultimo_acesso = Column(DateTime)
    tentativas_falhas = Column(Integer, default=0)
    bloqueado_ate = Column(DateTime)
    
    # Auditoria
    data_criacao = Column(DateTime, default=datetime.utcnow, index=True)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    criado_por_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)

    # Relacionamentos
    loja = relationship('Loja', back_populates='usuarios')
    criado_por = relationship('Usuario', remote_side=[id], foreign_keys=[criado_por_id])

    def __repr__(self):
        return f'<Usuario {self.email}>'

    def to_dict(self):
        """Converte usuário para dicionário"""
        return {
            'id': self.id,
            'loja_id': self.loja_id,
            'email': self.email,
            'nome': self.nome,
            'telefone': self.telefone,
            'avatar_url': self.avatar_url,
            'eh_admin': self.eh_admin,
            'eh_gerente': self.eh_gerente,
            'ativo': self.ativo,
            'verificado': self.verificado,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
        }

    def tem_permissao(self, permissao):
        """Verifica se usuário tem uma permissão específica"""
        if self.eh_admin:
            return True
        if not self.permissoes:
            return False
        return permissao in self.permissoes

    def bloquear_temporario(self, minutos=30):
        """Bloqueia usuário por tempo determinado"""
        from datetime import timedelta
        self.bloqueado_ate = datetime.utcnow() + timedelta(minutes=minutos)

    def está_bloqueado(self):
        """Verifica se usuário está bloqueado"""
        if not self.bloqueado_ate:
            return False
        if self.bloqueado_ate < datetime.utcnow():
            self.bloqueado_ate = None
            return False
        return True
