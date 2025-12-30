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
        self.groups_df = None  # Customer groups with markup
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

        # Group analysis tab
        self.group_widget = self._create_group_view()
        self.tab_widget.addTab(self.group_widget, "👥 Análise por Grupo")

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

        # Important: Disable automatic sorting for QTreeWidget with children
        # We'll sort the DataFrame before populating instead
        self.sintetica_tree.setSortingEnabled(False)

        # Make headers clickable for manual sorting
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self._sort_sintetica_table)

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

    def _sort_sintetica_table(self, column_index):
        """Sort sintética table by clicking column header"""
        if self.customer_summary_df is None or self.customer_summary_df.empty:
            return

        # Map column index to DataFrame column
        column_map = {
            0: 'cpf_cnpj_fmt',      # CPF/CNPJ
            1: 'nome',               # Nome
            2: 'qtd_notas',          # Qtd Notas
            3: 'total_emitido',      # Total Emitido
            4: 'total_recebido',     # Total Recebido
            5: 'total_pendente',     # Pendente
            6: 'percent_markup'      # % Markup
        }

        if column_index not in column_map:
            return

        df_column = column_map[column_index]

        # Toggle sort order if clicking same column
        if not hasattr(self, '_last_sort_column') or self._last_sort_column != column_index:
            self._sort_ascending = True
            self._last_sort_column = column_index
        else:
            self._sort_ascending = not self._sort_ascending

        # Sort DataFrame
        self.customer_summary_df = self.customer_summary_df.sort_values(
            by=df_column,
            ascending=self._sort_ascending
        )

        # Refresh table
        self.update_sintetica_table()

    def _create_detalhada_view(self):
        """Create detalhada view (by month/day with transactions)"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Visão Detalhada - Clique no '+' para expandir mês e ver recebimentos por dia (OFX + Cartão)")
        info_label.setStyleSheet("font-size: 10px; color: #666; padding: 5px;")
        layout.addWidget(info_label)

        # Tree widget (replaces table)
        self.detalhada_tree = QTreeWidget()
        self.detalhada_tree.setColumnCount(7)
        self.detalhada_tree.setHeaderLabels([
            'Data/Descrição', 'Tipo', 'CPF/CNPJ Cliente', 'Valor (R$)',
            'Nota Vinculada', 'Status', 'Observações'
        ])

        # Configure tree
        header = self.detalhada_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)

        self.detalhada_tree.setAlternatingRowColors(True)
        self.detalhada_tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.detalhada_tree.setSortingEnabled(False)  # Disable sorting to maintain chronological order
        self.detalhada_tree.setStyleSheet("""
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

        layout.addWidget(self.detalhada_tree)

        widget.setLayout(layout)
        return widget

    def _create_group_view(self):
        """Create group analysis view"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Info and controls
        info_layout = QHBoxLayout()

        info_label = QLabel("📊 Análise agregada por grupo de clientes com markup personalizado")
        info_label.setStyleSheet("font-size: 11px; color: #666; font-style: italic;")
        info_layout.addWidget(info_label)

        info_layout.addStretch()

        # Download template button
        self.btn_download_template = QPushButton("📥 Baixar Modelo CSV")
        self.btn_download_template.setStyleSheet("""
            QPushButton {
                background-color: #00897B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
        """)
        self.btn_download_template.clicked.connect(self.download_group_template)
        info_layout.addWidget(self.btn_download_template)

        # Import groups button
        self.btn_import_groups = QPushButton("📂 Importar Grupos (CSV)")
        self.btn_import_groups.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        self.btn_import_groups.clicked.connect(self.import_groups)
        info_layout.addWidget(self.btn_import_groups)

        layout.addLayout(info_layout)

        # Group summary tree (expandable to show clients)
        self.group_tree = QTreeWidget()
        self.group_tree.setColumnCount(7)
        self.group_tree.setHeaderLabels([
            "Grupo / Cliente", "Qtd Notas", "Total Emitido",
            "Total Recebido", "Total Pendente", "% Markup", "CPF"
        ])

        # Tree styling
        header = self.group_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Group/Client name
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.group_tree.setAlternatingRowColors(True)
        self.group_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #E0E0E0;
                background: white;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
            QTreeWidget::item:selected {
                background-color: #E3F2FD;
            }
        """)

        layout.addWidget(self.group_tree)

        # Status label
        self.group_status_label = QLabel("💡 Importe um arquivo CSV de grupos para começar")
        self.group_status_label.setStyleSheet("padding: 5px; font-size: 10px; color: #666; font-style: italic;")
        layout.addWidget(self.group_status_label)

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
            # Silently return if no data - no need to warn user
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

        # Detalhada view (now uses OFX and installments directly, no monthly summary needed)
        update_det_start = time.time()
        print(f"[ANALYSIS] Iniciando update_detalhada_table - {time.strftime('%H:%M:%S')}")
        self.update_detalhada_table()
        print(f"[ANALYSIS] update_detalhada_table concluído em {time.time() - update_det_start:.2f}s")

        status_start = time.time()
        print(f"[ANALYSIS] Iniciando update_status - {time.strftime('%H:%M:%S')}")
        self.update_status()
        print(f"[ANALYSIS] update_status concluído em {time.time() - status_start:.2f}s")

        # Update group analysis if groups are loaded
        if self.groups_df is not None and not self.groups_df.empty:
            group_start = time.time()
            print(f"[ANALYSIS] Iniciando update_group_analysis - {time.strftime('%H:%M:%S')}")
            self.update_group_analysis()
            print(f"[ANALYSIS] update_group_analysis concluído em {time.time() - group_start:.2f}s")

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
            parent_item.setData(2, Qt.UserRole, int(row['qtd_notas']))  # For numeric sorting
            parent_item.setTextAlignment(2, Qt.AlignCenter)

            # Total Emitido
            parent_item.setText(3, f"R$ {row['total_emitido']:,.2f}")
            parent_item.setData(3, Qt.UserRole, float(row['total_emitido']))  # For numeric sorting
            parent_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)

            # Total Recebido
            parent_item.setText(4, f"R$ {row['total_recebido']:,.2f}")
            parent_item.setData(4, Qt.UserRole, float(row['total_recebido']))  # For numeric sorting
            parent_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)

            # Pendente
            parent_item.setText(5, f"R$ {row['total_pendente']:,.2f}")
            parent_item.setData(5, Qt.UserRole, float(row['total_pendente']))  # For numeric sorting
            parent_item.setTextAlignment(5, Qt.AlignRight | Qt.AlignVCenter)

            # Color code for pendente
            if row['total_pendente'] > 0:
                parent_item.setBackground(5, QColor(255, 200, 200))
            else:
                parent_item.setBackground(5, QColor(200, 255, 200))

            # % Markup
            parent_item.setText(6, f"{row['percent_markup']:.1f}%")
            parent_item.setData(6, Qt.UserRole, float(row['percent_markup']))  # For numeric sorting
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
            # Get customer's credit card installments (match by CPF do cliente)
            customer_installments = self.installments_df[
                self.installments_df['cpf_cliente'] == cpf_cnpj
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
        """Update detalhada tree with month > day > transactions structure"""
        import time
        start_time = time.time()
        print(f"[DETALHADA-TREE] update_detalhada_table iniciado - {time.strftime('%H:%M:%S')}")

        self.detalhada_tree.clear()

        # Check if we have any data
        has_ofx = self.ofx_df is not None and not self.ofx_df.empty
        has_cards = self.installments_df is not None and not self.installments_df.empty

        if not has_ofx and not has_cards:
            return

        # Font for headers
        bold_font = QFont()
        bold_font.setBold(True)

        # Collect all transactions (OFX + Card installments)
        all_transactions = []

        # 1. Add OFX transactions (filtered)
        if has_ofx:
            ofx_filtered = self._filter_ofx_for_detalhada(self.ofx_df)
            for idx, ofx in ofx_filtered.iterrows():
                all_transactions.append({
                    'data_dt': ofx['data_dt'],
                    'data_str': ofx['data'],
                    'tipo': 'OFX',
                    'cpf_cnpj': ofx.get('cpf_cnpj', ''),
                    'cpf_cnpj_fmt': ofx.get('cpf_cnpj_formatted', ''),
                    'valor': ofx['valor'],
                    'descricao': ofx.get('descricao', ''),
                    'nota_vinculada': self._get_linked_invoice(ofx.get('cpf_cnpj', ''), ofx['data_dt'], ofx['valor']),
                    'status': 'Vinculado' if ofx.get('matched', False) else 'Não Vinculado',
                    'obs': ofx.get('historico', '')
                })

        # 2. Add credit card installments
        if has_cards:
            for idx, inst in self.installments_df.iterrows():
                # Use data_prevista (expected date) for installments
                data_prevista = inst['data_prevista']

                # Convert to datetime if it's a string, or use directly if it's already Timestamp
                if isinstance(data_prevista, str):
                    data_dt = pd.to_datetime(data_prevista, format='%d/%m/%Y', errors='coerce')
                    data_str = data_prevista
                else:
                    # It's already a Timestamp
                    data_dt = data_prevista
                    data_str = data_prevista.strftime('%d/%m/%Y') if pd.notna(data_prevista) else ''

                all_transactions.append({
                    'data_dt': data_dt,
                    'data_str': data_str,
                    'tipo': 'Cartão',
                    'cpf_cnpj': inst.get('cpf_cliente', ''),
                    'cpf_cnpj_fmt': inst.get('cpf_cliente', ''),  # Format if needed
                    'valor': inst['valor'],
                    'descricao': f"{inst.get('nome', '')} - Parcela {inst.get('numero_parcela', 0)}/{inst.get('total_parcelas', 0)} - {inst.get('bandeira', '')}",
                    'nota_vinculada': '',  # Cards don't link to invoices directly
                    'status': inst.get('status_vinculacao', 'Pendente'),
                    'obs': f"NSU: {inst.get('nsu_doc', '')}, Adquirente: {inst.get('adquirente', '')}"
                })

        # Sort all transactions by date (most recent first)
        all_transactions_df = pd.DataFrame(all_transactions)
        if all_transactions_df.empty:
            return

        all_transactions_df = all_transactions_df.sort_values('data_dt', ascending=False)

        # Group by month
        all_transactions_df['ano_mes'] = all_transactions_df['data_dt'].dt.to_period('M')
        months = all_transactions_df['ano_mes'].unique()

        # Create tree structure: Month > Day > Transactions
        for month in sorted(months, reverse=True):  # Most recent first
            month_data = all_transactions_df[all_transactions_df['ano_mes'] == month]
            month_total = month_data['valor'].sum()
            month_count = len(month_data)

            # Create month header
            month_str = month.strftime('%B/%Y').capitalize()
            # Translate month names to Portuguese
            month_str = month_str.replace('January', 'Janeiro').replace('February', 'Fevereiro').replace('March', 'Março')
            month_str = month_str.replace('April', 'Abril').replace('May', 'Maio').replace('June', 'Junho')
            month_str = month_str.replace('July', 'Julho').replace('August', 'Agosto').replace('September', 'Setembro')
            month_str = month_str.replace('October', 'Outubro').replace('November', 'Novembro').replace('December', 'Dezembro')

            month_item = QTreeWidgetItem(self.detalhada_tree)
            month_item.setText(0, f"📅 {month_str}")
            month_item.setText(3, f"R$ {month_total:,.2f}")
            month_item.setText(6, f"{month_count} recebimentos")
            month_item.setFont(0, bold_font)
            month_item.setBackground(0, QColor(240, 248, 255))

            # Group by day within month
            days = month_data['data_str'].unique()
            for day_str in sorted(days, reverse=True):  # Most recent first
                day_data = month_data[month_data['data_str'] == day_str]
                day_total = day_data['valor'].sum()
                day_count = len(day_data)

                # Create day header
                day_item = QTreeWidgetItem(month_item)
                day_item.setText(0, f"  📆 {day_str}")
                day_item.setText(3, f"R$ {day_total:,.2f}")
                day_item.setText(6, f"{day_count} recebimentos")
                day_item.setFont(0, bold_font)
                day_item.setBackground(0, QColor(250, 250, 250))

                # Add individual transactions
                for idx, trans in day_data.iterrows():
                    trans_item = QTreeWidgetItem(day_item)
                    trans_item.setText(0, f"    {trans['descricao']}")
                    trans_item.setText(1, trans['tipo'])
                    trans_item.setText(2, trans['cpf_cnpj_fmt'])
                    trans_item.setText(3, f"R$ {trans['valor']:,.2f}")
                    trans_item.setText(4, trans['nota_vinculada'])
                    trans_item.setText(5, trans['status'])
                    trans_item.setText(6, trans['obs'][:50] if trans['obs'] else '')  # Truncate long obs

                    # Color code by status
                    if trans['status'] == 'Vinculado':
                        trans_item.setForeground(5, QColor(0, 128, 0))
                    elif trans['status'] == 'Pendente':
                        trans_item.setForeground(5, QColor(200, 100, 0))

                    # Align value to right
                    trans_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)

        print(f"[DETALHADA-TREE] update_detalhada_table concluído em {time.time() - start_time:.2f}s")

    def _filter_ofx_for_detalhada(self, ofx_df):
        """Filter OFX transactions for detalhada view: only credits, no transfers, no card operators"""
        if ofx_df is None or ofx_df.empty:
            return pd.DataFrame()

        # Only credits (valor > 0)
        filtered = ofx_df[ofx_df['valor'] > 0].copy()

        # Filter out card operators (Cielo, Rede, Stone, PagSeguro, etc.)
        card_operators = ['CIELO', 'REDE', 'STONE', 'PAGSEGURO', 'GETNET', 'MERCADO PAGO',
                         'SAFRAPAY', 'BIN', 'ELAVON', 'ADYEN', 'SUMUP']

        if 'descricao' in filtered.columns:
            for operator in card_operators:
                filtered = filtered[~filtered['descricao'].str.contains(operator, case=False, na=False)]

        if 'historico' in filtered.columns:
            for operator in card_operators:
                filtered = filtered[~filtered['historico'].str.contains(operator, case=False, na=False)]

        # Filter out transfers (typical patterns)
        transfer_patterns = ['TRANSF', 'TED', 'DOC', 'PIX ENVIADO', 'APLICACAO', 'RESGATE']

        if 'descricao' in filtered.columns:
            for pattern in transfer_patterns:
                filtered = filtered[~filtered['descricao'].str.contains(pattern, case=False, na=False)]

        if 'historico' in filtered.columns:
            for pattern in transfer_patterns:
                filtered = filtered[~filtered['historico'].str.contains(pattern, case=False, na=False)]

        return filtered

    def _get_linked_invoice(self, cpf_cnpj, data_dt, valor):
        """Get linked invoice number if exists"""
        if self.invoices_df is None or self.invoices_df.empty or not cpf_cnpj:
            return ''

        # Look for invoice with same CPF and nearby date
        customer_invoices = self.invoices_df[self.invoices_df['cpf_cnpj'] == cpf_cnpj]
        if customer_invoices.empty:
            return ''

        # Find invoice within ±3 days
        for idx, inv in customer_invoices.iterrows():
            if 'data_dt' in inv and pd.notna(inv['data_dt']):
                days_diff = abs((inv['data_dt'] - data_dt).days)
                if days_diff <= 3:
                    return str(inv.get('numero', ''))

        return ''

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
                # File saved silently - no confirmation dialog needed
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro",
                    f"Erro ao exportar: {str(e)}"
                )

    def export_detalhada(self):
        """Export detalhada view to CSV - exports all daily transactions"""
        # Check if we have data
        has_ofx = self.ofx_df is not None and not self.ofx_df.empty
        has_cards = self.installments_df is not None and not self.installments_df.empty

        if not has_ofx and not has_cards:
            QMessageBox.warning(self, "Exportar", "Nenhuma transação disponível para exportar.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Análise Detalhada",
            "analise_detalhada_transacoes.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Collect all transactions (same logic as update_detalhada_table)
                all_transactions = []

                # Add OFX transactions (filtered)
                if has_ofx:
                    ofx_filtered = self._filter_ofx_for_detalhada(self.ofx_df)
                    for idx, ofx in ofx_filtered.iterrows():
                        all_transactions.append({
                            'Data': ofx['data'],
                            'Tipo': 'OFX',
                            'CPF/CNPJ Cliente': ofx.get('cpf_cnpj_formatted', ''),
                            'Valor (R$)': ofx['valor'],
                            'Descrição': ofx.get('descricao', ''),
                            'Nota Vinculada': self._get_linked_invoice(ofx.get('cpf_cnpj', ''), ofx['data_dt'], ofx['valor']),
                            'Status': 'Vinculado' if ofx.get('matched', False) else 'Não Vinculado',
                            'Observações': ofx.get('historico', '')
                        })

                # Add credit card installments
                if has_cards:
                    for idx, inst in self.installments_df.iterrows():
                        all_transactions.append({
                            'Data': inst['data_prevista'],
                            'Tipo': 'Cartão',
                            'CPF/CNPJ Cliente': inst.get('cpf_cliente', ''),
                            'Valor (R$)': inst['valor'],
                            'Descrição': f"{inst.get('nome', '')} - Parcela {inst.get('numero_parcela', 0)}/{inst.get('total_parcelas', 0)} - {inst.get('bandeira', '')}",
                            'Nota Vinculada': '',
                            'Status': inst.get('status_vinculacao', 'Pendente'),
                            'Observações': f"NSU: {inst.get('nsu_doc', '')}, Adquirente: {inst.get('adquirente', '')}"
                        })

                # Create DataFrame and export
                export_df = pd.DataFrame(all_transactions)
                if not export_df.empty:
                    export_df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    # File saved silently - no confirmation dialog needed
                # Silently skip if empty - no warning needed

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro",
                    f"Erro ao exportar: {str(e)}"
                )

    def download_group_template(self):
        """Download CSV template for groups"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Modelo CSV de Grupos",
            "modelo_grupos.csv",
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Create template DataFrame
                template_df = pd.DataFrame({
                    'nome': ['João Silva', 'Maria Santos', 'Pedro Costa'],
                    'cpf': ['12345678900', '98765432100', '45678912300'],
                    'grupo': ['Equipe A', 'Equipe A', 'Equipe B'],
                    'markup_percent': [15.0, 15.0, 20.0]
                })

                template_df.to_csv(file_path, index=False, encoding='utf-8-sig')

                QMessageBox.information(
                    self,
                    "Modelo Salvo",
                    f"Modelo CSV salvo com sucesso!\n\n"
                    f"Arquivo: {file_path}\n\n"
                    f"Colunas obrigatórias:\n"
                    f"• nome: Nome do cliente\n"
                    f"• cpf: CPF do cliente (11 dígitos)\n"
                    f"• grupo: Nome do grupo\n"
                    f"• markup_percent: % de markup do grupo (ex: 15.0)"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar modelo: {str(e)}")

    def import_groups(self):
        """Import groups from CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Grupos CSV",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )

        if file_path:
            try:
                # Read CSV
                groups_df = pd.read_csv(file_path, encoding='utf-8-sig')

                # Validate required columns
                required_cols = ['nome', 'cpf', 'grupo', 'markup_percent']
                missing_cols = [col for col in required_cols if col not in groups_df.columns]

                if missing_cols:
                    QMessageBox.warning(
                        self,
                        "Colunas Faltando",
                        f"O arquivo CSV deve conter as colunas:\n{', '.join(required_cols)}\n\n"
                        f"Colunas faltando: {', '.join(missing_cols)}"
                    )
                    return

                # Clean CPF (remove formatting)
                groups_df['cpf'] = groups_df['cpf'].astype(str).str.replace(r'[^\d]', '', regex=True)

                # Validate data
                if groups_df.empty:
                    QMessageBox.warning(self, "Aviso", "O arquivo CSV está vazio!")
                    return

                # Store groups
                self.groups_df = groups_df

                # Update analysis
                self.update_group_analysis()

                self.group_status_label.setText(
                    f"✓ {len(groups_df)} cliente(s) em {groups_df['grupo'].nunique()} grupo(s) importado(s)"
                )
                self.group_status_label.setStyleSheet("padding: 5px; font-size: 10px; color: #00897B; font-weight: bold;")

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar grupos: {str(e)}")

    def update_group_analysis(self):
        """Update group analysis tree (expandable to show clients)"""
        self.group_tree.clear()

        if self.groups_df is None or self.groups_df.empty:
            return

        if self.customer_summary_df is None or self.customer_summary_df.empty:
            QMessageBox.warning(
                self,
                "Sem Dados",
                "Execute a análise sintética primeiro para visualizar análise por grupo."
            )
            return

        try:
            # Merge customer summary with groups
            # Match by CPF
            merged_df = self.customer_summary_df.copy()
            merged_df['cpf_clean'] = merged_df['cpf_cnpj'].str.replace(r'[^\d]', '', regex=True)

            # Join with groups
            groups_lookup = self.groups_df.set_index('cpf')[['grupo', 'markup_percent']].to_dict('index')

            merged_df['grupo'] = merged_df['cpf_clean'].map(
                lambda cpf: groups_lookup.get(cpf, {}).get('grupo', 'Sem Grupo')
            )
            merged_df['markup_grupo'] = merged_df['cpf_clean'].map(
                lambda cpf: groups_lookup.get(cpf, {}).get('markup_percent', 0.0)
            )

            # Font for bold headers
            bold_font = QFont()
            bold_font.setBold(True)
            bold_font.setPointSize(10)

            # Group by grupo and iterate
            for grupo_name, group_data in merged_df.groupby('grupo'):
                # Calculate group totals
                qtd_clientes = len(group_data)
                qtd_notas = int(group_data['qtd_notas'].sum())
                total_emitido = group_data['total_emitido'].sum()
                total_recebido = group_data['total_recebido'].sum()
                total_pendente = group_data['total_pendente'].sum()
                markup_percent = group_data['markup_grupo'].iloc[0] if len(group_data) > 0 else 0.0

                # Create parent item (group summary)
                parent_item = QTreeWidgetItem(self.group_tree)
                parent_item.setFont(0, bold_font)

                # Group name with client count
                parent_item.setText(0, f"📁 {grupo_name} ({qtd_clientes} cliente(s))")
                parent_item.setText(1, str(qtd_notas))
                parent_item.setText(2, f"R$ {total_emitido:,.2f}")
                parent_item.setText(3, f"R$ {total_recebido:,.2f}")
                parent_item.setText(4, f"R$ {total_pendente:,.2f}")
                parent_item.setText(5, f"{markup_percent:.1f}%")
                parent_item.setText(6, "")  # No CPF for group

                # Style parent
                parent_item.setTextAlignment(1, Qt.AlignRight)
                parent_item.setTextAlignment(2, Qt.AlignRight)
                parent_item.setTextAlignment(3, Qt.AlignRight)
                parent_item.setTextAlignment(4, Qt.AlignRight)
                parent_item.setTextAlignment(5, Qt.AlignCenter)

                parent_item.setBackground(2, QColor(240, 240, 240))  # Light gray for totals
                parent_item.setBackground(3, QColor(200, 255, 200))  # Light green for received
                if total_pendente > 0:
                    parent_item.setBackground(4, QColor(255, 200, 200))  # Light red for pending
                parent_item.setBackground(5, QColor(220, 220, 255))  # Light blue for markup

                # Add each client as a child
                for idx, client in group_data.iterrows():
                    client_item = QTreeWidgetItem(parent_item)

                    # Client name
                    client_item.setText(0, f"  👤 {client['nome']}")
                    client_item.setText(1, str(int(client['qtd_notas'])))
                    client_item.setText(2, f"R$ {client['total_emitido']:,.2f}")
                    client_item.setText(3, f"R$ {client['total_recebido']:,.2f}")
                    client_item.setText(4, f"R$ {client['total_pendente']:,.2f}")
                    client_item.setText(5, f"{client['markup_grupo']:.1f}%")
                    client_item.setText(6, client['cpf_cnpj_fmt'])

                    # Alignment
                    client_item.setTextAlignment(1, Qt.AlignRight)
                    client_item.setTextAlignment(2, Qt.AlignRight)
                    client_item.setTextAlignment(3, Qt.AlignRight)
                    client_item.setTextAlignment(4, Qt.AlignRight)
                    client_item.setTextAlignment(5, Qt.AlignCenter)

                    # Highlight received/pending
                    client_item.setBackground(3, QColor(230, 255, 230))  # Light green
                    if client['total_pendente'] > 0:
                        client_item.setBackground(4, QColor(255, 230, 230))  # Light red

            # Expand all groups by default
            self.group_tree.expandAll()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar análise por grupo: {str(e)}")
