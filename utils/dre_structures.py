"""
DRE (Income Statement) Structures for Different Business Types

Defines how DRE should be calculated for each category preset
"""

# DRE Structure for Travel Agency
DRE_TRAVEL_AGENCY = {
    'title': 'DRE - Agência de Viagens',
    'items': [
        {
            'key': 'receita_comissoes',
            'label': 'RECEITAS DE COMISSÕES',
            'type': 'revenue',
            'is_total': True,
            'color': '#4CAF50',
            'categories': ['Receitas de Comissões', '4-01-001']
        },
        {
            'key': 'receita_markup',
            'label': '(+) Markup sobre Vendas',
            'type': 'revenue',
            'is_total': False,
            'color': None,
            'categories': ['Markup sobre Vendas', '4-01-001-0000100']
        },
        {
            'key': 'receita_taxas',
            'label': '(+) Taxas e FEE',
            'type': 'revenue',
            'is_total': False,
            'color': None,
            'categories': ['Taxas DU', 'FEE', 'Taxas de Serviços', '4-01-004']
        },
        {
            'key': 'receita_operacao_propria',
            'label': '(+) Operação Própria',
            'type': 'revenue',
            'is_total': False,
            'color': None,
            'categories': ['Operação Própria - Receitas', '4-01-120']
        },
        {
            'key': 'receita_bruta',
            'label': '(=) RECEITA BRUTA TOTAL',
            'type': 'calculated',
            'is_total': True,
            'color': '#66BB6A',
            'formula': lambda d: sum([
                d.get('receita_comissoes', 0),
                d.get('receita_markup', 0),
                d.get('receita_taxas', 0),
                d.get('receita_operacao_propria', 0)
            ])
        },
        {
            'key': 'desp_emissores',
            'label': '(-) Pagamentos a Emissores',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Emissores e Promotores', '2-01-002']
        },
        {
            'key': 'desp_comissoes',
            'label': '(-) Comissões Pagas',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Comissões de Agências', '3-02-200']
        },
        {
            'key': 'receita_liquida',
            'label': '(=) RECEITA LÍQUIDA',
            'type': 'calculated',
            'is_total': True,
            'color': '#81C784',
            'formula': lambda d: d.get('receita_bruta', 0) - d.get('desp_emissores', 0) - d.get('desp_comissoes', 0)
        },
        {
            'key': 'desp_pessoal',
            'label': '(-) Despesas com Pessoal',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Despesas c/ Pessoal', '3-02-002']
        },
        {
            'key': 'desp_aluguel',
            'label': '(-) Aluguel e Condomínio',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Aluguéis e Condomínios', '3-02-001']
        },
        {
            'key': 'desp_operacionais',
            'label': '(-) Outras Despesas Operacionais',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Comunicação', 'Energia Elétrica', 'Material de Escritório',
                          'Segurança e Limpeza', 'Despesas Administrativas', '3-02']
        },
        {
            'key': 'lucro_operacional',
            'label': '(=) LUCRO OPERACIONAL',
            'type': 'calculated',
            'is_total': True,
            'color': '#FFA726',
            'formula': lambda d: d.get('receita_liquida', 0) - sum([
                d.get('desp_pessoal', 0),
                d.get('desp_aluguel', 0),
                d.get('desp_operacionais', 0)
            ])
        },
        {
            'key': 'receitas_financeiras',
            'label': '(+) Receitas Financeiras',
            'type': 'revenue',
            'is_total': False,
            'color': None,
            'categories': ['Receitas Financeiras', 'Receitas de Overnight', '4-02-001']
        },
        {
            'key': 'despesas_financeiras',
            'label': '(-) Despesas Financeiras',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Despesas Financeiras', 'Juros e Comissões Bancárias', '3-02-010', '3-03-001']
        },
        {
            'key': 'resultado_financeiro',
            'label': '(=) Resultado Financeiro',
            'type': 'calculated',
            'is_total': False,
            'color': None,
            'formula': lambda d: d.get('receitas_financeiras', 0) - d.get('despesas_financeiras', 0)
        },
        {
            'key': 'lucro_antes_ir',
            'label': '(=) LUCRO ANTES DO IR',
            'type': 'calculated',
            'is_total': True,
            'color': '#FFB74D',
            'formula': lambda d: d.get('lucro_operacional', 0) + d.get('resultado_financeiro', 0)
        },
        {
            'key': 'impostos',
            'label': '(-) Impostos e Taxas',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Impostos e Taxas', '3-02-004']
        },
        {
            'key': 'lucro_liquido',
            'label': '(=) LUCRO LÍQUIDO',
            'type': 'calculated',
            'is_total': True,
            'color': '#1976D2',
            'formula': lambda d: d.get('lucro_antes_ir', 0) - d.get('impostos', 0)
        }
    ]
}

