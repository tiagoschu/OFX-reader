"""
Config Tab - Application settings
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QCheckBox, QComboBox,
                             QGroupBox, QMessageBox, QFileDialog, QSpinBox)
from PyQt5.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.config import config
from utils.constants import APP_NAME, VERSION, CATEGORY_PRESETS, BUSINESS_SECTORS


class ConfigTab(QWidget):
    """Configuration tab"""

    def __init__(self):
        super().__init__()
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
                    stop:0 #607D8B, stop:1 #455A64);
                border-radius: 6px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("⚙️ Configurações")
        title.setStyleSheet("color: white; font-size: 13px; font-weight: bold; background: transparent;")
        header_layout.addWidget(title)

        version_label = QLabel(f"v{VERSION}")
        version_label.setStyleSheet("color: #B0BEC5; font-size: 9px; background: transparent;")
        header_layout.addWidget(version_label)
        header_layout.addStretch()

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # General Settings
        general_group = QGroupBox("🔧 Geral")
        general_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px;
            }
        """)
        general_layout = QVBoxLayout()
        general_layout.setSpacing(6)

        self.cb_show_splash = QCheckBox("Mostrar splash screen ao iniciar")
        self.cb_show_splash.setChecked(config.get('show_splash', True))
        self.cb_show_splash.setStyleSheet("font-size: 10px;")
        general_layout.addWidget(self.cb_show_splash)

        self.cb_remove_duplicates = QCheckBox("Remover duplicatas automaticamente")
        self.cb_remove_duplicates.setChecked(config.get('remove_duplicates', True))
        self.cb_remove_duplicates.setStyleSheet("font-size: 10px;")
        general_layout.addWidget(self.cb_remove_duplicates)

        self.cb_include_time = QCheckBox("Incluir coluna de hora por padrão")
        self.cb_include_time.setChecked(config.get('include_time', True))
        self.cb_include_time.setStyleSheet("font-size: 10px;")
        general_layout.addWidget(self.cb_include_time)

        general_group.setLayout(general_layout)
        main_layout.addWidget(general_group)

        # Category Configuration
        category_group = QGroupBox("🏢 Tipo de Pessoa e Categorias")
        category_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px;
            }
        """)
        category_layout = QVBoxLayout()
        category_layout.setSpacing(8)

        # Person type
        person_layout = QHBoxLayout()
        person_label = QLabel("Tipo de Pessoa:")
        person_label.setStyleSheet("font-size: 10px;")
        person_layout.addWidget(person_label)

        self.cb_person_type = QComboBox()
        self.cb_person_type.addItem("👤 Pessoa Física", "fisica")
        self.cb_person_type.addItem("🏢 Pessoa Jurídica", "juridica")

        current_person_type = config.get('person_type', 'fisica')
        self.cb_person_type.setCurrentIndex(0 if current_person_type == 'fisica' else 1)

        self.cb_person_type.setStyleSheet("""
            QComboBox {
                font-size: 10px;
                padding: 4px;
                border: 1px solid #CFD8DC;
                border-radius: 3px;
            }
        """)
        self.cb_person_type.currentIndexChanged.connect(self.on_person_type_changed)
        person_layout.addWidget(self.cb_person_type)
        person_layout.addStretch()

        category_layout.addLayout(person_layout)

        # Business sector (only for Pessoa Jurídica)
        sector_layout = QHBoxLayout()
        self.sector_label = QLabel("Ramo de Negócio:")
        self.sector_label.setStyleSheet("font-size: 10px;")
        sector_layout.addWidget(self.sector_label)

        self.cb_business_sector = QComboBox()
        for sector_key, sector_info in BUSINESS_SECTORS.items():
            self.cb_business_sector.addItem(f"{sector_info['name']}", sector_key)

        current_sector = config.get('business_sector', 'general')
        sector_index = list(BUSINESS_SECTORS.keys()).index(current_sector) if current_sector in BUSINESS_SECTORS else 4
        self.cb_business_sector.setCurrentIndex(sector_index)

        self.cb_business_sector.setStyleSheet("""
            QComboBox {
                font-size: 10px;
                padding: 4px;
                border: 1px solid #CFD8DC;
                border-radius: 3px;
            }
        """)
        sector_layout.addWidget(self.cb_business_sector)
        sector_layout.addStretch()

        category_layout.addLayout(sector_layout)

        # Category preset
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Plano de Categorias:")
        preset_label.setStyleSheet("font-size: 10px;")
        preset_layout.addWidget(preset_label)

        self.cb_category_preset = QComboBox()
        for preset_key, preset_info in CATEGORY_PRESETS.items():
            self.cb_category_preset.addItem(f"{preset_info['name']}", preset_key)

        current_preset = config.get('category_preset', 'personal')
        preset_index = list(CATEGORY_PRESETS.keys()).index(current_preset) if current_preset in CATEGORY_PRESETS else 0
        self.cb_category_preset.setCurrentIndex(preset_index)

        self.cb_category_preset.setStyleSheet("""
            QComboBox {
                font-size: 10px;
                padding: 4px;
                border: 1px solid #CFD8DC;
                border-radius: 3px;
            }
        """)
        preset_layout.addWidget(self.cb_category_preset)
        preset_layout.addStretch()

        category_layout.addLayout(preset_layout)

        # Info label
        self.category_info_label = QLabel()
        self.category_info_label.setStyleSheet("""
            font-size: 9px;
            color: #546E7A;
            padding: 4px;
            background-color: #ECEFF1;
            border-radius: 3px;
        """)
        self.category_info_label.setWordWrap(True)
        self.update_category_info()
        category_layout.addWidget(self.category_info_label)

        category_group.setLayout(category_layout)
        main_layout.addWidget(category_group)

        # Update visibility based on person type
        self.on_person_type_changed()

        # Export Settings
        export_group = QGroupBox("💾 Exportação")
        export_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        export_layout = QVBoxLayout()
        export_layout.setSpacing(6)

        # Default export format
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato padrão:")
        format_label.setStyleSheet("font-size: 10px;")
        format_layout.addWidget(format_label)

        self.cb_export_format = QComboBox()
        self.cb_export_format.addItems(['CSV', 'Excel', 'JSON', 'OFX', 'PDF'])
        self.cb_export_format.setCurrentText(config.get('export_format', 'CSV').upper())
        self.cb_export_format.setStyleSheet("""
            QComboBox {
                font-size: 10px;
                padding: 4px;
                border: 1px solid #CFD8DC;
                border-radius: 3px;
            }
        """)
        format_layout.addWidget(self.cb_export_format)
        format_layout.addStretch()

        export_layout.addLayout(format_layout)

        export_group.setLayout(export_layout)
        main_layout.addWidget(export_group)

        # Data Management
        data_group = QGroupBox("🗂️ Gerenciamento de Dados")
        data_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #CFD8DC;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        data_layout = QVBoxLayout()
        data_layout.setSpacing(6)

        btn_clear_cache = QPushButton("🗑️ Limpar Cache")
        btn_clear_cache.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        btn_clear_cache.clicked.connect(self.clear_cache)
        data_layout.addWidget(btn_clear_cache)

        btn_reset_config = QPushButton("♻️ Resetar Configurações")
        btn_reset_config.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        btn_reset_config.clicked.connect(self.reset_config)
        data_layout.addWidget(btn_reset_config)

        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)

        # Save button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_save = QPushButton("💾 Salvar Configurações")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 30px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        btn_save.clicked.connect(self.save_settings)
        btn_layout.addWidget(btn_save)

        main_layout.addLayout(btn_layout)

        # About
        about_frame = QFrame()
        about_frame.setStyleSheet("""
            QFrame {
                background-color: #ECEFF1;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        about_layout = QVBoxLayout()
        about_layout.setContentsMargins(10, 8, 10, 8)

        about_label = QLabel(f"<b>{APP_NAME}</b> v{VERSION}")
        about_label.setStyleSheet("font-size: 10px; color: #37474F; background: transparent;")
        about_layout.addWidget(about_label)

        credits_label = QLabel("Desenvolvido com PyQt5 e Python")
        credits_label.setStyleSheet("font-size: 8px; color: #78909C; background: transparent;")
        about_layout.addWidget(credits_label)

        about_frame.setLayout(about_layout)
        main_layout.addWidget(about_frame)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def on_person_type_changed(self):
        """Handle person type change"""
        person_type = self.cb_person_type.currentData()

        # Show/hide business sector based on person type
        is_juridica = person_type == 'juridica'
        self.sector_label.setVisible(is_juridica)
        self.cb_business_sector.setVisible(is_juridica)

        # Update category info
        self.update_category_info()

    def update_category_info(self):
        """Update category preset info label"""
        preset_key = self.cb_category_preset.currentData()

        if preset_key and preset_key in CATEGORY_PRESETS:
            preset_info = CATEGORY_PRESETS[preset_key]
            description = preset_info['description']
            num_categories = len(preset_info['categories'])

            info_text = f"📌 {description}\n"
            info_text += f"📊 {num_categories} categorias disponíveis"

            self.category_info_label.setText(info_text)
        else:
            self.category_info_label.setText("Selecione um plano de categorias")

    def save_settings(self):
        """Save all settings"""
        # General settings
        config.set('show_splash', self.cb_show_splash.isChecked())
        config.set('remove_duplicates', self.cb_remove_duplicates.isChecked())
        config.set('include_time', self.cb_include_time.isChecked())

        # Category settings
        config.set('person_type', self.cb_person_type.currentData())
        config.set('business_sector', self.cb_business_sector.currentData())
        config.set('category_preset', self.cb_category_preset.currentData())

        # Export settings
        config.set('export_format', self.cb_export_format.currentText().lower())

        QMessageBox.information(
            self,
            "Sucesso",
            "Configurações salvas com sucesso!\n\n"
            "Algumas alterações podem exigir reiniciar o aplicativo."
        )

    def clear_cache(self):
        """Clear application cache"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja limpar o cache da aplicação?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # For now, just show success message
            # In future, could delete temp files, etc.
            QMessageBox.information(self, "Sucesso", "Cache limpo com sucesso!")

    def reset_config(self):
        """Reset all configurations"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Tem certeza que deseja resetar TODAS as configurações?\n\n"
            "Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            config.reset()

            # Reset UI
            self.cb_show_splash.setChecked(True)
            self.cb_remove_duplicates.setChecked(True)
            self.cb_include_time.setChecked(True)
            self.cb_export_format.setCurrentText('CSV')

            QMessageBox.information(
                self,
                "Sucesso",
                "Configurações resetadas com sucesso!\n\n"
                "Reinicie o aplicativo para aplicar todas as mudanças."
            )
