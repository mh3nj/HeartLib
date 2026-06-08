import cv2
from pyzbar import pyzbar
import time

class BatchScanner:
    def __init__(self):
        self.cap = None
    
    def scan_barcodes(self, on_barcode, on_finish):
        """Opens camera, scans barcodes one after another until user presses ESC."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            return
        
        scanned = set()
        print("Batch scanner started. Show barcode to camera. Press SPACE to skip, ESC to finish.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            decoded = pyzbar.decode(frame)
            for d in decoded:
                code = d.data.decode('utf-8')
                if code not in scanned:
                    scanned.add(code)
                    on_barcode(code)
                    # Draw green rectangle
                    points = d.polygon
                    if len(points) == 4:
                        pts = [(p.x, p.y) for p in points]
                        cv2.polylines(frame, [np.array(pts, np.int32)], True, (0,255,0), 2)
                    cv2.putText(frame, code, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.imshow("Batch Scanner - Press ESC to finish", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
        self.cap.release()
        cv2.destroyAllWindows()
        on_finish(list(scanned))