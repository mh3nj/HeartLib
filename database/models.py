# heartlib/database/models.py
from dataclasses import dataclass, field
from typing import Optional
import uuid
from datetime import datetime

@dataclass
class Book:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    author: str = ""
    isbn: str = ""
    copies_total: int = 1
    copies_available: int = 1
    location: str = ""
    description: str = ""
    last_modified: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    sync_version: int = 1
    deleted: bool = False
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "copies_total": self.copies_total,
            "copies_available": self.copies_available,
            "location": self.location,
            "description": self.description,
            "last_modified": self.last_modified,
            "sync_version": self.sync_version,
            "deleted": 1 if self.deleted else 0
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            author=data.get("author", ""),
            isbn=data.get("isbn", ""),
            copies_total=data.get("copies_total", 1),
            copies_available=data.get("copies_available", 1),
            location=data.get("location", ""),
            description=data.get("description", ""),
            last_modified=data.get("last_modified", int(datetime.now().timestamp())),
            sync_version=data.get("sync_version", 1),
            deleted=bool(data.get("deleted", 0))
        )


@dataclass
class Patron:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    phone: str = ""
    barcode: str = ""
    join_date: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    last_modified: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    sync_version: int = 1
    deleted: bool = False


@dataclass
class Loan:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    book_id: str = ""
    patron_id: str = ""
    checkout_time: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    due_time: int = 0
    return_time: Optional[int] = None
    last_modified: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    sync_version: int = 1