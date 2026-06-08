# heartlib/gui/checkout_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLabel, QMessageBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime, timedelta

class CheckoutDialog(QDialog):
    checkout_completed = pyqtSignal(dict)  # emits loan info when done
    
    def __init__(self, crud, parent=None):
        super().__init__(parent)
        self.crud = crud
        self.selected_patron = None
        self.selected_book = None
        self.setWindowTitle("📖 Check Out Book")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # ----- Patron Section -----
        patron_section = QVBoxLayout()
        patron_label = QLabel("👤 BORROWER")
        patron_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        patron_section.addWidget(patron_label)
        
        patron_select_layout = QHBoxLayout()
        self.patron_search = QLineEdit()
        self.patron_search.setPlaceholderText("Search patron by name, email, or barcode...")
        self.patron_search.textChanged.connect(self.search_patrons)
        patron_select_layout.addWidget(self.patron_search)
        
        self.patron_table = QTableWidget()
        self.patron_table.setColumnCount(3)
        self.patron_table.setHorizontalHeaderLabels(["Name", "Email", "Barcode"])
        self.patron_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.patron_table.setMaximumHeight(150)
        self.patron_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.patron_table.itemClicked.connect(self.on_patron_selected)
        patron_select_layout.addWidget(self.patron_table)
        
        patron_section.addLayout(patron_select_layout)
        
        self.selected_patron_label = QLabel("No patron selected")
        self.selected_patron_label.setStyleSheet("color: gray; padding: 5px;")
        patron_section.addWidget(self.selected_patron_label)
        
        layout.addLayout(patron_section)
        
        # ----- Book Section -----
        book_section = QVBoxLayout()
        book_label = QLabel("📚 BOOK")
        book_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        book_section.addWidget(book_label)
        
        book_select_layout = QHBoxLayout()
        self.book_search = QLineEdit()
        self.book_search.setPlaceholderText("Search book by title, author, or ISBN...")
        self.book_search.textChanged.connect(self.search_books)
        book_select_layout.addWidget(self.book_search)
        
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(4)
        self.book_table.setHorizontalHeaderLabels(["Title", "Author", "ISBN", "Available"])
        self.book_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.book_table.setMaximumHeight(150)
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.book_table.itemClicked.connect(self.on_book_selected)
        book_select_layout.addWidget(self.book_table)
        
        book_section.addLayout(book_select_layout)
        
        self.selected_book_label = QLabel("No book selected")
        self.selected_book_label.setStyleSheet("color: gray; padding: 5px;")
        book_section.addWidget(self.selected_book_label)
        
        layout.addLayout(book_section)
        
        # ----- Due Date -----
        due_section = QFormLayout()
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(14))
        self.due_date.setCalendarPopup(True)
        due_section.addRow("Due Date:", self.due_date)
        layout.addLayout(due_section)
        
        # ----- Buttons -----
        button_layout = QHBoxLayout()
        self.checkout_btn = QPushButton("✅ Confirm Checkout")
        self.checkout_btn.setEnabled(False)
        self.checkout_btn.clicked.connect(self.confirm_checkout)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.checkout_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Load initial data
        self.search_patrons()
        self.search_books()
    
    def search_patrons(self):
        """Search and display patrons"""
        query = self.patron_search.text().strip()
        if query:
            patrons = self.crud.search_patrons(query)
        else:
            patrons = self.crud.get_all_patrons()
        
        self.patron_table.setRowCount(len(patrons))
        for row, patron in enumerate(patrons):
            self.patron_table.setItem(row, 0, QTableWidgetItem(patron.get('name', '')))
            self.patron_table.setItem(row, 1, QTableWidgetItem(patron.get('email', '')))
            self.patron_table.setItem(row, 2, QTableWidgetItem(patron.get('barcode', '')))
            # Store patron ID
            self.patron_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, patron['id'])
    
    def on_patron_selected(self, item):
        """Handle patron selection from table"""
        row = item.row()
        patron_id = self.patron_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.selected_patron = self.crud.get_patron_by_id(patron_id)
        self.selected_patron_label.setText(f"✓ {self.selected_patron['name']} (Barcode: {self.selected_patron.get('barcode', 'N/A')})")
        self.selected_patron_label.setStyleSheet("color: green; padding: 5px;")
        self.update_checkout_button()
    
    def search_books(self):
        """Search and display books"""
        query = self.book_search.text().strip()
        if query:
            books = self.crud.search_books(query)
        else:
            books = self.crud.get_all_books()
        
        # Filter to available books only for checkout
        available_books = [b for b in books if b.get('copies_available', 0) > 0]
        
        self.book_table.setRowCount(len(available_books))
        for row, book in enumerate(available_books):
            self.book_table.setItem(row, 0, QTableWidgetItem(book.get('title', '')))
            self.book_table.setItem(row, 1, QTableWidgetItem(book.get('author', '')))
            self.book_table.setItem(row, 2, QTableWidgetItem(book.get('isbn', '')))
            self.book_table.setItem(row, 3, QTableWidgetItem(str(book.get('copies_available', 0))))
            # Store book ID
            self.book_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, book['id'])
    
    def on_book_selected(self, item):
        """Handle book selection from table"""
        row = item.row()
        book_id = self.book_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.selected_book = self.crud.get_book_by_id(book_id)
        self.selected_book_label.setText(f"✓ {self.selected_book['title']} by {self.selected_book.get('author', 'Unknown')}")
        self.selected_book_label.setStyleSheet("color: green; padding: 5px;")
        self.update_checkout_button()
    
    def update_checkout_button(self):
        """Enable checkout button only if both patron and book selected"""
        self.checkout_btn.setEnabled(self.selected_patron is not None and self.selected_book is not None)
    
    def confirm_checkout(self):
        """Process the checkout"""
        due_date_q = self.due_date.date()
        due_datetime = datetime(due_date_q.year(), due_date_q.month(), due_date_q.day())
        due_timestamp = int(due_datetime.timestamp())
        
        success = self.crud.checkout_book(
            self.selected_book['id'],
            self.selected_patron['id'],
            due_timestamp
        )
        
        if success:
            self.checkout_completed.emit({
                "book": self.selected_book,
                "patron": self.selected_patron,
                "due_date": due_date_q.toString("yyyy-MM-dd")
            })
            self.accept()
        else:
            QMessageBox.warning(self, "Checkout Failed", "Book is no longer available!")