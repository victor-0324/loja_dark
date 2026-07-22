"""
Script para popular banco de dados com dados de teste.
Cria: 1 loja, 1 usuário admin, 5 produtos, 3 clientes, 5 pedidos
"""

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from src import create_app
from src.database import DBConnectionHendler
from src.models import (
    Loja, Usuario, Produto, Cliente, Pedido, ItemPedido,
    PreferenciaCliente, Interacao
)

app = create_app('development')

def seed_database():
    """Popula o banco com dados de teste"""
    db_handler = DBConnectionHendler()
    session = db_handler.get_session()

    try:
        # Criar Loja
        loja = Loja(
            nome='Minha Loja de Moda',
            email='admin@minhaloja.com',
            telefone='(11) 98765-4321',
            endereco='Rua das Flores, 123',
            numero='123',
            cidade='São Paulo',
            estado='SP',
            cep='01234-567',
            cnpj='12.345.678/0001-90',
            cor_primaria='#FF1493',
            cor_secundaria='#0099FF',
        )
        session.add(loja)
        session.flush()

        # Criar Usuário Admin
        admin = Usuario(
            loja_id=loja.id,
            email='admin@minhaloja.com',
            senha_hash=generate_password_hash('admin123'),
            nome='Administrador',
            eh_admin=True,
            ativo=True,
            verificado=True
        )
        session.add(admin)

        # Criar Produtos
        produtos_dados = [
            {
                'nome': 'Camiseta Básica Preta',
                'sku': 'CAM-BAS-001',
                'categoria': 'Camisetas',
                'preco': 49.90,
                'preco_custo': 20.00,
                'estoque_total': 50,
                'cores_disponiveis': ['Preto', 'Branco', 'Azul'],
                'tamanhos_disponiveis': ['P', 'M', 'G', 'GG'],
            },
            {
                'nome': 'Calça Jeans Azul',
                'sku': 'CAL-JEAN-001',
                'categoria': 'Calças',
                'preco': 89.90,
                'preco_custo': 35.00,
                'estoque_total': 30,
                'cores_disponiveis': ['Azul', 'Preto'],
                'tamanhos_disponiveis': ['P', 'M', 'G', 'GG'],
            },
            {
                'nome': 'Vestido Floral',
                'sku': 'VES-FLOR-001',
                'categoria': 'Vestidos',
                'preco': 129.90,
                'preco_custo': 50.00,
                'estoque_total': 20,
                'cores_disponiveis': ['Flores', 'Rosa'],
                'tamanhos_disponiveis': ['P', 'M', 'G'],
            },
            {
                'nome': 'Jaqueta de Couro',
                'sku': 'JAC-COURO-001',
                'categoria': 'Jaquetas',
                'preco': 199.90,
                'preco_custo': 80.00,
                'estoque_total': 15,
                'cores_disponiveis': ['Preto', 'Marrom'],
                'tamanhos_disponiveis': ['P', 'M', 'G', 'GG'],
            },
            {
                'nome': 'Shorts de Praia',
                'sku': 'SHO-PRAIA-001',
                'categoria': 'Shorts',
                'preco': 59.90,
                'preco_custo': 22.00,
                'estoque_total': 40,
                'cores_disponiveis': ['Azul', 'Verde', 'Rosa'],
                'tamanhos_disponiveis': ['P', 'M', 'G'],
            },
        ]

        produtos = []
        for dados in produtos_dados:
            produto = Produto(
                loja_id=loja.id,
                **dados,
                descricao=f'Descrição do produto {dados["nome"]}',
                ativo=True,
                destaque=True,
            )
            produtos.append(produto)
            session.add(produto)

        session.flush()

        # Criar Clientes
        clientes_dados = [
            {
                'nome': 'João Silva',
                'email': 'joao@example.com',
                'telefone': '(11) 99999-8888',
                'cpf_cnpj': '123.456.789-00',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'tamanho_roupa': 'M',
                'cores_preferidas': ['Preto', 'Azul'],
                'estilos_preferidos': ['Casual'],
            },
            {
                'nome': 'Maria Santos',
                'email': 'maria@example.com',
                'telefone': '(11) 98888-7777',
                'cpf_cnpj': '987.654.321-00',
                'cidade': 'Rio de Janeiro',
                'estado': 'RJ',
                'tamanho_roupa': 'P',
                'cores_preferidas': ['Rosa', 'Branco'],
                'estilos_preferidos': ['Formal', 'Casual'],
            },
            {
                'nome': 'Carlos Oliveira',
                'email': 'carlos@example.com',
                'telefone': '(11) 97777-6666',
                'cidade': 'Brasília',
                'estado': 'DF',
                'tamanho_roupa': 'G',
                'cores_preferidas': ['Preto'],
                'estilos_preferidos': ['Casual'],
            },
        ]

        clientes = []
        for dados in clientes_dados:
            cliente = Cliente(
                loja_id=loja.id,
                **dados,
                status='ativo',
                origem='direto',
            )
            clientes.append(cliente)
            session.add(cliente)

        session.flush()

        # Criar Pedidos
        data_hoje = datetime.utcnow()
        for i, cliente in enumerate(clientes[:2]):
            for j in range(2 if i == 0 else 1):
                data_pedido = data_hoje - timedelta(days=7+j*3)
                
                pedido = Pedido(
                    loja_id=loja.id,
                    cliente_id=cliente.id,
                    numero_pedido=f'PED-2024-{(i+1)*100+(j+1):05d}',
                    subtotal=150.00 + j*50,
                    desconto=0,
                    taxa_envio=15.00,
                    valor_total=165.00 + j*50,
                    status='entregue' if j == 0 else 'confirmado',
                    metodo_pagamento='credito',
                    status_pagamento='aprovado',
                    endereco_entrega=cliente.endereco or 'Rua de Teste',
                    cidade_entrega=cliente.cidade,
                    estado_entrega=cliente.estado,
                    data_pedido=data_pedido,
                    data_confirmacao=data_pedido + timedelta(hours=1) if j == 0 else None,
                    data_entrega_realizada=data_pedido + timedelta(days=5) if j == 0 else None,
                )

                # Adicionar itens ao pedido
                item1 = ItemPedido(
                    pedido_id=None,
                    produto_id=produtos[0].id,
                    produto_nome=produtos[0].nome,
                    produto_sku=produtos[0].sku,
                    tamanho='M',
                    cor='Preto',
                    quantidade=2,
                    preco_unitario=49.90,
                    desconto_item=0,
                )
                pedido.itens.append(item1)

                item2 = ItemPedido(
                    pedido_id=None,
                    produto_id=produtos[1].id,
                    produto_nome=produtos[1].nome,
                    produto_sku=produtos[1].sku,
                    tamanho='M',
                    cor='Azul',
                    quantidade=1,
                    preco_unitario=89.90,
                    desconto_item=10.00,
                )
                pedido.itens.append(item2)

                session.add(pedido)

        session.flush()

        # Atualizar métricas do cliente
        for cliente in clientes:
            cliente.calcular_metricas()

        # Criar Preferências de Cliente
        for cliente in clientes:
            pref = PreferenciaCliente(
                cliente_id=cliente.id,
                email_marketing=True,
                sms_marketing=False,
                whatsapp_marketing=False,
            )
            session.add(pref)

        # Criar Interações
        for i, cliente in enumerate(clientes[:2]):
            interacao = Interacao(
                cliente_id=cliente.id,
                loja_id=loja.id,
                usuario_id=admin.id,
                tipo='email',
                assunto='Bem-vindo à loja!',
                descricao='Email de boas-vindas enviado',
                resultado='bem_sucedida',
                data_interacao=cliente.data_criacao,
            )
            session.add(interacao)

        # Commit
        session.commit()

        print("✅ Banco de dados populado com sucesso!")
        print("\n📊 Dados criados:")
        print(f"   - 1 Loja: {loja.nome}")
        print(f"   - 1 Usuário Admin: {admin.email}")
        print(f"   - 5 Produtos")
        print(f"   - 3 Clientes")
        print(f"   - 5 Pedidos")
        print("\n🔐 Credenciais de teste:")
        print(f"   Email: {admin.email}")
        print(f"   Senha: admin123")
        print("\n🚀 Acesse: http://localhost:5000")

    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao popular banco: {e}")
        raise
    finally:
        db_handler.remove_session()


if __name__ == '__main__':
    with app.app_context():
        seed_database()
