"""
Categories Tab - Interactive category management with transaction categorization
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QListWidget, QListWidgetItem,
                             QLineEdit, QTextEdit, QColorDialog, QMessageBox,
                             QInputDialog, QGroupBox, QScrollArea, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, QDialog,
                             QDialogButtonBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.constants import CATEGORIES
from utils.config import config
from core.categorizer import TransactionCategorizer


class RecategorizeDialog(QDialog):
    """Dialog for recategorizing a transaction"""

    def __init__(self, transaction, categories, parent=None):
        super().__init__(parent)
        self.transaction = transaction
        self.categories = categories
        self.selected_category = None
        self.add_keyword = False
        self.new_keyword = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Recategorizar Transação")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Transaction info
        info_group = QGroupBox("Transação")
        info_layout = QVBoxLayout()

        desc_label = QLabel(f"<b>Descrição:</b> {self.transaction.get('descricao', '')}")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        valor_label = QLabel(f"<b>Valor:</b> R$ {self.transaction.get('valor', 0):,.2f}")
        info_layout.addWidget(valor_label)

        data_label = QLabel(f"<b>Data:</b> {self.transaction.get('data', '')}")
        info_layout.addWidget(data_label)

        current_cat = QLabel(f"<b>Categoria atual:</b> {self.transaction.get('categoria', 'Sem categoria')}")
        info_layout.addWidget(current_cat)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Category selection
        cat_group = QGroupBox("Nova Categoria")
        cat_layout = QVBoxLayout()

        self.cb_category = QComboBox()
        for cat_name in sorted(self.categories.keys()):
            icon = self.categories[cat_name].get('icon', '📁')
            self.cb_category.addItem(f"{icon} {cat_name}")
        cat_layout.addWidget(self.cb_category)

        cat_group.setLayout(cat_layout)
        layout.addWidget(cat_group)

        # Keyword suggestion
        keyword_group = QGroupBox("Sugerir Palavra-chave")
        keyword_layout = QVBoxLayout()

        self.cb_add_keyword = QCheckBox("Adicionar palavra-chave da descrição às keywords desta categoria")
        keyword_layout.addWidget(self.cb_add_keyword)

        keyword_help = QLabel("Isso ajudará a categorizar automaticamente transações similares no futuro.")
        keyword_help.setStyleSheet("font-size: 9px; color: #666;")
        keyword_help.setWordWrap(True)
        keyword_layout.addWidget(keyword_help)

        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Palavra-chave sugerida (deixe em branco para extrair da descrição)")
        self.keyword_input.setEnabled(False)
        keyword_layout.addWidget(self.keyword_input)

        self.cb_add_keyword.stateChanged.connect(lambda: self.keyword_input.setEnabled(self.cb_add_keyword.isChecked()))

        keyword_group.setLayout(keyword_layout)
        layout.addWidget(keyword_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept_recategorize)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def accept_recategorize(self):
        """Accept and save recategorization"""
        selected_text = self.cb_category.currentText()
        # Remove emoji prefix
        self.selected_category = ' '.join(selected_text.split(' ')[1:])

        self.add_keyword = self.cb_add_keyword.isChecked()

        if self.add_keyword:
            self.new_keyword = self.keyword_input.text().strip()
            if not self.new_keyword:
                # Extract first meaningful word from description
                desc = str(self.transaction.get('descricao', '')).lower()
                words = desc.split()
                # Find words longer than 3 characters
                for word in words:
                    if len(word) > 3 and word.isalpha():
                        self.new_keyword = word
                        break

        self.accept()


class ExpandableCategoryWidget(QFrame):
    """Widget for a category that can be expanded to show transactions"""

    category_changed = pyqtSignal()  # Signal when category or transactions change

    def __init__(self, name, data, df, parent=None):
        super().__init__()
        self.name = name
        self.data = data
        self.df = df
        self.parent_widget = parent
        self.expanded = False
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 4px;
                border-left: 4px solid {self.data.get('color', '#757575')};
                padding: 0px;
                margin: 2px;
            }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header (always visible)
        header_frame = QFrame()
        header_frame.setStyleSheet("background: transparent; border: none;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 6, 8, 6)
        header_layout.setSpacing(8)

        # Expand/collapse button
        self.btn_expand = QPushButton("▶")
        self.btn_expand.setFixedSize(20, 20)
        self.btn_expand.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 10px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                border-radius: 10px;
            }
        """)
        self.btn_expand.clicked.connect(self.toggle_expand)
        header_layout.addWidget(self.btn_expand)

        # Icon + Name
        icon_label = QLabel(self.data.get('icon', '📁'))
        icon_label.setStyleSheet("font-size: 16px; background: transparent;")
        header_layout.addWidget(icon_label)

        name_label = QLabel(self.name)
        name_label.setStyleSheet("font-size: 11px; font-weight: bold; background: transparent;")
        header_layout.addWidget(name_label)

        # Transaction count in this category
        if self.df is not None and not self.df.empty and 'categoria' in self.df.columns:
            cat_transactions = self.df[self.df['categoria'] == self.name]
            count = len(cat_transactions)
            total_value = cat_transactions[cat_transactions['valor'] < 0]['valor'].sum() if not cat_transactions.empty else 0
        else:
            count = 0
            total_value = 0

        count_label = QLabel(f"{count} transações | R$ {abs(total_value):,.2f}")
        count_label.setStyleSheet("font-size: 9px; color: #666; background: transparent;")
        header_layout.addWidget(count_label)

        # Keywords count
        keywords_count = len(self.data.get('keywords', []))
        keywords_label = QLabel(f"({keywords_count} keywords)")
        keywords_label.setStyleSheet("font-size: 8px; color: #999; background: transparent;")
        header_layout.addWidget(keywords_label)

        header_layout.addStretch()

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
        header_layout.addWidget(btn_edit)

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Expandable content (transactions table)
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("background: #F5F5F5; border: none; border-top: 1px solid #E0E0E0;")
        self.content_frame.setVisible(False)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 8, 8, 8)

        # Transactions table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Data', 'Descrição', 'Valor', 'Banco', 'Ação'])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setMinimumHeight(400)
        self.table.setMaximumHeight(500)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                font-size: 9px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 4px;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
                font-size: 9px;
            }
        """)

        content_layout.addWidget(self.table)
        self.content_frame.setLayout(content_layout)
        main_layout.addWidget(self.content_frame)

        self.setLayout(main_layout)

    def toggle_expand(self):
        """Toggle expand/collapse"""
        self.expanded = not self.expanded
        self.content_frame.setVisible(self.expanded)
        self.btn_expand.setText("▼" if self.expanded else "▶")

        if self.expanded:
            self.populate_table()

    def populate_table(self):
        """Populate transaction table"""
        self.table.setRowCount(0)

        if self.df is None or self.df.empty or 'categoria' not in self.df.columns:
            return

        cat_transactions = self.df[self.df['categoria'] == self.name]

        for idx, (_, row) in enumerate(cat_transactions.iterrows()):
            self.table.insertRow(idx)

            # Data
            self.table.setItem(idx, 0, QTableWidgetItem(str(row.get('data', ''))))

            # Descrição
            desc_item = QTableWidgetItem(str(row.get('descricao', ''))[:50])
            desc_item.setToolTip(str(row.get('descricao', '')))
            self.table.setItem(idx, 1, desc_item)

            # Valor
            valor = row.get('valor', 0)
            valor_item = QTableWidgetItem(f"R$ {valor:,.2f}")
            if valor < 0:
                valor_item.setForeground(QColor('#D32F2F'))
            else:
                valor_item.setForeground(QColor('#4CAF50'))
            self.table.setItem(idx, 2, valor_item)

            # Banco
            self.table.setItem(idx, 3, QTableWidgetItem(str(row.get('banco', ''))[:20]))

            # Action button
            btn_recategorize = QPushButton("Recategorizar")
            btn_recategorize.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 2px;
                    padding: 3px 6px;
                    font-size: 8px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            btn_recategorize.clicked.connect(lambda checked, r=row: self.recategorize_transaction(r))
            self.table.setCellWidget(idx, 4, btn_recategorize)

        self.table.resizeColumnsToContents()

    def recategorize_transaction(self, transaction):
        """Open dialog to recategorize a transaction"""
        if self.parent_widget:
            self.parent_widget.recategorize_transaction(transaction, from_category=self.name)

    def edit_category(self):
        """Edit this category"""
        if self.parent_widget:
            self.parent_widget.edit_category(self.name, self.data)


class UncategorizedWidget(QFrame):
    """Widget showing uncategorized transactions"""

    category_changed = pyqtSignal()

    def __init__(self, df, parent=None):
        super().__init__()
        self.df = df
        self.parent_widget = parent
        self.expanded = False
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #FFF3E0;
                border-radius: 4px;
                border-left: 4px solid #FF9800;
                padding: 0px;
                margin: 2px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background: transparent; border: none;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 6, 8, 6)

        # Expand button
        self.btn_expand = QPushButton("▶")
        self.btn_expand.setFixedSize(20, 20)
        self.btn_expand.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #FFE0B2;
                border-radius: 10px;
            }
        """)
        self.btn_expand.clicked.connect(self.toggle_expand)
        header_layout.addWidget(self.btn_expand)

        title = QLabel("⚠️ Transações Sem Categoria")
        title.setStyleSheet("font-size: 11px; font-weight: bold; background: transparent;")
        header_layout.addWidget(title)

        # Count uncategorized
        if self.df is not None and not self.df.empty:
            if 'categoria' in self.df.columns:
                uncategorized = self.df[self.df['categoria'] == 'Outros']
            else:
                uncategorized = self.df
            count = len(uncategorized)
        else:
            count = 0

        count_label = QLabel(f"{count} transações não categorizadas")
        count_label.setStyleSheet("font-size: 9px; color: #E65100; background: transparent;")
        header_layout.addWidget(count_label)

        header_layout.addStretch()
        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Content
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("background: #FFECB3; border: none; border-top: 1px solid #FFE082;")
        self.content_frame.setVisible(False)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 8, 8, 8)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Data', 'Descrição', 'Valor', 'Banco', 'Ação'])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setMinimumHeight(400)
        self.table.setMaximumHeight(500)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #FFE082;
                font-size: 9px;
            }
            QHeaderView::section {
                background-color: #FFF3E0;
                padding: 4px;
                border: none;
                border-bottom: 1px solid #FFE082;
                font-weight: bold;
                font-size: 9px;
            }
        """)

        content_layout.addWidget(self.table)

        # Warning label container (hidden until needed)
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("font-size: 8px; color: #E65100; padding: 4px;")
        self.warning_label.setVisible(False)
        content_layout.addWidget(self.warning_label)

        self.content_frame.setLayout(content_layout)
        main_layout.addWidget(self.content_frame)

        self.setLayout(main_layout)

    def toggle_expand(self):
        """Toggle expand/collapse"""
        self.expanded = not self.expanded
        self.content_frame.setVisible(self.expanded)
        self.btn_expand.setText("▼" if self.expanded else "▶")

        if self.expanded:
            self.populate_table()

    def populate_table(self):
        """Populate uncategorized transactions table"""
        self.table.setRowCount(0)

        if self.df is None or self.df.empty:
            return

        if 'categoria' in self.df.columns:
            uncategorized = self.df[self.df['categoria'] == 'Outros']
        else:
            uncategorized = self.df

        for idx, (_, row) in enumerate(uncategorized.head(100).iterrows()):  # Limit to 100 for performance
            self.table.insertRow(idx)

            self.table.setItem(idx, 0, QTableWidgetItem(str(row.get('data', ''))))

            desc_item = QTableWidgetItem(str(row.get('descricao', ''))[:50])
            desc_item.setToolTip(str(row.get('descricao', '')))
            self.table.setItem(idx, 1, desc_item)

            valor = row.get('valor', 0)
            valor_item = QTableWidgetItem(f"R$ {valor:,.2f}")
            if valor < 0:
                valor_item.setForeground(QColor('#D32F2F'))
            else:
                valor_item.setForeground(QColor('#4CAF50'))
            self.table.setItem(idx, 2, valor_item)

            self.table.setItem(idx, 3, QTableWidgetItem(str(row.get('banco', ''))[:20]))

            btn_categorize = QPushButton("Categorizar")
            btn_categorize.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 2px;
                    padding: 3px 6px;
                    font-size: 8px;
                }
                QPushButton:hover {
                    background-color: #45A049;
                }
            """)
            btn_categorize.clicked.connect(lambda checked, r=row: self.categorize_transaction(r))
            self.table.setCellWidget(idx, 4, btn_categorize)

        self.table.resizeColumnsToContents()

        # Update warning label
        if len(uncategorized) > 100:
            self.warning_label.setText(f"Mostrando 100 de {len(uncategorized)} transações não categorizadas")
            self.warning_label.setVisible(True)
        else:
            self.warning_label.setVisible(False)

    def categorize_transaction(self, transaction):
        """Categorize an uncategorized transaction"""
        if self.parent_widget:
            self.parent_widget.recategorize_transaction(transaction, from_category='Outros')


