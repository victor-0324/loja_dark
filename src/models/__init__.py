"""
Ponto único de importação dos models.

Importar deste módulo (e não dos arquivos individuais) garante que todas
as classes sejam registradas em Base.metadata antes de qualquer
Base.metadata.create_all() -- evita o bug clássico de "tabela não criada
porque o model nunca foi importado".
"""

from src.database import Base
from src.models.loja_usuario import Loja, Usuario
from src.models.produto import Produto
from src.models.cliente import (
    Cliente,
    PreferenciaCliente,
    ProdutoFavorito,
    Interacao,
    Atendimento,
    CampanhaRecebida,
    CupomCliente,
)
from src.models.pedido import Pedido, ItemPedido, HistoricoStatusPedido, StatusPedido, MetodoPagamento

__all__ = [
    'Base',
    'Loja',
    'Usuario',
    'Produto',
    'Cliente',
    'PreferenciaCliente',
    'ProdutoFavorito',
    'Interacao',
    'Atendimento',
    'CampanhaRecebida',
    'CupomCliente',
    'Pedido',
    'ItemPedido',
    'HistoricoStatusPedido',
    'StatusPedido',
    'MetodoPagamento',
]
