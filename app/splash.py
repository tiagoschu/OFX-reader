"""
Splash screen for OFX Consolidador Pro
"""

from PyQt5.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import (
    APP_NAME, VERSION, AUTHOR, RELEASE_DATE, DESCRIPTION,
    COLOR_PRIMARY, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    SPLASH_DURATION
)


class SplashScreen(QSplashScreen):
    """Custom splash screen with app information"""

    def __init__(self):
        # Create pixmap with all content BEFORE passing to QSplashScreen
        pixmap = self.create_splash_pixmap()
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)

    def create_splash_pixmap(self):
        """Create the splash screen pixmap"""
        # Create pixmap
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(COLOR_PRIMARY))

        # Create painter on pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background gradient
        from PyQt5.QtGui import QLinearGradient
        gradient = QLinearGradient(0, 0, 600, 400)
        gradient.setColorAt(0, QColor(COLOR_PRIMARY))
        gradient.setColorAt(1, QColor("#0D47A1"))
        painter.fillRect(0, 0, 600, 400, gradient)

        # App icon/emoji
        font_icon = QFont("Segoe UI Emoji", 72)
        painter.setFont(font_icon)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(0, 0, 600, 180, Qt.AlignCenter, "💰")

        # App name
        font_title = QFont("Segoe UI", 32, QFont.Bold)
        painter.setFont(font_title)
        painter.drawText(0, 160, 600, 60, Qt.AlignCenter, APP_NAME)

        # Description
        font_desc = QFont("Segoe UI", 14)
        painter.setFont(font_desc)
        painter.setPen(QColor("#B3E5FC"))
        painter.drawText(0, 220, 600, 30, Qt.AlignCenter, DESCRIPTION)

        # Separator line
        painter.setPen(QColor("#FFFFFF"))
        painter.drawLine(150, 270, 450, 270)

        # Author
        font_info = QFont("Segoe UI", 12)
        painter.setFont(font_info)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(0, 290, 600, 25, Qt.AlignCenter, f"Criador: {AUTHOR}")

        # Version
        painter.drawText(0, 315, 600, 25, Qt.AlignCenter, f"Versão: {VERSION}")

        # Release date
        painter.drawText(0, 340, 600, 25, Qt.AlignCenter, f"Release: {RELEASE_DATE}")

        # Loading text
        font_loading = QFont("Segoe UI", 10, QFont.Light)
        painter.setFont(font_loading)
        painter.setPen(QColor("#B3E5FC"))
        painter.drawText(0, 370, 600, 20, Qt.AlignCenter, "Carregando...")

        # End painter before returning pixmap
        painter.end()

        return pixmap

    def show_message(self, message):
        """Show a message on the splash screen"""
        self.showMessage(
            message,
            Qt.AlignBottom | Qt.AlignHCenter,
            QColor("#FFFFFF")
        )


if __name__ == "__main__":
    # Test splash screen
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()

    # Show for 3 seconds
    QTimer.singleShot(3000, splash.close)
    QTimer.singleShot(3000, app.quit)

    sys.exit(app.exec_())
