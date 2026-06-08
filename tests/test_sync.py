# test_sync.py
import time
from database import DatabaseManager, CRUD
from database.models import Book
from networking.sync_server import SyncServer
from networking.sync_client import SyncClient

def test_sync():
    print("=" * 50)
    print("🧪 Testing HeartLib v2.0 Sync Engine")
    print("=" * 50)
    
    # Create two separate databases
    print("\n📁 Creating databases...")
    db_master = DatabaseManager("test_master.db")
    db_client = DatabaseManager("test_client.db")
    
    crud_master = CRUD(db_master)
    crud_client = CRUD(db_client)
    
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
    time.sleep(1)  # Give server time to start
    
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
    print("\n🏁 Test complete!")

if __name__ == "__main__":
    test_sync()