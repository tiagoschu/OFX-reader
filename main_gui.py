#!/usr/bin/env python3
"""
OFX Consolidador Pro v3.0
Main entry point for GUI application

Author: Tiago Schubert
Release: Janeiro 2025
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.splash import SplashScreen
from app.main_window import MainWindow
from utils.constants import SPLASH_DURATION
from utils.config import config


def main():
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("OFX Consolidador Pro")
    app.setApplicationVersion("3.0.0")
    app.setOrganizationName("Tiago Schubert")

    # Show splash screen if enabled
    show_splash = config.get('show_splash', True)

    if show_splash:
        splash = SplashScreen()
        splash.show()
        splash.show_message("Inicializando...")

        # Create main window (hidden)
        main_window = MainWindow()

        def show_main_window():
            """Show main window and close splash"""
            splash.finish(main_window)
            main_window.show()

        # Show main window after splash duration
        QTimer.singleShot(SPLASH_DURATION, show_main_window)

    else:
        # Show main window directly
        main_window = MainWindow()
        main_window.show()

    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
