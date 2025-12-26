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
        self.category_preset = 'personal'
        self.project_name = ''
        self.project_description = ''
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Configuração do Projeto")
        self.setModal(True)
        self.setMinimumSize(600, 550)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("⚙️ Configuração do Novo Projeto")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #1976D2; margin-bottom: 10px;")
        layout.addWidget(header)

        subtitle = QLabel("Configure o tipo de pessoa e plano de categorias para seu projeto")
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
                font-size: 10px;
                padding: 8px;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
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

        # Category Preset
        preset_group = QGroupBox("📊 Plano de Categorias")
        preset_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
            }
        """)
        preset_layout = QVBoxLayout()
        preset_layout.setSpacing(8)

        self.cb_category_preset = QComboBox()
        for preset_key, preset_info in CATEGORY_PRESETS.items():
            icon = "📋" if preset_key == "personal" else "💼"
            self.cb_category_preset.addItem(f"{icon} {preset_info['name']}", preset_key)

        self.cb_category_preset.setStyleSheet("""
            QComboBox {
                font-size: 10px;
                padding: 8px;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
            }
        """)
        self.cb_category_preset.currentIndexChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.cb_category_preset)

        # Preset info
        self.preset_info = QLabel()
        self.preset_info.setStyleSheet("""
            font-size: 9px;
            color: #1976D2;
            padding: 8px;
            background-color: #E3F2FD;
            border-radius: 3px;
            border-left: 3px solid #1976D2;
        """)
        self.preset_info.setWordWrap(True)
        preset_layout.addWidget(self.preset_info)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

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
            "💡 <b>Importante:</b> O plano de categorias define como suas transações serão "
            "classificadas e como o DRE será calculado. Escolha o mais adequado ao seu tipo de negócio."
        )
        info_label.setStyleSheet("font-size: 9px; color: #F57F17; background: transparent;")
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
        self.on_business_sector_changed()
        self.on_preset_changed()

    def on_person_type_changed(self):
        """Handle person type change"""
        is_juridica = self.rb_juridica.isChecked()
        self.person_type = 'juridica' if is_juridica else 'fisica'

        # Show/hide business sector
        self.sector_group.setVisible(is_juridica)

        # Auto-select appropriate preset
        if is_juridica:
            # For juridica, use business or travel_agency preset
            self.cb_category_preset.setCurrentIndex(1)  # business
        else:
            # For fisica, use personal preset
            self.cb_category_preset.setCurrentIndex(0)  # personal

    def on_business_sector_changed(self):
        """Handle business sector change"""
        sector_key = self.cb_business_sector.currentData()
        if sector_key and sector_key in BUSINESS_SECTORS:
            sector_info = BUSINESS_SECTORS[sector_key]
            self.business_sector = sector_key
            self.sector_desc.setText(f"📌 {sector_info['description']}")

            # Auto-select matching preset
            preset_key = sector_info.get('preset', 'business')
            preset_index = list(CATEGORY_PRESETS.keys()).index(preset_key) if preset_key in CATEGORY_PRESETS else 1
            self.cb_category_preset.setCurrentIndex(preset_index)

    def on_preset_changed(self):
        """Handle preset change"""
        preset_key = self.cb_category_preset.currentData()
        if preset_key and preset_key in CATEGORY_PRESETS:
            preset_info = CATEGORY_PRESETS[preset_key]
            self.category_preset = preset_key

            num_categories = len(preset_info['categories'])
            self.preset_info.setText(
                f"📊 {preset_info['description']}\n"
                f"✓ {num_categories} categorias disponíveis\n"
                f"✓ DRE adaptado para este tipo de negócio"
            )

    def get_config(self):
        """Get the selected configuration"""
        return {
            'name': self.name_input.text() or 'Projeto Sem Título',
            'person_type': self.person_type,
            'business_sector': self.business_sector if self.person_type == 'juridica' else None,
            'category_preset': self.category_preset
        }
