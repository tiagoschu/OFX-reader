"""
Placeholder tab for features under development
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class PlaceholderTab(QWidget):
    """Placeholder for tabs under development"""

    def __init__(self, tab_name, icon="🚧"):
        super().__init__()
        self.tab_name = tab_name
        self.icon = icon
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Icon
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("font-size: 72px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Title
        title = QLabel(f"{self.tab_name}")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1976D2;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Message
        message = QLabel("Esta funcionalidade está em desenvolvimento")
        message.setStyleSheet("font-size: 14px; color: #757575; margin-top: 10px;")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)

        # Coming soon
        coming_soon = QLabel("Em breve! 🎉")
        coming_soon.setStyleSheet("font-size: 12px; color: #9E9E9E; margin-top: 5px;")
        coming_soon.setAlignment(Qt.AlignCenter)
        layout.addWidget(coming_soon)

        self.setLayout(layout)
