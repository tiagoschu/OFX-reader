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

# Travel Agency Chart of Accounts (Plano de Contas para Agência de Viagens - WIZTOUR)
# Estrutura focada em evitar tributação indevida com ênfase no Passivo
CATEGORIES_TRAVEL_AGENCY = {

    # ========== 1 - ATIVO ==========
    '1 | Ativo': {
        'keywords': ['ativo'],
        'color': '#4CAF50',
        'icon': '📊',
        'type': 'asset',
        'code': '1'
    },
    '1.1 | Ativo Circulante': {
        'keywords': ['ativo circulante'],
        'color': '#66BB6A',
        'icon': '💹',
        'type': 'asset',
        'code': '1.1'
    },
    '1.1.1 | Caixa': {
        'keywords': ['caixa', 'dinheiro', 'especie', 'moeda'],
        'color': '#81C784',
        'icon': '💵',
        'type': 'asset',
        'code': '1.1.1'
    },
    '1.1.2 | Bancos Conta Movimento': {
        'keywords': ['banco', 'conta corrente', 'conta movimento', 'bradesco', 'itau', 'santander', 'bb', 'caixa economica'],
        'color': '#A5D6A7',
        'icon': '🏦',
        'type': 'asset',
        'code': '1.1.2'
    },
    '1.1.3 | Contas a Receber': {
        'keywords': ['contas a receber', 'receber', 'cliente', 'duplicata', 'credito a receber'],
        'color': '#C8E6C9',
        'icon': '📥',
        'type': 'asset',
        'code': '1.1.3'
    },

    # ========== 2 - PASSIVO (MAIS IMPORTANTE - evita tributação indevida) ==========
    '2 | Passivo': {
        'keywords': ['passivo'],
        'color': '#FF5252',
        'icon': '📊',
        'type': 'liability',
        'code': '2'
    },
    '2.1 | Passivo Circulante': {
        'keywords': ['passivo circulante'],
        'color': '#FF6E40',
        'icon': '📉',
        'type': 'liability',
        'code': '2.1'
    },
    '2.1.1 | Fornecedores': {
        'keywords': ['fornecedor', 'contas a pagar', 'pagar', 'companhia aerea', 'hotel', 'operadora'],
        'color': '#FF7043',
        'icon': '📤',
        'type': 'liability',
        'code': '2.1.1'
    },
    '2.1.2 | Receitas Diferidas – Viagens a Realizar': {
        'keywords': ['receita diferida', 'viagem a realizar', 'antecipacao', 'adiantamento cliente', 'pacote a realizar'],
        'color': '#FF8A65',
        'icon': '✈️',
        'type': 'liability',
        'code': '2.1.2'
    },
    '2.1.3 | Valores de Terceiros a Repassar': {
        'keywords': ['valores terceiros', 'repassar', 'repasse', 'taxa terceiro', 'valor intermediado'],
        'color': '#FFAB91',
        'icon': '🔄',
        'type': 'liability',
        'code': '2.1.3'
    },

    # ========== 3 - PATRIMÔNIO LÍQUIDO ==========
    '3 | Patrimônio Líquido': {
        'keywords': ['patrimonio liquido', 'patrimônio líquido'],
        'color': '#9C27B0',
        'icon': '💎',
        'type': 'equity',
        'code': '3'
    },
    '3.1 | Capital Social': {
        'keywords': ['capital social', 'capital subscrito', 'capital integralizado'],
        'color': '#AB47BC',
        'icon': '💰',
        'type': 'equity',
        'code': '3.1'
    },
    '3.2 | Lucros ou Prejuízos Acumulados': {
        'keywords': ['lucro acumulado', 'prejuizo acumulado', 'prejuízo acumulado', 'resultado acumulado'],
        'color': '#BA68C8',
        'icon': '📊',
        'type': 'equity',
        'code': '3.2'
    },

    # ========== 4 - RECEITAS (somente o que é DA WIZTOUR) ==========
    # ❌ NUNCA lançar valor de fornecedor aqui
    '4 | Receitas': {
        'keywords': ['receita'],
        'color': '#2196F3',
        'icon': '💵',
        'type': 'revenue',
        'code': '4'
    },
    '4.1 | Receita Operacional': {
        'keywords': ['receita operacional'],
        'color': '#42A5F5',
        'icon': '💼',
        'type': 'revenue',
        'code': '4.1'
    },
    '4.1.1 | Comissão de Intercâmbios': {
        'keywords': ['comissao intercambio', 'comissão intercâmbio', 'intercambio', 'cambio', 'remessa'],
        'color': '#64B5F6',
        'icon': '💱',
        'type': 'revenue',
        'code': '4.1.1'
    },
    '4.1.2 | Margem de Pacotes de Viagem': {
        'keywords': ['margem pacote', 'markup', 'lucro pacote', 'margem viagem'],
        'color': '#90CAF9',
        'icon': '✈️',
        'type': 'revenue',
        'code': '4.1.2'
    },
    '4.1.3 | Taxas de Serviço': {
        'keywords': ['taxa servico', 'taxa serviço', 'fee', 'taxa administrativa', 'servico prestado'],
        'color': '#BBDEFB',
        'icon': '🔧',
        'type': 'revenue',
        'code': '4.1.3'
    },

    # ========== 5 - DESPESAS OPERACIONAIS ==========
    '5 | Despesas': {
        'keywords': ['despesa'],
        'color': '#F44336',
        'icon': '💸',
        'type': 'expense',
        'code': '5'
    },
    '5.1 | Despesas Operacionais': {
        'keywords': ['despesa operacional'],
        'color': '#EF5350',
        'icon': '📊',
        'type': 'expense',
        'code': '5.1'
    },
    '5.1.1 | Marketing e Publicidade': {
        'keywords': ['marketing', 'publicidade', 'propaganda', 'anuncio', 'facebook ads', 'google ads', 'instagram'],
        'color': '#E57373',
        'icon': '📢',
        'type': 'expense',
        'code': '5.1.1'
    },
    '5.1.2 | Comissões de Vendas': {
        'keywords': ['comissao venda', 'comissão venda', 'comissao vendedor', 'comissão vendedor', 'bonus venda'],
        'color': '#EF9A9A',
        'icon': '💼',
        'type': 'expense',
        'code': '5.1.2'
    },
    '5.1.3 | Sistemas e Softwares': {
        'keywords': ['sistema', 'software', 'saas', 'tecnologia', 'crm', 'erp', 'assinatura'],
        'color': '#FFCDD2',
        'icon': '💻',
        'type': 'expense',
        'code': '5.1.3'
    },
    '5.1.4 | Honorários Contábeis': {
        'keywords': ['contador', 'contabilidade', 'honorario contabil', 'honorário contábil', 'escritorio contabil'],
        'color': '#E1BEE7',
        'icon': '📊',
        'type': 'expense',
        'code': '5.1.4'
    },
    '5.1.5 | Taxas Bancárias': {
        'keywords': ['taxa bancaria', 'taxa bancária', 'tarifa banco', 'ted', 'doc', 'boleto'],
        'color': '#CE93D8',
        'icon': '🏦',
        'type': 'expense',
        'code': '5.1.5'
    },
    '5.1.6 | Despesas Administrativas': {
        'keywords': ['despesa administrativa', 'administracao', 'administração', 'aluguel', 'energia', 'internet', 'telefone'],
        'color': '#BA68C8',
        'icon': '🏢',
        'type': 'expense',
        'code': '5.1.6'
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
