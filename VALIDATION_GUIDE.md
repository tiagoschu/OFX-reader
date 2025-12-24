# Guia de Validação - OFX Consolidador

Este guia ajuda você a validar se a aplicação está funcionando corretamente antes de processar grandes volumes de dados.

## Checklist de Validação

### ✅ Fase 1: Preparação

- [ ] Python 3.8+ instalado
- [ ] Todas as dependências instaladas (`pip install -r requirements.txt`)
- [ ] Aplicação abre sem erros (`python app.py`)
- [ ] Você tem pelo menos 2-3 arquivos OFX reais para testar

### ✅ Fase 2: Teste Básico

#### 2.1 Teste com 1 arquivo

- [ ] Adicione apenas 1 arquivo OFX
- [ ] Processe e exporte para CSV
- [ ] Abra o CSV e verifique:
  - [ ] Todas as transações estão presentes
  - [ ] Datas no formato dd/mm/yyyy
  - [ ] Horários no formato hh:mm:ss
  - [ ] Valores corretos (débitos negativos, créditos positivos)
  - [ ] Descrições legíveis (sem caracteres estranhos)

#### 2.2 Contagem Manual

Para validar, faça uma contagem manual:

```
Arquivo OFX original: 150 transações
CSV gerado: ___ transações (deve ser 150)
```

**Como contar transações em um OFX:**
- Abra o arquivo .ofx em um editor de texto
- Procure por `<STMTTRN>` (cada ocorrência = 1 transação)
- Ou use: `grep -c "<STMTTRN>" arquivo.ofx` (Linux/Mac)

### ✅ Fase 3: Teste de Duplicatas

#### 3.1 Teste com períodos sobrepostos

- [ ] Baixe extrato de Janeiro (01/01 a 31/01)
- [ ] Baixe extrato de Dezembro-Janeiro (15/12 a 15/01)
- [ ] Processe ambos **COM** remoção de duplicatas
- [ ] Processe ambos **SEM** remoção de duplicatas
- [ ] Compare os resultados

**Exemplo esperado:**
```
Arquivo 1: 100 transações
Arquivo 2: 80 transações (15 são duplicatas)
---
SEM remoção: 180 transações
COM remoção: 165 transações (15 removidas)
```

#### 3.2 Validação de duplicatas removidas

- [ ] Abra ambos os arquivos CSV
- [ ] Filtre por uma data que aparece nos dois arquivos
- [ ] Verifique se a transação aparece apenas 1 vez no arquivo com remoção
- [ ] Verifique se aparece 2 vezes no arquivo sem remoção

### ✅ Fase 4: Teste com Múltiplos Bancos

#### 4.1 Consolidação multi-banco

- [ ] Adicione arquivos de 2+ bancos diferentes
- [ ] Processe e exporte
- [ ] Verifique no CSV:
  - [ ] Coluna "banco" identifica corretamente cada banco
  - [ ] Coluna "conta" identifica cada conta
  - [ ] Transações estão ordenadas por data (não por banco)
  - [ ] Totais batem com a soma esperada

#### 4.2 Validação de totais

Calcule manualmente:

```
Banco A - Créditos: R$ 5.000,00
Banco A - Débitos:  R$ 3.000,00
Banco B - Créditos: R$ 2.000,00
Banco B - Débitos:  R$ 1.500,00
---
Total Créditos esperado:  R$ 7.000,00
Total Débitos esperado:   R$ 4.500,00
Saldo líquido esperado:   R$ 2.500,00
```

Compare com o resumo exibido pela aplicação.

### ✅ Fase 5: Teste de Caracteres Especiais

#### 5.1 Caracteres portugueses

Verifique se transações com caracteres especiais aparecem corretamente:
- [ ] Acentos: á, é, í, ó, ú, ã, õ, â, ê, ô
- [ ] Cedilha: ç
- [ ] Símbolos: R$, %, &

Exemplo de descrições que devem aparecer corretamente:
```
"PAGAMENTO FARMÁCIA SÃO JOÃO"
"TRANSFERÊNCIA JOÃO DA SILVA"
"COMPRA CAFÉ & CIA"
```

### ✅ Fase 6: Teste de Casos Extremos

- [ ] **Arquivo vazio**: Crie um .ofx sem transações
  - Deve: Exibir mensagem clara de erro
  - Não deve: Travar a aplicação

- [ ] **Arquivo corrompido**: Modifique um .ofx removendo tags
  - Deve: Exibir erro e continuar com outros arquivos
  - Não deve: Interromper todo o processamento

- [ ] **Valores zerados**: Transações com valor R$ 0,00
  - Deve: Incluir no CSV normalmente

- [ ] **Descrições longas**: Transações com memo muito grande
  - Deve: Incluir descrição completa no CSV

