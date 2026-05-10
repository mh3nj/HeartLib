# HeartLib – Library Management System with a Heart

**Status:** Stable Release v1.0  
**Build Date:** April 30, 2026

A complete, premium-quality library management system for librarians and patrons – with desktop app, PWA, multi-device sync, and zero fines. Because libraries have hearts, not just barcodes.

---

## About HeartLib

HeartLib (pronounced "hart-lib") is a free, privacy-first library management system built with kindness as its core value. Named after the belief that every library beats with a heart – serving communities, preserving knowledge, and treating patrons with empathy, not penalties.

### What HeartLib Helps You Do

- **Manage books** – Add, edit, delete, search with advanced filters (regex, case-sensitive, whole word)
- **Manage patrons** – Register members, issue library cards, track borrowing history
- **Checkout & return** – With due dates, real-time activity feed, and zero aggressive fines
- **Scan barcodes** – Camera-based scanning with manual fallback (no special hardware needed)
- **Sync across devices** – Connect multiple computers/tablets on the same local network (v2.0)
- **Generate reports** – Overview stats, popular books, overdue lists, grant-ready reports
- **Import/export CSV** – Migrate from legacy systems or backup your data
- **Serve patrons via PWA** – Let patrons search catalog, view loans, and renew books from their phones
- **Customize everything** – Dark/light themes, custom color schemes, export/import `.hth` theme files

**Desktop app + PWA (mobile) + Sync engine** | **100% offline-first** | **Zero telemetry** | **No cloud required**

---

## The Core Modules

| Module | Description |
|--------|-------------|
| 📚 **Books** | Complete book catalog with title, author, ISBN, copies, location, description. Advanced search with regex, case-sensitivity, whole word matching. |
| 👥 **Patrons** | Patron registry with name, email, phone, auto-generated barcode. Active loans tracking. |
| 🔄 **Circulation** | Checkout with due dates, return processing, real-time activity feed (color-coded: green=checkout, blue=return, red=overdue). |
| 🔍 **Scan Barcode** | Camera-based scanning using OpenCV + PyZBar. Manual entry fallback when camera unavailable. |
| 📊 **Reports** | Overview dashboard (total books, available, checked out, active loans). Popular books (last 30/90 days/year/all time). Overdue items list. Circulation history by date range. Grant-ready professional reports. |
| 📁 **CSV Tools** | Export books/patrons to CSV. Import from CSV for migration. Batch operations. |
| 🎨 **Theme Switcher** | Light mode, Dark mode, Custom themes. Pick any color for every UI element. Export/import themes as `.hth` files. |
| ⚙️ **Settings** | Library information (name, address, phone, email). Loan periods (default 14 days). Max loans per patron. Fine system (optional, disabled by default – kindness mode!). Sync server settings. Backup configuration. |
| 🔄 **Sync Engine (v2.0)** | Multi-device sync over local network. One server, many clients. Conflict detection with manual resolution. Works offline, syncs when connected. |
| 💾 **Backup** | Automatic scheduled backups. Manual one-click backups. Restore from any backup file. |
| 📖 **Help & Tutorial** | In-app help system with step-by-step tutorials for every feature. |
| 📱 **PWA (Patron Portal)** | Installable on any smartphone. Search catalog, view active loans, renew books. Dark/light theme. Multi-language (EN/ES/FR). Barcode scanning for library card login. Push notifications for due dates. Staff mode for checkout/return. |

---

## Getting Started

### Option 1: From Source (Python required)

```bash
git clone https://github.com/parsegan/HeartLib.git
cd HeartLib
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py
```

### Option 2: Standalone Executable

Download from GitHub Releases. No Python installation required. Just unzip and run `HeartLib.exe` (Windows) or `HeartLib.app` (macOS) or `HeartLib.AppImage` (Linux).

### Option 3: PWA for Patrons (after starting API server)

1. In HeartLib desktop, go to **Settings → Sync → Start API Server**
2. Patrons scan the QR code displayed at your checkout desk
3. Or open `http://[your-library-pc-ip]:8766` on any phone/tablet
4. Patrons scan their library card barcode to log in
5. They can search books, view loans, and renew online

---

## Keyboard Shortcuts (Desktop)

| Shortcut | Action |
|----------|--------|
| `Ctrl+1` | Patron Spotlight focus |
| `Ctrl+2` | Search Results focus |
| `Ctrl+3` | Circulation Feed focus |
| `Ctrl+4` | Details Panel focus |
| `Ctrl+N` | Add new book |
| `Ctrl+P` | Add new patron |
| `Ctrl+Shift+C` | Checkout |
| `Ctrl+Shift+R` | Return |
| `Ctrl+S` | Sync now |
| `Ctrl+Shift+S` | Scan barcode |
| `Ctrl+Comma` | Open Settings |
| `Ctrl+H` | Open Help |
| `Ctrl+T` | Theme switcher |
| `F5` | Refresh data |

