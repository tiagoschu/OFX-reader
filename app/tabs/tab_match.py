"""
Match Tab - Central hub for all matching operations
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox, QTextEdit, QProgressBar,
                             QSplitter, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QFont, QTextCursor
import pandas as pd
from datetime import datetime
from core.invoice_matcher import InvoiceMatcher
from core.credit_card_matcher import CreditCardMatcher


class MatchWorker(QThread):
    """Worker thread for matching operations"""
    progress = pyqtSignal(str)  # Log message
    finished = pyqtSignal(dict)  # Results
    data_updated = pyqtSignal(str, object)  # (data_type, dataframe) - notify when data changes

    def __init__(self, operation, data):
        super().__init__()
        self.operation = operation
        self.data = data

    def run(self):
        """Execute matching operation"""
        try:
            if self.operation == 'ofx_nfse':
                result = self.match_ofx_nfse()
            elif self.operation == 'ofx_cartao':
                result = self.match_ofx_cartao()
            elif self.operation == 'nfse_cartao':
                result = self.match_nfse_cartao()
            elif self.operation == 'all':
                result = self.match_all()
            else:
                result = {'success': False, 'error': 'Unknown operation'}

            self.finished.emit(result)
        except Exception as e:
            import traceback
            error_msg = f"Erro: {str(e)}\n{traceback.format_exc()}"
            self.progress.emit(f"❌ {error_msg}")
            self.finished.emit({'success': False, 'error': str(e)})

    def match_ofx_nfse(self):
        """Match OFX with NFSe invoices"""
        self.progress.emit("🔄 Iniciando vinculação OFX ↔ NFSe...")

        invoices_df = self.data.get('invoices_df')
        ofx_df = self.data.get('ofx_df')

        if invoices_df is None or invoices_df.empty:
            self.progress.emit("⚠️ Nenhuma nota fiscal importada")
            return {'success': False, 'error': 'No invoices'}

        if ofx_df is None or ofx_df.empty:
            self.progress.emit("⚠️ Nenhuma transação OFX importada")
            return {'success': False, 'error': 'No OFX data'}

        # Use agency mode by default (CPF + Date, ignore value difference)
        self.progress.emit("  📋 Configurações: Modo Agência (CPF + Data)")
        self.progress.emit("  📅 Tolerância: ±35 dias")

        matcher = InvoiceMatcher(
            tolerance_days=35,
            tolerance_percent=0.0,  # Ignored in agency mode
            mode='agency'
        )

        self.progress.emit(f"  🔍 Analisando {len(invoices_df)} notas contra {len(ofx_df[ofx_df['valor'] > 0])} créditos OFX...")

        invoices, matches, summary = matcher.match(invoices_df, ofx_df)

        # Emit updated invoices data
        self.data_updated.emit('invoices', invoices)

        matched = summary.get('matched', 0)
        total = summary.get('total_invoices', 0)
        matched_value = summary.get('matched_value', 0)

        self.progress.emit(f"  ✅ Vinculadas: {matched} de {total} notas")
        self.progress.emit(f"  💰 Valor vinculado: R$ {matched_value:,.2f}")

        return {
            'success': True,
            'matched': matched,
            'total': total,
            'matched_value': matched_value,
            'summary': summary
        }

    def match_ofx_cartao(self):
        """Match OFX with credit card installments"""
        self.progress.emit("🔄 Iniciando vinculação OFX ↔ Cartão...")

        installments_df = self.data.get('installments_df')
        ofx_df = self.data.get('ofx_df')

        if installments_df is None or installments_df.empty:
            self.progress.emit("⚠️ Nenhuma parcela de cartão importada")
            return {'success': False, 'error': 'No installments'}

        if ofx_df is None or ofx_df.empty:
            self.progress.emit("⚠️ Nenhuma transação OFX importada")
            return {'success': False, 'error': 'No OFX data'}

        self.progress.emit("  📋 Configurações: ±5 dias, ±10% valor")

        matcher = CreditCardMatcher(
            date_tolerance_days=5,
            value_tolerance=0.10
        )

        self.progress.emit(f"  🔍 Analisando {len(installments_df)} parcelas contra OFX...")

        installments, matches, summary = matcher.match(installments_df, ofx_df)

        # Emit updated installments data
        self.data_updated.emit('installments', installments)

        matched = summary.get('vinculadas', 0)
        total = summary.get('total_parcelas', 0)

        self.progress.emit(f"  ✅ Vinculadas: {matched} de {total} parcelas")

        return {
            'success': True,
            'matched': matched,
            'total': total,
            'summary': summary
        }

    def match_nfse_cartao(self):
        """Match NFSe with credit card sales"""
        self.progress.emit("🔄 Iniciando vinculação NFSe ↔ Cartão...")
        self.progress.emit("  ℹ️ Esta vinculação será implementada em versão futura")
        self.progress.emit("  💡 Por enquanto, use OFX como ponte entre NFSe e Cartão")

        return {
            'success': True,
            'matched': 0,
            'total': 0,
            'note': 'Not yet implemented'
        }

    def match_all(self):
        """Run all matching operations in sequence"""
        self.progress.emit("=" * 60)
        self.progress.emit("🚀 VINCULAÇÃO AUTOMÁTICA COMPLETA")
        self.progress.emit("=" * 60)
        self.progress.emit("")

        results = {}

        # 1. OFX <-> NFSe
        self.progress.emit("ETAPA 1/3: OFX ↔ NFSe")
        self.progress.emit("-" * 60)
        results['ofx_nfse'] = self.match_ofx_nfse()
        self.progress.emit("")

        # 2. OFX <-> Cartão
        self.progress.emit("ETAPA 2/3: OFX ↔ Cartão")
        self.progress.emit("-" * 60)
        results['ofx_cartao'] = self.match_ofx_cartao()
        self.progress.emit("")

        # 3. NFSe <-> Cartão (future)
        self.progress.emit("ETAPA 3/3: NFSe ↔ Cartão")
        self.progress.emit("-" * 60)
        results['nfse_cartao'] = self.match_nfse_cartao()
        self.progress.emit("")

        self.progress.emit("=" * 60)
        self.progress.emit("✅ VINCULAÇÃO COMPLETA FINALIZADA!")
        self.progress.emit("=" * 60)

        return {'success': True, 'results': results}


class MatchTab(QWidget):
    """Tab for centralized matching operations"""

    # Signals to notify other tabs
    match_completed = pyqtSignal(str)  # match_type
    invoices_updated = pyqtSignal(object)  # Updated invoices DataFrame
    installments_updated = pyqtSignal(object)  # Updated installments DataFrame

    def __init__(self):
        super().__init__()
        self.ofx_df = None
        self.invoices_df = None
        self.installments_df = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = self._create_header()
        main_layout.addWidget(header_frame)

        # Splitter: Controls on left, Log on right
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Matching controls
        controls_widget = self._create_controls()
        splitter.addWidget(controls_widget)

        # Right side: Log
        log_widget = self._create_log()
        splitter.addWidget(log_widget)

        # Set initial sizes (40% controls, 60% log)
        splitter.setSizes([400, 600])

        main_layout.addWidget(splitter)

        # Progress bar at bottom
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)

    def _create_header(self):
        """Create header section"""
        header_frame = QWidget()
        header_frame.setMaximumHeight(90)
        header_frame.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976D2, stop:1 #1565C0);
                border-radius: 8px;
            }
        """)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("🔗 Vincular Transações")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent;")

        subtitle = QLabel("Central de vinculação automática: OFX ↔ NFSe ↔ Cartão")
        subtitle.setStyleSheet("color: #BBDEFB; font-size: 11px; background: transparent;")

        info = QLabel("💡 Vincule seus dados em 3 passos ou use 'Vincular Tudo' para automação completa")
        info.setStyleSheet("color: #E3F2FD; font-size: 10px; background: transparent; margin-top: 5px;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(info)
        header_frame.setLayout(header_layout)

        return header_frame

    def _create_controls(self):
        """Create matching controls section"""
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)

        # Data status
        status_group = self._create_status_group()
        controls_layout.addWidget(status_group)

        # Individual matching operations
        operations_group = self._create_operations_group()
        controls_layout.addWidget(operations_group)

        # Master control
        master_group = self._create_master_group()
        controls_layout.addWidget(master_group)

        controls_layout.addStretch()
        controls_widget.setLayout(controls_layout)

        return controls_widget

    def _create_status_group(self):
        """Create data status group"""
        group = QGroupBox("📊 Status dos Dados")
        layout = QVBoxLayout()

        self.ofx_status = QLabel("📥 OFX: Nenhum arquivo carregado")
        self.ofx_status.setStyleSheet("padding: 5px; color: #666; font-size: 10px;")

        self.nfse_status = QLabel("📄 NFSe: Nenhum arquivo carregado")
        self.nfse_status.setStyleSheet("padding: 5px; color: #666; font-size: 10px;")

        self.cartao_status = QLabel("💳 Cartão: Nenhum arquivo carregado")
        self.cartao_status.setStyleSheet("padding: 5px; color: #666; font-size: 10px;")

        layout.addWidget(self.ofx_status)
        layout.addWidget(self.nfse_status)
        layout.addWidget(self.cartao_status)

        group.setLayout(layout)
        return group

    def _create_operations_group(self):
        """Create individual operations group"""
        group = QGroupBox("🔧 Vinculações Individuais")
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Operation 1: OFX <-> NFSe
        op1_layout = QHBoxLayout()
        op1_label = QLabel("1️⃣ OFX ↔ NFSe")
        op1_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.btn_match_ofx_nfse = QPushButton("Vincular OFX com Notas")
        self.btn_match_ofx_nfse.setStyleSheet(self._get_button_style("#00897B"))
        self.btn_match_ofx_nfse.clicked.connect(lambda: self.start_matching('ofx_nfse'))
        op1_layout.addWidget(op1_label)
        op1_layout.addWidget(self.btn_match_ofx_nfse)
        layout.addLayout(op1_layout)

        # Operation 2: OFX <-> Cartão
        op2_layout = QHBoxLayout()
        op2_label = QLabel("2️⃣ OFX ↔ Cartão")
        op2_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.btn_match_ofx_cartao = QPushButton("Vincular OFX com Parcelas")
        self.btn_match_ofx_cartao.setStyleSheet(self._get_button_style("#1976D2"))
        self.btn_match_ofx_cartao.clicked.connect(lambda: self.start_matching('ofx_cartao'))
        op2_layout.addWidget(op2_label)
        op2_layout.addWidget(self.btn_match_ofx_cartao)
        layout.addLayout(op2_layout)

        # Operation 3: NFSe <-> Cartão
        op3_layout = QHBoxLayout()
        op3_label = QLabel("3️⃣ NFSe ↔ Cartão")
        op3_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.btn_match_nfse_cartao = QPushButton("Vincular Notas com Vendas")
        self.btn_match_nfse_cartao.setStyleSheet(self._get_button_style("#F57C00"))
        self.btn_match_nfse_cartao.clicked.connect(lambda: self.start_matching('nfse_cartao'))
        op3_layout.addWidget(op3_label)
        op3_layout.addWidget(self.btn_match_nfse_cartao)
        layout.addLayout(op3_layout)

        group.setLayout(layout)
        return group

    def _create_master_group(self):
        """Create master control group"""
        group = QGroupBox("⚡ Automação Completa")
        layout = QVBoxLayout()

        info = QLabel("Executa todas as vinculações em sequência:")
        info.setStyleSheet("font-size: 10px; color: #666; margin-bottom: 5px;")
        layout.addWidget(info)

        steps = QLabel("  1. OFX ↔ NFSe\n  2. OFX ↔ Cartão\n  3. NFSe ↔ Cartão")
        steps.setStyleSheet("font-size: 9px; color: #888; margin-bottom: 10px;")
        layout.addWidget(steps)

        self.btn_match_all = QPushButton("🚀 VINCULAR TUDO")
        self.btn_match_all.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C62828;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.btn_match_all.clicked.connect(lambda: self.start_matching('all'))
        layout.addWidget(self.btn_match_all)

        group.setLayout(layout)
        return group

    def _create_log(self):
        """Create log section"""
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)

        log_header = QLabel("📋 Log de Vinculação")
        log_header.setStyleSheet("font-weight: bold; font-size: 11px; padding: 5px;")
        log_layout.addWidget(log_header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10px;
                border: 1px solid #424242;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Sistema iniciado - aguardando operações...\n")
        log_layout.addWidget(self.log_text)

        log_widget.setLayout(log_layout)
        return log_widget

    def _get_button_style(self, color):
        """Get button stylesheet"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
                color: #757575;
            }}
        """

    def _darken_color(self, hex_color):
        """Darken a hex color by 10%"""
        # Simple darkening - subtract from each RGB component
        return hex_color  # Simplified for now

    def set_data(self, ofx_df=None, invoices_df=None, installments_df=None):
        """Set data from other tabs"""
        if ofx_df is not None:
            self.ofx_df = ofx_df
            count = len(ofx_df)
            self.ofx_status.setText(f"📥 OFX: {count} transações carregadas ✓")
            self.ofx_status.setStyleSheet("padding: 5px; color: #00897B; font-size: 10px; font-weight: bold;")

        if invoices_df is not None:
            self.invoices_df = invoices_df
            count = len(invoices_df)
            self.nfse_status.setText(f"📄 NFSe: {count} notas carregadas ✓")
            self.nfse_status.setStyleSheet("padding: 5px; color: #00897B; font-size: 10px; font-weight: bold;")

        if installments_df is not None:
            self.installments_df = installments_df
            count = len(installments_df)
            self.cartao_status.setText(f"💳 Cartão: {count} parcelas carregadas ✓")
            self.cartao_status.setStyleSheet("padding: 5px; color: #00897B; font-size: 10px; font-weight: bold;")

        # Enable/disable buttons based on available data
        self.update_button_states()

    def update_button_states(self):
        """Enable/disable buttons based on available data"""
        has_ofx = self.ofx_df is not None and not self.ofx_df.empty
        has_nfse = self.invoices_df is not None and not self.invoices_df.empty
        has_cartao = self.installments_df is not None and not self.installments_df.empty

        self.btn_match_ofx_nfse.setEnabled(has_ofx and has_nfse)
        self.btn_match_ofx_cartao.setEnabled(has_ofx and has_cartao)
        self.btn_match_nfse_cartao.setEnabled(has_nfse and has_cartao)
        self.btn_match_all.setEnabled(has_ofx and has_nfse and has_cartao)

    def start_matching(self, operation):
        """Start matching operation"""
        self.log(f"\n{'='*60}")
        self.log(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando: {operation}")
        self.log(f"{'='*60}\n")

        # Disable buttons during operation
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        # Create and start worker
        self.worker = MatchWorker(operation, {
            'ofx_df': self.ofx_df,
            'invoices_df': self.invoices_df,
            'installments_df': self.installments_df
        })
        self.worker.progress.connect(self.log)
        self.worker.data_updated.connect(self.on_data_updated)
        self.worker.finished.connect(self.on_matching_finished)
        self.worker.start()

    def on_data_updated(self, data_type, dataframe):
        """Handle data updates from worker"""
        if data_type == 'invoices':
            self.invoices_df = dataframe
            self.invoices_updated.emit(dataframe)
            self.log(f"  📤 Dados de notas atualizados ({len(dataframe)} registros)")
        elif data_type == 'installments':
            self.installments_df = dataframe
            self.installments_updated.emit(dataframe)
            self.log(f"  📤 Dados de parcelas atualizados ({len(dataframe)} registros)")

    def on_matching_finished(self, result):
        """Handle matching completion"""
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)

        if result.get('success'):
            self.log(f"\n✅ Operação concluída com sucesso!")

            # Emit match_completed signal
            # This will trigger updates in other tabs
            self.match_completed.emit('completed')
        else:
            self.log(f"\n❌ Erro: {result.get('error', 'Unknown error')}")

        self.log(f"{'='*60}\n")

    def log(self, message):
        """Add message to log"""
        self.log_text.append(message)
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

    def set_buttons_enabled(self, enabled):
        """Enable/disable all buttons"""
        self.btn_match_ofx_nfse.setEnabled(enabled)
        self.btn_match_ofx_cartao.setEnabled(enabled)
        self.btn_match_nfse_cartao.setEnabled(enabled)
        self.btn_match_all.setEnabled(enabled)

        if enabled:
            self.update_button_states()
