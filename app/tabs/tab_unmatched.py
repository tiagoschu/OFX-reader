"""
Unmatched Items Tab - Show invoices and OFX transactions without matches
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QGroupBox,
                             QHeaderView, QAbstractItemView, QSplitter, QMessageBox,
                             QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
import pandas as pd


class UnmatchedTab(QWidget):
    """Tab for showing and managing unmatched invoices and OFX transactions"""

    manual_match_created = pyqtSignal(str, str)  # invoice_id, ofx_id

    def __init__(self):
        super().__init__()
        self.invoices_df = None
        self.ofx_df = None
        self.unmatched_invoices = pd.DataFrame()
        self.unmatched_ofx = pd.DataFrame()
        self.filtered_invoices = pd.DataFrame()  # For search filtering
        self.filtered_ofx = pd.DataFrame()  # For search filtering
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)

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

        # Splitter for two tables
        splitter = QSplitter(Qt.Vertical)

        # Unmatched invoices table
        invoices_group = self._create_invoices_table()
        splitter.addWidget(invoices_group)

        # Unmatched OFX transactions table
        ofx_group = self._create_ofx_table()
        splitter.addWidget(ofx_group)

        # Set initial sizes (50/50 split)
        splitter.setSizes([400, 400])

        main_layout.addWidget(splitter)

        # Manual matching controls
        controls_frame = self._create_controls()
        main_layout.addWidget(controls_frame)

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

    def _create_invoices_table(self):
        """Create unmatched invoices table"""
        invoices_group = QGroupBox("📄 Notas Fiscais Não Vinculadas")
        invoices_layout = QVBoxLayout()

        # Search box for invoices
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Buscar:")
        search_label.setStyleSheet("font-size: 10px; color: #666;")
        search_layout.addWidget(search_label)

        self.invoice_search = QLineEdit()
        self.invoice_search.setPlaceholderText("Digite para buscar (número, cliente, CPF/CNPJ)...")
        self.invoice_search.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                font-size: 10px;
            }
        """)
        self.invoice_search.textChanged.connect(self.filter_invoices)
        search_layout.addWidget(self.invoice_search)

        invoices_layout.addLayout(search_layout)

        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(7)
        self.invoices_table.setHorizontalHeaderLabels([
            'Nº', 'Data', 'Cliente', 'CPF/CNPJ', 'Valor', 'Status', 'Motivo'
        ])

        # Configure table - Cliente column gets more space
        header = self.invoices_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Número
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Cliente (expands)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # CPF
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Valor
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Motivo (expands)

        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.invoices_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.invoices_table.setSortingEnabled(True)  # Enable column sorting
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

        # Search box for OFX
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Buscar:")
        search_label.setStyleSheet("font-size: 10px; color: #666;")
        search_layout.addWidget(search_label)

        self.ofx_search = QLineEdit()
        self.ofx_search.setPlaceholderText("Digite para buscar (descrição, CPF/CNPJ, banco)...")
        self.ofx_search.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                font-size: 10px;
            }
        """)
        self.ofx_search.textChanged.connect(self.filter_ofx)
        search_layout.addWidget(self.ofx_search)

        ofx_layout.addLayout(search_layout)

        self.ofx_table = QTableWidget()
        self.ofx_table.setColumnCount(6)
        self.ofx_table.setHorizontalHeaderLabels([
            'Data', 'Descrição', 'CPF/CNPJ', 'Valor', 'Banco', 'Conta'
        ])

        # Configure table - Descrição gets much more space
        header = self.ofx_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Descrição (expands - twice as much space)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # CPF
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Valor
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Banco
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Conta

        # Make Descrição column wider by setting minimum width
        header.setMinimumSectionSize(200)  # Minimum 200px for description

        self.ofx_table.setAlternatingRowColors(True)
        self.ofx_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ofx_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ofx_table.setSortingEnabled(True)  # Enable column sorting
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

    def _create_controls(self):
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

        # Initialize filtered data (same as unmatched initially)
        self.filtered_invoices = self.unmatched_invoices.copy()
        self.filtered_ofx = self.unmatched_ofx.copy()

        # Update tables
        self.update_invoices_table()
        self.update_ofx_table()
        self.update_summary()

    def filter_invoices(self, search_text):
        """Filter invoices table based on search text"""
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
        """Filter OFX table based on search text"""
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

            # Motivo (placeholder - can be enhanced)
            motivo = "Sem pagamento encontrado"
            if row.get('cpf_cnpj', '') == '':
                motivo = "CPF/CNPJ não identificado"

            self.invoices_table.setItem(row_idx, 6, QTableWidgetItem(motivo))

    def update_ofx_table(self):
        """Update unmatched OFX transactions table"""
        df = self.filtered_ofx  # Use filtered data

        if df is None or df.empty:
            self.ofx_table.setRowCount(0)
            return

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

            # Conta
            conta = row.get('conta', 'N/A')[:15]
            self.ofx_table.setItem(row_idx, 5, QTableWidgetItem(conta))

    def update_summary(self):
        """Update summary label"""
        total_invoices = len(self.unmatched_invoices) if not self.unmatched_invoices.empty else 0
        total_ofx = len(self.unmatched_ofx) if not self.unmatched_ofx.empty else 0

        valor_invoices = self.unmatched_invoices['valor_liquido'].sum() if not self.unmatched_invoices.empty else 0
        valor_ofx = self.unmatched_ofx['valor'].sum() if not self.unmatched_ofx.empty else 0

        self.summary_label.setText(
            f"📄 Notas não vinculadas: {total_invoices} (R$ {valor_invoices:,.2f}) | "
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
