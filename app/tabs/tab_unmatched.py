"""
Unmatched Items Tab - Show invoices and OFX transactions without matches
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QGroupBox,
                             QHeaderView, QAbstractItemView, QSplitter, QMessageBox,
                             QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
import pandas as pd


class UnmatchedTab(QWidget):
    """Tab for showing and managing unmatched invoices and OFX transactions"""

    manual_match_created = pyqtSignal(str, str)  # invoice_id, ofx_id

    def __init__(self):
        super().__init__()
        self.invoices_df = None
        self.ofx_df = None
        self.installments_df = None  # Credit card installments
        self.unmatched_invoices = pd.DataFrame()
        self.unmatched_ofx = pd.DataFrame()
        self.unmatched_installments = pd.DataFrame()  # Unmatched credit card installments
        self.filtered_invoices = pd.DataFrame()  # For search filtering
        self.filtered_ofx = pd.DataFrame()  # For search filtering
        self.filtered_installments = pd.DataFrame()  # For search filtering

        # Debounce timer for unified search (prevent lag on typing)
        self.unified_search_timer = QTimer()
        self.unified_search_timer.setSingleShot(True)
        self.unified_search_timer.timeout.connect(self._execute_unified_filter)
        self.pending_unified_search = ""

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)

        # Unified search and controls
        top_controls = self._create_top_controls()
        main_layout.addWidget(top_controls)

        # Summary stats
        self.summary_label = QLabel("Aguardando dados de vinculação...")
        self.summary_label.setStyleSheet("""
            padding: 10px;
            background-color: #FFF3E0;
            border-radius: 6px;
            font-size: 11px;
            color: #424242;
        """)
        main_layout.addWidget(self.summary_label)

        # Three tables stacked vertically (no splitter)
        # 1. Unmatched invoices
        invoices_group = self._create_invoices_table()
        main_layout.addWidget(invoices_group)

        # 2. Unmatched OFX transactions
        ofx_group = self._create_ofx_table()
        main_layout.addWidget(ofx_group)

        # 3. Unmatched credit card installments
        installments_group = self._create_installments_table()
        main_layout.addWidget(installments_group)

        self.setLayout(main_layout)

    def _create_header(self):
        """Create header section"""
        header_frame = QWidget()
        header_frame.setMaximumHeight(70)
        header_frame.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F57C00, stop:1 #E65100);
                border-radius: 8px;
            }
        """)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("🔍 Itens Não Vinculados")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")

        subtitle = QLabel("Notas fiscais e pagamentos sem vinculação automática")
        subtitle.setStyleSheet("color: #FFE0B2; font-size: 10px; background: transparent;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_frame.setLayout(header_layout)

        return header_frame

    def _create_top_controls(self):
        """Create unified search and link button"""
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

        # Unified search
        search_label = QLabel("🔍 Buscar:")
        search_label.setStyleSheet("font-size: 11px; color: #666; font-weight: bold;")
        controls_layout.addWidget(search_label)

        self.unified_search = QLineEdit()
        self.unified_search.setPlaceholderText("Digite para buscar em todas as tabelas (número, cliente, CPF, descrição)...")
        self.unified_search.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 2px solid #00897B;
                border-radius: 4px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #00695C;
            }
        """)
        self.unified_search.textChanged.connect(self.filter_all_tables)
        controls_layout.addWidget(self.unified_search, 1)  # Take most space

        controls_layout.addSpacing(20)

        # Manual match button
        self.btn_manual_match = QPushButton("🔗 Vincular Selecionados")
        self.btn_manual_match.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.btn_manual_match.clicked.connect(self.create_manual_match)
        self.btn_manual_match.setEnabled(False)
        controls_layout.addWidget(self.btn_manual_match)

        controls_frame.setLayout(controls_layout)
        return controls_frame

    def _create_invoices_table(self):
        """Create unmatched invoices table"""
        invoices_group = QGroupBox("📄 Notas Fiscais Não Vinculadas")
        invoices_layout = QVBoxLayout()

        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(6)
        self.invoices_table.setHorizontalHeaderLabels([
            'Nº', 'Data', 'Cliente', 'CPF/CNPJ', 'Valor', 'Status'
        ])

        # Configure table - Cliente column gets more space
        header = self.invoices_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Número
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Cliente (expands)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # CPF
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Valor
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status

        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.invoices_table.setSelectionMode(QAbstractItemView.MultiSelection)  # Allow multiple selection
        self.invoices_table.setSortingEnabled(True)  # Enable column sorting
        self.invoices_table.itemSelectionChanged.connect(self.update_link_button_state)  # Update button when selection changes
        self.invoices_table.setStyleSheet("""
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

        invoices_layout.addWidget(self.invoices_table)
        invoices_group.setLayout(invoices_layout)

        return invoices_group

    def _create_ofx_table(self):
        """Create unmatched OFX transactions table"""
        ofx_group = QGroupBox("💰 Pagamentos Não Vinculados (OFX)")
        ofx_layout = QVBoxLayout()

        self.ofx_table = QTableWidget()
        self.ofx_table.setColumnCount(5)
        self.ofx_table.setHorizontalHeaderLabels([
            'Data', 'Descrição', 'CPF/CNPJ', 'Valor', 'Banco'
        ])

        # Configure table - Descrição gets much more space
        header = self.ofx_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Descrição (expands)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # CPF
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Valor
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Banco

        # Make Descrição column wider by setting minimum width
        header.setMinimumSectionSize(200)  # Minimum 200px for description

        self.ofx_table.setAlternatingRowColors(True)
        self.ofx_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ofx_table.setSelectionMode(QAbstractItemView.MultiSelection)  # Allow multiple selection
        self.ofx_table.setSortingEnabled(True)  # Enable column sorting
        self.ofx_table.itemSelectionChanged.connect(self.update_link_button_state)  # Update button when selection changes
        self.ofx_table.setStyleSheet("""
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

        ofx_layout.addWidget(self.ofx_table)
        ofx_group.setLayout(ofx_layout)

        return ofx_group

    def _create_installments_table(self):
        """Create unmatched credit card installments table"""
        installments_group = QGroupBox("💳 Parcelas de Cartão Não Vinculadas")
        installments_layout = QVBoxLayout()

        self.installments_table = QTableWidget()
        self.installments_table.setColumnCount(5)
        self.installments_table.setHorizontalHeaderLabels([
            'NSU/DOC', 'Data Prevista', 'Nome', 'CPF Cliente', 'Valor Líquido'
        ])

        # Configure table
        header = self.installments_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # NSU
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Nome (expands)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # CPF
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Valor

        self.installments_table.setAlternatingRowColors(True)
        self.installments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.installments_table.setSelectionMode(QAbstractItemView.MultiSelection)  # Allow multiple selection
        self.installments_table.setSortingEnabled(True)  # Enable column sorting
        self.installments_table.itemSelectionChanged.connect(self.update_link_button_state)  # Update button when selection changes
        self.installments_table.setStyleSheet("""
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

        installments_layout.addWidget(self.installments_table)
        installments_group.setLayout(installments_layout)

        return installments_group

    def _create_controls_old(self):
        """Create manual matching controls"""
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

        # Info label
        info_label = QLabel("Selecione uma nota fiscal e um pagamento para vinculá-los manualmente:")
        info_label.setStyleSheet("font-size: 10px; color: #666;")
        controls_layout.addWidget(info_label)

        controls_layout.addStretch()

        # Manual match button
        self.btn_manual_match = QPushButton("🔗 Vincular Selecionados")
        self.btn_manual_match.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.btn_manual_match.clicked.connect(self.create_manual_match)
        self.btn_manual_match.setEnabled(False)
        controls_layout.addWidget(self.btn_manual_match)

        # Refresh button
        self.btn_refresh = QPushButton("🔄 Atualizar")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #424242;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #BDBDBD;
            }
        """)
        self.btn_refresh.clicked.connect(self.refresh_unmatched)
        controls_layout.addWidget(self.btn_refresh)

        controls_frame.setLayout(controls_layout)
        return controls_frame

    def set_data(self, invoices_df, ofx_df):
        """
        Set invoices and OFX data

        Args:
            invoices_df: DataFrame with invoices (including match status)
            ofx_df: DataFrame with OFX transactions
        """
        self.invoices_df = invoices_df
        self.ofx_df = ofx_df
        self.refresh_unmatched()

    def set_card_data(self, installments_df):
        """
        Set credit card installments data

        Args:
            installments_df: DataFrame with credit card installments
        """
        self.installments_df = installments_df
        self.refresh_unmatched()

    def filter_all_tables(self, search_text):
        """Filter all tables based on unified search text (with debounce)"""
        # Stop previous timer
        self.unified_search_timer.stop()

        # Store search text
        self.pending_unified_search = search_text

        # Start timer (300ms delay - waits for user to stop typing)
        self.unified_search_timer.start(300)

    def _execute_unified_filter(self):
        """Actually execute the unified filter on all tables (called by timer)"""
        search_text = self.pending_unified_search

        # Filter invoices
        if not search_text or self.unmatched_invoices.empty:
            self.filtered_invoices = self.unmatched_invoices.copy()
        else:
            search_lower = search_text.lower()
            mask = (
                self.unmatched_invoices['numero'].astype(str).str.lower().str.contains(search_lower, na=False) |
                self.unmatched_invoices['nome_tomador'].astype(str).str.lower().str.contains(search_lower, na=False) |
                self.unmatched_invoices['cpf_cnpj'].astype(str).str.contains(search_lower, na=False) |
                self.unmatched_invoices.get('cpf_cnpj_formatted', pd.Series([''] * len(self.unmatched_invoices))).astype(str).str.contains(search_lower, na=False)
            )
            self.filtered_invoices = self.unmatched_invoices[mask].copy()

        # Filter OFX
        if not search_text or self.unmatched_ofx.empty:
            self.filtered_ofx = self.unmatched_ofx.copy()
        else:
            search_lower = search_text.lower()
            mask = (
                self.unmatched_ofx.get('descricao', pd.Series([''] * len(self.unmatched_ofx))).astype(str).str.lower().str.contains(search_lower, na=False) |
                self.unmatched_ofx.get('cpf_cnpj', pd.Series([''] * len(self.unmatched_ofx))).astype(str).str.contains(search_lower, na=False) |
                self.unmatched_ofx.get('banco', pd.Series([''] * len(self.unmatched_ofx))).astype(str).str.lower().str.contains(search_lower, na=False)
            )
            self.filtered_ofx = self.unmatched_ofx[mask].copy()

        # Filter installments
        if not search_text or self.unmatched_installments.empty:
            self.filtered_installments = self.unmatched_installments.copy()
        else:
            search_lower = search_text.lower()
            mask = (
                self.unmatched_installments.get('nsu_doc', pd.Series([''] * len(self.unmatched_installments))).astype(str).str.contains(search_lower, na=False) |
                self.unmatched_installments.get('nome', pd.Series([''] * len(self.unmatched_installments))).astype(str).str.lower().str.contains(search_lower, na=False) |
                self.unmatched_installments.get('cpf_cliente', pd.Series([''] * len(self.unmatched_installments))).astype(str).str.contains(search_lower, na=False)
            )
            self.filtered_installments = self.unmatched_installments[mask].copy()

        # Update all tables
        self.update_invoices_table()
        self.update_ofx_table()
        self.update_installments_table()

    def update_link_button_state(self):
        """Enable/disable link button based on selections"""
        invoice_selected = len(self.invoices_table.selectedItems()) > 0
        ofx_selected = len(self.ofx_table.selectedItems()) > 0
        installment_selected = len(self.installments_table.selectedItems()) > 0

        # Enable button if: (1 invoice AND (1 OFX OR 1 installment))
        can_link = invoice_selected and (ofx_selected or installment_selected)
        self.btn_manual_match.setEnabled(can_link)

    def refresh_unmatched(self):
        """Refresh unmatched items lists"""
        # Find unmatched invoices
        if self.invoices_df is not None and not self.invoices_df.empty:
            # Unmatched: status is Pendente or valor_matched is 0
            self.unmatched_invoices = self.invoices_df[
                (self.invoices_df['status'] == 'Pendente') |
                (self.invoices_df.get('valor_matched', 0) == 0)
            ].copy()
        else:
            self.unmatched_invoices = pd.DataFrame()

        # Find unmatched OFX transactions (credits without match)
        if self.ofx_df is not None and not self.ofx_df.empty:
            # Get only credits
            ofx_credits = self.ofx_df[self.ofx_df['valor'] > 0].copy()

            # Mark as unmatched if not referenced in any invoice
            # This is simplified - in reality we'd need to track which OFX IDs are matched
            # For now, show all credits with CPF/CNPJ that don't match invoice amounts
            self.unmatched_ofx = ofx_credits.copy()
        else:
            self.unmatched_ofx = pd.DataFrame()

        # Find unmatched credit card installments
        if self.installments_df is not None and not self.installments_df.empty:
            self.unmatched_installments = self.installments_df[
                self.installments_df['status_vinculacao'] == 'Pendente'
            ].copy()
        else:
            self.unmatched_installments = pd.DataFrame()

        # Initialize filtered data (same as unmatched initially)
        self.filtered_invoices = self.unmatched_invoices.copy()
        self.filtered_ofx = self.unmatched_ofx.copy()
        self.filtered_installments = self.unmatched_installments.copy()

        # Update tables
        self.update_invoices_table()
        self.update_ofx_table()
        self.update_installments_table()
        self.update_summary()

    def filter_invoices(self, search_text):
        """Filter invoices table based on search text (with debounce)"""
        # Stop previous timer
        self.invoice_search_timer.stop()

        # Store search text
        self.pending_invoice_search = search_text

        # Start timer (300ms delay - waits for user to stop typing)
        self.invoice_search_timer.start(300)

    def _execute_invoice_filter(self):
        """Actually execute the invoice filter (called by timer)"""
        search_text = self.pending_invoice_search

        if not search_text or self.unmatched_invoices.empty:
            self.filtered_invoices = self.unmatched_invoices.copy()
        else:
            search_text = search_text.lower()
            mask = (
                self.unmatched_invoices['numero'].astype(str).str.lower().str.contains(search_text, na=False) |
                self.unmatched_invoices['nome_tomador'].astype(str).str.lower().str.contains(search_text, na=False) |
                self.unmatched_invoices['cpf_cnpj'].astype(str).str.contains(search_text, na=False) |
                self.unmatched_invoices.get('cpf_cnpj_formatted', pd.Series([''] * len(self.unmatched_invoices))).astype(str).str.contains(search_text, na=False)
            )
            self.filtered_invoices = self.unmatched_invoices[mask].copy()

        self.update_invoices_table()

    def filter_ofx(self, search_text):
        """Filter OFX table based on search text (with debounce)"""
        # Stop previous timer
        self.ofx_search_timer.stop()

        # Store search text
        self.pending_ofx_search = search_text

        # Start timer (300ms delay - waits for user to stop typing)
        self.ofx_search_timer.start(300)

    def _execute_ofx_filter(self):
        """Actually execute the OFX filter (called by timer)"""
        search_text = self.pending_ofx_search

        if not search_text or self.unmatched_ofx.empty:
            self.filtered_ofx = self.unmatched_ofx.copy()
        else:
            search_text = search_text.lower()
            mask = (
                self.unmatched_ofx.get('descricao', pd.Series([''] * len(self.unmatched_ofx))).astype(str).str.lower().str.contains(search_text, na=False) |
                self.unmatched_ofx.get('cpf_cnpj', pd.Series([''] * len(self.unmatched_ofx))).astype(str).str.contains(search_text, na=False) |
                self.unmatched_ofx.get('banco', pd.Series([''] * len(self.unmatched_ofx))).astype(str).str.lower().str.contains(search_text, na=False) |
                self.unmatched_ofx.get('conta', pd.Series([''] * len(self.unmatched_ofx))).astype(str).str.contains(search_text, na=False)
            )
            self.filtered_ofx = self.unmatched_ofx[mask].copy()

        self.update_ofx_table()

    def update_invoices_table(self):
        """Update unmatched invoices table"""
        df = self.filtered_invoices  # Use filtered data

        if df is None or df.empty:
            self.invoices_table.setRowCount(0)
            return

        # Disable sorting during update (major performance improvement)
        self.invoices_table.setSortingEnabled(False)

        self.invoices_table.setRowCount(len(df))

        for row_idx, (idx, row) in enumerate(df.iterrows()):
            # Número
            self.invoices_table.setItem(row_idx, 0, QTableWidgetItem(str(row['numero'])))

            # Data
            self.invoices_table.setItem(row_idx, 1, QTableWidgetItem(row['data']))

            # Cliente
            self.invoices_table.setItem(row_idx, 2, QTableWidgetItem(row['nome_tomador'][:30]))

            # CPF/CNPJ
            cpf_cnpj = row.get('cpf_cnpj_formatted', row.get('cpf_cnpj', ''))
            self.invoices_table.setItem(row_idx, 3, QTableWidgetItem(cpf_cnpj))

            # Valor
            valor_item = QTableWidgetItem(f"R$ {row['valor_liquido']:,.2f}")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.invoices_table.setItem(row_idx, 4, valor_item)

            # Status
            status = row.get('status', 'Pendente')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setBackground(QColor(255, 200, 200))
            self.invoices_table.setItem(row_idx, 5, status_item)

        # Re-enable sorting
        self.invoices_table.setSortingEnabled(True)

    def update_ofx_table(self):
        """Update unmatched OFX transactions table"""
        df = self.filtered_ofx  # Use filtered data

        if df is None or df.empty:
            self.ofx_table.setRowCount(0)
            return

        # Disable sorting during update (major performance improvement)
        self.ofx_table.setSortingEnabled(False)

        self.ofx_table.setRowCount(len(df))

        for row_idx, (idx, row) in enumerate(df.iterrows()):
            # Data
            self.ofx_table.setItem(row_idx, 0, QTableWidgetItem(row['data']))

            # Descrição - mostrar mais caracteres (100 em vez de 50)
            descricao = row.get('descricao', row.get('memo', ''))
            # Não truncar - deixar a coluna Stretch mostrar tudo
            self.ofx_table.setItem(row_idx, 1, QTableWidgetItem(descricao))

            # CPF/CNPJ
            cpf_cnpj = row.get('cpf_cnpj', '')
            if not cpf_cnpj:
                cpf_cnpj = '-'
            self.ofx_table.setItem(row_idx, 2, QTableWidgetItem(cpf_cnpj))

            # Valor
            valor_item = QTableWidgetItem(f"R$ {row['valor']:,.2f}")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            valor_item.setBackground(QColor(200, 255, 200))
            self.ofx_table.setItem(row_idx, 3, valor_item)

            # Banco
            banco = row.get('banco', 'N/A')[:20]
            self.ofx_table.setItem(row_idx, 4, QTableWidgetItem(banco))

        # Re-enable sorting
        self.ofx_table.setSortingEnabled(True)

    def update_installments_table(self):
        """Update unmatched credit card installments table"""
        df = self.filtered_installments  # Use filtered data

        if df is None or df.empty:
            self.installments_table.setRowCount(0)
            return

        # Disable sorting during update (major performance improvement)
        self.installments_table.setSortingEnabled(False)

        self.installments_table.setRowCount(len(df))

        for row_idx, (idx, row) in enumerate(df.iterrows()):
            # NSU/DOC
            self.installments_table.setItem(row_idx, 0, QTableWidgetItem(str(row.get('nsu_doc', ''))))

            # Data Prevista - convert Timestamp to string
            data_prevista = row.get('data_prevista', '')
            if isinstance(data_prevista, str):
                data_str = data_prevista
            else:
                # It's a Timestamp, convert to string
                data_str = str(data_prevista)[:10] if pd.notna(data_prevista) else ''
            self.installments_table.setItem(row_idx, 1, QTableWidgetItem(data_str))

            # Nome
            nome = row.get('nome', '')
            self.installments_table.setItem(row_idx, 2, QTableWidgetItem(str(nome)))

            # CPF Cliente
            cpf = row.get('cpf_cliente', '-')
            self.installments_table.setItem(row_idx, 3, QTableWidgetItem(str(cpf)))

            # Valor Líquido
            valor_item = QTableWidgetItem(f"R$ {row.get('valor', 0):,.2f}")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            valor_item.setBackground(QColor(255, 248, 220))  # Light yellow for card
            self.installments_table.setItem(row_idx, 4, valor_item)

        # Re-enable sorting
        self.installments_table.setSortingEnabled(True)

    def update_summary(self):
        """Update summary label"""
        total_invoices = len(self.unmatched_invoices) if not self.unmatched_invoices.empty else 0
        total_ofx = len(self.unmatched_ofx) if not self.unmatched_ofx.empty else 0
        total_installments = len(self.unmatched_installments) if not self.unmatched_installments.empty else 0

        valor_invoices = self.unmatched_invoices['valor_liquido'].sum() if not self.unmatched_invoices.empty else 0
        valor_ofx = self.unmatched_ofx['valor'].sum() if not self.unmatched_ofx.empty else 0
        valor_installments = self.unmatched_installments['valor'].sum() if not self.unmatched_installments.empty else 0

        self.summary_label.setText(
            f"📄 Notas não vinculadas: {total_invoices} (R$ {valor_invoices:,.2f}) | "
            f"💳 Parcelas cartão não vinculadas: {total_installments} (R$ {valor_installments:,.2f}) | "
            f"💰 Pagamentos não vinculados: {total_ofx} (R$ {valor_ofx:,.2f})"
        )

    def create_manual_match(self):
        """Create a manual match between selected invoice and OFX transaction"""
        # Get selected rows
        invoice_selection = self.invoices_table.selectedItems()
        ofx_selection = self.ofx_table.selectedItems()

        if not invoice_selection or not ofx_selection:
            QMessageBox.warning(
                self,
                "Seleção Incompleta",
                "Selecione uma nota fiscal e um pagamento para vincular."
            )
            return

        # Get selected row indices
        invoice_row = self.invoices_table.selectedItems()[0].row()
        ofx_row = self.ofx_table.selectedItems()[0].row()

        # Get the data
        invoice_numero = self.invoices_table.item(invoice_row, 0).text()
        invoice_valor = self.invoices_table.item(invoice_row, 4).text()
        ofx_descricao = self.ofx_table.item(ofx_row, 1).text()
        ofx_valor = self.ofx_table.item(ofx_row, 3).text()

        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirmar Vinculação Manual",
            f"Vincular manualmente:\n\n"
            f"Nota Fiscal: {invoice_numero} - {invoice_valor}\n"
            f"Pagamento: {ofx_descricao} - {ofx_valor}\n\n"
            f"Confirmar vinculação?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Emit signal for manual match creation
            # This should be handled by the main application to update the data
            QMessageBox.information(
                self,
                "Vinculação Manual",
                "Funcionalidade de vinculação manual será implementada na próxima versão.\n"
                "Esta vinculação permitirá associar pagamentos com notas fiscais que não foram "
                "detectadas automaticamente."
            )
            # TODO: Implement manual matching persistence
            # self.manual_match_created.emit(invoice_numero, ofx_id)

    def get_unmatched_summary(self):
        """
        Get summary of unmatched items

        Returns:
            dict: Summary statistics
        """
        return {
            'unmatched_invoices_count': len(self.unmatched_invoices) if not self.unmatched_invoices.empty else 0,
            'unmatched_invoices_value': self.unmatched_invoices['valor_liquido'].sum() if not self.unmatched_invoices.empty else 0,
            'unmatched_ofx_count': len(self.unmatched_ofx) if not self.unmatched_ofx.empty else 0,
            'unmatched_ofx_value': self.unmatched_ofx['valor'].sum() if not self.unmatched_ofx.empty else 0,
        }
