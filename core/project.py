"""
Project Manager - Save and load complete application state
"""

import pickle
import gzip
import json
import os
from datetime import datetime
from pathlib import Path


class Project:
    """Manages project files with all application data and configurations"""

    VERSION = "1.0"

    def __init__(self):
        self.data = {
            'version': self.VERSION,
            'created_at': None,
            'modified_at': None,
            'dataframe': None,
            'duplicates': [],
            'custom_categories': {},  # Custom user categorizations
            'config': {
                'person_type': 'fisica',  # 'fisica' or 'juridica'
                'business_sector': None,  # For juridica: 'travel_agency', 'retail', etc.
                'category_preset': 'personal',  # 'personal', 'business', 'chart_of_accounts', 'custom'
            },
            'metadata': {
                'name': 'Projeto Sem Título',
                'description': '',
                'total_transactions': 0,
                'banks': [],
                'date_range': None,
            }
        }

    def save(self, file_path, df=None, duplicates=None, custom_categories=None, config=None, metadata=None):
        """
        Save project to file

        Args:
            file_path: Path to save the project file
            df: DataFrame with transactions
            duplicates: List of duplicate transactions
            custom_categories: Dict of custom categorizations
            config: Configuration dict
            metadata: Project metadata dict
        """
        # Update data
        if df is not None:
            self.data['dataframe'] = df

            # Auto-update metadata from DataFrame
            if not df.empty:
                self.data['metadata']['total_transactions'] = len(df)
                if 'banco' in df.columns:
                    self.data['metadata']['banks'] = df['banco'].unique().tolist()
                if 'data_dt' in df.columns:
                    self.data['metadata']['date_range'] = {
                        'start': df['data_dt'].min().isoformat(),
                        'end': df['data_dt'].max().isoformat()
                    }

        if duplicates is not None:
            self.data['duplicates'] = duplicates

        if custom_categories is not None:
            self.data['custom_categories'] = custom_categories

        if config is not None:
            self.data['config'].update(config)

        if metadata is not None:
            self.data['metadata'].update(metadata)

        # Set timestamps
        if self.data['created_at'] is None:
            self.data['created_at'] = datetime.now().isoformat()
        self.data['modified_at'] = datetime.now().isoformat()

        # Save with gzip compression
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with gzip.open(file_path, 'wb') as f:
                pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)

            return True, f"Projeto salvo com sucesso: {file_path}"

        except Exception as e:
            return False, f"Erro ao salvar projeto: {str(e)}"

    def load(self, file_path):
        """
        Load project from file

        Args:
            file_path: Path to the project file

        Returns:
            tuple: (success, message, data_dict)
        """
        try:
            if not os.path.exists(file_path):
                return False, "Arquivo de projeto não encontrado", None

            with gzip.open(file_path, 'rb') as f:
                loaded_data = pickle.load(f)

            # Validate version
            if loaded_data.get('version') != self.VERSION:
                return False, f"Versão do projeto incompatível: {loaded_data.get('version')}", None

            self.data = loaded_data
            return True, "Projeto carregado com sucesso", self.data

        except Exception as e:
            return False, f"Erro ao carregar projeto: {str(e)}", None

    def get_dataframe(self):
        """Get the loaded DataFrame"""
        return self.data.get('dataframe')

    def get_duplicates(self):
        """Get the duplicates list"""
        return self.data.get('duplicates', [])

    def get_custom_categories(self):
        """Get custom categorizations"""
        return self.data.get('custom_categories', {})

    def get_config(self):
        """Get project configuration"""
        return self.data.get('config', {})

    def get_metadata(self):
        """Get project metadata"""
        return self.data.get('metadata', {})

    @staticmethod
    def get_default_projects_dir():
        """Get default directory for projects"""
        home = Path.home()
        projects_dir = home / "OFX-Projetos"
        projects_dir.mkdir(parents=True, exist_ok=True)
        return str(projects_dir)

    @staticmethod
    def get_recent_projects(max_count=10):
        """
        Get list of recent project files

        Returns:
            list: List of recent project file paths
        """
        projects_dir = Path(Project.get_default_projects_dir())

        if not projects_dir.exists():
            return []

        # Find all .ofxproj files
        project_files = list(projects_dir.glob("*.ofxproj"))

        # Sort by modification time (most recent first)
        project_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        return [str(f) for f in project_files[:max_count]]

    @staticmethod
    def get_project_info(file_path):
        """
        Get basic info about a project without fully loading it

        Args:
            file_path: Path to project file

        Returns:
            dict: Project info or None if error
        """
        try:
            with gzip.open(file_path, 'rb') as f:
                data = pickle.load(f)

            return {
                'name': data['metadata'].get('name', 'Sem Título'),
                'description': data['metadata'].get('description', ''),
                'modified_at': data.get('modified_at', ''),
                'total_transactions': data['metadata'].get('total_transactions', 0),
                'banks': data['metadata'].get('banks', []),
                'date_range': data['metadata'].get('date_range'),
                'person_type': data['config'].get('person_type', 'fisica'),
                'business_sector': data['config'].get('business_sector'),
            }

        except Exception as e:
            return None
