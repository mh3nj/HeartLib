# heartlib/gui/reports_dashboard.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QFileDialog, QGroupBox, QGridLayout, QComboBox,
                             QDateEdit, QTextEdit)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime, timedelta
from PyQt6.QtGui import QColor
import csv

class ReportsDashboard(QDialog):
    def __init__(self, crud, parent=None):
        super().__init__(parent)
        self.crud = crud
        self.setWindowTitle("📊 HeartLib Reports")
        self.setMinimumSize(900, 700)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Tab 1: Overview Stats
        overview_tab = self.create_overview_tab()
        tabs.addTab(overview_tab, "📈 Overview")
        
        # Tab 2: Popular Books
        popular_tab = self.create_popular_tab()
        tabs.addTab(popular_tab, "⭐ Popular Books")
        
        # Tab 3: Overdue Items
        overdue_tab = self.create_overdue_tab()
        tabs.addTab(overdue_tab, "⚠️ Overdue Items")
        
        # Tab 4: Circulation History
        circulation_tab = self.create_circulation_tab()
        tabs.addTab(circulation_tab, "🔄 Circulation History")
        
        # Tab 5: Grant Report
        grant_tab = self.create_grant_tab()
        tabs.addTab(grant_tab, "📝 Grant Report")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def create_overview_tab(self):
        """Create overview statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Get stats
        stats = self.crud.get_stats()
        
        # Stats grid
        grid = QGridLayout()
        
        # Total Books
        total_box = self.create_stat_box("📚 Total Books", str(stats['total_books']))
        grid.addWidget(total_box, 0, 0)
        
        # Available Books
        avail_box = self.create_stat_box("✅ Available", str(stats['available']))
        grid.addWidget(avail_box, 0, 1)
        
        # Checked Out
        out_box = self.create_stat_box("📖 Checked Out", str(stats['checked_out']))
        grid.addWidget(out_box, 0, 2)
        
        # Active Loans
        loans_box = self.create_stat_box("🔄 Active Loans", str(stats['active_loans']))
        grid.addWidget(loans_box, 1, 0)
        
        # Total Patrons
        patrons = self.crud.get_all_patrons()
        patrons_box = self.create_stat_box("👥 Total Patrons", str(len(patrons)))
        grid.addWidget(patrons_box, 1, 1)
        
        # Today's Activity
        today_loans = self.get_today_activity()
        activity_box = self.create_stat_box("📅 Today's Activity", str(today_loans))
        grid.addWidget(activity_box, 1, 2)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        return tab
    
    def create_stat_box(self, title, value):
        """Create a styled statistics box"""
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 32px; font-weight: bold; padding: 20px;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        return box
    
    def create_popular_tab(self):
        """Create popular books tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Period selector
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Period:"))
        self.popular_period = QComboBox()
        self.popular_period.addItems(["Last 30 Days", "Last 90 Days", "Last Year", "All Time"])
        self.popular_period.currentTextChanged.connect(self.load_popular_books)
        period_layout.addWidget(self.popular_period)
        period_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("📤 Export to CSV")
        export_btn.clicked.connect(lambda: self.export_popular_books())
        period_layout.addWidget(export_btn)
        
        layout.addLayout(period_layout)
        
        # Table
        self.popular_table = QTableWidget()
        self.popular_table.setColumnCount(4)
        self.popular_table.setHorizontalHeaderLabels(["Title", "Author", "Times Borrowed", "Currently Available"])
        self.popular_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.popular_table.setAlternatingRowColors(True)
        layout.addWidget(self.popular_table)
        
        self.load_popular_books()
        
        return tab
    
    def load_popular_books(self):
        """Load and display popular books"""
        period = self.popular_period.currentText()
        days = {"Last 30 Days": 30, "Last 90 Days": 90, "Last Year": 365, "All Time": 0}
        popular = self.crud.get_popular_books(days.get(period, 0))
        
        self.popular_table.setRowCount(len(popular))
        for row, book in enumerate(popular):
            self.popular_table.setItem(row, 0, QTableWidgetItem(book.get('title', '')))
            self.popular_table.setItem(row, 1, QTableWidgetItem(book.get('author', '')))
            self.popular_table.setItem(row, 2, QTableWidgetItem(str(book.get('borrow_count', 0))))
            available = book.get('copies_available', 0)
            avail_item = QTableWidgetItem(str(available))
            if available == 0:
                avail_item.setForeground(QColor(255, 0, 0))
            self.popular_table.setItem(row, 3, avail_item)
    
    def create_overdue_tab(self):
        """Create overdue items tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_overdue_items)
        layout.addWidget(refresh_btn)
        
        # Table
        self.overdue_table = QTableWidget()
        self.overdue_table.setColumnCount(5)
        self.overdue_table.setHorizontalHeaderLabels(["Book Title", "Patron", "Borrowed Date", "Due Date", "Days Overdue"])
        self.overdue_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.overdue_table.setAlternatingRowColors(True)
        layout.addWidget(self.overdue_table)
        
        # Export button
        export_btn = QPushButton("📤 Export Overdue List")
        export_btn.clicked.connect(self.export_overdue_list)
        layout.addWidget(export_btn)
        
        self.load_overdue_items()
        
        return tab
    
    def load_overdue_items(self):
        """Load and display overdue items"""
        overdue = self.crud.get_overdue_loans()
        
        self.overdue_table.setRowCount(len(overdue))
        now = datetime.now().timestamp()
        
        for row, loan in enumerate(overdue):
            self.overdue_table.setItem(row, 0, QTableWidgetItem(loan.get('title', '')))
            self.overdue_table.setItem(row, 1, QTableWidgetItem(loan.get('patron_name', '')))
            
            checkout = datetime.fromtimestamp(loan.get('checkout_time', 0)).strftime('%Y-%m-%d')
            self.overdue_table.setItem(row, 2, QTableWidgetItem(checkout))
            
            due = datetime.fromtimestamp(loan.get('due_time', 0)).strftime('%Y-%m-%d')
            due_item = QTableWidgetItem(due)
            due_item.setForeground(QColor(255, 0, 0))
            self.overdue_table.setItem(row, 3, due_item)
            
            days_overdue = int((now - loan.get('due_time', now)) / 86400)
            overdue_item = QTableWidgetItem(f"{days_overdue} days")
            overdue_item.setForeground(QColor(255, 0, 0))
            self.overdue_table.setItem(row, 4, overdue_item)
    
    def create_circulation_tab(self):
        """Create circulation history tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Date range selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)
        
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_circulation_history)
        date_layout.addWidget(load_btn)
        
        export_btn = QPushButton("📤 Export to CSV")
        export_btn.clicked.connect(self.export_circulation_history)
        date_layout.addWidget(export_btn)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Table
        self.circulation_table = QTableWidget()
        self.circulation_table.setColumnCount(5)
        self.circulation_table.setHorizontalHeaderLabels(["Date", "Action", "Book", "Patron", "Due Date"])
        self.circulation_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.circulation_table.setAlternatingRowColors(True)
        layout.addWidget(self.circulation_table)
        
        self.load_circulation_history()
        
        return tab
    
    def qdate_to_timestamp(self, qdate):
        """Convert QDate to timestamp"""
        return int(datetime(qdate.year(), qdate.month(), qdate.day()).timestamp())
    
    def load_circulation_history(self):
        """Load circulation history for date range"""
        start_ts = self.qdate_to_timestamp(self.start_date.date())
        end_ts = self.qdate_to_timestamp(self.end_date.date()) + 86400
        
        history = self.crud.get_circulation_history(start_ts, end_ts)
        
        self.circulation_table.setRowCount(len(history))
        for row, record in enumerate(history):
            date = datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M')
            self.circulation_table.setItem(row, 0, QTableWidgetItem(date))
            self.circulation_table.setItem(row, 1, QTableWidgetItem(record.get('action', '')))
            self.circulation_table.setItem(row, 2, QTableWidgetItem(record.get('book_title', '')))
            self.circulation_table.setItem(row, 3, QTableWidgetItem(record.get('patron_name', '')))
            due = datetime.fromtimestamp(record.get('due_time', 0)).strftime('%Y-%m-%d') if record.get('due_time') else ''
            self.circulation_table.setItem(row, 4, QTableWidgetItem(due))
    
    def create_grant_tab(self):
        """Create grant report tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Report info
        info_label = QLabel("Generate a professional report for grant applications or board meetings.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Report options
        options_group = QGroupBox("Report Options")
        options_layout = QGridLayout(options_group)
        
        options_layout.addWidget(QLabel("Report Period:"), 0, 0)
        self.report_period = QComboBox()
        self.report_period.addItems(["Last 30 Days", "Last Quarter", "Last Year", "Custom"])
        options_layout.addWidget(self.report_period, 0, 1)
        
        options_layout.addWidget(QLabel("Library Name:"), 1, 0)
        self.library_name = QComboBox()
        self.library_name.setEditable(True)
        self.library_name.addItem("Your Library Name")
        options_layout.addWidget(self.library_name, 1, 1)
        
        options_layout.addWidget(QLabel("Prepared By:"), 2, 0)
        self.prepared_by = QComboBox()
        self.prepared_by.setEditable(True)
        self.prepared_by.addItem("Librarian Name")
        options_layout.addWidget(self.prepared_by, 2, 1)
        
        layout.addWidget(options_group)
        
        # Generate button
        generate_btn = QPushButton("📄 Generate Grant Report")
        generate_btn.clicked.connect(self.generate_grant_report)
        layout.addWidget(generate_btn)
        
        # Preview area
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        layout.addWidget(self.report_preview)
        
        return tab
    
    def generate_grant_report(self):
        """Generate a formatted grant report"""
        stats = self.crud.get_stats()
        popular = self.crud.get_popular_books(30)
        patrons = len(self.crud.get_all_patrons())
        overdue = len(self.crud.get_overdue_loans())
        
        report = f"""
