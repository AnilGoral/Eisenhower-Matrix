import json
from pathlib import Path
from typing import Optional


class SettingsManager:
    def __init__(self, app_data_dir: Optional[str] = None):
        if app_data_dir:
            self.settings_file = Path(app_data_dir) / 'settings.json'
        else:
            self.settings_file = Path.home() / '.eisenhower_matrix' / 'settings.json'
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_settings()

    def load_settings(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, encoding='utf-8') as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                # Corrupt or unreadable — fall back to defaults
                self.settings = self.get_default_settings()
                self.save_settings()
        else:
            self.settings = self.get_default_settings()
            self.save_settings()

    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2)

    def get(self, section: str, key: str, default=None):
        """Get a setting value by section and key."""
        return self.settings.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value, auto_save: bool = True):
        """Set a setting value by section and key."""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        if auto_save:
            self.save_settings()

    def get_default_settings(self):
        return {
            'appearance': {
                'background_color': '#0f0f1a',
                'text_color': '#E8E8F0',
                'opacity': 97,
                'font_scale': 100,
            },
            'quadrants': {
                'names': [
                    "Important & Urgent",
                    "Important but Not Urgent",
                    "Not Important but Urgent",
                    "Not Important & Not Urgent"
                ]
            },
            'window': {
                'x': 100,
                'y': 100,
                'width': 750,
                'height': 580
            },
            'theme': 'dark',
            'auto_start': False
        }