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

# Travel Agency Categories (Categorias para Agência de Viagens - WIZTOUR)
# Estrutura completa e profissional baseada na operação real
CATEGORIES_TRAVEL_AGENCY = {

    # ========== RECEITAS - PACOTES COMPLETOS ==========
    'Pacotes com Estudos': {
        'keywords': ['pacote estudo', 'intercambio estudo', 'curso ingles', 'high school', 'college'],
        'color': '#4CAF50',
        'icon': '📚',
        'type': 'revenue',
        'dre_account': 'Receita Bruta de Vendas',
        'group': 'Pacotes Completos'
    },
    'Pacotes Fun Trip': {
        'keywords': ['fun trip', 'pacote turismo', 'viagem lazer', 'tour grupo'],
        'color': '#66BB6A',
        'icon': '🎉',
        'type': 'revenue',
        'dre_account': 'Receita Bruta de Vendas',
        'group': 'Pacotes Completos'
    },
    'Pacotes Culturais': {
        'keywords': ['pacote cultural', 'intercambio cultural', 'au pair', 'voluntariado'],
        'color': '#81C784',
        'icon': '🌍',
        'type': 'revenue',
        'dre_account': 'Receita Bruta de Vendas',
        'group': 'Pacotes Completos'
    },

    # ========== RECEITAS - VENDAS AVULSO ==========
    'Vendas Avulso com Markup': {
        'keywords': ['venda avulsa', 'servico avulso', 'markup', 'margem'],
        'color': '#AED581',
        'icon': '💰',
        'type': 'revenue',
        'dre_account': 'Receita Bruta de Vendas',
        'group': 'Vendas Avulso com Markup'
    },

    # ========== RECEITAS - COMISSÕES RECEBIDAS ==========
    'Comissões - Consolidadora Confiança': {
        'keywords': ['comissao confianca', 'comissão confiança', 'confianca'],
        'color': '#2196F3',
        'icon': '🤝',
        'type': 'revenue',
        'dre_account': 'Outras Receitas',
        'group': 'Comissões Recebidas'
    },
    'Comissões - Portal JustTravel': {
        'keywords': ['justtravel', 'just travel', 'comissao portal'],
        'color': '#42A5F5',
        'icon': '🌐',
        'type': 'revenue',
        'dre_account': 'Outras Receitas',
        'group': 'Comissões Recebidas'
    },
    'Comissões - Outras Consolidadoras': {
        'keywords': ['comissao consolidadora', 'comissão consolidadora'],
        'color': '#64B5F6',
        'icon': '🏢',
        'type': 'revenue',
        'dre_account': 'Outras Receitas',
        'group': 'Comissões Recebidas'
    },
    'Comissões - Fornecedores Diretos': {
        'keywords': ['comissao fornecedor', 'comissão direta', 'bonus fornecedor'],
        'color': '#90CAF9',
        'icon': '✈️',
        'type': 'revenue',
        'dre_account': 'Outras Receitas',
        'group': 'Comissões Recebidas'
    },

    # ========== RECEITAS FINANCEIRAS ==========
    'Rendimentos de Aplicações': {
        'keywords': ['rendimento', 'aplicacao', 'aplicação', 'cdb', 'renda fixa'],
        'color': '#7E57C2',
        'icon': '📈',
        'type': 'revenue',
        'dre_account': 'Receitas Financeiras',
        'group': 'Receitas Financeiras'
    },
    'Juros Recebidos': {
        'keywords': ['juros recebido', 'juros ativo', 'correcao monetaria'],
        'color': '#9575CD',
        'icon': '💹',
        'type': 'revenue',
        'dre_account': 'Receitas Financeiras',
        'group': 'Receitas Financeiras'
    },
    'Ganhos com Variação Cambial': {
        'keywords': ['ganho cambial', 'variacao cambial positiva', 'lucro cambio'],
        'color': '#B39DDB',
        'icon': '💱',
        'type': 'revenue',
        'dre_account': 'Receitas Financeiras',
        'group': 'Receitas Financeiras'
    },

    # ========== RECEITAS - OUTRAS ENTRADAS ==========
    'Reembolso de Despesas': {
        'keywords': ['reembolso', 'ressarcimento', 'devolucao despesa'],
        'color': '#80CBC4',
        'icon': '↩️',
        'type': 'revenue',
        'dre_account': 'Outras Receitas',
        'group': 'Outras Entradas'
    },
    'Empréstimos Bancários': {
        'keywords': ['emprestimo', 'empréstimo', 'financiamento recebido'],
        'color': '#4DB6AC',
        'icon': '🏦',
        'type': 'other',
        'dre_account': None,
        'group': 'Outras Entradas'
    },
    'Venda de Ativos': {
        'keywords': ['venda ativo', 'venda equipamento', 'alienacao'],
        'color': '#26A69A',
        'icon': '🖥️',
        'type': 'other',
        'dre_account': None,
        'group': 'Outras Entradas'
    },

    # ========== RECEITAS - DEVOLUÇÕES ==========
    'Devoluções de Compra de Ativo': {
        'keywords': ['devolucao ativo', 'devolução compra'],
        'color': '#80DEEA',
        'icon': '🔙',
        'type': 'other',
        'dre_account': None,
        'group': 'Devoluções'
    },
    'Devoluções de Compra de Serviços': {
        'keywords': ['devolucao servico', 'devolução serviço', 'estorno fornecedor'],
        'color': '#4DD0E1',
        'icon': '↪️',
        'type': 'other',
        'dre_account': None,
        'group': 'Devoluções'
    },

    # ========== RECEITAS - ADIANTAMENTOS ==========
    'Adiantamentos - Pacotes Futuros': {
        'keywords': ['adiantamento cliente', 'antecipacao', 'sinal', 'entrada pacote'],
        'color': '#FFA726',
        'icon': '💳',
        'type': 'liability',
        'dre_account': None,
        'group': 'Adiantamentos de Clientes'
    },

    # ========== DESPESAS - DESPESAS DIRETAS (CUSTO) ==========
    'Fornecedores - Escolas/Acomodações USA': {
        'keywords': ['escola usa', 'acomodacao usa', 'homestay', 'residencia estudantil'],
        'color': '#EF5350',
        'icon': '🏫',
        'type': 'expense',
        'dre_account': 'Custo dos Serviços Prestados',
        'group': 'Despesas Diretas'
    },
    'Compra de Serviços': {
        'keywords': ['compra servico', 'servico terceiro'],
        'color': '#E57373',
        'icon': '🛒',
        'type': 'expense',
        'dre_account': 'Custo dos Serviços Prestados',
        'group': 'Despesas Diretas'
    },
    'Fornecedores - Passagens Aéreas': {
        'keywords': ['passagem aerea', 'passagem aérea', 'bilhete aereo', 'cia aerea', 'latam', 'gol', 'azul'],
        'color': '#EF9A9A',
        'icon': '✈️',
        'type': 'expense',
        'dre_account': 'Custo dos Serviços Prestados',
        'group': 'Despesas Diretas'
    },
    'Fornecedores - Seguros Viagem': {
        'keywords': ['seguro viagem', 'assist card', 'travel ace', 'coris'],
        'color': '#FFCDD2',
        'icon': '🛡️',
        'type': 'expense',
        'dre_account': 'Custo dos Serviços Prestados',
        'group': 'Despesas Diretas'
    },
    'Fornecedores - Ingressos Parques': {
        'keywords': ['ingresso', 'ticket', 'disney', 'universal', 'parque'],
        'color': '#FF8A80',
        'icon': '🎢',
        'type': 'expense',
        'dre_account': 'Custo dos Serviços Prestados',
        'group': 'Despesas Diretas'
    },
    'Fornecedores - Transfers USA': {
        'keywords': ['transfer', 'transporte', 'shuttle', 'uber'],
        'color': '#FF5252',
        'icon': '🚐',
        'type': 'expense',
        'dre_account': 'Custo dos Serviços Prestados',
        'group': 'Despesas Diretas'
    },

    # ========== DESPESAS - MARKETING E COMERCIAL ==========
    'Despesas de Viagens': {
        'keywords': ['viagem comercial', 'hospedagem', 'passagem trabalho'],
        'color': '#AB47BC',
        'icon': '✈️',
        'type': 'expense',
        'dre_account': 'Despesas de Vendas e Marketing',
        'group': 'Despesas de Marketing e Comercial'
    },
    'Google Ads': {
        'keywords': ['google ads', 'adwords', 'google advertising'],
        'color': '#BA68C8',
        'icon': '🔍',
        'type': 'expense',
        'dre_account': 'Despesas de Vendas e Marketing',
        'group': 'Despesas de Marketing e Comercial'
    },
    'Facebook/Instagram Ads': {
        'keywords': ['facebook ads', 'instagram ads', 'meta ads', 'facebook advertising'],
        'color': '#CE93D8',
        'icon': '📱',
        'type': 'expense',
        'dre_account': 'Despesas de Vendas e Marketing',
        'group': 'Despesas de Marketing e Comercial'
    },
    'Material Promocional': {
        'keywords': ['material promocional', 'brochure', 'folder', 'catalogo'],
        'color': '#E1BEE7',
        'icon': '📰',
        'type': 'expense',
        'dre_account': 'Despesas de Vendas e Marketing',
        'group': 'Despesas de Marketing e Comercial'
    },
    'Eventos e Feiras': {
        'keywords': ['evento', 'feira', 'congresso', 'stand'],
        'color': '#F3E5F5',
        'icon': '🎪',
        'type': 'expense',
        'dre_account': 'Despesas de Vendas e Marketing',
        'group': 'Despesas de Marketing e Comercial'
    },
    'Brindes e presentes': {
        'keywords': ['brinde', 'presente', 'cortesia'],
        'color': '#D1C4E9',
        'icon': '🎁',
        'type': 'expense',
        'dre_account': 'Despesas de Vendas e Marketing',
        'group': 'Despesas de Marketing e Comercial'
    },

    # ========== DESPESAS - PESSOAL ==========
    'Salários': {
        'keywords': ['salario', 'salário', 'vencimento', 'remuneracao'],
        'color': '#5C6BC0',
        'icon': '💼',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'Adiantamento': {
        'keywords': ['adiantamento', 'adiantamento salarial', 'vale'],
        'color': '#7986CB',
        'icon': '💵',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'Rescisões': {
        'keywords': ['rescisao', 'rescisão', 'demissao', 'demissão'],
        'color': '#9FA8DA',
        'icon': '📋',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'Férias': {
        'keywords': ['ferias', 'férias'],
        'color': '#C5CAE9',
        'icon': '🏖️',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    '13º Salário': {
        'keywords': ['13 salario', '13º salário', 'decimo terceiro'],
        'color': '#E8EAF6',
        'icon': '🎁',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'INSS': {
        'keywords': ['inss', 'previdencia', 'previdência'],
        'color': '#3F51B5',
        'icon': '🏛️',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'FGTS': {
        'keywords': ['fgts', 'fundo garantia'],
        'color': '#536DFE',
        'icon': '🏦',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'IRRF': {
        'keywords': ['irrf', 'ir fonte', 'imposto renda retido'],
        'color': '#304FFE',
        'icon': '📊',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'Assistência Médica': {
        'keywords': ['plano saude', 'plano de saúde', 'assistencia medica', 'unimed'],
        'color': '#448AFF',
        'icon': '⚕️',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'Seguro de Vida': {
        'keywords': ['seguro vida'],
        'color': '#82B1FF',
        'icon': '🛡️',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'Outros Benefícios': {
        'keywords': ['beneficio', 'benefício', 'vale alimentacao', 'vale transporte', 'vr', 'vt'],
        'color': '#B3D9FF',
        'icon': '🎫',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'Prestadores de Serviço - PJ': {
        'keywords': ['prestador servico', 'pj', 'autonomo', 'autônomo'],
        'color': '#1976D2',
        'icon': '👔',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },
    'Pró-Labore': {
        'keywords': ['pro labore', 'pró-labore', 'retirada socio', 'retirada sócio'],
        'color': '#1565C0',
        'icon': '👨‍💼',
        'type': 'expense',
        'dre_account': 'Despesas com Pessoal',
        'group': 'Despesas com Pessoal'
    },

    # ========== DESPESAS - ADMINISTRATIVAS ==========
    'Telefonia': {
        'keywords': ['telefone', 'celular', 'telefonia', 'tim', 'vivo', 'claro'],
        'color': '#00897B',
        'icon': '📞',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Despesas Administrativas'
    },
    'Material de Escritório': {
        'keywords': ['material escritorio', 'material escritório', 'papelaria'],
        'color': '#26A69A',
        'icon': '✏️',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Despesas Administrativas'
    },
    'Seguros': {
        'keywords': ['seguro', 'apolice', 'apólice'],
        'color': '#4DB6AC',
        'icon': '🛡️',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Despesas Administrativas'
    },
    'Contabilidade': {
        'keywords': ['contabilidade', 'contador', 'escritorio contabil'],
        'color': '#80CBC4',
        'icon': '📊',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Despesas Administrativas'
    },
    'Advogados': {
        'keywords': ['advogado', 'juridico', 'jurídico', 'honorario advocaticio'],
        'color': '#B2DFDB',
        'icon': '⚖️',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Despesas Administrativas'
    },

    # ========== DESPESAS - TECNOLOGIA E SISTEMAS ==========
    'Software - Gestão de Website': {
        'keywords': ['website', 'site', 'dominio', 'hospedagem', 'wordpress'],
        'color': '#FF6F00',
        'icon': '🌐',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Tecnologia e Sistemas'
    },
    'Software - CRM e gestão': {
        'keywords': ['crm', 'salesforce', 'pipedrive', 'hubspot'],
        'color': '#FF8F00',
        'icon': '👥',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Tecnologia e Sistemas'
    },
    'Software - ERP e gestão financeira': {
        'keywords': ['erp', 'gestao financeira', 'gestão financeira', 'omie', 'bling'],
        'color': '#FFA000',
        'icon': '💼',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Tecnologia e Sistemas'
    },
    'Software - Google Workspace e gestão de rotinas': {
        'keywords': ['google workspace', 'g suite', 'gmail', 'drive'],
        'color': '#FFB300',
        'icon': '📧',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Tecnologia e Sistemas'
    },
    'Software - Outros': {
        'keywords': ['software', 'assinatura', 'saas'],
        'color': '#FFC107',
        'icon': '💻',
        'type': 'expense',
        'dre_account': 'Despesas Administrativas',
        'group': 'Tecnologia e Sistemas'
    },

    # ========== DESPESAS FINANCEIRAS / BANCOS ==========
    'Juros sobre Empréstimos': {
        'keywords': ['juros emprestimo', 'juros empréstimo', 'encargo financeiro'],
        'color': '#D32F2F',
        'icon': '📉',
        'type': 'expense',
        'dre_account': 'Despesas Financeiras',
        'group': 'Despesas Financeiras / Bancos'
    },
    'Multas': {
        'keywords': ['multa', 'penalidade'],
        'color': '#E64A19',
        'icon': '⚠️',
        'type': 'expense',
        'dre_account': 'Despesas Financeiras',
        'group': 'Despesas Financeiras / Bancos'
    },
    'Pagamento de Empréstimos': {
        'keywords': ['pagamento emprestimo', 'pagamento empréstimo', 'amortizacao'],
        'color': '#F57C00',
        'icon': '💳',
        'type': 'other',
        'dre_account': None,
        'group': 'Despesas Financeiras / Bancos'
    },
    'Tarifas Bancárias': {
        'keywords': ['tarifa bancaria', 'tarifa bancária', 'taxa banco', 'ted', 'doc'],
        'color': '#FFA000',
        'icon': '🏦',
        'type': 'expense',
        'dre_account': 'Despesas Financeiras',
        'group': 'Despesas Financeiras / Bancos'
    },
    'IOF': {
        'keywords': ['iof', 'imposto operacao financeira'],
        'color': '#FBC02D',
        'icon': '📊',
        'type': 'expense',
        'dre_account': 'Despesas Financeiras',
        'group': 'Despesas Financeiras / Bancos'
    },
    'Spread Cambial': {
        'keywords': ['spread cambial', 'variacao cambial negativa', 'perda cambio'],
        'color': '#F9A825',
        'icon': '💱',
        'type': 'expense',
        'dre_account': 'Despesas Financeiras',
        'group': 'Despesas Financeiras / Bancos'
    },
    'Taxas Gateway Pagamento': {
        'keywords': ['gateway', 'pagseguro', 'mercado pago', 'paypal', 'stripe'],
        'color': '#F57F17',
        'icon': '💳',
        'type': 'expense',
        'dre_account': 'Despesas Financeiras',
        'group': 'Despesas Financeiras / Bancos'
    },

    # ========== IMPOSTOS E TAXAS ==========
    'Simples Nacional (DAS)': {
        'keywords': ['simples nacional', 'das', 'imposto simples'],
        'color': '#C62828',
        'icon': '🏛️',
        'type': 'expense',
        'dre_account': 'Impostos',
        'group': 'Impostos e Taxas'
    },
    'Taxas Municipais/Alvará': {
        'keywords': ['taxa municipal', 'alvara', 'alvará', 'iss'],
        'color': '#AD1457',
        'icon': '🏢',
        'type': 'expense',
        'dre_account': 'Outros Tributos',
        'group': 'Impostos e Taxas'
    },

    # ========== COMISSÕES PAGAS ==========
    'Comissões Pagas - Escolas Parceiras': {
        'keywords': ['comissao escola', 'comissão escola', 'comissao parceiro'],
        'color': '#6A1B9A',
        'icon': '🎓',
        'type': 'expense',
        'dre_account': 'Despesas Variáveis',
        'group': 'Comissões Pagas'
    },
    'Comissões Pagas - Indicações': {
        'keywords': ['comissao indicacao', 'comissão indicação', 'comissao parceiro'],
        'color': '#8E24AA',
        'icon': '🤝',
        'type': 'expense',
        'dre_account': 'Despesas Variáveis',
        'group': 'Comissões Pagas'
    },
    'Bonificações - Acompanhante de grupo': {
        'keywords': ['acompanhante', 'lider grupo', 'líder grupo', 'group leader'],
        'color': '#AB47BC',
        'icon': '👨‍✈️',
        'type': 'expense',
        'dre_account': 'Despesas Variáveis',
        'group': 'Comissões Pagas'
    },
    'Outras bonificações': {
        'keywords': ['bonificacao', 'bonificação', 'bonus', 'bônus'],
        'color': '#BA68C8',
        'icon': '🎁',
        'type': 'expense',
        'dre_account': 'Despesas Variáveis',
        'group': 'Comissões Pagas'
    },

    # ========== DEVOLUÇÕES DE VENDAS ==========
    'Devoluções de Vendas de Serviços Prestados': {
        'keywords': ['devolucao venda', 'devolução venda', 'cancelamento', 'estorno cliente'],
        'color': '#FF5252',
        'icon': '↩️',
        'type': 'expense',
        'dre_account': 'Deduções de Receita',
        'group': 'Devoluções de Vendas'
    },

    # ========== INVESTIMENTOS ==========
    'Máquinas e Equipamentos': {
        'keywords': ['maquina', 'máquina', 'equipamento'],
        'color': '#546E7A',
        'icon': '⚙️',
        'type': 'other',
        'dre_account': None,
        'group': 'Investimento'
    },
    'Equipamentos de Informática': {
        'keywords': ['computador', 'notebook', 'impressora', 'monitor'],
        'color': '#607D8B',
        'icon': '💻',
        'type': 'other',
        'dre_account': None,
        'group': 'Investimento'
    },
    'Comunicação': {
        'keywords': ['equipamento comunicacao', 'equipamento comunicação'],
        'color': '#78909C',
        'icon': '📡',
        'type': 'other',
        'dre_account': None,
        'group': 'Investimento'
    },

    # ========== OUTRAS DESPESAS ==========
    'Adiantamento a Fornecedores': {
        'keywords': ['adiantamento fornecedor', 'antecipacao fornecedor'],
        'color': '#90A4AE',
        'icon': '💸',
        'type': 'other',
        'dre_account': None,
        'group': 'Outras Despesas'
    },
    'Distribuição de Lucros - Retirada': {
        'keywords': ['distribuicao lucro', 'distribuição lucro', 'dividendo', 'retirada lucro'],
        'color': '#B0BEC5',
        'icon': '💰',
        'type': 'other',
        'dre_account': None,
        'group': 'Outras Despesas'
    },

    'Uncategorized': {
        'keywords': [],
        'color': '#607D8B',
        'icon': '❓',
        'type': 'uncategorized',
        'dre_account': None,
        'group': 'Sem Categoria'
    }
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
