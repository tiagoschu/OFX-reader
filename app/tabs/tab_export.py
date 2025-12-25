"""
Export Tab - Multi-format data export
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QComboBox, QCheckBox,
                             QFileDialog, QMessageBox, QGroupBox, QRadioButton,
                             QButtonGroup, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.exporter import DataExporter
from utils.config import config


class ExportThread(QThread):
    """Thread for exporting data"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, df, export_format, file_path, options):
        super().__init__()
        self.df = df
        self.export_format = export_format
        self.file_path = file_path
        self.options = options

    def run(self):
        try:
            exporter = DataExporter(self.df)
            self.progress.emit(f"Exportando para {self.export_format.upper()}...")

            success = False
            if self.export_format == 'csv':
                success = exporter.export_csv(self.file_path, include_time=self.options.get('include_time', True))
            elif self.export_format == 'excel':
                success = exporter.export_excel(self.file_path, include_time=self.options.get('include_time', True))
            elif self.export_format == 'json':
                success = exporter.export_json(self.file_path)
            elif self.export_format == 'ofx':
                success = exporter.export_ofx_consolidated(self.file_path)
            elif self.export_format == 'pdf':
                success = exporter.export_pdf_report(self.file_path)

            if success:
                self.finished.emit(True, self.file_path)
            else:
                self.finished.emit(False, "Erro durante exportação")

        except Exception as e:
            self.finished.emit(False, str(e))


class ExportTab(QWidget):
    """Export tab for multi-format data export"""

    def __init__(self):
        super().__init__()
        self.df = None
        self.export_thread = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header_frame = QFrame()
        header_frame.setMaximumHeight(50)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00897B, stop:1 #00695C);
                border-radius: 6px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("💾 Exportar Dados")
        title.setStyleSheet("color: white; font-size: 13px; font-weight: bold; background: transparent;")
        header_layout.addWidget(title)

        self.status_label = QLabel("Pronto para exportar")
        self.status_label.setStyleSheet("color: #B2DFDB; font-size: 9px; background: transparent;")
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Format selection
        format_group = QGroupBox("📋 Formato de Exportação")
        format_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #B2DFDB;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px;
            }
        """)
        format_layout = QVBoxLayout()
        format_layout.setSpacing(4)

        self.format_group = QButtonGroup()
        formats = [
            ('csv', '📊 CSV (Comma-Separated Values)', 'Compatível com Excel e planilhas'),
            ('excel', '📗 Excel (XLSX)', 'Arquivo Excel nativo com formatação'),
            ('json', '📄 JSON', 'Formato estruturado para APIs'),
            ('ofx', '💼 OFX Consolidado', 'Único arquivo OFX com todas transações'),
            ('pdf', '📕 PDF Report', 'Relatório visual em PDF'),
        ]

        for i, (fmt, label, desc) in enumerate(formats):
            radio = QRadioButton(label)
            radio.setProperty('format', fmt)
            radio.setStyleSheet("font-size: 10px;")

            desc_label = QLabel(f"  └─ {desc}")
            desc_label.setStyleSheet("font-size: 8px; color: #666; margin-left: 20px;")

            self.format_group.addButton(radio, i)
            format_layout.addWidget(radio)
            format_layout.addWidget(desc_label)

            if fmt == 'csv':
                radio.setChecked(True)

        format_group.setLayout(format_layout)
        main_layout.addWidget(format_group)

        # Options
        options_group = QGroupBox("⚙️ Opções")
        options_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #B2DFDB;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        options_layout = QVBoxLayout()
        options_layout.setSpacing(4)

        self.cb_include_time = QCheckBox("Incluir coluna de hora (hh:mm:ss)")
        self.cb_include_time.setChecked(True)
        self.cb_include_time.setStyleSheet("font-size: 10px;")

        self.cb_open_after = QCheckBox("Abrir arquivo após exportação")
        self.cb_open_after.setChecked(True)
        self.cb_open_after.setStyleSheet("font-size: 10px;")

        options_layout.addWidget(self.cb_include_time)
        options_layout.addWidget(self.cb_open_after)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #B2DFDB;
                border-radius: 3px;
                text-align: center;
                font-size: 9px;
            }
            QProgressBar::chunk {
                background-color: #00897B;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Export button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_export = QPushButton("💾 Exportar Dados")
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #00897B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 30px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
            QPushButton:disabled {
                background-color: #B2DFDB;
            }
        """)
        self.btn_export.clicked.connect(self.export_data)
        self.btn_export.setEnabled(False)

        btn_layout.addWidget(self.btn_export)
        main_layout.addLayout(btn_layout)

        # Info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #E0F2F1;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(8, 6, 8, 6)

        info_label = QLabel(
            "ℹ️ <b>Dica:</b> Importe dados na aba <b>Importar</b> antes de exportar."
        )
        info_label.setStyleSheet("font-size: 9px; color: #00695C; background: transparent;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        info_frame.setLayout(info_layout)
        main_layout.addWidget(info_frame)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def update_data(self, df):
        """Update with data to export"""
        self.df = df

        if df is None or df.empty:
            self.btn_export.setEnabled(False)
            self.status_label.setText("Nenhum dado para exportar")
        else:
            self.btn_export.setEnabled(True)
            self.status_label.setText(f"{len(df)} transações prontas para exportar")

    def export_data(self):
        """Export data in selected format"""
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "Aviso", "Nenhum dado para exportar!")
            return

        # Get selected format
        selected_btn = self.format_group.checkedButton()
        if not selected_btn:
            QMessageBox.warning(self, "Aviso", "Selecione um formato de exportação!")
            return

        export_format = selected_btn.property('format')

        # File extensions
        extensions = {
            'csv': 'CSV Files (*.csv)',
            'excel': 'Excel Files (*.xlsx)',
            'json': 'JSON Files (*.json)',
            'ofx': 'OFX Files (*.ofx)',
            'pdf': 'PDF Files (*.pdf)',
        }

        # Get save location
        last_dir = config.get('last_export_directory', os.path.expanduser('~'))
        file_filter = extensions.get(export_format, 'All Files (*.*)')

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Arquivo",
            last_dir,
            file_filter
        )

        if not file_path:
            return

        # Save last directory
        config.set('last_export_directory', os.path.dirname(file_path))

        # Prepare options
        options = {
            'include_time': self.cb_include_time.isChecked(),
        }

        # Start export thread
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.btn_export.setEnabled(False)

        self.export_thread = ExportThread(self.df, export_format, file_path, options)
        self.export_thread.progress.connect(self.on_export_progress)
        self.export_thread.finished.connect(self.on_export_finished)
        self.export_thread.start()

    def on_export_progress(self, message):
        """Handle export progress"""
        self.status_label.setText(message)

    def on_export_finished(self, success, result):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        self.btn_export.setEnabled(True)

        if success:
            self.status_label.setText(f"✅ Exportado com sucesso!")

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Sucesso")
            msg.setText("Dados exportados com sucesso!")
            msg.setInformativeText(f"Arquivo salvo em:\n{result}")
            msg.setStandardButtons(QMessageBox.Ok)

            if self.cb_open_after.isChecked():
                btn_open = msg.addButton("Abrir Arquivo", QMessageBox.ActionRole)
                msg.exec_()

                if msg.clickedButton() == btn_open:
                    import subprocess
                    import platform

                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', result])
                    elif platform.system() == 'Windows':
                        os.startfile(result)
                    else:  # Linux
                        subprocess.call(['xdg-open', result])
            else:
                msg.exec_()
        else:
            self.status_label.setText(f"❌ Erro na exportação")
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao exportar dados:\n{result}"
            )
