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

    def export_pdf_report(self, file_path: str, report_type: str = 'complete',
                          include_details: bool = False, date_filter: tuple = None) -> bool:
        """
        Export PDF report with customizable content

        Args:
            file_path: Path to save PDF
            report_type: Type of report ('complete', 'monthly', 'by_bank', 'by_category', 'detailed', 'gaps')
            include_details: Whether to include full transaction details
            date_filter: Optional tuple (start_date, end_date) in dd/mm/yyyy format
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT

            # Filter data by date if specified
            df = self.df.copy()
            if date_filter and not df.empty:
                df = self._filter_by_date(df, date_filter[0], date_filter[1])

            # Create PDF
            if include_details or report_type == 'detailed':
                doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
            else:
                doc = SimpleDocTemplate(file_path, pagesize=A4)

            story = []
            styles = getSampleStyleSheet()

            # Title style
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#4527A0'),
                spaceAfter=30,
                alignment=TA_CENTER
            )

            # Generate report based on type
            if report_type == 'complete':
                story = self._generate_complete_report(df, styles, title_style, include_details)
            elif report_type == 'monthly':
                story = self._generate_monthly_report(df, styles, title_style, include_details)
            elif report_type == 'by_bank':
                story = self._generate_by_bank_report(df, styles, title_style, include_details)
            elif report_type == 'by_category':
                story = self._generate_by_category_report(df, styles, title_style, include_details)
            elif report_type == 'detailed':
                story = self._generate_detailed_report(df, styles, title_style)
            elif report_type == 'gaps':
                story = self._generate_gaps_report(df, styles, title_style)
            else:
                story = self._generate_complete_report(df, styles, title_style, include_details)

            # Build PDF
            doc.build(story)
            return True

        except ImportError:
            print("⚠️  reportlab não disponível, usando fpdf como fallback")
            return self._export_pdf_simple(file_path, include_details)
        except Exception as e:
            print(f"Error exporting PDF: {e}")
            return False

    def _filter_by_date(self, df, start_date: str, end_date: str):
        """Filter dataframe by date range"""
        try:
            df_copy = df.copy()
            df_copy['data_dt'] = pd.to_datetime(df_copy['data'], format='%d/%m/%Y', errors='coerce')
            start_dt = pd.to_datetime(start_date, format='%d/%m/%Y')
            end_dt = pd.to_datetime(end_date, format='%d/%m/%Y')
            mask = (df_copy['data_dt'] >= start_dt) & (df_copy['data_dt'] <= end_dt)
            return df_copy[mask].drop('data_dt', axis=1)
        except:
            return df

    def _generate_complete_report(self, df, styles, title_style, include_details):
        """Generate complete financial summary report"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        story = []

        # Title
        story.append(Paragraph("📈 Relatório Financeiro Completo", title_style))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        if df.empty:
            story.append(Paragraph("Nenhum dado disponível para o período selecionado.", styles['Normal']))
            return story

        # Summary statistics
        total = len(df)
        receitas = df[df['valor'] > 0]['valor'].sum()
        despesas = abs(df[df['valor'] < 0]['valor'].sum())
        saldo = receitas - despesas

        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Transações', f'{total:,}'],
            ['Receitas', f'R$ {receitas:,.2f}'],
            ['Despesas', f'R$ {despesas:,.2f}'],
            ['Saldo', f'R$ {saldo:,.2f}'],
            ['Bancos', str(df['banco'].nunique())],
            ['Contas', str(df['conta'].nunique())],
        ]

        t = Table(summary_data, colWidths=[8*cm, 8*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4527A0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 1*cm))

        if include_details:
            story.append(self._add_transaction_table(df, styles))

        return story

    def _generate_monthly_report(self, df, styles, title_style, include_details):
        """Generate monthly analysis report"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        story = []
        story.append(Paragraph("📅 Análise Mensal", title_style))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        if df.empty:
            story.append(Paragraph("Nenhum dado disponível.", styles['Normal']))
            return story

        # Convert dates and extract month/year
        df_copy = df.copy()
        df_copy['data_dt'] = pd.to_datetime(df_copy['data'], format='%d/%m/%Y', errors='coerce')
        df_copy['mes_ano'] = df_copy['data_dt'].dt.strftime('%m/%Y')

        # Group by month
        monthly_data = [['Mês/Ano', 'Transações', 'Receitas', 'Despesas', 'Saldo']]

        for mes_ano in sorted(df_copy['mes_ano'].dropna().unique()):
            month_df = df_copy[df_copy['mes_ano'] == mes_ano]
            total = len(month_df)
            receitas = month_df[month_df['valor'] > 0]['valor'].sum()
            despesas = abs(month_df[month_df['valor'] < 0]['valor'].sum())
            saldo = receitas - despesas

            monthly_data.append([
                mes_ano,
                str(total),
                f'R$ {receitas:,.2f}',
                f'R$ {despesas:,.2f}',
                f'R$ {saldo:,.2f}'
            ])

        t = Table(monthly_data, colWidths=[3*cm, 3*cm, 4*cm, 4*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4527A0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)

        if include_details:
            story.append(PageBreak())
            story.append(Paragraph("Detalhamento por Mês", styles['Heading2']))
            story.append(Spacer(1, 0.5*cm))

            for mes_ano in sorted(df_copy['mes_ano'].dropna().unique()):
                month_df = df_copy[df_copy['mes_ano'] == mes_ano]
                story.append(Paragraph(f"<b>{mes_ano}</b>", styles['Heading3']))
                story.append(self._add_transaction_table(month_df.drop(['data_dt', 'mes_ano'], axis=1), styles, max_rows=100))
                story.append(Spacer(1, 0.5*cm))

        return story

    def _generate_by_bank_report(self, df, styles, title_style, include_details):
        """Generate bank comparison report"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        story = []
        story.append(Paragraph("🏦 Análise por Banco", title_style))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        if df.empty:
            story.append(Paragraph("Nenhum dado disponível.", styles['Normal']))
            return story

        # Group by bank
        bank_data = [['Banco', 'Contas', 'Transações', 'Receitas', 'Despesas', 'Saldo']]

        for banco in sorted(df['banco'].unique()):
            bank_df = df[df['banco'] == banco]
            contas = bank_df['conta'].nunique()
            total = len(bank_df)
            receitas = bank_df[bank_df['valor'] > 0]['valor'].sum()
            despesas = abs(bank_df[bank_df['valor'] < 0]['valor'].sum())
            saldo = receitas - despesas

            bank_data.append([
                banco[:30],
                str(contas),
                str(total),
                f'R$ {receitas:,.2f}',
                f'R$ {despesas:,.2f}',
                f'R$ {saldo:,.2f}'
            ])

        t = Table(bank_data, colWidths=[5*cm, 2*cm, 2.5*cm, 3*cm, 3*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4527A0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)

        if include_details:
            story.append(PageBreak())
            story.append(Paragraph("Detalhamento por Banco", styles['Heading2']))
            story.append(Spacer(1, 0.5*cm))

            for banco in sorted(df['banco'].unique()):
                bank_df = df[df['banco'] == banco]
                story.append(Paragraph(f"<b>{banco}</b>", styles['Heading3']))
                story.append(self._add_transaction_table(bank_df, styles, max_rows=100))
                story.append(Spacer(1, 0.5*cm))

        return story

    def _generate_by_category_report(self, df, styles, title_style, include_details):
        """Generate category analysis report"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        story = []
        story.append(Paragraph("📊 Análise por Categoria", title_style))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        if df.empty or 'categoria' not in df.columns:
            story.append(Paragraph("Nenhum dado de categorias disponível.", styles['Normal']))
            return story

        # Group by category
        cat_data = [['Categoria', 'Transações', 'Valor Total', '% do Total']]

        total_valor = abs(df[df['valor'] < 0]['valor'].sum())  # Only expenses

        for categoria in sorted(df['categoria'].unique()):
            cat_df = df[(df['categoria'] == categoria) & (df['valor'] < 0)]
            if not cat_df.empty:
                total = len(cat_df)
                valor = abs(cat_df['valor'].sum())
                percent = (valor / total_valor * 100) if total_valor > 0 else 0

                cat_data.append([
                    categoria,
                    str(total),
                    f'R$ {valor:,.2f}',
                    f'{percent:.1f}%'
                ])

        t = Table(cat_data, colWidths=[6*cm, 4*cm, 4*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4527A0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)

        if include_details:
            story.append(PageBreak())
            story.append(Paragraph("Detalhamento por Categoria", styles['Heading2']))
            story.append(Spacer(1, 0.5*cm))

            for categoria in sorted(df['categoria'].unique()):
                cat_df = df[df['categoria'] == categoria]
                if not cat_df.empty:
                    story.append(Paragraph(f"<b>{categoria}</b>", styles['Heading3']))
                    story.append(self._add_transaction_table(cat_df, styles, max_rows=100))
                    story.append(Spacer(1, 0.5*cm))

        return story

    def _generate_detailed_report(self, df, styles, title_style):
        """Generate detailed transaction list"""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm

        story = []
        story.append(Paragraph("🔍 Transações Detalhadas", title_style))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        if df.empty:
            story.append(Paragraph("Nenhum dado disponível.", styles['Normal']))
            return story

        story.append(Paragraph(f"<b>Total de transações: {len(df)}</b>", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        story.append(self._add_transaction_table(df, styles, max_rows=None))  # All transactions

        return story

    def _generate_gaps_report(self, df, styles, title_style):
        """Generate gaps and inconsistencies report"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        story = []
        story.append(Paragraph("⚠️ Gaps e Inconsistências", title_style))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        if df.empty:
            story.append(Paragraph("Nenhum dado disponível.", styles['Normal']))
            return story

        # Detect gaps per bank/account
        from core.analyzer import DataAnalyzer
        analyzer = DataAnalyzer(df)
        gaps = analyzer.detect_gaps()

        if gaps:
            story.append(Paragraph(f"<b>Foram detectados {len(gaps)} gaps:</b>", styles['Normal']))
            story.append(Spacer(1, 0.3*cm))

            gap_data = [['Banco', 'Conta', 'Período Faltante', 'Dias']]
            for gap in gaps:
                gap_data.append([
                    gap.get('banco', '')[:25],
                    gap.get('conta', ''),
                    f"{gap.get('gap_start', '')} - {gap.get('gap_end', '')}",
                    str(gap.get('days', 0))
                ])

            t = Table(gap_data, colWidths=[5*cm, 3*cm, 6*cm, 2*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D32F2F')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(t)
        else:
            story.append(Paragraph("✅ Nenhum gap detectado!", styles['Normal']))

        return story

    def _add_transaction_table(self, df, styles, max_rows=50):
        """Add transaction table to report"""
        from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        if df.empty:
            return Paragraph("Nenhuma transação.", styles['Normal'])

        # Limit rows if specified
        display_df = df.head(max_rows) if max_rows else df

        # Build table data
        table_data = [['Data', 'Descrição', 'Valor', 'Banco', 'Conta']]

        for _, row in display_df.iterrows():
            table_data.append([
                str(row.get('data', '')),
                str(row.get('descricao', ''))[:40],
                f"R$ {row.get('valor', 0):,.2f}",
                str(row.get('banco', ''))[:20],
                str(row.get('conta', ''))[:15]
            ])

        t = Table(table_data, colWidths=[2.5*cm, 8*cm, 3*cm, 5*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4527A0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        if max_rows and len(df) > max_rows:
            elements = [t, Spacer(1, 0.3*cm), Paragraph(f"<i>Mostrando {max_rows} de {len(df)} transações</i>", styles['Italic'])]
            from reportlab.platypus import KeepTogether
            return KeepTogether(elements)

        return t

    def _export_pdf_simple(self, file_path: str, include_details: bool = False) -> bool:
        """Simple PDF export fallback using fpdf"""
        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Relatório de Transações - OFX Consolidador Pro', ln=True, align='C')
            pdf.ln(5)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', ln=True)
            pdf.ln(5)

            # Transaction table
            if not self.df.empty:
                limit = None if include_details else 100
                display_df = self.df.head(limit) if limit else self.df

                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f'Transações ({len(display_df)} de {len(self.df)})', ln=True)

                pdf.set_font('Arial', 'B', 8)
                pdf.cell(25, 6, 'Data', border=1)
                pdf.cell(60, 6, 'Descrição', border=1)
                pdf.cell(30, 6, 'Valor', border=1)
                pdf.cell(40, 6, 'Banco', border=1)
                pdf.ln()

                pdf.set_font('Arial', '', 8)
                for idx, row in display_df.iterrows():
                    pdf.cell(25, 6, str(row.get('data', '')), border=1)
                    desc = str(row.get('descricao', ''))[:30]
                    pdf.cell(60, 6, desc, border=1)
                    valor = row.get('valor', 0)
                    pdf.cell(30, 6, f'R$ {valor:,.2f}', border=1)
                    banco = str(row.get('banco', ''))[:20]
                    pdf.cell(40, 6, banco, border=1)
                    pdf.ln()

            pdf.output(file_path)
            return True
        except Exception as e:
            print(f"Error in simple PDF export: {e}")
            return False
