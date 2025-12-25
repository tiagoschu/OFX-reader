"""
Home Tab - Dashboard with overview
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.constants import APP_NAME, VERSION, AUTHOR, RELEASE_DATE


class StatCard(QFrame):
    """Stat card widget"""

    def __init__(self, title, value, icon="", color="#1976D2"):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout()

        # Icon and title
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #757575; font-weight: bold;")

        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()

        layout.addLayout(header)

        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #212121;")
        layout.addWidget(value_label)

        self.setLayout(layout)


class HomeTab(QWidget):
    """Home/Dashboard tab"""

    def __init__(self):
        super().__init__()
        self.df = None
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # Welcome section
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border-radius: 10px;
                padding: 30px;
            }
        """)
        welcome_layout = QVBoxLayout()

        title = QLabel(f"Bem-vindo ao {APP_NAME}")
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        welcome_layout.addWidget(title)

        subtitle = QLabel("Análise Inteligente de Extratos Bancários")
        subtitle.setStyleSheet("color: #B3E5FC; font-size: 16px;")
        welcome_layout.addWidget(subtitle)

        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"📌 Versão {VERSION}"))
        info_layout.addWidget(QLabel(f"👤 {AUTHOR}"))
        info_layout.addWidget(QLabel(f"📅 {RELEASE_DATE}"))
        info_layout.addStretch()

        for label in info_layout.findChildren(QLabel):
            label.setStyleSheet("color: white; font-size: 12px;")

        welcome_layout.addLayout(info_layout)
        welcome_frame.setLayout(welcome_layout)
        content_layout.addWidget(welcome_frame)

        # Stats section
        stats_label = QLabel("📊 Visão Geral")
        stats_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        content_layout.addWidget(stats_label)

        # Stats cards
        self.stats_grid = QGridLayout()
        content_layout.addLayout(self.stats_grid)

        # Create placeholder cards
        self.create_placeholder_cards()

        # Quick start section
        quick_start_label = QLabel("🚀 Início Rápido")
        quick_start_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        content_layout.addWidget(quick_start_label)

        instructions = QLabel("""
        <p><b>1.</b> Vá para a aba <b>Importar</b> e adicione seus arquivos OFX</p>
        <p><b>2.</b> Configure as opções de processamento</p>
        <p><b>3.</b> Clique em <b>Processar Arquivos</b></p>
        <p><b>4.</b> Explore as análises e gráficos nas outras abas</p>
        <p><b>5.</b> Exporte seus dados no formato desejado</p>
        """)
        instructions.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        instructions.setWordWrap(True)
        content_layout.addWidget(instructions)

        content_layout.addStretch()

        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)

        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def create_placeholder_cards(self):
        """Create placeholder stat cards"""
        cards_data = [
            ("💰 Total de Transações", "---", "#1976D2"),
            ("📈 Créditos", "R$ ---", "#4CAF50"),
            ("📉 Débitos", "R$ ---", "#F44336"),
            ("💵 Saldo Líquido", "R$ ---", "#9C27B0"),
        ]

        for i, (title, value, color) in enumerate(cards_data):
            card = StatCard(title, value, "", color)
            self.stats_grid.addWidget(card, i // 2, i % 2)

    def update_stats(self, df):
        """Update statistics with real data"""
        self.df = df

        if df is None or df.empty:
            return

        # Clear existing cards
        for i in reversed(range(self.stats_grid.count())):
            self.stats_grid.itemAt(i).widget().setParent(None)

        # Calculate stats
        total_trans = len(df)
        total_credits = df[df['valor'] > 0]['valor'].sum()
        total_debits = df[df['valor'] < 0]['valor'].sum()
        balance = df['valor'].sum()

        # Create new cards with real data
        cards_data = [
            ("💰 Total de Transações", str(total_trans), "#1976D2"),
            ("📈 Créditos", f"R$ {total_credits:,.2f}", "#4CAF50"),
            ("📉 Débitos", f"R$ {total_debits:,.2f}", "#F44336"),
            ("💵 Saldo Líquido", f"R$ {balance:,.2f}", "#9C27B0"),
        ]

        for i, (title, value, color) in enumerate(cards_data):
            card = StatCard(title, value, "", color)
            self.stats_grid.addWidget(card, i // 2, i % 2)
