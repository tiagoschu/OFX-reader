"""
Invoices Tab - Import and manage NFSe invoices
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QFileDialog,
                             QGroupBox, QProgressBar, QMessageBox, QComboBox,
                             QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.invoice_parser import NFSeParser
from core.invoice_matcher import InvoiceMatcher


class ParseThread(QThread):
    """Thread for parsing invoice XML files"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)  # DataFrame

    def __init__(self, files):
        super().__init__()
        self.files = files

    def run(self):
        parser = NFSeParser()
        self.progress.emit(f"Processando {len(self.files)} arquivo(s) XML...")

        df = parser.parse_files(self.files)

        if df.empty:
            self.progress.emit("Nenhuma nota fiscal encontrada")
        else:
            self.progress.emit(f"{len(df)} nota(s) fiscal(is) importada(s)")

        self.finished.emit(df)


class MatchThread(QThread):
    """Thread for matching invoices with OFX"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object, object, object)  # invoices_df, matches_df, summary

    def __init__(self, invoices_df, ofx_df, tolerance_days, tolerance_percent):
        super().__init__()
        self.invoices_df = invoices_df
        self.ofx_df = ofx_df
        self.tolerance_days = tolerance_days
        self.tolerance_percent = tolerance_percent

    def run(self):
        self.progress.emit("Iniciando análise...")

        matcher = InvoiceMatcher(
            tolerance_days=self.tolerance_days,
            tolerance_percent=self.tolerance_percent
        )

        invoices, matches, summary = matcher.match(self.invoices_df, self.ofx_df)

        self.progress.emit(f"Análise concluída: {summary['matched']} de {summary['total_invoices']} nota(s) vinculada(s)")

        self.finished.emit(invoices, matches, summary)


class InvoicesTab(QWidget):
    """Tab for importing and managing invoices"""

    invoices_loaded = pyqtSignal(object)  # Emit DataFrame when invoices are loaded
    match_requested = pyqtSignal()  # Request OFX data for matching

    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.invoices_df = None
        self.matches_df = None
        self.ofx_df = None  # Will be set from main window
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

        # Table
        table_group = self._create_table()
        main_layout.addWidget(table_group)

        # Status bar
        self.status_label = QLabel("Nenhuma nota fiscal importada")
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
                    stop:0 #5C6BC0, stop:1 #3F51B5);
                border-radius: 8px;
            }
        """)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("📄 Notas Fiscais Emitidas (NFSe)")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")

        subtitle = QLabel("Importação e gestão de notas fiscais eletrônicas")
        subtitle.setStyleSheet("color: #C5CAE9; font-size: 10px; background: transparent;")

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

        # Import button
        self.btn_import = QPushButton("📂 Importar XMLs")
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #5C6BC0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3F51B5;
            }
        """)
        self.btn_import.clicked.connect(self.import_invoices)
        controls_layout.addWidget(self.btn_import)

        # Clear button
        self.btn_clear = QPushButton("🗑️ Limpar")
        self.btn_clear.setStyleSheet("""
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
        self.btn_clear.clicked.connect(self.clear_invoices)
        controls_layout.addWidget(self.btn_clear)

        controls_layout.addSpacing(20)

        # Match button
        self.btn_match = QPushButton("🔗 Vincular com OFX")
        self.btn_match.setStyleSheet("""
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
        self.btn_match.clicked.connect(self.match_with_ofx)
        self.btn_match.setEnabled(False)
        controls_layout.addWidget(self.btn_match)

        # Filter combo
        controls_layout.addSpacing(20)
        filter_label = QLabel("Filtro:")
        filter_label.setStyleSheet("font-size: 10px; color: #666;")
        controls_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todas", "Pagas", "Pendentes", "Parciais"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
                min-width: 100px;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        controls_layout.addWidget(self.filter_combo)

        controls_layout.addStretch()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)

        controls_frame.setLayout(controls_layout)
        return controls_frame

    def _create_table(self):
        """Create invoices table"""
        table_group = QGroupBox("Notas Fiscais")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            'Nº', 'Data', 'Cliente', 'CPF/CNPJ', 'Valor', 'ISS', 'Status',
            'Vinculado', 'Descrição'
        ])

        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Número
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Cliente
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # CPF
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Valor
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # ISS
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Vinculado
        header.setSectionResizeMode(8, QHeaderView.Stretch)  # Descrição

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
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

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)

        return table_group

    def import_invoices(self):
        """Import invoice files (XML, CSV, PDF)"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Arquivos de Notas Fiscais",
            "",
            "Todos NFSe (*.xml *.csv *.pdf);;XML Files (*.xml);;CSV Files (*.csv);;PDF Files (*.pdf);;All Files (*.*)"
        )

        if not files:
            return

        self.selected_files = files

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.btn_import.setEnabled(False)

        # Start parsing thread
        self.parse_thread = ParseThread(files)
        self.parse_thread.progress.connect(self.on_parse_progress)
        self.parse_thread.finished.connect(self.on_parse_finished)
        self.parse_thread.start()

    def on_parse_progress(self, message):
        """Handle parse progress"""
        self.status_label.setText(message)

    def on_parse_finished(self, df):
        """Handle parse finished"""
        self.progress_bar.setVisible(False)
        self.btn_import.setEnabled(True)

        if df.empty:
            QMessageBox.warning(
                self,
                "Importação",
                "Nenhuma nota fiscal válida foi encontrada nos arquivos selecionados."
            )
            return

        self.invoices_df = df
        self.update_table()
        self.update_status()
        self.btn_match.setEnabled(True)

        # Emit signal
        self.invoices_loaded.emit(df)

        QMessageBox.information(
            self,
            "Importação Concluída",
            f"{len(df)} nota(s) fiscal(is) importada(s) com sucesso!"
        )

    def update_table(self, df=None):
        """Update table with invoices"""
        if df is None:
            df = self.invoices_df

        if df is None or df.empty:
            self.table.setRowCount(0)
            return

        self.table.setRowCount(len(df))

        for row_idx, (idx, row) in enumerate(df.iterrows()):
            # Número
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['numero'])))

            # Data
            self.table.setItem(row_idx, 1, QTableWidgetItem(row['data']))

            # Cliente
            self.table.setItem(row_idx, 2, QTableWidgetItem(row['nome_tomador'][:30]))

            # CPF/CNPJ
            self.table.setItem(row_idx, 3, QTableWidgetItem(row['cpf_cnpj_formatted']))

            # Valor
            valor_item = QTableWidgetItem(f"R$ {row['valor_liquido']:,.2f}")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 4, valor_item)

            # ISS
            iss_item = QTableWidgetItem(f"R$ {row['valor_iss']:,.2f}")
            iss_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 5, iss_item)

            # Status
            status = row.get('status', 'Pendente')
            status_item = QTableWidgetItem(self._get_status_icon(status))
            status_item.setTextAlignment(Qt.AlignCenter)

            # Color code
            if status == 'Pago':
                status_item.setBackground(QColor(200, 255, 200))
            elif status == 'Parcial':
                status_item.setBackground(QColor(255, 255, 200))
            else:
                status_item.setBackground(QColor(255, 200, 200))

            self.table.setItem(row_idx, 6, status_item)

            # Vinculado
            matched_value = row.get('valor_matched', 0)
            if matched_value > 0:
                vinculado_text = f"R$ {matched_value:,.2f}"
            else:
                vinculado_text = "-"

            vinculado_item = QTableWidgetItem(vinculado_text)
            vinculado_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 7, vinculado_item)

            # Descrição
            discriminacao = row.get('discriminacao', '')[:50]
            self.table.setItem(row_idx, 8, QTableWidgetItem(discriminacao))

    def _get_status_icon(self, status):
        """Get icon for status"""
        if status == 'Pago':
            return '🟢 Pago'
        elif status == 'Parcial':
            return '🟡 Parcial'
        else:
            return '🔴 Pendente'

    def update_status(self):
        """Update status label"""
        if self.invoices_df is None or self.invoices_df.empty:
            self.status_label.setText("Nenhuma nota fiscal importada")
            return

        total = len(self.invoices_df)
        total_value = self.invoices_df['valor_liquido'].sum()

        pagas = len(self.invoices_df[self.invoices_df['status'] == 'Pago'])
        pendentes = len(self.invoices_df[self.invoices_df['status'] == 'Pendente'])
        parciais = len(self.invoices_df[self.invoices_df['status'] == 'Parcial'])

        self.status_label.setText(
            f"Total: {total} notas | R$ {total_value:,.2f} | "
            f"🟢 Pagas: {pagas} | 🔴 Pendentes: {pendentes} | 🟡 Parciais: {parciais}"
        )

    def clear_invoices(self):
        """Clear all invoices"""
        reply = QMessageBox.question(
            self,
            "Limpar Notas",
            "Tem certeza que deseja limpar todas as notas fiscais importadas?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.invoices_df = None
            self.matches_df = None
            self.table.setRowCount(0)
            self.update_status()
            self.btn_match.setEnabled(False)

    def match_with_ofx(self):
        """Match invoices with OFX data"""
        if self.invoices_df is None or self.invoices_df.empty:
            QMessageBox.warning(self, "Vincular", "Nenhuma nota fiscal importada.")
            return

        if self.ofx_df is None or self.ofx_df.empty:
            reply = QMessageBox.question(
                self,
                "Dados OFX",
                "Nenhum arquivo OFX foi importado ainda. Deseja importar agora?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.match_requested.emit()
            return

        # Ask for tolerance settings
        from PyQt5.QtWidgets import QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Configurações de Vinculação")

        layout = QFormLayout()

        days_spin = QSpinBox()
        days_spin.setRange(0, 30)
        days_spin.setValue(3)
        layout.addRow("Tolerância de dias (±):", days_spin)

        percent_spin = QDoubleSpinBox()
        percent_spin.setRange(0, 50)
        percent_spin.setValue(5.0)
        percent_spin.setSuffix("%")
        layout.addRow("Tolerância de valor (±):", percent_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.setLayout(layout)

        if dialog.exec_() != QDialog.Accepted:
            return

        tolerance_days = days_spin.value()
        tolerance_percent = percent_spin.value()

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.btn_match.setEnabled(False)

        # Start matching thread
        self.match_thread = MatchThread(
            self.invoices_df,
            self.ofx_df,
            tolerance_days,
            tolerance_percent
        )
        self.match_thread.progress.connect(self.on_match_progress)
        self.match_thread.finished.connect(self.on_match_finished)
        self.match_thread.start()

    def on_match_progress(self, message):
        """Handle match progress"""
        self.status_label.setText(message)

    def on_match_finished(self, invoices, matches, summary):
        """Handle match finished"""
        self.progress_bar.setVisible(False)
        self.btn_match.setEnabled(True)

        self.invoices_df = invoices
        self.matches_df = matches

        self.update_table()
        self.update_status()

        QMessageBox.information(
            self,
            "Vinculação Concluída",
            f"Análise concluída:\n\n"
            f"Total de notas: {summary['total_invoices']}\n"
            f"Vinculadas: {summary['matched']}\n"
            f"Pendentes: {summary['pending']}\n\n"
            f"Valor total: R$ {summary['total_value']:,.2f}\n"
            f"Valor vinculado: R$ {summary['matched_value']:,.2f}\n"
            f"Valor pendente: R$ {summary['pending_value']:,.2f}"
        )

    def apply_filter(self, filter_text):
        """Apply filter to table"""
        if self.invoices_df is None or self.invoices_df.empty:
            return

        if filter_text == "Todas":
            filtered_df = self.invoices_df
        elif filter_text == "Pagas":
            filtered_df = self.invoices_df[self.invoices_df['status'] == 'Pago']
        elif filter_text == "Pendentes":
            filtered_df = self.invoices_df[self.invoices_df['status'] == 'Pendente']
        elif filter_text == "Parciais":
            filtered_df = self.invoices_df[self.invoices_df['status'] == 'Parcial']
        else:
            filtered_df = self.invoices_df

        self.update_table(filtered_df)

    def set_ofx_data(self, ofx_df):
        """Set OFX data for matching"""
        self.ofx_df = ofx_df

    def get_invoices_data(self):
        """Get current invoices DataFrame"""
        return self.invoices_df

    def load_invoices(self, df):
        """Load invoices from DataFrame (from project)"""
        self.invoices_df = df
        self.update_table()
        self.update_status()
        if df is not None and not df.empty:
            self.btn_match.setEnabled(True)
