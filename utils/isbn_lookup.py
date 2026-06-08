# heartlib/utils/isbn_lookup.py
"""Look up book metadata by ISBN from online APIs"""

import requests
from typing import Optional, Dict

class ISBNLookup:
    """Fetch book information from OpenLibrary API"""
    
    def __init__(self):
        self.base_url = "https://openlibrary.org/api/books"
    
    def fetch(self, isbn: str) -> Optional[Dict]:
        try:
            resp = requests.get(
                self.base_url,
                params={
                    "bibkeys": f"ISBN:{isbn}",
                    "format": "json",
                    "jscmd": "data"
                },
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                key = f"ISBN:{isbn}"
                if key in data:
                    book = data[key]
                    authors = [a.get('name', '') for a in book.get('authors', [])]
                    return {
                        'title': book.get('title', ''),
                        'author': ', '.join(authors),
                        'isbn': isbn,
                        'description': book.get('notes', ''),
                        'cover': book.get('cover', {}).get('large', '')
                    }
        except Exception as e:
            print(f"ISBN lookup error: {e}")
        return None

    def lookup(self, isbn: str) -> Optional[Dict]:
        """Fetch book metadata for given ISBN"""
        try:
            response = requests.get(
                self.base_url,
                params={
                    "bibkeys": f"ISBN:{isbn}",
                    "format": "json",
                    "jscmd": "data"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                key = f"ISBN:{isbn}"
                if key in data:
                    book_data = data[key]
                    return {
                        "title": book_data.get("title", ""),
                        "author": ", ".join([a.get("name", "") for a in book_data.get("authors", [])]),
                        "isbn": isbn,
                        "description": book_data.get("notes", ""),
                        "cover": book_data.get("cover", {}).get("large", "")
                    }
        except Exception as e:
            print(f"ISBN lookup failed: {e}")
        
        return None