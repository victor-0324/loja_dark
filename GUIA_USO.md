# 📖 Guia Prático de Uso - VendeMais

## 🎯 Objetivo

Este guia ajuda você a usar o **VendeMais** de forma eficiente, desde a configuração inicial até o gerenciamento completo de sua loja.

---

## 1️⃣ Configuração Inicial

### Passo 1: Criar Loja

```bash
# Acessar a aplicação
http://localhost:5000/cadastro

# Preencher:
- Nome da Loja: Sua loja
- Email: seu@email.com
- Telefone: (11) 9999-9999
- CNPJ: 12.345.678/0001-90
- Cores: Primária #FF1493, Secundária #0099FF
```

### Passo 2: Criar Usuário Admin

```bash
POST /auth/registrar
{
  "email": "admin@sualojavendemais.com",
  "senha": "SenhaForte123!",
  "nome": "Seu Nome",
  "eh_admin": true
}
```

### Passo 3: Configurar Loja

**Dashboard → Configurações:**
- [ ] Logo da loja
- [ ] Cores da marca
- [ ] Endereço e contato
- [ ] Política de devolução
- [ ] Frete padrão
- [ ] Horário de funcionamento

---

## 2️⃣ Gestão de Produtos

### Cadastrar Produto

**Menu → Produtos → Novo Produto**

```
Informação Obrigatória:
- Nome: "Camiseta Básica"
- SKU: "CAM-BAS-001"
- Categoria: "Camisetas"
- Preço: R$ 49,90
- Estoque: 50

Informação Recomendada:
- Cores: ["Preto", "Branco", "Azul"]
- Tamanhos: ["P", "M", "G", "GG"]
- Material: "100% Algodão"
- Imagem: Upload
- Descrição: Detalhar características
```

### Gerenciar Estoque

**Produtos → Estoque:**

```
Operações:
1. Atualizar: Define quantidade exata
2. Adicionar: Soma quantidade (entrada)
3. Remover: Reduz quantidade (saída)

Alertas:
- Estoque baixo: Quando < quantidade mínima
- Saiba: Menu → Alertas → Estoque Baixo
```

### Criar Promoção

**Produtos → [Produto] → Editar:**

```
- Ativar Promoção: ☑️
- Preço Original: R$ 99,90
- Preço com Desconto: R$ 69,90
- Data Início: 01/07/2024
- Data Fim: 31/07/2024

Resultado: Automaticamente calcula -30% no produto
```

---

## 3️⃣ Gestão de Clientes (CRM)

### Cadastrar Cliente

**Menu → Clientes → Novo Cliente**

**Dados Essenciais:**
```
- Nome: "Maria Silva"
- Email: maria@email.com
- Telefone: (11) 98888-7777
- CPF: 123.456.789-00
```

**Dados de Endereço:**
```
- Endereço: Rua das Flores, 123
- Número: 123
- Complemento: Apto 456
- Cidade: São Paulo
- Estado: SP
- CEP: 01234-567
```

**Preferências (Importante!):**
```
- Tamanho de Roupa: M
- Tamanho de Calçado: 37
- Cores Preferidas: Preto, Azul, Rosa
- Estilos: Casual, Minimalista
- Origem: Redes Sociais, Indicação, Google, etc
```

### Ver Detalhes do Cliente

**Clientes → [Cliente] → Detalhes**

Você verá:

**📊 Indicadores:**
- Total de pedidos
- Valor total gasto
- Ticket médio
- Nível de fidelidade
- Pontos acumulados
- Cupons disponíveis

**📋 Abas:**

**1. Dados Pessoais**
- Todos os dados cadastrados
- Editar em tempo real
- Observações internas

**2. Histórico de Compras**
- Lista de pedidos
- Status de cada pedido
- Datas e valores
- Link para detalhes do pedido

**3. Interações**
- Email enviados
- Telefonemas registrados
- Chats e mensagens
- Datas e resultados

**4. Preferências**
- Email marketing (ativar/desativar)
- SMS, WhatsApp, Push
- Frequência preferida
- Dias e horários

