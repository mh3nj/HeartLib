# heartlib/gui/barcode_scanner.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QMessageBox, QLineEdit, QDialogButtonBox, QWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
from pyzbar import pyzbar

class BarcodeScannerDialog(QDialog):
    barcode_scanned = pyqtSignal(str)
    
    def __init__(self, mode="book", parent=None):
        """
        mode: "book" for book ISBN/barcode, "patron" for patron barcode
        """
        super().__init__(parent)
        self.mode = mode
        self.camera_active = False
        self.camera = None
        self.timer = None
        self.setWindowTitle(f"Scan {'Book' if mode == 'book' else 'Patron'} Barcode")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Mode selection (camera or manual)
        mode_layout = QHBoxLayout()
        self.camera_btn = QPushButton("📷 Use Camera")
        self.camera_btn.clicked.connect(self.start_camera_mode)
        self.manual_btn = QPushButton("✏️ Manual Entry")
        self.manual_btn.clicked.connect(self.manual_input)
        mode_layout.addWidget(self.camera_btn)
        mode_layout.addWidget(self.manual_btn)
        layout.addLayout(mode_layout)
        
        # Camera view area (hidden initially)
        self.camera_widget = QWidget()
        camera_layout = QVBoxLayout(self.camera_widget)
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: #333; border: 2px solid gray; min-height: 300px;")
        camera_layout.addWidget(self.video_label)
        
        self.instruction_label = QLabel("Click 'Start Camera' to begin scanning")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet("padding: 10px;")
        camera_layout.addWidget(self.instruction_label)
        
        self.scanned_label = QLabel("")
        self.scanned_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        camera_layout.addWidget(self.scanned_label)
        
        self.stop_camera_btn = QPushButton("⏹️ Stop Camera")
        self.stop_camera_btn.clicked.connect(self.stop_camera_mode)
        self.stop_camera_btn.setEnabled(False)
        camera_layout.addWidget(self.stop_camera_btn)
        
        layout.addWidget(self.camera_widget)
        self.camera_widget.hide()
        
        # Manual entry area (hidden initially)
        self.manual_widget = QWidget()
        manual_layout = QVBoxLayout(self.manual_widget)
        
        manual_layout.addWidget(QLabel(f"Enter {mode} barcode manually:"))
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Type or paste barcode here...")
        self.barcode_input.returnPressed.connect(self.submit_manual)
        manual_layout.addWidget(self.barcode_input)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.submit_manual)
        btn_box.rejected.connect(self.stop_camera_mode)
        manual_layout.addWidget(btn_box)
        
        layout.addWidget(self.manual_widget)
        self.manual_widget.hide()
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
    
    def start_camera_mode(self):
        """Initialize and start camera"""
        self.camera_widget.show()
        self.manual_widget.hide()
        self.camera_btn.setEnabled(False)
        self.manual_btn.setEnabled(True)
        
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("Could not open camera")
            
            self.camera_active = True
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
            
            self.instruction_label.setText("📷 Position barcode in front of camera")
            self.stop_camera_btn.setEnabled(True)
            self.scanned_label.setText("Waiting for scan...")
        except Exception as e:
            QMessageBox.warning(self, "Camera Error", 
                               f"Could not open camera: {str(e)}\n\nPlease use Manual Entry instead.")
            self.stop_camera_mode()
            self.manual_input()
    
    def stop_camera_mode(self):
        """Stop camera and clean up"""
        if self.timer:
            self.timer.stop()
            self.timer = None
        if self.camera:
            self.camera.release()
            self.camera = None
        self.camera_active = False
        self.camera_widget.hide()
        self.camera_btn.setEnabled(True)
        self.stop_camera_btn.setEnabled(False)
        self.video_label.clear()
    
    def update_frame(self):
        """Capture and process camera frame"""
        if not self.camera_active or self.camera is None:
            return
        
        ret, frame = self.camera.read()
        if not ret:
            return
        
        # Convert to RGB for display
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Scale to fit label
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.video_label.width(), self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)
        
        # Scan for barcodes
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            # Draw rectangle around barcode
            points = barcode.polygon
            if len(points) == 4:
                pts = np.array([(p.x, p.y) for p in points], np.int32)
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            
            self.scanned_label.setText(f"✅ Scanned: {barcode_data} ({barcode_type})")
            self.scanned_label.setStyleSheet("color: green; padding: 5px; font-weight: bold;")
            
            self.barcode_scanned.emit(barcode_data)
            self.stop_camera_mode()
            self.accept()
            return
    
    def manual_input(self):
        """Switch to manual entry mode"""
        self.camera_widget.hide()
        self.manual_widget.show()
        self.camera_btn.setEnabled(True)
        self.manual_btn.setEnabled(False)
        self.stop_camera_mode()
        self.barcode_input.clear()  # Clear any previous input
        self.barcode_input.setFocus()
    
    def submit_manual(self):
        """Submit manually entered barcode"""
        barcode = self.barcode_input.text().strip()
        if barcode:
            self.barcode_scanned.emit(barcode)
            self.accept()
        else:
            QMessageBox.warning(self, "Empty Barcode", "Please enter a barcode.")
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.stop_camera_mode()
        event.accept()