# heartlib/gui/settings_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QPushButton, QGroupBox,
                             QSpinBox, QComboBox, QCheckBox, QLineEdit,
                             QFileDialog, QMessageBox, QFormLayout)
from PyQt6.QtCore import Qt, QSettings

class SettingsDialog(QDialog):
    def __init__(self, crud, config, theme_manager, parent=None):
        super().__init__(parent)
        self.crud = crud
        self.config = config
        self.theme_manager = theme_manager
        self.setWindowTitle("⚙️ HeartLib Settings")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Circulation tab
        circulation_tab = self.create_circulation_tab()
        tabs.addTab(circulation_tab, "Circulation")
        
        # Sync tab (v2.0)
        sync_tab = self.create_sync_tab()
        tabs.addTab(sync_tab, "Sync")
        qr_btn = QPushButton("📱 Show Patron QR Code")
        qr_btn.clicked.connect(self.show_qrcode)
        
        # Backup tab
        backup_tab = self.create_backup_tab()
        tabs.addTab(backup_tab, "Backup")
        
        # About tab
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "About")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Load current settings
        self.load_settings()
    
    def create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Library info
        library_group = QGroupBox("Library Information")
        library_layout = QFormLayout(library_group)
        
        self.library_name = QLineEdit()
        self.library_name.setPlaceholderText("Your Library Name")
        library_layout.addRow("Library Name:", self.library_name)
        
        self.library_address = QLineEdit()
        self.library_address.setPlaceholderText("Library Address")
        library_layout.addRow("Address:", self.library_address)
        
        self.library_phone = QLineEdit()
        self.library_phone.setPlaceholderText("Phone Number")
        library_layout.addRow("Phone:", self.library_phone)
        
        self.library_email = QLineEdit()
        self.library_email.setPlaceholderText("Email")
        library_layout.addRow("Email:", self.library_email)
        
        layout.addWidget(library_group)
        
        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout(display_group)
        
        self.default_theme = QComboBox()
        self.default_theme.addItems(self.theme_manager.get_theme_list())
        display_layout.addRow("Default Theme:", self.default_theme)
        
        self.items_per_page = QSpinBox()
        self.items_per_page.setMinimum(10)
        self.items_per_page.setMaximum(200)
        self.items_per_page.setValue(50)
        display_layout.addRow("Items Per Page:", self.items_per_page)
        
        layout.addWidget(display_group)
        
        layout.addStretch()
        return tab
    
    def create_circulation_tab(self):
        """Create circulation settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Loan settings
        loan_group = QGroupBox("Loan Settings")
        loan_layout = QFormLayout(loan_group)
        
        self.default_loan_days = QSpinBox()
        self.default_loan_days.setMinimum(1)
        self.default_loan_days.setMaximum(365)
        self.default_loan_days.setValue(14)
        loan_layout.addRow("Default Loan Period (days):", self.default_loan_days)
        
        self.max_loans_per_patron = QSpinBox()
        self.max_loans_per_patron.setMinimum(1)
        self.max_loans_per_patron.setMaximum(100)
        self.max_loans_per_patron.setValue(10)
        loan_layout.addRow("Max Loans Per Patron:", self.max_loans_per_patron)
        
        layout.addWidget(loan_group)
        
        # Fine settings (optional - kindness mode)
        fine_group = QGroupBox("Fine Settings (Kindness Mode)")
        fine_layout = QFormLayout(fine_group)
        
        self.enable_fines = QCheckBox("Enable late fines")
        fine_layout.addRow(self.enable_fines)
        
        self.fine_per_day = QSpinBox()
        self.fine_per_day.setMinimum(0)
        self.fine_per_day.setMaximum(100)
        self.fine_per_day.setValue(25)
        fine_layout.addRow("Fine per day (cents):", self.fine_per_day)
        
        layout.addWidget(fine_group)
        
        layout.addStretch()
        return tab
    
    def create_sync_tab(self):
        """Create sync settings tab (v2.0)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        sync_group = QGroupBox("Sync Settings (v2.0)")
        sync_layout = QFormLayout(sync_group)
        
        self.enable_sync = QCheckBox("Enable automatic sync")
        sync_layout.addRow(self.enable_sync)
        
        self.sync_interval = QSpinBox()
        self.sync_interval.setMinimum(1)
        self.sync_interval.setMaximum(60)
        self.sync_interval.setValue(30)
        sync_layout.addRow("Sync Interval (minutes):", self.sync_interval)
        
        self.server_host = QLineEdit()
        self.server_host.setText("localhost")
        self.server_host.setPlaceholderText("Server IP address")
        sync_layout.addRow("Server Host:", self.server_host)
        
        self.server_port = QSpinBox()
        self.server_port.setMinimum(1024)
        self.server_port.setMaximum(65535)
        self.server_port.setValue(8765)
        sync_layout.addRow("Server Port:", self.server_port)
        
        layout.addWidget(sync_group)
        
        # Server control
        server_control_group = QGroupBox("Server Control")
        server_control_layout = QVBoxLayout(server_control_group)
        
        self.start_server_btn = QPushButton("🚀 Start Sync Server")
        self.start_server_btn.clicked.connect(self.start_server)
        server_control_layout.addWidget(self.start_server_btn)
        
        self.stop_server_btn = QPushButton("⏹️ Stop Sync Server")
        self.stop_server_btn.setEnabled(False)
        self.stop_server_btn.clicked.connect(self.stop_server)
        server_control_layout.addWidget(self.stop_server_btn)
        
        layout.addWidget(server_control_group)
        
        layout.addStretch()
        return tab
    
    def create_backup_tab(self):
        """Create backup settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        backup_group = QGroupBox("Backup Settings")
        backup_layout = QFormLayout(backup_group)
        
        self.enable_auto_backup = QCheckBox("Enable automatic backups")
        backup_layout.addRow(self.enable_auto_backup)
        
        self.backup_interval = QSpinBox()
        self.backup_interval.setMinimum(1)
        self.backup_interval.setMaximum(30)
        self.backup_interval.setValue(7)
        backup_layout.addRow("Backup Interval (days):", self.backup_interval)
        
        self.backup_location = QLineEdit()
        self.backup_location.setPlaceholderText("Backup folder location")
        backup_layout.addRow("Backup Location:", self.backup_location)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_backup_location)
        backup_layout.addRow("", browse_btn)
        
        layout.addWidget(backup_group)
        
        # Manual backup
        manual_group = QGroupBox("Manual Backup")
        manual_layout = QVBoxLayout(manual_group)
        
        backup_now_btn = QPushButton("💾 Create Backup Now")
        backup_now_btn.clicked.connect(self.create_backup)
        manual_layout.addWidget(backup_now_btn)
        
        restore_btn = QPushButton("🔄 Restore from Backup")
        restore_btn.clicked.connect(self.restore_backup)
        manual_layout.addWidget(restore_btn)
        
        layout.addWidget(manual_group)
        
        layout.addStretch()
        return tab
    
    def create_about_tab(self):
        """Create about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        about_text = QLabel("""
        <h1>❤️ HeartLib</h1>
        <p><b>Version 2.0</b></p>
        <p>A library management system with a heart.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
            <li>Complete book and patron management</li>
            <li>Barcode scanning support</li>
            <li>Checkout/return with due dates</li>
            <li>CSV import/export</li>
            <li>Beautiful reports dashboard</li>
            <li>Customizable themes</li>
            <li>Multi-device sync (v2.0)</li>
        </ul>
        <br>
        <p><b>Created with love for libraries everywhere.</b></p>
        <br>
        <p><i>"Because libraries have hearts, not just barcodes."</i></p>
        """)
        about_text.setWordWrap(True)
        about_text.setStyleSheet("padding: 20px;")
        about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(about_text)
        
        layout.addStretch()
        return tab
    
    def load_settings(self):
        """Load current settings from config"""
        self.library_name.setText(self.config.get("library_name", "HeartLib Library"))
        self.library_address.setText(self.config.get("library_address", ""))
        self.library_phone.setText(self.config.get("library_phone", ""))
        self.library_email.setText(self.config.get("library_email", ""))
        
        self.default_theme.setCurrentText(self.config.get("theme", "Light"))
        self.items_per_page.setValue(self.config.get("items_per_page", 50))
        
        self.default_loan_days.setValue(self.config.get("default_loan_days", 14))
        self.max_loans_per_patron.setValue(self.config.get("max_loans_per_patron", 10))
        
        self.enable_fines.setChecked(self.config.get("enable_fines", False))
        self.fine_per_day.setValue(self.config.get("fine_per_day", 25))
        
        self.enable_sync.setChecked(self.config.get("enable_sync", False))
        self.sync_interval.setValue(self.config.get("sync_interval", 30))
        self.server_host.setText(self.config.get("server_host", "localhost"))
        self.server_port.setValue(self.config.get("server_port", 8765))
        
        self.enable_auto_backup.setChecked(self.config.get("enable_auto_backup", True))
        self.backup_interval.setValue(self.config.get("backup_interval", 7))
        self.backup_location.setText(self.config.get("backup_location", "./backups"))
    
    def save_settings(self):
        """Save settings to config"""
        self.config.set("library_name", self.library_name.text())
        self.config.set("library_address", self.library_address.text())
        self.config.set("library_phone", self.library_phone.text())
        self.config.set("library_email", self.library_email.text())
        
        self.config.set("theme", self.default_theme.currentText())
        self.config.set("items_per_page", self.items_per_page.value())
        
        self.config.set("default_loan_days", self.default_loan_days.value())
        self.config.set("max_loans_per_patron", self.max_loans_per_patron.value())
        
        self.config.set("enable_fines", self.enable_fines.isChecked())
        self.config.set("fine_per_day", self.fine_per_day.value())
        
        self.config.set("enable_sync", self.enable_sync.isChecked())
        self.config.set("sync_interval", self.sync_interval.value())
        self.config.set("server_host", self.server_host.text())
        self.config.set("server_port", self.server_port.value())
        
        self.config.set("enable_auto_backup", self.enable_auto_backup.isChecked())
        self.config.set("backup_interval", self.backup_interval.value())
        self.config.set("backup_location", self.backup_location.text())
        
        # Apply theme if changed
        if self.default_theme.currentText() != self.config.get("theme", "Light"):
            self.theme_manager.load_theme_by_name(self.default_theme.currentText())
        
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved.")
        self.accept()
    
    def browse_backup_location(self):
        """Browse for backup folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if folder:
            self.backup_location.setText(folder)
    
    def create_backup(self):
        """Create a manual backup"""
        from utils.backup import BackupManager
        import os
        
        backup_dir = self.backup_location.text() or "./backups"
        backup_mgr = BackupManager(self.crud.db.db_path, backup_dir)
        backup_file = backup_mgr.create_backup()
        
        if backup_file:
            QMessageBox.information(self, "Backup Created", f"Backup saved to:\n{backup_file}")
        else:
            QMessageBox.warning(self, "Backup Failed", "Could not create backup.")
    
    def show_qrcode(self):
        from gui.qrcode_dialog import QRCodeDialog
        local_ip = socket.gethostbyname(socket.gethostname())
        url = f"http://{local_ip}:8766"
        dialog = QRCodeDialog(url, self)
        dialog.exec()

    def restore_backup(self):
        """Restore from backup file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "", "Database Files (*.db);;All Files (*)"
        )
        if filepath:
            reply = QMessageBox.question(self, "Restore Backup", 
                                        "Restoring will replace current data.\nAre you sure?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                from utils.backup import BackupManager
                backup_mgr = BackupManager(self.crud.db.db_path, "")
                if backup_mgr.restore_backup(filepath):
                    QMessageBox.information(self, "Restore Complete", "Database restored. Please restart HeartLib.")
                else:
                    QMessageBox.warning(self, "Restore Failed", "Could not restore backup.")
    
    def start_server(self):
        """Start sync server"""
        try:
            from networking.sync_server import SyncServer
            import threading
            
            if not hasattr(self, '_sync_server'):
                self._sync_server = SyncServer(self.crud, host=self.server_host.text(), port=self.server_port.value())
                server_thread = threading.Thread(target=self._sync_server.start, daemon=True)
                server_thread.start()
                self.start_server_btn.setEnabled(False)
                self.stop_server_btn.setEnabled(True)
                QMessageBox.information(self, "Server Started", f"Sync server running on port {self.server_port.value()}")
        except Exception as e:
            QMessageBox.warning(self, "Server Error", f"Could not start server: {e}")
    
    def stop_server(self):
        """Stop sync server"""
        if hasattr(self, '_sync_server') and self._sync_server:
            self._sync_server.stop()
            self._sync_server = None
            self.start_server_btn.setEnabled(True)
            self.stop_server_btn.setEnabled(False)
            QMessageBox.information(self, "Server Stopped", "Sync server has been stopped.")