"""
Main Window for OFX Consolidador Pro
"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, QMessageBox,
                             QApplication)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tabs.tab_home import HomeTab
from app.tabs.tab_import import ImportTab
from app.tabs.tab_analysis import AnalysisTab
from app.tabs.tab_placeholder import PlaceholderTab
from utils.constants import APP_NAME, VERSION, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from utils.config import config


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.df = None  # Current dataframe
        self.init_ui()

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
        self.tab_analysis = AnalysisTab()
        self.tab_charts = PlaceholderTab("Gráficos", "📈")
        self.tab_categories = PlaceholderTab("Categorias", "🎯")
        self.tab_reports = PlaceholderTab("Relatórios", "📋")
        self.tab_export = PlaceholderTab("Exportar", "💾")
        self.tab_settings = PlaceholderTab("Configurações", "⚙️")

        # Add tabs
        self.tabs.addTab(self.tab_home, "🏠 Início")
        self.tabs.addTab(self.tab_import, "📥 Importar")
        self.tabs.addTab(self.tab_analysis, "📊 Análises")
        self.tabs.addTab(self.tab_charts, "📈 Gráficos")
        self.tabs.addTab(self.tab_categories, "🎯 Categorias")
        self.tabs.addTab(self.tab_reports, "📋 Relatórios")
        self.tabs.addTab(self.tab_export, "💾 Exportar")
        self.tabs.addTab(self.tab_settings, "⚙️ Config")

        # Connect signals
        self.tab_import.data_processed.connect(self.on_data_processed)

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

        # Switch to home tab to show summary
        QTimer.singleShot(100, lambda: self.tabs.setCurrentWidget(self.tab_home))

        self.statusBar().showMessage(f"Processados {len(df)} transações", 5000)

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
