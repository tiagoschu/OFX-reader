"""
Home Tab - Dashboard with overview
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.constants import APP_NAME, VERSION, AUTHOR, RELEASE_DATE
from core.transfer_detector import TransferDetector


class CompactStatCard(QFrame):
    """Compact stat card widget"""

    def __init__(self, icon, title, value, subtitle="", color="#1976D2"):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: none;
                border-left: 4px solid {color};
                padding: 12px;
                margin: 2px;
            }}
            QFrame:hover {{
                background-color: #F5F5F5;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        # Icon and title in same line
        header = QHBoxLayout()
        header.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px; background: transparent; border: none;")

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 11px; color: #757575; font-weight: 600; background: transparent; border: none;")

        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()

        layout.addLayout(header)

        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #212121; background: transparent; border: none;")
        layout.addWidget(value_label)

        # Subtitle if provided
        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setStyleSheet("font-size: 9px; color: #9E9E9E; background: transparent; border: none;")
            layout.addWidget(sub_label)

        self.setLayout(layout)


class HomeTab(QWidget):
    """Home/Dashboard tab"""

    def __init__(self):
        super().__init__()
        self.df = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Compact header
        header_frame = QFrame()
        header_frame.setMaximumHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976D2, stop:1 #1565C0);
                border-radius: 8px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Title section
        title_section = QVBoxLayout()
        title = QLabel(f"💰 {APP_NAME}")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: transparent;")

        info_text = QLabel(f"v{VERSION} • {AUTHOR} • {RELEASE_DATE}")
        info_text.setStyleSheet("color: #B3E5FC; font-size: 10px; background: transparent;")

        title_section.addWidget(title)
        title_section.addWidget(info_text)

        header_layout.addLayout(title_section)
        header_layout.addStretch()

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Stats grid - 2x4 layout (more compact)
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(8)
        main_layout.addLayout(self.stats_grid)

        # Create placeholder cards
        self.create_placeholder_cards()

        # Quick actions section
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        actions_layout = QVBoxLayout()

        quick_label = QLabel("🚀 Início Rápido")
        quick_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        actions_layout.addWidget(quick_label)

        steps = QLabel("""
        <div style='line-height: 1.4; font-size: 11px;'>
        <b>1.</b> Aba <b>Importar</b> → Adicionar arquivos OFX<br>
        <b>2.</b> Configurar opções → <b>Processar</b><br>
        <b>3.</b> Explorar análises e gráficos<br>
        <b>4.</b> Exportar dados no formato desejado
        </div>
        """)
        steps.setStyleSheet("color: #616161; background: transparent;")
        actions_layout.addWidget(steps)

        actions_frame.setLayout(actions_layout)
        main_layout.addWidget(actions_frame)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def create_placeholder_cards(self):
        """Create placeholder stat cards in compact 2x4 grid"""
        cards_data = [
            # Row 1
            ("💰", "Transações", "---", "", "#1976D2"),
            ("📈", "Receitas Reais", "R$ ---", "excluindo transferências", "#4CAF50"),
            ("📉", "Despesas Reais", "R$ ---", "excluindo transferências", "#F44336"),
            ("💵", "Saldo Líquido", "R$ ---", "receitas - despesas", "#9C27B0"),
            # Row 2
            ("🔄", "Transferências", "R$ ---", "entre suas contas", "#FF9800"),
            ("🏦", "Bancos", "---", "", "#00BCD4"),
            ("📊", "Contas", "---", "", "#E91E63"),
            ("📅", "Período", "---", "", "#607D8B"),
        ]

        for i, (icon, title, value, subtitle, color) in enumerate(cards_data):
            card = CompactStatCard(icon, title, value, subtitle, color)
            self.stats_grid.addWidget(card, i // 4, i % 4)

    def update_stats(self, df):
        """Update statistics with real data"""
        self.df = df

        if df is None or df.empty:
            return

        # Clear existing cards
        for i in reversed(range(self.stats_grid.count())):
            self.stats_grid.itemAt(i).widget().setParent(None)

        # Use proper transfer pair detection
        detector = TransferDetector(tolerance=1.0)
        df = detector.detect_transfer_pairs(df)
        df = detector.detect_unpaired_transfers(df)

        # Calculate stats excluding PAIRED internal transfers only
        df_credits = df[(df['valor'] > 0) & (~df.get('is_internal_transfer', False))]
        df_debits = df[(df['valor'] < 0) & (~df.get('is_internal_transfer', False))]
        df_transfers = df[df.get('is_internal_transfer', False)]

        total_trans = len(df)
        real_credits = df_credits['valor'].sum()
        real_debits = df_debits['valor'].sum()

        # For transfers, count each pair once (sum and divide by 2)
        transfers_total = df_transfers['valor'].abs().sum() / 2 if not df_transfers.empty else 0

        balance = real_credits + real_debits  # Debits are already negative

        num_banks = df['banco'].nunique()
        num_accounts = df['conta'].nunique()

        # Debug: Show banco/conta info
        print("\n" + "=" * 60)
        print("DEBUG: BANCOS E CONTAS")
        print("=" * 60)
        print(f"Bancos únicos ({num_banks}):")
        for banco in sorted(df['banco'].unique()):
            count = len(df[df['banco'] == banco])
            print(f"  • {banco} ({count} trans.)")

        print(f"\nContas únicas ({num_accounts}):")
        for conta in sorted(df['conta'].unique()):
            banco = df[df['conta'] == conta]['banco'].iloc[0]
            count = len(df[df['conta'] == conta])
            print(f"  • {conta} ({banco}) - {count} trans.")

        print("\nCombinações Banco+Conta:")
        for banco in sorted(df['banco'].unique()):
            contas = df[df['banco'] == banco]['conta'].unique()
            print(f"  • {banco}: {len(contas)} conta(s)")
            for conta in contas:
                print(f"      - {conta}")
        print("=" * 60 + "\n")

        # Date range
        if 'data' in df.columns:
            dates = df['data'].dropna()
            if len(dates) > 0:
                period = f"{dates.iloc[0]} a {dates.iloc[-1]}"
            else:
                period = "---"
        else:
            period = "---"

        # Get transfer summary
        transfer_summary = detector.get_transfer_summary(df)
        num_pairs = transfer_summary.get('total_transfer_pairs', 0)
        num_unpaired = transfer_summary.get('total_unpaired_possible', 0)

        # Build transfer subtitle
        transfer_subtitle = f"{num_pairs} pares detectados"
        if num_unpaired > 0:
            transfer_subtitle += f", {num_unpaired} para revisão"

        # Create cards with real data
        cards_data = [
            ("💰", "Transações", f"{total_trans:,}", "", "#1976D2"),
            ("📈", "Receitas Reais", f"R$ {real_credits:,.2f}", "excluindo transferências", "#4CAF50"),
            ("📉", "Despesas Reais", f"R$ {abs(real_debits):,.2f}", "excluindo transferências", "#F44336"),
            ("💵", "Saldo Líquido", f"R$ {balance:,.2f}", "receitas - despesas", "#9C27B0"),
            ("🔄", "Transferências", f"R$ {transfers_total:,.2f}", transfer_subtitle, "#FF9800"),
            ("🏦", "Bancos", str(num_banks), "", "#00BCD4"),
            ("📊", "Contas", str(num_accounts), "", "#E91E63"),
            ("📅", "Período", period, "", "#607D8B"),
        ]

        for i, (icon, title, value, subtitle, color) in enumerate(cards_data):
            card = CompactStatCard(icon, title, value, subtitle, color)
            self.stats_grid.addWidget(card, i // 4, i % 4)
