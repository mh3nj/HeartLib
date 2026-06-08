# heartlib/gui/quick_actions.py
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

class QuickActionsWidget(QWidget):
    scan_requested = pyqtSignal()
    add_book_requested = pyqtSignal()
    switch_patron_requested = pyqtSignal()
    sync_requested = pyqtSignal()
    return_book_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.scan_btn = QPushButton("🔍 Scan Barcode")
        self.scan_btn.clicked.connect(self.scan_requested.emit)
        
        self.add_btn = QPushButton("➕ Add Book")
        self.add_btn.clicked.connect(self.add_book_requested.emit)
        
        self.switch_btn = QPushButton("👥 Switch Patron")
        self.switch_btn.clicked.connect(self.switch_patron_requested.emit)
        
        self.return_btn = QPushButton("🔄 Return Book")
        self.return_btn.clicked.connect(self.return_book_requested.emit)
        
        self.sync_btn = QPushButton("🔄 Sync Now")
        self.sync_btn.clicked.connect(self.sync_requested.emit)
        
        layout.addWidget(self.scan_btn)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.switch_btn)
        layout.addWidget(self.return_btn)
        layout.addWidget(self.sync_btn)
        
        self.setLayout(layout)