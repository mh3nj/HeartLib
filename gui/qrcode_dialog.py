# heartlib/gui/qrcode_dialog.py
import qrcode
from PIL import Image
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import io

class QRCodeDialog(QDialog):
    def __init__(self, server_url, parent=None):
        super().__init__(parent)
        self.server_url = server_url
        self.setWindowTitle("📱 Patron Access QR Code")
        self.setMinimumSize(400, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Patrons can scan this QR code to access HeartLib PWA.\n\n"
            "They can search catalog, view their loans, and renew books.\n\n"
            "Place this QR code at checkout desk or entrance."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        # QR Code image
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.generate_qrcode()
        layout.addWidget(self.qr_label)
        
        # URL display
        url_label = QLabel(f"URL: {server_url}")
        url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        url_label.setStyleSheet("color: gray; font-family: monospace;")
        layout.addWidget(url_label)
        
        # Buttons
        save_btn = QPushButton("💾 Save QR Code as Image")
        save_btn.clicked.connect(self.save_qrcode)
        layout.addWidget(save_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def generate_qrcode(self):
        """Generate QR code from server URL"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.server_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to QPixmap
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.read())
        
        # Scale to reasonable size
        scaled = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
        self.qr_label.setPixmap(scaled)
    
    def save_qrcode(self):
        """Save QR code as PNG file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save QR Code", "heartlib_qrcode.png", "PNG Images (*.png)"
        )
        if filepath:
            # Regenerate and save
            qr = qrcode.make(self.server_url)
            qr.save(filepath)
            QMessageBox.information(self, "Saved", f"QR code saved to {filepath}")