HEARTLIB GRANT REPORT
=====================

Library: {self.library_name.currentText()}
Prepared By: {self.prepared_by.currentText()}
Date: {datetime.now().strftime('%B %d, %Y')}
Period: {self.report_period.currentText()}

SECTION 1: COLLECTION OVERVIEW
-------------------------------
Total Books in Collection: {stats['total_books']}
Books Currently Available: {stats['available']}
Books Checked Out: {stats['checked_out']}
Active Patrons: {patrons}

SECTION 2: CIRCULATION STATISTICS
----------------------------------
Active Loans: {stats['active_loans']}
Overdue Items: {overdue}
Items Checked Out Per Patron (avg): {stats['checked_out'] / max(patrons, 1):.1f}

SECTION 3: COMMUNITY ENGAGEMENT
-------------------------------
Total Patrons Served: {patrons}
Most Popular Books (Last 30 Days):
"""
        for i, book in enumerate(popular[:5], 1):
            report += f"  {i}. {book.get('title', 'Unknown')} - {book.get('borrow_count', 0)} borrows\n"
        
        report += f"""
SECTION 4: IMPACT SUMMARY
------------------------
HeartLib has successfully served {patrons} patrons with a collection of {stats['total_books']} books.
Current circulation rate shows active engagement with {stats['active_loans']} items currently in patron hands.

