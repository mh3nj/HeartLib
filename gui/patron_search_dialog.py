# heartlib/gui/patron_search_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal

class PatronSearchDialog(QDialog):
    patron_selected = pyqtSignal(dict)
    
    def __init__(self, crud, parent=None):
        super().__init__(parent)
        self.crud = crud
        self.setWindowTitle("Select Patron")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name, email, or barcode...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Email", "Barcode", "Active Loans"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self.on_select)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.select_btn = QPushButton("✓ Select Patron")
        self.select_btn.clicked.connect(self.on_select)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Load all patrons initially
        self.perform_search()
    
    def perform_search(self):
        """Search patrons based on query"""
        query = self.search_input.text().strip()
        if query:
            patrons = self.crud.search_patrons(query)
        else:
            patrons = self.crud.get_all_patrons()
        
        self.table.setRowCount(len(patrons))
        
        for row, patron in enumerate(patrons):
            # Get active loans count
            active_loans = self.get_active_loan_count(patron['id'])
            
            self.table.setItem(row, 0, QTableWidgetItem(patron.get('name', '')))
            self.table.setItem(row, 1, QTableWidgetItem(patron.get('email', '')))
            self.table.setItem(row, 2, QTableWidgetItem(patron.get('barcode', '')))
            self.table.setItem(row, 3, QTableWidgetItem(str(active_loans)))
            
            # Store patron ID in the row
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, patron['id'])
    
    def get_active_loan_count(self, patron_id):
        """Get number of active loans for a patron"""
        try:
            if hasattr(self.crud, 'get_active_loans_for_patron'):
                loans = self.crud.get_active_loans_for_patron(patron_id)
                return len(loans)
        except:
            pass
        return 0
    
    def on_select(self):
        """Emit selected patron and close dialog"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            patron_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            # Get full patron data
            patron = self.crud.get_patron_by_id(patron_id)
            if patron:
                self.patron_selected.emit(patron)
                self.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a patron from the list.")
