# heartlib/database/db_manager.py
import sqlite3
import os
import uuid
from datetime import datetime
from typing import Optional

class DatabaseManager:
    def __init__(self, db_path: str = "heartlib.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def _init_db(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                isbn TEXT,
                copies_total INTEGER DEFAULT 1,
                copies_available INTEGER DEFAULT 1,
                location TEXT,
                description TEXT,
                last_modified INTEGER,
                sync_version INTEGER DEFAULT 1,
                deleted INTEGER DEFAULT 0
            )
        ''')
        
        # Patrons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patrons (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                barcode TEXT UNIQUE,
                join_date INTEGER,
                last_modified INTEGER,
                sync_version INTEGER DEFAULT 1,
                deleted INTEGER DEFAULT 0
            )
        ''')
        
        # Loans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id TEXT PRIMARY KEY,
                book_id TEXT,
                patron_id TEXT,
                checkout_time INTEGER,
                due_time INTEGER,
                return_time INTEGER,
                last_modified INTEGER,
                sync_version INTEGER DEFAULT 1,
                FOREIGN KEY(book_id) REFERENCES books(id),
                FOREIGN KEY(patron_id) REFERENCES patrons(id)
            )
        ''')
        
        # Sync metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_metadata (
                device_id TEXT PRIMARY KEY,
                last_sync_timestamp INTEGER,
                server_url TEXT
            )
        ''')
        
        # Sync queue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
                id TEXT PRIMARY KEY,
                device_id TEXT,
                table_name TEXT,
                record_id TEXT,
                operation TEXT,
                old_data TEXT,
                new_data TEXT,
                timestamp INTEGER,
                synced INTEGER DEFAULT 0,
                conflict_resolved INTEGER DEFAULT 0
            )
        ''')

        # Devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                name TEXT,
                last_seen INTEGER,
                is_server INTEGER DEFAULT 0,
                encryption_key TEXT
            )
        ''')

        # Sync metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')


        conn.commit()
        
        # Insert some sample books if table is empty
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            self._insert_sample_books()
    
    def _insert_sample_books(self):
        """Add sample books for testing"""
        sample_books = [
            ("Dune", "Frank Herbert", "9780441013593", "Sci-Fi Section", "The classic sci-fi epic about desert planet Arrakis"),
            ("Python Crash Course", "Eric Matthes", "9781593279288", "Programming", "Learn Python fast with hands-on projects"),
            ("The Name of the Wind", "Patrick Rothfuss", "9780756404741", "Fantasy", "A legendary fantasy epic"),
            ("1984", "George Orwell", "9780451524935", "Classics", "Dystopian masterpiece about surveillance and control"),
            ("Pride and Prejudice", "Jane Austen", "9780141439518", "Classics", "Timeless romance and social commentary"),
        ]
        
        cursor = self.conn.cursor()
        for title, author, isbn, location, desc in sample_books:
            cursor.execute('''
                INSERT INTO books (id, title, author, isbn, copies_total, copies_available, location, description, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), title, author, isbn, 1, 1, location, desc, int(datetime.now().timestamp())))
        
        self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None