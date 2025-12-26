"""
DRE (Income Statement) Structures for Different Business Types

Defines how DRE should be calculated for each category preset
"""

# DRE Structure for Travel Agency - WIZTOUR
# Estrutura focada nas receitas reais da agência (não inclui valores de terceiros)
DRE_TRAVEL_AGENCY = {
    'title': 'DRE - Agência de Viagens (Wiztour)',
    'items': [
        # RECEITAS OPERACIONAIS
        {
            'key': 'receita_comissoes_intercambio',
            'label': 'RECEITAS OPERACIONAIS',
            'type': 'revenue',
            'is_total': True,
            'color': '#2196F3',
            'categories': ['4.1.1', 'Comissão de Intercâmbios']
        },
        {
            'key': 'receita_margem_pacotes',
            'label': '(+) Margem de Pacotes de Viagem',
            'type': 'revenue',
            'is_total': False,
            'color': None,
            'categories': ['4.1.2', 'Margem de Pacotes']
        },
        {
            'key': 'receita_taxas_servico',
            'label': '(+) Taxas de Serviço',
            'type': 'revenue',
            'is_total': False,
            'color': None,
            'categories': ['4.1.3', 'Taxas de Serviço']
        },
        {
            'key': 'receita_bruta',
            'label': '(=) RECEITA BRUTA',
            'type': 'calculated',
            'is_total': True,
            'color': '#42A5F5',
            'formula': lambda d: sum([
                d.get('receita_comissoes_intercambio', 0),
                d.get('receita_margem_pacotes', 0),
                d.get('receita_taxas_servico', 0)
            ])
        },

        # DESPESAS OPERACIONAIS
        {
            'key': 'desp_marketing',
            'label': '(-) Marketing e Publicidade',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['5.1.1', 'Marketing e Publicidade']
        },
        {
            'key': 'desp_comissoes_vendas',
            'label': '(-) Comissões de Vendas',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['5.1.2', 'Comissões de Vendas']
        },
        {
            'key': 'desp_sistemas',
            'label': '(-) Sistemas e Softwares',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['5.1.3', 'Sistemas e Softwares']
        },
        {
            'key': 'desp_contabilidade',
            'label': '(-) Honorários Contábeis',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['5.1.4', 'Honorários Contábeis']
        },
        {
            'key': 'desp_bancarias',
            'label': '(-) Taxas Bancárias',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['5.1.5', 'Taxas Bancárias']
        },
        {
            'key': 'desp_administrativas',
            'label': '(-) Despesas Administrativas',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['5.1.6', 'Despesas Administrativas']
        },
        {
            'key': 'total_despesas',
            'label': '(=) TOTAL DESPESAS OPERACIONAIS',
            'type': 'calculated',
            'is_total': True,
            'color': '#EF5350',
            'formula': lambda d: sum([
                d.get('desp_marketing', 0),
                d.get('desp_comissoes_vendas', 0),
                d.get('desp_sistemas', 0),
                d.get('desp_contabilidade', 0),
                d.get('desp_bancarias', 0),
                d.get('desp_administrativas', 0)
            ])
        },

        # RESULTADO
        {
            'key': 'lucro_liquido',
            'label': '(=) LUCRO LÍQUIDO',
            'type': 'calculated',
            'is_total': True,
            'color': '#4CAF50',
            'formula': lambda d: d.get('receita_bruta', 0) - d.get('total_despesas', 0)
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
