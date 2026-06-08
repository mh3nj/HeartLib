# heartlib/gui/circulation_feed.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from datetime import datetime

class CirculationFeedWidget(QWidget):
    # Signal when an item is clicked (to potentially show details)
    activity_clicked = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Title bar with clear button
        title_layout = QHBoxLayout()
        title_label = QLabel("🔄 Circulation Activity Feed")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)
        
        self.clear_btn = QPushButton("Clear Feed")
        self.clear_btn.setFixedWidth(80)
        self.clear_btn.clicked.connect(self.clear_feed)
        title_layout.addWidget(self.clear_btn)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # List widget for activities
        self.activity_list = QListWidget()
        self.activity_list.setAlternatingRowColors(True)
        self.activity_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.activity_list)
        
        # Activity counter
        self.counter_label = QLabel("0 activities today")
        self.counter_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.counter_label)
        
        # Store activities for counting
        self.activities = []  # list of dicts with timestamp, type, message
        
    def add_activity(self, activity_type: str, book_title: str, patron_name: str = None, extra: str = ""):
        """
        Add a new activity to the feed.
        activity_type: "checkout", "return", "hold", "overdue", "patron_added", "book_added"
        """
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        
        # Create message based on type
        if activity_type == "checkout":
            message = f"📖 {timestamp} – '{book_title}' checked out"
            if patron_name:
                message += f" by {patron_name}"
        elif activity_type == "return":
            message = f"✅ {timestamp} – '{book_title}' returned"
            if patron_name:
                message += f" from {patron_name}"
        elif activity_type == "hold":
            message = f"⏰ {timestamp} – Hold placed on '{book_title}'"
            if patron_name:
                message += f" by {patron_name}"
        elif activity_type == "overdue":
            message = f"⚠️ {timestamp} – '{book_title}' is overdue"
            if patron_name:
                message += f" (borrowed by {patron_name})"
        elif activity_type == "patron_added":
            message = f"👤 {timestamp} – New patron added: {book_title}"  # book_title holds patron name
        elif activity_type == "book_added":
            message = f"📚 {timestamp} – New book added: '{book_title}'"
        else:
            message = f"ℹ️ {timestamp} – {extra or activity_type}"
        
        if extra:
            message += f" {extra}"
        
        # Create list item
        item = QListWidgetItem(message)
        
        # Color code based on type (using Qt.GlobalColor)
        if activity_type == "checkout":
            item.setForeground(Qt.GlobalColor.darkGreen)
        elif activity_type == "return":
            item.setForeground(Qt.GlobalColor.darkBlue)
        elif activity_type == "hold":
            item.setForeground(Qt.GlobalColor.darkMagenta)
        elif activity_type == "overdue":
            item.setForeground(Qt.GlobalColor.darkRed)
        else:
            item.setForeground(Qt.GlobalColor.black)
        
        # Add to top of list (most recent first)
        self.activity_list.insertItem(0, item)
        
        # Store the activity data
        activity_data = {
            "timestamp": timestamp,
            "date": date_str,
            "type": activity_type,
            "book_title": book_title,
            "patron_name": patron_name,
            "message": message
        }
        self.activities.insert(0, activity_data)
        
        # Limit to last 100 activities to prevent memory bloat
        if len(self.activities) > 100:
            self.activities = self.activities[:100]
            while self.activity_list.count() > 100:
                self.activity_list.takeItem(100)
        
        # Update counter (activities from today)
        today_count = sum(1 for a in self.activities if a.get("date", "") == date_str)
        self.counter_label.setText(f"{today_count} activities today")
    
    def clear_feed(self):
        """Clear all activities from the feed"""
        self.activity_list.clear()
        self.activities = []
        self.counter_label.setText("0 activities today")
    
    def on_item_clicked(self, item):
        """Emit signal with activity data when clicked"""
        row = self.activity_list.row(item)
        if row < len(self.activities):
            self.activity_clicked.emit(self.activities[row])