# heartlib/main.py
import sys
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QStatusBar, QMenuBar, 
                             QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

# Import all widgets
from gui.quick_actions import QuickActionsWidget
from gui.search_results import SearchResultsWidget
from gui.patron_spotlight import PatronSpotlightWidget
from gui.circulation_feed import CirculationFeedWidget
from gui.details_panel import DetailsPanelWidget
from gui.add_book_dialog import AddBookDialog
from gui.add_patron_dialog import AddPatronDialog
from gui.patron_search_dialog import PatronSearchDialog
from gui.checkout_dialog import CheckoutDialog
from gui.return_dialog import ReturnDialog
from gui.barcode_scanner import BarcodeScannerDialog
from gui.csv_import_export import CSVImportExportDialog
from gui.theme_manager import ThemeManager
from gui.theme_dialog import ThemeDialog
from gui.help_dialog import HelpDialog
from gui.settings_dialog import SettingsDialog

# Import database modules
from database import DatabaseManager, CRUD
from database.models import Book
from database.models import Patron

class HeartLibMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HeartLib – Library with a Heart")
        self.setMinimumSize(1200, 800)
        
        # ----- Initialize Database FIRST -----
        self.db = DatabaseManager("heartlib.db")
        self.crud = CRUD(self.db)

        self.api_server = None
        
        # Sync variables (v2.0)
        self.sync_client = None
        self.sync_server = None
        self.sync_enabled = False
        
        # Central widget and main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # ----- 3-column splitter (left, middle, right) -----
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT PANEL (vertical split inside: Patron Spotlight + Quick Actions)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Patron Spotlight
        self.patron_spotlight = PatronSpotlightWidget()
        self.patron_spotlight.patron_selected.connect(self.on_patron_selected)
        self.patron_spotlight.select_patron_requested.connect(self.on_select_patron_clicked)
        
        # Quick Actions
        self.quick_actions = QuickActionsWidget()
        self.quick_actions.scan_requested.connect(self.on_scan)
        self.quick_actions.add_book_requested.connect(self.on_add_book)
        self.quick_actions.switch_patron_requested.connect(self.on_switch_patron)
        self.quick_actions.sync_requested.connect(self.manual_sync)
        self.quick_actions.return_book_requested.connect(self.on_return_book)
        
        left_layout.addWidget(self.patron_spotlight)
        left_layout.addWidget(self.quick_actions)
        
        # MIDDLE PANEL (vertical split: Search Results + Circulation Feed)
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_results = SearchResultsWidget()
        self.search_results.book_selected.connect(self.on_book_selected)
        
        self.circulation_feed = CirculationFeedWidget()
        self.circulation_feed.activity_clicked.connect(self.on_activity_clicked)
        
        middle_layout.addWidget(self.search_results)
        middle_layout.addWidget(self.circulation_feed)
        
        # RIGHT PANEL (Details)
        self.details_panel = DetailsPanelWidget()
        self.details_panel.edit_requested.connect(self.on_edit_requested)
        self.details_panel.delete_requested.connect(self.on_delete_requested)
        
        # Add panels to splitter
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(middle_panel)
        self.main_splitter.addWidget(self.details_panel)
        # Set initial proportions (left: 20%, middle: 50%, right: 30%)
        self.main_splitter.setSizes([240, 600, 360])
        
        main_layout.addWidget(self.main_splitter)
        
        # ----- Menu Bar -----
        self.create_menu_bar()
        
        # ----- Status Bar -----
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add sync status to status bar
        self.sync_status = QLabel("🔄 Sync: Ready")
        self.status_bar.addPermanentWidget(self.sync_status)
        
        # ----- Load Data from Database -----
        self.load_books_into_search()
        self.update_status_stats()
        
        # ----- Auto-sync timer (placeholder for v2.0) -----
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.auto_sync)
        self.sync_timer.start(30 * 60 * 1000)  # default 30 min
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # Library menu
        library_menu = menubar.addMenu("📚 Library")
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.open_settings)
        library_menu.addAction(settings_action)
        
        backup_action = QAction("💾 Backup / Restore", self)
        library_menu.addAction(backup_action)
        
        # Patrons menu
        patrons_menu = menubar.addMenu("👥 Patrons")
        add_patron_action = QAction("➕ Add Patron", self)
        add_patron_action.triggered.connect(self.on_add_patron)
        patrons_menu.addAction(add_patron_action)
        
        # Circulation menu
        circ_menu = menubar.addMenu("🔄 Circulation")
        checkout_action = QAction("📖 Check Out", self)
        checkout_action.triggered.connect(self.on_checkout)
        circ_menu.addAction(checkout_action)
        
        # Reports menu
        reports_menu = menubar.addMenu("📊 Reports")
        reports_action = QAction("📊 Reports Dashboard", self)
        reports_action.triggered.connect(self.open_reports)
        reports_menu.addAction(reports_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("🔧 Tools")
        
        # Add CSV Import/Export to Tools menu
        import_export_action = QAction("📊 CSV Import/Export", self)
        import_export_action.triggered.connect(self.open_csv_tools)
        tools_menu.addAction(import_export_action)
        
        # Theme switcher
        theme_action = QAction("🎨 Theme Switcher", self)
        theme_action.triggered.connect(self.open_theme_switcher)
        tools_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        tutorial_action = QAction("📖 In-app Tutorial", self)
        tutorial_action.triggered.connect(self.open_help)
        help_menu.addAction(tutorial_action)
        coffee_action = QAction("☕ Buy us a coffee", self)
        coffee_action.triggered.connect(self.buy_coffee)
        help_menu.addAction(coffee_action)
        
    def load_books_into_search(self):
        """Load all books from database into search results"""
        books = self.crud.get_all_books()
        self.search_results.load_books(books)
        self.status_bar.showMessage(f"📚 Loaded {len(books)} books", 3000)
    
    def update_status_stats(self):
        """Update status bar with library stats"""
        stats = self.crud.get_stats()
        self.status_bar.showMessage(
            f"📚 {stats['total_books']} total | 📖 {stats['checked_out']} checked out | "
            f"✅ {stats['available']} available | 🔄 {stats['active_loans']} active loans"
        )
    
    # ----- Signal handlers -----
    def on_scan(self):
        """Open barcode scanner for books"""
        dialog = BarcodeScannerDialog(mode="book", parent=self)
        dialog.barcode_scanned.connect(self.on_barcode_scanned)
        dialog.exec()

    def on_barcode_scanned(self, barcode):
        """Handle scanned barcode - search for book or patron"""
        print(f"Scanned: {barcode}")
        
        # First, try to find as book by ISBN/barcode
        books = self.crud.search_books(barcode)
        if books:
            # Found a book - show it
            book = books[0]
            self.search_results.perform_search(barcode)
            self.details_panel.show_book_details(book)
            self.status_bar.showMessage(f"📖 Found book: {book['title']}", 3000)
            return
        
        # If not found as book, try as patron
        patron = self.crud.get_patron_by_barcode(barcode)
        if patron:
            # Found a patron - select them
            self.patron_spotlight.set_patron(patron)
            self.status_bar.showMessage(f"👤 Patron selected: {patron['name']}", 3000)
            return
        
        # Not found
        QMessageBox.information(self, "Not Found", 
                            f"No book or patron found with barcode: {barcode}\n\n"
                            "You can add a new book with this barcode.")
        
    def on_add_book(self):
        """Open dialog to add a new book"""
        dialog = AddBookDialog(self)
        if dialog.exec():
            book_data = dialog.get_book_data()
            if book_data:
                book = Book(
                    title=book_data["title"],
                    author=book_data["author"],
                    isbn=book_data["isbn"],
                    copies_total=book_data["copies_total"],
                    copies_available=book_data["copies_available"],
                    location=book_data["location"],
                    description=book_data.get("description", "")
                )
                self.crud.add_book(book)
                self.load_books_into_search()
                self.update_status_stats()
                self.circulation_feed.add_activity("book_added", book_data['title'])
                self.status_bar.showMessage(f"✅ Book '{book_data['title']}' added!", 3000)
        
    def on_switch_patron(self):
        """Switch patron - open patron search dialog"""
        self.on_select_patron_clicked()

    def on_patron_barcode_scanned(self, barcode):
        """Handle patron barcode scan"""
        patron = self.crud.get_patron_by_barcode(barcode)
        if patron:
            self.patron_spotlight.set_patron(patron)
            self.status_bar.showMessage(f"👤 Patron selected: {patron['name']}", 3000)
        else:
            reply = QMessageBox.question(self, "Patron Not Found", 
                                        f"No patron found with barcode: {barcode}\n\nWould you like to add this patron?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                dialog = AddPatronDialog(self)
                dialog.barcode_input.setText(barcode)
                if dialog.exec():
                    patron_data = dialog.get_patron_data()
                    if patron_data:
                        patron = Patron(
                            name=patron_data["name"],
                            email=patron_data["email"],
                            phone=patron_data["phone"],
                            barcode=patron_data["barcode"],
                            join_date=patron_data["join_date"]
                        )
                        self.crud.add_patron(patron)
                        self.circulation_feed.add_activity("patron_added", patron_data['name'])
                        self.status_bar.showMessage(f"✅ Patron '{patron_data['name']}' added!", 3000)

    # ----- Sync Methods (v2.0) -----
    def manual_sync(self):
        """Manual sync button pressed - v2.0 feature"""
        try:
            from networking.sync_client import SyncClient
            
            print("🔄 Manual sync requested")
            self.sync_status.setText("🔄 Syncing...")
            self.status_bar.showMessage("Starting sync...", 1000)
            
            def do_sync():
                try:
                    client = SyncClient(self.crud, server_host='localhost', server_port=8765)
                    success = client.sync()
                    if success:
                        self.sync_status.setText("✅ Sync: OK")
                        self.status_bar.showMessage("Sync completed successfully!", 3000)
                        self.load_books_into_search()
                        self.update_status_stats()
                    else:
                        self.sync_status.setText("❌ Sync: Failed")
                        self.status_bar.showMessage("Sync failed - server not found", 3000)
                except Exception as e:
                    self.sync_status.setText("❌ Sync: Error")
                    self.status_bar.showMessage(f"Sync error: {e}", 3000)
            
            thread = threading.Thread(target=do_sync, daemon=True)
            thread.start()
            
        except ImportError as e:
            QMessageBox.information(self, "Sync Feature", 
                                f"Sync engine not available: {e}\n\n"
                                "Sync will be available in HeartLib v2.0")
            self.status_bar.showMessage("Sync feature coming in v2.0", 3000)

    def auto_sync(self):
        """Auto sync timer triggered - v2.0 feature"""
        pass
    
    def start_sync_server(self):
        """Start the sync server"""
        try:
            from networking.sync_server import SyncServer
            
            if not hasattr(self, '_sync_server'):
                self._sync_server = SyncServer(self.crud, host='localhost', port=8765)
                server_thread = threading.Thread(target=self._sync_server.start, daemon=True)
                server_thread.start()
                self.sync_status.setText("🟢 Server: Running")
                self.status_bar.showMessage("Sync server started", 3000)
        except ImportError as e:
            print(f"Sync server not available: {e}")
    
    # ----- Other handlers -----
    def on_book_selected(self, book):
        """Called when a book is double-clicked in search results"""
        print(f"Book selected: {book.get('title', 'Unknown')}")
        self.details_panel.show_book_details(book)
        
    def on_patron_selected(self, patron):
        """Called when a patron is selected in patron spotlight"""
        if patron and isinstance(patron, dict):
            print(f"Patron selected: {patron.get('name', 'Unknown')}")
            self.details_panel.show_patron_details(patron)
        else:
            print("Patron cleared")
            self.details_panel.clear()
        
    def on_activity_clicked(self, activity):
        """Called when an activity is clicked in circulation feed"""
        print(f"Activity clicked: {activity.get('message', '')}")
        
    def on_edit_requested(self, type_str, id_str):
        print(f"Edit {type_str} with id: {id_str}")
        
    def on_delete_requested(self, type_str, id_str):
        """Handle delete request from details panel"""
        if type_str == "book":
            active_loans = self.crud.get_active_loans_for_book(id_str)
            if active_loans:
                QMessageBox.warning(self, "Cannot Delete", 
                                "This book has active loans. Please return all copies before deleting.")
                return
            
            reply = QMessageBox.question(self, "Delete Book", 
                                        "Are you sure you want to delete this book?\nThis action cannot be undone.",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                if self.crud.soft_delete_book(id_str):
                    self.load_books_into_search()
                    self.update_status_stats()
                    self.details_panel.clear()
                    self.circulation_feed.add_activity("book_deleted", "Book deleted", extra=f"ID: {id_str[:8]}")
                    self.status_bar.showMessage("✅ Book deleted", 3000)
                else:
                    QMessageBox.warning(self, "Delete Failed", "Could not delete the book.")
        
        elif type_str == "patron":
            active_loans = self.crud.get_active_loans_for_patron(id_str)
            if active_loans:
                QMessageBox.warning(self, "Cannot Delete", 
                                "This patron has active loans. Please return all books before deleting.")
                return
            
            reply = QMessageBox.question(self, "Delete Patron", 
                                        "Are you sure you want to delete this patron?\nThis action cannot be undone.",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                if self.crud.soft_delete_patron(id_str):
                    if self.patron_spotlight.current_patron and self.patron_spotlight.current_patron['id'] == id_str:
                        self.patron_spotlight.clear_patron()
                    self.details_panel.clear()
                    self.circulation_feed.add_activity("patron_deleted", "Patron deleted", extra=f"ID: {id_str[:8]}")
                    self.status_bar.showMessage("✅ Patron deleted", 3000)
                else:
                    QMessageBox.warning(self, "Delete Failed", "Could not delete the patron.")
        
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.crud, self.config, self.theme_manager, self)
        dialog.exec()
        # Reload settings after closing
        self.load_books_into_search()
        self.update_status_stats()

    def open_help(self):
        """Open help dialog"""
        dialog = HelpDialog(self)
        dialog.exec()
        
    def open_theme_switcher(self):
        """Open theme switcher dialog"""
        dialog = ThemeDialog(self.theme_manager, self)
        if dialog.exec():
            theme_name = self.theme_manager.current_theme["name"]
            self.config.set_theme(theme_name)
        
    def buy_coffee(self):
        QMessageBox.information(self, "☕ Thank you!", "Your support keeps HeartLib alive. (Payment link will go here)")

    def on_add_patron(self):
        """Open dialog to add a new patron"""
        dialog = AddPatronDialog(self)
        if dialog.exec():
            patron_data = dialog.get_patron_data()
            if patron_data:
                patron = Patron(
                    name=patron_data["name"],
                    email=patron_data["email"],
                    phone=patron_data["phone"],
                    barcode=patron_data["barcode"],
                    join_date=patron_data["join_date"]
                )
                self.crud.add_patron(patron)
                self.circulation_feed.add_activity("patron_added", patron_data['name'])
                self.status_bar.showMessage(f"✅ Patron '{patron_data['name']}' added!", 3000)

    def on_select_patron_clicked(self):
        """Open patron search dialog"""
        dialog = PatronSearchDialog(self.crud, self)
        dialog.patron_selected.connect(self.on_patron_selected_from_dialog)
        dialog.exec()

    def on_patron_selected_from_dialog(self, patron):
        """Handle patron selection from dialog"""
        print(f"Patron selected from dialog: {patron.get('name')}")
        self.patron_spotlight.set_patron(patron)
        self.circulation_feed.add_activity("patron_selected", patron['name'], extra="selected")
        
    def on_checkout(self):
        """Open checkout dialog"""
        dialog = CheckoutDialog(self.crud, self)
        dialog.checkout_completed.connect(self.on_checkout_completed)
        dialog.exec()

    def on_checkout_completed(self, loan_info):
        """Handle successful checkout"""
        book = loan_info['book']
        patron = loan_info['patron']
        due_date = loan_info['due_date']
        
        self.load_books_into_search()
        self.update_status_stats()
        self.circulation_feed.add_activity(
            "checkout", 
            book['title'], 
            patron['name'],
            f"due {due_date}"
        )
        self.status_bar.showMessage(f"✅ '{book['title']}' checked out to {patron['name']}", 3000)
        
        if self.patron_spotlight.current_patron and self.patron_spotlight.current_patron['id'] == patron['id']:
            self.details_panel.show_patron_details(patron)

    def on_return_book(self):
        """Open return dialog"""
        dialog = ReturnDialog(self.crud, self)
        dialog.return_completed.connect(self.on_return_completed)
        dialog.exec()

    def on_return_completed(self, return_info):
        """Handle successful return"""
        book_title = return_info['book_title']
        patron_name = return_info['patron_name']
        
        self.load_books_into_search()
        self.update_status_stats()
        self.circulation_feed.add_activity("return", book_title, patron_name)
        self.status_bar.showMessage(f"✅ '{book_title}' returned from {patron_name}", 3000)
        
        if self.patron_spotlight.current_patron:
            current_patron = self.crud.get_patron_by_id(self.patron_spotlight.current_patron['id'])
            if current_patron:
                self.details_panel.show_patron_details(current_patron)

    def open_csv_tools(self):
        """Open CSV import/export dialog"""
        dialog = CSVImportExportDialog(self.crud, self)
        dialog.exec()
        self.load_books_into_search()
        self.update_status_stats()

    def open_reports(self):
        """Open reports dashboard"""
        from gui.reports_dashboard import ReportsDashboard
        dialog = ReportsDashboard(self.crud, self)
        dialog.exec()

    def start_api_server(self):
        from networking.api_server import HeartLibAPI
        self.api_server = HeartLibAPI(self.crud, host='0.0.0.0', port=8766)
        self.api_server.start_background()
        self.status_bar.showMessage("🌐 Mobile API server started on port 8766", 3000)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HeartLib")
    app.setOrganizationName("HeartLib Community")
    
    try:
        from config import config
        print(f"Config loaded. Theme: {config.get_theme()}")
    except Exception as e:
        print(f"Config not available: {e}")
        class SimpleConfig:
            def get_theme(self): return "Light"
            def set_theme(self, v): pass
        config = SimpleConfig()
    
    theme_manager = ThemeManager(app)
    last_theme = config.get_theme()
    print(f"Loading theme: {last_theme}")
    theme_manager.load_theme_by_name(last_theme)
    
    window = HeartLibMainWindow()
    window.theme_manager = theme_manager
    window.config = config
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
