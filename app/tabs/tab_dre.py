"""
DRE Tab - Demonstração do Resultado do Exercício (Income Statement)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QComboBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QDateEdit, QCheckBox,
                             QMessageBox, QFileDialog, QGroupBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.config import config


class DRETab(QWidget):
    """DRE (Income Statement) tab"""

    def __init__(self):
        super().__init__()
        self.df = None
        self.dre_data = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setMaximumHeight(60)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1565C0, stop:1 #0D47A1);
                border-radius: 8px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("📊 DRE - Demonstração do Resultado do Exercício")
        title.setStyleSheet("color: white; font-size: 14px; font-weight: bold; background: transparent;")
        header_layout.addWidget(title)

        self.period_label = QLabel("Selecione um período")
        self.period_label.setStyleSheet("color: #BBDEFB; font-size: 10px; background: transparent;")
        header_layout.addWidget(self.period_label)
        header_layout.addStretch()

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Period selection
        period_group = QGroupBox("📅 Período de Análise")
        period_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #BBDEFB;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        period_layout = QHBoxLayout()
        period_layout.setSpacing(10)

        # Preset selector
        period_layout.addWidget(QLabel("Período:"))
        self.cb_period = QComboBox()
        self.cb_period.addItems([
            'Último Mês',
            'Últimos 3 Meses',
            'Últimos 6 Meses',
            'Último Ano',
            'Ano Atual',
            'Personalizado'
        ])
        self.cb_period.setStyleSheet("font-size: 10px; padding: 5px;")
        self.cb_period.currentIndexChanged.connect(self.on_period_changed)
        period_layout.addWidget(self.cb_period)

        # Custom date range
        period_layout.addWidget(QLabel("De:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setEnabled(False)
        self.date_from.setStyleSheet("font-size: 10px; padding: 4px;")
        period_layout.addWidget(self.date_from)

        period_layout.addWidget(QLabel("Até:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setEnabled(False)
        self.date_to.setStyleSheet("font-size: 10px; padding: 4px;")
        period_layout.addWidget(self.date_to)

        # Calculate button
        btn_calculate = QPushButton("🔄 Calcular DRE")
        btn_calculate.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        btn_calculate.clicked.connect(self.calculate_dre)
        period_layout.addWidget(btn_calculate)

        period_layout.addStretch()
        period_group.setLayout(period_layout)
        main_layout.addWidget(period_group)

        # DRE Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Descrição', 'Valor (R$)'])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #BBDEFB;
                border-radius: 4px;
                font-size: 10px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #E3F2FD;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #1976D2;
                font-weight: bold;
                font-size: 10px;
            }
        """)
        main_layout.addWidget(self.table)

        # Export button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_export = QPushButton("📄 Exportar DRE (PDF)")
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        btn_export.clicked.connect(self.export_dre)
        btn_layout.addWidget(btn_export)

        main_layout.addLayout(btn_layout)

        # Info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(10, 8, 10, 8)

        info_label = QLabel(
            "ℹ️ <b>Sobre a DRE:</b> A Demonstração do Resultado do Exercício mostra o "
            "desempenho financeiro do período, calculando receitas, custos, despesas e lucro líquido."
        )
        info_label.setStyleSheet("font-size: 9px; color: #0D47A1; background: transparent;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        info_frame.setLayout(info_layout)
        main_layout.addWidget(info_frame)

        self.setLayout(main_layout)

        # Initialize empty table
        self.populate_empty_table()

    def on_period_changed(self):
        """Handle period selection change"""
        period = self.cb_period.currentText()

        if period == 'Personalizado':
            self.date_from.setEnabled(True)
            self.date_to.setEnabled(True)
        else:
            self.date_from.setEnabled(False)
            self.date_to.setEnabled(False)

            # Set dates based on preset
            today = QDate.currentDate()
            if period == 'Último Mês':
                self.date_from.setDate(today.addMonths(-1))
                self.date_to.setDate(today)
            elif period == 'Últimos 3 Meses':
                self.date_from.setDate(today.addMonths(-3))
                self.date_to.setDate(today)
            elif period == 'Últimos 6 Meses':
                self.date_from.setDate(today.addMonths(-6))
                self.date_to.setDate(today)
            elif period == 'Último Ano':
                self.date_from.setDate(today.addYears(-1))
                self.date_to.setDate(today)
            elif period == 'Ano Atual':
                self.date_from.setDate(QDate(today.year(), 1, 1))
                self.date_to.setDate(today)

    def update_data(self, df):
        """Update with transaction data"""
        self.df = df
        if self.df is not None and not self.df.empty:
            self.period_label.setText(f"{len(df)} transações carregadas")
            # Auto-calculate on data update
            self.calculate_dre()

    def calculate_dre(self):
        """Calculate DRE values"""
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "Aviso", "Nenhum dado disponível para cálculo!")
            return

        # Filter by date range
        start_date = self.date_from.date().toString('dd/MM/yyyy')
        end_date = self.date_to.date().toString('dd/MM/yyyy')

        try:
            df_filtered = self.filter_by_date(self.df, start_date, end_date)

            if df_filtered.empty:
                QMessageBox.warning(self, "Aviso", "Nenhuma transação no período selecionado!")
                return

            # Calculate DRE components
            self.dre_data = self.compute_dre(df_filtered)

            # Update period label
            self.period_label.setText(f"Período: {start_date} a {end_date} ({len(df_filtered)} transações)")

            # Populate table
            self.populate_dre_table()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao calcular DRE:\n{str(e)}")

    def filter_by_date(self, df, start_date, end_date):
        """Filter dataframe by date range"""
        df_copy = df.copy()
        df_copy['data_dt'] = pd.to_datetime(df_copy['data'], format='%d/%m/%Y', errors='coerce')
        start_dt = pd.to_datetime(start_date, format='%d/%m/%Y')
        end_dt = pd.to_datetime(end_date, format='%d/%m/%Y')
        mask = (df_copy['data_dt'] >= start_dt) & (df_copy['data_dt'] <= end_dt)
        return df_copy[mask]

    def compute_dre(self, df):
        """Compute DRE values from transaction data"""
        dre = {}

        # Separate income and expenses
        receitas = df[df['valor'] > 0]
        despesas = df[df['valor'] < 0]

        # 1. Receita Bruta
        if 'categoria' in df.columns:
            receita_vendas = receitas[receitas['categoria'].str.contains('Receita', case=False, na=False)]['valor'].sum()
        else:
            receita_vendas = receitas['valor'].sum()

        dre['receita_bruta'] = receita_vendas

        # 2. Deduções (impostos sobre vendas)
        if 'categoria' in df.columns:
            deducoes = despesas[despesas['categoria'].str.contains('Imposto|Taxa', case=False, na=False)]['valor'].sum()
        else:
            deducoes = 0

        dre['deducoes'] = abs(deducoes)

        # 3. Receita Líquida
        dre['receita_liquida'] = dre['receita_bruta'] - dre['deducoes']

        # 4. CMV/CPV (Custo de Mercadorias/Produtos Vendidos)
        if 'categoria' in df.columns:
            cmv = despesas[despesas['categoria'].str.contains('CMV|Custo|Produção', case=False, na=False)]['valor'].sum()
        else:
            cmv = 0

        dre['cmv'] = abs(cmv)

        # 5. Lucro Bruto
        dre['lucro_bruto'] = dre['receita_liquida'] - dre['cmv']

        # 6. Despesas Operacionais
        if 'categoria' in df.columns:
            desp_op = despesas[despesas['categoria'].str.contains(
                'Despesa|Pessoal|Aluguel|Marketing|Tecnologia|Utilidades|Escritório|Honorários|Viagem|Manutenção',
                case=False, na=False
            )]['valor'].sum()
        else:
            desp_op = despesas['valor'].sum()

        dre['despesas_operacionais'] = abs(desp_op)

        # 7. Lucro Operacional
        dre['lucro_operacional'] = dre['lucro_bruto'] - dre['despesas_operacionais']

        # 8. Resultado Financeiro
        if 'categoria' in df.columns:
            receitas_fin = receitas[receitas['categoria'].str.contains('Financeira|Juros recebido|Rendimento', case=False, na=False)]['valor'].sum()
            despesas_fin = despesas[despesas['categoria'].str.contains('Financeira|Juros pagos|Bancária', case=False, na=False)]['valor'].sum()
        else:
            receitas_fin = 0
            despesas_fin = 0

        dre['resultado_financeiro'] = receitas_fin - abs(despesas_fin)

        # 9. Lucro antes do IR
        dre['lucro_antes_ir'] = dre['lucro_operacional'] + dre['resultado_financeiro']

        # 10. IR/CSLL
        if 'categoria' in df.columns:
            ir_csll = despesas[despesas['categoria'].str.contains('IRPJ|CSLL|Imposto', case=False, na=False)]['valor'].sum()
        else:
            ir_csll = 0

        dre['ir_csll'] = abs(ir_csll)

        # 11. Lucro Líquido
        dre['lucro_liquido'] = dre['lucro_antes_ir'] - dre['ir_csll']

        return dre

    def populate_empty_table(self):
        """Populate table with empty DRE structure"""
        self.table.setRowCount(0)

        rows = [
            ("RECEITA BRUTA", 0, True, '#4CAF50'),
            ("(-) Deduções e Impostos sobre Vendas", 0, False, None),
            ("(=) RECEITA LÍQUIDA", 0, True, '#66BB6A'),
            ("(-) Custo das Mercadorias Vendidas (CMV)", 0, False, None),
            ("(=) LUCRO BRUTO", 0, True, '#81C784'),
            ("(-) Despesas Operacionais", 0, False, None),
            ("(=) LUCRO OPERACIONAL", 0, True, '#FFA726'),
            ("(+/-) Resultado Financeiro", 0, False, None),
            ("(=) LUCRO ANTES DO IR", 0, True, '#FFB74D'),
            ("(-) IR e CSLL", 0, False, None),
            ("(=) LUCRO LÍQUIDO DO EXERCÍCIO", 0, True, '#1976D2'),
        ]

        for row_data in rows:
            self.add_dre_row(*row_data)

    def populate_dre_table(self):
        """Populate table with calculated DRE values"""
        self.table.setRowCount(0)

        d = self.dre_data

        rows = [
            ("RECEITA BRUTA", d.get('receita_bruta', 0), True, '#4CAF50'),
            ("(-) Deduções e Impostos sobre Vendas", d.get('deducoes', 0), False, None),
            ("(=) RECEITA LÍQUIDA", d.get('receita_liquida', 0), True, '#66BB6A'),
            ("(-) Custo das Mercadorias Vendidas (CMV)", d.get('cmv', 0), False, None),
            ("(=) LUCRO BRUTO", d.get('lucro_bruto', 0), True, '#81C784'),
            ("(-) Despesas Operacionais", d.get('despesas_operacionais', 0), False, None),
            ("(=) LUCRO OPERACIONAL", d.get('lucro_operacional', 0), True, '#FFA726'),
            ("(+/-) Resultado Financeiro", d.get('resultado_financeiro', 0), False, None),
            ("(=) LUCRO ANTES DO IR", d.get('lucro_antes_ir', 0), True, '#FFB74D'),
            ("(-) IR e CSLL", d.get('ir_csll', 0), False, None),
            ("(=) LUCRO LÍQUIDO DO EXERCÍCIO", d.get('lucro_liquido', 0), True, '#1976D2'),
        ]

        for row_data in rows:
            self.add_dre_row(*row_data)

    def add_dre_row(self, description, value, is_total, bg_color):
        """Add a row to the DRE table"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Description
        desc_item = QTableWidgetItem(description)
        if is_total:
            font = QFont()
            font.setBold(True)
            desc_item.setFont(font)
        if bg_color:
            desc_item.setBackground(QColor(bg_color))
            desc_item.setForeground(QColor('white'))
        self.table.setItem(row, 0, desc_item)

        # Value
        value_item = QTableWidgetItem(f"R$ {value:,.2f}")
        value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if is_total:
            font = QFont()
            font.setBold(True)
            value_item.setFont(font)
        if bg_color:
            value_item.setBackground(QColor(bg_color))
            value_item.setForeground(QColor('white'))
        elif value < 0:
            value_item.setForeground(QColor('#D32F2F'))
        self.table.setItem(row, 1, value_item)

    def export_dre(self):
        """Export DRE to PDF"""
        if not self.dre_data:
            QMessageBox.warning(self, "Aviso", "Calcule a DRE antes de exportar!")
            return

        # Get save location
        last_dir = config.get('last_export_directory', os.path.expanduser('~'))

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar DRE",
            last_dir,
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        # Save directory
        config.set('last_export_directory', os.path.dirname(file_path))

        # Generate PDF
        try:
            self.generate_dre_pdf(file_path)

            QMessageBox.information(
                self,
                "Sucesso",
                f"DRE exportada com sucesso!\n\nSalvo em:\n{file_path}"
            )

            # Open file
            import subprocess
            import platform

            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            elif platform.system() == 'Windows':
                os.startfile(file_path)
            else:  # Linux
                subprocess.call(['xdg-open', file_path])

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar DRE:\n{str(e)}")

    def generate_dre_pdf(self, file_path):
        """Generate DRE PDF report"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib.enums import TA_CENTER

            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#0D47A1'),
                spaceAfter=20,
                alignment=TA_CENTER
            )
            story.append(Paragraph("DRE - Demonstração do Resultado do Exercício", title_style))

            # Period and date
            period = f"Período: {self.date_from.date().toString('dd/MM/yyyy')} a {self.date_to.date().toString('dd/MM/yyyy')}"
            story.append(Paragraph(period, styles['Normal']))
            story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 1*cm))

            # DRE Table
            d = self.dre_data

            table_data = [
                ['Descrição', 'Valor (R$)'],
                ['RECEITA BRUTA', f"R$ {d.get('receita_bruta', 0):,.2f}"],
                ['(-) Deduções e Impostos', f"R$ {d.get('deducoes', 0):,.2f}"],
                ['(=) RECEITA LÍQUIDA', f"R$ {d.get('receita_liquida', 0):,.2f}"],
                ['(-) CMV', f"R$ {d.get('cmv', 0):,.2f}"],
                ['(=) LUCRO BRUTO', f"R$ {d.get('lucro_bruto', 0):,.2f}"],
                ['(-) Despesas Operacionais', f"R$ {d.get('despesas_operacionais', 0):,.2f}"],
                ['(=) LUCRO OPERACIONAL', f"R$ {d.get('lucro_operacional', 0):,.2f}"],
                ['(+/-) Resultado Financeiro', f"R$ {d.get('resultado_financeiro', 0):,.2f}"],
                ['(=) LUCRO ANTES DO IR', f"R$ {d.get('lucro_antes_ir', 0):,.2f}"],
                ['(-) IR e CSLL', f"R$ {d.get('ir_csll', 0):,.2f}"],
                ['(=) LUCRO LÍQUIDO', f"R$ {d.get('lucro_liquido', 0):,.2f}"],
            ]

            t = Table(table_data, colWidths=[12*cm, 5*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                # Highlight total rows
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),  # Receita Bruta
                ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),  # Receita Líquida
                ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),  # Lucro Bruto
                ('FONTNAME', (0, 7), (-1, 7), 'Helvetica-Bold'),  # Lucro Operacional
                ('FONTNAME', (0, 9), (-1, 9), 'Helvetica-Bold'),  # Lucro antes IR
                ('FONTNAME', (0, 11), (-1, 11), 'Helvetica-Bold'), # Lucro Líquido

                ('BACKGROUND', (0, 11), (-1, 11), colors.HexColor('#E3F2FD')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))

            story.append(t)

            # Build PDF
            doc.build(story)

        except ImportError:
            raise Exception("reportlab não está instalado. Execute: pip install reportlab")
