"""
Reports Tab - Generate detailed reports
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QComboBox, QGroupBox,
                             QFileDialog, QMessageBox, QDateEdit, QCheckBox)
from PyQt5.QtCore import Qt, QDate
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.exporter import DataExporter
from core.analyzer import DataAnalyzer
from utils.config import config


class ReportsTab(QWidget):
    """Reports generation tab"""

    def __init__(self):
        super().__init__()
        self.df = None
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
                    stop:0 #5E35B1, stop:1 #4527A0);
                border-radius: 6px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("📋 Relatórios")
        title.setStyleSheet("color: white; font-size: 13px; font-weight: bold; background: transparent;")
        header_layout.addWidget(title)

        self.status_label = QLabel("Selecione um tipo de relatório")
        self.status_label.setStyleSheet("color: #D1C4E9; font-size: 9px; background: transparent;")
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Report Type
        type_group = QGroupBox("📊 Tipo de Relatório")
        type_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #D1C4E9;
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
        type_layout = QVBoxLayout()
        type_layout.setSpacing(6)

        self.cb_report_type = QComboBox()
        self.cb_report_type.addItems([
            '📈 Resumo Financeiro Completo',
            '📊 Análise por Categoria',
            '🏦 Análise por Banco',
            '📅 Análise Mensal',
            '🔍 Transações Detalhadas',
            '⚠️ Gaps e Inconsistências',
        ])
        self.cb_report_type.setStyleSheet("""
            QComboBox {
                font-size: 10px;
                padding: 6px;
                border: 1px solid #D1C4E9;
                border-radius: 3px;
            }
        """)
        self.cb_report_type.currentIndexChanged.connect(self.on_report_type_changed)
        type_layout.addWidget(self.cb_report_type)

        # Description
        self.report_description = QLabel(
            "Relatório completo com todas as métricas financeiras, gráficos e análises."
        )
        self.report_description.setStyleSheet("font-size: 9px; color: #666; padding: 4px;")
        self.report_description.setWordWrap(True)
        type_layout.addWidget(self.report_description)

        type_group.setLayout(type_layout)
        main_layout.addWidget(type_group)

        # Period
        period_group = QGroupBox("📅 Período")
        period_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #D1C4E9;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        period_layout = QVBoxLayout()
        period_layout.setSpacing(6)

        self.cb_all_period = QCheckBox("Incluir todo o período disponível")
        self.cb_all_period.setChecked(True)
        self.cb_all_period.setStyleSheet("font-size: 10px;")
        self.cb_all_period.stateChanged.connect(self.on_period_changed)
        period_layout.addWidget(self.cb_all_period)

        # Date range
        date_layout = QHBoxLayout()

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-6))
        self.date_from.setEnabled(False)
        self.date_from.setStyleSheet("font-size: 10px; padding: 4px;")
        date_layout.addWidget(QLabel("De:"))
        date_layout.addWidget(self.date_from)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setEnabled(False)
        self.date_to.setStyleSheet("font-size: 10px; padding: 4px;")
        date_layout.addWidget(QLabel("Até:"))
        date_layout.addWidget(self.date_to)

        period_layout.addLayout(date_layout)
        period_group.setLayout(period_layout)
        main_layout.addWidget(period_group)

        # Options
        options_group = QGroupBox("⚙️ Opções")
        options_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #D1C4E9;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        options_layout = QVBoxLayout()
        options_layout.setSpacing(4)

        self.cb_include_charts = QCheckBox("Incluir gráficos")
        self.cb_include_charts.setChecked(True)
        self.cb_include_charts.setStyleSheet("font-size: 10px;")
        options_layout.addWidget(self.cb_include_charts)

        self.cb_include_details = QCheckBox("Incluir tabela detalhada de transações")
        self.cb_include_details.setChecked(False)
        self.cb_include_details.setStyleSheet("font-size: 10px;")
        options_layout.addWidget(self.cb_include_details)

        self.cb_open_after = QCheckBox("Abrir relatório após geração")
        self.cb_open_after.setChecked(True)
        self.cb_open_after.setStyleSheet("font-size: 10px;")
        options_layout.addWidget(self.cb_open_after)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Generate button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_generate = QPushButton("📋 Gerar Relatório (PDF)")
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #5E35B1;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 30px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #512DA8;
            }
            QPushButton:disabled {
                background-color: #D1C4E9;
            }
        """)
        self.btn_generate.clicked.connect(self.generate_report)
        self.btn_generate.setEnabled(False)
        btn_layout.addWidget(self.btn_generate)

        main_layout.addLayout(btn_layout)

        # Info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #EDE7F6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(8, 6, 8, 6)

        info_label = QLabel(
            "ℹ️ <b>Dica:</b> Os relatórios em PDF incluem análises visuais "
            "e podem ser compartilhados facilmente."
        )
        info_label.setStyleSheet("font-size: 9px; color: #4A148C; background: transparent;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        info_frame.setLayout(info_layout)
        main_layout.addWidget(info_frame)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def on_report_type_changed(self):
        """Update description based on report type"""
        descriptions = {
            0: "Relatório completo com todas as métricas financeiras, gráficos e análises.",
            1: "Análise detalhada de despesas organizadas por categoria.",
            2: "Comparação de transações entre diferentes bancos e contas.",
            3: "Evolução mensal de receitas, despesas e saldo.",
            4: "Lista completa de todas as transações com filtros aplicados.",
            5: "Relatório de períodos faltantes e possíveis inconsistências nos dados.",
        }

        idx = self.cb_report_type.currentIndex()
        self.report_description.setText(descriptions.get(idx, ""))

    def on_period_changed(self):
        """Toggle date range inputs"""
        enabled = not self.cb_all_period.isChecked()
        self.date_from.setEnabled(enabled)
        self.date_to.setEnabled(enabled)

    def update_data(self, df):
        """Update with data"""
        self.df = df

        if df is None or df.empty:
            self.btn_generate.setEnabled(False)
            self.status_label.setText("Nenhum dado disponível")
        else:
            self.btn_generate.setEnabled(True)
            self.status_label.setText(f"{len(df)} transações disponíveis")

    def generate_report(self):
        """Generate selected report"""
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "Aviso", "Nenhum dado disponível para gerar relatório!")
            return

        # Get save location
        last_dir = config.get('last_export_directory', os.path.expanduser('~'))

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            last_dir,
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        # Save directory
        config.set('last_export_directory', os.path.dirname(file_path))

        # Map report type index to report type string
        report_types = {
            0: 'complete',      # Resumo Financeiro Completo
            1: 'by_category',   # Análise por Categoria
            2: 'by_bank',       # Análise por Banco
            3: 'monthly',       # Análise Mensal
            4: 'detailed',      # Transações Detalhadas
            5: 'gaps',          # Gaps e Inconsistências
        }

        report_type = report_types.get(self.cb_report_type.currentIndex(), 'complete')

        # Get date filter if not all period
        date_filter = None
        if not self.cb_all_period.isChecked():
            start_date = self.date_from.date().toString('dd/MM/yyyy')
            end_date = self.date_to.date().toString('dd/MM/yyyy')
            date_filter = (start_date, end_date)

        # Generate report
        try:
            exporter = DataExporter(self.df)
            success = exporter.export_pdf_report(
                file_path,
                report_type=report_type,
                include_details=self.cb_include_details.isChecked(),
                date_filter=date_filter
            )

            if success:
                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Relatório gerado com sucesso!\n\nSalvo em:\n{file_path}"
                )

                if self.cb_open_after.isChecked():
                    import subprocess
                    import platform

                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', file_path])
                    elif platform.system() == 'Windows':
                        os.startfile(file_path)
                    else:  # Linux
                        subprocess.call(['xdg-open', file_path])
            else:
                QMessageBox.warning(self, "Erro", "Erro ao gerar relatório!")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório:\n{str(e)}")
