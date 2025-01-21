import json
from pathlib import Path

class SettingsManager:
    def __init__(self):
        self.settings_file = Path.home() / '.eisenhower_matrix' / 'settings.json'
        self.settings_file.parent.mkdir(exist_ok=True)
        self.load_settings()

    def load_settings(self):
        if self.settings_file.exists():
            with open(self.settings_file) as f:
                self.settings = json.load(f)
        else:
            self.settings = self.get_default_settings()
            self.save_settings()

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def get_default_settings(self):
        return {
            'appearance': {
                'background_color': '#646464',
                'text_color': '#FFFFFF',
                'opacity': 95,
            },
            'quadrants': {
                'names': [
                    "Important & Urgent",
                    "Important but Not Urgent",
                    "Not Important but Urgent",
                    "Not Important & Not Urgent"
                ]
            },
            'theme': 'dark'
        } 