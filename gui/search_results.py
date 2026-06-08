# heartlib/gui/search_results.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTableView, QHeaderView, QCheckBox, 
                             QComboBox, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QKeySequence, QShortcut
import re

class BooksTableModel(QAbstractTableModel):
    def __init__(self, books=None):
        super().__init__()
        self.headers = ["Title", "Author", "ISBN", "Available", "Location"]
        self.books = books or []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.books)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        book = self.books[index.row()]
        field = self.headers[index.column()].lower()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if field == "title":
                return book.get("title", "")
            elif field == "author":
                return book.get("author", "")
            elif field == "isbn":
                return book.get("isbn", "")
            elif field == "available":
                copies_avail = book.get("copies_available", 0)
                copies_total = book.get("copies_total", 0)
                return f"{copies_avail}/{copies_total}"
            elif field == "location":
                return book.get("location", "")
        elif role == Qt.ItemDataRole.TextAlignmentRole and field == "available":
            return Qt.AlignmentFlag.AlignCenter
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None
    
    def get_book_at_row(self, row):
        if 0 <= row < len(self.books):
            return self.books[row]
        return None


class SearchResultsWidget(QWidget):
    book_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.all_books = []  # Store full book list for reset
        layout = QVBoxLayout(self)
        
        # Search bar row
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by title, author, or ISBN...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_btn)
        
        # Advanced filters row
        filter_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("Match case")
        self.whole_word = QCheckBox("Whole word")
        self.regex_mode = QCheckBox("Regex")
        self.view_selector = QComboBox()
        self.view_selector.addItems(["Everything", "Books only", "Available only"])
        filter_layout.addWidget(self.case_sensitive)
        filter_layout.addWidget(self.whole_word)
        filter_layout.addWidget(self.regex_mode)
        filter_layout.addWidget(QLabel("View:"))
        filter_layout.addWidget(self.view_selector)
        filter_layout.addStretch()
        
        # Table view
        self.table = QTableView()
        self.model = BooksTableModel()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self.on_double_click)
        
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+C"), self, self.case_sensitive.toggle)
        QShortcut(QKeySequence("Ctrl+W"), self, self.whole_word.toggle)
        QShortcut(QKeySequence("Ctrl+R"), self, self.regex_mode.toggle)
        
        # Assemble
        layout.addLayout(search_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        
        # Connect view selector
        self.view_selector.currentTextChanged.connect(self.apply_view_filter)
    
    def load_books(self, books):
        """Load books from database into the table"""
        self.all_books = books.copy()  # Store full list
        self.model.books = books.copy()
        self.model.layoutChanged.emit()
    
    def perform_search(self):
        """Search books based on query and filters"""
        query = self.search_input.text().strip()
        
        # If search is empty, show all books
        if not query:
            self.reset_to_all_books()
            return
        
        # Filter books based on query
        filtered = []
        for book in self.all_books:
            text = f"{book.get('title', '')} {book.get('author', '')} {book.get('isbn', '')}"
            
            if not self.case_sensitive.isChecked():
                text = text.lower()
                q = query.lower()
            else:
                q = query
            
            if self.regex_mode.isChecked():
                try:
                    if re.search(q, text):
                        filtered.append(book)
                except re.error:
                    pass
            else:
                if self.whole_word.isChecked():
                    words = re.findall(r'\b\w+\b', text)
                    if q in words:
                        filtered.append(book)
                else:
                    if q in text:
                        filtered.append(book)
        
        self.model.books = filtered
        self.model.layoutChanged.emit()
        self.apply_view_filter()  # Apply view filter after search
    
    def clear_search(self):
        """Clear search input and reset to all books"""
        self.search_input.clear()
        self.reset_to_all_books()
    
    def reset_to_all_books(self):
        """Reset the table to show all books"""
        self.model.books = self.all_books.copy()
        self.model.layoutChanged.emit()
        self.apply_view_filter()
    
    def apply_view_filter(self):
        """Apply the view selector filter (Everything / Available only)"""
        view = self.view_selector.currentText()
        
        if view == "Available only":
            filtered = [b for b in self.model.books if b.get('copies_available', 0) > 0]
            self.model.books = filtered
            self.model.layoutChanged.emit()
        elif view == "Everything":
            # Already showing everything
            pass
    
    def on_double_click(self, index):
        row = index.row()
        book = self.model.get_book_at_row(row)
        if book:
            self.book_selected.emit(book)