from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
)
from sqlalchemy.orm import relationship
from src.database import Base


class Produto(Base):
    """Modelo de Produto - itens no catálogo da loja"""
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    loja_id = Column(Integer, ForeignKey('lojas.id'), nullable=False)
    
    # Identificação
    nome = Column(String(255), nullable=False, index=True)
    descricao = Column(Text)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    codigo_barras = Column(String(100), unique=True)
    
    # Categorização
    categoria = Column(String(100), nullable=False, index=True)  # Camisetas, Calças, Vestidos, Sapatos, Acessórios
    subcategoria = Column(String(100))  # Blusa Manga Curta, Calça Jeans, etc
    colecao = Column(String(100))  # Coleção/Linha de produtos
    
    # Atributos
    tamanhos_disponiveis = Column(JSON)  # ["P", "M", "G", "GG"]
    cores_disponiveis = Column(JSON)  # ["preto", "branco", "azul"]
    material = Column(String(100))  # Algodão, Poliéster, Lã, etc
    
    # Preço
    preco = Column(Float, nullable=False)
    preco_original = Column(Float)  # Preço antes de desconto
    preco_custo = Column(Float)  # Preço de custo
    margem_lucro = Column(Float)  # Margem percentual
    
    # Estoque
    estoque_total = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=5)  # Quantidade mínima antes de alertar
    estoque_reservado = Column(Integer, default=0)  # Itens em pedidos não confirmados
    
    # Imagens e mídia
    imagem_principal_url = Column(String(500))
    imagens_urls = Column(JSON)  # Lista de URLs de outras imagens
    
    # Metadata
    peso = Column(Float)  # em gramas
    dimensoes = Column(String(100))  # "30x20x5" em cm
    largura = Column(Float)
    altura = Column(Float)
    profundidade = Column(Float)
    
    # SEO e visibilidade
    meta_descricao = Column(String(255))
    tags_busca = Column(JSON)  # ["moda", "feminino", "verão"]
    
    # Status
    ativo = Column(Boolean, default=True, index=True)
    destaque = Column(Boolean, default=False)  # Produto em destaque na loja
    promocao = Column(Boolean, default=False)
    data_inicio_promocao = Column(DateTime)
    data_fim_promocao = Column(DateTime)
    
    # Controle
    visualizacoes = Column(Integer, default=0)
    avaliacoes_media = Column(Float, default=0)
    numero_avaliacoes = Column(Integer, default=0)
    
    data_criacao = Column(DateTime, default=datetime.utcnow, index=True)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Relacionamentos
    loja = relationship('Loja', back_populates='produtos')
    itens_pedido = relationship('ItemPedido', back_populates='produto', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Produto {self.nome} (SKU: {self.sku})>'

    @property
    def estoque_disponivel(self):
        """Estoque disponível = total - reservado"""
        return max(0, self.estoque_total - self.estoque_reservado)

    @property
    def em_estoque(self):
        """Verifica se há estoque disponível"""
        return self.estoque_disponivel > 0

    @property
    def estoque_baixo(self):
        """Verifica se estoque está abaixo do mínimo"""
        return self.estoque_disponivel < self.estoque_minimo

    @property
    def preco_desconto_percentual(self):
        """Calcula percentual de desconto se houver preço original"""
        if not self.preco_original or self.preco_original == 0:
            return 0
        return ((self.preco_original - self.preco) / self.preco_original) * 100

    def to_dict(self, include_estoque=True):
        """Converte produto para dicionário"""
        dados = {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'sku': self.sku,
            'categoria': self.categoria,
            'subcategoria': self.subcategoria,
            'preco': float(self.preco),
            'preco_original': float(self.preco_original) if self.preco_original else None,
            'preco_desconto_percentual': self.preco_desconto_percentual,
            'imagem_principal_url': self.imagem_principal_url,
            'ativo': self.ativo,
            'destaque': self.destaque,
            'avaliacoes_media': float(self.avaliacoes_media) if self.avaliacoes_media else 0,
            'numero_avaliacoes': self.numero_avaliacoes,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
        }

        if include_estoque:
            dados.update({
                'estoque_total': self.estoque_total,
                'estoque_disponivel': self.estoque_disponivel,
                'em_estoque': self.em_estoque,
                'estoque_baixo': self.estoque_baixo,
                'tamanhos_disponiveis': self.tamanhos_disponiveis or [],
                'cores_disponiveis': self.cores_disponiveis or [],
            })

        return dados

    def to_dict_completo(self):
        """Retorna dicionário com todos os dados do produto"""
        dados = self.to_dict(include_estoque=True)
        dados.update({
            'id': self.id,
            'loja_id': self.loja_id,
            'codigo_barras': self.codigo_barras,
            'colecao': self.colecao,
            'material': self.material,
            'preco_custo': float(self.preco_custo) if self.preco_custo else None,
            'margem_lucro': float(self.margem_lucro) if self.margem_lucro else None,
            'estoque_minimo': self.estoque_minimo,
            'estoque_reservado': self.estoque_reservado,
            'imagens_urls': self.imagens_urls or [],
            'peso': float(self.peso) if self.peso else None,
            'dimensoes': self.dimensoes,
            'largura': float(self.largura) if self.largura else None,
            'altura': float(self.altura) if self.altura else None,
            'profundidade': float(self.profundidade) if self.profundidade else None,
            'meta_descricao': self.meta_descricao,
            'tags_busca': self.tags_busca or [],
            'promocao': self.promocao,
            'data_inicio_promocao': self.data_inicio_promocao.isoformat() if self.data_inicio_promocao else None,
            'data_fim_promocao': self.data_fim_promocao.isoformat() if self.data_fim_promocao else None,
            'visualizacoes': self.visualizacoes,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
        })
        return dados
