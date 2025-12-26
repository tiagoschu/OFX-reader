"""
Charts Tab - Interactive visualizations with Plotly
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QComboBox, QPushButton,
                             QGridLayout)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class ChartWidget(QFrame):
    """Widget to display a Plotly chart"""

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

        # Web view for Plotly
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(350)

        # Configure settings for Plotly to work properly
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)

        layout.addWidget(self.web_view)

        self.setLayout(layout)

    def set_chart(self, fig):
        """Set Plotly figure to display"""
        try:
            # Use include_plotlyjs=True to embed the library (works offline, no CDN issues)
            # Full page mode for better rendering
            html = fig.to_html(
                include_plotlyjs=True,
                config={
                    'responsive': True,
                    'displayModeBar': True,
                    'displaylogo': False
                },
                full_html=True,
                validate=True
            )
            # Set HTML with base URL to ensure proper resource loading
            self.web_view.setHtml(html, QUrl("file:///"))
        except Exception as e:
            self.show_message(f"Erro ao renderizar gráfico: {str(e)}")

    def show_message(self, message):
        """Show a message instead of chart"""
        html = f"""
        <html>
        <body style="display: flex; align-items: center; justify-content: center; height: 100%; margin: 0; font-family: Arial;">
            <div style="text-align: center; color: #757575;">
                <div style="font-size: 48px; margin-bottom: 10px;">📊</div>
                <div style="font-size: 14px;">{message}</div>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)


class ChartsTab(QWidget):
    """Charts tab with Plotly visualizations"""

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

        title = QLabel("📈 Gráficos Interativos")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")

        subtitle = QLabel("Visualizações dinâmicas dos seus dados financeiros")
        subtitle.setStyleSheet("color: #B2DFDB; font-size: 10px; background: transparent;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Check if Plotly is available
        if not PLOTLY_AVAILABLE:
            error_label = QLabel("⚠️ Plotly não instalado. Execute: pip install plotly")
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
            daily = df.groupby('date_only').agg({
                'valor': lambda x: x[x > 0].sum() if (x > 0).any() else 0
            }).reset_index()
            daily.columns = ['date', 'credits']

            daily['debits'] = df.groupby('date_only').agg({
                'valor': lambda x: abs(x[x < 0].sum()) if (x < 0).any() else 0
            }).values

            # Create figure
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=daily['date'],
                y=daily['credits'],
                mode='lines+markers',
                name='Receitas',
                line=dict(color='#4CAF50', width=2),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(76, 175, 80, 0.1)'
            ))

            fig.add_trace(go.Scatter(
                x=daily['date'],
                y=daily['debits'],
                mode='lines+markers',
                name='Despesas',
                line=dict(color='#F44336', width=2),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(244, 67, 54, 0.1)'
            ))

            fig.update_layout(
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=10),
                margin=dict(l=50, r=20, t=20, b=50),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
                yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Valor (R$)')
            )

            self.chart_timeline.set_chart(fig)

        except Exception as e:
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

            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=cat_summary.index,
                values=cat_summary.values,
                hole=0.4,
                marker=dict(line=dict(color='white', width=2))
            )])

            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=10),
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
            )

            self.chart_categories.set_chart(fig)

        except Exception as e:
            self.chart_categories.show_message(f"Erro ao gerar gráfico: {str(e)}")

    def generate_banks_chart(self):
        """Generate banks comparison bar chart"""
        try:
            df = self.df.copy()

            # Group by bank
            banks_summary = df.groupby('banco').agg({
                'valor': ['count', 'sum']
            }).reset_index()
            banks_summary.columns = ['banco', 'transacoes', 'total']

            # Separate credits and debits
            banks_credits = df[df['valor'] > 0].groupby('banco')['valor'].sum()
            banks_debits = df[df['valor'] < 0].groupby('banco')['valor'].sum().abs()

            banks_summary['creditos'] = banks_summary['banco'].map(banks_credits).fillna(0)
            banks_summary['debitos'] = banks_summary['banco'].map(banks_debits).fillna(0)

            banks_summary = banks_summary.sort_values('transacoes', ascending=True)

            # Create figure
            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=banks_summary['banco'],
                x=banks_summary['creditos'],
                name='Receitas',
                orientation='h',
                marker=dict(color='#4CAF50')
            ))

            fig.add_trace(go.Bar(
                y=banks_summary['banco'],
                x=banks_summary['debitos'],
                name='Despesas',
                orientation='h',
                marker=dict(color='#F44336')
            ))

            fig.update_layout(
                barmode='group',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=10),
                margin=dict(l=150, r=20, t=20, b=50),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Valor (R$)'),
                yaxis=dict(showgrid=False)
            )

            self.chart_banks.set_chart(fig)

        except Exception as e:
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

            monthly = df.groupby('year_month').agg({
                'valor': 'sum'
            }).reset_index()
            monthly.columns = ['month', 'balance']

            monthly['credits'] = df[df['valor'] > 0].groupby(df['data_dt'].dt.to_period('M'))['valor'].sum().values
            monthly['debits'] = df[df['valor'] < 0].groupby(df['data_dt'].dt.to_period('M'))['valor'].sum().abs().values

            monthly['month_str'] = monthly['month'].astype(str)

            # Create figure
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=monthly['month_str'],
                y=monthly['credits'],
                name='Receitas',
                marker=dict(color='#4CAF50')
            ))

            fig.add_trace(go.Bar(
                x=monthly['month_str'],
                y=monthly['debits'],
                name='Despesas',
                marker=dict(color='#F44336')
            ))

            # Add balance line
            fig.add_trace(go.Scatter(
                x=monthly['month_str'],
                y=monthly['balance'],
                name='Saldo',
                mode='lines+markers',
                line=dict(color='#1976D2', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))

            fig.update_layout(
                barmode='group',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=10),
                margin=dict(l=50, r=50, t=20, b=80),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False, tickangle=-45),
                yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Receitas/Despesas (R$)'),
                yaxis2=dict(showgrid=False, overlaying='y', side='right', title='Saldo (R$)')
            )

            self.chart_monthly.set_chart(fig)

        except Exception as e:
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
