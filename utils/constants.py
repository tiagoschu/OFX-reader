"""
Constants for OFX Consolidador Pro
"""

# Application Information
APP_NAME = "OFX Consolidador Pro"
VERSION = "3.0.0"
AUTHOR = "Tiago Schubert"
RELEASE_DATE = "Janeiro 2025"
DESCRIPTION = "Análise Inteligente de Extratos Bancários"

# Window Settings
WINDOW_TITLE = f"{APP_NAME} v{VERSION}"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
SPLASH_DURATION = 2000  # milliseconds

# Colors (Material Design inspired)
COLOR_PRIMARY = "#1976D2"       # Blue
COLOR_PRIMARY_DARK = "#1565C0"
COLOR_PRIMARY_LIGHT = "#42A5F5"
COLOR_ACCENT = "#FF4081"        # Pink
COLOR_SUCCESS = "#4CAF50"       # Green
COLOR_WARNING = "#FFC107"       # Amber
COLOR_ERROR = "#F44336"         # Red
COLOR_INFO = "#2196F3"          # Light Blue

# Background colors
COLOR_BG_DARK = "#263238"
COLOR_BG_LIGHT = "#ECEFF1"
COLOR_CARD_BG = "#FFFFFF"

# Text colors
COLOR_TEXT_PRIMARY = "#212121"
COLOR_TEXT_SECONDARY = "#757575"
COLOR_TEXT_DISABLED = "#BDBDBD"

# Transaction categories - Personal use
CATEGORIES_PERSONAL = {
    'Alimentação': {
        'keywords': ['mercado', 'supermercado', 'padaria', 'restaurante', 'lanchonete',
                    'ifood', 'rappi', 'uber eats', 'delivery'],
        'color': '#FF6F00',
        'icon': '🍽️'
    },
    'Transporte': {
        'keywords': ['uber', '99', 'combustivel', 'gasolina', 'posto', 'estacionamento',
                    'pedágio', 'transporte', 'onibus', 'metro'],
        'color': '#1976D2',
        'icon': '🚗'
    },
    'Transferências': {
        'keywords': ['pix', 'ted', 'doc', 'transferencia', 'transferência'],
        'color': '#7B1FA2',
        'icon': '💸'
    },
    'Investimentos': {
        'keywords': ['aplicacao', 'aplicação', 'resgate', 'investimento', 'cdb',
                    'tesouro', 'fundo', 'acao', 'ação'],
        'color': '#388E3C',
        'icon': '📈'
    },
    'Salário/Receitas': {
        'keywords': ['salario', 'salário', 'vencimento', 'pagamento recebido',
                    'deposito', 'depósito'],
        'color': '#4CAF50',
        'icon': '💰'
    },
    'Contas/Serviços': {
        'keywords': ['conta', 'fatura', 'energia', 'agua', 'água', 'internet',
                    'telefone', 'celular', 'tv', 'streaming', 'netflix', 'spotify'],
        'color': '#F57C00',
        'icon': '📄'
    },
    'Saúde': {
        'keywords': ['farmacia', 'farmácia', 'drogaria', 'hospital', 'clinica',
                    'clínica', 'medico', 'médico', 'consulta', 'exame'],
        'color': '#C62828',
        'icon': '⚕️'
    },
    'Educação': {
        'keywords': ['escola', 'faculdade', 'universidade', 'curso', 'livro',
                    'material escolar'],
        'color': '#0277BD',
        'icon': '📚'
    },
    'Lazer': {
        'keywords': ['cinema', 'show', 'teatro', 'viagem', 'hotel', 'passeio',
                    'parque', 'ingresso'],
        'color': '#E91E63',
        'icon': '🎭'
    },
    'Compras': {
        'keywords': ['loja', 'shopping', 'magazine', 'eletronico', 'eletrônico',
                    'roupa', 'calçado'],
        'color': '#9C27B0',
        'icon': '🛍️'
    },
    'Cartão': {
        'keywords': ['fatura de cartao', 'fatura de cartão', 'pagamento cartao'],
        'color': '#455A64',
        'icon': '💳'
    },
    'Outros': {
        'keywords': [],
        'color': '#607D8B',
        'icon': '📦'
    }
}

