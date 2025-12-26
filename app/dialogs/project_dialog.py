"""
Project Dialog - Create/Open project at startup
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QFrame, QLineEdit, QTextEdit, QFileDialog,
                             QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime
import os

from core.project import Project


class ProjectDialog(QDialog):
    """Dialog for creating or opening a project"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project = None
        self.project_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("OFX Consolidador Pro - Projetos")
        self.setModal(True)
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Bem-vindo ao OFX Consolidador Pro")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #00897B; margin-bottom: 10px;")
        layout.addWidget(header)

        subtitle = QLabel("Abra um projeto existente ou crie um novo para começar")
        subtitle.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # Main content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # Left side - Recent projects
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        recent_label = QLabel("📂 Projetos Recentes")
        recent_label.setFont(QFont("Arial", 11, QFont.Bold))
        recent_label.setStyleSheet("background: transparent; color: #424242;")
        left_layout.addWidget(recent_label)

        # Recent projects list
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #DDD;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEE;
            }
            QListWidget::item:hover {
                background-color: #E0F2F1;
            }
            QListWidget::item:selected {
                background-color: #00897B;
                color: white;
            }
        """)
        self.recent_list.itemDoubleClicked.connect(self.on_open_recent)
        left_layout.addWidget(self.recent_list)

        # Load recent projects
        self.load_recent_projects()

        open_recent_btn = QPushButton("📂 Abrir Selecionado")
        open_recent_btn.setStyleSheet("""
            QPushButton {
                background-color: #00897B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        open_recent_btn.clicked.connect(self.on_open_recent)
        left_layout.addWidget(open_recent_btn)

        left_frame.setLayout(left_layout)
        content_layout.addWidget(left_frame, 3)

        # Right side - Actions
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        actions_label = QLabel("⚡ Ações")
        actions_label.setFont(QFont("Arial", 11, QFont.Bold))
        actions_label.setStyleSheet("background: transparent; color: #424242;")
        right_layout.addWidget(actions_label)

        # New project button
        new_project_btn = QPushButton("✨ Criar Novo Projeto")
        new_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 15px;
                font-size: 12px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        new_project_btn.setMinimumHeight(50)
        new_project_btn.clicked.connect(self.on_new_project)
        right_layout.addWidget(new_project_btn)

        # Open from file button
        open_file_btn = QPushButton("📁 Abrir de Arquivo...")
        open_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6F00;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 15px;
                font-size: 12px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #E65100;
            }
        """)
        open_file_btn.setMinimumHeight(50)
        open_file_btn.clicked.connect(self.on_open_file)
        right_layout.addWidget(open_file_btn)

        # Continue without project button
        continue_btn = QPushButton("▶️  Continuar sem Projeto")
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 15px;
                font-size: 12px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        continue_btn.setMinimumHeight(50)
        continue_btn.clicked.connect(self.on_continue_without_project)
        right_layout.addWidget(continue_btn)

        right_layout.addStretch()

        # Info box
        info_box = QFrame()
        info_box.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border: 1px solid #2196F3;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        info_title = QLabel("💡 Dica")
        info_title.setFont(QFont("Arial", 9, QFont.Bold))
        info_title.setStyleSheet("background: transparent; color: #1976D2;")
        info_layout.addWidget(info_title)

        info_text = QLabel(
            "Projetos salvam seus dados, categorizações\n"
            "e configurações para uso futuro."
        )
        info_text.setStyleSheet("background: transparent; color: #424242; font-size: 9px;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        info_box.setLayout(info_layout)
        right_layout.addWidget(info_box)

        right_frame.setLayout(right_layout)
        content_layout.addWidget(right_frame, 2)

        layout.addLayout(content_layout)

        self.setLayout(layout)

    def load_recent_projects(self):
        """Load and display recent projects"""
        self.recent_list.clear()
        recent_projects = Project.get_recent_projects()

        if not recent_projects:
            item = QListWidgetItem("Nenhum projeto recente")
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(Qt.gray)
            self.recent_list.addItem(item)
            return

        for project_path in recent_projects:
            info = Project.get_project_info(project_path)

            if info:
                # Format display text
                name = info['name']
                trans_count = info['total_transactions']
                modified = info.get('modified_at', '')

                # Parse and format date
                try:
                    dt = datetime.fromisoformat(modified)
                    date_str = dt.strftime('%d/%m/%Y %H:%M')
                except:
                    date_str = 'Data desconhecida'

                display_text = f"{name}\n{trans_count} transações • {date_str}"

                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, project_path)
                self.recent_list.addItem(item)

    def on_new_project(self):
        """Create a new project"""
        self.project = Project()
        self.project_path = None
        self.accept()

    def on_open_file(self):
        """Open project from file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Projeto",
            Project.get_default_projects_dir(),
            "Projetos OFX (*.ofxproj);;Todos os arquivos (*.*)"
        )

        if file_path:
            self.load_project_file(file_path)

    def on_open_recent(self):
        """Open selected recent project"""
        current_item = self.recent_list.currentItem()

        if current_item:
            project_path = current_item.data(Qt.UserRole)

            if project_path:
                self.load_project_file(project_path)

    def load_project_file(self, file_path):
        """Load a project file"""
        project = Project()
        success, message, data = project.load(file_path)

        if success:
            self.project = project
            self.project_path = file_path
            self.accept()
        else:
            QMessageBox.critical(self, "Erro ao Abrir Projeto", message)

    def on_continue_without_project(self):
        """Continue without loading a project"""
        self.project = None
        self.project_path = None
        self.accept()

    def get_project(self):
        """Get the loaded project"""
        return self.project

    def get_project_path(self):
        """Get the project file path"""
        return self.project_path
