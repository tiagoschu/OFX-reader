# Guia de Importação de Vendas no Cartão de Crédito

## 📋 Visão Geral

O OFX Consolidador Pro agora suporta importação de vendas realizadas em cartões de crédito através de arquivos CSV. O sistema:
- ✅ Importa vendas com múltiplas parcelas
- ✅ Gera automaticamente as parcelas com progressão mensal
- ✅ Vincula parcelas com recebimentos OFX
- ✅ Ajusta última parcela para evitar diferenças de centavos
- ✅ Suporta qualquer adquirente (Cielo, Stone, Rede, etc.)

## 🗂️ Nova Estrutura de Abas

A estrutura de abas foi reorganizada para agrupar as importações:

1. **🏠 Início** - Dashboard principal
2. **📥 OFX Import** - Importação de extratos bancários OFX
3. **📄 NFSe Import** - Importação de notas fiscais eletrônicas
4. **💳 Vendas Cartão** - **NOVO** - Importação de vendas de cartão
5. **🔗 Análise NFSe** - Análise de vinculação NFSe ↔ OFX
6. **🔍 Não Vinculados** - Itens pendentes de vinculação
7. *Demais abas...*

## 📁 Formato do Arquivo CSV

### Template Disponível

Você pode baixar o modelo CSV diretamente na interface:
- Clique no botão **"📋 Baixar Modelo CSV"** na aba **💳 Vendas Cartão**
- Ou copie o arquivo `templates/vendas_cartao_modelo.csv`

### Campos Obrigatórios (*)

Os seguintes campos são **obrigatórios** e devem estar preenchidos:

1. **CPF/CNPJ do estabelecimento*** - CPF ou CNPJ do cliente/estabelecimento
2. **Quantidade total de parcelas*** - Número de parcelas (1 para à vista)
3. **Valor bruto*** - Valor total da venda antes de taxas
4. **Taxa/tarifa*** - Valor da taxa cobrada pela adquirente
5. **Valor líquido*** - Valor que será recebido (bruto - taxa)
6. **Data do lançamento*** - Data da transação/venda
7. **Data prevista do pagamento*** - Data prevista do primeiro recebimento

### Campos Opcionais

Todos os demais campos são opcionais, mas recomendados para melhor rastreamento:

- **Data da venda** - Data da venda (DD/MM/YYYY)
- **Hora da venda** - Hora da venda (HH:MM:SS)
- **Estabelecimento** - Nome do estabelecimento
- **Forma de pagamento** - Ex: "Crédito parcelado", "Crédito à vista", "Débito"
- **Bandeira** - Ex: Visa, Mastercard, Elo, Amex
- **Status da venda** - Ex: "Aprovada", "Cancelada"
- **Tipo de lançamento** - Ex: "Venda", "Estorno"
- **Modalidade** - Ex: "Parcelado", "À vista", "Débito"
- **Tipo de captura** - Ex: "Online", "Presencial"
- **Documento de origem** - Referência do documento
- **Origem do valor** - Origem da transação
- **Motivo** - Motivo da transação
- **Código de autorização** - Código de autorização da adquirente
- **NSU/DOC** - Número Sequencial Único
- **Código da venda** - ID interno da venda
- **TID** - Transaction ID
- **Origem do cartão** - Ex: "Nacional", "Internacional"
- **Nome** - Nome do cliente
- **Email** - Email do cliente
- **Telefone** - Telefone do cliente
- **CPF** - CPF do cliente (diferente do estabelecimento)
- **Adquirente** - Nome da adquirente (Cielo, Stone, Rede, etc.)

### Exemplo de CSV

```csv
Data da venda,Hora da venda,Estabelecimento,CPF/CNPJ do estabelecimento,Forma de pagamento,Quantidade total de parcelas,Bandeira,Valor bruto,Taxa/tarifa,Valor líquido,Status da venda,Tipo de lançamento,Modalidade,Tipo de captura,Documento de origem,Origem do valor,Motivo,Data do lançamento,Data prevista do pagamento,Código de autorização,NSU/DOC,Código da venda,TID,Origem do cartão,Nome,Email,Telefone,CPF,Adquirente
10/05/2025,14:30:00,Loja Exemplo Ltda,12.345.678/0001-90,Crédito parcelado,4,Visa,100.00,4.49,95.51,Aprovada,Venda,Parcelado,Online,DOC123,Venda,Compra aprovada,10/05/2025,10/06/2025,AUTH001,NSU12345,VENDA001,TID001,Nacional,João Silva,joao@email.com,11999999999,12345678900,Cielo
```

## 🔄 Como Funciona

### 1. Geração Automática de Parcelas

Quando você importa uma venda com 4 parcelas de R$ 95,51:

```
Venda: R$ 95,51 ÷ 4 parcelas
├─ Parcela 1/4: R$ 23,88 - Data: 10/06/2025
├─ Parcela 2/4: R$ 23,88 - Data: 10/07/2025
├─ Parcela 3/4: R$ 23,88 - Data: 10/08/2025
└─ Parcela 4/4: R$ 23,87 - Data: 10/09/2025 ← Última parcela ajustada
                                              Total: R$ 95,51 ✓
```

**Observações:**
- As datas progridem mensalmente (usando `relativedelta`)
- A última parcela carrega o "resto" para evitar diferença de centavos
- Cada parcela é vinculada independentemente ao OFX

### 2. Vinculação com OFX

O sistema busca recebimentos OFX que correspondam a cada parcela usando:

**Tolerância de Data:** ±5 dias da data prevista
**Tolerância de Valor:** ±R$ 0,10 do valor da parcela

