# heartlib/gui/csv_import_export.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFileDialog, QProgressBar, QTextEdit,
                             QMessageBox, QTabWidget, QWidget, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import csv
import os
from datetime import datetime
import uuid

class ImportWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(int, list)
    error = pyqtSignal(str)
    
    def __init__(self, filepath, import_type, crud):
        super().__init__()
        self.filepath = filepath
        self.import_type = import_type
        self.crud = crud
    
    def run(self):
        try:
            count = 0
            errors = []
            
            with open(self.filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if self.import_type == "books":
                            self.import_book(row)
                        else:
                            self.import_patron(row)
                        count += 1
                        self.progress.emit(int(count), f"Imported {count} items...")
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
            
            self.finished.emit(count, errors)
        except Exception as e:
            self.error.emit(str(e))
    
    def import_book(self, row):
        """Import a book from CSV row"""
        from database.models import Book
        
        book = Book(
            id=row.get('id', str(uuid.uuid4())),
            title=row.get('title', ''),
            author=row.get('author', ''),
            isbn=row.get('isbn', ''),
            copies_total=int(row.get('copies_total', 1)),
            copies_available=int(row.get('copies_available', row.get('copies_total', 1))),
            location=row.get('location', ''),
            description=row.get('description', ''),
            last_modified=int(datetime.now().timestamp())
        )
        self.crud.add_book(book)
    
    def import_patron(self, row):
        """Import a patron from CSV row"""
        from database.models import Patron
        
        patron = Patron(
            id=row.get('id', str(uuid.uuid4())),
            name=row.get('name', ''),
            email=row.get('email', ''),
            phone=row.get('phone', ''),
            barcode=row.get('barcode', f"LIB{uuid.uuid4().hex[:8].upper()}"),
            join_date=int(row.get('join_date', datetime.now().timestamp()))
        )
        self.crud.add_patron(patron)


class CSVImportExportDialog(QDialog):
    def __init__(self, crud, parent=None):
        super().__init__(parent)
        self.crud = crud
        self.setWindowTitle("CSV Import / Export")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Import tab
        import_tab = QWidget()
        import_layout = QVBoxLayout(import_tab)
        
        # Import type selection
        import_type_layout = QHBoxLayout()
        import_type_layout.addWidget(QLabel("Import Type:"))
        self.import_type = QComboBox()
        self.import_type.addItems(["Books", "Patrons"])
        import_type_layout.addWidget(self.import_type)
        import_type_layout.addStretch()
        import_layout.addLayout(import_type_layout)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 5px; border: 1px solid gray;")
        file_layout.addWidget(self.file_label)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        import_layout.addLayout(file_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        import_layout.addWidget(self.progress_bar)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        import_layout.addWidget(self.status_text)
        
        # Import button
        self.import_btn = QPushButton("📥 Start Import")
        self.import_btn.clicked.connect(self.start_import)
        self.import_btn.setEnabled(False)
        import_layout.addWidget(self.import_btn)
        
        import_layout.addStretch()
        
        # Export tab
        export_tab = QWidget()
        export_layout = QVBoxLayout(export_tab)
        
        export_type_layout = QHBoxLayout()
        export_type_layout.addWidget(QLabel("Export Type:"))
        self.export_type = QComboBox()
        self.export_type.addItems(["Books", "Patrons", "Both (separate files)"])
        export_type_layout.addWidget(self.export_type)
        export_type_layout.addStretch()
        export_layout.addLayout(export_type_layout)
        
        # Export buttons
        self.export_btn = QPushButton("📤 Export to CSV")
        self.export_btn.clicked.connect(self.start_export)
        export_layout.addWidget(self.export_btn)
        
        export_layout.addStretch()
        
        tabs.addTab(import_tab, "Import")
        tabs.addTab(export_tab, "Export")
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.selected_file = None
        self.import_worker = None
    
    def browse_file(self):
        """Select CSV file for import"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if filepath:
            self.selected_file = filepath
            self.file_label.setText(os.path.basename(filepath))
            self.import_btn.setEnabled(True)
    
    def start_import(self):
        """Start the import process"""
        if not self.selected_file:
            return
        
        self.import_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_text.clear()
        
        import_type = "books" if self.import_type.currentText() == "Books" else "patrons"
        
        self.import_worker = ImportWorker(self.selected_file, import_type, self.crud)
        self.import_worker.progress.connect(self.update_import_progress)
        self.import_worker.finished.connect(self.import_finished)
        self.import_worker.error.connect(self.import_error)
        self.import_worker.start()
    
    def update_import_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_text.append(message)
    
    def import_finished(self, count, errors):
        """Handle import completion"""
        self.status_text.append(f"\n✅ Import complete! {count} items imported.")
        if errors:
            self.status_text.append(f"\n⚠️ {len(errors)} errors:")
            for error in errors[:10]:
                self.status_text.append(f"  - {error}")
            if len(errors) > 10:
                self.status_text.append(f"  ... and {len(errors) - 10} more")
        
        QMessageBox.information(self, "Import Complete", 
                               f"Successfully imported {count} {self.import_type.currentText().lower()}.\n"
                               f"Errors: {len(errors)}")
        
        self.import_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
    
    def import_error(self, error_msg):
        """Handle import error"""
        QMessageBox.critical(self, "Import Error", f"Failed to import: {error_msg}")
        self.import_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
    
    def start_export(self):
        """Export data to CSV"""
        export_type = self.export_type.currentText()
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "", "CSV Files (*.csv)"
        )
        
        if not filepath:
            return
        
        try:
            if export_type == "Books":
                self.export_books(filepath)
            elif export_type == "Patrons":
                self.export_patrons(filepath)
            else:
                base_name = os.path.splitext(filepath)[0]
                self.export_books(f"{base_name}_books.csv")
                self.export_patrons(f"{base_name}_patrons.csv")
                QMessageBox.information(self, "Export Complete", 
                                       f"Exported to:\n{base_name}_books.csv\n{base_name}_patrons.csv")
                return
            
            QMessageBox.information(self, "Export Complete", f"Data exported to {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
    
    def export_books(self, filepath):
        """Export books to CSV"""
        books = self.crud.get_all_books()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if books:
                fieldnames = ['id', 'title', 'author', 'isbn', 'copies_total', 
                             'copies_available', 'location', 'description']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(books)
            else:
                f.write("No books found")
    
    def export_patrons(self, filepath):
        """Export patrons to CSV"""
        patrons = self.crud.get_all_patrons()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if patrons:
                fieldnames = ['id', 'name', 'email', 'phone', 'barcode', 'join_date']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(patrons)
            else:
                f.write("No patrons found")