# Transaction categories - Business use
CATEGORIES_BUSINESS = {
    # Revenue / Receitas
    'Receita de Vendas': {
        'keywords': ['venda', 'pagamento recebido', 'faturamento', 'receita'],
        'color': '#4CAF50',
        'icon': '💰'
    },
    'Receita de Serviços': {
        'keywords': ['servico', 'serviço', 'consultoria', 'honorarios', 'honorários'],
        'color': '#66BB6A',
        'icon': '🛠️'
    },
    'Receitas Financeiras': {
        'keywords': ['juros recebido', 'rendimento', 'aplicacao', 'aplicação'],
        'color': '#81C784',
        'icon': '📈'
    },

    # Cost of Goods Sold / Custo dos Produtos Vendidos
    'CMV - Custo Mercadoria': {
        'keywords': ['compra mercadoria', 'estoque', 'fornecedor', 'produto'],
        'color': '#F57C00',
        'icon': '📦'
    },
    'Custo de Produção': {
        'keywords': ['materia prima', 'matéria prima', 'insumo', 'producao', 'produção'],
        'color': '#FB8C00',
        'icon': '🏭'
    },

    # Operating Expenses / Despesas Operacionais
    'Despesas com Pessoal': {
        'keywords': ['salario', 'salário', 'folha pagamento', 'inss', 'fgts', 'ferias', 'férias'],
        'color': '#1976D2',
        'icon': '👥'
    },
    'Aluguel e Condomínio': {
        'keywords': ['aluguel', 'condominio', 'condomínio', 'locacao', 'locação'],
        'color': '#1E88E5',
        'icon': '🏢'
    },
    'Despesas com Veículos': {
        'keywords': ['combustivel', 'combustível', 'manutencao veiculo', 'manutenção veículo', 'ipva', 'seguro auto'],
        'color': '#2196F3',
        'icon': '🚗'
    },
    'Marketing e Publicidade': {
        'keywords': ['marketing', 'publicidade', 'propaganda', 'anuncio', 'anúncio', 'google ads', 'facebook ads'],
        'color': '#E91E63',
        'icon': '📢'
    },
    'Tecnologia e Software': {
        'keywords': ['software', 'licenca', 'licença', 'hospedagem', 'dominio', 'domínio', 'saas'],
        'color': '#9C27B0',
        'icon': '💻'
    },
    'Utilidades e Serviços': {
        'keywords': ['energia', 'agua', 'água', 'internet', 'telefone', 'limpeza', 'seguranca', 'segurança'],
        'color': '#FF9800',
        'icon': '⚡'
    },
    'Material de Escritório': {
        'keywords': ['material escritorio', 'material escritório', 'papelaria', 'suprimento'],
        'color': '#FFC107',
        'icon': '📝'
    },
    'Despesas Bancárias': {
        'keywords': ['tarifa', 'taxa bancaria', 'taxa bancária', 'juros pagos', 'iof'],
        'color': '#795548',
        'icon': '🏦'
    },
    'Impostos e Taxas': {
        'keywords': ['imposto', 'taxa', 'tributo', 'pis', 'cofins', 'icms', 'iss', 'irpj', 'csll'],
        'color': '#D32F2F',
        'icon': '📋'
    },
    'Honorários Profissionais': {
        'keywords': ['contador', 'contabilidade', 'advogado', 'consultoria', 'auditoria'],
        'color': '#00796B',
        'icon': '👔'
    },
    'Viagens e Hospedagem': {
        'keywords': ['viagem', 'hotel', 'passagem', 'hospedagem', 'translado'],
        'color': '#0097A7',
        'icon': '✈️'
    },
    'Manutenção e Reparos': {
        'keywords': ['manutencao', 'manutenção', 'reparo', 'conserto'],
        'color': '#5D4037',
        'icon': '🔧'
    },

    # Financial
    'Empréstimos e Financiamentos': {
        'keywords': ['emprestimo', 'empréstimo', 'financiamento', 'parcela'],
        'color': '#C62828',
        'icon': '💳'
    },
    'Transferências Internas': {
        'keywords': ['transferencia', 'transferência', 'pix', 'ted', 'doc'],
        'color': '#7B1FA2',
        'icon': '💸'
    },

    'Outros': {
        'keywords': [],
        'color': '#607D8B',
        'icon': '📦'
    }
}

