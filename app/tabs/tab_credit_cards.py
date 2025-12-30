"""
Credit Cards Tab - Import and manage credit card sales
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QFileDialog,
                             QGroupBox, QProgressBar, QMessageBox, QTreeWidget,
                             QTreeWidgetItem, QHeaderView, QAbstractItemView,
                             QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.credit_card_parser import CreditCardParser
from core.credit_card_matcher import CreditCardMatcher


class ParseThread(QThread):
    """Thread for parsing credit card sales CSV"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object, object, object)  # sales_df, installments_df, errors

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        parser = CreditCardParser()
        self.progress.emit(f"Processando arquivo CSV...")

        sales_df, installments_df, errors = parser.parse_csv(self.file_path)

        if errors:
            error_msg = f"{len(errors)} erro(s) encontrado(s):\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... e mais {len(errors) - 5} erro(s)"
            self.progress.emit(error_msg)

        if not sales_df.empty:
            self.progress.emit(f"{len(sales_df)} venda(s) e {len(installments_df)} parcela(s) importada(s)")
        else:
            self.progress.emit("Nenhuma venda encontrada")

        self.finished.emit(sales_df, installments_df, errors)


class MatchThread(QThread):
    """Thread for matching credit card installments with OFX"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object, object, object)  # installments_df, matches_df, summary

    def __init__(self, installments_df, ofx_df, date_tolerance=5, value_tolerance=0.10):
        super().__init__()
        self.installments_df = installments_df
        self.ofx_df = ofx_df
        self.date_tolerance = date_tolerance
        self.value_tolerance = value_tolerance

    def run(self):
        import time

        start_time = time.time()
        self.progress.emit("Iniciando vinculação com OFX...")
        print(f"[CARD-MATCHING] Thread iniciada - {time.strftime('%H:%M:%S')}")

        matcher = CreditCardMatcher(
            date_tolerance_days=self.date_tolerance,
            value_tolerance=self.value_tolerance
        )

        match_start = time.time()
        print(f"[CARD-MATCHING] Iniciando match() - {time.strftime('%H:%M:%S')}")
        installments, matches, summary = matcher.match(self.installments_df, self.ofx_df)
        match_end = time.time()
        print(f"[CARD-MATCHING] Match concluído em {match_end - match_start:.2f}s - {time.strftime('%H:%M:%S')}")

        self.progress.emit(f"Vinculação concluída: {summary['vinculadas']} de {summary['total_parcelas']} parcela(s) vinculada(s)")

        emit_start = time.time()
        print(f"[CARD-MATCHING] Emitindo sinal finished - {time.strftime('%H:%M:%S')}")
        self.finished.emit(installments, matches, summary)
        emit_end = time.time()
        print(f"[CARD-MATCHING] Sinal emitido em {emit_end - emit_start:.2f}s - {time.strftime('%H:%M:%S')}")
        print(f"[CARD-MATCHING] Thread finalizada - Tempo total: {emit_end - start_time:.2f}s")


class CreditCardsTab(QWidget):
    """Tab for importing and managing credit card sales"""

    cards_loaded = pyqtSignal(object, object)  # Emit sales_df, installments_df when loaded
    match_requested = pyqtSignal()  # Request OFX data for matching

    def __init__(self):
        super().__init__()
        self.file_path = None
        self.sales_df = None
        self.installments_df = None
        self.matches_df = None
        self.ofx_df = None  # Will be set from main window
        self.errors = []
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Import section
        import_group = self._create_import_section()
        layout.addWidget(import_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Nenhum arquivo carregado")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

        # Summary section
        summary_group = self._create_summary_section()
        layout.addWidget(summary_group)

        # Splitter for tables
        splitter = QSplitter(Qt.Vertical)

        # Sales table (top)
        sales_group = self._create_sales_section()
        splitter.addWidget(sales_group)

        # Installments table (bottom)
        installments_group = self._create_installments_section()
        splitter.addWidget(installments_group)

        splitter.setStretchFactor(0, 3)  # Sales get more space
        splitter.setStretchFactor(1, 2)  # Installments get less space

        layout.addWidget(splitter)

        self.setLayout(layout)

    def _create_import_section(self):
        """Create import controls section"""
        group = QGroupBox("📁 Importação de Vendas no Cartão")
        layout = QVBoxLayout()

        # File selection
        file_layout = QHBoxLayout()

        self.import_btn = QPushButton("📂 Selecionar CSV de Vendas")
        self.import_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.import_btn)

        self.template_btn = QPushButton("📋 Baixar Modelo CSV")
        self.template_btn.clicked.connect(self.download_template)
        file_layout.addWidget(self.template_btn)

        file_layout.addStretch()
        layout.addLayout(file_layout)

        # File path display
        self.file_label = QLabel("Nenhum arquivo selecionado")
        self.file_label.setStyleSheet("color: #666; font-style: italic; margin-left: 10px;")
        layout.addWidget(self.file_label)

        # Match controls
        match_layout = QHBoxLayout()

        self.match_btn = QPushButton("🔗 Vincular com OFX")
        self.match_btn.clicked.connect(self.start_matching)
        self.match_btn.setEnabled(False)
        match_layout.addWidget(self.match_btn)

        self.refresh_btn = QPushButton("🔄 Atualizar")
        self.refresh_btn.clicked.connect(self.refresh_tables)
        self.refresh_btn.setEnabled(False)
        match_layout.addWidget(self.refresh_btn)

        match_layout.addStretch()
        layout.addLayout(match_layout)

        group.setLayout(layout)
        return group

    def _create_summary_section(self):
        """Create summary statistics section"""
        group = QGroupBox("📊 Resumo")
        layout = QHBoxLayout()

        self.summary_labels = {
            'vendas': QLabel("Vendas: 0"),
            'parcelas': QLabel("Parcelas: 0"),
            'vinculadas': QLabel("Vinculadas: 0"),
            'pendentes': QLabel("Pendentes: 0"),
            'valor_total': QLabel("Total: R$ 0,00"),
            'valor_vinculado': QLabel("Vinculado: R$ 0,00"),
            'valor_pendente': QLabel("Pendente: R$ 0,00")
        }

        for label in self.summary_labels.values():
            label.setStyleSheet("font-weight: bold; padding: 5px;")
            layout.addWidget(label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_sales_section(self):
        """Create sales table section"""
        group = QGroupBox("💳 Vendas Importadas")
        layout = QVBoxLayout()

        self.sales_tree = QTreeWidget()
        self.sales_tree.setHeaderLabels([
            'NSU/DOC', 'CPF/CNPJ', 'Nome', 'Data Venda', 'Bandeira',
            'Parcelas', 'Valor Bruto', 'Valor Líquido', 'Adquirente'
        ])

        # Configure table
        self.sales_tree.setAlternatingRowColors(True)
        self.sales_tree.setSortingEnabled(True)

        # Column widths
        header = self.sales_tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # NSU/DOC
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # CPF/CNPJ
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Nome
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Bandeira
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Parcelas
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Valor Bruto
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Valor Líquido
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Adquirente

        layout.addWidget(self.sales_tree)
        group.setLayout(layout)
        return group

    def _create_installments_section(self):
        """Create installments table section"""
        group = QGroupBox("📅 Parcelas Detalhadas")
        layout = QVBoxLayout()

        self.installments_table = QTableWidget()
        self.installments_table.setColumnCount(9)
        self.installments_table.setHorizontalHeaderLabels([
            'NSU/DOC', 'Parcela', 'Data Prevista', 'Valor', 'Status',
            'OFX Data', 'OFX Valor', 'Dif. Dias', 'Dif. Valor'
        ])

        # Configure table
        self.installments_table.setAlternatingRowColors(True)
        self.installments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.installments_table.setSortingEnabled(True)
        self.installments_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Column widths
        header = self.installments_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Venda ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Parcela
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Valor
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # OFX Data
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # OFX Valor
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Dif. Dias
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Dif. Valor

        layout.addWidget(self.installments_table)
        group.setLayout(layout)
        return group

    def select_file(self):
        """Open file dialog to select CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo CSV de vendas",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Arquivo: {os.path.basename(file_path)}")
            self.file_label.setStyleSheet("color: #000; margin-left: 10px;")
            self.start_parsing()

    def download_template(self):
        """Download CSV template"""
        # Ask where to save
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar modelo CSV",
            "vendas_cartao_modelo.csv",
            "CSV Files (*.csv)"
        )

        if save_path:
            # Create template CSV content
            template_content = """Data da venda,Hora da venda,Estabelecimento,CPF/CNPJ do estabelecimento,Forma de pagamento,Quantidade total de parcelas,Bandeira,Valor bruto,Taxa/tarifa,Valor líquido,Status da venda,Tipo de lançamento,Modalidade,Tipo de captura,Documento de origem,Origem do valor,Motivo,Data do lançamento,Data prevista do pagamento,Código de autorização,NSU/DOC,Código da venda,TID,Origem do cartão,Nome,Email,Telefone,CPF,Adquirente
10/05/2025,14:30:00,Loja Exemplo Ltda,12.345.678/0001-90,Crédito parcelado,4,Visa,100.00,4.49,95.51,Aprovada,Venda,Parcelado,Online,DOC123,Venda,Compra aprovada,10/05/2025,10/06/2025,AUTH001,NSU12345,VENDA001,TID001,Nacional,João Silva,joao@email.com,11999999999,12345678900,Cielo
15/05/2025,16:45:00,Restaurante ABC,98.765.432/0001-10,Crédito à vista,1,Mastercard,250.00,7.50,242.50,Aprovada,Venda,À vista,Presencial,DOC124,Venda,Compra aprovada,15/05/2025,15/06/2025,AUTH002,NSU12346,VENDA002,TID002,Nacional,Maria Santos,maria@email.com,11988888888,98765432100,Stone
20/05/2025,10:15:00,Serviços XYZ,11.222.333/0001-44,Débito,1,Elo,150.00,3.00,147.00,Aprovada,Venda,Débito,Online,DOC125,Venda,Compra aprovada,20/05/2025,22/05/2025,AUTH003,NSU12347,VENDA003,TID003,Nacional,Pedro Costa,pedro@email.com,11977777777,11122233344,Rede
"""

            try:
                # Write template to file
                with open(save_path, 'w', encoding='utf-8-sig') as f:
                    f.write(template_content)

                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Modelo CSV salvo em:\n{save_path}\n\nCampos obrigatórios (*):\n" +
                    "- CPF/CNPJ do estabelecimento\n" +
                    "- Quantidade total de parcelas\n" +
                    "- Valor bruto\n" +
                    "- Taxa/tarifa\n" +
                    "- Valor líquido\n" +
                    "- Data do lançamento\n" +
                    "- Data prevista do pagamento"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro",
                    f"Erro ao salvar modelo:\n{str(e)}"
                )

    def start_parsing(self):
        """Start parsing CSV file in background thread"""
        if not self.file_path:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.import_btn.setEnabled(False)
        self.status_label.setText("Processando arquivo...")

        self.parse_thread = ParseThread(self.file_path)
        self.parse_thread.progress.connect(self.update_progress)
        self.parse_thread.finished.connect(self.on_parse_finished)
        self.parse_thread.start()

    def update_progress(self, message):
        """Update progress label"""
        self.status_label.setText(message)

    def on_parse_finished(self, sales_df, installments_df, errors):
        """Handle parse completion"""
        import time

        start_time = time.time()
        print(f"[CARD-UI] on_parse_finished iniciado - {time.strftime('%H:%M:%S')}")

        self.progress_bar.setVisible(False)
        self.import_btn.setEnabled(True)
        self.errors = errors

        if sales_df.empty:
            self.status_label.setText("❌ Nenhuma venda foi importada")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

            if errors:
                error_msg = "Erros encontrados:\n\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    error_msg += f"\n\n... e mais {len(errors) - 10} erro(s)"
                QMessageBox.warning(self, "Erros na Importação", error_msg)
            return

        self.sales_df = sales_df
        self.installments_df = installments_df

        # Update UI
        update_start = time.time()
        self.update_tables()
        print(f"[CARD-UI] update_tables() concluído em {time.time() - update_start:.2f}s")

        self.update_summary()
        self.match_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)

        self.status_label.setText(
            f"✓ {len(sales_df)} venda(s) e {len(installments_df)} parcela(s) importada(s)"
        )
        self.status_label.setStyleSheet("color: green; font-weight: bold;")

        # Emit signal to main window
        self.cards_loaded.emit(sales_df, installments_df)

        # Show warnings if any
        if errors:
            error_msg = f"{len(errors)} aviso(s)/erro(s) encontrado(s):\n\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n\n... e mais {len(errors) - 10} aviso(s)"
            QMessageBox.warning(self, "Avisos na Importação", error_msg)

        print(f"[CARD-UI] on_parse_finished concluído em {time.time() - start_time:.2f}s")

    def update_tables(self):
        """Update sales and installments tables"""
        if self.sales_df is None or self.sales_df.empty:
            return

        # Update sales tree
        self.sales_tree.clear()

        for _, sale in self.sales_df.iterrows():
            sale_item = QTreeWidgetItem([
                str(sale.get('nsu_doc', '')),
                str(sale.get('cpf_cnpj', '')),
                str(sale.get('nome', '')),
                str(sale.get('data_venda', ''))[:10] if pd.notna(sale.get('data_venda')) else '',
                str(sale.get('bandeira', '')),
                f"{sale.get('qtd_parcelas', 0)}x",
                f"R$ {sale.get('valor_bruto', 0):,.2f}",
                f"R$ {sale.get('valor_liquido', 0):,.2f}",
                str(sale.get('adquirente', ''))
            ])

            self.sales_tree.addTopLevelItem(sale_item)

            # Add installments as children
            if self.installments_df is not None:
                sale_installments = self.installments_df[
                    self.installments_df['venda_id'] == sale.get('id')
                ].copy()

                for _, inst in sale_installments.iterrows():
                    status = inst.get('status_vinculacao', 'Pendente')

                    inst_text = [
                        '',
                        f"  Parcela {inst.get('numero_parcela')}/{inst.get('total_parcelas')}",
                        str(inst.get('data_prevista', ''))[:10] if pd.notna(inst.get('data_prevista')) else '',
                        f"R$ {inst.get('valor', 0):,.2f}",
                        status,
                        str(inst.get('ofx_data', '')) if pd.notna(inst.get('ofx_data')) else '',
                        f"R$ {inst.get('ofx_valor', 0):,.2f}" if pd.notna(inst.get('ofx_valor')) else '',
                        ''
                    ]

                    inst_item = QTreeWidgetItem(inst_text)

                    # Color code by status
                    if status == 'Vinculado':
                        inst_item.setForeground(4, QColor(0, 128, 0))
                    else:
                        inst_item.setForeground(4, QColor(200, 100, 0))

                    sale_item.addChild(inst_item)

        # Update installments table
        self.update_installments_table()

    def update_installments_table(self):
        """Update installments table"""
        if self.installments_df is None or self.installments_df.empty:
            self.installments_table.setRowCount(0)
            return

        # Temporarily disable sorting for performance
        self.installments_table.setSortingEnabled(False)

        self.installments_table.setRowCount(len(self.installments_df))

        for row_idx, (_, inst) in enumerate(self.installments_df.iterrows()):
            # NSU/DOC
            self.installments_table.setItem(row_idx, 0, QTableWidgetItem(str(inst.get('nsu_doc', ''))))

            # Parcela
            parcela_text = f"{inst.get('numero_parcela', 0)}/{inst.get('total_parcelas', 0)}"
            self.installments_table.setItem(row_idx, 1, QTableWidgetItem(parcela_text))

            # Data Prevista
            data_prevista = str(inst.get('data_prevista', ''))[:10] if pd.notna(inst.get('data_prevista')) else ''
            self.installments_table.setItem(row_idx, 2, QTableWidgetItem(data_prevista))

            # Valor
            valor_item = QTableWidgetItem(f"R$ {inst.get('valor', 0):,.2f}")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.installments_table.setItem(row_idx, 3, valor_item)

            # Status
            status = inst.get('status_vinculacao', 'Pendente')
            status_item = QTableWidgetItem(status)
            if status == 'Vinculado':
                status_item.setForeground(QColor(0, 128, 0))
            else:
                status_item.setForeground(QColor(200, 100, 0))
            self.installments_table.setItem(row_idx, 4, status_item)

            # OFX Data
            ofx_data = str(inst.get('ofx_data', '')) if pd.notna(inst.get('ofx_data')) else ''
            self.installments_table.setItem(row_idx, 5, QTableWidgetItem(ofx_data))

            # OFX Valor
            ofx_valor = inst.get('ofx_valor', None)
            ofx_valor_text = f"R$ {ofx_valor:,.2f}" if pd.notna(ofx_valor) else ''
            ofx_valor_item = QTableWidgetItem(ofx_valor_text)
            ofx_valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.installments_table.setItem(row_idx, 6, ofx_valor_item)

            # Diferença Dias
            dif_dias = inst.get('diferenca_dias', None)
            dif_dias_text = str(int(dif_dias)) if pd.notna(dif_dias) else ''
            self.installments_table.setItem(row_idx, 7, QTableWidgetItem(dif_dias_text))

            # Diferença Valor
            dif_valor = inst.get('diferenca_valor', None)
            dif_valor_text = f"R$ {dif_valor:.2f}" if pd.notna(dif_valor) else ''
            dif_valor_item = QTableWidgetItem(dif_valor_text)
            dif_valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.installments_table.setItem(row_idx, 8, dif_valor_item)

        # Re-enable sorting
        self.installments_table.setSortingEnabled(True)

    def update_summary(self):
        """Update summary statistics"""
        if self.sales_df is None or self.sales_df.empty:
            return

        vendas_count = len(self.sales_df)
        parcelas_count = len(self.installments_df) if self.installments_df is not None else 0

        if self.installments_df is not None and not self.installments_df.empty:
            vinculadas = len(self.installments_df[self.installments_df['status_vinculacao'] == 'Vinculado'])
            pendentes = parcelas_count - vinculadas

            valor_total = self.installments_df['valor'].sum()
            valor_vinculado = self.installments_df[
                self.installments_df['status_vinculacao'] == 'Vinculado'
            ]['valor'].sum()
            valor_pendente = valor_total - valor_vinculado
        else:
            vinculadas = 0
            pendentes = 0
            valor_total = 0
            valor_vinculado = 0
            valor_pendente = 0

        # Update labels
        self.summary_labels['vendas'].setText(f"Vendas: {vendas_count}")
        self.summary_labels['parcelas'].setText(f"Parcelas: {parcelas_count}")
        self.summary_labels['vinculadas'].setText(f"Vinculadas: {vinculadas}")
        self.summary_labels['vinculadas'].setStyleSheet("font-weight: bold; padding: 5px; color: green;")

        self.summary_labels['pendentes'].setText(f"Pendentes: {pendentes}")
        self.summary_labels['pendentes'].setStyleSheet("font-weight: bold; padding: 5px; color: orange;")

        self.summary_labels['valor_total'].setText(f"Total: R$ {valor_total:,.2f}")
        self.summary_labels['valor_vinculado'].setText(f"Vinculado: R$ {valor_vinculado:,.2f}")
        self.summary_labels['valor_vinculado'].setStyleSheet("font-weight: bold; padding: 5px; color: green;")

        self.summary_labels['valor_pendente'].setText(f"Pendente: R$ {valor_pendente:,.2f}")
        self.summary_labels['valor_pendente'].setStyleSheet("font-weight: bold; padding: 5px; color: orange;")

    def set_ofx_data(self, ofx_df):
        """Set OFX data for matching"""
        self.ofx_df = ofx_df
        print(f"[CARD-TAB] OFX data set: {len(ofx_df) if ofx_df is not None and not ofx_df.empty else 0} transações")

    def start_matching(self):
        """Start matching installments with OFX"""
        if self.installments_df is None or self.installments_df.empty:
            QMessageBox.warning(
                self,
                "Sem Dados",
                "Nenhuma parcela disponível para vincular."
            )
            return

        if self.ofx_df is None or self.ofx_df.empty:
            QMessageBox.warning(
                self,
                "Sem Dados OFX",
                "Nenhuma transação OFX disponível.\nImporte um arquivo OFX primeiro."
            )
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.match_btn.setEnabled(False)
        self.status_label.setText("Vinculando com OFX...")

        self.match_thread = MatchThread(self.installments_df, self.ofx_df)
        self.match_thread.progress.connect(self.update_progress)
        self.match_thread.finished.connect(self.on_match_finished)
        self.match_thread.start()

    def on_match_finished(self, installments, matches, summary):
        """Handle match completion"""
        import time

        start_time = time.time()
        print(f"[CARD-UI] on_match_finished iniciado - {time.strftime('%H:%M:%S')}")

        self.progress_bar.setVisible(False)
        self.match_btn.setEnabled(True)

        self.installments_df = installments
        self.matches_df = matches

        # Update UI
        update_start = time.time()
        self.update_tables()
        print(f"[CARD-UI] update_tables() concluído em {time.time() - update_start:.2f}s")

        self.update_summary()

        self.status_label.setText(
            f"✓ Vinculação concluída: {summary['vinculadas']} de {summary['total_parcelas']} parcela(s)"
        )
        self.status_label.setStyleSheet("color: green; font-weight: bold;")

        # Emit signal to update other tabs
        self.cards_loaded.emit(self.sales_df, self.installments_df)

        print(f"[CARD-UI] on_match_finished concluído em {time.time() - start_time:.2f}s")

    def refresh_tables(self):
        """Refresh all tables"""
        self.update_tables()
        self.update_summary()

    def get_installments_df(self):
        """Get current installments DataFrame"""
        return self.installments_df

    def get_sales_df(self):
        """Get current sales DataFrame"""
        return self.sales_df
