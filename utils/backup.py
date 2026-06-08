# heartlib/utils/backup.py
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from .logger import logger

class BackupManager:
    def __init__(self, db_path, backup_dir):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self):
        """Create a timestamped backup of the database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"heartlib_backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_path, backup_file)
            logger.info(f"Backup created: {backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return None
    
    def restore_backup(self, backup_file):
        """Restore from a backup file"""
        try:
            # Close any existing connections
            shutil.copy2(backup_file, self.db_path)
            logger.info(f"Restored from backup: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return False
    
    def list_backups(self):
        """List all available backups"""
        backups = list(self.backup_dir.glob("heartlib_backup_*.db"))
        backups.sort(reverse=True)
        return [str(b) for b in backups]