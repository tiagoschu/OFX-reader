# OFX Consolidador - Extratos Bancários

Aplicação Python com interface gráfica para consolidar múltiplos arquivos OFX (Open Financial Exchange) de diferentes bancos em um único arquivo CSV ou Excel.

## Funcionalidades

- Interface gráfica intuitiva para seleção de arquivos
- Suporte a múltiplos arquivos OFX de diferentes bancos
- Detecção automática de encoding de arquivos
- Remoção de transações duplicadas baseado no ID da transação
- Conversão de datas para formato brasileiro (dd/mm/yyyy)
- Extração de horários no formato hh:mm:ss
- Exportação para CSV (separado por ponto e vírgula) ou Excel
- Resumo detalhado do processamento
- Ordenação cronológica das transações

## Requisitos

- Python 3.8 ou superior
- Bibliotecas Python (instaladas automaticamente):
  - ofxparse
  - pandas
  - chardet
  - openpyxl

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd OFX-reader
```

### 2. Crie um ambiente virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## Como Usar

### 1. Execute a aplicação

```bash
python app.py
```

### 2. Adicione arquivos OFX

- Clique em "📁 Adicionar Arquivos OFX"
- Selecione um ou mais arquivos .ofx
- Os arquivos aparecerão na lista

### 3. Configure as opções

- **Remover duplicadas**: Remove transações duplicadas com base no ID
- **Incluir horário**: Adiciona a coluna de horário (hh:mm:ss) no resultado
- **Formato**: Escolha entre CSV ou Excel

### 4. Processe e exporte

- Clique em "⚡ Processar e Exportar"
- Visualize o resumo na área de resultados
- Escolha o local para salvar o arquivo
- Pronto!

## Estrutura do Arquivo de Saída

O arquivo consolidado contém as seguintes colunas:

| Coluna | Descrição |
|--------|-----------|
| data | Data da transação (dd/mm/yyyy) |
| hora | Horário da transação (hh:mm:ss) |
| banco | Identificação do banco |
| conta | Número da conta |
| tipo_conta | Tipo da conta (CHECKING, SAVINGS, etc) |
| tipo_transacao | Tipo da transação (DEBIT, CREDIT, etc) |
| valor | Valor da transação (negativo para débitos) |
| descricao | Descrição/memo da transação |
| id_transacao | ID único da transação |
| numero_cheque | Número do cheque (quando aplicável) |
| arquivo_origem | Nome do arquivo OFX de origem |

## Formato CSV

O arquivo CSV é gerado com:
- Separador: ponto e vírgula (;)
- Encoding: UTF-8 com BOM (abre corretamente no Excel)
- Datas no formato: dd/mm/yyyy
- Horários no formato: hh:mm:ss

## Recursos Avançados

### Remoção de Duplicatas

A aplicação identifica e remove transações duplicadas usando:
- ID da transação (FITID)
- Número da conta
- Identificação do banco

Isso é especialmente útil quando você tem arquivos OFX com períodos sobrepostos.

### Detecção Automática de Encoding

A aplicação detecta automaticamente o encoding dos arquivos OFX, tratando corretamente:
- UTF-8
- ISO-8859-1 (Latin-1)
- Windows-1252
- Outros encodings comuns

### Tratamento de Erros

- Arquivos corrompidos ou inválidos são reportados
- O processamento continua mesmo se alguns arquivos falharem
- Todos os erros são exibidos na área de resultados

## Validação Antes de Usar

### 1. Teste com poucos arquivos primeiro

- Comece com 2-3 arquivos OFX
- Verifique se o resultado está correto
- Confira se as datas e valores estão corretos

### 2. Verifique duplicatas

- Exporte com e sem a opção de remover duplicatas
- Compare o número de transações
- Valide se as duplicatas removidas são realmente duplicadas

### 3. Confira os totais

- Some manualmente algumas transações
- Compare com o resumo exibido
- Verifique se créditos são positivos e débitos negativos

### 4. Abra o arquivo final

- Abra o CSV no Excel ou LibreOffice
- Verifique se as colunas estão corretas
- Confira a formatação de datas e valores

## Solução de Problemas

### Erro ao importar ofxparse

```bash
pip install --upgrade ofxparse
```

### Erro de encoding

A aplicação detecta automaticamente, mas se houver problemas:
- Abra o arquivo OFX em um editor de texto
- Salve como UTF-8
- Tente novamente

### Valores incorretos

- Verifique se o arquivo OFX está completo
- Alguns bancos podem gerar arquivos incompletos
- Baixe o arquivo novamente do banco

### CSV não abre corretamente no Excel

- Use a opção de exportar para Excel (.xlsx)
- Ou abra o CSV usando "Dados > Importar de Texto" no Excel

## Estrutura do Projeto

```
OFX-reader/
│
├── app.py                  # Aplicação GUI principal
├── ofx_processor.py        # Lógica de processamento OFX
├── requirements.txt        # Dependências Python
├── README.md              # Este arquivo
└── .gitignore             # Arquivos ignorados pelo git
```

## Contribuindo

Sugestões e melhorias são bem-vindas! Sinta-se livre para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## Licença

Este projeto é fornecido "como está", sem garantias de qualquer tipo.

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório do projeto.

---

**Desenvolvido com Python e Tkinter**
