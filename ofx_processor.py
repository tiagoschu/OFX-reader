"""
OFX Processor Module
Handles parsing of OFX files and consolidation into pandas DataFrame
"""

import os
from datetime import datetime
from typing import List, Dict, Any
import chardet
import pandas as pd
from ofxparse import OfxParser


class OFXProcessor:
    def __init__(self):
        self.transactions = []
        self.processed_files = []
        self.errors = []

    def try_parse_with_encoding(self, file_path: str, encoding: str) -> Any:
        """Try to parse OFX file with a specific encoding"""
        try:
            with open(file_path, encoding=encoding, errors='strict') as f:
                content = f.read()
                # Reset file pointer by reading from string
                from io import StringIO
                f_string = StringIO(content)
                ofx = OfxParser.parse(f_string)
                return ofx, encoding
        except (UnicodeDecodeError, UnicodeEncodeError, LookupError):
            # Encoding error - try next encoding
            return None, None
        except Exception:
            # Other errors (OFX parsing errors, etc) - try next encoding
            return None, None

    def parse_ofx_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a single OFX file and extract transactions"""
        file_name = os.path.basename(file_path)

        try:
            # List of encodings to try in order
            encodings_to_try = [
                'utf-8',
                'iso-8859-1',  # Latin-1
                'windows-1252',  # Windows Latin-1
                'cp1252',  # Another Windows encoding
                'latin-1',
                'cp850',  # DOS Latin-1
                'cp437',  # DOS US
                'iso-8859-15',  # Latin-9 with Euro sign
                'utf-16',  # Wide unicode
                'utf-8-sig',  # UTF-8 with BOM
                'ascii'
            ]

            # First try with chardet detection
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    detected = chardet.detect(raw_data)
                    if detected and detected.get('encoding') and detected.get('confidence', 0) > 0.7:
                        detected_encoding = detected['encoding']
                        # Add detected encoding to the front of the list if not already there
                        if detected_encoding not in encodings_to_try:
                            encodings_to_try.insert(0, detected_encoding)
                        elif detected_encoding != encodings_to_try[0]:
                            encodings_to_try.remove(detected_encoding)
                            encodings_to_try.insert(0, detected_encoding)
            except Exception:
                pass  # If chardet fails, continue with default list

            # Try each encoding until one works
            ofx = None
            used_encoding = None

            for encoding in encodings_to_try:
                ofx, used_encoding = self.try_parse_with_encoding(file_path, encoding)
                if ofx is not None:
                    break

            # If all encodings failed, try with errors='ignore' as last resort
            if ofx is None:
                try:
                    with open(file_path, encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        from io import StringIO
                        f_string = StringIO(content)
                        ofx = OfxParser.parse(f_string)
                        used_encoding = 'utf-8 (with errors ignored)'
                except Exception:
                    pass

            # If still failed, try with latin-1 and errors='replace'
            if ofx is None:
                try:
                    with open(file_path, encoding='latin-1', errors='replace') as f:
                        content = f.read()
                        from io import StringIO
                        f_string = StringIO(content)
                        ofx = OfxParser.parse(f_string)
                        used_encoding = 'latin-1 (with errors replaced)'
                except Exception:
                    pass

            # Last resort: try reading as binary and forcing ISO-8859-1
            if ofx is None:
                try:
                    with open(file_path, 'rb') as f:
                        raw_content = f.read()
                        # Force decode as ISO-8859-1 (never fails)
                        content = raw_content.decode('iso-8859-1', errors='ignore')
                        from io import StringIO
                        f_string = StringIO(content)
                        ofx = OfxParser.parse(f_string)
                        used_encoding = 'iso-8859-1 (binary fallback)'
                except Exception as fallback_error:
                    # Capture the actual parsing error for better debugging
                    raise ValueError(f"Não foi possível ler o arquivo. Último erro: {str(fallback_error)}")

            transactions = []

            # Process each account in the OFX file
            for account in ofx.accounts:
                bank_id = getattr(account.institution, 'organization', 'N/A') if hasattr(account, 'institution') else 'N/A'
                account_id = account.account_id if hasattr(account, 'account_id') else 'N/A'
                account_type = account.account_type if hasattr(account, 'account_type') else 'N/A'

                # Extract statement data
                statement = account.statement

                # Process each transaction
                for txn in statement.transactions:
                    transaction = {
                        'arquivo_origem': file_name,
                        'banco': bank_id,
                        'conta': account_id,
                        'tipo_conta': account_type,
                        'data': self.format_date(txn.date),
                        'hora': self.format_time(txn.date),
                        'tipo_transacao': txn.type if hasattr(txn, 'type') else 'OTHER',
                        'valor': float(txn.amount),
                        'descricao': (txn.memo or '').strip(),
                        'id_transacao': txn.id if hasattr(txn, 'id') else '',
                        'numero_cheque': txn.checknum if hasattr(txn, 'checknum') else '',
                    }
                    transactions.append(transaction)

            self.processed_files.append({
                'file': file_name,
                'transactions': len(transactions),
                'status': f'success (encoding: {used_encoding})'
            })

            return {
                'success': True,
                'file': file_name,
                'transactions': transactions,
                'count': len(transactions),
                'encoding': used_encoding
            }

        except Exception as e:
            error_msg = f"Erro ao processar {os.path.basename(file_path)}: {str(e)}"
            self.errors.append(error_msg)
            self.processed_files.append({
                'file': os.path.basename(file_path),
                'transactions': 0,
                'status': f'error: {str(e)}'
            })
            return {
                'success': False,
                'file': os.path.basename(file_path),
                'error': str(e),
                'transactions': [],
                'count': 0
            }

    def format_date(self, date_obj) -> str:
        """Convert datetime to dd/mm/yyyy format"""
        if date_obj is None:
            return ''
        try:
            if isinstance(date_obj, datetime):
                return date_obj.strftime('%d/%m/%Y')
            return str(date_obj)
        except:
            return str(date_obj)

    def format_time(self, date_obj) -> str:
        """Convert datetime to hh:mm:ss format"""
        if date_obj is None:
            return ''
        try:
            if isinstance(date_obj, datetime):
                return date_obj.strftime('%H:%M:%S')
            return ''
        except:
            return ''

    def process_multiple_files(self, file_paths: List[str], remove_duplicates: bool = True) -> pd.DataFrame:
        """Process multiple OFX files and consolidate into a single DataFrame"""
        self.transactions = []
        self.processed_files = []
        self.errors = []

        # Process each file
        for file_path in file_paths:
            result = self.parse_ofx_file(file_path)
            if result['success']:
                self.transactions.extend(result['transactions'])

        # Create DataFrame
        if not self.transactions:
            return pd.DataFrame()

        df = pd.DataFrame(self.transactions)

        # Remove duplicates based on id_transacao + conta + banco
        if remove_duplicates and 'id_transacao' in df.columns:
            initial_count = len(df)
            # Remove rows where id_transacao is not empty and is duplicate
            df_with_id = df[df['id_transacao'] != '']
            df_without_id = df[df['id_transacao'] == '']

            if not df_with_id.empty:
                df_with_id = df_with_id.drop_duplicates(
                    subset=['id_transacao', 'conta', 'banco'],
                    keep='first'
                )

            df = pd.concat([df_with_id, df_without_id], ignore_index=True)
            duplicates_removed = initial_count - len(df)

            if duplicates_removed > 0:
                print(f"Removidas {duplicates_removed} transações duplicadas")

        # Sort by date (convert dd/mm/yyyy to datetime for sorting)
        if 'data' in df.columns and not df.empty:
            try:
                df['data_sort'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
                df = df.sort_values('data_sort')
                df = df.drop('data_sort', axis=1)
            except:
                pass

        return df

    def export_to_csv(self, df: pd.DataFrame, output_path: str, include_time: bool = True) -> bool:
        """Export DataFrame to CSV file"""
        try:
            # Reorder columns
            columns_order = [
                'data', 'hora', 'banco', 'conta', 'tipo_conta',
                'tipo_transacao', 'valor', 'descricao',
                'id_transacao', 'numero_cheque', 'arquivo_origem'
            ]

            # Filter only existing columns
            existing_columns = [col for col in columns_order if col in df.columns]

            # If not including time, remove hora column
            if not include_time and 'hora' in existing_columns:
                existing_columns.remove('hora')

            df_export = df[existing_columns]

            # Export to CSV
            df_export.to_csv(output_path, index=False, encoding='utf-8-sig', sep=';')
            return True
        except Exception as e:
            self.errors.append(f"Erro ao exportar CSV: {str(e)}")
            return False

    def export_to_excel(self, df: pd.DataFrame, output_path: str, include_time: bool = True) -> bool:
        """Export DataFrame to Excel file"""
        try:
            # Reorder columns
            columns_order = [
                'data', 'hora', 'banco', 'conta', 'tipo_conta',
                'tipo_transacao', 'valor', 'descricao',
                'id_transacao', 'numero_cheque', 'arquivo_origem'
            ]

            # Filter only existing columns
            existing_columns = [col for col in columns_order if col in df.columns]

            # If not including time, remove hora column
            if not include_time and 'hora' in existing_columns:
                existing_columns.remove('hora')

            df_export = df[existing_columns]

            # Export to Excel
            df_export.to_excel(output_path, index=False, engine='openpyxl')
            return True
        except Exception as e:
            self.errors.append(f"Erro ao exportar Excel: {str(e)}")
            return False

    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics"""
        if df.empty:
            return {}

        summary = {
            'total_transacoes': len(df),
            'total_creditos': len(df[df['valor'] > 0]) if 'valor' in df.columns else 0,
            'total_debitos': len(df[df['valor'] < 0]) if 'valor' in df.columns else 0,
            'soma_creditos': float(df[df['valor'] > 0]['valor'].sum()) if 'valor' in df.columns else 0,
            'soma_debitos': float(df[df['valor'] < 0]['valor'].sum()) if 'valor' in df.columns else 0,
            'saldo_liquido': float(df['valor'].sum()) if 'valor' in df.columns else 0,
            'bancos': df['banco'].nunique() if 'banco' in df.columns else 0,
            'contas': df['conta'].nunique() if 'conta' in df.columns else 0,
            'arquivos_processados': len(self.processed_files),
            'arquivos_com_erro': len([f for f in self.processed_files if 'error' in f['status']])
        }

        return summary
