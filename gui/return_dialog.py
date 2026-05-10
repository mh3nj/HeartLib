# heartlib/gui/return_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime

class ReturnDialog(QDialog):
    return_completed = pyqtSignal(dict)
    
    def __init__(self, crud, parent=None):
        super().__init__(parent)
        self.crud = crud
        self.selected_loan = None
        self.setWindowTitle("🔄 Return Book")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by book title, patron name, or barcode...")
        self.search_input.textChanged.connect(self.search_loans)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Active loans table
        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(5)
        self.loans_table.setHorizontalHeaderLabels(["Book Title", "Patron", "Borrowed Date", "Due Date", "Status"])
        self.loans_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.loans_table.setAlternatingRowColors(True)
        self.loans_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.loans_table.itemClicked.connect(self.on_loan_selected)
        layout.addWidget(self.loans_table)
        
        # Selected loan info
        self.selected_label = QLabel("Select a loan to return")
        self.selected_label.setStyleSheet("color: gray; padding: 10px;")
        layout.addWidget(self.selected_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.return_btn = QPushButton("✅ Confirm Return")
        self.return_btn.setEnabled(False)
        self.return_btn.clicked.connect(self.confirm_return)
        self.cancel_btn = QPushButton("Close")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.return_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Load all active loans
        self.search_loans()
    
    def search_loans(self):
        """Search active loans"""
        query = self.search_input.text().strip()
        active_loans = self.crud.get_all_active_loans()
        
        # Filter based on search query
        if query:
            filtered = []
            query_lower = query.lower()
            for loan in active_loans:
                if (query_lower in loan.get('title', '').lower() or
                    query_lower in loan.get('patron_name', '').lower() or
                    query_lower in loan.get('barcode', '').lower()):
                    filtered.append(loan)
            active_loans = filtered
        
        self.loans_table.setRowCount(len(active_loans))
        
        for row, loan in enumerate(active_loans):
            self.loans_table.setItem(row, 0, QTableWidgetItem(loan.get('title', '')))
            self.loans_table.setItem(row, 1, QTableWidgetItem(loan.get('patron_name', '')))
            
            # Borrowed date
            checkout_time = loan.get('checkout_time', 0)
            if checkout_time:
                borrow_date = datetime.fromtimestamp(checkout_time).strftime('%Y-%m-%d')
            else:
                borrow_date = 'Unknown'
            self.loans_table.setItem(row, 2, QTableWidgetItem(borrow_date))
            
            # Due date
            due_time = loan.get('due_time', 0)
            if due_time:
                due_date = datetime.fromtimestamp(due_time).strftime('%Y-%m-%d')
                # Check if overdue
                if due_time < datetime.now().timestamp():
                    due_date += " ⚠️ OVERDUE"
            else:
                due_date = 'Unknown'
            self.loans_table.setItem(row, 3, QTableWidgetItem(due_date))
            
            # Status
            self.loans_table.setItem(row, 4, QTableWidgetItem("Active"))
            
            # Store loan ID
            self.loans_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, loan['id'])
    
    def on_loan_selected(self, item):
        """Handle loan selection"""
        row = item.row()
        loan_id = self.loans_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.selected_loan = self.crud.get_loan_by_id(loan_id)
        
        book_title = self.loans_table.item(row, 0).text()
        patron_name = self.loans_table.item(row, 1).text()
        
        self.selected_label.setText(f"✓ Returning: '{book_title}' borrowed by {patron_name}")
        self.selected_label.setStyleSheet("color: green; padding: 10px;")
        self.return_btn.setEnabled(True)
    
    def confirm_return(self):
        """Process the return"""
        if self.selected_loan:
            success = self.crud.return_book(self.selected_loan['id'])
            
            if success:
                self.return_completed.emit({
                    "loan": self.selected_loan,
                    "book_title": self.selected_loan.get('title'),
                    "patron_name": self.selected_loan.get('patron_name')
                })
                self.accept()
            else:
                QMessageBox.warning(self, "Return Failed", "Could not process return.")
