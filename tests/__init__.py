# tests/test_sync.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from database import DatabaseManager, CRUD
from database.models import Book
from networking.sync_server import SyncServer
from networking.sync_client import SyncClient

def test_sync():
    print("=" * 50)
    print("🧪 Testing HeartLib v2.0 Sync Engine")
    print("=" * 50)
    
    # Create two separate databases in temp location
    import tempfile
    import os
    
    master_path = os.path.join(tempfile.gettempdir(), "test_master.db")
    client_path = os.path.join(tempfile.gettempdir(), "test_client.db")
    
    print(f"\n📁 Master DB: {master_path}")
    print(f"📁 Client DB: {client_path}")
    
    # Create databases
    db_master = DatabaseManager(master_path)
    db_client = DatabaseManager(client_path)
    
    crud_master = CRUD(db_master)
    crud_client = CRUD(db_client)
    
    # Clear any existing data
    conn = db_master.get_connection()
    conn.execute("DELETE FROM books")
    conn.commit()
    
    conn = db_client.get_connection()
    conn.execute("DELETE FROM books")
    conn.commit()
    
    # Add a book to master
    print("\n📚 Adding book to MASTER...")
    book = Book(title="Sync Test Book", author="Test Author", copies_total=5)
    crud_master.add_book(book)
    print(f"   Added: {book.title} (ID: {book.id[:8]}...)")
    
    # Start sync server (in background thread)
    print("\n🚀 Starting sync server...")
    server = SyncServer(crud_master, host='localhost', port=8765)
    
    import threading
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(2)  # Give server time to start
    
    # Run sync client
    print("\n🔄 Running sync client...")
    client = SyncClient(crud_client, server_host='localhost', server_port=8765)
    success = client.sync()
    
    if success:
        print("\n✅ SYNC SUCCESSFUL!")
        
        # Verify book was synced to client
        books = crud_client.get_all_books()
        print(f"\n📚 Client now has {len(books)} book(s):")
        for b in books:
            print(f"   - {b['title']} by {b['author']}")
    else:
        print("\n❌ SYNC FAILED")
    
    # Stop server
    server.stop()
    
    # Clean up
    try:
        os.remove(master_path)
        os.remove(client_path)
    except:
        pass
    
    print("\n🏁 Test complete!")

if __name__ == "__main__":
    test_sync()