"""
Invoice Analysis Tab - Analyze invoices vs OFX receipts
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QFileDialog,
                             QGroupBox, QComboBox, QHeaderView, QAbstractItemView,
                             QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.invoice_matcher import InvoiceMatcher
from core.exporter import DataExporter


class InvoiceAnalysisTab(QWidget):
    """Tab for analyzing invoices vs OFX receipts"""

    def __init__(self):
        super().__init__()
        self.invoices_df = None
        self.ofx_df = None
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
        info_label = QLabel("Resumo por cliente (CPF/CNPJ) - Total de notas emitidas vs recebimentos")
        info_label.setStyleSheet("font-size: 10px; color: #666; padding: 5px;")
        layout.addWidget(info_label)

        # Table
        self.sintetica_table = QTableWidget()
        self.sintetica_table.setColumnCount(7)
        self.sintetica_table.setHorizontalHeaderLabels([
            'CPF/CNPJ', 'Nome', 'Qtd Notas', 'Total Emitido (R$)',
            'Total Recebido (R$)', 'Pendente (R$)', '% Markup'
        ])

        # Configure table
        header = self.sintetica_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.sintetica_table.setAlternatingRowColors(True)
        self.sintetica_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sintetica_table.setStyleSheet("""
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

        layout.addWidget(self.sintetica_table)

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
        self.invoices_df = invoices_df
        self.ofx_df = ofx_df
        self.refresh_analysis()

    def refresh_analysis(self):
        """Refresh analysis"""
        if self.invoices_df is None or self.invoices_df.empty:
            QMessageBox.warning(
                self,
                "Análise",
                "Nenhuma nota fiscal importada. Por favor, importe notas fiscais primeiro."
            )
            return

        # Generate summaries
        matcher = InvoiceMatcher()

        # Customer summary
        self.customer_summary_df = matcher.analyze_by_customer(self.invoices_df, self.ofx_df)
        self.update_sintetica_table()

        # Monthly summary
        self.monthly_summary_df = matcher.analyze_by_month(self.invoices_df, self.ofx_df)
        self.update_detalhada_table()

        self.update_status()

    def update_sintetica_table(self):
        """Update sintética table"""
        df = self.customer_summary_df

        if df is None or df.empty:
            self.sintetica_table.setRowCount(0)
            return

        self.sintetica_table.setRowCount(len(df))

        for row_idx, (idx, row) in enumerate(df.iterrows()):
            # CPF/CNPJ
            self.sintetica_table.setItem(row_idx, 0, QTableWidgetItem(row['cpf_cnpj_fmt']))

            # Nome
            self.sintetica_table.setItem(row_idx, 1, QTableWidgetItem(row['nome']))

            # Qtd Notas
            qtd_item = QTableWidgetItem(str(row['qtd_notas']))
            qtd_item.setTextAlignment(Qt.AlignCenter)
            self.sintetica_table.setItem(row_idx, 2, qtd_item)

            # Total Emitido
            emitido_item = QTableWidgetItem(f"R$ {row['total_emitido']:,.2f}")
            emitido_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sintetica_table.setItem(row_idx, 3, emitido_item)

            # Total Recebido
            recebido_item = QTableWidgetItem(f"R$ {row['total_recebido']:,.2f}")
            recebido_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sintetica_table.setItem(row_idx, 4, recebido_item)

            # Pendente
            pendente_item = QTableWidgetItem(f"R$ {row['total_pendente']:,.2f}")
            pendente_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Color code
            if row['total_pendente'] > 0:
                pendente_item.setBackground(QColor(255, 200, 200))
            else:
                pendente_item.setBackground(QColor(200, 255, 200))

            self.sintetica_table.setItem(row_idx, 5, pendente_item)

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

            self.sintetica_table.setItem(row_idx, 6, percent_item)

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
