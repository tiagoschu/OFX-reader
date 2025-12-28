"""
NFSe Parser - Multi-format support
Supports XML (ABRASF 2.x), CSV, and PDF invoice files
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import re
import os
from utils.cpf_cnpj_validator import clean_cpf_cnpj, identify_and_format


class NFSeParser:
    """Parse NFSe files in multiple formats (XML, CSV, PDF)"""

    def __init__(self):
        self.supported_standards = ['ABRASF_2', 'CSV', 'PDF']
        self.invoices = []

    def parse_file(self, file_path):
        """
        Parse single NFSe file (auto-detect format)

        Args:
            file_path: Path to invoice file (XML, CSV, or PDF)

        Returns:
            dict or list: Invoice data or None if failed
        """
        try:
            # Detect file format
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.xml':
                return self._parse_xml_file(file_path)
            elif file_ext == '.csv':
                return self._parse_csv_file(file_path)
            elif file_ext == '.pdf':
                return self._parse_pdf_file(file_path)
            else:
                print(f"[INVOICE] Unsupported file format: {file_ext}")
                return None

        except Exception as e:
            print(f"[INVOICE] Error parsing {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _parse_xml_file(self, file_path):
        """Parse XML file"""
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Detect standard
        standard = self._detect_standard(root)

        if standard == 'ABRASF_2':
            return self._parse_abrasf_2(root, file_path)
        else:
            print(f"[INVOICE] Unsupported XML standard: {standard}")
            return None

    def _parse_csv_file(self, file_path):
        """
        Parse CSV file with NFSe data

        Expected format:
        ,"NFS-e","Emissão","Competência","Número RPS","Série RPS","Alíquota","Retido","Valor","Dedução","Desc.Inc.","ISS","Incidência","Situação","Tomador",""

        Returns:
            list: List of invoice dicts (one per row)
        """
        try:
            # Read CSV - skip first row if it's header
            df = pd.read_csv(file_path, encoding='utf-8-sig', skipinitialspace=True)

            # Alternative: Try latin-1 if utf-8 fails
            if df.empty:
                df = pd.read_csv(file_path, encoding='latin-1', skipinitialspace=True)

            # Clean column names (remove leading/trailing spaces and quotes)
            df.columns = df.columns.str.strip().str.replace('"', '')

            invoices = []

            for idx, row in df.iterrows():
                try:
                    # Extract data
                    numero = str(row.get('NFS-e', '')).strip()
                    if not numero or numero == '':
                        continue

                    data_emissao_str = str(row.get('Emissão', row.get('Emissao', ''))).strip()
                    competencia_str = str(row.get('Competência', row.get('Competencia', ''))).strip()

                    # Parse dates (DD/MM/YYYY)
                    try:
                        data_dt = datetime.strptime(data_emissao_str, '%d/%m/%Y')
                    except:
                        data_dt = None

                    # Parse values
                    valor_str = str(row.get('Valor', '0')).replace('.', '').replace(',', '.')
                    valor_liquido = float(valor_str) if valor_str else 0.0

                    iss_str = str(row.get('ISS', '0')).replace('.', '').replace(',', '.')
                    valor_iss = float(iss_str) if iss_str else 0.0

                    deducao_str = str(row.get('Dedução', row.get('Deducao', '0'))).replace('.', '').replace(',', '.')
                    valor_deducoes = float(deducao_str) if deducao_str else 0.0

                    # Alíquota (format: "2,01%" -> 2.01)
                    aliquota_str = str(row.get('Alíquota', row.get('Aliquota', '0')))
                    aliquota_str = aliquota_str.replace('%', '').replace(',', '.').strip()
                    aliquota = float(aliquota_str) if aliquota_str else 0.0

                    # Tomador (format: "CPF-Nome" ou "CPF - Nome")
                    tomador_str = str(row.get('Tomador', '')).strip()

                    # Extract CPF/CNPJ and name
                    cpf_cnpj = ''
                    nome_tomador = tomador_str

                    if '-' in tomador_str:
                        parts = tomador_str.split('-', 1)
                        cpf_cnpj = clean_cpf_cnpj(parts[0].strip())
                        nome_tomador = parts[1].strip() if len(parts) > 1 else tomador_str

                    # Format CPF/CNPJ
                    tipo_doc, cpf_cnpj_formatted, is_valid = identify_and_format(cpf_cnpj)

                    # Other fields
                    retido = str(row.get('Retido', 'Não')).strip()
                    situacao = str(row.get('Situação', row.get('Situacao', 'Normal'))).strip()
                    incidencia = str(row.get('Incidência', row.get('Incidencia', ''))).strip()

                    invoice_data = {
                        'numero': numero,
                        'codigo_verificacao': '',
                        'data_emissao': data_emissao_str,
                        'data_dt': data_dt,
                        'data': data_dt.strftime('%d/%m/%Y') if data_dt else data_emissao_str,
                        'competencia': competencia_str,

                        'valor_servicos': valor_liquido,
                        'valor_liquido': valor_liquido,
                        'valor_iss': valor_iss,
                        'aliquota': aliquota,

                        'valor_deducoes': valor_deducoes,
                        'valor_pis': 0.0,
                        'valor_cofins': 0.0,
                        'valor_inss': 0.0,
                        'valor_ir': 0.0,
                        'valor_csll': 0.0,

                        'discriminacao': f"Serviço prestado - {situacao}",
                        'item_lista_servico': '',
                        'codigo_cnae': '',

                        'cpf_cnpj': cpf_cnpj,
                        'cpf_cnpj_formatted': cpf_cnpj_formatted,
                        'tipo_documento': tipo_doc,
                        'cpf_cnpj_valid': is_valid,
                        'nome_tomador': nome_tomador,

                        'tomador_endereco': '',
                        'tomador_numero': '',
                        'tomador_bairro': '',
                        'tomador_cidade_cod': incidencia,
                        'tomador_uf': '',
                        'tomador_cep': '',

                        'prestador_cnpj': '',
                        'prestador_razao': '',

                        'arquivo_xml': file_path,
                        'standard': 'CSV',

                        'status': 'Pendente',
                        'match_ofx_ids': None,
                        'match_count': 0,
                        'valor_matched': 0.0
                    }

                    invoices.append(invoice_data)

                except Exception as e:
                    print(f"[INVOICE] Error parsing CSV row {idx}: {str(e)}")
                    continue

            return invoices

        except Exception as e:
            print(f"[INVOICE] Error parsing CSV file: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _parse_pdf_file(self, file_path):
        """
        Parse PDF file with NFSe data

        Returns:
            list: List of invoice dicts (may contain multiple invoices)
        """
        try:
            # Try to import PDF library
            try:
                import pdfplumber
                PDF_LIBRARY = 'pdfplumber'
            except ImportError:
                try:
                    from PyPDF2 import PdfReader
                    PDF_LIBRARY = 'pypdf2'
                except ImportError:
                    print("[INVOICE] PDF parsing requires 'pdfplumber' or 'PyPDF2'. Install with: pip install pdfplumber")
                    return None

            invoices = []
            text = ""

            # Extract text from PDF
            if PDF_LIBRARY == 'pdfplumber':
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
            else:  # pypdf2
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text() + "\n"

            # Parse extracted text using regex patterns
            # Pattern for NFSe number
            nfse_pattern = r'(?:NFS-?e|Nota Fiscal|N[úu]mero)[\s:]*(\d+)'
            data_pattern = r'(?:Emiss[ãa]o|Data)[\s:]*(\d{2}/\d{2}/\d{4})'
            valor_pattern = r'(?:Valor|Total)[\s:]*R?\$?\s*([\d.,]+)'
            iss_pattern = r'(?:ISS|Imposto)[\s:]*R?\$?\s*([\d.,]+)'
            cpf_pattern = r'(\d{3}\.?\d{3}\.?\d{3}-?\d{2})'
            cnpj_pattern = r'(\d{2}\.?\d{3}\.?\d{3}/?\\d{4}-?\d{2})'

            # Try to find invoices in text
            # Split by common separators
            sections = re.split(r'={10,}|-{10,}|_{10,}', text)

            for section in sections:
                try:
                    # Look for invoice number
                    nfse_match = re.search(nfse_pattern, section, re.IGNORECASE)
                    if not nfse_match:
                        continue

                    numero = nfse_match.group(1)

                    # Extract other data
                    data_match = re.search(data_pattern, section)
                    data_str = data_match.group(1) if data_match else ''

                    try:
                        data_dt = datetime.strptime(data_str, '%d/%m/%Y')
                    except:
                        data_dt = None

                    valor_match = re.search(valor_pattern, section)
                    valor_str = valor_match.group(1).replace('.', '').replace(',', '.') if valor_match else '0'
                    valor_liquido = float(valor_str)

                    iss_match = re.search(iss_pattern, section)
                    iss_str = iss_match.group(1).replace('.', '').replace(',', '.') if iss_match else '0'
                    valor_iss = float(iss_str)

                    # Find CPF/CNPJ
                    cpf_match = re.search(cpf_pattern, section)
                    cnpj_match = re.search(cnpj_pattern, section)

                    cpf_cnpj = ''
                    if cnpj_match:
                        cpf_cnpj = clean_cpf_cnpj(cnpj_match.group(1))
                    elif cpf_match:
                        cpf_cnpj = clean_cpf_cnpj(cpf_match.group(1))

                    tipo_doc, cpf_cnpj_formatted, is_valid = identify_and_format(cpf_cnpj)

                    # Try to find name (usually after CPF/CNPJ)
                    nome_tomador = ''
                    if cpf_match or cnpj_match:
                        # Get text after CPF/CNPJ (next line usually)
                        cpf_pos = section.find(cpf_cnpj)
                        if cpf_pos > 0:
                            rest = section[cpf_pos:cpf_pos + 200]
                            lines = rest.split('\n')
                            if len(lines) > 1:
                                nome_tomador = lines[1].strip()

                    invoice_data = {
                        'numero': numero,
                        'codigo_verificacao': '',
                        'data_emissao': data_str,
                        'data_dt': data_dt,
                        'data': data_dt.strftime('%d/%m/%Y') if data_dt else data_str,
                        'competencia': data_str,

                        'valor_servicos': valor_liquido,
                        'valor_liquido': valor_liquido,
                        'valor_iss': valor_iss,
                        'aliquota': (valor_iss / valor_liquido * 100) if valor_liquido > 0 else 0,

                        'valor_deducoes': 0.0,
                        'valor_pis': 0.0,
                        'valor_cofins': 0.0,
                        'valor_inss': 0.0,
                        'valor_ir': 0.0,
                        'valor_csll': 0.0,

                        'discriminacao': section[:200],  # First 200 chars as description
                        'item_lista_servico': '',
                        'codigo_cnae': '',

                        'cpf_cnpj': cpf_cnpj,
                        'cpf_cnpj_formatted': cpf_cnpj_formatted,
                        'tipo_documento': tipo_doc,
                        'cpf_cnpj_valid': is_valid,
                        'nome_tomador': nome_tomador,

                        'tomador_endereco': '',
                        'tomador_numero': '',
                        'tomador_bairro': '',
                        'tomador_cidade_cod': '',
                        'tomador_uf': '',
                        'tomador_cep': '',

                        'prestador_cnpj': '',
                        'prestador_razao': '',

                        'arquivo_xml': file_path,
                        'standard': 'PDF',

                        'status': 'Pendente',
                        'match_ofx_ids': None,
                        'match_count': 0,
                        'valor_matched': 0.0
                    }

                    invoices.append(invoice_data)

                except Exception as e:
                    print(f"[INVOICE] Error parsing PDF section: {str(e)}")
                    continue

            return invoices if invoices else None

        except Exception as e:
            print(f"[INVOICE] Error parsing PDF file: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def parse_files(self, file_paths):
        """
        Parse multiple NFSe files (XML, CSV, PDF)

        Args:
            file_paths: List of file paths

        Returns:
            pandas.DataFrame: All invoices
        """
        self.invoices = []

        for file_path in file_paths:
            result = self.parse_file(file_path)

            if result:
                # CSV and PDF return lists, XML returns single dict
                if isinstance(result, list):
                    self.invoices.extend(result)
                else:
                    self.invoices.append(result)

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
