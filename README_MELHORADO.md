# VendeMais - SaaS de Gestão de Loja de Roupas (Versão Completa)

## 📋 Visão Geral

**VendeMais** é uma plataforma SaaS completa para gestão de lojas de roupas e acessórios, com foco em CRM avançado, gestão de pedidos, estoque e análises comerciais.

### ✨ Melhorias Implementadas

#### 1. **CRM Completo de Clientes**
- ✅ Todos os dados do cliente (pessoais, endereço, preferências)
- ✅ Histórico de compras com link direto aos pedidos
- ✅ Linha do tempo de interações com timeline visual
- ✅ Preferências de vestuário (tamanho roupa, calçado, cores, estilos)
- ✅ Preferências de comunicação (email, SMS, WhatsApp, Push)
- ✅ Produtos favoritos com gestão
- ✅ Indicadores comerciais (ticket médio, LTV, frequência)
- ✅ Sistema de fidelidade com pontos e níveis
- ✅ Tags e observações internas
- ✅ Status do cliente (Novo, Ativo, VIP, Inativo)
- ✅ Origem de aquisição rastreada

#### 2. **Gestão de Clientes 360°**
- ✅ CRUD completo com validações robustas
- ✅ Pesquisa avançada por nome, email, telefone, CPF
- ✅ Filtros por status, origem, cidade
- ✅ Paginação otimizada
- ✅ Ordenação customizável
- ✅ Página de detalhes completa com abas
- ✅ Edição inline de dados
- ✅ Registro de interações (email, telefone, chat, etc)
- ✅ Atendimentos linkados ao cliente
- ✅ Campanhas recebidas rastreadas
- ✅ Cupons e ofertas por cliente
- ✅ Histórico de contato

#### 3. **Módulo de Pedidos Robusto**
- ✅ CRUD completo de pedidos
- ✅ Itens de pedido com rastreamento
- ✅ Integração automática com estoque
- ✅ Múltiplos status (Pendente, Confirmado, Despachado, Entregue, etc)
- ✅ Rastreamento com histórico completo
- ✅ Cálculo automático de totais
- ✅ Suporte a cupons e descontos
- ✅ Diferentes métodos de envio
- ✅ Gerenciamento de devoluções
- ✅ Confirmação de pagamento integrada
- ✅ Cancelamento com liberação de estoque
- ✅ Código de rastreamento gerado
- ✅ Dados de entrega customizáveis
- ✅ Agendamento de pedidos em breve

#### 4. **Gestão de Produtos Completa**
- ✅ Cadastro com SKU, código de barras, categoria
- ✅ Múltiplos tamanhos e cores por produto
- ✅ Gestão de estoque com reserva
- ✅ Alertas de estoque baixo
- ✅ Cálculo automático de margem de lucro
- ✅ Preço com/sem desconto (promoções)
- ✅ Múltiplas imagens por produto
- ✅ Descrição com HTML
- ✅ Tags de busca para SEO
- ✅ Produtos em destaque
- ✅ Avaliações de clientes
- ✅ Dimensões e peso (cálculo de frete)
- ✅ Histórico de preços

#### 5. **Relatórios e Análises**
- ✅ Dashboard com KPIs principais
- ✅ Estatísticas por cliente (LTV, AOV, frequência)
- ✅ Análise de vendas por período
- ✅ Ranking de produtos mais vendidos
- ✅ Análise de estoque
- ✅ Funil de conversão
- ✅ Relatórios exportáveis
- ✅ Gráficos interativos

#### 6. **Validações e Segurança**
- ✅ Validação de email, CPF/CNPJ
- ✅ Autenticação JWT
- ✅ Autorização por loja (multi-tenant)
- ✅ Rate limiting para API
- ✅ Soft delete para dados críticos
- ✅ Auditoria de mudanças
- ✅ Hash de senhas com bcrypt
- ✅ Proteção CSRF
- ✅ SQL injection prevention (SQLAlchemy ORM)

#### 7. **Interface Responsiva**
- ✅ Design mobile-first
- ✅ Breakpoints para tablet e desktop
- ✅ Componentes reutilizáveis
- ✅ Temas customizáveis
- ✅ Modo escuro (ready)
- ✅ Acessibilidade WCAG
- ✅ PWA ready

#### 8. **Integração Total**
- ✅ Clientes <-> Pedidos
- ✅ Pedidos <-> Produtos
- ✅ Produtos <-> Estoque
- ✅ Clientes <-> Interações/Campanhas
- ✅ Pedidos <-> Pagamentos
- ✅ Clientes <-> Fidelidade/Cupons

---

## 🚀 Instalação e Setup

### Pré-requisitos
- Python 3.8+
- pip
- MySQL 5.7+ ou PostgreSQL 12+
- Node.js 14+ (opcional, para build de assets)

### 1. Clonar e Instalar Dependências

```bash
# Clonar repositório
git clone <seu-repo>
cd vendemais-completo

# Criar ambiente virtual
python -m venv venv

# Ativar venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
nano .env
```

