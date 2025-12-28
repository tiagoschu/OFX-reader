"""
NFSe XML Parser
Supports ABRASF 2.x and extensible for other standards
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
from utils.cpf_cnpj_validator import clean_cpf_cnpj, identify_and_format


class NFSeParser:
    """Parse NFSe XML files (Brazilian service invoices)"""

    def __init__(self):
        self.supported_standards = ['ABRASF_2']
        self.invoices = []

    def parse_file(self, file_path):
        """
        Parse single NFSe XML file

        Args:
            file_path: Path to XML file

        Returns:
            dict: Invoice data or None if failed
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Detect standard
            standard = self._detect_standard(root)

            if standard == 'ABRASF_2':
                return self._parse_abrasf_2(root, file_path)
            else:
                print(f"[INVOICE] Unsupported standard: {standard}")
                return None

        except Exception as e:
            print(f"[INVOICE] Error parsing {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def parse_files(self, file_paths):
        """
        Parse multiple NFSe XML files

        Args:
            file_paths: List of file paths

        Returns:
            pandas.DataFrame: All invoices
        """
        self.invoices = []

        for file_path in file_paths:
            invoice = self.parse_file(file_path)
            if invoice:
                self.invoices.append(invoice)

        if not self.invoices:
            return pd.DataFrame()

        return pd.DataFrame(self.invoices)

    def _detect_standard(self, root):
        """Detect NFSe XML standard"""
        # ABRASF namespace
        if 'abrasf.org.br' in (root.tag or ''):
            return 'ABRASF_2'

        # Check for ABRASF elements
        ns = {'nfse': 'http://www.abrasf.org.br/nfse.xsd'}
        if root.find('.//nfse:Nfse', ns) is not None:
            return 'ABRASF_2'

        # Default to ABRASF_2 if has Nfse element
        if 'Nfse' in root.tag or root.find('.//*Nfse') is not None:
            return 'ABRASF_2'

        return 'UNKNOWN'

    def _parse_abrasf_2(self, root, file_path):
        """
        Parse ABRASF 2.x standard NFSe

        Args:
            root: XML root element
            file_path: Source file path

        Returns:
            dict: Invoice data
        """
        try:
            # Namespace (may or may not be present)
            ns = {'nfse': 'http://www.abrasf.org.br/nfse.xsd'}

            # Try with and without namespace
            def find_element(path):
                # Try with namespace
                elem = root.find(path, ns)
                if elem is not None:
                    return elem
                # Try without namespace (remove ns prefix)
                simple_path = path.replace('nfse:', './/')
                return root.find(simple_path)

            def get_text(path, default=''):
                elem = find_element(path)
                return elem.text.strip() if elem is not None and elem.text else default

            # Basic info
            numero = get_text('.//Numero')
            codigo_verificacao = get_text('.//CodigoVerificacao')
            data_emissao = get_text('.//DataEmissao')
            competencia = get_text('.//Competencia')

            # Parse date
            try:
                if 'T' in data_emissao:
                    data_dt = datetime.fromisoformat(data_emissao.replace('Z', '+00:00'))
                else:
                    data_dt = datetime.strptime(data_emissao, '%Y-%m-%d')
            except:
                data_dt = None

            # Values
            valor_servicos = float(get_text('.//ValorServicos', '0').replace(',', '.'))
            valor_liquido = float(get_text('.//ValorLiquidoNfse', '0').replace(',', '.'))
            valor_iss = float(get_text('.//ValorIss', '0').replace(',', '.'))
            aliquota = float(get_text('.//Aliquota', '0').replace(',', '.'))

            # Deductions and retentions
            valor_deducoes = float(get_text('.//ValorDeducoes', '0').replace(',', '.'))
            valor_pis = float(get_text('.//ValorPis', '0').replace(',', '.'))
            valor_cofins = float(get_text('.//ValorCofins', '0').replace(',', '.'))
            valor_inss = float(get_text('.//ValorInss', '0').replace(',', '.'))
            valor_ir = float(get_text('.//ValorIr', '0').replace(',', '.'))
            valor_csll = float(get_text('.//ValorCsll', '0').replace(',', '.'))

            # Service info
            discriminacao = get_text('.//Discriminacao')
            item_lista_servico = get_text('.//ItemListaServico')
            codigo_cnae = get_text('.//CodigoCnae')

            # Tomador (customer)
            cpf = get_text('.//Tomador//Cpf')
            cnpj = get_text('.//Tomador//Cnpj')
            cpf_cnpj = cnpj if cnpj else cpf
            cpf_cnpj_clean = clean_cpf_cnpj(cpf_cnpj)

            nome_tomador = get_text('.//Tomador//RazaoSocial')

            # Tomador address
            tomador_endereco = get_text('.//Tomador//Endereco//Endereco')
            tomador_numero = get_text('.//Tomador//Endereco//Numero')
            tomador_bairro = get_text('.//Tomador//Endereco//Bairro')
            tomador_cidade_cod = get_text('.//Tomador//Endereco//CodigoMunicipio')
            tomador_uf = get_text('.//Tomador//Endereco//Uf')
            tomador_cep = get_text('.//Tomador//Endereco//Cep')

            # Prestador (provider) - for validation
            prestador_cnpj = get_text('.//PrestadorServico//Cnpj') or get_text('.//Prestador//Cnpj')
            prestador_razao = get_text('.//PrestadorServico//RazaoSocial')

            # Format CPF/CNPJ
            tipo_doc, cpf_cnpj_formatted, is_valid = identify_and_format(cpf_cnpj_clean)

            invoice_data = {
                'numero': numero,
                'codigo_verificacao': codigo_verificacao,
                'data_emissao': data_emissao,
                'data_dt': data_dt,
                'data': data_dt.strftime('%d/%m/%Y') if data_dt else '',
                'competencia': competencia,

                'valor_servicos': valor_servicos,
                'valor_liquido': valor_liquido,
                'valor_iss': valor_iss,
                'aliquota': aliquota,

                'valor_deducoes': valor_deducoes,
                'valor_pis': valor_pis,
                'valor_cofins': valor_cofins,
                'valor_inss': valor_inss,
                'valor_ir': valor_ir,
                'valor_csll': valor_csll,

                'discriminacao': discriminacao,
                'item_lista_servico': item_lista_servico,
                'codigo_cnae': codigo_cnae,

                'cpf_cnpj': cpf_cnpj_clean,
                'cpf_cnpj_formatted': cpf_cnpj_formatted,
                'tipo_documento': tipo_doc,
                'cpf_cnpj_valid': is_valid,
                'nome_tomador': nome_tomador,

                'tomador_endereco': tomador_endereco,
                'tomador_numero': tomador_numero,
                'tomador_bairro': tomador_bairro,
                'tomador_cidade_cod': tomador_cidade_cod,
                'tomador_uf': tomador_uf,
                'tomador_cep': tomador_cep,

                'prestador_cnpj': clean_cpf_cnpj(prestador_cnpj),
                'prestador_razao': prestador_razao,

                'arquivo_xml': file_path,
                'standard': 'ABRASF_2',

                # For matching
                'status': 'Pendente',
                'match_ofx_ids': None,
                'match_count': 0,
                'valor_matched': 0.0
            }

            return invoice_data

        except Exception as e:
            print(f"[INVOICE] Error parsing ABRASF 2.x: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_summary(self, df):
        """
        Get summary statistics of invoices

        Args:
            df: DataFrame with invoices

        Returns:
            dict: Summary statistics
        """
        if df is None or df.empty:
            return {
                'total_invoices': 0,
                'total_value': 0.0,
                'total_iss': 0.0,
                'unique_customers': 0,
                'date_range': None
            }

        return {
            'total_invoices': len(df),
            'total_value': df['valor_liquido'].sum(),
            'total_iss': df['valor_iss'].sum(),
            'unique_customers': df['cpf_cnpj'].nunique(),
            'date_range': (df['data_dt'].min(), df['data_dt'].max()) if 'data_dt' in df.columns else None,
            'pending_count': len(df[df['status'] == 'Pendente']),
            'matched_count': len(df[df['status'] == 'Pago'])
        }
