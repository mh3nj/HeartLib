# heartlib/database/sync_engine.py
import json
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import sqlite3

class SyncEngine:
    """Handles synchronization between devices"""
    
    def __init__(self, crud, device_id: str = None):
        self.crud = crud
        self.device_id = device_id or str(uuid.uuid4())
        self._init_sync_tables()
    
    def _init_sync_tables(self):
        """Create sync tables if they don't exist"""
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        
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
                is_server INTEGER DEFAULT 0
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
        
        # Register this device
        cursor.execute('''
            INSERT OR REPLACE INTO devices (id, name, last_seen, is_server)
            VALUES (?, ?, ?, ?)
        ''', (self.device_id, f"Device_{self.device_id[:8]}", int(datetime.now().timestamp()), 0))
        conn.commit()
    
    def queue_change(self, table: str, record_id: str, operation: str, 
                     old_data: Dict = None, new_data: Dict = None):
        """Queue a change for sync"""
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_queue (id, device_id, table_name, record_id, operation, 
                                   old_data, new_data, timestamp, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()), self.device_id, table, record_id, operation,
            json.dumps(old_data) if old_data else None,
            json.dumps(new_data) if new_data else None,
            int(datetime.now().timestamp()), 0
        ))
        conn.commit()
    
    def get_unsynced_changes(self) -> List[Dict]:
        """Get all unsynced changes from this device"""
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM sync_queue 
            WHERE synced = 0 AND device_id = ?
            ORDER BY timestamp
        ''', (self.device_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_synced(self, change_ids: List[str]):
        """Mark changes as synced"""
        if not change_ids:
            return
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        cursor.executemany(
            "UPDATE sync_queue SET synced = 1 WHERE id = ?",
            [(cid,) for cid in change_ids]
        )
        conn.commit()
    
    def get_all_changes_for_sync(self) -> List[Dict]:
        """Get all unsynced changes (for server to send to clients)"""
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM sync_queue 
            WHERE synced = 0
            ORDER BY timestamp
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def apply_remote_changes(self, changes: List[Dict]) -> Dict:
        """Apply changes received from another device"""
        results = {"applied": 0, "conflicts": 0, "skipped": 0}
        
        for change in changes:
            # Skip if this device made the change
            if change['device_id'] == self.device_id:
                results['skipped'] += 1
                continue
            
            # Check for conflict
            if self.has_conflict(change):
                self.handle_conflict(change)
                results['conflicts'] += 1
                continue
            
            # Apply the change
            success = self.apply_change(change)
            if success:
                results['applied'] += 1
        
        return results
    
    def has_conflict(self, change: Dict) -> bool:
        """Check if a change conflicts with local data"""
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        
        table = change['table_name']
        record_id = change['record_id']
        timestamp = change['timestamp']
        
        if table == 'books':
            cursor.execute("SELECT last_modified FROM books WHERE id = ? AND deleted = 0", (record_id,))
        elif table == 'patrons':
            cursor.execute("SELECT last_modified FROM patrons WHERE id = ? AND deleted = 0", (record_id,))
        else:
            return False
        
        row = cursor.fetchone()
        if row and row['last_modified'] > timestamp:
            return True
        return False
    
    def handle_conflict(self, change: Dict):
        """Handle a sync conflict - mark for manual resolution"""
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sync_queue 
            SET conflict_resolved = 0 
            WHERE id = ?
        ''', (change['id'],))
        conn.commit()
        print(f"⚠️ Conflict detected for {change['table_name']} record {change['record_id']}")
    
    def apply_change(self, change: Dict) -> bool:
        """Apply a single change to local database"""
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        
        try:
            table = change['table_name']
            record_id = change['record_id']
            operation = change['operation']
            new_data = json.loads(change['new_data']) if change['new_data'] else None
            
            if operation == 'INSERT' or operation == 'UPDATE':
                if table == 'books' and new_data:
                    cursor.execute('''
                        INSERT OR REPLACE INTO books (id, title, author, isbn, copies_total,
                                 copies_available, location, description, last_modified, sync_version, deleted)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (record_id, new_data.get('title'), new_data.get('author'),
                          new_data.get('isbn'), new_data.get('copies_total'),
                          new_data.get('copies_available'), new_data.get('location'),
                          new_data.get('description'), new_data.get('last_modified'),
                          new_data.get('sync_version', 1), new_data.get('deleted', 0)))
                
                elif table == 'patrons' and new_data:
                    cursor.execute('''
                        INSERT OR REPLACE INTO patrons (id, name, email, phone, barcode,
                                 join_date, last_modified, sync_version, deleted)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (record_id, new_data.get('name'), new_data.get('email'),
                          new_data.get('phone'), new_data.get('barcode'),
                          new_data.get('join_date'), new_data.get('last_modified'),
                          new_data.get('sync_version', 1), new_data.get('deleted', 0)))
            
            elif operation == 'DELETE':
                if table == 'books':
                    cursor.execute("DELETE FROM books WHERE id = ?", (record_id,))
                elif table == 'patrons':
                    cursor.execute("DELETE FROM patrons WHERE id = ?", (record_id,))
            
            conn.commit()
            print(f"✅ Applied {operation} on {table}: {record_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error applying change: {e}")
            conn.rollback()
            return False
    
    def get_conflicts(self) -> List[Dict]:
        """Get all unresolved conflicts"""
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM sync_queue 
            WHERE conflict_resolved = 0 AND synced = 0
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def resolve_conflict(self, conflict_id: str, chosen_data: Dict):
        """Resolve a conflict by choosing which data to keep"""
        conn = self.crud.db.get_connection()
        cursor = conn.cursor()
        
        # Apply the chosen data
        cursor.execute("SELECT * FROM sync_queue WHERE id = ?", (conflict_id,))
        conflict = cursor.fetchone()
        
        if conflict:
            # Update the record with chosen data
            self.apply_change({
                'table_name': conflict['table_name'],
                'record_id': conflict['record_id'],
                'operation': 'UPDATE',
                'new_data': json.dumps(chosen_data)
            })
            
            # Mark conflict as resolved
            cursor.execute('''
                UPDATE sync_queue SET conflict_resolved = 1, synced = 1 WHERE id = ?
            ''', (conflict_id,))
            conn.commit()
            return True
        return False