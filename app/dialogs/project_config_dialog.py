"""
Project Configuration Dialog - REWRITTEN FROM SCRATCH
Clean, well-structured layout for project setup
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QComboBox, QGroupBox,
                             QLineEdit, QButtonGroup, QFrame, QScrollArea, QWidget,
                             QTabWidget, QTextBrowser, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSizePolicy, QAbstractItemView, QFileDialog,
                             QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import platform
import subprocess
import os

from utils.constants import CATEGORY_PRESETS, BUSINESS_SECTORS


class ProjectConfigDialog(QDialog):
    """Clean, well-structured dialog for project configuration"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.person_type = 'fisica'
        self.business_sector = 'general'
        self.category_preset = 'personal'
        self.init_ui()

    def init_ui(self):
        """Initialize UI with clean structure"""
        self.setWindowTitle("Configuração do Projeto")
        self.setModal(True)
        self.resize(650, 600)

        # Main layout with scroll area
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")

        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)

        # === HEADER ===
        header_label = QLabel("⚙️ Configuração do Novo Projeto")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #1976D2;")
        content_layout.addWidget(header_label)

        subtitle = QLabel("Configure o tipo de projeto. As categorias serão aplicadas automaticamente.")
        subtitle.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 10px;")
        subtitle.setWordWrap(True)
        content_layout.addWidget(subtitle)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("background: #E0E0E0;")
        sep1.setFixedHeight(2)
        content_layout.addWidget(sep1)

        # === PROJECT NAME ===
        name_label = QLabel("📝 Nome do Projeto")
        name_label.setFont(QFont("Arial", 11, QFont.Bold))
        content_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Digite o nome do projeto...")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        content_layout.addWidget(self.name_input)

        # === PERSON TYPE ===
        person_label = QLabel("👤 Tipo de Pessoa")
        person_label.setFont(QFont("Arial", 11, QFont.Bold))
        content_layout.addWidget(person_label)

        person_buttons = QHBoxLayout()
        person_buttons.setSpacing(15)

        self.person_group = QButtonGroup()

        self.rb_fisica = QRadioButton("👤 Pessoa Física")
        self.rb_fisica.setChecked(True)
        self.rb_fisica.setStyleSheet("font-size: 12px; padding: 5px;")
        self.rb_fisica.toggled.connect(self.on_person_type_changed)
        self.person_group.addButton(self.rb_fisica, 0)
        person_buttons.addWidget(self.rb_fisica)

        self.rb_juridica = QRadioButton("🏢 Pessoa Jurídica")
        self.rb_juridica.setStyleSheet("font-size: 12px; padding: 5px;")
        self.rb_juridica.toggled.connect(self.on_person_type_changed)
        self.person_group.addButton(self.rb_juridica, 1)
        person_buttons.addWidget(self.rb_juridica)

        person_buttons.addStretch()
        content_layout.addLayout(person_buttons)

        # === BUSINESS SECTOR (hidden by default) ===
        self.sector_container = QWidget()
        sector_container_layout = QVBoxLayout()
        sector_container_layout.setContentsMargins(0, 0, 0, 0)
        sector_container_layout.setSpacing(10)

        sector_label = QLabel("🏢 Ramo de Negócio")
        sector_label.setFont(QFont("Arial", 11, QFont.Bold))
        sector_container_layout.addWidget(sector_label)

        self.cb_business_sector = QComboBox()
        self.cb_business_sector.setMaxVisibleItems(6)  # Limit dropdown height

        for sector_key, sector_info in BUSINESS_SECTORS.items():
            icon = sector_info.get('icon', '🏢')
            self.cb_business_sector.addItem(f"{icon}  {sector_info['name']}", sector_key)

        self.cb_business_sector.setStyleSheet("""
            QComboBox {
                padding: 12px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #2196F3;
                selection-background-color: #E3F2FD;
                selection-color: #000;
                font-size: 13px;
                font-weight: bold;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 35px;
                padding: 8px;
            }
        """)
        self.cb_business_sector.currentIndexChanged.connect(self.on_business_sector_changed)
        sector_container_layout.addWidget(self.cb_business_sector)

        # Sector description
        self.sector_desc = QLabel()
        self.sector_desc.setStyleSheet("""
            background: #F5F5F5;
            padding: 10px;
            border-left: 3px solid #2196F3;
            color: #424242;
            font-size: 11px;
            border-radius: 3px;
        """)
        self.sector_desc.setWordWrap(True)
        sector_container_layout.addWidget(self.sector_desc)

        self.sector_container.setLayout(sector_container_layout)
        self.sector_container.setVisible(False)  # Hidden by default
        content_layout.addWidget(self.sector_container)

        # === AUTO CONFIG INFO ===
        self.auto_info = QLabel()
        self.auto_info.setStyleSheet("""
            background: #E3F2FD;
            padding: 15px;
            border-left: 4px solid #2196F3;
            color: #1565C0;
            font-size: 12px;
            font-weight: bold;
            border-radius: 4px;
        """)
        self.auto_info.setWordWrap(True)
        content_layout.addWidget(self.auto_info)

        # === PREVIEW BUTTON ===
        btn_preview = QPushButton("👁️  Ver Categorias e Estrutura DRE")
        btn_preview.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        btn_preview.clicked.connect(self.show_preview)
        content_layout.addWidget(btn_preview)

        # === IMPORT/EXPORT BUTTONS ===
        import_layout = QHBoxLayout()
        import_layout.setSpacing(10)

        btn_import_categories = QPushButton("📥 Importar Categorias (CSV)")
        btn_import_categories.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #F57C00;
            }
        """)
        btn_import_categories.clicked.connect(self.import_categories)
        import_layout.addWidget(btn_import_categories)

        btn_download_template = QPushButton("📄 Baixar Templates")
        btn_download_template.setStyleSheet("""
            QPushButton {
                background: #9C27B0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7B1FA2;
            }
        """)
        btn_download_template.clicked.connect(self.download_templates)
        import_layout.addWidget(btn_download_template)

        content_layout.addLayout(import_layout)

        # === INFO NOTE ===
        info_note = QLabel(
            "💡 <b>Dica:</b> As categorias e DRE serão configurados automaticamente. "
            "Você pode recategorizar depois na aba Categorias."
        )
        info_note.setStyleSheet("""
            background: #FFF9C4;
            padding: 12px;
            border-left: 4px solid #FBC02D;
            color: #F57F17;
            font-size: 11px;
            border-radius: 4px;
        """)
        info_note.setWordWrap(True)
        content_layout.addWidget(info_note)

        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # === BOTTOM BUTTONS ===
        button_bar = QFrame()
        button_bar.setStyleSheet("background: #F5F5F5; border-top: 1px solid #E0E0E0;")
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 15, 20, 15)
        button_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #757575;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 30px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #616161;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)

        btn_create = QPushButton("✓  Criar Projeto")
        btn_create.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 30px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45A049;
            }
        """)
        btn_create.clicked.connect(self.accept)
        button_layout.addWidget(btn_create)

        button_bar.setLayout(button_layout)
        main_layout.addWidget(button_bar)

        self.setLayout(main_layout)

        # Initialize
        self.update_auto_info()

    def on_person_type_changed(self):
        """Handle person type change"""
        is_juridica = self.rb_juridica.isChecked()
        self.person_type = 'juridica' if is_juridica else 'fisica'

        # Show/hide business sector
        self.sector_container.setVisible(is_juridica)

        # Set preset
        if is_juridica:
            self.on_business_sector_changed()
        else:
            self.category_preset = 'personal'
            self.update_auto_info()

    def on_business_sector_changed(self):
        """Handle business sector change"""
        sector_key = self.cb_business_sector.currentData()
        if sector_key and sector_key in BUSINESS_SECTORS:
            sector_info = BUSINESS_SECTORS[sector_key]
            self.business_sector = sector_key
            self.sector_desc.setText(f"📌 {sector_info['description']}")

            # Auto-determine preset
            self.category_preset = sector_info.get('preset', 'business')
            self.update_auto_info()

    def update_auto_info(self):
        """Update auto-configuration info"""
        # Handle custom categories from CSV import
        if self.category_preset == 'custom' and hasattr(self, 'custom_categories'):
            num_cats = len(self.custom_categories)
            text = (
                f"<b>✓ Configuração Customizada (CSV):</b><br><br>"
                f"<b>Tipo:</b> {'🏢 Pessoa Jurídica' if self.person_type == 'juridica' else '👤 Pessoa Física'}<br>"
                f"<b>Plano:</b> Importado de CSV<br>"
                f"<b>Categorias:</b> {num_cats} categorias customizadas"
            )
            self.auto_info.setText(text)
            return

        if not self.category_preset or self.category_preset not in CATEGORY_PRESETS:
            return

        preset_info = CATEGORY_PRESETS[self.category_preset]
        num_cats = len(preset_info['categories'])

        if self.person_type == 'juridica':
            sector_info = BUSINESS_SECTORS.get(self.business_sector, {})
            text = (
                f"<b>✓ Configuração Automática:</b><br><br>"
                f"<b>Tipo:</b> 🏢 Pessoa Jurídica<br>"
                f"<b>Ramo:</b> {sector_info.get('name', 'Geral')}<br>"
                f"<b>Plano:</b> {preset_info['name']}<br>"
                f"<b>Categorias:</b> {num_cats} pré-configuradas"
            )
        else:
            text = (
                f"<b>✓ Configuração Automática:</b><br><br>"
                f"<b>Tipo:</b> 👤 Pessoa Física<br>"
                f"<b>Plano:</b> {preset_info['name']}<br>"
                f"<b>Categorias:</b> {num_cats} pré-configuradas"
            )

        self.auto_info.setText(text)

    def show_preview(self):
        """Show editable preview dialog with categories and DRE"""
        from utils.dre_structures import get_dre_structure

        if not self.category_preset or self.category_preset not in CATEGORY_PRESETS:
            return

        preset_info = CATEGORY_PRESETS[self.category_preset]

        # Create editable copy of categories
        editable_categories = {}
        for cat_name, cat_data in preset_info['categories'].items():
            editable_categories[cat_name] = cat_data.copy()

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar: {preset_info['name']}")
        dialog.resize(1050, 700)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel(f"📋 {preset_info['name']}")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #1976D2; padding: 10px; background: #E3F2FD; border-radius: 4px;")
        layout.addWidget(header)

        subtitle = QLabel(f"Você pode adicionar, editar ou remover categorias")
        subtitle.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(subtitle)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab {
                background: #F5F5F5;
                padding: 12px 25px;
                margin-right: 3px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
        """)

        # Categories tab with editable table
        cat_tab = QWidget()
        cat_layout = QVBoxLayout()
        cat_layout.setContentsMargins(10, 10, 10, 10)

        # Toolbar
        toolbar = QHBoxLayout()
        btn_add = QPushButton("➕ Adicionar Categoria")
        btn_add.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45A049;
            }
        """)

        toolbar.addWidget(btn_add)
        toolbar.addStretch()
        cat_layout.addLayout(toolbar)

        # Categories table
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['Categoria', 'Tipo', 'Keywords', 'Ícone', 'Código', 'Ação'])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        table.setStyleSheet("""
            QTableWidget {
                font-size: 11px;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background: #2196F3;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)

        def populate_table():
            """Populate table with current categories"""
            table.setRowCount(len(editable_categories))
            for row, (cat_name, cat_data) in enumerate(sorted(editable_categories.items())):
                # Category name (editable)
                table.setItem(row, 0, QTableWidgetItem(cat_name))

                # Type (editable)
                table.setItem(row, 1, QTableWidgetItem(cat_data.get('type', 'other')))

                # Keywords (editable, full list)
                keywords = cat_data.get('keywords', [])
                kw_text = '; '.join(keywords)
                table.setItem(row, 2, QTableWidgetItem(kw_text))

                # Icon (editable)
                table.setItem(row, 3, QTableWidgetItem(cat_data.get('icon', '📁')))

                # Code (editable)
                table.setItem(row, 4, QTableWidgetItem(cat_data.get('code', '')))

                # Delete button
                btn_delete = QPushButton("🗑️")
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background: #F44336;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        background: #D32F2F;
                    }
                """)
                btn_delete.setProperty('row', row)
                btn_delete.setProperty('cat_name', cat_name)
                btn_delete.clicked.connect(lambda checked, r=row, name=cat_name: delete_category(name))
                table.setCellWidget(row, 5, btn_delete)

        def add_category():
            """Add new category row"""
            new_name = f"Nova Categoria {len(editable_categories) + 1}"
            editable_categories[new_name] = {
                'type': 'other',
                'keywords': [],
                'icon': '📁',
                'code': '',
                'color': '#757575'
            }
            populate_table()

        def delete_category(cat_name):
            """Delete category"""
            if cat_name in editable_categories:
                del editable_categories[cat_name]
                populate_table()

        def save_edits():
            """Save table edits back to editable_categories"""
            # Clear and rebuild
            temp_cats = {}
            for row in range(table.rowCount()):
                name_item = table.item(row, 0)
                type_item = table.item(row, 1)
                kw_item = table.item(row, 2)
                icon_item = table.item(row, 3)
                code_item = table.item(row, 4)

                if name_item:
                    name = name_item.text().strip()
                    if name:
                        # Parse keywords
                        kw_text = kw_item.text() if kw_item else ''
                        keywords = [kw.strip() for kw in kw_text.split(';') if kw.strip()]

                        temp_cats[name] = {
                            'type': type_item.text() if type_item else 'other',
                            'keywords': keywords,
                            'icon': icon_item.text() if icon_item else '📁',
                            'code': code_item.text() if code_item else '',
                            'color': '#757575'
                        }

            return temp_cats

        # Connect buttons
        btn_add.clicked.connect(add_category)

        # Initial populate
        populate_table()

        cat_layout.addWidget(table)
        cat_tab.setLayout(cat_layout)
        tabs.addTab(cat_tab, "📂 Categorias (Editável)")

        # DRE structure (read-only)
        dre_browser = QTextBrowser()
        dre_browser.setStyleSheet("font-size: 12px; padding: 10px;")
        dre_struct = get_dre_structure(self.category_preset)
        html = f"<h2 style='color: #1976D2;'>{dre_struct['title']}</h2><hr>"
        html += "<div style='font-family: monospace; line-height: 2.0;'>"
        for item in dre_struct['items']:
            if item['is_total']:
                html += f"<p style='font-weight: bold; color: #1976D2; font-size: 13px;'>{item['label']}</p>"
            else:
                html += f"<p style='padding-left: 30px; color: #424242;'>{item['label']}</p>"
        html += "</div>"
        dre_browser.setHtml(html)
        tabs.addTab(dre_browser, "💼 DRE")

        layout.addWidget(tabs)

        # Action buttons
        btn_layout = QHBoxLayout()

        btn_cancel = QPushButton("✕ Cancelar")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 30px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #757575;
            }
        """)
        btn_cancel.clicked.connect(dialog.reject)

        btn_save = QPushButton("✓ Salvar e Aplicar")
        btn_save.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 30px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45A049;
            }
        """)

        def on_save():
            """Save changes and apply as custom preset"""
            final_cats = save_edits()
            if final_cats:
                self.custom_categories = final_cats
                self.category_preset = 'custom'
                self.update_auto_info()
                dialog.accept()

        btn_save.clicked.connect(on_save)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def import_categories(self):
        """Import custom categories from CSV"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from utils.csv_templates import CSVTemplates

        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Categorias",
            CSVTemplates.get_templates_dir(),
            "CSV Files (*.csv);;All Files (*.*)"
        )

        if not filepath:
            return

        try:
            # Parse CSV
            custom_categories = CSVTemplates.parse_categories_csv(filepath)

            # Show confirmation
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Categorias Importadas")
            msg.setText(f"✓ {len(custom_categories)} categorias importadas com sucesso!")
            msg.setInformativeText(
                f"As categorias customizadas serão aplicadas ao projeto.\n\n"
                f"Primeiras categorias:\n" +
                '\n'.join(list(custom_categories.keys())[:5]) +
                (f"\n... e mais {len(custom_categories) - 5}" if len(custom_categories) > 5 else "")
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            # Store custom categories (will be applied when project is created)
            self.custom_categories = custom_categories
            self.category_preset = 'custom'

            # Update info
            self.update_auto_info()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao Importar",
                f"Erro ao importar categorias:\n{str(e)}\n\n"
                f"Verifique se o arquivo está no formato correto."
            )

    def download_templates(self):
        """Generate and save template CSV files"""
        from PyQt5.QtWidgets import QMessageBox
        from utils.csv_templates import CSVTemplates
        import os

        try:
            # Generate templates
            cat_path = CSVTemplates.generate_categories_template()
            dre_path = CSVTemplates.generate_dre_template()

            templates_dir = CSVTemplates.get_templates_dir()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Templates Gerados")
            msg.setText("✓ Templates CSV criados com sucesso!")
            msg.setInformativeText(
                f"Os templates foram salvos em:\n\n"
                f"📂 {templates_dir}\n\n"
                f"📄 template_categorias.csv\n"
                f"📄 template_dre.csv\n\n"
                f"Edite os arquivos e importe para customizar seu projeto."
            )

            # Add button to open folder
            msg.setStandardButtons(QMessageBox.Ok)
            open_btn = msg.addButton("📂 Abrir Pasta", QMessageBox.ActionRole)

            result = msg.exec_()

            # Open folder if requested
            if msg.clickedButton() == open_btn:
                import platform
                import subprocess

                if platform.system() == 'Windows':
                    os.startfile(templates_dir)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.Popen(['open', templates_dir])
                else:  # Linux
                    subprocess.Popen(['xdg-open', templates_dir])

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao gerar templates:\n{str(e)}"
            )

    def get_config(self):
        """Get configuration"""
        config = {
            'name': self.name_input.text() or 'Projeto Sem Título',
            'person_type': self.person_type,
            'business_sector': self.business_sector if self.person_type == 'juridica' else None,
            'category_preset': self.category_preset
        }

        # Add custom categories if imported
        if hasattr(self, 'custom_categories'):
            config['custom_categories'] = self.custom_categories

        return config