# DRE Structure for General Business
DRE_BUSINESS = {
    'title': 'DRE - Empresarial',
    'items': [
        {
            'key': 'receita_vendas',
            'label': 'RECEITA DE VENDAS',
            'type': 'revenue',
            'is_total': True,
            'color': '#4CAF50',
            'categories': ['Receita de Vendas', 'Receita de Serviços']
        },
        {
            'key': 'deducoes',
            'label': '(-) Deduções e Impostos sobre Vendas',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Deduções', 'Impostos sobre Vendas']
        },
        {
            'key': 'receita_liquida',
            'label': '(=) RECEITA LÍQUIDA',
            'type': 'calculated',
            'is_total': True,
            'color': '#66BB6A',
            'formula': lambda d: d.get('receita_vendas', 0) - d.get('deducoes', 0)
        },
        {
            'key': 'cmv',
            'label': '(-) CMV - Custo das Mercadorias Vendidas',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['CMV - Custo Mercadoria', 'Custo de Produção']
        },
        {
            'key': 'lucro_bruto',
            'label': '(=) LUCRO BRUTO',
            'type': 'calculated',
            'is_total': True,
            'color': '#81C784',
            'formula': lambda d: d.get('receita_liquida', 0) - d.get('cmv', 0)
        },
        {
            'key': 'despesas_operacionais',
            'label': '(-) Despesas Operacionais',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Despesas com Pessoal', 'Aluguel e Condomínio', 'Despesas com Veículos',
                          'Marketing e Publicidade', 'Tecnologia e Software', 'Utilidades e Serviços',
                          'Material de Escritório', 'Despesas Bancárias']
        },
        {
            'key': 'lucro_operacional',
            'label': '(=) LUCRO OPERACIONAL',
            'type': 'calculated',
            'is_total': True,
            'color': '#FFA726',
            'formula': lambda d: d.get('lucro_bruto', 0) - d.get('despesas_operacionais', 0)
        },
        {
            'key': 'resultado_financeiro',
            'label': '(+/-) Resultado Financeiro',
            'type': 'mixed',
            'is_total': False,
            'color': None,
            'categories': ['Receitas Financeiras', 'Empréstimos e Financiamentos']
        },
        {
            'key': 'lucro_antes_ir',
            'label': '(=) LUCRO ANTES DO IR',
            'type': 'calculated',
            'is_total': True,
            'color': '#FFB74D',
            'formula': lambda d: d.get('lucro_operacional', 0) + d.get('resultado_financeiro', 0)
        },
        {
            'key': 'ir_csll',
            'label': '(-) IR e CSLL',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Impostos e Taxas', 'IRPJ', 'CSLL']
        },
        {
            'key': 'lucro_liquido',
            'label': '(=) LUCRO LÍQUIDO DO EXERCÍCIO',
            'type': 'calculated',
            'is_total': True,
            'color': '#1976D2',
            'formula': lambda d: d.get('lucro_antes_ir', 0) - d.get('ir_csll', 0)
        }
    ]
}

# DRE Structure for Personal (simplified)
DRE_PERSONAL = {
    'title': 'Demonstrativo de Resultado Pessoal',
    'items': [
        {
            'key': 'receitas',
            'label': 'RECEITAS TOTAIS',
            'type': 'revenue',
            'is_total': True,
            'color': '#4CAF50',
            'categories': ['Salário', 'Rendimentos', 'Investimentos', 'Outras Receitas']
        },
        {
            'key': 'despesas_essenciais',
            'label': '(-) Despesas Essenciais',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Moradia', 'Alimentação', 'Saúde', 'Transporte']
        },
        {
            'key': 'despesas_variaveis',
            'label': '(-) Despesas Variáveis',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Lazer', 'Educação', 'Vestuário', 'Outros']
        },
        {
            'key': 'saldo',
            'label': '(=) SALDO FINAL',
            'type': 'calculated',
            'is_total': True,
            'color': '#1976D2',
            'formula': lambda d: d.get('receitas', 0) - d.get('despesas_essenciais', 0) - d.get('despesas_variaveis', 0)
        }
    ]
}

# Map category presets to DRE structures
DRE_STRUCTURES = {
    'travel_agency': DRE_TRAVEL_AGENCY,
    'business': DRE_BUSINESS,
    'chart_of_accounts': DRE_BUSINESS,  # Use business DRE for chart of accounts
    'personal': DRE_PERSONAL
}


def get_dre_structure(category_preset):
    """
    Get DRE structure for a given category preset

    Args:
        category_preset: Category preset key ('travel_agency', 'business', 'personal', etc.)

    Returns:
        DRE structure dict
    """
    return DRE_STRUCTURES.get(category_preset, DRE_BUSINESS)