This report demonstrates the vital role HeartLib plays in our community's literacy,
education, and access to knowledge.

_________________________________________
Signature
"""
        
        self.report_preview.setText(report)
    
    def save_report(self, report_text):
        """Save report to file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Report", f"grant_report_{datetime.now().strftime('%Y%m%d')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_text)
            QMessageBox.information(self, "Report Saved", f"Report saved to {filepath}")
    
    def get_today_activity(self):
        """Get today's circulation activity count"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
        stats = self.crud.get_circulation_stats(today_start)
        return stats.get('total', 0)
    
    def export_popular_books(self):
        """Export popular books to CSV"""
        period = self.popular_period.currentText()
        days = {"Last 30 Days": 30, "Last 90 Days": 90, "Last Year": 365, "All Time": 0}
        popular = self.crud.get_popular_books(days.get(period, 0))
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Popular Books", f"popular_books_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        if filepath:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Title', 'Author', 'Times Borrowed', 'Available'])
                writer.writeheader()
                for book in popular:
                    writer.writerow({
                        'Title': book.get('title', ''),
                        'Author': book.get('author', ''),
                        'Times Borrowed': book.get('borrow_count', 0),
                        'Available': book.get('copies_available', 0)
                    })
            QMessageBox.information(self, "Export Complete", f"Exported to {filepath}")
    
    def export_overdue_list(self):
        """Export overdue items to CSV"""
        overdue = self.crud.get_overdue_loans()
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Overdue List", f"overdue_items_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        if filepath:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Book Title', 'Patron', 'Due Date', 'Days Overdue'])
                writer.writeheader()
                now = datetime.now().timestamp()
                for loan in overdue:
                    days = int((now - loan.get('due_time', now)) / 86400)
                    writer.writerow({
                        'Book Title': loan.get('title', ''),
                        'Patron': loan.get('patron_name', ''),
                        'Due Date': datetime.fromtimestamp(loan.get('due_time', 0)).strftime('%Y-%m-%d'),
                        'Days Overdue': days
                    })
            QMessageBox.information(self, "Export Complete", f"Exported to {filepath}")
    
    def export_circulation_history(self):
        """Export circulation history to CSV"""
        start_ts = self.qdate_to_timestamp(self.start_date.date())
        end_ts = self.qdate_to_timestamp(self.end_date.date()) + 86400
        history = self.crud.get_circulation_history(start_ts, end_ts)
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Circulation History", f"circulation_history_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        if filepath:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Date', 'Action', 'Book', 'Patron', 'Due Date'])
                writer.writeheader()
                for record in history:
                    writer.writerow({
                        'Date': datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M'),
                        'Action': record.get('action', ''),
                        'Book': record.get('book_title', ''),
                        'Patron': record.get('patron_name', ''),
                        'Due Date': datetime.fromtimestamp(record.get('due_time', 0)).strftime('%Y-%m-%d') if record.get('due_time') else ''
                    })
            QMessageBox.information(self, "Export Complete", f"Exported to {filepath}")
