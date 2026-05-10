# heartlib/networking/server.py
"""HeartLib sync server - coming in v2.0"""

class SyncServer:
    """Central server for multi-device sync"""
    
    def __init__(self, db_path, port=8765):
        self.db_path = db_path
        self.port = port
    
    def start(self):
        """Start the sync server"""
        print(f"Sync server starting on port {self.port} - coming in v2.0")
    
    def stop(self):
        """Stop the sync server"""
        print("Sync server stopped")
