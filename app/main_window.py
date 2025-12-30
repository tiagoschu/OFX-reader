"""
Main Window for OFX Consolidador Pro
"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, QMessageBox,
                             QApplication, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tabs.tab_home import HomeTab
from app.tabs.tab_import import ImportTab
from app.tabs.tab_analysis import AnalysisTab
from app.tabs.tab_charts import ChartsTab
from app.tabs.tab_categories import CategoriesTab
from app.tabs.tab_reports import ReportsTab
from app.tabs.tab_dre import DRETab
from app.tabs.tab_export import ExportTab
from app.tabs.tab_config import ConfigTab
from app.tabs.tab_invoices import InvoicesTab
from app.tabs.tab_invoice_analysis import InvoiceAnalysisTab
from app.tabs.tab_unmatched import UnmatchedTab
from app.tabs.tab_credit_cards import CreditCardsTab
from core.project import Project
from utils.constants import APP_NAME, VERSION, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from utils.config import config


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, project=None, project_path=None):
        super().__init__()
        self.df = None  # Current dataframe
        self.processor = None
        self.project = project or Project()
        self.project_path = project_path
        self.init_ui()

        # Apply project configuration to tabs
        self.apply_project_config()

        # Load project data if provided
        if project and project.get_dataframe() is not None:
            self.load_from_project()

    def init_ui(self):
        # Window properties
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Restore geometry if saved
        geometry = config.get('window_geometry')
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1400, 900)

        # Create tab widget FIRST
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)

        # Create tabs
        self.tab_home = HomeTab()
        self.tab_import = ImportTab()
        self.tab_invoices = InvoicesTab()
        self.tab_credit_cards = CreditCardsTab()
        self.tab_invoice_analysis = InvoiceAnalysisTab()
        self.tab_unmatched = UnmatchedTab()
        self.tab_analysis = AnalysisTab()
        self.tab_charts = ChartsTab()
        self.tab_categories = CategoriesTab()
        self.tab_reports = ReportsTab()
        self.tab_dre = DRETab()
        self.tab_export = ExportTab()
        self.tab_settings = ConfigTab()

        # Add tabs (reorganized: import tabs at positions 1, 2, 3)
        self.tabs.addTab(self.tab_home, "🏠 Início")
        self.tabs.addTab(self.tab_import, "📥 OFX Import")
        self.tabs.addTab(self.tab_invoices, "📄 NFSe Import")
        self.tabs.addTab(self.tab_credit_cards, "💳 Vendas Cartão")
        self.tabs.addTab(self.tab_invoice_analysis, "🔗 Análise NFSe")
        self.tabs.addTab(self.tab_unmatched, "🔍 Não Vinculados")
        self.tabs.addTab(self.tab_analysis, "📊 Análises")
        self.tabs.addTab(self.tab_charts, "📈 Gráficos")
        self.tabs.addTab(self.tab_categories, "🎯 Categorias")
        self.tabs.addTab(self.tab_reports, "📋 Relatórios")
        self.tabs.addTab(self.tab_dre, "💼 DRE")
        self.tabs.addTab(self.tab_export, "💾 Exportar")
        self.tabs.addTab(self.tab_settings, "⚙️ Config")

        # Connect signals
        self.tab_import.data_processed.connect(self.on_data_processed)
        self.tab_categories.data_recategorized.connect(self.on_data_recategorized)
        self.tab_invoices.invoices_loaded.connect(self.on_invoices_loaded)
        self.tab_invoices.match_requested.connect(self.on_match_requested)
        self.tab_credit_cards.cards_loaded.connect(self.on_cards_loaded)
        self.tab_credit_cards.match_requested.connect(self.on_match_requested)

        # Set central widget
        self.setCentralWidget(self.tabs)

        # Create menu bar AFTER tabs are created
        self.create_menu_bar()

        # Status bar
        self.statusBar().showMessage("Pronto")

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("Arquivo")

        # Project actions
        new_project_action = QAction("Novo Projeto", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self.on_new_project)
        file_menu.addAction(new_project_action)

        open_project_action = QAction("Abrir Projeto...", self)
        open_project_action.setShortcut("Ctrl+Shift+O")
        open_project_action.triggered.connect(self.on_open_project)
        file_menu.addAction(open_project_action)

        save_project_action = QAction("Salvar Projeto", self)
        save_project_action.setShortcut("Ctrl+S")
        save_project_action.triggered.connect(self.on_save_project)
        file_menu.addAction(save_project_action)

        save_project_as_action = QAction("Salvar Projeto Como...", self)
        save_project_as_action.setShortcut("Ctrl+Shift+S")
        save_project_as_action.triggered.connect(self.on_save_project_as)
        file_menu.addAction(save_project_as_action)

        file_menu.addSeparator()

        import_action = QAction("Importar OFX...", self)
        import_action.setShortcut("Ctrl+O")
        import_action.triggered.connect(lambda: self.tabs.setCurrentWidget(self.tab_import))
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("Visualizar")

        for i in range(self.tabs.count()):
            action = QAction(self.tabs.tabText(i), self)
            action.triggered.connect(lambda checked, idx=i: self.tabs.setCurrentIndex(idx))
            view_menu.addAction(action)

        # Help menu
        help_menu = menubar.addMenu("Ajuda")

        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_data_processed(self, df, processor):
        """Handle data processed signal"""
        self.df = df
        self.processor = processor

        # Update home tab with stats
        self.tab_home.update_stats(df)

        # Update analysis tab with data and duplicates
        self.tab_analysis.update_data(df, processor.duplicates if processor else [])

        # Update charts tab with data
        self.tab_charts.update_data(df)

        # Update categories tab with data
        self.tab_categories.update_data(df)

        # Update export tab with data
        self.tab_export.update_data(df)

        # Update reports tab with data
        self.tab_reports.update_data(df)

        # Update DRE tab with data
        self.tab_dre.update_data(df)

        # Update invoices tab with OFX data for matching
        self.tab_invoices.set_ofx_data(df)

        # Update credit cards tab with OFX data for matching
        self.tab_credit_cards.set_ofx_data(df)

        # Update invoice analysis tab with OFX data
        self.tab_invoice_analysis.set_data(self.tab_invoices.get_invoices_data(), df)

        # Update unmatched items tab
        self.tab_unmatched.set_data(self.tab_invoices.get_invoices_data(), df)

        # Switch to home tab to show summary
        QTimer.singleShot(100, lambda: self.tabs.setCurrentWidget(self.tab_home))

        self.statusBar().showMessage(f"Processados {len(df)} transações", 5000)

    def on_invoices_loaded(self, invoices_df):
        """Handle invoices loaded signal"""
        # Update invoice analysis tab with invoice data
        self.tab_invoice_analysis.set_data(invoices_df, self.df)

        # Update unmatched items tab
        self.tab_unmatched.set_data(invoices_df, self.df)

        self.statusBar().showMessage(f"{len(invoices_df)} notas fiscais carregadas", 5000)

    def on_cards_loaded(self, sales_df, installments_df):
        """Handle credit card sales loaded signal"""
        # Update invoice analysis tab with credit card sales data
        self.tab_invoice_analysis.set_card_data(sales_df, installments_df)

        # TODO: Update unmatched tab to show unmatched installments

        self.statusBar().showMessage(
            f"{len(sales_df)} venda(s) e {len(installments_df)} parcela(s) de cartão carregadas",
            5000
        )

    def on_match_requested(self):
        """Handle match requested - switch to import tab"""
        self.tabs.setCurrentWidget(self.tab_import)
        QMessageBox.information(
            self,
            "Importar OFX",
            "Por favor, importe arquivos OFX na aba 'Importar' antes de vincular com notas fiscais."
        )

    def on_data_recategorized(self, df):
        """Handle data recategorized signal from Categories tab"""
        self.df = df

        # Update project with recategorized data
        if self.project:
            self.project.data['dataframe'] = df

        # Update all tabs with recategorized data
        self.tab_home.update_stats(df)
        self.tab_analysis.update_data(df, self.processor.duplicates if self.processor else [])
        self.tab_charts.update_data(df)
        self.tab_categories.update_data(df)
        self.tab_export.update_data(df)
        self.tab_reports.update_data(df)
        self.tab_dre.update_data(df)

        self.statusBar().showMessage(f"Recategorizadas {len(df)} transações", 5000)

    def apply_project_config(self):
        """Apply project configuration to tabs"""
        if self.project:
            config = self.project.get_config()
            category_preset = config.get('category_preset', 'personal')

            # Set category preset for import tab (used when importing new data)
            self.tab_import.set_category_preset(category_preset)

            # Set category preset for DRE tab (affects DRE structure)
            self.tab_dre.set_category_preset(category_preset)

            # Set category preset for Categories tab (for recategorization)
            self.tab_categories.set_category_preset(category_preset)

    def load_from_project(self):
        """Load data from current project"""
        df = self.project.get_dataframe()
        duplicates = self.project.get_duplicates()
        invoices_df = self.project.get_invoices()

        if df is not None and not df.empty:
            # Simulate processor for compatibility
            class DummyProcessor:
                def __init__(self, duplicates):
                    self.duplicates = duplicates

            self.processor = DummyProcessor(duplicates)
            self.on_data_processed(df, self.processor)

            # Load invoices if present
            if invoices_df is not None and not invoices_df.empty:
                self.tab_invoices.load_invoices(invoices_df)
                self.tab_invoice_analysis.set_data(invoices_df, df)
                self.tab_unmatched.set_data(invoices_df, df)

            # Update title with project name
            project_name = self.project.get_metadata().get('name', 'Projeto')
            self.setWindowTitle(f"{APP_NAME} v{VERSION} - {project_name}")

    def on_new_project(self):
        """Create a new project"""
        reply = QMessageBox.question(
            self,
            "Novo Projeto",
            "Criar um novo projeto? Os dados atuais não salvos serão perdidos.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.project = Project()
            self.project_path = None
            self.df = None
            self.processor = None

            # Clear all tabs
            self.tab_home.update_stats(None)
            self.setWindowTitle(f"{APP_NAME} v{VERSION}")

            # Apply new project config
            self.apply_project_config()

            self.statusBar().showMessage("Novo projeto criado", 3000)

    def on_open_project(self):
        """Open a project file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Projeto",
            Project.get_default_projects_dir(),
            "Projetos OFX (*.ofxproj);;Todos os arquivos (*.*)"
        )

        if file_path:
            project = Project()
            success, message, data = project.load(file_path)

            if success:
                self.project = project
                self.project_path = file_path

                # Apply project config first
                self.apply_project_config()

                # Then load data
                self.load_from_project()

                self.statusBar().showMessage(f"Projeto aberto: {file_path}", 5000)
            else:
                QMessageBox.critical(self, "Erro ao Abrir Projeto", message)

    def on_save_project(self):
        """Save the current project"""
        if self.project_path:
            self._save_project_to_file(self.project_path)
        else:
            self.on_save_project_as()

    def on_save_project_as(self):
        """Save project with a new name"""
        default_dir = Project.get_default_projects_dir()

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Projeto Como",
            default_dir,
            "Projetos OFX (*.ofxproj);;Todos os arquivos (*.*)"
        )

        if file_path:
            # Ensure .ofxproj extension
            if not file_path.endswith('.ofxproj'):
                file_path += '.ofxproj'

            self._save_project_to_file(file_path)

    def _save_project_to_file(self, file_path):
        """Internal method to save project to file"""
        # Get project name from filename
        import os
        project_name = os.path.splitext(os.path.basename(file_path))[0]

        # Update metadata
        metadata = {
            'name': project_name
        }

        # Save project
        success, message = self.project.save(
            file_path,
            df=self.df,
            duplicates=self.processor.duplicates if self.processor else [],
            invoices_df=self.tab_invoices.get_invoices_data(),
            invoice_matches_df=self.tab_invoices.matches_df if hasattr(self.tab_invoices, 'matches_df') else None,
            credit_card_sales_df=self.tab_credit_cards.get_sales_df(),
            credit_card_installments_df=self.tab_credit_cards.get_installments_df(),
            metadata=metadata
        )

        if success:
            self.project_path = file_path
            self.setWindowTitle(f"{APP_NAME} v{VERSION} - {project_name}")
            self.statusBar().showMessage(f"Projeto salvo: {file_path}", 5000)
            QMessageBox.information(self, "Projeto Salvo", message)
        else:
            QMessageBox.critical(self, "Erro ao Salvar", message)

    def show_about(self):
        """Show about dialog"""
        from utils.constants import AUTHOR, RELEASE_DATE, DESCRIPTION

        about_text = f"""
        <h2>{APP_NAME}</h2>
        <p><b>Versão:</b> {VERSION}</p>
        <p><b>Autor:</b> {AUTHOR}</p>
        <p><b>Release:</b> {RELEASE_DATE}</p>
        <br>
        <p>{DESCRIPTION}</p>
        <br>
        <p><i>Desenvolvido com PyQt5 e Python</i></p>
        """

        QMessageBox.about(self, f"Sobre {APP_NAME}", about_text)

    def closeEvent(self, event):
        """Handle window close event"""
        # Save window geometry
        config.set('window_geometry', self.saveGeometry())

        # Confirm exit if data is loaded
        if self.df is not None and not self.df.empty:
            reply = QMessageBox.question(
                self,
                "Confirmar Saída",
                "Deseja realmente sair?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                event.ignore()
                return

        event.accept()
