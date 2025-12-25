"""
Multi-format Exporter
Exports transaction data to various formats
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict


class DataExporter:
    """Exports data to multiple formats"""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize exporter

        Args:
            df: DataFrame with transaction data
        """
        self.df = df.copy() if not df.empty else pd.DataFrame()

    def export_csv(self, file_path: str, separator=';', include_index=False) -> bool:
        """Export to CSV"""
        try:
            self.df.to_csv(
                file_path,
                index=include_index,
                encoding='utf-8-sig',
                sep=separator
            )
            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False

    def export_excel(self, file_path: str, sheet_name='Transações') -> bool:
        """Export to Excel"""
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                self.df.to_excel(writer, sheet_name=sheet_name, index=False)
            return True
        except Exception as e:
            print(f"Error exporting Excel: {e}")
            return False

    def export_json(self, file_path: str, orient='records') -> bool:
        """Export to JSON"""
        try:
            self.df.to_json(
                file_path,
                orient=orient,
                force_ascii=False,
                indent=2,
                date_format='iso'
            )
            return True
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return False

    def export_ofx_consolidated(self, file_path: str) -> bool:
        """
        Export to consolidated OFX format

        Creates a single OFX file with all transactions
        """
        try:
            # OFX Header (SGML format for compatibility)
            ofx_content = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:UTF-8
CHARSET:NONE
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

"""

            # Get current datetime for server timestamp
            now = datetime.now()
            dtserver = now.strftime('%Y%m%d%H%M%S')

            # OFX Body
            ofx_content += f"""<OFX>
<SIGNONMSGSRSV1>
<SONRS>
<STATUS>
<CODE>0</CODE>
<SEVERITY>INFO</SEVERITY>
</STATUS>
<DTSERVER>{dtserver}</DTSERVER>
<LANGUAGE>POR</LANGUAGE>
<FI>
<ORG>OFX Consolidador Pro</ORG>
<FID>0</FID>
</FI>
</SONRS>
</SIGNONMSGSRSV1>
"""

            # Group transactions by bank and account
            if not self.df.empty:
                grouped = self.df.groupby(['banco', 'conta'])

                for (banco, conta), group in grouped:
                    # Sort by date
                    group_sorted = group.sort_values('data')

                    # Get date range
                    if len(group_sorted) > 0:
                        dtstart = self._convert_date_to_ofx(group_sorted.iloc[0]['data'])
                        dtend = self._convert_date_to_ofx(group_sorted.iloc[-1]['data'])

                        # Start bank message
                        ofx_content += f"""<BANKMSGSRSV1>
<STMTTRNRS>
<TRNUID>1</TRNUID>
<STATUS>
<CODE>0</CODE>
<SEVERITY>INFO</SEVERITY>
</STATUS>
<STMTRS>
<CURDEF>BRL</CURDEF>
<BANKACCTFROM>
<BANKID>{banco}</BANKID>
<ACCTID>{conta}</ACCTID>
<ACCTTYPE>CHECKING</ACCTTYPE>
</BANKACCTFROM>
<BANKTRANLIST>
<DTSTART>{dtstart}</DTSTART>
<DTEND>{dtend}</DTEND>
"""

                        # Add each transaction
                        for _, txn in group_sorted.iterrows():
                            dtposted = self._convert_date_to_ofx(txn.get('data', ''))
                            trnamt = txn.get('valor', 0)
                            fitid = txn.get('id_transacao', '') or f"TXN{_}"
                            trntype = self._get_trntype(txn.get('tipo_transacao', ''), trnamt)
                            memo = str(txn.get('descricao', '')).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

                            ofx_content += f"""<STMTTRN>
<TRNTYPE>{trntype}</TRNTYPE>
<DTPOSTED>{dtposted}</DTPOSTED>
<TRNAMT>{trnamt}</TRNAMT>
<FITID>{fitid}</FITID>
<MEMO>{memo}</MEMO>
</STMTTRN>
"""

                        # Close bank transaction list
                        ofx_content += """</BANKTRANLIST>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
"""

            # Close OFX
            ofx_content += "</OFX>\n"

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(ofx_content)

            return True

        except Exception as e:
            print(f"Error exporting OFX: {e}")
            return False

    def _convert_date_to_ofx(self, date_str: str) -> str:
        """Convert dd/mm/yyyy to YYYYMMDD format"""
        try:
            if '/' in date_str:
                # Format: dd/mm/yyyy
                parts = date_str.split('/')
                if len(parts) == 3:
                    return f"{parts[2]}{parts[1]}{parts[0]}"
            return datetime.now().strftime('%Y%m%d')
        except:
            return datetime.now().strftime('%Y%m%d')

    def _get_trntype(self, tipo_transacao: str, valor: float) -> str:
        """Determine OFX transaction type"""
        if tipo_transacao:
            return tipo_transacao.upper()
        elif valor > 0:
            return 'CREDIT'
        else:
            return 'DEBIT'

    def export_pdf_report(self, file_path: str, summary_stats: Dict = None) -> bool:
        """
        Export PDF report with transaction summary

        Args:
            file_path: Path to save PDF
            summary_stats: Optional dictionary with summary statistics
        """
        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()

            # Title
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Relatório de Transações - OFX Consolidador Pro', ln=True, align='C')
            pdf.ln(5)

            # Date
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', ln=True)
            pdf.ln(5)

            # Summary stats if provided
            if summary_stats:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Resumo Geral', ln=True)
                pdf.set_font('Arial', '', 10)

                for key, value in summary_stats.items():
                    if isinstance(value, (int, float)):
                        if 'soma' in key.lower() or 'saldo' in key.lower() or 'total' in key.lower():
                            pdf.cell(0, 6, f'{key}: R$ {value:,.2f}', ln=True)
                        else:
                            pdf.cell(0, 6, f'{key}: {value}', ln=True)

                pdf.ln(5)

            # Transaction table (first 50 transactions)
            if not self.df.empty:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Transações (primeiras 50)', ln=True)

                pdf.set_font('Arial', 'B', 8)
                pdf.cell(25, 6, 'Data', border=1)
                pdf.cell(60, 6, 'Descrição', border=1)
                pdf.cell(30, 6, 'Valor', border=1)
                pdf.cell(40, 6, 'Banco', border=1)
                pdf.ln()

                pdf.set_font('Arial', '', 8)
                for idx, row in self.df.head(50).iterrows():
                    pdf.cell(25, 6, str(row.get('data', '')), border=1)
                    desc = str(row.get('descricao', ''))[:30]  # Truncate long descriptions
                    pdf.cell(60, 6, desc, border=1)
                    valor = row.get('valor', 0)
                    pdf.cell(30, 6, f'R$ {valor:,.2f}', border=1)
                    banco = str(row.get('banco', ''))[:20]
                    pdf.cell(40, 6, banco, border=1)
                    pdf.ln()

            # Save PDF
            pdf.output(file_path)
            return True

        except Exception as e:
            print(f"Error exporting PDF: {e}")
            return False
