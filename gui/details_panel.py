# heartlib/gui/details_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, 
                             QPushButton, QFrame, QStackedWidget, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal

class DetailsPanelWidget(QWidget):
    # Signals for actions from this panel
    edit_requested = pyqtSignal(str, str)  # type ("book" or "patron"), id
    delete_requested = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.current_mode = "none"  # "book", "patron", or "none"
        self.current_id = None
        
        layout = QVBoxLayout(self)
        
        # Title
        self.title_label = QLabel("📋 Details")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)
        
        # Stacked widget to switch between book and patron views
        self.stack = QStackedWidget()
        
        # ----- Book Details View (index 0) -----
        self.book_widget = QWidget()
        book_layout = QVBoxLayout(self.book_widget)
        
        # Book cover placeholder
        self.cover_label = QLabel("📖")
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setStyleSheet("font-size: 48px; background-color: #f0f0f0; padding: 20px;")
        book_layout.addWidget(self.cover_label)
        
        # Book info grid
        book_info_layout = QGridLayout()
        self.book_title = QLabel("")
        self.book_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.book_author = QLabel("")
        self.book_isbn = QLabel("")
        self.book_copies = QLabel("")
        self.book_location = QLabel("")
        self.book_status = QLabel("")
        
        row = 0
        book_info_layout.addWidget(QLabel("Title:"), row, 0)
        book_info_layout.addWidget(self.book_title, row, 1)
        row += 1
        book_info_layout.addWidget(QLabel("Author:"), row, 0)
        book_info_layout.addWidget(self.book_author, row, 1)
        row += 1
        book_info_layout.addWidget(QLabel("ISBN:"), row, 0)
        book_info_layout.addWidget(self.book_isbn, row, 1)
        row += 1
        book_info_layout.addWidget(QLabel("Copies:"), row, 0)
        book_info_layout.addWidget(self.book_copies, row, 1)
        row += 1
        book_info_layout.addWidget(QLabel("Location:"), row, 0)
        book_info_layout.addWidget(self.book_location, row, 1)
        row += 1
        book_info_layout.addWidget(QLabel("Status:"), row, 0)
        book_info_layout.addWidget(self.book_status, row, 1)
        
        book_layout.addLayout(book_info_layout)
        
        # Book action buttons
        book_btn_layout = QVBoxLayout()
        self.edit_book_btn = QPushButton("✏️ Edit Book")
        self.edit_book_btn.clicked.connect(lambda: self.edit_requested.emit("book", self.current_id))
        self.delete_book_btn = QPushButton("🗑️ Delete Book")
        self.delete_book_btn.clicked.connect(lambda: self.delete_requested.emit("book", self.current_id))
        book_btn_layout.addWidget(self.edit_book_btn)
        book_btn_layout.addWidget(self.delete_book_btn)
        book_layout.addLayout(book_btn_layout)
        
        book_layout.addStretch()
        
        # ----- Patron Details View (index 1) -----
        self.patron_widget = QWidget()
        patron_layout = QVBoxLayout(self.patron_widget)
        
        # Patron avatar placeholder
        self.avatar_label = QLabel("👤")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("font-size: 48px; background-color: #f0f0f0; padding: 20px;")
        patron_layout.addWidget(self.avatar_label)
        
        # Patron info grid
        patron_info_layout = QGridLayout()
        self.patron_name = QLabel("")
        self.patron_name.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.patron_email = QLabel("")
        self.patron_phone = QLabel("")
        self.patron_barcode = QLabel("")
        self.patron_join_date = QLabel("")
        self.patron_active_loans = QLabel("")
        
        row = 0
        patron_info_layout.addWidget(QLabel("Name:"), row, 0)
        patron_info_layout.addWidget(self.patron_name, row, 1)
        row += 1
        patron_info_layout.addWidget(QLabel("Email:"), row, 0)
        patron_info_layout.addWidget(self.patron_email, row, 1)
        row += 1
        patron_info_layout.addWidget(QLabel("Phone:"), row, 0)
        patron_info_layout.addWidget(self.patron_phone, row, 1)
        row += 1
        patron_info_layout.addWidget(QLabel("Barcode:"), row, 0)
        patron_info_layout.addWidget(self.patron_barcode, row, 1)
        row += 1
        patron_info_layout.addWidget(QLabel("Joined:"), row, 0)
        patron_info_layout.addWidget(self.patron_join_date, row, 1)
        row += 1
        patron_info_layout.addWidget(QLabel("Active Loans:"), row, 0)
        patron_info_layout.addWidget(self.patron_active_loans, row, 1)
        
        patron_layout.addLayout(patron_info_layout)
        
        # Patron action buttons
        patron_btn_layout = QVBoxLayout()
        self.edit_patron_btn = QPushButton("✏️ Edit Patron")
        self.edit_patron_btn.clicked.connect(lambda: self.edit_requested.emit("patron", self.current_id))
        self.delete_patron_btn = QPushButton("🗑️ Delete Patron")
        self.delete_patron_btn.clicked.connect(lambda: self.delete_requested.emit("patron", self.current_id))
        patron_btn_layout.addWidget(self.edit_patron_btn)
        patron_btn_layout.addWidget(self.delete_patron_btn)
        patron_layout.addLayout(patron_btn_layout)
        
        patron_layout.addStretch()
        
        # ----- Empty View (index 2) -----
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_label = QLabel("✨ Select a book or patron\n to see details here")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet("color: gray; font-size: 14px;")
        empty_layout.addWidget(empty_label)
        
        # Add all views to stack
        self.stack.addWidget(self.book_widget)    # index 0
        self.stack.addWidget(self.patron_widget)  # index 1
        self.stack.addWidget(self.empty_widget)   # index 2
        
        layout.addWidget(self.stack)
        self.set_current_mode("none")
    
    def set_current_mode(self, mode):
        """Switch between 'book', 'patron', or 'none'"""
        self.current_mode = mode
        if mode == "book":
            self.stack.setCurrentIndex(0)
        elif mode == "patron":
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(2)
    
    def show_book_details(self, book: dict):
        """Display book information in the panel"""
        self.current_id = book.get("id")
        self.book_title.setText(book.get("title", "Unknown"))
        self.book_author.setText(book.get("author", "Unknown"))
        self.book_isbn.setText(book.get("isbn", "N/A"))
        self.book_copies.setText(f"{book.get('copies_available', 0)} / {book.get('copies_total', 0)}")
        self.book_location.setText(book.get("location", "Not specified"))
        
        status = book.get("status", "available")
        if status == "available" or book.get("copies_available", 0) > 0:
            self.book_status.setText("✅ Available")
            self.book_status.setStyleSheet("color: green;")
        else:
            self.book_status.setText("❌ Checked Out")
            self.book_status.setStyleSheet("color: red;")
        
        self.set_current_mode("book")
    
    def show_patron_details(self, patron: dict):
        """Display patron information in the panel"""
        self.current_id = patron.get("id")
        self.patron_name.setText(patron.get("name", "Unknown"))
        self.patron_email.setText(patron.get("email", "N/A"))
        self.patron_phone.setText(patron.get("phone", "N/A"))
        self.patron_barcode.setText(patron.get("barcode", "N/A"))
        
        # Format join date
        join_ts = patron.get("join_date")
        if join_ts:
            from datetime import datetime
            join_date = datetime.fromtimestamp(join_ts).strftime("%Y-%m-%d")
            self.patron_join_date.setText(join_date)
        else:
            self.patron_join_date.setText("Unknown")
        
        # Active loans count
        active = patron.get("active_loans", 0)
        self.patron_active_loans.setText(str(active))
        
        self.set_current_mode("patron")
    
    def clear(self):
        """Clear the panel and show empty state"""
        self.current_id = None
        self.set_current_mode("none")