**5. Linha do Tempo**
- Visualização cronológica
- Pedidos, interações, eventos
- Filtros por tipo

### Registrar Interação

**Clientes → [Cliente] → Nova Interação**

```
- Tipo: Email, Telefone, Chat, Redes Sociais, Presencial
- Assunto: "Dúvida sobre tamanho"
- Descrição: Detalhes da conversa
- Resultado: Bem-sucedida, Pendente, Falha, Agendada
- Próximo Contato: Data opcional

Resultado: Interação fica no histórico do cliente
```

### Adicionar a Favoritos

**Clientes → [Cliente] → Produtos Favoritos**

```
1. Clicar "+ Adicionar Favorito"
2. Pesquisar produto
3. Clicar em Adicionar
4. Produto aparece na aba "Preferências"

Uso: Sugerir produtos similares, oferecer nova cor, etc
```

### Filtrar Clientes

**Clientes:**

```
Pesquisa: Nome, Email, Telefone, CPF
Filtros:
- Status: Novo, Ativo, VIP, Inativo
- Origem: Direto, Indicação, Redes Sociais, Google, etc
- Cidade: São Paulo, Rio de Janeiro, etc

Ordenar por: Nome, Data de Cadastro, Valor Gasto
```

---

## 4️⃣ Gestão de Pedidos

### Criar Pedido

**Menu → Pedidos → Novo Pedido**

**Cliente:**
```
1. Selecionar cliente (ou criar novo)
2. Se novo, preencher dados
```

**Itens:**
```
1. Clicar "+ Adicionar Item"
2. Selecionar produto
3. Escolher tamanho e cor
4. Informar quantidade
5. Preço unitário (já vem do catálogo)
6. Desconto do item (opcional)
7. Adicionar mais itens se necessário
```

**Totais (Automático):**
```
- Subtotal: Soma dos itens
- Desconto: Redução geral
- Frete: Taxa de envio
- Serviço: Taxa de embalagem
- Total: Cálculo automático
```

**Endereço de Entrega:**
```
Opção 1: Usar endereço do cliente
Opção 2: Editar endereço específico
- Rua, número, complemento
- Cidade, estado, CEP
```

**Envio:**
```
- Transportadora: Correios, Sedex, Loggi, Jadlog
- Tipo: Normal, Expresso, Agendado
- Data entrega prevista (automática)
```

**Pagamento:**
```
- Método: Crédito, Débito, PIX, Boleto, Dinheiro
- Status: Pendente, Processando, Aprovado, Reprovado
```

### Rastrear Pedido

**Pedidos → [Pedido]**

**Informações:**
```
- Número: PED-2024-00001
- Código de rastreamento: (gerado automaticamente)
- Status: Pendente → Confirmado → Despachado → Entregue
```

**Histórico de Status:**
```
- Data e hora de cada mudança
- Motivo da mudança
- Quem fez a mudança
- Observações internas
```

**Itens do Pedido:**
```
- Produto, tamanho, cor
- Quantidade e preço
- Desconto aplicado
- Subtotal
```

### Alterar Status

**Pedidos → [Pedido] → Alterar Status**

**Fluxo Recomendado:**
```
1. PENDENTE (novo pedido)
   ↓
2. CONFIRMADO (cliente confirmou)
   ↓
3. PROCESSANDO (separando produtos)
   ↓
4. DESPACHADO (saiu da loja)
   ↓
5. ENVIADO (entregue à transportadora)
   ↓
6. ENTREGUE (cliente recebeu)

Alternativas:
- CANCELADO (a qualquer momento antes de enviado)
- DEVOLVIDO (após entregue)
```

### Confirmar Pagamento

**Pedidos → [Pedido] → Confirmação de Pagamento**

```
- Status: Aprovado, Reprovado, Reembolsado
- Data: Automática
- Número da Transação: PIX, Boleto, etc

Se Aprovado + Status Pendente:
→ Pedido passa automaticamente para CONFIRMADO
```

### Cancelar Pedido

**Pedidos → [Pedido] → Cancelar**

