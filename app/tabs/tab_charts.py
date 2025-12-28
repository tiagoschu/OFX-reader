"""
Charts Tab - Static visualizations with Matplotlib
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QComboBox, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys
import os
import pandas as pd
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartWidget(QFrame):
    """Widget to display a Matplotlib chart as an image"""

    def __init__(self, title=""):
        super().__init__()
        self.title = title
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #212121; background: transparent;")
            layout.addWidget(title_label)

        # Image label for displaying chart
        self.image_label = QLabel()
        self.image_label.setMinimumHeight(350)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: transparent;")
        self.image_label.setScaledContents(False)

        layout.addWidget(self.image_label)

        self.setLayout(layout)

    def set_chart(self, fig):
        """Convert matplotlib figure to QPixmap and display"""
        try:
            # Convert figure to PNG in memory
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
            buf.seek(0)

            # Load into QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())

            # Scale to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)

            # Close the figure to free memory
            plt.close(fig)

        except Exception as e:
            print(f"[CHARTS] ERROR rendering chart '{self.title}': {str(e)}")
            import traceback
            traceback.print_exc()
            self.show_message(f"Erro ao renderizar gráfico: {str(e)}")

    def show_message(self, message):
        """Show a message instead of chart"""
        self.image_label.setText(f"📊\n{message}")
        self.image_label.setStyleSheet("color: #757575; font-size: 14px; background: transparent;")


class ChartsTab(QWidget):
    """Charts tab with Matplotlib visualizations"""

    def __init__(self):
        super().__init__()
        self.df = None
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
                    stop:0 #00897B, stop:1 #00695C);
                border-radius: 8px;
            }
        """)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("📈 Gráficos")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")

        subtitle = QLabel("Visualizações dos seus dados financeiros")
        subtitle.setStyleSheet("color: #B2DFDB; font-size: 10px; background: transparent;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Check if Matplotlib is available
        if not MATPLOTLIB_AVAILABLE:
            error_label = QLabel("⚠️ Matplotlib não instalado. Execute: pip install matplotlib")
            error_label.setStyleSheet("color: #F44336; font-size: 12px; padding: 20px;")
            error_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(error_label)
            self.setLayout(main_layout)
            return

        # Controls
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 5, 10, 5)

        controls_label = QLabel("📊 Visualizar:")
        controls_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #424242;")
        controls_layout.addWidget(controls_label)

        self.chart_selector = QComboBox()
        self.chart_selector.addItem("Todas as Visualizações", "all")
        self.chart_selector.addItem("📈 Evolução Temporal", "timeline")
        self.chart_selector.addItem("🥧 Distribuição por Categoria", "categories")
        self.chart_selector.addItem("🏦 Comparação entre Bancos", "banks")
        self.chart_selector.addItem("📊 Evolução Mensal", "monthly")
        self.chart_selector.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 10px;
                min-width: 200px;
            }
        """)
        self.chart_selector.currentIndexChanged.connect(self.update_charts_display)
        controls_layout.addWidget(self.chart_selector)

        controls_layout.addStretch()

        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #00897B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 15px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_charts)
        controls_layout.addWidget(refresh_btn)

        controls_frame.setLayout(controls_layout)
        main_layout.addWidget(controls_frame)

        # Charts area (scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.charts_container = QWidget()
        self.charts_layout = QVBoxLayout()
        self.charts_layout.setSpacing(10)
        self.charts_container.setLayout(self.charts_layout)

        scroll_area.setWidget(self.charts_container)
        main_layout.addWidget(scroll_area)

        # Create chart widgets
        self.chart_timeline = ChartWidget("📈 Evolução Temporal - Receitas vs Despesas")
        self.chart_categories = ChartWidget("🥧 Distribuição por Categoria")
        self.chart_banks = ChartWidget("🏦 Comparação entre Bancos")
        self.chart_monthly = ChartWidget("📊 Evolução Mensal - Balanço")

        # Show placeholder
        self.show_placeholder()

        self.setLayout(main_layout)

    def show_placeholder(self):
        """Show placeholder when no data"""
        for i in reversed(range(self.charts_layout.count())):
            widget = self.charts_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        placeholder = QLabel("📂 Importe arquivos OFX na aba Importar para ver os gráficos")
        placeholder.setStyleSheet("font-size: 12px; color: #757575; padding: 40px;")
        placeholder.setAlignment(Qt.AlignCenter)
        self.charts_layout.addWidget(placeholder)

    def update_data(self, df):
        """Update charts with new data"""
        self.df = df

        if df is None or df.empty:
            self.show_placeholder()
            return

        # Generate all charts
        self.generate_charts()
        self.update_charts_display()

    def refresh_charts(self):
        """Refresh charts"""
        if self.df is not None and not self.df.empty:
            self.generate_charts()
            self.update_charts_display()

    def generate_charts(self):
        """Generate all chart visualizations"""
        if self.df is None or self.df.empty:
            return

        # 1. Timeline chart
        self.generate_timeline_chart()

        # 2. Categories pie chart
        self.generate_categories_chart()

        # 3. Banks comparison
        self.generate_banks_chart()

        # 4. Monthly evolution
        self.generate_monthly_chart()

    def generate_timeline_chart(self):
        """Generate timeline evolution chart"""
        try:
            df = self.df.copy()

            # Ensure we have datetime
            if 'data_dt' not in df.columns:
                df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')

            df = df.dropna(subset=['data_dt'])

            if df.empty:
                self.chart_timeline.show_message("Sem dados de data válidos")
                return

            # Group by date
            df['date_only'] = df['data_dt'].dt.date
            daily_credits = df[df['valor'] > 0].groupby('date_only')['valor'].sum()
            daily_debits = df[df['valor'] < 0].groupby('date_only')['valor'].sum().abs()

            # Get all dates
            all_dates = sorted(df['date_only'].unique())
            credits = [daily_credits.get(d, 0) for d in all_dates]
            debits = [daily_debits.get(d, 0) for d in all_dates]

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 5))

            ax.plot(all_dates, credits, color='#4CAF50', linewidth=2, marker='o',
                   markersize=4, label='Receitas', alpha=0.8)
            ax.fill_between(all_dates, credits, alpha=0.2, color='#4CAF50')

            ax.plot(all_dates, debits, color='#F44336', linewidth=2, marker='o',
                   markersize=4, label='Despesas', alpha=0.8)
            ax.fill_between(all_dates, debits, alpha=0.2, color='#F44336')

            ax.set_xlabel('Data', fontsize=10)
            ax.set_ylabel('Valor (R$)', fontsize=10)
            ax.legend(loc='upper left', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(labelsize=9)

            # Format x-axis dates
            if len(all_dates) > 20:
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.tick_params(axis='x', rotation=45)

            fig.tight_layout()

            self.chart_timeline.set_chart(fig)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.chart_timeline.show_message(f"Erro ao gerar gráfico: {str(e)}")

    def generate_categories_chart(self):
        """Generate categories distribution pie chart"""
        try:
            df = self.df.copy()

            if 'categoria' not in df.columns:
                self.chart_categories.show_message("Categorias não disponíveis")
                return

            # Group by category (only expenses)
            expenses = df[df['valor'] < 0].copy()
            expenses['valor_abs'] = expenses['valor'].abs()

            cat_summary = expenses.groupby('categoria')['valor_abs'].sum().sort_values(ascending=False)

            if cat_summary.empty:
                self.chart_categories.show_message("Sem despesas categorizadas")
                return

            # Limit to top 10 categories, group rest as "Outros"
            if len(cat_summary) > 10:
                top_10 = cat_summary.head(10)
                outros = cat_summary.iloc[10:].sum()
                cat_summary = pd.concat([top_10, pd.Series({'Outros': outros})])

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))

            # Generate colors
            colors = plt.cm.Set3(range(len(cat_summary)))

            wedges, texts, autotexts = ax.pie(
                cat_summary.values,
                labels=cat_summary.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops={'fontsize': 9}
            )

            # Make percentage text bold
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
                autotext.set_fontsize(8)

            ax.axis('equal')
            fig.tight_layout()

            self.chart_categories.set_chart(fig)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.chart_categories.show_message(f"Erro ao gerar gráfico: {str(e)}")

    def generate_banks_chart(self):
        """Generate banks comparison bar chart"""
        try:
            df = self.df.copy()

            # Group by bank
            banks_credits = df[df['valor'] > 0].groupby('banco')['valor'].sum()
            banks_debits = df[df['valor'] < 0].groupby('banco')['valor'].sum().abs()

            # Get all banks
            all_banks = sorted(set(banks_credits.index) | set(banks_debits.index))

            credits = [banks_credits.get(b, 0) for b in all_banks]
            debits = [banks_debits.get(b, 0) for b in all_banks]

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))

            x = range(len(all_banks))
            width = 0.35

            ax.barh([i - width/2 for i in x], credits, width, label='Receitas', color='#4CAF50', alpha=0.8)
            ax.barh([i + width/2 for i in x], debits, width, label='Despesas', color='#F44336', alpha=0.8)

            ax.set_yticks(x)
            ax.set_yticklabels(all_banks, fontsize=9)
            ax.set_xlabel('Valor (R$)', fontsize=10)
            ax.legend(loc='best', fontsize=9)
            ax.grid(True, alpha=0.3, axis='x', linestyle='--')
            ax.tick_params(labelsize=9)

            fig.tight_layout()

            self.chart_banks.set_chart(fig)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.chart_banks.show_message(f"Erro ao gerar gráfico: {str(e)}")

    def generate_monthly_chart(self):
        """Generate monthly balance evolution"""
        try:
            df = self.df.copy()

            # Ensure datetime
            if 'data_dt' not in df.columns:
                df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')

            df = df.dropna(subset=['data_dt'])

            if df.empty:
                self.chart_monthly.show_message("Sem dados de data válidos")
                return

            # Group by month
            df['year_month'] = df['data_dt'].dt.to_period('M')

            monthly_credits = df[df['valor'] > 0].groupby('year_month')['valor'].sum()
            monthly_debits = df[df['valor'] < 0].groupby('year_month')['valor'].sum().abs()
            monthly_balance = df.groupby('year_month')['valor'].sum()

            # Get all months
            all_months = sorted(set(monthly_credits.index) | set(monthly_debits.index))
            month_labels = [str(m) for m in all_months]

            credits = [monthly_credits.get(m, 0) for m in all_months]
            debits = [monthly_debits.get(m, 0) for m in all_months]
            balance = [monthly_balance.get(m, 0) for m in all_months]

            # Create figure with two y-axes
            fig, ax1 = plt.subplots(figsize=(12, 6))

            x = range(len(all_months))
            width = 0.35

            # Bars for credits and debits
            ax1.bar([i - width/2 for i in x], credits, width, label='Receitas', color='#4CAF50', alpha=0.8)
            ax1.bar([i + width/2 for i in x], debits, width, label='Despesas', color='#F44336', alpha=0.8)

            ax1.set_xlabel('Mês', fontsize=10)
            ax1.set_ylabel('Receitas/Despesas (R$)', fontsize=10, color='black')
            ax1.tick_params(axis='y', labelcolor='black', labelsize=9)
            ax1.tick_params(axis='x', rotation=45, labelsize=9)
            ax1.set_xticks(x)
            ax1.set_xticklabels(month_labels)
            ax1.grid(True, alpha=0.3, axis='y', linestyle='--')

            # Line for balance on secondary axis
            ax2 = ax1.twinx()
            ax2.plot(x, balance, color='#1976D2', linewidth=3, marker='o',
                    markersize=6, label='Saldo', zorder=10)
            ax2.set_ylabel('Saldo (R$)', fontsize=10, color='#1976D2')
            ax2.tick_params(axis='y', labelcolor='#1976D2', labelsize=9)

            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

            fig.tight_layout()

            self.chart_monthly.set_chart(fig)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.chart_monthly.show_message(f"Erro ao gerar gráfico: {str(e)}")

    def update_charts_display(self):
        """Update which charts are displayed based on selection"""
        # Clear layout
        for i in reversed(range(self.charts_layout.count())):
            widget = self.charts_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if self.df is None or self.df.empty:
            self.show_placeholder()
            return

        selected = self.chart_selector.currentData()

        if selected == "all" or selected == "timeline":
            self.charts_layout.addWidget(self.chart_timeline)

        if selected == "all" or selected == "categories":
            self.charts_layout.addWidget(self.chart_categories)

        if selected == "all" or selected == "banks":
            self.charts_layout.addWidget(self.chart_banks)

        if selected == "all" or selected == "monthly":
            self.charts_layout.addWidget(self.chart_monthly)

        self.charts_layout.addStretch()
