# heartlib/gui/theme_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QComboBox, QColorDialog,
                             QGroupBox, QGridLayout, QFileDialog, QMessageBox,
                             QLineEdit)
from PyQt6.QtCore import Qt
from .theme_manager import ThemeManager

class ThemeDialog(QDialog):
    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowTitle("🎨 Theme Switcher")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Theme selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Theme:"))
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(self.theme_manager.get_theme_list())
        self.theme_selector.currentTextChanged.connect(self.preview_theme)
        selector_layout.addWidget(self.theme_selector)
        
        apply_btn = QPushButton("Apply Theme")
        apply_btn.clicked.connect(self.apply_theme)
        selector_layout.addWidget(apply_btn)
        
        layout.addLayout(selector_layout)
        
        # Custom theme editor
        custom_group = QGroupBox("Custom Theme Editor")
        custom_layout = QGridLayout(custom_group)
        
        row = 0
        self.color_inputs = {}
        colors = [
            ("bg_primary", "Background Primary"),
            ("bg_secondary", "Background Secondary"),
            ("text_primary", "Text Primary"),
            ("text_secondary", "Text Secondary"),
            ("accent", "Accent Color"),
            ("accent_hover", "Accent Hover"),
            ("border", "Border Color"),
            ("success", "Success Color"),
            ("warning", "Warning Color"),
            ("error", "Error Color"),
            ("info", "Info Color")
        ]
        
        for color_key, color_label in colors:
            custom_layout.addWidget(QLabel(f"{color_label}:"), row, 0)
            
            color_layout = QHBoxLayout()
            color_value = QLabel("")
            color_value.setFrameStyle(1)
            color_value.setFixedSize(50, 25)
            color_btn = QPushButton("Pick Color")
            color_btn.setFixedWidth(80)
            
            self.color_inputs[color_key] = {
                "value": color_value,
                "button": color_btn,
                "current": "#FFFFFF"
            }
            
            color_btn.clicked.connect(lambda checked, k=color_key: self.pick_color(k))
            color_layout.addWidget(color_value)
            color_layout.addWidget(color_btn)
            color_layout.addStretch()
            
            custom_layout.addLayout(color_layout, row, 1)
            row += 1
        
        # Theme name
        custom_layout.addWidget(QLabel("Theme Name:"), row, 0)
        self.theme_name_input = QLineEdit()
        self.theme_name_input.setPlaceholderText("My Custom Theme")
        custom_layout.addWidget(self.theme_name_input, row, 1)
        row += 1
        
        # Save/Delete buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Custom Theme")
        save_btn.clicked.connect(self.save_custom_theme)
        delete_btn = QPushButton("🗑️ Delete Custom Theme")
        delete_btn.clicked.connect(self.delete_custom_theme)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)
        custom_layout.addLayout(button_layout, row, 0, 1, 2)
        
        layout.addWidget(custom_group)
        
        # Import/Export buttons
        import_export_layout = QHBoxLayout()
        import_btn = QPushButton("📥 Import Theme (.hth)")
        import_btn.clicked.connect(self.import_theme)
        export_btn = QPushButton("📤 Export Theme (.hth)")
        export_btn.clicked.connect(self.export_theme)
        import_export_layout.addWidget(import_btn)
        import_export_layout.addWidget(export_btn)
        layout.addLayout(import_export_layout)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def pick_color(self, color_key):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self.color_inputs[color_key]["current"] = hex_color
            self.color_inputs[color_key]["value"].setStyleSheet(f"background-color: {hex_color}; border: 1px solid gray;")
    
    def preview_theme(self, theme_name):
        """Preview a theme (update color picker values)"""
        if theme_name == "Light":
            theme = self.theme_manager.LIGHT_THEME
        elif theme_name == "Dark":
            theme = self.theme_manager.DARK_THEME
        else:
            theme = self.theme_manager.custom_themes.get(theme_name)
        
        if theme:
            for key, color in theme.items():
                if key in self.color_inputs:
                    self.color_inputs[key]["current"] = color
                    self.color_inputs[key]["value"].setStyleSheet(f"background-color: {color}; border: 1px solid gray;")
            self.theme_name_input.setText(theme.get("name", ""))
    
    def apply_theme(self):
        """Apply selected theme"""
        theme_name = self.theme_selector.currentText()
        self.theme_manager.load_theme_by_name(theme_name)
        
        # Save to config
        try:
            from config import config
            config.set_theme(theme_name)
            print(f"Theme saved: {theme_name}")
        except:
            pass
        
        QMessageBox.information(self, "Theme Applied", f"Theme '{theme_name}' has been applied.")
    
    def get_current_colors(self):
        """Get current colors from UI"""
        theme = {"name": self.theme_name_input.text().strip()}
        for key, data in self.color_inputs.items():
            theme[key] = data["current"]
        return theme
    
    def save_custom_theme(self):
        """Save custom theme"""
        theme = self.get_current_colors()
        if not theme["name"]:
            QMessageBox.warning(self, "Missing Name", "Please enter a theme name.")
            return
        
        self.theme_manager.save_custom_theme(theme)
        self.theme_selector.clear()
        self.theme_selector.addItems(self.theme_manager.get_theme_list())
        self.theme_selector.setCurrentText(theme["name"])
        QMessageBox.information(self, "Theme Saved", f"Theme '{theme['name']}' has been saved.")
    
    def delete_custom_theme(self):
        """Delete custom theme"""
        theme_name = self.theme_selector.currentText()
        if theme_name in ["Light", "Dark"]:
            QMessageBox.warning(self, "Cannot Delete", "Cannot delete built-in themes.")
            return
        
        reply = QMessageBox.question(self, "Delete Theme", 
                                    f"Delete theme '{theme_name}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.theme_manager.delete_custom_theme(theme_name)
            self.theme_selector.clear()
            self.theme_selector.addItems(self.theme_manager.get_theme_list())
            QMessageBox.information(self, "Theme Deleted", f"Theme '{theme_name}' has been deleted.")
    
    def import_theme(self):
        """Import theme from .hth file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Theme", "", "HeartLib Theme (*.hth);;All Files (*)"
        )
        if filepath:
            try:
                theme_name = self.theme_manager.import_theme(filepath)
                self.theme_selector.clear()
                self.theme_selector.addItems(self.theme_manager.get_theme_list())
                self.theme_selector.setCurrentText(theme_name)
                QMessageBox.information(self, "Theme Imported", f"Theme '{theme_name}' has been imported.")
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", str(e))
    
    def export_theme(self):
        """Export current theme to .hth file"""
        theme_name = self.theme_selector.currentText()
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Theme", f"{theme_name}.hth", "HeartLib Theme (*.hth)"
        )
        if filepath:
            if self.theme_manager.export_theme(theme_name, filepath):
                QMessageBox.information(self, "Theme Exported", f"Theme exported to {filepath}")
            else:
                QMessageBox.critical(self, "Export Failed", "Could not export theme.")