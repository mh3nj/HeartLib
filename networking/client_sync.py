# heartlib/networking/client_sync.py
"""HeartLib sync client - coming in v2.0"""

class SyncClient:
    """Client for syncing with HeartLib server"""
    
    def __init__(self, server_url):
        self.server_url = server_url
    
    def sync(self):
        """Sync local database with server"""
        print(f"Syncing with {self.server_url} - coming in v2.0")
        return True