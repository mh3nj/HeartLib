# heartlib/database/crud.py
import sqlite3
from typing import List, Dict, Optional
from .db_manager import DatabaseManager
from .models import Book, Patron, Loan
from datetime import datetime
import uuid

class CRUD:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    # ----- Book operations -----
    def add_book(self, book: Book) -> str:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO books (id, title, author, isbn, copies_total, copies_available, 
                             location, description, last_modified, sync_version, deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (book.id, book.title, book.author, book.isbn, book.copies_total, book.copies_available,
              book.location, book.description, book.last_modified, book.sync_version, 0))
        conn.commit()
        return book.id
    
    def get_all_books(self) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE deleted = 0 ORDER BY title")
        return [dict(row) for row in cursor.fetchall()]
    
    def search_books(self, query: str) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM books 
            WHERE deleted = 0 AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)
            ORDER BY title
        ''', (search_term, search_term, search_term))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_book_by_id(self, book_id: str) -> Optional[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ? AND deleted = 0", (book_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_book(self, book_id: str, book_data: Dict) -> bool:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE books 
            SET title = ?, author = ?, isbn = ?, copies_total = ?, copies_available = ?,
                location = ?, description = ?, last_modified = ?, sync_version = sync_version + 1
            WHERE id = ?
        ''', (book_data['title'], book_data['author'], book_data['isbn'],
              book_data['copies_total'], book_data['copies_available'],
              book_data['location'], book_data['description'],
              int(datetime.now().timestamp()), book_id))
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_book(self, book_id: str) -> bool:
        """Soft delete - just mark as deleted"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE books SET deleted = 1, last_modified = ?, sync_version = sync_version + 1
            WHERE id = ?
        ''', (int(datetime.now().timestamp()), book_id))
        conn.commit()
        return cursor.rowcount > 0
    
    # ----- Patron operations (will add more later) -----
    def get_all_patrons(self) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patrons WHERE deleted = 0 ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    

    # Add to database/crud.py (inside CRUD class)

    def add_patron(self, patron) -> str:
        """Add a new patron to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO patrons (id, name, email, phone, barcode, join_date, last_modified, sync_version, deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patron.id, patron.name, patron.email, patron.phone, patron.barcode,
            patron.join_date, patron.last_modified, patron.sync_version, 0))
        conn.commit()
        return patron.id

    def get_all_patrons(self) -> List[Dict]:
        """Get all patrons"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patrons WHERE deleted = 0 ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def search_patrons(self, query: str) -> List[Dict]:
        """Search patrons by name, email, or barcode"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM patrons 
            WHERE deleted = 0 AND (name LIKE ? OR email LIKE ? OR barcode LIKE ?)
            ORDER BY name
        ''', (search_term, search_term, search_term))
        return [dict(row) for row in cursor.fetchall()]

    def get_patron_by_barcode(self, barcode: str):
        """Find patron by barcode (for scanning)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patrons WHERE barcode = ? AND deleted = 0", (barcode,))
        row = cursor.fetchone()
        return dict(row) if row else None


    def get_patron_by_id(self, patron_id: str) -> Optional[Dict]:
        """Get patron by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patrons WHERE id = ? AND deleted = 0", (patron_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # Add to CRUD class in database/crud.py

    def checkout_book(self, book_id: str, patron_id: str, due_timestamp: int) -> bool:
        """Check out a book to a patron"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check availability
        cursor.execute("SELECT copies_available FROM books WHERE id = ? AND deleted = 0", (book_id,))
        row = cursor.fetchone()
        if not row or row['copies_available'] <= 0:
            return False
        
        # Reduce available copies
        cursor.execute("UPDATE books SET copies_available = copies_available - 1 WHERE id = ?", (book_id,))
        
        # Create loan record
        now = int(datetime.now().timestamp())
        loan_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO loans (id, book_id, patron_id, checkout_time, due_time, last_modified, sync_version)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (loan_id, book_id, patron_id, now, due_timestamp, now, 1))
        
        conn.commit()
        return True

    def get_active_loans_for_patron(self, patron_id: str) -> List[Dict]:
        """Get all active loans for a patron"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, b.title, b.author 
            FROM loans l
            JOIN books b ON l.book_id = b.id
            WHERE l.patron_id = ? AND l.return_time IS NULL
            ORDER BY l.due_time
        ''', (patron_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_active_loans(self) -> List[Dict]:
        """Get all active loans with book and patron info"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, b.title, b.author, p.name as patron_name, p.barcode
            FROM loans l
            JOIN books b ON l.book_id = b.id
            JOIN patrons p ON l.patron_id = p.id
            WHERE l.return_time IS NULL AND b.deleted = 0 AND p.deleted = 0
            ORDER BY l.due_time
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def get_loan_by_id(self, loan_id: str) -> Optional[Dict]:
        """Get a specific loan by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, b.title, b.author, p.name as patron_name
            FROM loans l
            JOIN books b ON l.book_id = b.id
            JOIN patrons p ON l.patron_id = p.id
            WHERE l.id = ?
        ''', (loan_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def return_book(self, loan_id: str) -> bool:
        """Return a book by loan ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get the book_id from the loan
        cursor.execute("SELECT book_id FROM loans WHERE id = ? AND return_time IS NULL", (loan_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        book_id = row['book_id']
        now = int(datetime.now().timestamp())
        
        # Mark loan as returned
        cursor.execute('''
            UPDATE loans 
            SET return_time = ?, last_modified = ?, sync_version = sync_version + 1
            WHERE id = ?
        ''', (now, now, loan_id))
        
        # Increase available copies
        cursor.execute('''
            UPDATE books 
            SET copies_available = copies_available + 1, last_modified = ?, sync_version = sync_version + 1
            WHERE id = ?
        ''', (now, book_id))
        
        conn.commit()
        return True

    def get_popular_books(self, days: int = 30) -> List[Dict]:
        """Get most borrowed books in the last X days"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        since = int(datetime.now().timestamp()) - (days * 86400) if days > 0 else 0
        
        if days > 0:
            cursor.execute('''
                SELECT b.id, b.title, b.author, b.copies_available, COUNT(l.id) as borrow_count
                FROM books b
                JOIN loans l ON b.id = l.book_id
                WHERE l.checkout_time > ? AND b.deleted = 0
                GROUP BY b.id
                ORDER BY borrow_count DESC
                LIMIT 20
            ''', (since,))
        else:
            cursor.execute('''
                SELECT b.id, b.title, b.author, b.copies_available, COUNT(l.id) as borrow_count
                FROM books b
                JOIN loans l ON b.id = l.book_id
                WHERE b.deleted = 0
                GROUP BY b.id
                ORDER BY borrow_count DESC
                LIMIT 20
            ''')
        
        return [dict(row) for row in cursor.fetchall()]

    def get_overdue_loans(self) -> List[Dict]:
        """Get all overdue loans"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        now = int(datetime.now().timestamp())
        cursor.execute('''
            SELECT l.*, b.title, p.name as patron_name
            FROM loans l
            JOIN books b ON l.book_id = b.id
            JOIN patrons p ON l.patron_id = p.id
            WHERE l.return_time IS NULL AND l.due_time < ?
            ORDER BY l.due_time
        ''', (now,))
        return [dict(row) for row in cursor.fetchall()]

    def get_circulation_history(self, start_timestamp: int, end_timestamp: int) -> List[Dict]:
        """Get circulation history for a date range"""
        # For now, return active loans as circulation history
        # In a full implementation, you'd have a separate history table
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.checkout_time as timestamp, 'checkout' as action, 
                b.title as book_title, p.name as patron_name, l.due_time
            FROM loans l
            JOIN books b ON l.book_id = b.id
            JOIN patrons p ON l.patron_id = p.id
            WHERE l.checkout_time BETWEEN ? AND ?
            UNION
            SELECT l.return_time as timestamp, 'return' as action,
                b.title as book_title, p.name as patron_name, NULL as due_time
            FROM loans l
            JOIN books b ON l.book_id = b.id
            JOIN patrons p ON l.patron_id = p.id
            WHERE l.return_time BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (start_timestamp, end_timestamp, start_timestamp, end_timestamp))
        return [dict(row) for row in cursor.fetchall()]

    def get_circulation_stats(self, since_timestamp: int) -> Dict:
        """Get circulation stats for a period"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as total
            FROM loans
            WHERE checkout_time > ?
        ''', (since_timestamp,))
        row = cursor.fetchone()
        return dict(row) if row else {'total': 0}

    # Add to database/crud.py

    def delete_book_permanently(self, book_id: str) -> bool:
        """Permanently delete a book from database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            # First check if book has any active loans
            cursor.execute("SELECT COUNT(*) FROM loans WHERE book_id = ? AND return_time IS NULL", (book_id,))
            if cursor.fetchone()[0] > 0:
                return False  # Cannot delete book with active loans
            
            # Delete the book
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"Error deleting book: {e}")
            return False

    def delete_patron_permanently(self, patron_id: str) -> bool:
        """Permanently delete a patron from database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            # Check if patron has any active loans
            cursor.execute("SELECT COUNT(*) FROM loans WHERE patron_id = ? AND return_time IS NULL", (patron_id,))
            if cursor.fetchone()[0] > 0:
                return False  # Cannot delete patron with active loans
            
            # Delete the patron
            cursor.execute("DELETE FROM patrons WHERE id = ?", (patron_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"Error deleting patron: {e}")
            return False

    def soft_delete_book(self, book_id: str) -> bool:
        """Soft delete - just mark as deleted"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE books SET deleted = 1, last_modified = ? WHERE id = ?
        ''', (int(datetime.now().timestamp()), book_id))
        conn.commit()
        return cursor.rowcount > 0

    def soft_delete_patron(self, patron_id: str) -> bool:
        """Soft delete - just mark as deleted"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE patrons SET deleted = 1, last_modified = ? WHERE id = ?
        ''', (int(datetime.now().timestamp()), patron_id))
        conn.commit()
        return cursor.rowcount > 0

    def get_active_loans_for_book(self, book_id: str) -> List[Dict]:
        """Get active loans for a specific book"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, p.name as patron_name
            FROM loans l
            JOIN patrons p ON l.patron_id = p.id
            WHERE l.book_id = ? AND l.return_time IS NULL
        ''', (book_id,))
        return [dict(row) for row in cursor.fetchall()]

    # ----- Stats -----
    def get_stats(self) -> Dict:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM books WHERE deleted = 0")
        total_books = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(copies_available) FROM books WHERE deleted = 0")
        available = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(copies_total) - SUM(copies_available) FROM books WHERE deleted = 0")
        checked_out = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM loans WHERE return_time IS NULL")
        active_loans = cursor.fetchone()[0]
        
        return {
            "total_books": total_books,
            "available": available,
            "checked_out": checked_out,
            "active_loans": active_loans
        }