```
Condições:
- Pedido deve estar em PENDENTE ou CONFIRMADO
- Após enviado não pode cancelar (deve abrir devolução)

Ao Cancelar:
- Estoque é liberado
- Histórico fica registrado
- Cliente é notificado
```

### Registrar Devolução

**Pedidos → [Pedido] → Registrar Devolução**

```
Condições:
- Pedido deve estar ENTREGUE
- Preencher motivo da devolução

Dados:
- Data de devolução
- Motivo: Defeito, Não gostou, Tamanho, etc
- Valor de reembolso (pode ser parcial)

Resultado:
- Status muda para DEVOLVIDO
- Histórico fica registrado
- Pode reabrir para trocas
```

---

## 5️⃣ Análises e Relatórios

### Dashboard Principal

**Menu → Dashboard**

Visualiza:
```
- Total de vendas (período)
- Número de pedidos
- Número de clientes ativos
- Produtos mais vendidos
- Gráficos de vendas
- Últimos pedidos
- Alertas (estoque baixo, etc)
```

### Estatísticas de Cliente

**Clientes → [Cliente] → Estatísticas**

```
Metricas Gerais:
- Total de pedidos
- Valor total gasto
- Ticket médio
- Frequência de compras
- Última compra

Por Período:
- Últimos 30 dias
- Últimos 90 dias
- Último ano

Fidelidade:
- Nível atual
- Pontos acumulados
- Cupons disponíveis
```

### Estatísticas de Pedidos

**Menu → Relatórios → Pedidos**

```
- Total de pedidos (geral, mês, ano)
- Por status: Pendente, Confirmado, Entregue, etc
- Por método de pagamento
- Valor total de vendas
- Valor médio de pedido
- Período customizado
```

### Produtos com Estoque Baixo

**Menu → Alertas → Estoque Baixo**

```
Lista automática de:
- Produto
- Estoque atual
- Estoque mínimo
- Quanto falta
- Ação: Aumentar estoque
```

---

## 6️⃣ Interações e Follow-up

### Workflow de Cliente Novo

```
1. Cliente cadastrado → Status: NOVO

2. Primeira compra?
   SIM → Mudar para ATIVO
   NÃO → Registrar interação (email, SMS, etc)

3. Cliente após 1ª compra → Status: ATIVO
   - Acompanhar com pedidos futuros
   - Registrar todas as interações

4. Cliente com compras acima de R$ 5.000
   → Status: VIP
   → Oferecer benefícios especiais
   → Cupons exclusivos
   → Atendimento prioritário

5. Sem compras por 6 meses
   → Status: INATIVO
   → Criar campanha de retorno
   → Oferecer cupom de volta
```

### Registrar Contato com Cliente

**Clientes → [Cliente] → Nova Interação**

**Exemplos de Uso:**

**Email de Boas-vindas:**
```
Tipo: Email
Assunto: Bem-vindo à Loja!
Descrição: Enviado email de boas-vindas
Resultado: Bem-sucedida
```

**Acompanhamento de Pedido:**
```
Tipo: Email ou SMS
Assunto: Seu pedido foi enviado!
Descrição: Informado código de rastreamento
Resultado: Bem-sucedida
Próximo Contato: 3 dias após entrega
```

**Promoção:**
```
Tipo: Email ou WhatsApp
Assunto: Promoção exclusiva para você
Descrição: Cupom 20% de desconto em camisetas
Resultado: Bem-sucedida
Próximo Contato: Sem agenda
```

**Pesquisa de Satisfação:**
```
Tipo: Email
Assunto: Avalie sua experiência
Descrição: Questionário de satisfação
Resultado: Pendente (aguardando resposta)
Próximo Contato: 7 dias se não responder
```

---

## 7️⃣ Dicas e Boas Práticas

### Para Aumentar Vendas

1. **Segmentar Clientes:**
   - Criar tags: "gosto de camisetas", "prefere azul", "apressa"
   - Enviar ofertas direcionadas
   - Promoção por tamanho/cor preferida

2. **Fidelização:**
   - Programa de pontos (10 pontos por real gasto)
   - Cupom após cada 5ª compra
   - Status VIP com benefícios

