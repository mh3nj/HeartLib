# heartlib/gui/theme_manager.py - Add save_last_theme method
import json
import os
from PyQt6.QtCore import QSettings, QByteArray
from PyQt6.QtGui import QColor, QPalette


class ThemeManager:
    """Manages themes for HeartLib"""
    
    LIGHT_THEME = {
        "name": "Light",
        "bg_primary": "#FFFFFF",
        "bg_secondary": "#F5F5F5",
        "text_primary": "#000000",
        "text_secondary": "#666666",
        "accent": "#2C3E50",
        "accent_hover": "#1A252F",
        "border": "#DDDDDD",
        "success": "#27AE60",
        "warning": "#F39C12",
        "error": "#E74C3C",
        "info": "#3498DB"
    }
    
    DARK_THEME = {
        "name": "Dark",
        "bg_primary": "#1E1E1E",
        "bg_secondary": "#2D2D2D",
        "text_primary": "#FFFFFF",
        "text_secondary": "#BBBBBB",
        "accent": "#3498DB",
        "accent_hover": "#2980B9",
        "border": "#444444",
        "success": "#27AE60",
        "warning": "#F39C12",
        "error": "#E74C3C",
        "info": "#3498DB"
    }
    
    def __init__(self, app):
        self.app = app
        self.settings = QSettings("HeartLib", "HeartLib")
        self.current_theme = None
        self.custom_themes = self.load_custom_themes()
    
    def load_custom_themes(self):
        """Load saved custom themes from settings"""
        themes_data = self.settings.value("custom_themes", "")
        if themes_data:
            try:
                return json.loads(themes_data)
            except:
                return {}
        return {}
    
    def save_custom_themes(self):
        """Save custom themes to settings"""
        self.settings.setValue("custom_themes", json.dumps(self.custom_themes))
    
    def save_last_theme(self, theme_name):
        """Save last used theme name"""
        self.settings.setValue("last_theme", theme_name)
    
    def get_last_theme(self):
        """Get last used theme name"""
        return self.settings.value("last_theme", "Light")
    
    def apply_theme(self, theme):
        """Apply a theme to the application"""
        self.current_theme = theme
        
        # Create palette
        palette = QPalette()
        
        # Set colors
        bg_primary = QColor(theme["bg_primary"])
        bg_secondary = QColor(theme["bg_secondary"])
        text_primary = QColor(theme["text_primary"])
        text_secondary = QColor(theme["text_secondary"])
        
        palette.setColor(QPalette.ColorRole.Window, bg_primary)
        palette.setColor(QPalette.ColorRole.WindowText, text_primary)
        palette.setColor(QPalette.ColorRole.Base, bg_secondary)
        palette.setColor(QPalette.ColorRole.AlternateBase, bg_primary)
        palette.setColor(QPalette.ColorRole.ToolTipBase, bg_primary)
        palette.setColor(QPalette.ColorRole.ToolTipText, text_primary)
        palette.setColor(QPalette.ColorRole.Text, text_primary)
        palette.setColor(QPalette.ColorRole.Button, bg_secondary)
        palette.setColor(QPalette.ColorRole.ButtonText, text_primary)
        palette.setColor(QPalette.ColorRole.BrightText, QColor(theme["accent"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["accent"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        
        self.app.setPalette(palette)
        
        # Apply stylesheet
        stylesheet = f"""
            QMainWindow {{ background-color: {theme["bg_primary"]}; }}
            QLabel {{ color: {theme["text_primary"]}; }}
            QPushButton {{
                background-color: {theme["accent"]};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: {theme["accent_hover"]}; }}
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit {{
                background-color: {theme["bg_secondary"]};
                color: {theme["text_primary"]};
                border: 1px solid {theme["border"]};
                padding: 6px;
                border-radius: 3px;
            }}
            QTableWidget, QListWidget {{
                background-color: {theme["bg_secondary"]};
                color: {theme["text_primary"]};
                alternate-background-color: {theme["bg_primary"]};
                gridline-color: {theme["border"]};
            }}
            QHeaderView::section {{
                background-color: {theme["bg_primary"]};
                color: {theme["text_primary"]};
                padding: 6px;
                border: 1px solid {theme["border"]};
            }}
            QMenuBar {{
                background-color: {theme["bg_secondary"]};
                color: {theme["text_primary"]};
            }}
            QMenuBar::item:selected {{
                background-color: {theme["accent"]};
                color: white;
            }}
            QMenu {{
                background-color: {theme["bg_secondary"]};
                color: {theme["text_primary"]};
                border: 1px solid {theme["border"]};
            }}
            QMenu::item:selected {{
                background-color: {theme["accent"]};
                color: white;
            }}
            QStatusBar {{
                background-color: {theme["bg_secondary"]};
                color: {theme["text_secondary"]};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                background-color: {theme["bg_primary"]};
            }}
            QTabBar::tab {{
                background-color: {theme["bg_secondary"]};
                color: {theme["text_primary"]};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme["accent"]};
                color: white;
            }}
            QGroupBox {{
                border: 1px solid {theme["border"]};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: {theme["text_primary"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QScrollBar:vertical {{
                background-color: {theme["bg_secondary"]};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme["border"]};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme["accent"]};
            }}
        """
        self.app.setStyleSheet(stylesheet)
        
        # Save last theme
        self.save_last_theme(theme["name"])

            # Also try to save to config file if available
        try:
            from config import config
            config.set_theme(theme["name"])
            print(f"Theme saved to config: {theme['name']}")
        except:
            pass  # Config not available yet
    
    def get_theme_list(self):
        """Get list of available themes"""
        themes = ["Light", "Dark"]
        themes.extend(self.custom_themes.keys())
        return themes
    
    def load_theme_by_name(self, theme_name):
        """Load a theme by name"""
        if theme_name == "Light":
            self.apply_theme(self.LIGHT_THEME)
        elif theme_name == "Dark":
            self.apply_theme(self.DARK_THEME)
        elif theme_name in self.custom_themes:
            self.apply_theme(self.custom_themes[theme_name])
    
    def save_custom_theme(self, theme):
        """Save a custom theme"""
        self.custom_themes[theme["name"]] = theme
        self.save_custom_themes()
    
    def delete_custom_theme(self, theme_name):
        """Delete a custom theme"""
        if theme_name in self.custom_themes:
            del self.custom_themes[theme_name]
            self.save_custom_themes()
    
    def export_theme(self, theme_name, filepath):
        """Export theme to .hth file"""
        if theme_name == "Light":
            theme = self.LIGHT_THEME
        elif theme_name == "Dark":
            theme = self.DARK_THEME
        else:
            theme = self.custom_themes.get(theme_name)
        
        if theme:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(theme, f, indent=2)
            return True
        return False
    
    def import_theme(self, filepath):
        """Import theme from .hth file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme = json.load(f)
            if "name" not in theme:
                theme["name"] = os.path.splitext(os.path.basename(filepath))[0]
            self.custom_themes[theme["name"]] = theme
            self.save_custom_themes()
            return theme["name"]
        except Exception as e:
            raise Exception(f"Failed to import theme: {str(e)}")
