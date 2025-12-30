"""
Credit Card Sales Parser - Parse credit card sales CSV files
Supports multiple acquirers (Cielo, Stone, Rede, etc.)
"""

import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class CreditCardParser:
    """Parser for credit card sales CSV files"""

    # Campos obrigatórios (marcados com * no CSV)
    REQUIRED_FIELDS = [
        'CPF/CNPJ do estabelecimento',
        'Quantidade total de parcelas',
        'Valor bruto',
        'Taxa/tarifa',
        'Valor líquido',
        'Data do lançamento',
        'Data prevista do pagamento'
    ]

    def __init__(self):
        self.sales = []
        self.installments = []  # Parcelas geradas
        self.errors = []

    def parse_csv(self, file_path):
        """
        Parse credit card sales CSV file

        Args:
            file_path: Path to CSV file

        Returns:
            tuple: (sales_df, installments_df, errors_list)
        """
        print(f"[CARD-PARSER] Iniciando parse de {file_path}")

        try:
            # Read CSV with Brazilian encoding
            df = pd.read_csv(file_path, encoding='utf-8-sig', dtype=str)

            print(f"[CARD-PARSER] Arquivo lido: {len(df)} linhas")

            # Process each sale
            for idx, row in df.iterrows():
                try:
                    # Validate required fields
                    missing_fields = self._validate_required_fields(row)
                    if missing_fields:
                        error_msg = f"Linha {idx + 2}: Campos obrigatórios faltando: {', '.join(missing_fields)}"
                        print(f"[CARD-PARSER] ERRO: {error_msg}")
                        self.errors.append(error_msg)
                        continue

                    # Parse sale
                    sale = self._parse_sale(row, idx)
                    self.sales.append(sale)

                    # Generate installments
                    installments = self._generate_installments(sale)
                    self.installments.extend(installments)

                except Exception as e:
                    error_msg = f"Linha {idx + 2}: Erro ao processar - {str(e)}"
                    print(f"[CARD-PARSER] ERRO: {error_msg}")
                    self.errors.append(error_msg)
                    continue

            # Create DataFrames
            sales_df = pd.DataFrame(self.sales) if self.sales else pd.DataFrame()
            installments_df = pd.DataFrame(self.installments) if self.installments else pd.DataFrame()

            print(f"[CARD-PARSER] Processado: {len(self.sales)} vendas, {len(self.installments)} parcelas")
            print(f"[CARD-PARSER] Erros: {len(self.errors)}")

            return sales_df, installments_df, self.errors

        except Exception as e:
            error_msg = f"Erro ao ler arquivo: {str(e)}"
            print(f"[CARD-PARSER] ERRO CRÍTICO: {error_msg}")
            self.errors.append(error_msg)
            return pd.DataFrame(), pd.DataFrame(), self.errors

    def _validate_required_fields(self, row):
        """
        Validate that all required fields are present

        Returns:
            list: Missing field names (empty if all present)
        """
        missing = []
        for field in self.REQUIRED_FIELDS:
            value = str(row.get(field, '')).strip()
            if not value or value.lower() == 'nan':
                missing.append(field)
        return missing

    def _parse_sale(self, row, idx):
        """
        Parse a single sale row

        Returns:
            dict: Parsed sale data
        """
        # Parse dates
        data_venda = self._parse_date(row.get('Data da venda', ''))
        data_lancamento = self._parse_date(row.get('Data do lançamento', ''))
        data_primeiro_pagamento = self._parse_date(row.get('Data prevista do pagamento', ''))

        # Parse values
        valor_bruto = self._parse_decimal(row.get('Valor bruto', '0'))
        taxa_tarifa = self._parse_decimal(row.get('Taxa/tarifa', '0'))
        valor_liquido = self._parse_decimal(row.get('Valor líquido', '0'))

        # Parse installments
        qtd_parcelas = int(row.get('Quantidade total de parcelas', '1'))

        # Clean CPF/CNPJ
        cpf_cnpj = self._clean_cpf_cnpj(row.get('CPF/CNPJ do estabelecimento', ''))
        cpf_cliente = self._clean_cpf_cnpj(row.get('CPF', ''))

        sale = {
            'id': f"{row.get('Código da venda', f'VENDA_{idx}')}",
            'data_venda': data_venda,
            'hora_venda': row.get('Hora da venda', ''),
            'estabelecimento': row.get('Estabelecimento', ''),
            'cpf_cnpj_estabelecimento': cpf_cnpj,
            'forma_pagamento': row.get('Forma de pagamento', ''),
            'qtd_parcelas': qtd_parcelas,
            'bandeira': row.get('Bandeira', ''),
            'valor_bruto': valor_bruto,
            'taxa_tarifa': taxa_tarifa,
            'valor_liquido': valor_liquido,
            'status': row.get('Status da venda', ''),
            'tipo_lancamento': row.get('Tipo de lançamento', ''),
            'modalidade': row.get('Modalidade', ''),
            'tipo_captura': row.get('Tipo de captura', ''),
            'documento_origem': row.get('Documento de origem', ''),
            'origem_valor': row.get('Origem do valor', ''),
            'motivo': row.get('Motivo', ''),
            'data_lancamento': data_lancamento,
            'data_primeiro_pagamento': data_primeiro_pagamento,
            'codigo_autorizacao': row.get('Código de autorização', ''),
            'nsu_doc': row.get('NSU/DOC', ''),
            'codigo_venda': row.get('Código da venda', ''),
            'tid': row.get('TID', ''),
            'origem_cartao': row.get('Origem do cartão', ''),
            'nome_cliente': row.get('Nome', ''),
            'email_cliente': row.get('Email', ''),
            'telefone_cliente': row.get('Telefone', ''),
            'cpf_cliente': cpf_cliente,
            'adquirente': row.get('Adquirente', 'Não especificado')
        }

        return sale

    def _generate_installments(self, sale):
        """
        Generate installments for a sale

        Args:
            sale: Parsed sale dict

        Returns:
            list: List of installment dicts
        """
        installments = []
        qtd_parcelas = sale['qtd_parcelas']
        valor_liquido = sale['valor_liquido']
        data_base = sale['data_primeiro_pagamento']

        if not data_base or qtd_parcelas < 1:
            return []

        # Calculate installment value
        valor_parcela = valor_liquido / qtd_parcelas
        valor_parcela_rounded = round(valor_parcela, 2)

        # Generate installments
        total_distribuido = 0
        for i in range(qtd_parcelas):
            # Calculate date (add i months to base date)
            data_parcela = data_base + relativedelta(months=i)

            # Last installment gets the remainder
            if i == qtd_parcelas - 1:
                valor_parcela_atual = round(valor_liquido - total_distribuido, 2)
            else:
                valor_parcela_atual = valor_parcela_rounded
                total_distribuido += valor_parcela_atual

            installment = {
                'venda_id': sale['id'],
                'numero_parcela': i + 1,
                'total_parcelas': qtd_parcelas,
                'data_prevista': data_parcela,
                'valor': valor_parcela_atual,
                'cpf_cnpj_estabelecimento': sale['cpf_cnpj_estabelecimento'],
                'estabelecimento': sale['estabelecimento'],
                'bandeira': sale['bandeira'],
                'adquirente': sale['adquirente'],
                'nsu_doc': sale['nsu_doc'],
                'status_vinculacao': 'Pendente',  # To be updated by matcher
                'ofx_id': None  # To be filled by matcher
            }

            installments.append(installment)

        return installments

    def _parse_date(self, date_str):
        """Parse date string (DD/MM/YYYY) to datetime"""
        if not date_str or str(date_str).lower() == 'nan':
            return None

        try:
            return datetime.strptime(str(date_str).strip(), '%d/%m/%Y')
        except:
            return None

    def _parse_decimal(self, value_str):
        """Parse decimal value (handles comma and dot)"""
        if not value_str or str(value_str).lower() == 'nan':
            return 0.0

        try:
            # Remove thousands separator and replace comma with dot
            clean_value = str(value_str).replace('.', '').replace(',', '.')
            return float(clean_value)
        except:
            return 0.0

    def _clean_cpf_cnpj(self, cpf_cnpj):
        """Remove formatting from CPF/CNPJ"""
        if not cpf_cnpj or str(cpf_cnpj).lower() == 'nan':
            return ''

        # Remove all non-numeric characters
        return ''.join(filter(str.isdigit, str(cpf_cnpj)))