3. **Acompanhamento:**
   - Email 24h após compra (confirmação)
   - Email 2 dias antes de chegar (rastreamento)
   - Email 3 dias após entrega (avaliação)
   - Email em aniversário (cupom de presente)

4. **Cross-selling:**
   - Ver produtos favoritos do cliente
   - Sugerir combos (camiseta + shorts)
   - Oferecer complementos (meias, cinto)

### Para Reduzir Devoluções

1. **Informações Completas:**
   - Descrever bem tamanhos (com tabela)
   - Múltiplas imagens do produto
   - Avaliações de quem já comprou

2. **Atendimento Pré-compra:**
   - Chat ao vivo durante horário
   - FAQ detalhado de tamanhos
   - Sugerir tamanho baseado em histórico

3. **Pós-compra:**
   - Email com dicas de cuidado
   - Política de troca clara
   - Fácil abrir devoluções

### Para Melhorar Conversão

1. **Produtos em Destaque:**
   - Marcar produtos best-sellers como "Destaque"
   - Rotacionar semanalmente
   - Combinar com promoção

2. **Pesquisa de Cliente:**
   - Registrar preferências (cores, estilos, tamanhos)
   - Usar para sugestões futuras
   - Análise de tendências

3. **Relacionamento:**
   - Registrar todas as interações
   - Linha do tempo do cliente
   - Histórico de preferências e compras

---

## 8️⃣ Troubleshooting Comum

### "Estoque aparece errado"

**Verificar:**
```
1. Ir em Produtos → [Produto]
2. Ver estoque_total vs estoque_disponível
3. Se menor que total → há reservas pendentes
4. Verificar pedidos não confirmados
5. Liberar estoque de pedidos cancelados
```

### "Cliente não aparece na pesquisa"

**Verificar:**
```
1. Filtro "Apenas Ativos" está ligado?
   → Se cliente é inativo, mudar filtro
2. Pesquisa exata (nome completo)?
   → Tentar apenas primeiro nome
3. Email correto?
   → Clicar na tabela para editar
4. Cliente foi soft-deleted?
   → Não pode recuperar via UI (contato suporte)
```

### "Não consigo criar pedido"

**Verificar:**
```
1. Cliente selecionado?
   → Obrigatório selecionar cliente
2. Produto em estoque?
   → Ver estoque_disponivel > quantidade
3. Endereço completo?
   → Preencher rua, número, cidade, CEP
4. Preço informado?
   → Verificar campo de preço unitário
```

### "Status do pedido não muda"

**Verificar:**
```
1. Permissão do usuário
   → Apenas admin pode mudar status
2. Status anterior bloqueado?
   → Pedido cancelado não pode voltar
3. Botão não responde?
   → Atualizar página (F5)
   → Verificar conexão
4. Tentar em outro navegador
```

---

## 9️⃣ Atalhos Teclado

```
Ctrl + K        Busca rápida
Ctrl + N        Novo cliente
Ctrl + Shift + S Salvar (em formulários)
Enter           Submeter form modal
Esc             Fechar modal
```

---

## 🔟 Checklist de Startup

Antes de abrir ao público:

- [ ] Loja configurada com logo e cores
- [ ] Pelo menos 20 produtos cadastrados
- [ ] Categorias criadas
- [ ] Preços corrigidos
- [ ] Fotos dos produtos (mínimo 2 por produto)
- [ ] Descrições completas
- [ ] Tamanhos e cores atualizados
- [ ] Estoque verificado
- [ ] Frete configurado
- [ ] Políticas claras (devolução, trocas)
- [ ] Email de contato testado
- [ ] 1º cliente teste criado
- [ ] 1º pedido de teste criado
- [ ] Fluxo de compra testado
- [ ] Email de confirmação configurado
- [ ] Backup do banco de dados
- [ ] Time treinado
- [ ] Documentação acessível

---

**Dúvidas?** Entre em contato: suporte@vendemais.com  
**Documentação completa:** https://docs.vendemais.com  
**Versão deste guia:** 2.0 | Julho 2024
