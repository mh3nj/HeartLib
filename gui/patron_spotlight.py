# heartlib/gui/patron_spotlight.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import pyqtSignal

class PatronSpotlightWidget(QWidget):
    patron_selected = pyqtSignal(object)  # Changed from dict to object to allow None
    select_patron_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_patron = None
        
        layout = QVBoxLayout(self)
        
        # Title
        self.title_label = QLabel("👤 Patron Spotlight")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)
        
        # Patron info area
        self.info_frame = QFrame()
        self.info_frame.setFrameShape(QFrame.Shape.Box)
        info_layout = QVBoxLayout(self.info_frame)
        
        self.name_label = QLabel("No patron selected")
        self.name_label.setWordWrap(True)
        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("color: gray; font-size: 12px;")
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.details_label)
        layout.addWidget(self.info_frame)
        
        # Action buttons
        self.select_btn = QPushButton("📇 Select Patron")
        self.select_btn.clicked.connect(self.on_select_clicked)
        layout.addWidget(self.select_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_patron)
        layout.addWidget(self.clear_btn)
        
        layout.addStretch()
    
    def set_patron(self, patron: dict):
        """Set the current patron and update UI."""
        self.current_patron = patron
        self.name_label.setText(f"<b>{patron.get('name', 'Unknown')}</b>")
        details = []
        if patron.get('barcode'):
            details.append(f"📇 {patron['barcode']}")
        if patron.get('email'):
            details.append(f"✉️ {patron['email']}")
        self.details_label.setText(" | ".join(details) if details else "No extra info")
        self.patron_selected.emit(patron)
    
    def clear_patron(self):
        """Clear the current patron."""
        self.current_patron = None
        self.name_label.setText("No patron selected")
        self.details_label.setText("")
        self.patron_selected.emit(None)  # Now works because signal accepts object
    
    def on_select_clicked(self):
        """Open patron search dialog."""
        self.select_patron_requested.emit()
