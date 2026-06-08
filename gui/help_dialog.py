# heartlib/gui/help_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QPushButton, QTextEdit, 
                             QTreeWidget, QTreeWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, QTimer

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 HeartLib Help & Tutorial")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Tab 1: Getting Started
        getting_started_tab = self.create_getting_started_tab()
        tabs.addTab(getting_started_tab, "🚀 Getting Started")
        
        # Tab 2: Quick Actions
        quick_actions_tab = self.create_quick_actions_tab()
        tabs.addTab(quick_actions_tab, "⚡ Quick Actions")
        
        # Tab 3: Managing Books
        books_tab = self.create_books_tab()
        tabs.addTab(books_tab, "📚 Managing Books")
        
        # Tab 4: Managing Patrons
        patrons_tab = self.create_patrons_tab()
        tabs.addTab(patrons_tab, "👥 Managing Patrons")
        
        # Tab 5: Circulation
        circulation_tab = self.create_circulation_tab()
        tabs.addTab(circulation_tab, "🔄 Circulation")
        
        # Tab 6: Reports & Sync
        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, "📊 Advanced")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def create_getting_started_tab(self):
        """Create getting started tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("Welcome to HeartLib!")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        intro = QLabel("""
        HeartLib is a library management system designed with kindness and simplicity in mind.
        
        📚 WHAT YOU CAN DO:
        • Add and manage books and patrons
        • Check out and return books with due dates
        • Scan barcodes for quick checkouts
        • Generate reports for grants and board meetings
        • Import/Export data from CSV files
        • Customize the look with themes
        
        💡 TIP: Most actions can be accessed from the Quick Actions panel on the left!
        """)
        intro.setWordWrap(True)
        intro.setStyleSheet("padding: 20px; font-size: 13px;")
        layout.addWidget(intro)
        
        layout.addStretch()
        return tab
    
    def create_quick_actions_tab(self):
        """Create quick actions tutorial tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        actions = [
            ("🔍 Scan Barcode", "Scan book or patron barcodes using your camera. Fallback to manual entry if camera fails."),
            ("➕ Add Book", "Add new books to your library catalog. Fill in title, author, ISBN, and location."),
            ("👥 Switch Patron", "Select a patron to work with. Search by name, email, or barcode."),
            ("🔄 Return Book", "Process book returns. Search by book title or patron name."),
            ("🔄 Sync Now", "Sync with other HeartLib devices on your network (v2.0 feature)."),
        ]
        
        for i, (title, desc) in enumerate(actions):
            action_title = QLabel(title)
            action_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
            layout.addWidget(action_title)
            
            action_desc = QLabel(desc)
            action_desc.setWordWrap(True)
            action_desc.setStyleSheet("margin-left: 20px; color: gray;")
            layout.addWidget(action_desc)
        
        layout.addStretch()
        return tab
    
    def create_books_tab(self):
        """Create books management tutorial tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        tips = QLabel("""
        📖 ADDING BOOKS:
        1. Click 'Add Book' button or go to Books menu
        2. Fill in the book details (title is required)
        3. Set total copies available
        4. Add location/shelf information (helps with finding books!)
        5. Click Save
        
        🔍 SEARCHING BOOKS:
        • Use the search bar to find books by title, author, or ISBN
        • Advanced filters: Match case, Whole word, Regex
        • Double-click any book to see full details
        
        ✏️ EDITING & DELETION:
        • Select a book from search results
        • Use the Details panel on the right to edit or delete
        • Books with active loans cannot be deleted
        
        💡 TIP: Use the ISBN lookup feature (coming soon) to auto-fill book information!
        """)
        tips.setWordWrap(True)
        tips.setStyleSheet("padding: 15px; font-size: 13px;")
        layout.addWidget(tips)
        
        layout.addStretch()
        return tab
    
    def create_patrons_tab(self):
        """Create patrons management tutorial tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        tips = QLabel("""
        👤 ADDING PATRONS:
        1. Click Patrons → Add Patron from the menu
        2. Enter patron name (required), email, and phone
        3. Barcode is auto-generated if left blank
        4. Click Save
        
        🔍 FINDING PATRONS:
        • Click 'Switch Patron' to search and select a patron
        • Search by name, email, or barcode
        • Selected patron appears in the Patron Spotlight panel
        
        📋 PATRON DETAILS:
        • View active loans count
        • See borrowing history
        • Edit patron information
        • Delete patron (only if no active loans)
        
        💡 TIP: Print patron barcodes on library cards for quick scanning!
        """)
        tips.setWordWrap(True)
        tips.setStyleSheet("padding: 15px; font-size: 13px;")
        layout.addWidget(tips)
        
        layout.addStretch()
        return tab
    
    def create_circulation_tab(self):
        """Create circulation tutorial tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        tips = QLabel("""
        🔄 CHECKING OUT BOOKS:
        1. Select a patron (using Switch Patron)
        2. Click 'Check Out' or go to Circulation menu
        3. Search for a book (or scan barcode)
        4. Set due date (default: 14 days)
        5. Confirm checkout
        
        🔄 RETURNING BOOKS:
        1. Click 'Return Book' button
        2. Search for active loans by book title or patron
        3. Select the loan to return
        4. Confirm return
        
        📋 CIRCULATION FEED:
        • Shows real-time activity log
        • Color-coded entries (green=checkout, blue=return, red=overdue)
        • Click any entry for details
        • Use 'Clear Feed' to reset
        
        ⚠️ OVERDUE ITEMS:
        • Check Reports → Overdue Items
        • Export overdue list to CSV
        • Send reminders to patrons (coming soon)
        """)
        tips.setWordWrap(True)
        tips.setStyleSheet("padding: 15px; font-size: 13px;")
        layout.addWidget(tips)
        
        layout.addStretch()
        return tab
    
    def create_advanced_tab(self):
        """Create advanced features tutorial tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        tips = QLabel("""
        📊 REPORTS DASHBOARD:
        • Overview: Quick library statistics
        • Popular Books: Most borrowed titles
        • Overdue Items: Track late returns
        • Circulation History: Filter by date range
        • Grant Report: Generate professional reports
        
        📥 CSV IMPORT/EXPORT:
        • Export books or patrons to CSV files
        • Import from CSV for migration from old systems
        • Supports batch import
        
        🎨 THEME SWITCHER:
        • Light mode for daytime
        • Dark mode for evening cataloging
        • Create custom themes with any colors
        • Export/Import themes (.hth files)
        
        🔄 SYNC (v2.0):
        • Sync between multiple computers on same network
        • One server, many clients
        • Automatic conflict resolution
        
        ☕ SUPPORT:
        • Buy us a coffee to support development
        • Report issues on GitHub
        """)
        tips.setWordWrap(True)
        tips.setStyleSheet("padding: 15px; font-size: 13px;")
        layout.addWidget(tips)
        
        layout.addStretch()
        return tab