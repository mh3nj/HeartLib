# heartlib/gui/about_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About HeartLib")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # REPLACE THIS PLACEHOLDER WITH YOUR ACTUAL LOGO
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(128, 128)  # Made larger for about dialog
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Check if logo exists and load it
        logo_path = "resources/icons/heartlib_logo_128.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        else:
            # Fallback placeholder (remove this after adding your logo)
            self.logo_label.setText("❤️")
            self.logo_label.setStyleSheet("font-size: 48px; border: 1px dashed #999; background-color: #f0f0f0;")
        
        layout.addWidget(self.logo_label)
        
        # Title
        title_label = QLabel("HeartLib")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: gray; margin-bottom: 20px;")
        layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel(
            "A library management system with a heart.\n"
            "Free. Offline. Privacy first. No fines. No cloud. No subscription."
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin: 20px; line-height: 1.5;")
        layout.addWidget(desc_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Credits
        credits_label = QLabel(
            "Created by Mohsen Jafari\n"
            "github.com/mh3nj\n\n"
            "Because libraries have hearts, not just barcodes."
        )
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setStyleSheet("color: gray; margin: 15px;")
        layout.addWidget(credits_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)