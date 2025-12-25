"""
Analysis Tab - Gap Detection and Data Quality
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
                             QHeaderView, QPushButton, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.analyzer import DataAnalyzer


class GapCard(QFrame):
    """Card widget for displaying gap information"""

    def __init__(self, gap_info):
        super().__init__()
        self.gap_info = gap_info
        self.init_ui()

    def init_ui(self):
        # Determine severity color
        severity_colors = {
            'alta': '#F44336',    # Red
            'baixa': '#FF9800',   # Orange
        }
        color = severity_colors.get(self.gap_info.get('severidade', 'baixa'), '#FF9800')

        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 6px;
                border-left: 4px solid {color};
                padding: 10px;
                margin: 3px;
            }}
            QFrame:hover {{
                background-color: #FAFAFA;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(10, 8, 10, 8)

        # Header: Bank + Account
        header = QLabel(f"🏦 {self.gap_info['banco']} • Conta {self.gap_info['conta']}")
        header.setStyleSheet("font-size: 11px; font-weight: bold; color: #212121;")
        layout.addWidget(header)

        # Period
        period = QLabel(f"📅 {self.gap_info['mes_nome']}")
        period.setStyleSheet("font-size: 10px; color: #616161;")
        layout.addWidget(period)

        # Message
        msg = QLabel(self.gap_info['mensagem'])
        msg.setStyleSheet(f"font-size: 9px; color: {color}; font-weight: 600;")
        msg.setWordWrap(True)
        layout.addWidget(msg)

        self.setLayout(layout)


class AnalysisTab(QWidget):
    """Analysis tab with gap detection"""

    def __init__(self):
        super().__init__()
        self.df = None
        self.analyzer = None
        self.gaps = []
        self.duplicates = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setMaximumHeight(70)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #673AB7, stop:1 #512DA8);
                border-radius: 8px;
            }
        """)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("🔍 Análise de Gaps - Períodos Faltantes")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")

        subtitle = QLabel("Identifica meses sem movimentação por banco/conta")
        subtitle.setStyleSheet("color: #E1BEE7; font-size: 10px; background: transparent;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Summary cards
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(8)
        main_layout.addLayout(self.summary_layout)

        # Create placeholder summary
        self.create_placeholder_summary()

        # Filter section
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(10, 8, 10, 8)

        filter_label = QLabel("🔎 Filtrar:")
        filter_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #424242;")
        filter_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Todos os gaps", "all")
        self.filter_combo.addItem("⚠️ Apenas alta severidade", "high")
        self.filter_combo.addItem("⚡ Apenas baixa severidade", "low")
        self.filter_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 10px;
                min-width: 180px;
            }
        """)
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)

        filter_layout.addStretch()

        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #673AB7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 15px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5E35B1;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_analysis)
        filter_layout.addWidget(refresh_btn)

        filter_frame.setLayout(filter_layout)
        main_layout.addWidget(filter_frame)

        # Duplicates section
        self.duplicates_frame = QFrame()
        self.duplicates_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF3E0;
                border-radius: 6px;
                border-left: 4px solid #FF9800;
                padding: 10px;
            }
        """)
        self.duplicates_frame.setVisible(False)  # Hidden by default

        duplicates_main_layout = QVBoxLayout()
        duplicates_main_layout.setSpacing(8)
        duplicates_main_layout.setContentsMargins(10, 10, 10, 10)

        # Duplicates header
        dup_header = QHBoxLayout()
        dup_title = QLabel("🔄 Duplicatas Detectadas")
        dup_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #E65100; background: transparent;")
        dup_header.addWidget(dup_title)

        self.dup_count_label = QLabel("0 grupos")
        self.dup_count_label.setStyleSheet("font-size: 10px; color: #F57C00; background: transparent;")
        dup_header.addWidget(self.dup_count_label)
        dup_header.addStretch()

        duplicates_main_layout.addLayout(dup_header)

        # Duplicates list container (scrollable)
        dup_scroll = QScrollArea()
        dup_scroll.setWidgetResizable(True)
        dup_scroll.setMaximumHeight(200)
        dup_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.duplicates_container = QWidget()
        self.duplicates_layout = QVBoxLayout()
        self.duplicates_layout.setSpacing(4)
        self.duplicates_container.setLayout(self.duplicates_layout)

        dup_scroll.setWidget(self.duplicates_container)
        duplicates_main_layout.addWidget(dup_scroll)

        self.duplicates_frame.setLayout(duplicates_main_layout)
        main_layout.addWidget(self.duplicates_frame)

        # Gaps display area (scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.gaps_container = QWidget()
        self.gaps_layout = QVBoxLayout()
        self.gaps_layout.setSpacing(5)
        self.gaps_container.setLayout(self.gaps_layout)

        scroll_area.setWidget(self.gaps_container)
        main_layout.addWidget(scroll_area)

        # Placeholder message
        self.create_placeholder_message()

        self.setLayout(main_layout)

    def create_placeholder_summary(self):
        """Create placeholder summary cards"""
        cards_data = [
            ("📊", "Total de Gaps", "---", "#9C27B0"),
            ("⚠️", "Alta Severidade", "---", "#F44336"),
            ("⚡", "Baixa Severidade", "---", "#FF9800"),
            ("✅", "Cobertura", "---", "#4CAF50"),
        ]

        for icon, title, value, color in cards_data:
            card = self.create_summary_card(icon, title, value, color)
            self.summary_layout.addWidget(card)

    def create_summary_card(self, icon, title, value, color):
        """Create a summary card widget"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 6px;
                border-top: 3px solid {color};
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 9px; color: #757575; font-weight: 600; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; background: transparent;")
        value_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.setLayout(layout)
        return card

    def create_placeholder_message(self):
        """Show placeholder message when no data"""
        msg_frame = QFrame()
        msg_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 8px;
                padding: 30px;
            }
        """)

        msg_layout = QVBoxLayout()
        msg_layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("📂")
        icon.setStyleSheet("font-size: 48px; background: transparent;")
        icon.setAlignment(Qt.AlignCenter)

        text = QLabel("Importe arquivos OFX na aba Importar para ver a análise de gaps")
        text.setStyleSheet("font-size: 12px; color: #757575; background: transparent;")
        text.setAlignment(Qt.AlignCenter)

        msg_layout.addWidget(icon)
        msg_layout.addWidget(text)
        msg_frame.setLayout(msg_layout)

        self.gaps_layout.addWidget(msg_frame)

    def update_data(self, df, duplicates=None):
        """Update analysis with new data"""
        self.df = df
        self.duplicates = duplicates if duplicates else []

        if df is None or df.empty:
            return

        # Create analyzer
        self.analyzer = DataAnalyzer(df)

        # Detect gaps
        self.gaps = self.analyzer.detect_gaps()

        # Update display
        self.refresh_display()

    def refresh_analysis(self):
        """Refresh the analysis"""
        if self.df is not None:
            self.update_data(self.df)

    def refresh_display(self):
        """Refresh the gaps display"""
        # Update duplicates display
        self.update_duplicates_display()

        # Clear existing widgets
        for i in reversed(range(self.gaps_layout.count())):
            widget = self.gaps_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Update summary cards
        self.update_summary_cards()

        # Apply current filter
        self.apply_filter()

    def update_summary_cards(self):
        """Update summary statistics"""
        # Clear existing cards
        for i in reversed(range(self.summary_layout.count())):
            widget = self.summary_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Calculate stats
        total_gaps = len(self.gaps)
        high_severity = len([g for g in self.gaps if g.get('severidade') == 'alta'])
        low_severity = len([g for g in self.gaps if g.get('severidade') == 'baixa'])

        # Calculate coverage (percentage of months without gaps)
        if self.analyzer and not self.df.empty:
            # Get total expected months across all accounts
            total_expected = 0
            for (banco, conta), group in self.df.groupby(['banco', 'conta']):
                if 'data_dt' in group.columns:
                    group_valid = group.dropna(subset=['data_dt'])
                    if not group_valid.empty:
                        min_date = group_valid['data_dt'].min()
                        max_date = group_valid['data_dt'].max()
                        months_diff = ((max_date.year - min_date.year) * 12 +
                                     max_date.month - min_date.month + 1)
                        total_expected += months_diff

            if total_expected > 0:
                coverage = ((total_expected - total_gaps) / total_expected) * 100
                coverage_str = f"{coverage:.1f}%"
            else:
                coverage_str = "N/A"
        else:
            coverage_str = "N/A"

        # Create new cards
        cards_data = [
            ("📊", "Total de Gaps", str(total_gaps), "#9C27B0"),
            ("⚠️", "Alta Severidade", str(high_severity), "#F44336"),
            ("⚡", "Baixa Severidade", str(low_severity), "#FF9800"),
            ("✅", "Cobertura", coverage_str, "#4CAF50"),
        ]

        for icon, title, value, color in cards_data:
            card = self.create_summary_card(icon, title, value, color)
            self.summary_layout.addWidget(card)

    def apply_filter(self):
        """Apply selected filter to gaps"""
        # Clear gaps display
        for i in reversed(range(self.gaps_layout.count())):
            widget = self.gaps_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not self.gaps:
            self.create_placeholder_message()
            return

        # Get selected filter
        filter_type = self.filter_combo.currentData()

        # Filter gaps
        filtered_gaps = self.gaps
        if filter_type == 'high':
            filtered_gaps = [g for g in self.gaps if g.get('severidade') == 'alta']
        elif filter_type == 'low':
            filtered_gaps = [g for g in self.gaps if g.get('severidade') == 'baixa']

        if not filtered_gaps:
            no_results = QLabel("✨ Nenhum gap encontrado com esse filtro!")
            no_results.setStyleSheet("font-size: 12px; color: #4CAF50; padding: 20px;")
            no_results.setAlignment(Qt.AlignCenter)
            self.gaps_layout.addWidget(no_results)
            return

        # Group gaps by bank/account
        gaps_by_account = {}
        for gap in filtered_gaps:
            key = (gap['banco'], gap['conta'])
            if key not in gaps_by_account:
                gaps_by_account[key] = []
            gaps_by_account[key].append(gap)

        # Display gaps grouped by account
        for (banco, conta), account_gaps in sorted(gaps_by_account.items()):
            # Account header
            header = QFrame()
            header.setStyleSheet("""
                QFrame {
                    background-color: #EDE7F6;
                    border-radius: 4px;
                    padding: 8px;
                    margin-top: 5px;
                }
            """)
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(8, 5, 8, 5)

            header_label = QLabel(f"🏦 {banco} • Conta {conta}")
            header_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #4A148C; background: transparent;")

            count_label = QLabel(f"{len(account_gaps)} gap(s)")
            count_label.setStyleSheet("font-size: 10px; color: #7B1FA2; background: transparent;")

            header_layout.addWidget(header_label)
            header_layout.addStretch()
            header_layout.addWidget(count_label)

            header.setLayout(header_layout)
            self.gaps_layout.addWidget(header)

            # Gap cards for this account
            for gap in sorted(account_gaps, key=lambda x: (x['ano'], x['mes'])):
                gap_card = GapCard(gap)
                self.gaps_layout.addWidget(gap_card)

        # Add stretch at the end
        self.gaps_layout.addStretch()

    def update_duplicates_display(self):
        """Update duplicates display section"""
        # Clear existing widgets
        for i in reversed(range(self.duplicates_layout.count())):
            widget = self.duplicates_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Show/hide duplicates frame
        if not self.duplicates or len(self.duplicates) == 0:
            self.duplicates_frame.setVisible(False)
            return

        self.duplicates_frame.setVisible(True)
        self.dup_count_label.setText(f"{len(self.duplicates)} grupo(s) de duplicatas")

        # Display each duplicate group
        for dup_group in self.duplicates:
            # Create card for duplicate group
            dup_card = QFrame()
            dup_card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 4px;
                    padding: 8px;
                    margin: 2px;
                }
            """)

            card_layout = QVBoxLayout()
            card_layout.setSpacing(4)
            card_layout.setContentsMargins(8, 6, 8, 6)

            # Header
            header = QLabel(f"ID: {dup_group['id_transacao']} • {dup_group['banco']} • Conta {dup_group['conta']}")
            header.setStyleSheet("font-size: 10px; font-weight: bold; color: #E65100; background: transparent;")
            card_layout.addWidget(header)

            # Count
            count_label = QLabel(f"📊 {dup_group['count']} ocorrências encontradas (mantida apenas a primeira)")
            count_label.setStyleSheet("font-size: 9px; color: #666; background: transparent;")
            card_layout.addWidget(count_label)

            # Show all occurrences
            for i, occurrence in enumerate(dup_group['occurrences']):
                status = "✅ Mantida" if i == 0 else "🗑️ Removida"
                occ_label = QLabel(
                    f"{status}: {occurrence.get('data', 'N/A')} - "
                    f"R$ {occurrence.get('valor', 0):,.2f} - "
                    f"{occurrence.get('descricao', 'N/A')[:40]}... - "
                    f"Arquivo: {occurrence.get('arquivo_origem', 'N/A')}"
                )
                occ_label.setStyleSheet(f"font-size: 8px; color: {'#4CAF50' if i == 0 else '#999'}; background: transparent;")
                occ_label.setWordWrap(True)
                card_layout.addWidget(occ_label)

            dup_card.setLayout(card_layout)
            self.duplicates_layout.addWidget(dup_card)

        self.duplicates_layout.addStretch()
