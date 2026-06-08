import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image
import io

class CameraBatchScanner:
    def __init__(self):
        self.cap = None
    
    def scan_books_from_camera(self, num_books=10):
        """Capture multiple book spines and read barcodes/ISBNs"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Cannot open camera")
        
        barcodes = []
        print("Position book barcode in front of camera. Press SPACE to capture, ESC to finish.")
        
        while len(barcodes) < num_books:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Display frame
            cv2.imshow("Batch Scanner - Press SPACE to capture, ESC to finish", frame)
            
            # Scan for barcodes in current frame
            decoded = pyzbar.decode(frame)
            if decoded:
                for d in decoded:
                    code = d.data.decode('utf-8')
                    if code not in barcodes:
                        barcodes.append(code)
                        print(f"Captured: {code}")
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                # Force capture even if no barcode visible? We already scan continuously.
                pass
        
        self.cap.release()
        cv2.destroyAllWindows()
        return barcodes