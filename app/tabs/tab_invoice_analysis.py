"""
Invoice Analysis Tab - Analyze invoices vs OFX receipts
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QFileDialog,
                             QGroupBox, QComboBox, QHeaderView, QAbstractItemView,
                             QMessageBox, QTabWidget, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.invoice_matcher import InvoiceMatcher
from core.exporter import DataExporter
from core.name_matcher import NameMatcher


class InvoiceAnalysisTab(QWidget):
    """Tab for analyzing invoices vs OFX receipts"""

    def __init__(self):
        super().__init__()
        self.invoices_df = None
        self.ofx_df = None
        self.sales_df = None  # Credit card sales
        self.installments_df = None  # Credit card installments
        self.customer_summary_df = None
        self.monthly_summary_df = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)

        # Controls
        controls_frame = self._create_controls()
        main_layout.addWidget(controls_frame)

        # Tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                background: white;
            }
            QTabBar::tab {
                background: #F5F5F5;
                border: 1px solid #E0E0E0;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
        """)

        # Sintética tab
        self.sintetica_widget = self._create_sintetica_view()
        self.tab_widget.addTab(self.sintetica_widget, "📊 Visão Sintética (por Cliente)")

        # Detalhada tab
        self.detalhada_widget = self._create_detalhada_view()
        self.tab_widget.addTab(self.detalhada_widget, "📋 Visão Detalhada (por Mês)")

        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("Nenhuma análise disponível")
        self.status_label.setStyleSheet("padding: 5px; font-size: 10px; color: #666;")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def _create_header(self):
        """Create header section"""
        header_frame = QWidget()
        header_frame.setMaximumHeight(70)
        header_frame.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00897B, stop:1 #00695C);
                border-radius: 8px;
            }
        """)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("📊 Análise: Notas Fiscais vs Recebimentos")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")

        subtitle = QLabel("Comparação entre notas emitidas e valores recebidos via OFX")
        subtitle.setStyleSheet("color: #B2DFDB; font-size: 10px; background: transparent;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_frame.setLayout(header_layout)

        return header_frame

    def _create_controls(self):
        """Create controls section"""
        controls_frame = QWidget()
        controls_frame.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 5, 10, 5)

        # Refresh button
        self.btn_refresh = QPushButton("🔄 Atualizar Análise")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #00897B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
        """)
        self.btn_refresh.clicked.connect(self.refresh_analysis)
        controls_layout.addWidget(self.btn_refresh)

        controls_layout.addSpacing(20)

        # Export buttons
        self.btn_export_sintetica = QPushButton("📄 Exportar Sintética (CSV)")
        self.btn_export_sintetica.setStyleSheet("""
            QPushButton {
                background-color: #5C6BC0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3F51B5;
            }
        """)
        self.btn_export_sintetica.clicked.connect(self.export_sintetica)
        controls_layout.addWidget(self.btn_export_sintetica)

        self.btn_export_detalhada = QPushButton("📄 Exportar Detalhada (CSV)")
        self.btn_export_detalhada.setStyleSheet("""
            QPushButton {
                background-color: #5C6BC0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3F51B5;
            }
        """)
        self.btn_export_detalhada.clicked.connect(self.export_detalhada)
        controls_layout.addWidget(self.btn_export_detalhada)

        controls_layout.addStretch()

        controls_frame.setLayout(controls_layout)
        return controls_frame

    def _create_sintetica_view(self):
        """Create sintética view (by customer)"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Resumo por cliente (CPF/CNPJ) - Clique no '+' para expandir e ver notas e recebimentos")
        info_label.setStyleSheet("font-size: 10px; color: #666; padding: 5px;")
        layout.addWidget(info_label)

        # Tree widget (replaces table for expandable rows)
        self.sintetica_tree = QTreeWidget()
        self.sintetica_tree.setColumnCount(7)
        self.sintetica_tree.setHeaderLabels([
            'CPF/CNPJ', 'Nome', 'Qtd Notas', 'Total Emitido (R$)',
            'Total Recebido (R$)', 'Pendente (R$)', '% Markup'
        ])

        # Configure tree
        header = self.sintetica_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.sintetica_tree.setAlternatingRowColors(True)
        self.sintetica_tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sintetica_tree.setSortingEnabled(True)  # Enable column sorting
        self.sintetica_tree.setStyleSheet("""
            QTreeWidget {
                gridline-color: #E0E0E0;
                font-size: 10px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 4px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
                font-size: 10px;
            }
        """)

        layout.addWidget(self.sintetica_tree)

        widget.setLayout(layout)
        return widget

    def _create_detalhada_view(self):
        """Create detalhada view (by month)"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Resumo mensal - Notas emitidas vs recebimentos por mês")
        info_label.setStyleSheet("font-size: 10px; color: #666; padding: 5px;")
        layout.addWidget(info_label)

        # Table
        self.detalhada_table = QTableWidget()
        self.detalhada_table.setColumnCount(6)
        self.detalhada_table.setHorizontalHeaderLabels([
            'Mês', 'Qtd Notas', 'Total Emitido (R$)',
            'Total Recebido (R$)', 'Pendente (R$)', '% Markup'
        ])

        # Configure table
        header = self.detalhada_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.detalhada_table.setAlternatingRowColors(True)
        self.detalhada_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.detalhada_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                font-size: 10px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 4px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
                font-size: 10px;
            }
        """)

        layout.addWidget(self.detalhada_table)

        widget.setLayout(layout)
        return widget

    def set_data(self, invoices_df, ofx_df):
        """Set data for analysis"""
        import time
        start_time = time.time()
        print(f"[ANALYSIS] set_data iniciado - Invoices: {len(invoices_df) if invoices_df is not None else 0}, OFX: {len(ofx_df) if ofx_df is not None else 0} - {time.strftime('%H:%M:%S')}")

        self.invoices_df = invoices_df
        self.ofx_df = ofx_df
        self.refresh_analysis()

        print(f"[ANALYSIS] set_data concluído em {time.time() - start_time:.2f}s")

    def set_card_data(self, sales_df, installments_df):
        """Set credit card sales data for analysis"""
        import time
        start_time = time.time()
        print(f"[ANALYSIS] set_card_data iniciado - Sales: {len(sales_df) if sales_df is not None else 0}, Installments: {len(installments_df) if installments_df is not None else 0} - {time.strftime('%H:%M:%S')}")

        self.sales_df = sales_df
        self.installments_df = installments_df
        self.refresh_analysis()

        print(f"[ANALYSIS] set_card_data concluído em {time.time() - start_time:.2f}s")

    def refresh_analysis(self):
        """Refresh analysis"""
        import time
        start_time = time.time()
        print(f"[ANALYSIS] refresh_analysis iniciado - {time.strftime('%H:%M:%S')}")

        # Check if we have any data to analyze
        has_invoices = self.invoices_df is not None and not self.invoices_df.empty
        has_cards = self.installments_df is not None and not self.installments_df.empty

        if not has_invoices and not has_cards:
            QMessageBox.warning(
                self,
                "Análise",
                "Nenhum dado importado. Por favor, importe notas fiscais ou vendas de cartão primeiro."
            )
            return

        # Generate summaries
        matcher = InvoiceMatcher()

        # Customer summary
        customer_start = time.time()
        print(f"[ANALYSIS] Iniciando analyze_by_customer - {time.strftime('%H:%M:%S')}")
        self.customer_summary_df = matcher.analyze_by_customer(self.invoices_df, self.ofx_df)
        print(f"[ANALYSIS] analyze_by_customer concluído em {time.time() - customer_start:.2f}s")

        update_sint_start = time.time()
        print(f"[ANALYSIS] Iniciando update_sintetica_table - {time.strftime('%H:%M:%S')}")
        self.update_sintetica_table()
        print(f"[ANALYSIS] update_sintetica_table concluído em {time.time() - update_sint_start:.2f}s")

        # Monthly summary
        monthly_start = time.time()
        print(f"[ANALYSIS] Iniciando analyze_by_month - {time.strftime('%H:%M:%S')}")
        self.monthly_summary_df = matcher.analyze_by_month(self.invoices_df, self.ofx_df)
        print(f"[ANALYSIS] analyze_by_month concluído em {time.time() - monthly_start:.2f}s")

        update_det_start = time.time()
        print(f"[ANALYSIS] Iniciando update_detalhada_table - {time.strftime('%H:%M:%S')}")
        self.update_detalhada_table()
        print(f"[ANALYSIS] update_detalhada_table concluído em {time.time() - update_det_start:.2f}s")

        status_start = time.time()
        print(f"[ANALYSIS] Iniciando update_status - {time.strftime('%H:%M:%S')}")
        self.update_status()
        print(f"[ANALYSIS] update_status concluído em {time.time() - status_start:.2f}s")

        print(f"[ANALYSIS] refresh_analysis concluído - Tempo total: {time.time() - start_time:.2f}s")

    def update_sintetica_table(self):
        """Update sintética tree with expandable customer details"""
        import time
        start_time = time.time()
        print(f"[ANALYSIS-TREE] update_sintetica_table iniciado - {time.strftime('%H:%M:%S')}")

        df = self.customer_summary_df

        if df is None or df.empty:
            self.sintetica_tree.clear()
            return

        clear_start = time.time()
        self.sintetica_tree.clear()
        print(f"[ANALYSIS-TREE] Tree cleared em {time.time() - clear_start:.2f}s")

        # Font for parent items (bold)
        bold_font = QFont()
        bold_font.setBold(True)

        populate_start = time.time()
        for row_idx, (idx, row) in enumerate(df.iterrows()):
            # Create parent item (customer summary)
            parent_item = QTreeWidgetItem(self.sintetica_tree)
            parent_item.setFont(0, bold_font)

            # CPF/CNPJ
            parent_item.setText(0, row['cpf_cnpj_fmt'])

            # Nome
            parent_item.setText(1, row['nome'])

            # Qtd Notas
            parent_item.setText(2, str(row['qtd_notas']))
            parent_item.setTextAlignment(2, Qt.AlignCenter)

            # Total Emitido
            parent_item.setText(3, f"R$ {row['total_emitido']:,.2f}")
            parent_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)

            # Total Recebido
            parent_item.setText(4, f"R$ {row['total_recebido']:,.2f}")
            parent_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)

            # Pendente
            parent_item.setText(5, f"R$ {row['total_pendente']:,.2f}")
            parent_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)

            # Color code for pendente
            if row['total_pendente'] > 0:
                parent_item.setBackground(5, QColor(255, 200, 200))
            else:
                parent_item.setBackground(5, QColor(200, 255, 200))

            # % Markup
            parent_item.setText(6, f"{row['percent_markup']:.1f}%")
            parent_item.setTextAlignment(6, Qt.AlignRight | Qt.AlignVCenter)

            # Color code for markup
            if 5 <= row['percent_markup'] <= 15:
                parent_item.setBackground(6, QColor(200, 255, 200))  # Green - normal range
            elif row['percent_markup'] < 5 or row['percent_markup'] > 20:
                parent_item.setBackground(6, QColor(255, 200, 200))  # Red - unusual
            else:
                parent_item.setBackground(6, QColor(255, 255, 200))  # Yellow - acceptable

            # Add child items (invoices and OFX receipts)
            self._add_customer_details(parent_item, row['cpf_cnpj'])

        print(f"[ANALYSIS-TREE] Populated {len(df)} customers em {time.time() - populate_start:.2f}s")
        print(f"[ANALYSIS-TREE] update_sintetica_table concluído - Tempo total: {time.time() - start_time:.2f}s")

    def _add_customer_details(self, parent_item, cpf_cnpj):
        """Add child items showing invoices and OFX receipts for a customer"""
        # Get customer name for name matching
        customer_name = None

        # Try to get name from invoices first
        if self.invoices_df is not None and not self.invoices_df.empty:
            customer_invoices = self.invoices_df[self.invoices_df['cpf_cnpj'] == cpf_cnpj].copy()
            if not customer_invoices.empty:
                customer_name = customer_invoices.iloc[0].get('nome_tomador', '')
        else:
            customer_invoices = pd.DataFrame()

        # If no name yet, try from credit card installments
        if not customer_name and self.installments_df is not None and not self.installments_df.empty:
            customer_cards = self.installments_df[self.installments_df['cpf_cnpj'] == cpf_cnpj].copy()
            if not customer_cards.empty:
                customer_name = customer_cards.iloc[0].get('nome', '')

        # Sort by date (most recent first)
        if not customer_invoices.empty and 'data_dt' in customer_invoices.columns:
            customer_invoices = customer_invoices.sort_values('data_dt', ascending=False)

        if not customer_invoices.empty:
            # Add "Notas Fiscais" section header
            invoices_header = QTreeWidgetItem(parent_item)
            invoices_header.setText(0, f"📄 NOTAS FISCAIS ({len(customer_invoices)} notas)")
            invoices_header.setBackground(0, QColor(240, 248, 255))
            font = QFont()
            font.setBold(True)
            invoices_header.setFont(0, font)

            # DEBUG: Log invoice totals
            total_invoices = customer_invoices['valor_servicos'].sum()
            print(f"[DEBUG-CLIENTE] CPF={cpf_cnpj} | Notas: {len(customer_invoices)} | Total Notas: R$ {total_invoices:,.2f}")

            # Add each invoice as a child
            for idx, invoice in customer_invoices.iterrows():
                invoice_item = QTreeWidgetItem(invoices_header)
                invoice_item.setText(0, str(invoice.get('numero', 'N/A')))
                invoice_item.setText(1, invoice.get('nome_tomador', ''))
                invoice_item.setText(2, invoice.get('data_emissao', '')[:10] if pd.notna(invoice.get('data_emissao')) else '')
                invoice_item.setText(3, f"R$ {invoice.get('valor_servicos', 0):,.2f}")

                # Show match status
                status = invoice.get('status', 'Pendente')
                if status == 'Vinculado' or status == 'Pago':
                    invoice_item.setText(4, "✓ Vinculado")
                    invoice_item.setForeground(4, QColor(0, 128, 0))
                elif status == 'Parcial':
                    invoice_item.setText(4, "◐ Parcial")
                    invoice_item.setForeground(4, QColor(200, 150, 0))
                else:
                    invoice_item.setText(4, "⚠ Pendente")
                    invoice_item.setForeground(4, QColor(200, 100, 0))

        # Add credit card sales section
        if self.installments_df is not None and not self.installments_df.empty:
            # Get customer's credit card installments
            customer_installments = self.installments_df[
                self.installments_df['cpf_cnpj'] == cpf_cnpj
            ].copy()

            if not customer_installments.empty:
                # Add "Vendas no Cartão" section header
                cards_header = QTreeWidgetItem(parent_item)
                cards_header.setText(0, f"💳 VENDAS NO CARTÃO ({len(customer_installments)} parcelas)")
                cards_header.setBackground(0, QColor(255, 248, 240))
                font = QFont()
                font.setBold(True)
                cards_header.setFont(0, font)

                # DEBUG: Log card totals
                total_cards = customer_installments['valor'].sum()
                vinculadas = len(customer_installments[customer_installments['status_vinculacao'] == 'Vinculado'])
                print(f"[DEBUG-CLIENTE] CPF={cpf_cnpj} | Parcelas Cartão: {len(customer_installments)} | Total Cartão: R$ {total_cards:,.2f} | Vinculadas: {vinculadas}")

                # Add each installment as a child
                for idx, inst in customer_installments.iterrows():
                    inst_item = QTreeWidgetItem(cards_header)
                    inst_item.setText(0, f"{inst.get('nsu_doc', 'N/A')} - {inst.get('numero_parcela', 0)}/{inst.get('total_parcelas', 0)}")
                    inst_item.setText(1, inst.get('nome', ''))
                    inst_item.setText(2, str(inst.get('data_prevista', ''))[:10] if pd.notna(inst.get('data_prevista')) else '')
                    inst_item.setText(3, f"R$ {inst.get('valor', 0):,.2f}")

                    # Show match status
                    status = inst.get('status_vinculacao', 'Pendente')
                    if status == 'Vinculado':
                        inst_item.setText(4, "✓ Vinculado")
                        inst_item.setForeground(4, QColor(0, 128, 0))
                    else:
                        inst_item.setText(4, "⚠ Pendente")
                        inst_item.setForeground(4, QColor(200, 100, 0))

        # Get customer's OFX receipts (only credits/receipts, valor > 0)
        if self.ofx_df is not None and not self.ofx_df.empty:
            # DEBUG: Check ALL OFX for this customer (before filtering)
            all_customer_ofx = self.ofx_df[self.ofx_df['cpf_cnpj'] == cpf_cnpj].copy()
            print(f"[DEBUG-CLIENTE] CPF={cpf_cnpj} | Total OFX (TODAS): {len(all_customer_ofx)}")
            if not all_customer_ofx.empty:
                print(f"[DEBUG-CLIENTE]   Créditos: {len(all_customer_ofx[all_customer_ofx['valor'] > 0])}")
                print(f"[DEBUG-CLIENTE]   Débitos: {len(all_customer_ofx[all_customer_ofx['valor'] <= 0])}")
                total_creditos = all_customer_ofx[all_customer_ofx['valor'] > 0]['valor'].sum()
                total_debitos = all_customer_ofx[all_customer_ofx['valor'] <= 0]['valor'].sum()
                print(f"[DEBUG-CLIENTE]   Soma Créditos: R$ {total_creditos:,.2f}")
                print(f"[DEBUG-CLIENTE]   Soma Débitos: R$ {total_debitos:,.2f}")

                # List all OFX transactions for this customer
                print(f"[DEBUG-CLIENTE] Detalhes de TODAS as {len(all_customer_ofx)} transações OFX:")
                for idx, ofx in all_customer_ofx.iterrows():
                    valor = ofx.get('valor', 0)
                    data = ofx.get('data', 'N/A')
                    desc = ofx.get('descricao', '')[:40]
                    tipo = "CRÉDITO" if valor > 0 else "DÉBITO"
                    print(f"[DEBUG-CLIENTE]   {tipo} | {data} | R$ {valor:,.2f} | {desc}")

            # First, try matching by CPF/CNPJ
            customer_ofx = self.ofx_df[
                (self.ofx_df['cpf_cnpj'] == cpf_cnpj) &
                (self.ofx_df['valor'] > 0)
            ].copy()

            # If we have customer name, also try matching by name for OFX without CPF
            if customer_name:
                print(f"[NAME-MATCH] Tentando matching por nome: '{customer_name}' para CPF={cpf_cnpj}")

                # Get OFX transactions that don't have CPF or have empty CPF
                ofx_no_cpf = self.ofx_df[
                    ((self.ofx_df['cpf_cnpj'].isna()) | (self.ofx_df['cpf_cnpj'] == '')) &
                    (self.ofx_df['valor'] > 0)
                ].copy()

                # Try to match by name
                matched_by_name = []
                for idx, ofx in ofx_no_cpf.iterrows():
                    descricao = ofx.get('descricao', '') or ofx.get('memo', '')
                    is_match, num_matches, matched_words = NameMatcher.match_names(descricao, customer_name, min_matches=2)

                    if is_match:
                        print(f"[NAME-MATCH] ✓ Match encontrado: '{descricao}' | Palavras: {matched_words} ({num_matches} matches)")
                        matched_by_name.append(idx)

                # Add matched transactions to customer_ofx
                if matched_by_name:
                    ofx_by_name = ofx_no_cpf.loc[matched_by_name]
                    customer_ofx = pd.concat([customer_ofx, ofx_by_name], ignore_index=False)
                    print(f"[NAME-MATCH] {len(matched_by_name)} transação(ões) adicionada(s) por nome")

            # Remove duplicates (in case same transaction was matched by both CPF and name)
            if not customer_ofx.empty:
                customer_ofx = customer_ofx.drop_duplicates(subset=['id_transacao'] if 'id_transacao' in customer_ofx.columns else None)

            # Sort by date (most recent first)
            if not customer_ofx.empty and 'data_dt' in customer_ofx.columns:
                customer_ofx = customer_ofx.sort_values('data_dt', ascending=False)
            elif not customer_ofx.empty and 'data' in customer_ofx.columns:
                # If data_dt doesn't exist, create it
                customer_ofx['data_dt'] = pd.to_datetime(customer_ofx['data'], format='%d/%m/%Y', errors='coerce')
                customer_ofx = customer_ofx.sort_values('data_dt', ascending=False)

            if not customer_ofx.empty:
                # DEBUG: Log OFX totals
                total_ofx = customer_ofx['valor'].sum()
                print(f"[DEBUG-CLIENTE] CPF={cpf_cnpj} | OFX Mostrados: {len(customer_ofx)} | Total OFX: R$ {total_ofx:,.2f}")

                # Add "Recebimentos OFX" section header
                ofx_header = QTreeWidgetItem(parent_item)
                ofx_header.setText(0, f"💰 RECEBIMENTOS OFX ({len(customer_ofx)} transações)")
                ofx_header.setBackground(0, QColor(240, 255, 240))
                font = QFont()
                font.setBold(True)
                ofx_header.setFont(0, font)

                # Add each OFX transaction as a child
                for idx, ofx in customer_ofx.iterrows():
                    ofx_item = QTreeWidgetItem(ofx_header)
                    ofx_item.setText(0, str(ofx.get('id_transacao', 'N/A')))
                    ofx_item.setText(1, ofx.get('descricao', ''))
                    ofx_item.setText(2, ofx.get('data', '')[:10] if pd.notna(ofx.get('data')) else '')
                    ofx_item.setText(4, f"R$ {ofx.get('valor', 0):,.2f}")
                    ofx_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)

    def update_detalhada_table(self):
        """Update detalhada table"""
        df = self.monthly_summary_df

        if df is None or df.empty:
            self.detalhada_table.setRowCount(0)
            return

        self.detalhada_table.setRowCount(len(df))

        for row_idx, (idx, row) in enumerate(df.iterrows()):
            # Mês
            self.detalhada_table.setItem(row_idx, 0, QTableWidgetItem(row['mes']))

            # Qtd Notas
            qtd_item = QTableWidgetItem(str(row['qtd_notas']))
            qtd_item.setTextAlignment(Qt.AlignCenter)
            self.detalhada_table.setItem(row_idx, 1, qtd_item)

            # Total Emitido
            emitido_item = QTableWidgetItem(f"R$ {row['total_emitido']:,.2f}")
            emitido_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.detalhada_table.setItem(row_idx, 2, emitido_item)

            # Total Recebido
            recebido_item = QTableWidgetItem(f"R$ {row['total_recebido']:,.2f}")
            recebido_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.detalhada_table.setItem(row_idx, 3, recebido_item)

            # Pendente
            pendente_item = QTableWidgetItem(f"R$ {row['total_pendente']:,.2f}")
            pendente_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Color code
            if row['total_pendente'] > 0:
                pendente_item.setBackground(QColor(255, 200, 200))
            else:
                pendente_item.setBackground(QColor(200, 255, 200))

            self.detalhada_table.setItem(row_idx, 4, pendente_item)

            # % Markup
            percent_item = QTableWidgetItem(f"{row['percent_markup']:.1f}%")
            percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Color code (for markup: 5-15% is normal range for agency commission)
            if 5 <= row['percent_markup'] <= 15:
                percent_item.setBackground(QColor(200, 255, 200))  # Green - normal range
            elif row['percent_markup'] < 5 or row['percent_markup'] > 20:
                percent_item.setBackground(QColor(255, 200, 200))  # Red - unusual
            else:
                percent_item.setBackground(QColor(255, 255, 200))  # Yellow - acceptable

            self.detalhada_table.setItem(row_idx, 5, percent_item)

    def update_status(self):
        """Update status label"""
        if self.customer_summary_df is None or self.customer_summary_df.empty:
            self.status_label.setText("Nenhuma análise disponível")
            return

        total_customers = len(self.customer_summary_df)
        total_emitido = self.customer_summary_df['total_emitido'].sum()
        total_recebido = self.customer_summary_df['total_recebido'].sum()
        total_pendente = self.customer_summary_df['total_pendente'].sum()
        percent_global = (total_recebido / total_emitido * 100) if total_emitido > 0 else 0

        self.status_label.setText(
            f"Clientes: {total_customers} | "
            f"Total Emitido: R$ {total_emitido:,.2f} | "
            f"Total Recebido: R$ {total_recebido:,.2f} | "
            f"Pendente: R$ {total_pendente:,.2f} | "
            f"% Recebido: {percent_global:.1f}%"
        )

    def export_sintetica(self):
        """Export sintética view to CSV"""
        if self.customer_summary_df is None or self.customer_summary_df.empty:
            QMessageBox.warning(self, "Exportar", "Nenhuma análise disponível para exportar.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Análise Sintética",
            "analise_sintetica_notas.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Prepare export dataframe
                export_df = self.customer_summary_df[[
                    'cpf_cnpj_fmt', 'nome', 'qtd_notas',
                    'total_emitido', 'total_recebido', 'total_pendente', 'percent_markup'
                ]].copy()

                export_df.columns = [
                    'CPF/CNPJ', 'Nome', 'Qtd Notas',
                    'Total Emitido (R$)', 'Total Recebido (R$)', 'Pendente (R$)', '% Markup'
                ]

                export_df.to_csv(file_path, index=False, encoding='utf-8-sig')

                QMessageBox.information(
                    self,
                    "Exportação",
                    f"Análise sintética exportada com sucesso!\n\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro",
                    f"Erro ao exportar: {str(e)}"
                )

    def export_detalhada(self):
        """Export detalhada view to CSV"""
        if self.monthly_summary_df is None or self.monthly_summary_df.empty:
            QMessageBox.warning(self, "Exportar", "Nenhuma análise disponível para exportar.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Análise Detalhada",
            "analise_detalhada_notas.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Prepare export dataframe
                export_df = self.monthly_summary_df[[
                    'mes', 'qtd_notas',
                    'total_emitido', 'total_recebido', 'total_pendente', 'percent_markup'
                ]].copy()

                export_df.columns = [
                    'Mês', 'Qtd Notas',
                    'Total Emitido (R$)', 'Total Recebido (R$)', 'Pendente (R$)', '% Markup'
                ]

                export_df.to_csv(file_path, index=False, encoding='utf-8-sig')

                QMessageBox.information(
                    self,
                    "Exportação",
                    f"Análise detalhada exportada com sucesso!\n\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro",
                    f"Erro ao exportar: {str(e)}"
                )