# Chart of Accounts - International standard
CATEGORIES_CHART_OF_ACCOUNTS = {
    # Assets / Ativos
    'Assets - Cash': {
        'keywords': ['saque', 'deposito', 'depósito', 'caixa'],
        'color': '#4CAF50',
        'icon': '💵'
    },
    'Assets - Accounts Receivable': {
        'keywords': ['recebimento', 'cliente', 'duplicata', 'contas receber'],
        'color': '#66BB6A',
        'icon': '📥'
    },
    'Assets - Inventory': {
        'keywords': ['estoque', 'mercadoria', 'produto'],
        'color': '#81C784',
        'icon': '📦'
    },
    'Assets - Fixed Assets': {
        'keywords': ['imovel', 'imóvel', 'veiculo', 'veículo', 'equipamento', 'maquina', 'máquina'],
        'color': '#A5D6A7',
        'icon': '🏗️'
    },
    'Assets - Investments': {
        'keywords': ['investimento', 'aplicacao', 'aplicação', 'acao', 'ação', 'cdb', 'fundo'],
        'color': '#C8E6C9',
        'icon': '📈'
    },

    # Liabilities / Passivos
    'Liabilities - Accounts Payable': {
        'keywords': ['fornecedor', 'contas pagar', 'duplicata pagar'],
        'color': '#F44336',
        'icon': '📤'
    },
    'Liabilities - Loans Payable': {
        'keywords': ['emprestimo', 'empréstimo', 'financiamento'],
        'color': '#E57373',
        'icon': '🏦'
    },
    'Liabilities - Salaries Payable': {
        'keywords': ['salario', 'salário', 'folha', 'pagamento pessoal'],
        'color': '#EF5350',
        'icon': '💼'
    },
    'Liabilities - Taxes Payable': {
        'keywords': ['imposto', 'taxa', 'tributo'],
        'color': '#E53935',
        'icon': '📋'
    },

    # Equity / Patrimônio Líquido
    'Equity - Owner\'s Capital': {
        'keywords': ['capital', 'aporte', 'investimento socio', 'investimento sócio'],
        'color': '#2196F3',
        'icon': '👤'
    },
    'Equity - Retained Earnings': {
        'keywords': ['lucro retido', 'reserva', 'lucro acumulado'],
        'color': '#42A5F5',
        'icon': '💎'
    },
    'Equity - Drawings': {
        'keywords': ['retirada', 'pro labore', 'pró-labore', 'distribuicao', 'distribuição'],
        'color': '#64B5F6',
        'icon': '💰'
    },

    # Revenue / Receitas
    'Revenue - Sales': {
        'keywords': ['venda', 'receita venda', 'faturamento'],
        'color': '#4CAF50',
        'icon': '💵'
    },
    'Revenue - Service Revenue': {
        'keywords': ['receita servico', 'receita serviço', 'prestacao servico', 'prestação serviço'],
        'color': '#66BB6A',
        'icon': '🛠️'
    },
    'Revenue - Interest Income': {
        'keywords': ['juros recebido', 'receita financeira', 'rendimento'],
        'color': '#81C784',
        'icon': '📊'
    },
    'Revenue - Other Income': {
        'keywords': ['receita', 'ganho'],
        'color': '#A5D6A7',
        'icon': '💰'
    },

    # Expenses / Despesas
    'Expenses - Cost of Goods Sold': {
        'keywords': ['custo mercadoria', 'cmv', 'custo produto'],
        'color': '#FF9800',
        'icon': '📦'
    },
    'Expenses - Salaries': {
        'keywords': ['salario', 'salário', 'folha pagamento'],
        'color': '#FFA726',
        'icon': '👥'
    },
    'Expenses - Rent': {
        'keywords': ['aluguel', 'locacao', 'locação'],
        'color': '#FFB74D',
        'icon': '🏢'
    },
    'Expenses - Utilities': {
        'keywords': ['energia', 'agua', 'água', 'gas', 'gás', 'internet', 'telefone'],
        'color': '#FFCC80',
        'icon': '⚡'
    },
    'Expenses - Office Supplies': {
        'keywords': ['material escritorio', 'material escritório', 'suprimento'],
        'color': '#FFE0B2',
        'icon': '📝'
    },
    'Expenses - Marketing': {
        'keywords': ['marketing', 'publicidade', 'propaganda'],
        'color': '#E91E63',
        'icon': '📢'
    },
    'Expenses - Insurance': {
        'keywords': ['seguro'],
        'color': '#EC407A',
        'icon': '🛡️'
    },
    'Expenses - Depreciation': {
        'keywords': ['depreciacao', 'depreciação', 'amortizacao', 'amortização'],
        'color': '#F06292',
        'icon': '📉'
    },
    'Expenses - Interest Expense': {
        'keywords': ['juros pagos', 'despesa financeira'],
        'color': '#F48FB1',
        'icon': '💸'
    },
    'Expenses - Taxes': {
        'keywords': ['imposto', 'taxa', 'tributo'],
        'color': '#F8BBD0',
        'icon': '📋'
    },
    'Expenses - Other Expenses': {
        'keywords': ['despesa', 'gasto'],
        'color': '#FCE4EC',
        'icon': '💳'
    },

    'Uncategorized': {
        'keywords': [],
        'color': '#607D8B',
        'icon': '❓'
    }
}