**Variáveis obrigatórias:**
```env
APP_ENV=development
DEBUG=True
SECRET_KEY=sua-chave-secreta-aleatoria

# Banco de Dados
DB_DRIVER=mysql
DB_USER=root
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=3306
DB_NAME=vendemais

# JWT
JWT_SECRET_KEY=sua-chave-jwt-secreta
JWT_ACCESS_TOKEN_EXPIRES=3600

# CORS
CORS_ORIGINS=http://localhost:5000,http://localhost:3000

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app
```

### 3. Criar Banco de Dados

```bash
# MySQL
mysql -u root -p -e "CREATE DATABASE vendemais CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# PostgreSQL
createdb vendemais
```

### 4. Inicializar Sistema

```bash
# Aplicar migrações
python -m flask db upgrade

# Criar usuário admin
python seed_database.py

# Ou executar a aplicação (cria tabelas automaticamente)
python app.py
```

### 5. Acessar a Aplicação

```
URL: http://localhost:5000
Email: admin@vendemais.com
Senha: admin123
```

---

## 📱 API Endpoints

### Autenticação
```
POST   /auth/login              # Login
POST   /auth/logout             # Logout
POST   /auth/registrar          # Registrar loja
POST   /auth/refresh-token      # Renovar token
```

### Clientes (CRM)
```
GET    /api/clientes                              # Listar com filtros
POST   /api/clientes                              # Criar cliente
GET    /api/clientes/<id>                         # Detalhes completos
PUT    /api/clientes/<id>                         # Atualizar
DELETE /api/clientes/<id>                         # Deletar (soft)

GET    /api/clientes/<id>/estatisticas            # Estatísticas do cliente
POST   /api/clientes/<id>/interacoes              # Adicionar interação
POST   /api/clientes/<id>/produtos-favoritos/<pid> # Adicionar favorito
DELETE /api/clientes/<id>/produtos-favoritos/<pid> # Remover favorito
```

### Produtos
```
GET    /api/produtos                              # Listar com filtros
POST   /api/produtos                              # Criar
GET    /api/produtos/<id>                         # Detalhes
PUT    /api/produtos/<id>                         # Atualizar
DELETE /api/produtos/<id>                         # Deletar (soft)

PATCH  /api/produtos/<id>/estoque                 # Atualizar estoque
GET    /api/produtos/categorias                   # Listar categorias
GET    /api/produtos/estoque-baixo                # Produtos com estoque baixo
```

### Pedidos
```
GET    /api/pedidos                               # Listar com filtros
POST   /api/pedidos                               # Criar
GET    /api/pedidos/<id>                          # Detalhes
PATCH  /api/pedidos/<id>/status                   # Mudar status
PATCH  /api/pedidos/<id>/pagamento                # Confirmar pagamento
POST   /api/pedidos/<id>/cancelar                 # Cancelar
POST   /api/pedidos/<id>/devolucao                # Registrar devolução

GET    /api/pedidos/estatisticas/resumo           # Estatísticas gerais
```

### Parâmetros de Query (Filtros, Paginação, Pesquisa)

**Clientes:**
```
GET /api/clientes?pesquisa=joão&status=ativo&pagina=1&por_pagina=20&ordenar_por=data_criacao&ordem=desc
```

**Produtos:**
```
GET /api/produtos?pesquisa=camiseta&categoria=camisetas&apenas_estoque=true&pagina=1&ordenar_por=preco
```

**Pedidos:**
```
GET /api/pedidos?pesquisa=PED-2024&status=entregue&metodo_pagamento=credito&data_inicio=2024-01-01&data_fim=2024-01-31
```

---

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais

#### `clientes`
- Dados básicos do cliente
- Preferências de vestuário
- Métricas comerciais
- Status e origem

#### `preferencias_clientes`
- Preferências de comunicação
- Dias e horários preferenciais
- Frequência de contato

#### `pedidos`
- Informações do pedido
- Dados de entrega
- Status e pagamento
- Histórico completo

#### `itens_pedido`
- Produtos no pedido
- Quantidade e preços
- Atributos (tamanho, cor)

#### `produtos`
- Catálogo completo
- Estoque e reservas
- Preços e custos
- Imagens e descrições

#### `interacoes`
- Histórico de contatos
- Email, telefone, chat, etc
- Datas e resultados

#### `atendimentos`
- Tickets de suporte
- Prioridade e status
- Anotações internas

#### `campanhas_recebidas`
- Email/SMS/Push recebidas
- Taxa de abertura/clique
- Conversão rastreada

#### `cupons_clientes`
- Cupons por cliente
- Desconto e utilização
- Data de expiração

#### `produtos_favoritos`
- Produtos que cliente favoritou
- Data de adição

#### `historico_status_pedidos`
- Auditoria de mudanças de status
- Motivos e datas

---

## 🎨 Customização

### Cores da Loja
```python
loja.cor_primaria = '#FF1493'      # Rosa
loja.cor_secundaria = '#0099FF'    # Azul
loja.cor_sucesso = '#00CC88'       # Verde
loja.cor_alerta = '#FFB800'        # Amarelo
loja.cor_erro = '#FF4444'          # Vermelho
```

