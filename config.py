# heartlib/config.py - Add language settings
import json
import os
from pathlib import Path

class Config:
    """Configuration manager for HeartLib"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "settings.json"
        self.settings = self.load()
    
    def load(self):
        """Load settings from JSON file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return self.get_defaults()
    
    def save(self):
        """Save settings to JSON file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2)
    
    def get_defaults(self):
        """Return default settings"""
        return {
            "theme": "Light",
            "language": "en",
            "auto_sync_interval": 30,
            "default_loan_days": 14,
            "items_per_page": 50,
            "backup_enabled": True,
            "backup_interval_days": 7
        }
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save()
    
    def get_language(self):
        """Get current language"""
        return self.get("language", "en")
    
    def set_language(self, lang_code):
        """Set language"""
        self.set("language", lang_code)
    
    def get_theme(self):
        """Get current theme"""
        return self.get("theme", "Light")
    
    def set_theme(self, theme_name):
        """Set theme"""
        self.set("theme", theme_name)

# Global config instance
config = Config()