# Default category set (for backward compatibility)
CATEGORIES = CATEGORIES_PERSONAL

# Travel Agency Chart of Accounts (Plano de Contas para Agência de Viagens)
CATEGORIES_TRAVEL_AGENCY = {
    # 1 - ATIVO
    '1-01-01-001 Caixa Geral': {
        'keywords': ['caixa', 'dinheiro', 'especie'],
        'color': '#4CAF50',
        'icon': '💵',
        'type': 'asset',
        'code': '1-01-01-001-0000001'
    },
    '1-01-01-001 Cheques Pré Datados': {
        'keywords': ['cheque', 'pre datado', 'pré-datado'],
        'color': '#66BB6A',
        'icon': '📝',
        'type': 'asset',
        'code': '1-01-01-001-0000002'
    },
    '1-01-01-002 BRADESCO': {
        'keywords': ['bradesco', 'banco bradesco'],
        'color': '#81C784',
        'icon': '🏦',
        'type': 'asset',
        'code': '1-01-01-002-0000002'
    },
    '1-01-01-002 Banco do Brasil': {
        'keywords': ['banco do brasil', 'bb', 'conta corrente bb'],
        'color': '#A5D6A7',
        'icon': '🏦',
        'type': 'asset',
        'code': '1-01-01-002-0000003'
    },
    '1-01-01-003 Aplicações Financeiras': {
        'keywords': ['aplicacao', 'aplicação', 'renda fixa', 'investimento'],
        'color': '#C8E6C9',
        'icon': '📈',
        'type': 'asset',
        'code': '1-01-01-003-0000001'
    },
    '1-02-001 Clientes': {
        'keywords': ['cliente', 'contas a receber', 'receber'],
        'color': '#FFB74D',
        'icon': '👥',
        'type': 'asset',
        'code': '1-02-001'
    },
    '1-02-002 Cartões de Débito/Crédito': {
        'keywords': ['cartao', 'cartão', 'credito', 'crédito', 'debito', 'débito'],
        'color': '#FFA726',
        'icon': '💳',
        'type': 'asset',
        'code': '1-02-002'
    },
    '1-02-100 Lei Kandir - Tarifas': {
        'keywords': ['lei kandir', 'kandir tarifa'],
        'color': '#FF9800',
        'icon': '⚖️',
        'type': 'asset',
        'code': '1-02-100-0000001'
    },
    '1-03-001 Computadores e Equipamentos': {
        'keywords': ['computador', 'impressora', 'equipamento', 'hardware'],
        'color': '#64B5F6',
        'icon': '💻',
        'type': 'asset',
        'code': '1-03-001-0000001'
    },
    '1-03-002 Veículos': {
        'keywords': ['veiculo', 'veículo', 'carro', 'van', 'onibus', 'ônibus'],
        'color': '#42A5F5',
        'icon': '🚗',
        'type': 'asset',
        'code': '1-03-002'
    },

    # 2 - PASSIVO E PATRIMÔNIO LÍQUIDO
    '2-01-001 Fornecedores': {
        'keywords': ['fornecedor', 'contas a pagar', 'pagar'],
        'color': '#FF5252',
        'icon': '📤',
        'type': 'liability',
        'code': '2-01-001'
    },
    '2-01-002 Emissores e Promotores': {
        'keywords': ['emissor', 'promotor', 'companhia aerea', 'companhia aérea'],
        'color': '#FF6E40',
        'icon': '✈️',
        'type': 'liability',
        'code': '2-01-002'
    },
    '2-01-003 Emissores de Agências Clientes': {
        'keywords': ['emissor cliente', 'agencia cliente', 'agência'],
        'color': '#FF7043',
        'icon': '🏢',
        'type': 'liability',
        'code': '2-01-003'
    },
    '2-01-100 Tarifas - Recursos Temporários': {
        'keywords': ['tarifa temporaria', 'temporário tarifa'],
        'color': '#FF8A65',
        'icon': '⏱️',
        'type': 'liability',
        'code': '2-01-100-0000001'
    },
    '2-01-100 Taxas - Recursos Temporários': {
        'keywords': ['taxa temporaria', 'temporário taxa'],
        'color': '#FFAB91',
        'icon': '⏱️',
        'type': 'liability',
        'code': '2-01-100-0000002'
    },
    '2-01-100 Taxa Seguro': {
        'keywords': ['taxa seguro', 'seguro viagem'],
        'color': '#FFCCBC',
        'icon': '🛡️',
        'type': 'liability',
        'code': '2-01-100-0000003'
    },
    '2-01-100 Taxa No Show': {
        'keywords': ['no show', 'falta', 'ausencia', 'ausência'],
        'color': '#D84315',
        'icon': '❌',
        'type': 'liability',
        'code': '2-01-100-0000007'
    },
    '2-03-001 Capital Social': {
        'keywords': ['capital social', 'capital subscrito'],
        'color': '#9C27B0',
        'icon': '💰',
        'type': 'equity',
        'code': '2-03-001-0000001'
    },
    '2-03-007 Prejuízos Acumulados': {
        'keywords': ['prejuizo', 'prejuízo', 'lucro acumulado'],
        'color': '#BA68C8',
        'icon': '📉',
        'type': 'equity',
        'code': '2-03-007'
    },

    # 3 - CUSTOS E DESPESAS
    '3-01-001 Custos dos Serviços Prestados': {
        'keywords': ['custo servico', 'custo serviço', 'csp'],
        'color': '#F44336',
        'icon': '💸',
        'type': 'expense',
        'code': '3-01-001'
    },
    '3-02-001 Aluguéis e Condomínios': {
        'keywords': ['aluguel', 'condominio', 'condomínio'],
        'color': '#EF5350',
        'icon': '🏠',
        'type': 'expense',
        'code': '3-02-001'
    },
    '3-02-002 Despesas c/ Pessoal': {
        'keywords': ['salario', 'salário', 'folha', 'funcionario', 'funcionário'],
        'color': '#E57373',
        'icon': '👥',
        'type': 'expense',
        'code': '3-02-002'
    },
    '3-02-003 Comunicação': {
        'keywords': ['telefone', 'internet', 'fax', 'comunicacao', 'comunicação'],
        'color': '#EF9A9A',
        'icon': '📞',
        'type': 'expense',
        'code': '3-02-003'
    },
    '3-02-004 Impostos e Taxas': {
        'keywords': ['imposto', 'taxa', 'tributo', 'iptu', 'ir'],
        'color': '#FFCDD2',
        'icon': '📋',
        'type': 'expense',
        'code': '3-02-004'
    },
    '3-02-005 Propaganda e Publicidade': {
        'keywords': ['propaganda', 'publicidade', 'marketing', 'anuncio', 'anúncio'],
        'color': '#FF8A80',
        'icon': '📢',
        'type': 'expense',
        'code': '3-02-005'
    },
    '3-02-006 Transporte e Locomoção': {
        'keywords': ['transporte', 'locomocao', 'locomoção', 'combustivel', 'combustível'],
        'color': '#FF5252',
        'icon': '🚗',
        'type': 'expense',
        'code': '3-02-006'
    },
    '3-02-007 Despesas Administrativas': {
        'keywords': ['administrativa', 'administracao', 'administração'],
        'color': '#F48FB1',
        'icon': '📊',
        'type': 'expense',
        'code': '3-02-007'
    },
    '3-02-008 Energia Elétrica': {
        'keywords': ['energia', 'luz', 'eletrica', 'elétrica'],
        'color': '#F8BBD0',
        'icon': '💡',
        'type': 'expense',
        'code': '3-02-008'
    },
    '3-02-009 Serviços de Terceiros': {
        'keywords': ['servico terceiro', 'serviço terceiro', 'terceirizado'],
        'color': '#FCE4EC',
        'icon': '🔧',
        'type': 'expense',
        'code': '3-02-009'
    },
    '3-02-010 Juros e Comissões Bancárias': {
        'keywords': ['juros', 'comissao bancaria', 'comissão bancária', 'tarifa bancaria', 'tarifa bancária'],
        'color': '#CE93D8',
        'icon': '🏦',
        'type': 'expense',
        'code': '3-02-010'
    },
    '3-02-014 Material de Escritório': {
        'keywords': ['material escritorio', 'material escritório', 'papelaria'],
        'color': '#B39DDB',
        'icon': '✏️',
        'type': 'expense',
        'code': '3-02-014'
    },
    '3-02-015 Despesas Diversas': {
        'keywords': ['despesa diversa', 'outras despesas'],
        'color': '#9FA8DA',
        'icon': '💳',
        'type': 'expense',
        'code': '3-02-015'
    },
    '3-02-016 Segurança e Limpeza': {
        'keywords': ['seguranca', 'segurança', 'limpeza', 'vigilancia', 'vigilância'],
        'color': '#90CAF9',
        'icon': '🧹',
        'type': 'expense',
        'code': '3-02-016'
    },
    '3-02-100 Descontos Concedidos': {
        'keywords': ['desconto concedido', 'desconto venda'],
        'color': '#81D4FA',
        'icon': '🏷️',
        'type': 'expense',
        'code': '3-02-100'
    },
    '3-02-200 Comissões de Agências': {
        'keywords': ['comissao agencia', 'comissão agência', 'comissao paga', 'comissão paga'],
        'color': '#80DEEA',
        'icon': '💼',
        'type': 'expense',
        'code': '3-02-200'
    },
    '3-02-300 Taxas de Cartão': {
        'keywords': ['taxa cartao', 'taxa cartão', 'maquininha', 'adquirente'],
        'color': '#80CBC4',
        'icon': '💳',
        'type': 'expense',
        'code': '3-02-300'
    },
    '3-02-650 Taxa de Emissão de Passagens': {
        'keywords': ['taxa emissao', 'taxa emissão', 'emissao passagem', 'emissão passagem'],
        'color': '#A5D6A7',
        'icon': '🎫',
        'type': 'expense',
        'code': '3-02-650'
    },
    '3-03-001 Despesas Financeiras': {
        'keywords': ['despesa financeira', 'juros pagos'],
        'color': '#C5E1A5',
        'icon': '📉',
        'type': 'expense',
        'code': '3-03-001'
    },

    # 4 - RECEITAS
    '4-01-001 Receitas de Comissões': {
        'keywords': ['receita comissao', 'receita comissão', 'comissao recebida', 'comissão recebida'],
        'color': '#4CAF50',
        'icon': '💰',
        'type': 'revenue',
        'code': '4-01-001-0000001'
    },
    '4-01-001 Receitas de Overnight': {
        'keywords': ['overnight', 'open market', 'aplicacao overnight', 'aplicação overnight'],
        'color': '#66BB6A',
        'icon': '📈',
        'type': 'revenue',
        'code': '4-01-001-0000010'
    },
    '4-01-001 Markup sobre Vendas': {
        'keywords': ['markup', 'margem', 'lucro venda'],
        'color': '#81C784',
        'icon': '💵',
        'type': 'revenue',
        'code': '4-01-001-0000100'
    },
    '4-01-001 Taxas DU': {
        'keywords': ['taxa du', 'intermediacao', 'intermediação'],
        'color': '#A5D6A7',
        'icon': '💼',
        'type': 'revenue',
        'code': '4-01-001-0000300'
    },
    '4-01-002 Receitas de Diferenças': {
        'keywords': ['diferenca reconciliacao', 'diferença reconciliação', 'ajuste'],
        'color': '#C8E6C9',
        'icon': '🔄',
        'type': 'revenue',
        'code': '4-01-002-0000001'
    },
    '4-01-004 FEE': {
        'keywords': ['fee', 'taxa fee'],
        'color': '#E8F5E9',
        'icon': '💎',
        'type': 'revenue',
        'code': '4-01-004-0000001'
    },
    '4-01-004 Taxas de Serviços': {
        'keywords': ['taxa servico', 'taxa serviço', 'servico prestado', 'serviço prestado'],
        'color': '#DCEDC8',
        'icon': '🔧',
        'type': 'revenue',
        'code': '4-01-004-0000002'
    },
    '4-01-120 Operação Própria - Receitas': {
        'keywords': ['operacao propria', 'operação própria', 'receita propria', 'receita própria'],
        'color': '#C5E1A5',
        'icon': '✈️',
        'type': 'revenue',
        'code': '4-01-120'
    },
    '4-02-001 Receitas Financeiras': {
        'keywords': ['receita financeira', 'juros recebido', 'rendimento'],
        'color': '#AED581',
        'icon': '💹',
        'type': 'revenue',
        'code': '4-02-001'
    },

    'Uncategorized': {
        'keywords': [],
        'color': '#607D8B',
        'icon': '❓',
        'type': 'uncategorized',
        'code': '0000'
    }
}

