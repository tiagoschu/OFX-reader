"""
Import Tab - File selection and processing
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QFileDialog,
                             QCheckBox, QRadioButton, QButtonGroup, QTextEdit,
                             QGroupBox, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ofx_processor import OFXProcessor
from core.categorizer import TransactionCategorizer
from core.exporter import DataExporter
from utils.config import config
from datetime import datetime


class ProcessThread(QThread):
    """Thread for processing OFX files"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object, object)  # df, processor

    def __init__(self, files, remove_duplicates):
        super().__init__()
        self.files = files
        self.remove_duplicates = remove_duplicates

    def run(self):
        processor = OFXProcessor()
        self.progress.emit("Processando arquivos...")

        df = processor.process_multiple_files(self.files, self.remove_duplicates)

        # Add categorization
        if not df.empty:
            self.progress.emit("Categorizando transações...")
            categorizer = TransactionCategorizer()
            df = categorizer.categorize_dataframe(df)

        self.finished.emit(df, processor)


class ImportTab(QWidget):
    """Tab for importing OFX files"""

    data_processed = pyqtSignal(object, object)  # Emit DataFrame and processor when processed

    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.df_result = None
        self.processor = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("📥 Importar Arquivos OFX")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # File selection section
        file_group = QGroupBox("Seleção de Arquivos")
        file_layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("📁 Adicionar Arquivos OFX")
        self.btn_add.clicked.connect(self.add_files)
        self.btn_clear = QPushButton("🗑️ Limpar Lista")
        self.btn_clear.clicked.connect(self.clear_files)
        self.file_count_label = QLabel("Nenhum arquivo selecionado")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.file_count_label)
        btn_layout.addStretch()

        file_layout.addLayout(btn_layout)

        # File table
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(['Arquivo', 'Tamanho', 'Caminho'])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        file_layout.addWidget(self.file_table)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Options section
        options_group = QGroupBox("Opções de Processamento")
        options_layout = QVBoxLayout()

        self.cb_remove_duplicates = QCheckBox("Remover transações duplicadas")
        self.cb_remove_duplicates.setChecked(config.get('remove_duplicates', True))

        self.cb_include_time = QCheckBox("Incluir coluna de horário")
        self.cb_include_time.setChecked(config.get('include_time', True))

        options_layout.addWidget(self.cb_remove_duplicates)
        options_layout.addWidget(self.cb_include_time)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Process button
        self.btn_process = QPushButton("⚡ Processar Arquivos")
        self.btn_process.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.btn_process.clicked.connect(self.process_files)
        layout.addWidget(self.btn_process)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results section
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        self.setLayout(layout)

    def add_files(self):
        """Add OFX files"""
        last_dir = config.get('last_directory', os.path.expanduser('~'))
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecione arquivos OFX",
            last_dir,
            "OFX Files (*.ofx);;All Files (*.*)"
        )

        if files:
            # Save last directory
            config.set('last_directory', os.path.dirname(files[0]))

            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)

                    # Add to table
                    row = self.file_table.rowCount()
                    self.file_table.insertRow(row)

                    file_name = os.path.basename(file_path)
                    size = os.path.getsize(file_path)
                    size_str = self.format_size(size)

                    self.file_table.setItem(row, 0, QTableWidgetItem(file_name))
                    self.file_table.setItem(row, 1, QTableWidgetItem(size_str))
                    self.file_table.setItem(row, 2, QTableWidgetItem(file_path))

            self.update_file_count()

    def clear_files(self):
        """Clear file list"""
        self.selected_files = []
        self.file_table.setRowCount(0)
        self.results_text.clear()
        self.update_file_count()

    def update_file_count(self):
        """Update file count label"""
        count = len(self.selected_files)
        if count == 0:
            self.file_count_label.setText("Nenhum arquivo selecionado")
        elif count == 1:
            self.file_count_label.setText("1 arquivo selecionado")
        else:
            self.file_count_label.setText(f"{count} arquivos selecionados")

    def format_size(self, size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def process_files(self):
        """Process selected files"""
        if not self.selected_files:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo selecionado!")
            return

        # Clear results
        self.results_text.clear()

        # Disable button
        self.btn_process.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        # Save config
        config.set('remove_duplicates', self.cb_remove_duplicates.isChecked())
        config.set('include_time', self.cb_include_time.isChecked())

        # Start processing thread
        self.thread = ProcessThread(
            self.selected_files,
            self.cb_remove_duplicates.isChecked()
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_processing_finished)
        self.thread.start()

    def update_progress(self, message):
        """Update progress message"""
        self.results_text.append(message)

    def on_processing_finished(self, df, processor):
        """Handle processing completion"""
        self.df_result = df
        self.processor = processor

        # Hide progress
        self.progress_bar.setVisible(False)
        self.btn_process.setEnabled(True)

        if df.empty:
            self.results_text.append("\n❌ Nenhuma transação encontrada!")
            QMessageBox.warning(self, "Aviso", "Nenhuma transação foi encontrada nos arquivos.")
            return

        # Show summary
        self.show_summary()

        # Emit signal with data and processor
        self.data_processed.emit(df, processor)

        # Ask to save
        reply = QMessageBox.question(
            self,
            "Exportar Dados",
            "Processamento concluído! Deseja exportar os dados agora?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.save_results()

    def show_summary(self):
        """Show processing summary"""
        summary = self.processor.get_summary(self.df_result)

        self.results_text.append("\n" + "="*60)
        self.results_text.append("RESUMO DO PROCESSAMENTO")
        self.results_text.append("="*60 + "\n")

        self.results_text.append(f"Total de transações: {summary['total_transacoes']}")
        self.results_text.append(f"  - Créditos: {summary['total_creditos']} (R$ {summary['soma_creditos']:,.2f})")
        self.results_text.append(f"  - Débitos: {summary['total_debitos']} (R$ {summary['soma_debitos']:,.2f})")
        self.results_text.append(f"  - Saldo líquido: R$ {summary['saldo_liquido']:,.2f}\n")

        self.results_text.append(f"Bancos distintos: {summary['bancos']}")
        self.results_text.append(f"Contas distintas: {summary['contas']}")
        self.results_text.append(f"Arquivos processados: {summary['arquivos_processados']}")

        if summary['arquivos_com_erro'] > 0:
            self.results_text.append(f"⚠️ Arquivos com erro: {summary['arquivos_com_erro']}")

        if self.processor.errors:
            self.results_text.append("\nERROS ENCONTRADOS:")
            for error in self.processor.errors:
                self.results_text.append(f"  - {error}")

        self.results_text.append("\n" + "="*60)

    def save_results(self):
        """Save processed data"""
        if self.df_result is None or self.df_result.empty:
            return

        # Get export format from config
        export_format = config.get('export_format', 'csv')

        if export_format == 'csv':
            default_ext = ".csv"
            file_filter = "CSV Files (*.csv)"
        else:
            default_ext = ".xlsx"
            file_filter = "Excel Files (*.xlsx)"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"extratos_consolidados_{timestamp}{default_ext}"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar arquivo",
            default_name,
            file_filter
        )

        if file_path:
            exporter = DataExporter(self.df_result)

            if export_format == 'csv':
                success = exporter.export_csv(file_path)
            else:
                success = exporter.export_excel(file_path)

            if success:
                self.results_text.append(f"\n✅ Arquivo salvo em: {file_path}")
                QMessageBox.information(self, "Sucesso", f"Arquivo exportado com sucesso!\n\n{file_path}")
            else:
                QMessageBox.critical(self, "Erro", "Falha ao exportar arquivo.")