**Exemplo:**
```
Parcela esperada: R$ 23,88 em 10/06/2025

✓ MATCH encontrado:
  - Data OFX: 12/06/2025 (diferença: 2 dias)
  - Valor OFX: R$ 23,90 (diferença: R$ 0,02)
  - Status: VINCULADO ✓
```

### 3. Múltiplos Matches

Se houver múltiplas transações OFX que correspondam à mesma parcela:
- O sistema usa a **PRIMEIRA OCORRÊNCIA** (ordenada por data)
- Um aviso detalhado é registrado no log mostrando todas as opções
- Você pode revisar manualmente na aba "Não Vinculados" se necessário

## 🚀 Passo a Passo de Uso

### 1. Importar Arquivo CSV

1. Acesse a aba **💳 Vendas Cartão**
2. Clique em **"📂 Selecionar CSV de Vendas"**
3. Escolha seu arquivo CSV
4. Aguarde o processamento

**O sistema irá:**
- Validar campos obrigatórios
- Gerar parcelas automaticamente
- Mostrar estatísticas de importação
- Listar erros encontrados (se houver)

### 2. Vincular com OFX

1. Certifique-se de ter importado arquivos OFX na aba **📥 OFX Import**
2. Na aba **💳 Vendas Cartão**, clique em **"🔗 Vincular com OFX"**
3. Aguarde o processamento
4. Veja o resumo de vinculação:
   - ✅ Parcelas vinculadas (verde)
   - ⚠️ Parcelas pendentes (laranja)

### 3. Revisar Resultados

**Tabela de Vendas (superior):**
- Lista todas as vendas importadas
- Expanda uma venda para ver suas parcelas
- Veja quais parcelas foram vinculadas

**Tabela de Parcelas (inferior):**
- Todas as parcelas detalhadas
- Status de vinculação
- Dados do match OFX (se vinculado)
- Diferenças de data e valor

## 📊 Estatísticas Exibidas

O resumo mostra:
- **Vendas:** Total de vendas importadas
- **Parcelas:** Total de parcelas geradas
- **Vinculadas:** Parcelas vinculadas com OFX (verde)
- **Pendentes:** Parcelas sem vinculação (laranja)
- **Total:** Valor total de todas as parcelas
- **Vinculado:** Valor total das parcelas vinculadas
- **Pendente:** Valor total das parcelas pendentes

## 🔍 Logs e Troubleshooting

### Logs no Terminal

O sistema gera logs detalhados para debugging:

```
[CARD-PARSER] Iniciando parse de vendas_maio.csv
[CARD-PARSER] Arquivo lido: 50 linhas
[CARD-PARSER] Processado: 50 vendas, 200 parcelas
[CARD-PARSER] Erros: 0

[CARD-MATCHER] Iniciando matching de 200 parcelas com 1500 transações OFX
[CARD-MATCHER] Créditos OFX disponíveis: 800
[CARD-MATCHER] Matching concluído: 185 de 200 parcelas vinculadas
```

### Múltiplos Matches

Quando há ambiguidade:

```
[CARD-MATCHER] AVISO: Múltiplos matches encontrados para parcela VENDA001 #2
[CARD-MATCHER]   Valor esperado: R$ 23,88
[CARD-MATCHER]   Data esperada: 10/07/2025
[CARD-MATCHER]   Matches encontrados: 3
[CARD-MATCHER]     1. Data: 10/07/2025 | Valor: R$ 23,88 | TED RECEBIDA - CLIENTE ABC
[CARD-MATCHER]     2. Data: 11/07/2025 | Valor: R$ 23,90 | PIX RECEBIDO - CLIENTE ABC
[CARD-MATCHER]     3. Data: 12/07/2025 | Valor: R$ 23,85 | TED RECEBIDA - CLIENTE ABC
[CARD-MATCHER]   Usando PRIMEIRA OCORRÊNCIA
```

### Erros Comuns

**1. Campos obrigatórios faltando:**
```
Linha 15: Campos obrigatórios faltando: CPF/CNPJ do estabelecimento, Valor líquido
```
**Solução:** Preencha todos os campos marcados com * no CSV

**2. Data inválida:**
```
Linha 22: Erro ao processar - invalid date format
```
**Solução:** Use formato DD/MM/YYYY (ex: 10/05/2025)

**3. Nenhuma transação OFX:**
```
[CARD-MATCHER] Aviso: Nenhuma transação OFX disponível
```
**Solução:** Importe arquivos OFX primeiro na aba "📥 OFX Import"

## 💾 Salvar e Carregar Projetos

Os dados de vendas de cartão são salvos automaticamente nos projetos `.ofxproj`:
- Vendas importadas
- Parcelas geradas
- Vinculações com OFX

Ao abrir um projeto salvo, todos os dados de cartão são restaurados automaticamente.

## 🔮 Próximas Funcionalidades

Em desenvolvimento:
- [ ] Integração com "Análise NFSe" para separar:
  - Pendente Notas vs Pendente Cartão vs OFX
- [ ] Vinculação Venda ↔ Nota Fiscal por CPF/CNPJ
- [ ] Exibir parcelas pendentes na aba "Não Vinculados"
- [ ] Exportação de relatório de vendas de cartão
- [ ] Filtros e buscas avançadas

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no terminal
2. Baixe e preencha o modelo CSV corretamente
3. Certifique-se de ter dados OFX importados antes de vincular
4. Verifique se os valores e datas estão no formato brasileiro

---

**Versão:** 1.0
**Data:** Dezembro 2025
**Desenvolvido para:** OFX Consolidador Pro - Gestão Financeira para Agências de Viagem