# Category presets
CATEGORY_PRESETS = {
    'personal': {
        'name': 'Uso Pessoal',
        'description': 'Categorias para controle financeiro pessoal',
        'categories': CATEGORIES_PERSONAL,
        'person_type': 'fisica'
    },
    'business': {
        'name': 'Uso Empresarial',
        'description': 'Categorias para gestão empresarial (DRE)',
        'categories': CATEGORIES_BUSINESS,
        'person_type': 'juridica'
    },
    'chart_of_accounts': {
        'name': 'Plano de Contas (Chart of Accounts)',
        'description': 'Plano de contas contábil internacional',
        'categories': CATEGORIES_CHART_OF_ACCOUNTS,
        'person_type': 'juridica'
    },
    'travel_agency': {
        'name': 'Agência de Viagens',
        'description': 'Plano de contas completo para agências de viagens',
        'categories': CATEGORIES_TRAVEL_AGENCY,
        'person_type': 'juridica',
        'business_sector': 'travel_agency'
    }
}

# Business sectors for Pessoa Jurídica
BUSINESS_SECTORS = {
    'travel_agency': {
        'name': 'Agência de Viagens',
        'description': 'Agências de turismo e viagens',
        'preset': 'travel_agency'
    },
    'retail': {
        'name': 'Comércio Varejista',
        'description': 'Lojas e comércio em geral',
        'preset': 'business'
    },
    'services': {
        'name': 'Prestação de Serviços',
        'description': 'Empresas de serviços',
        'preset': 'business'
    },
    'industry': {
        'name': 'Indústria',
        'description': 'Empresas industriais e manufatura',
        'preset': 'business'
    },
    'general': {
        'name': 'Geral',
        'description': 'Plano de contas empresarial genérico',
        'preset': 'business'
    }
}

# Export formats
EXPORT_FORMATS = {
    'csv': {'name': 'CSV (separado por ;)', 'extension': '.csv'},
    'excel': {'name': 'Excel (.xlsx)', 'extension': '.xlsx'},
    'ofx': {'name': 'OFX Consolidado', 'extension': '.ofx'},
    'json': {'name': 'JSON', 'extension': '.json'},
    'pdf': {'name': 'PDF com Relatório', 'extension': '.pdf'},
}

# Date formats
DATE_FORMAT_DISPLAY = "%d/%m/%Y"
TIME_FORMAT_DISPLAY = "%H:%M:%S"
DATETIME_FORMAT_DISPLAY = f"{DATE_FORMAT_DISPLAY} {TIME_FORMAT_DISPLAY}"

# Chart settings
CHART_HEIGHT = 400
CHART_COLORS = [
    '#1976D2', '#FF4081', '#4CAF50', '#FFC107', '#9C27B0',
    '#FF5722', '#00BCD4', '#8BC34A', '#FF9800', '#E91E63'
]
