"""
Configuration manager for OFX Consolidador Pro
"""

import json
import os
from pathlib import Path


class Config:
    """Manages application configuration"""

    def __init__(self):
        self.config_dir = Path.home() / '.ofx_consolidador'
        self.config_file = self.config_dir / 'config.json'
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file"""
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)

        # Default configuration
        default_config = {
            'last_directory': str(Path.home()),
            'remove_duplicates': True,
            'include_time': True,
            'export_format': 'csv',
            'theme': 'light',
            'window_geometry': None,
            'custom_categories': {},
            'show_splash': True
        }

        # Try to load existing config
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults (in case new keys were added)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")

        return default_config

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()

    def reset(self):
        """Reset configuration to defaults"""
        if self.config_file.exists():
            self.config_file.unlink()
        self.config = self.load_config()


# Global config instance
config = Config()
