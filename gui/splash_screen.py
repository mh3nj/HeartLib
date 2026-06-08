from PyQt6.QtWidgets import QSplashScreen, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
import os

class HeartLibSplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        logo_path = "resources/icons/heartlib_logo_256.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(scaled)
        else:
            self.setPixmap(QPixmap(300, 300))
            self.showMessage("HeartLib", Qt.AlignmentFlag.AlignCenter, Qt.white)