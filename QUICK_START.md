# Início Rápido - OFX Consolidador

Guia de 5 minutos para começar a usar o OFX Consolidador.

## 🚀 Instalação Expressa

### Windows (CMD ou PowerShell)

```cmd
# 1. Navegue até a pasta do projeto
cd OFX-reader

# 2. Instale
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Execute
python app.py
```

### Linux/Mac (Terminal)

```bash
# 1. Navegue até a pasta do projeto
cd OFX-reader

# 2. Instale
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Execute
python app.py
```

## 📖 Uso Básico

### Passo 1: Obtenha seus arquivos OFX

Baixe seus extratos bancários no formato OFX:

**Itaú:**
- Acesse > Conta Corrente > Extrato
- Selecione o período
- Baixar > OFX

**Bradesco:**
- Acesse > Contas > Extrato
- Exportar > Arquivo OFX

**Nubank:**
- App > Menu > Exportar extrato
- Formato: OFX

**Banco do Brasil:**
- Acesse > Extrato
- Exportar > OFX/Money

*Outros bancos têm opções similares*

### Passo 2: Use a aplicação

1. **Adicionar arquivos**
   - Clique em "📁 Adicionar Arquivos OFX"
   - Selecione todos os .ofx que você baixou
   - Pressione "Abrir"

2. **Configurar opções** (recomendado manter padrão)
   - ✅ Remover duplicadas (mantenha marcado)
   - ✅ Incluir horário (mantenha marcado)
   - Formato: CSV (ou Excel se preferir)

3. **Processar**
   - Clique em "⚡ Processar e Exportar"
   - Aguarde o processamento
   - Visualize o resumo

4. **Salvar**
   - Escolha onde salvar
   - Nomeie seu arquivo (ex: extratos_2024.csv)
   - Clique em "Salvar"

5. **Abrir e usar**
   - Abra o arquivo no Excel, LibreOffice ou Google Sheets
   - Suas transações estão consolidadas e prontas para análise!

## 📊 O Que Você Verá

### Resumo do Processamento

```
============================================================
RESUMO DO PROCESSAMENTO
============================================================

Total de transações: 547
  - Créditos: 245 (R$ 45.320,50)
  - Débitos: 302 (R$ 38.127,80)
  - Saldo líquido: R$ 7.192,70

Bancos distintos: 3
Contas distintas: 4
Arquivos processados: 12

============================================================
```

### Arquivo CSV Gerado

```csv
data;hora;banco;conta;tipo_conta;tipo_transacao;valor;descricao;id_transacao;numero_cheque;arquivo_origem
01/01/2024;00:00:00;BANCO ITAU SA;12345-6;CHECKING;CREDIT;3500.00;SALARIO;123456789;;extrato_jan.ofx
02/01/2024;14:30:00;BANCO ITAU SA;12345-6;CHECKING;DEBIT;-150.50;MERCADO ABC;123456790;;extrato_jan.ofx
...
```

## 💡 Dicas para Melhor Uso

### 1. Organize seus arquivos OFX

Crie uma estrutura de pastas:
```
Documentos/
  └── Extratos_OFX/
      └── 2024/
          ├── itau_jan_2024.ofx
          ├── itau_fev_2024.ofx
          ├── bradesco_jan_2024.ofx
          └── ...
```

### 2. Nomeie os arquivos de forma clara

Use padrão: `banco_mes_ano.ofx`
- ✅ `itau_janeiro_2024.ofx`
- ✅ `nubank_01_2024.ofx`
- ❌ `extrato.ofx`
- ❌ `download(1).ofx`

### 3. Baixe períodos que não se sobrepõem muito

**Ideal:**
- Janeiro: 01/01 a 31/01
- Fevereiro: 01/02 a 28/02
- Etc.

**Evite:**
- Janeiro: 01/01 a 31/01
- Janeiro-Fevereiro: 15/01 a 15/02
- (Muitas duplicatas para remover)

### 4. Faça backup dos OFX originais

Antes de processar, copie os arquivos .ofx para uma pasta de backup.

### 5. Valide o primeiro processamento

Use o [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) para validar que tudo está correto.

## 🎯 Casos de Uso Comuns

### Caso 1: Controle Financeiro Pessoal

**Objetivo:** Analisar gastos do ano

1. Baixe todos os extratos de 2024
2. Processe tudo em um único CSV
3. Abra no Excel e crie uma tabela dinâmica
4. Agrupe por categoria (use a coluna "descricao")
5. Visualize seus gastos por mês/categoria

### Caso 2: Declaração de Imposto de Renda

**Objetivo:** Ter todas as movimentações para consulta

1. Baixe extratos de todas as contas
2. Processe e gere Excel
3. Use como referência ao preencher a declaração
4. Filtre por tipo_transacao para encontrar rendimentos, etc.

### Caso 3: Conciliação Bancária (Empresas)

**Objetivo:** Consolidar movimentações de múltiplas contas

1. Baixe extratos de todas as contas da empresa
2. Processe mantendo a opção "remover duplicatas"
3. Use a coluna "conta" para separar por conta
4. Exporte para Excel e compartilhe com contador

### Caso 4: Análise de Investimentos

**Objetivo:** Rastrear entradas e saídas

1. Baixe extratos da conta corrente e poupança
2. Filtre transações tipo "XFER" (transferências)
3. Identifique aportes e resgates
4. Compare com rentabilidade

## ⚠️ Problemas Comuns

### "Nenhuma transação encontrada"

**Causas:**
- Arquivo OFX vazio ou inválido
- Arquivo corrompido no download

**Solução:**
- Baixe o arquivo novamente do banco
- Verifique se o arquivo tem mais de 1KB

### "Erro ao processar arquivo X"

**Causas:**
- Formato OFX não padrão
- Encoding incompatível

**Solução:**
- A aplicação continuará processando outros arquivos
- Verifique o arquivo problemático em um editor de texto
- Tente baixar novamente

### CSV abre com tudo em uma coluna no Excel

**Causa:**
- Excel configurado para separador diferente

**Solução:**
- Use "Dados > Importar de Texto" no Excel
- Escolha separador: ponto e vírgula (;)
- Ou exporte para Excel (.xlsx) em vez de CSV

### Valores aparecem como texto no Excel

**Solução:**
- Selecione a coluna "valor"
- Vá em "Dados > Texto para Colunas"
- Escolha "Delimitado" > Próximo > Concluir

## 📚 Próximos Passos

Agora que você já sabe o básico:

1. ✅ Use o [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) para validar tudo
2. 📖 Leia o [README.md](README.md) para detalhes completos
3. 🔧 Consulte o [INSTALL.md](INSTALL.md) se tiver problemas

## 🆘 Precisa de Ajuda?

- **Dúvidas de uso:** Leia o README.md
- **Problemas técnicos:** Consulte INSTALL.md
- **Validação:** Use VALIDATION_GUIDE.md
- **Bugs:** Abra uma issue no GitHub

---

**Bom uso! 🎉**
