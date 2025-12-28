"""
DRE (Income Statement) Structures for Different Business Types

Defines how DRE should be calculated for each category preset
"""

# DRE Structure for Travel Agency - WIZTOUR
# Estrutura profissional baseada na operação real
DRE_TRAVEL_AGENCY = {
    'title': 'DRE - Agência de Viagens (Wiztour)',
    'items': [
        # RECEITA BRUTA DE VENDAS
        {
            'key': 'receita_pacotes',
            'label': 'RECEITA BRUTA DE VENDAS',
            'type': 'revenue',
            'is_total': True,
            'color': '#4CAF50',
            'categories': ['Pacotes com Estudos', 'Pacotes Fun Trip', 'Pacotes Culturais', 'Vendas Avulso com Markup']
        },

        # DEDUÇÕES
        {
            'key': 'devolucoes',
            'label': '(-) Devoluções e Cancelamentos',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Devoluções de Vendas de Serviços Prestados']
        },
        {
            'key': 'receita_liquida_vendas',
            'label': '(=) RECEITA LÍQUIDA DE VENDAS',
            'type': 'calculated',
            'is_total': True,
            'color': '#66BB6A',
            'formula': lambda d: d.get('receita_pacotes', 0) - d.get('devolucoes', 0)
        },

        # CUSTO DOS SERVIÇOS PRESTADOS
        {
            'key': 'custo_servicos',
            'label': '(-) CUSTO DOS SERVIÇOS PRESTADOS',
            'type': 'expense',
            'is_total': True,
            'color': '#FF5252',
            'categories': [
                'Fornecedores - Escolas/Acomodações USA',
                'Compra de Serviços',
                'Fornecedores - Passagens Aéreas',
                'Fornecedores - Seguros Viagem',
                'Fornecedores - Ingressos Parques',
                'Fornecedores - Transfers USA'
            ]
        },

        # LUCRO BRUTO
        {
            'key': 'lucro_bruto',
            'label': '(=) LUCRO BRUTO',
            'type': 'calculated',
            'is_total': True,
            'color': '#81C784',
            'formula': lambda d: d.get('receita_liquida_vendas', 0) - d.get('custo_servicos', 0)
        },

        # OUTRAS RECEITAS
        {
            'key': 'outras_receitas',
            'label': '(+) Outras Receitas',
            'type': 'revenue',
            'is_total': False,
            'color': None,
            'categories': [
                'Comissões - Consolidadora Confiança',
                'Comissões - Portal JustTravel',
                'Comissões - Outras Consolidadoras',
                'Comissões - Fornecedores Diretos',
                'Reembolso de Despesas'
            ]
        },

        # DESPESAS DE VENDAS E MARKETING
        {
            'key': 'desp_vendas_marketing',
            'label': '(-) Despesas de Vendas e Marketing',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': [
                'Despesas de Viagens',
                'Google Ads',
                'Facebook/Instagram Ads',
                'Material Promocional',
                'Eventos e Feiras',
                'Brindes e presentes'
            ]
        },

        # DESPESAS COM PESSOAL
        {
            'key': 'desp_pessoal',
            'label': '(-) Despesas com Pessoal',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': [
                'Salários', 'Adiantamento', 'Rescisões', 'Férias', '13º Salário',
                'INSS', 'FGTS', 'IRRF',
                'Assistência Médica', 'Seguro de Vida', 'Outros Benefícios',
                'Prestadores de Serviço - PJ', 'Pró-Labore'
            ]
        },

        # DESPESAS ADMINISTRATIVAS
        {
            'key': 'desp_administrativas',
            'label': '(-) Despesas Administrativas',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': [
                'Telefonia',
                'Material de Escritório',
                'Seguros',
                'Contabilidade',
                'Advogados',
                'Software - Gestão de Website',
                'Software - CRM e gestão',
                'Software - ERP e gestão financeira',
                'Software - Google Workspace e gestão de rotinas',
                'Software - Outros'
            ]
        },

        # DESPESAS VARIÁVEIS
        {
            'key': 'desp_variaveis',
            'label': '(-) Despesas Variáveis (Comissões)',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': [
                'Comissões Pagas - Escolas Parceiras',
                'Comissões Pagas - Indicações',
                'Bonificações - Acompanhante de grupo',
                'Outras bonificações'
            ]
        },

        # LUCRO OPERACIONAL
        {
            'key': 'lucro_operacional',
            'label': '(=) LUCRO OPERACIONAL (EBITDA)',
            'type': 'calculated',
            'is_total': True,
            'color': '#FFA726',
            'formula': lambda d: d.get('lucro_bruto', 0) + d.get('outras_receitas', 0) - sum([
                d.get('desp_vendas_marketing', 0),
                d.get('desp_pessoal', 0),
                d.get('desp_administrativas', 0),
                d.get('desp_variaveis', 0)
            ])
        },

        # RESULTADO FINANCEIRO
        {
            'key': 'receitas_financeiras',
            'label': '(+) Receitas Financeiras',
            'type': 'revenue',
            'is_total': False,
            'color': None,
            'categories': [
                'Rendimentos de Aplicações',
                'Juros Recebidos',
                'Ganhos com Variação Cambial'
            ]
        },
        {
            'key': 'despesas_financeiras',
            'label': '(-) Despesas Financeiras',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': [
                'Juros sobre Empréstimos',
                'Multas',
                'Tarifas Bancárias',
                'IOF',
                'Spread Cambial',
                'Taxas Gateway Pagamento'
            ]
        },
        {
            'key': 'resultado_financeiro',
            'label': '(=) Resultado Financeiro',
            'type': 'calculated',
            'is_total': False,
            'color': None,
            'formula': lambda d: d.get('receitas_financeiras', 0) - d.get('despesas_financeiras', 0)
        },

        # LUCRO ANTES DOS IMPOSTOS
        {
            'key': 'lucro_antes_impostos',
            'label': '(=) LUCRO ANTES DOS IMPOSTOS',
            'type': 'calculated',
            'is_total': True,
            'color': '#FFB74D',
            'formula': lambda d: d.get('lucro_operacional', 0) + d.get('resultado_financeiro', 0)
        },

        # IMPOSTOS
        {
            'key': 'impostos',
            'label': '(-) Impostos e Tributos',
            'type': 'expense',
            'is_total': False,
            'color': None,
            'categories': ['Simples Nacional (DAS)', 'Taxas Municipais/Alvará']
        },

        # LUCRO LÍQUIDO
        {
            'key': 'lucro_liquido',
            'label': '(=) LUCRO LÍQUIDO',
            'type': 'calculated',
            'is_total': True,
            'color': '#1976D2',
            'formula': lambda d: d.get('lucro_antes_impostos', 0) - d.get('impostos', 0)
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