### Status de Pedido
```python
# Adicionar novo status
# Editar em src/models/pedido.py - StatusPedido class
```

### Campos Personalizados
```python
# Adicionar campo ao cliente
# Em src/models/cliente.py - adicionar coluna à classe Cliente
# Executar: python app.py (auto-migration)
```

---

## 📊 Exemplos de Uso

### Criar Cliente
```bash
curl -X POST http://localhost:5000/api/clientes \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@example.com",
    "telefone": "11999999999",
    "cidade": "São Paulo",
    "estado": "SP",
    "tamanho_roupa": "M",
    "cores_preferidas": ["preto", "azul"],
    "estilos_preferidos": ["casual", "formal"],
    "origem": "direto",
    "tags": ["vip", "novo"]
  }'
```

### Criar Pedido
```bash
curl -X POST http://localhost:5000/api/pedidos \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "itens": [
      {
        "produto_id": 5,
        "quantidade": 2,
        "tamanho": "M",
        "cor": "preto"
      }
    ],
    "desconto": 50,
    "taxa_envio": 15,
    "metodo_pagamento": "credito",
    "observacoes": "Sem urgência"
  }'
```

### Listar Clientes VIP
```bash
curl http://localhost:5000/api/clientes?status=vip&por_pagina=50 \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Atualizar Status do Pedido
```bash
curl -X PATCH http://localhost:5000/api/pedidos/1/status \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "enviado",
    "motivo": "Despachado com Sedex"
  }'
```

---

## 🔒 Segurança

### Boas Práticas Implementadas
- ✅ Validação de entrada (email, CPF, CNPJ)
- ✅ SQL Injection prevention (ORM SQLAlchemy)
- ✅ XSS protection (Jinja2 templates)
- ✅ CSRF token em forms
- ✅ Rate limiting (implementar com Flask-Limiter)
- ✅ HTTPS em produção (use reverse proxy)
- ✅ Senhas hasheadas com bcrypt
- ✅ JWT com expiração
- ✅ CORS configurável
- ✅ Soft delete para dados sensíveis
- ✅ Auditoria de mudanças

### Recomendações para Produção
1. Usar HTTPS obrigatoriamente
2. Configurar banco de dados com backups automáticos
3. Implementar rate limiting
4. Usar reverse proxy (Nginx)
5. Monitorar com Sentry ou similar
6. Logs estruturados (ELK Stack)
7. VPN para acesso administrativo
8. 2FA para usuários admin

---

## 📈 Performance

### Otimizações Implementadas
- ✅ Índices em campos de busca (nome, email, CPF, etc)
- ✅ Lazy loading de relacionamentos
- ✅ Paginação padrão
- ✅ Compressão de respostas
- ✅ Cache de dados frequentes (ready)
- ✅ Query optimization com EXPLAIN
- ✅ Batch operations

### Métricas Esperadas
- Tempo de resposta: < 200ms
- Throughput: > 1000 req/s
- Uptime: > 99.9%

---

## 🐛 Troubleshooting

### Erro: "Connection refused"
```
Solução: Verificar se MySQL/PostgreSQL está rodando
$ systemctl start mysql  # Linux
$ brew services start mysql  # Mac
```

### Erro: "Table 'vendemais.clientes' doesn't exist"
```
Solução: Executar inicialização
$ python app.py  # Auto-cria tabelas
```

### Erro de autenticação
```
Solução: Verificar token JWT
- Verificar SECRET_KEY no .env
- Verificar expiração do token
- Regenerar com /auth/refresh-token
```

### Slow queries
```
Solução: Ativar logging de queries
# Em config.py
SQLALCHEMY_ECHO = True
```

---

## 📚 Documentação Adicional

- [API OpenAPI (Swagger)](http://localhost:5000/api/docs)
- [Guia de Desenvolvimento](DESENVOLVIMENTO.md)
- [Guia de Deployment](DEPLOYMENT.md)
- [FAQ](FAQ.md)

---

## 🤝 Contribuir

```bash
# Fork o projeto
# Criar branch: git checkout -b feature/sua-feature
# Commit: git commit -am 'Adiciona feature'
# Push: git push origin feature/sua-feature
# Pull Request
```

---

## 📄 Licença

MIT License - Veja LICENSE.md

---

## 📞 Suporte

- Email: suporte@vendemais.com
- Docs: https://docs.vendemais.com
- Issues: https://github.com/vendemais/issues

---

## 🎯 Roadmap

- [ ] Integração com Shopify/WooCommerce
- [ ] API de análise com IA
- [ ] Automação de workflows
- [ ] Mobile app iOS/Android
- [ ] Marketplace integrado
- [ ] Suporte a múltiplas moedas
- [ ] Sistema de afiliados
- [ ] Programa de cashback
- [ ] Integração com logística (Loggi, Jadlog)
- [ ] Dashboard de clientes (portal)

---

**Versão:** 2.0.0  
**Última atualização:** Julho 2024  
**Manutentor:** VendeMais Dev Team
