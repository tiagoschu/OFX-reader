"""
Project Configuration Dialog - Set up project type and categories
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QComboBox, QGroupBox,
                             QTextEdit, QLineEdit, QButtonGroup, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from utils.constants import CATEGORY_PRESETS, BUSINESS_SECTORS


class ProjectConfigDialog(QDialog):
    """Dialog to configure project settings when creating new project"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.person_type = 'fisica'
        self.business_sector = 'general'
        self.category_preset = 'personal'  # Automatically determined
        self.project_name = ''
        self.project_description = ''
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Configuração do Projeto")
        self.setModal(True)
        self.setMinimumSize(600, 480)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("⚙️ Configuração do Novo Projeto")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #1976D2; margin-bottom: 10px;")
        layout.addWidget(header)

        subtitle = QLabel("O plano de contas será configurado automaticamente de acordo com o tipo selecionado")
        subtitle.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # Project Name
        name_group = QGroupBox("📝 Nome do Projeto")
        name_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
            }
        """)
        name_layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Digite o nome do projeto...")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                font-size: 10px;
            }
        """)
        name_layout.addWidget(self.name_input)

        name_group.setLayout(name_layout)
        layout.addWidget(name_group)

        # Person Type
        person_group = QGroupBox("👤 Tipo de Pessoa")
        person_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
            }
        """)
        person_layout = QHBoxLayout()
        person_layout.setSpacing(20)

        self.person_group = QButtonGroup()

        self.rb_fisica = QRadioButton("👤 Pessoa Física")
        self.rb_fisica.setChecked(True)
        self.rb_fisica.setStyleSheet("font-size: 10px;")
        self.rb_fisica.toggled.connect(self.on_person_type_changed)
        self.person_group.addButton(self.rb_fisica, 0)
        person_layout.addWidget(self.rb_fisica)

        self.rb_juridica = QRadioButton("🏢 Pessoa Jurídica")
        self.rb_juridica.setStyleSheet("font-size: 10px;")
        self.rb_juridica.toggled.connect(self.on_person_type_changed)
        self.person_group.addButton(self.rb_juridica, 1)
        person_layout.addWidget(self.rb_juridica)

        person_layout.addStretch()
        person_group.setLayout(person_layout)
        layout.addWidget(person_group)

        # Business Sector (only for Juridica)
        self.sector_group = QGroupBox("🏢 Ramo de Negócio")
        self.sector_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
            }
        """)
        sector_layout = QVBoxLayout()
        sector_layout.setSpacing(8)

        self.cb_business_sector = QComboBox()
        for sector_key, sector_info in BUSINESS_SECTORS.items():
            icon = "✈️" if sector_key == "travel_agency" else "🏢"
            self.cb_business_sector.addItem(f"{icon} {sector_info['name']}", sector_key)

        self.cb_business_sector.setStyleSheet("""
            QComboBox {
                font-size: 12px;
                font-weight: bold;
                padding: 12px;
                border: 2px solid #CFD8DC;
                border-radius: 4px;
                min-height: 40px;
            }
            QComboBox::drop-down {
                border: none;
                width: 35px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                font-size: 12px;
                font-weight: bold;
                padding: 8px;
                selection-background-color: #E3F2FD;
                selection-color: #000;
            }
            QComboBox QAbstractItemView::item {
                min-height: 40px;
                padding: 10px;
            }
        """)
        self.cb_business_sector.currentIndexChanged.connect(self.on_business_sector_changed)
        sector_layout.addWidget(self.cb_business_sector)

        # Sector description
        self.sector_desc = QLabel()
        self.sector_desc.setStyleSheet("""
            font-size: 9px;
            color: #546E7A;
            padding: 6px;
            background-color: #ECEFF1;
            border-radius: 3px;
        """)
        self.sector_desc.setWordWrap(True)
        sector_layout.addWidget(self.sector_desc)

        self.sector_group.setLayout(sector_layout)
        layout.addWidget(self.sector_group)

        # Auto-configuration info display (replaces manual category preset selection)
        self.auto_config_info = QLabel()
        self.auto_config_info.setStyleSheet("""
            font-size: 10px;
            color: #1976D2;
            padding: 12px;
            background-color: #E3F2FD;
            border-radius: 4px;
            border-left: 4px solid #1976D2;
        """)
        self.auto_config_info.setWordWrap(True)
        layout.addWidget(self.auto_config_info)

        # Preview button
        btn_preview = QPushButton("👁️ Ver Detalhes (Categorias e DRE)")
        btn_preview.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn_preview.clicked.connect(self.show_preview)
        layout.addWidget(btn_preview)

        # Info box
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF9C4;
                border: 1px solid #FBC02D;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout()

        info_label = QLabel(
            "⚡ <b>Importante:</b> O plano de categorias e estrutura do DRE serão configurados "
            "automaticamente de acordo com o tipo de pessoa e ramo de negócio selecionados. "
            "Você pode recategorizar os dados a qualquer momento na aba Categorias."
        )
        info_label.setStyleSheet("font-size: 11px; color: #F57F17; background: transparent; font-weight: bold;")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 25px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_create = QPushButton("Criar Projeto")
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 25px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        btn_create.clicked.connect(self.accept)
        btn_layout.addWidget(btn_create)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Initialize
        self.on_person_type_changed()
        self.update_auto_config_display()

    def on_person_type_changed(self):
        """Handle person type change"""
        is_juridica = self.rb_juridica.isChecked()
        self.person_type = 'juridica' if is_juridica else 'fisica'

        # Show/hide business sector
        self.sector_group.setVisible(is_juridica)

        # Automatically determine category preset
        if is_juridica:
            # For juridica, preset depends on business sector
            self.on_business_sector_changed()
        else:
            # For fisica, always use personal preset
            self.category_preset = 'personal'
            self.update_auto_config_display()

    def on_business_sector_changed(self):
        """Handle business sector change and automatically set category preset"""
        sector_key = self.cb_business_sector.currentData()
        if sector_key and sector_key in BUSINESS_SECTORS:
            sector_info = BUSINESS_SECTORS[sector_key]
            self.business_sector = sector_key
            self.sector_desc.setText(f"📌 {sector_info['description']}")

            # Automatically determine category preset based on business sector
            self.category_preset = sector_info.get('preset', 'business')

            # Update the auto-config display
            self.update_auto_config_display()

    def update_auto_config_display(self):
        """Update the auto-configuration info display"""
        if self.category_preset and self.category_preset in CATEGORY_PRESETS:
            preset_info = CATEGORY_PRESETS[self.category_preset]
            num_categories = len(preset_info['categories'])

            person_type_label = "👤 Pessoa Física" if self.person_type == 'fisica' else "🏢 Pessoa Jurídica"

            if self.person_type == 'juridica':
                sector_info = BUSINESS_SECTORS.get(self.business_sector, {})
                sector_label = sector_info.get('name', 'Geral')
                config_text = (
                    f"<b>✓ Configuração Automática:</b><br>"
                    f"• Tipo: {person_type_label}<br>"
                    f"• Ramo: {sector_label}<br>"
                    f"• Plano: {preset_info['name']}<br>"
                    f"• {num_categories} categorias pré-configuradas<br>"
                    f"• DRE adaptado para este tipo de negócio"
                )
            else:
                config_text = (
                    f"<b>✓ Configuração Automática:</b><br>"
                    f"• Tipo: {person_type_label}<br>"
                    f"• Plano: {preset_info['name']}<br>"
                    f"• {num_categories} categorias pré-configuradas<br>"
                    f"• DRE para controle pessoal"
                )

            self.auto_config_info.setText(config_text)

    def show_preview(self):
        """Show preview of categories and DRE structure with full list"""
        from PyQt5.QtWidgets import QTabWidget, QTextBrowser, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
        from utils.dre_structures import get_dre_structure

        if not self.category_preset or self.category_preset not in CATEGORY_PRESETS:
            return

        preset_info = CATEGORY_PRESETS[self.category_preset]

        # Create preview dialog
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle(f"Preview: {preset_info['name']}")
        preview_dialog.setMinimumSize(900, 700)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header = QLabel(f"📋 {preset_info['name']}")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #1976D2; padding: 10px; background: #E3F2FD; border-radius: 4px;")
        layout.addWidget(header)

        subtitle = QLabel(f"Total: {len(preset_info['categories'])} categorias pré-configuradas")
        subtitle.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(subtitle)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #CFD8DC;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #F5F5F5;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
        """)

        # Categories table - Show ALL categories
        categories_table = QTableWidget()
        categories_table.setColumnCount(4)
        categories_table.setHorizontalHeaderLabels(['Categoria', 'Tipo', 'Keywords', 'Ícone'])
        categories_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        categories_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        categories_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        categories_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        categories_table.setAlternatingRowColors(True)
        categories_table.setStyleSheet("""
            QTableWidget {
                font-size: 11px;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        # Populate ALL categories
        categories_table.setRowCount(len(preset_info['categories']))
        for row, (cat_name, cat_data) in enumerate(sorted(preset_info['categories'].items())):
            # Category name
            name_item = QTableWidgetItem(cat_name)
            categories_table.setItem(row, 0, name_item)

            # Type
            cat_type = cat_data.get('type', 'other')
            type_item = QTableWidgetItem(cat_type)
            categories_table.setItem(row, 1, type_item)

            # Keywords
            keywords = cat_data.get('keywords', [])
            keywords_text = ', '.join(keywords[:5])  # Show first 5
            if len(keywords) > 5:
                keywords_text += f' ... (+{len(keywords)-5})'
            keywords_item = QTableWidgetItem(keywords_text)
            categories_table.setItem(row, 2, keywords_item)

            # Icon
            icon_item = QTableWidgetItem(cat_data.get('icon', '📁'))
            categories_table.setItem(row, 3, icon_item)

        tabs.addTab(categories_table, "📂 Categorias (TODAS)")

        # DRE tab with better formatting
        dre_browser = QTextBrowser()
        dre_browser.setStyleSheet("font-size: 12px; padding: 10px;")
        dre_structure = get_dre_structure(self.category_preset)
        dre_html = f"<h2 style='color: #1976D2;'>{dre_structure['title']}</h2><hr>"
        dre_html += "<div style='font-family: monospace; line-height: 1.8;'>"

        for item in dre_structure['items']:
            if item['is_total']:
                dre_html += f"<p style='font-weight: bold; color: #1976D2; font-size: 13px;'>{item['label']}</p>"
            else:
                dre_html += f"<p style='padding-left: 20px; color: #424242;'>{item['label']}</p>"

        dre_html += "</div>"
        dre_browser.setHtml(dre_html)
        tabs.addTab(dre_browser, "💼 Estrutura DRE")

        layout.addWidget(tabs)

        # Info note
        note = QLabel("ℹ️ Estas categorias serão aplicadas automaticamente. Você poderá recategorizar depois na aba Categorias.")
        note.setStyleSheet("""
            background: #E3F2FD;
            padding: 10px;
            border-left: 4px solid #2196F3;
            color: #1976D2;
            font-size: 10px;
            border-radius: 4px;
        """)
        note.setWordWrap(True)
        layout.addWidget(note)

        # Close button
        btn_close = QPushButton("✓ Entendi - Fechar")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 25px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        btn_close.clicked.connect(preview_dialog.accept)
        layout.addWidget(btn_close)

        preview_dialog.setLayout(layout)
        preview_dialog.exec_()

    def get_config(self):
        """Get the selected configuration"""
        return {
            'name': self.name_input.text() or 'Projeto Sem Título',
            'person_type': self.person_type,
            'business_sector': self.business_sector if self.person_type == 'juridica' else None,
            'category_preset': self.category_preset
        }
