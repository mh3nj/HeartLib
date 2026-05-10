# heartlib/gui/add_book_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QSpinBox, QPushButton, QHBoxLayout, QMessageBox,
                             QTextEdit, QLabel)
from PyQt6.QtCore import Qt
import uuid
from datetime import datetime

class AddBookDialog(QDialog):
    def __init__(self, parent=None, book_to_edit=None):
        super().__init__(parent)
        self.book_to_edit = book_to_edit  # If provided, we're editing
        self.setWindowTitle("Add New Book" if not book_to_edit else "Edit Book")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Form layout for fields
        form_layout = QFormLayout()
        
        # Title (required)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Book title")
        form_layout.addRow("Title *:", self.title_input)
        
        # Author
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Author name")
        form_layout.addRow("Author:", self.author_input)
        
        # ISBN
        self.isbn_input = QLineEdit()
        self.isbn_input.setPlaceholderText("978-3-16-148410-0")
        form_layout.addRow("ISBN:", self.isbn_input)

        self.lookup_btn = QPushButton("🔍 Lookup ISBN")
        self.lookup_btn.clicked.connect(self.lookup_isbn)
        form_layout.addRow("", self.lookup_btn)
        
        # Total copies
        self.copies_input = QSpinBox()
        self.copies_input.setMinimum(1)
        self.copies_input.setMaximum(999)
        self.copies_input.setValue(1)
        form_layout.addRow("Total Copies:", self.copies_input)
        
        # Location/shelf
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g., A3, Fiction, Row 2")
        form_layout.addRow("Location:", self.location_input)
        
        # Description (optional)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Optional description, notes, or summary...")
        form_layout.addRow("Description:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Book")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # If editing, populate fields
        if book_to_edit:
            self.populate_fields(book_to_edit)
    
    def populate_fields(self, book):
        """Fill form with existing book data for editing"""
        self.title_input.setText(book.get("title", ""))
        self.author_input.setText(book.get("author", ""))
        self.isbn_input.setText(book.get("isbn", ""))
        self.copies_input.setValue(book.get("copies_total", 1))
        self.location_input.setText(book.get("location", ""))
        if book.get("description"):
            self.description_input.setText(book.get("description"))
    
    def lookup_isbn(self):
        isbn = self.isbn_input.text().strip()
        if not isbn:
            QMessageBox.warning(self, "ISBN Required", "Please enter an ISBN first.")
            return
        
        from utils.isbn_lookup import ISBNLookup
        lookup = ISBNLookup()
        data = lookup.fetch(isbn)
        if data:
            if data.get('title'):
                self.title_input.setText(data['title'])
            if data.get('author'):
                self.author_input.setText(data['author'])
            if data.get('description'):
                self.description_input.setText(data['description'])
            QMessageBox.information(self, "Success", f"Fetched data for {data['title']}")
        else:
            QMessageBox.warning(self, "Not Found", "No book found for this ISBN.")

    def get_book_data(self):
        """Return book data as dict"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Missing Info", "Book title is required.")
            return None
        
        return {
            "id": self.book_to_edit.get("id") if self.book_to_edit else str(uuid.uuid4()),
            "title": title,
            "author": self.author_input.text().strip(),
            "isbn": self.isbn_input.text().strip(),
            "copies_total": self.copies_input.value(),
            "copies_available": self.copies_input.value(),  # new books start all available
            "location": self.location_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "last_modified": int(datetime.now().timestamp()),
            "sync_version": 1,
            "deleted": 0
        }