---

## Features In Detail

### Books Management
- Add books with title, author, ISBN, total copies, location, description
- Edit existing books (update any field)
- Soft delete (books with active loans cannot be deleted)
- Search by title, author, or ISBN
- Advanced filters: match case, whole word, regex
- View available/total copies count
- Double-click any book to see full details in right panel

### Patrons Management
- Register patrons with name, email, phone, optional custom barcode
- Auto-generate barcode if left empty
- Edit patron information
- Soft delete (patrons with active loans cannot be deleted)
- Search by name, email, or barcode
- View active loans count in real-time

### Checkout & Return
- Checkout: Select patron → Search/scan book → Set due date (default 14 days) → Confirm
- Return: Search active loans by book title or patron → Select loan → Confirm return
- Circulation feed shows every transaction with color-coding
- Due date tracking with overdue detection
- Renew loans (extend by 14 days)

### Barcode Scanning
- Uses your computer's camera (OpenCV + PyZBar)
- Scan book ISBNs or patron barcodes
- Manual entry fallback when camera unavailable
- Auto-fills search when scanning
- For patrons: scan library card to log into PWA

### Reports Dashboard
- **Overview:** Total books, available, checked out, active loans, total patrons, today's activity
- **Popular Books:** Most borrowed titles (filter by 30/90 days, 1 year, all time). Export to CSV.
- **Overdue Items:** List all overdue loans with patron name, book title, due date, days overdue. Export to CSV.
- **Circulation History:** Filter by date range, view all checkouts/returns. Export to CSV.
- **Grant Report:** Generate professional PDF-ready reports with library name, period, stats, popular books, impact summary. Save as text file.

### CSV Import/Export
- **Export:** Books or patrons to CSV with all fields
- **Import:** Batch import books or patrons from CSV
- Handles duplicate IDs (generates new ones)
- Progress bar and error logging during import
- Perfect for migrating from legacy systems

### Theme System
- **Light theme:** Clean white background, dark text
- **Dark theme:** Eye-friendly for evening cataloging
- **Custom themes:** Pick any color for every UI element (11 color slots)
- Save unlimited custom themes
- Export themes as `.hth` files (JSON format)
- Import themes shared by other libraries
- Theme persists across app restarts

### Sync Engine (v2.0)
- **One server, many clients** over local WiFi/ethernet
- **Offline-first:** Each device works offline, syncs when connected
- **Conflict detection:** Server detects when same record was edited on two devices
- **Manual resolution:** Side-by-side diff view, choose which version to keep
- **Auto-sync:** Configurable interval (1 min – 1 hour, default 30 min)
- **Manual sync:** One-click sync button for immediate updates
- **No internet required:** All sync happens on your local network
- **Encryption optional:** AES-256 for patron data

### Backup System
- **Automatic backups:** Schedule daily/weekly backups
- **Manual backups:** One-click backup of entire database
- **Restore:** Any backup file with one click
- Backups stored in user-specified location
- Timestamped filenames for easy identification

### Settings
- **Library Information:** Name, address, phone, email (appears in grant reports)
- **Loan Settings:** Default loan period (days), max loans per patron
- **Fine Settings:** Enable/disable fines (kindness mode is default!), fine per day (cents)
- **Sync Settings:** Enable auto-sync, sync interval, server host/port, start/stop server
- **Backup Settings:** Enable auto-backup, backup interval (days), backup location
- **Theme:** Default theme selection

### In-App Help & Tutorial
- **Getting Started:** Welcome guide and feature overview
- **Quick Actions:** Explanation of all 5 quick action buttons
- **Managing Books:** How to add, search, edit, delete books
- **Managing Patrons:** How to add, find, edit, delete patrons
- **Circulation:** Checkout, return, renewal workflows
- **Advanced Features:** Reports, CSV tools, themes, sync

### PWA (Patron Portal)
- **Installable:** Add to home screen, works offline (service worker)
- **Dark/Light theme:** Toggle, persists in localStorage
- **Multi-language:** English, Spanish, French (add more easily)
- **Barcode login:** Scan library card using device camera
- **Search catalog:** By title, author, ISBN
- **View loans:** Active loans with due dates, renew directly
- **Staff mode:** PIN-protected checkout/return (for library staff on mobile)
- **Push notifications:** Due date reminders, overdue alerts
- **Fully responsive:** Works on any phone size

### REST API (for custom integrations)
- `GET /api/books` – List all books
- `GET /api/search?q=query` – Search books
- `GET /api/books/{id}` – Get single book
- `GET /api/patrons/{barcode}` – Get patron by barcode
- `GET /api/patron/{id}/loans` – Get patron's active loans
- `POST /api/checkout` – Checkout a book
- `POST /api/return` – Return a book
- `POST /api/renew` – Renew a loan
- `GET /api/stats` – Library statistics
- CORS-enabled – can be used by any frontend (Flutter, React Native, etc.)