class CategoriesTab(QWidget):
    """Interactive categories management tab"""

    def __init__(self):
        super().__init__()
        self.categories = CATEGORIES.copy()
        self.custom_categories = config.get('custom_categories', {})
        self.categories.update(self.custom_categories)
        self.df = None
        self.category_preset = None  # Will be set by MainWindow when project is loaded
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

        self.info_label = QLabel(f"{len(self.categories)} categorias")
        self.info_label.setStyleSheet("color: #F8BBD0; font-size: 9px; background: transparent;")
        header_layout.addWidget(self.info_label)
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

        btn_recategorize = QPushButton("🔁 Recategorizar Tudo")
        btn_recategorize.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        btn_recategorize.setToolTip("Recategoriza todas as transações usando o plano de categorias atual")
        btn_recategorize.clicked.connect(self.recategorize_all)
        controls_layout.addWidget(btn_recategorize)

        btn_expand_all = QPushButton("📂 Expandir Todas")
        btn_expand_all.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn_expand_all.clicked.connect(self.expand_all_categories)
        controls_layout.addWidget(btn_expand_all)

        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        # Scrollable categories area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.categories_container = QWidget()
        self.categories_layout = QVBoxLayout()
        self.categories_layout.setSpacing(4)
        self.categories_container.setLayout(self.categories_layout)

        scroll.setWidget(self.categories_container)
        main_layout.addWidget(scroll)

        # Refresh display
        self.refresh_categories()

        self.setLayout(main_layout)

    def update_data(self, df):
        """Update with transaction data"""
        self.df = df
        self.refresh_categories()

    def refresh_categories(self):
        """Refresh categories display"""
        # Clear existing
        for i in reversed(range(self.categories_layout.count())):
            widget = self.categories_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Add uncategorized first (if we have data)
        if self.df is not None and not self.df.empty:
            uncategorized_widget = UncategorizedWidget(self.df, self)
            uncategorized_widget.category_changed.connect(self.refresh_categories)
            self.categories_layout.addWidget(uncategorized_widget)

        # Add categories
        for name, data in sorted(self.categories.items()):
            cat_widget = ExpandableCategoryWidget(name, data, self.df, self)
            cat_widget.category_changed.connect(self.refresh_categories)
            self.categories_layout.addWidget(cat_widget)

        self.categories_layout.addStretch()

        # Update info
        if self.df is not None and not self.df.empty and 'categoria' in self.df.columns:
            uncategorized_count = len(self.df[self.df['categoria'] == 'Outros'])
            self.info_label.setText(f"{len(self.categories)} categorias | {uncategorized_count} sem categoria")
        else:
            self.info_label.setText(f"{len(self.categories)} categorias")

    def expand_all_categories(self):
        """Expand all category widgets"""
        for i in range(self.categories_layout.count()):
            widget = self.categories_layout.itemAt(i).widget()
            if isinstance(widget, (ExpandableCategoryWidget, UncategorizedWidget)):
                if not widget.expanded:
                    widget.toggle_expand()

    def recategorize_transaction(self, transaction, from_category='Outros'):
        """Recategorize a transaction"""
        dialog = RecategorizeDialog(transaction, self.categories, self)

        if dialog.exec_() == QDialog.Accepted:
            new_category = dialog.selected_category

            # Update dataframe
            if self.df is not None and not self.df.empty:
                # Find and update the transaction
                mask = (
                    (self.df['descricao'] == transaction.get('descricao')) &
                    (self.df['data'] == transaction.get('data')) &
                    (self.df['valor'] == transaction.get('valor'))
                )
                self.df.loc[mask, 'categoria'] = new_category

            # Add keyword if requested
            if dialog.add_keyword and dialog.new_keyword:
                if new_category in self.categories:
                    keywords = self.categories[new_category].get('keywords', [])
                    if dialog.new_keyword.lower() not in [k.lower() for k in keywords]:
                        keywords.append(dialog.new_keyword.lower())
                        self.categories[new_category]['keywords'] = keywords

                        # Save if custom category
                        if new_category in self.custom_categories:
                            self.custom_categories[new_category] = self.categories[new_category]
                            config.set('custom_categories', self.custom_categories)

                        QMessageBox.information(
                            self,
                            "Keyword Adicionada",
                            f"Keyword '{dialog.new_keyword}' adicionada à categoria '{new_category}'"
                        )

            self.refresh_categories()
            QMessageBox.information(self, "Sucesso", f"Transação recategorizada para '{new_category}'")

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

        keywords = [k.strip().lower() for k in keywords_text.split('\n') if k.strip()]

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
        # Show details
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

    def set_category_preset(self, preset):
        """Set the category preset to use for recategorization"""
        self.category_preset = preset

    def recategorize_all(self):
        """Recategorize all transactions using the current category preset"""
        if self.df is None or self.df.empty:
            QMessageBox.warning(
                self,
                "Sem Dados",
                "Não há transações para recategorizar.\nImporte arquivos OFX primeiro."
            )
            return

        # Confirm action
        reply = QMessageBox.question(
            self,
            "Recategorizar Tudo",
            "Tem certeza que deseja recategorizar todas as transações?\n\n"
            "Isso irá aplicar as regras de categorização do plano atual\n"
            "e pode alterar categorias atribuídas manualmente.\n\n"
            f"Total de transações: {len(self.df)}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        try:
            # Create categorizer with current preset
            categorizer = TransactionCategorizer(category_preset=self.category_preset)

            # Recategorize dataframe
            self.df = categorizer.categorize_dataframe(self.df)

            # Refresh display
            self.refresh_categories()

            QMessageBox.information(
                self,
                "Sucesso",
                f"Todas as {len(self.df)} transações foram recategorizadas com sucesso!\n\n"
                "As alterações foram aplicadas aos dados em memória.\n"
                "Não esqueça de salvar o projeto para manter as mudanças."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao recategorizar transações:\n{str(e)}"
            )
