# heartlib/gui/add_patron_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QPushButton, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
import uuid
from datetime import datetime

class AddPatronDialog(QDialog):
    def __init__(self, parent=None, patron_to_edit=None):
        super().__init__(parent)
        self.patron_to_edit = patron_to_edit
        self.setWindowTitle("Add New Patron" if not patron_to_edit else "Edit Patron")
        self.setMinimumWidth(450)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name (required)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        form_layout.addRow("Name *:", self.name_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("patron@example.com")
        form_layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("(555) 123-4567")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Barcode (library card number)
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Auto-generated if left empty")
        form_layout.addRow("Barcode:", self.barcode_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Patron")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # If editing, populate fields
        if patron_to_edit:
            self.populate_fields(patron_to_edit)
    
    def populate_fields(self, patron):
        """Fill form with existing patron data"""
        self.name_input.setText(patron.get("name", ""))
        self.email_input.setText(patron.get("email", ""))
        self.phone_input.setText(patron.get("phone", ""))
        self.barcode_input.setText(patron.get("barcode", ""))
    
    def get_patron_data(self):
        """Return patron data as dict"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Info", "Patron name is required.")
            return None
        
        # Generate barcode if not provided
        barcode = self.barcode_input.text().strip()
        if not barcode:
            barcode = f"LIB{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "id": self.patron_to_edit.get("id") if self.patron_to_edit else str(uuid.uuid4()),
            "name": name,
            "email": self.email_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "barcode": barcode,
            "join_date": int(datetime.now().timestamp()),
            "last_modified": int(datetime.now().timestamp()),
            "sync_version": 1,
            "deleted": 0
        }