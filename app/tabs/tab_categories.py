"""
Categories Tab - Manage transaction categories
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QListWidget, QListWidgetItem,
                             QLineEdit, QTextEdit, QColorDialog, QMessageBox,
                             QInputDialog, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.constants import CATEGORIES
from utils.config import config


class CategoryItem(QFrame):
    """Widget for displaying a category"""

    def __init__(self, name, data, parent=None):
        super().__init__()
        self.name = name
        self.data = data
        self.parent_widget = parent
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 3px;
                border-left: 4px solid {self.data.get('color', '#757575')};
                padding: 6px;
                margin: 2px;
            }}
            QFrame:hover {{
                background-color: #F5F5F5;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        # Icon + Name
        icon_label = QLabel(self.data.get('icon', '📁'))
        icon_label.setStyleSheet("font-size: 16px; background: transparent;")
        layout.addWidget(icon_label)

        name_label = QLabel(self.name)
        name_label.setStyleSheet("font-size: 10px; font-weight: bold; background: transparent;")
        layout.addWidget(name_label)

        # Keywords count
        keywords_count = len(self.data.get('keywords', []))
        count_label = QLabel(f"({keywords_count} palavras-chave)")
        count_label.setStyleSheet("font-size: 8px; color: #666; background: transparent;")
        layout.addWidget(count_label)

        layout.addStretch()

        # Edit button
        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(24, 24)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn_edit.clicked.connect(self.edit_category)
        layout.addWidget(btn_edit)

        self.setLayout(layout)

    def edit_category(self):
        """Edit this category"""
        if self.parent_widget:
            self.parent_widget.edit_category(self.name, self.data)


class CategoriesTab(QWidget):
    """Categories management tab"""

    def __init__(self):
        super().__init__()
        self.categories = CATEGORIES.copy()
        self.custom_categories = config.get('custom_categories', {})
        self.categories.update(self.custom_categories)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header_frame = QFrame()
        header_frame.setMaximumHeight(50)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E91E63, stop:1 #C2185B);
                border-radius: 6px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("🎯 Gerenciar Categorias")
        title.setStyleSheet("color: white; font-size: 13px; font-weight: bold; background: transparent;")
        header_layout.addWidget(title)

        info = QLabel(f"{len(self.categories)} categorias")
        info.setStyleSheet("color: #F8BBD0; font-size: 9px; background: transparent;")
        header_layout.addWidget(info)
        header_layout.addStretch()

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        btn_add = QPushButton("➕ Nova Categoria")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        btn_add.clicked.connect(self.add_category)
        controls_layout.addWidget(btn_add)

        btn_reset = QPushButton("🔄 Restaurar Padrões")
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        btn_reset.clicked.connect(self.reset_categories)
        controls_layout.addWidget(btn_reset)

        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        # Categories list
        self.categories_container = QWidget()
        self.categories_layout = QVBoxLayout()
        self.categories_layout.setSpacing(2)
        self.categories_container.setLayout(self.categories_layout)

        main_layout.addWidget(self.categories_container)

        # Refresh display
        self.refresh_categories()

        # Info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #FCE4EC;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(8, 6, 8, 6)

        info_label = QLabel(
            "ℹ️ <b>Dica:</b> Categorias ajudam a organizar suas transações. "
            "Adicione palavras-chave que identificam cada tipo de gasto."
        )
        info_label.setStyleSheet("font-size: 9px; color: #880E4F; background: transparent;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        info_frame.setLayout(info_layout)
        main_layout.addWidget(info_frame)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def refresh_categories(self):
        """Refresh categories display"""
        # Clear existing
        for i in reversed(range(self.categories_layout.count())):
            widget = self.categories_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Add categories
        for name, data in sorted(self.categories.items()):
            cat_item = CategoryItem(name, data, self)
            self.categories_layout.addWidget(cat_item)

        self.categories_layout.addStretch()

    def add_category(self):
        """Add new custom category"""
        name, ok = QInputDialog.getText(
            self,
            "Nova Categoria",
            "Nome da categoria:"
        )

        if not ok or not name:
            return

        if name in self.categories:
            QMessageBox.warning(self, "Aviso", "Esta categoria já existe!")
            return

        # Get keywords
        keywords_text, ok = QInputDialog.getMultiLineText(
            self,
            "Palavras-chave",
            "Digite as palavras-chave (uma por linha):"
        )

        if not ok:
            return

        keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]

        # Get color
        color = QColorDialog.getColor()
        if not color.isValid():
            color = QColor("#757575")

        # Get icon
        icon, ok = QInputDialog.getText(
            self,
            "Ícone",
            "Ícone (emoji):",
            text="📁"
        )

        if not ok or not icon:
            icon = "📁"

        # Add category
        self.custom_categories[name] = {
            'keywords': keywords,
            'color': color.name(),
            'icon': icon
        }

        self.categories[name] = self.custom_categories[name]

        # Save
        config.set('custom_categories', self.custom_categories)

        # Refresh
        self.refresh_categories()

        QMessageBox.information(self, "Sucesso", f"Categoria '{name}' adicionada!")

    def edit_category(self, name, data):
        """Edit existing category"""
        # For now, just show details
        details = f"**{name}**\n\n"
        details += f"Ícone: {data.get('icon', '📁')}\n"
        details += f"Cor: {data.get('color', '#757575')}\n\n"
        details += f"Palavras-chave ({len(data.get('keywords', []))}):\n"
        details += '\n'.join(f"  • {k}" for k in data.get('keywords', []))

        QMessageBox.information(self, f"Categoria: {name}", details)

    def reset_categories(self):
        """Reset to default categories"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Tem certeza que deseja restaurar as categorias padrão?\n"
            "Todas as categorias customizadas serão removidas.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.custom_categories = {}
            self.categories = CATEGORIES.copy()
            config.set('custom_categories', {})
            self.refresh_categories()
            QMessageBox.information(self, "Sucesso", "Categorias restauradas!")