### ✅ Fase 7: Teste de Formatos de Exportação

#### 7.1 CSV

- [ ] Exportar como CSV
- [ ] Abrir no Excel (deve abrir com colunas separadas)
- [ ] Abrir no LibreOffice Calc
- [ ] Abrir no Google Sheets
- [ ] Verificar se acentos aparecem corretamente em todos

#### 7.2 Excel

- [ ] Exportar como Excel (.xlsx)
- [ ] Abrir no Excel
- [ ] Verificar se colunas estão formatadas
- [ ] Verificar se valores estão como números (não texto)
- [ ] Verificar se datas estão como texto (não número de série)

### ✅ Fase 8: Validação de Integridade

#### 8.1 Teste de saldo

Para arquivos que incluem saldo final:

1. Some todas as transações manualmente (ou no Excel)
2. Compare com o saldo final informado no OFX
3. Deve bater com o "Saldo líquido" do resumo

**Fórmula no Excel:**
```
=SOMA(coluna_valor)
```

#### 8.2 Ordenação cronológica

- [ ] Verifique se as transações estão em ordem cronológica
- [ ] A primeira linha deve ter a data mais antiga
- [ ] A última linha deve ter a data mais recente

### ✅ Fase 9: Teste de Performance

#### 9.1 Volume de dados

Teste com diferentes volumes:

- [ ] 1 arquivo com ~100 transações → Deve processar em < 2 segundos
- [ ] 5 arquivos com ~500 transações total → Deve processar em < 5 segundos
- [ ] 10+ arquivos com 1000+ transações → Deve processar em < 10 segundos

Se demorar muito mais, pode haver problema.

### ✅ Fase 10: Validação Final

#### 10.1 Checklist pré-produção

Antes de processar seus dados reais de 1 ano:

- [ ] Todos os testes acima passaram
- [ ] Você entendeu como a aplicação funciona
- [ ] Você fez backup dos arquivos OFX originais
- [ ] Você sabe interpretar o resumo exibido
- [ ] Você testou abrir os CSV/Excel gerados
- [ ] Você validou que duplicatas são removidas corretamente

#### 10.2 Primeiro processamento real

1. **Faça backup**: Copie todos os .ofx para uma pasta de backup
2. **Processe em etapas**:
   - Primeiro: arquivos de 1 mês
   - Depois: arquivos de 3 meses
   - Por fim: todos os 12 meses
3. **Valide cada etapa**: Confira os totais e transações
4. **Documente**: Anote quantas transações cada banco teve

## Problemas Comuns e Soluções

### ❌ Problema: Datas aparecem em formato errado

**Solução**:
- Verifique se está usando a última versão do código
- Datas devem estar em dd/mm/yyyy
- Se aparecerem em outro formato, reporte o problema

### ❌ Problema: Caracteres estranhos nas descrições

**Solução**:
- A aplicação detecta encoding automaticamente
- Se persistir, tente salvar o OFX como UTF-8 antes de processar

### ❌ Problema: Valores incorretos

**Solução**:
- Verifique o arquivo OFX original
- Débitos devem ser negativos
- Créditos devem ser positivos
- Se estiver invertido, pode ser problema no OFX do banco

### ❌ Problema: Transações faltando

**Solução**:
- Conte as tags `<STMTTRN>` no arquivo OFX original
- Compare com o número de linhas no CSV
- Se não bater, pode haver erro no parsing

### ❌ Problema: Muitas duplicatas removidas

**Solução**:
- Isso é normal em períodos sobrepostos
- Verifique manualmente algumas transações
- Se estiver removendo transações legítimas, desative a opção

## Dicas Avançadas

### 📊 Validação com Excel

Crie uma planilha de validação:

```
Planilha 1: Importar CSV gerado
Planilha 2: Criar tabela dinâmica
  - Linhas: Banco, Conta
  - Valores: Soma de Valor, Contar Transações
  - Compare com seus extratos originais
```

### 🔍 Inspeção Visual

Abra alguns OFX em paralelo com o CSV:
- Escolha 5-10 transações aleatórias
- Verifique se data, valor e descrição batem
- Isso garante que o parsing está correto

### 📝 Mantenha um Log

Documente seu processamento:

```
Data: 24/12/2024
Arquivos: 12 (Jan-Dez 2024)
Bancos: Itaú, Bradesco, Nubank
Total transações: 1.547
Duplicatas removidas: 23
Saldo líquido: R$ 12.345,67
Status: ✅ Validado
```

## Conclusão

Se todos os testes passarem, você pode confiar na aplicação para processar seus extratos bancários!

Em caso de dúvidas ou problemas, consulte:
- [README.md](README.md) - Documentação geral
- [INSTALL.md](INSTALL.md) - Guia de instalação
- Issues no GitHub do projeto