---

## Project Structure

```
HeartLib/
├── main.py                      # Entry point
├── config.py                    # Settings manager (JSON)
├── settings.json                # User preferences
├── heartlib.db                  # SQLite database
│
├── gui/                         # Desktop GUI modules (14 files)
│   ├── quick_actions.py
│   ├── search_results.py
│   ├── patron_spotlight.py
│   ├── circulation_feed.py
│   ├── details_panel.py
│   ├── add_book_dialog.py
│   ├── add_patron_dialog.py
│   ├── patron_search_dialog.py
│   ├── checkout_dialog.py
│   ├── return_dialog.py
│   ├── barcode_scanner.py
│   ├── csv_import_export.py
│   ├── reports_dashboard.py
│   ├── theme_manager.py
│   ├── theme_dialog.py
│   ├── settings_dialog.py
│   └── help_dialog.py
│
├── database/                    # Database & sync
│   ├── db_manager.py            # Connection, schema, encryption
│   ├── models.py                # Book, Patron, Loan dataclasses
│   ├── crud.py                  # All database operations
│   └── sync_engine.py           # Sync queue, conflict detection
│
├── networking/                  # Sync & API (v2.0)
│   ├── sync_server.py           # TCP sync server
│   ├── sync_client.py           # TCP sync client
│   ├── discovery.py             # mDNS network discovery
│   └── api_server.py            # Flask REST API for PWA
│
├── utils/                       # Utility modules
│   ├── logger.py                # File + console logging
│   ├── backup.py                # Backup/restore manager
│   ├── isbn_lookup.py           # OpenLibrary API (stub)
│   ├── camera_batch.py          # Batch scanning (stub)
│   └── emailer.py               # SMTP notifications (stub)
│
├── pwa/                         # Progressive Web App
│   ├── index.html               # Complete PWA (catalog, loans, staff)
│   ├── manifest.json            # PWA manifest (installable)
│   └── sw.js                    # Service Worker (offline + push)
│
├── resources/                   # Assets
│   ├── icons/                   # App icons
│   ├── themes/                  # Custom theme storage
│   └── translations/            # i18n JSON files (future)
│
└── tests/                       # Unit & integration tests (planned)
```

---

## Requirements

### Desktop App
- Python 3.10+
- PyQt6 (GUI framework)
- OpenCV + PyZBar (barcode scanning)
- requests (ISBN lookup – optional)
- cryptography (encryption – optional)

### PWA (no installation required)
- Any modern browser (Chrome, Firefox, Safari, Edge)
- Camera access for barcode scanning (optional)

---

## Development Timeline

| Phase | Date (2026) | Key Achievements |
|-------|-------------|------------------|
| Day 1 | April 23 | Project planning, database schema, GUI skeleton (5 panels) |
| Day 2 | April 24 | Books CRUD, Patrons CRUD, basic search |
| Day 3 | April 25 | Checkout/return system, circulation feed, details panel, barcode scanner |
| Day 4 | April 26 | CSV import/export, reports dashboard, theme manager (light/dark) |
| Day 5 | April 27 | Sync engine (server + client), backup manager, settings dialog |
| Day 6 | April 28 | PWA development – catalog, loans, barcode scan, theme & language |
| Day 7 | April 29 | PWA staff mode, push notifications, camera permission handling |
| Day 8 | April 30 | Final polishing, documentation, packaging, release v1.0 |

**Total:** ~48 hours | **Lines of code:** 8,000+ (desktop) + 1,500 (PWA) | **Modules:** 25+ Python files, 3 PWA files

---

## Author

**Mohsen Jafari** - Creator, Developer, Designer

- GitHub: [mh3nj](https://github.com/mh3nj)
- LinkedIn: [mh3nj](https://linkedin.com/in/mh3nj)
- Websites: [Parsegan.com](https://parsegan.com) (logo design), [Dahgan.com](https://dahgan.com) (land surveying/portfolio)

---

## License

**MIT License** – Free for personal and commercial use with attribution.  
Because libraries should have hearts, not price tags.

---

## Acknowledgments

- PyQt6 team (Qt for Python)
- OpenCV + PyZBar (barcode scanning)
- Flask (REST API)
- html5-qrcode library (PWA scanning)
- The open-source community
- Every librarian who inspired the "kindness mode" (no aggressive fines)

---

## Future Enhancements (v1.1 / v2.1)

- ISBN auto-lookup via OpenLibrary API
- Batch camera scanning for inventory
- Email notifications (SMTP)
- Native Flutter mobile app (iOS/Android)
- Cloud backup (optional)
- More languages (German, Chinese, Arabic)

---

*This project was created during internet restrictions in Iran – proof that creativity and persistence know no boundaries.*

**HeartLib – Because libraries have hearts, not just barcodes. ❤️📚**

---
