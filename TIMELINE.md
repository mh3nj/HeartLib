# HeartLib – Development Timeline

**Project Start:** April 23, 2026  
**Completion Date:** April 30, 2026  
**Version:** 1.0.0

---

## Development Journey

### Day 1 – April 23, 2026 (Foundation)

#### Morning Session (3 hours)
- Project architecture planning (desktop + PWA + sync)
- Technology stack selection (PyQt6, SQLite, OpenCV, Flask)
- Repository setup and virtual environment configuration
- Database schema design (books, patrons, loans, sync tables)
- Core data models (Book, Patron, Loan dataclasses)

#### Afternoon Session (3 hours)
- Database manager with encryption support
- CRUD operations for books and patrons
- Basic search functionality
- GUI skeleton – 5‑panel layout with QSplitter

#### Evening Session (2 hours)
- Menu bar (Library, Patrons, Circulation, Reports, Tools, Help)
- Status bar with live stats placeholder
- Quick Actions buttons (Scan, Add Book, Switch Patron, Sync, Return)

**Day 1 Total:** ~8 hours | **Modules completed:** database (3 files), gui skeleton

---

### Day 2 – April 24, 2026 (GUI & Core Features)

#### Morning Session (4 hours)
- Patron Spotlight widget (display current patron)
- Search Results widget (table view, dummy data)
- Circulation Feed widget (activity log with color codes)
- Details Panel widget (contextual book/patron info)
- All 5 panels connected with signals

#### Afternoon Session (3 hours)
- Add Book dialog (title, author, ISBN, copies, location)
- Add Patron dialog (name, email, phone, auto-generated barcode)
- Patron Search dialog (search by name/email/barcode)
- Database integration – load sample books on first run

#### Evening Session (2 hours)
- Real data binding from database to GUI
- Status bar stats (total books, available, checked out, active loans)
- Soft delete books/patrons (with active loan checks)
- Circulation feed test activities

**Day 2 Total:** ~9 hours | **GUI modules:** 7 completed | **Database:** fully integrated

---

### Day 3 – April 25, 2026 (Circulation & Barcode)

#### Morning Session (4 hours)
- Checkout dialog (select patron, search/scan book, set due date)
- Return dialog (search active loans, select to return)
- Checkout/return CRUD methods (update book copies, create/close loans)
- Real-time circulation feed updates

#### Afternoon Session (4 hours)
- Barcode scanner (OpenCV + PyZBar integration)
- Camera fallback – manual entry mode
- Toggle between camera and manual input
- Scanner dialog with mode selection
- Barcode → book/patron search integration

#### Evening Session (2 hours)
- Active loan tracking per patron
- Due date calculations (default 14 days)
- Overdue detection (red color in circulation feed)
- Sync timer placeholder (30 min default)

**Day 3 Total:** ~10 hours | **Core features:** Checkout/Return + Barcode scanning

---

### Day 4 – April 26, 2026 (Reports & Themes)

#### Morning Session (4 hours)
- CSV Import/Export dialog (books + patrons)
- Bulk import with progress bar and error logging
- Export to CSV with all fields
- Reports Dashboard – Overview tab (stats cards)

#### Afternoon Session (4 hours)
- Reports Dashboard – Popular Books tab (period selector)
- Reports Dashboard – Overdue Items tab (list + export)
- Reports Dashboard – Circulation History tab (date range filter)
- Reports Dashboard – Grant Report tab (professional output)

#### Evening Session (2 hours)
- Theme Manager (light/dark/custom)
- Theme Dialog (color picker for 11 UI slots)
- Export/import themes as `.hth` files (JSON)
- Theme persistence via QSettings + config.json

**Day 4 Total:** ~10 hours | **Reports:** 5 tabs | **Themes:** fully customizable

---

### Day 5 – April 27, 2026 (Sync Engine)

#### Morning Session (4 hours)
- Sync database tables (sync_queue, devices, sync_metadata)
- Sync Engine core (queue_change, get_unsynced_changes)
- Change tracking with timestamps and version numbers
- Conflict detection logic

#### Afternoon Session (4 hours)
- Sync Server (TCP socket, multi‑threaded)
- Sync Client (push/pull protocol)
- Network Discovery (mDNS broadcast)
- Sync full cycle testing on localhost

#### Evening Session (2 hours)
- Sync status indicator in status bar
- Manual sync button integration
- Auto‑sync timer (configurable interval)
- Conflict resolution placeholder

**Day 5 Total:** ~10 hours | **Sync Engine:** server + client working | **v2.0 complete**

---

### Day 6 – April 28, 2026 (PWA – Part 1)

#### Morning Session (4 hours)
- Flask API server (endpoints for books, patrons, loans)
- CORS enabled for mobile access
- PWA folder structure (index.html, manifest.json, sw.js)
- Basic PWA layout – catalog view, search bar

#### Afternoon Session (4 hours)
- PWA patron login via barcode scanning (html5-qrcode)
- PWA loans view (active loans list)
- PWA renew functionality via API
- Dark/light theme toggle with localStorage persistence

#### Evening Session (2 hours)
- Language switcher (EN/ES/FR – dynamic without page reload)
- Service Worker (offline caching)
- Install to home screen capability
- API integration testing (search, checkout, renew)

**Day 6 Total:** ~10 hours | **PWA:** core patron features complete

---

### Day 7 – April 29, 2026 (PWA – Part 2 & Polish)

#### Morning Session (4 hours)
- PWA staff mode (PIN‑protected checkout/return)
- Checkout flow: scan patron → scan book → confirm
- Return flow: search active loans → confirm return
- Staff panel with 6 action cards

#### Afternoon Session (4 hours)
- Push notifications – Web Push API integration
- Subscription storage on server
- Daily scheduler for due date notifications (3 days before)
- Overdue notifications
- Camera permission handling (explicit getUserMedia check)

#### Evening Session (2 hours)
- Settings dialog (library info, loan periods, fines, backup, sync)
- In‑app Help system (6 tutorial tabs)
- Backup manager (auto + manual)
- Logger system (file + console)

**Day 7 Total:** ~10 hours | **PWA:** staff mode + push notifications | **Desktop:** settings + backup + help

---

### Day 8 – April 30, 2026 (Final Polish & Release)

#### Morning Session (4 hours)
- Dark/light theme propagation to ALL desktop widgets
- Fix theme switching on settings dialog and help dialog
- Fix sync status label initialization
- Fix barcode scanner camera permission flow
- All known bugs squashed

#### Afternoon Session (2 hours)
- Cross‑platform testing (Windows)
- PyInstaller packaging preparation
- README.md documentation
- TIMELINE.md documentation
- PROJECT_SUMMARY.md documentation

#### Evening Session (2 hours)
- Logo integration (desktop + PWA)
- GitHub repository structure finalization
- Release notes prepared
- v1.0 tag and release (when internet returns)

**Day 8 Total:** ~8 hours | **Status:** COMPLETE

---

## Feature Count Summary

| Category | Features |
|----------|----------|
| **Desktop Core** |
| Books Management | Add, Edit, Delete, Search (regex/case/whole word) |
| Patrons Management | Add, Edit, Delete, Search, Auto‑barcode |
| Circulation | Checkout, Return, Renew, Due dates, Activity feed |
| Barcode Scanner | Camera + manual fallback (OpenCV + PyZBar) |
| CSV Tools | Import/Export books & patrons (progress bar) |
| Reports Dashboard | Overview, Popular, Overdue, History, Grant |
| Theme Switcher | Light, Dark, Custom (.hth import/export) |
| Settings | Library info, Loans, Fines, Backup, Sync |
| Backup | Auto/manual backup, One‑click restore |
| Help | 6‑tab in‑app tutorial |
| Sync Engine (v2.0) | Server/client, Conflict detection, Auto/manual |
| **PWA (Patron + Staff)** |
| Catalog | Search, Borrow, View details |
| Loans | View active loans, Renew |
| Staff Mode | Checkout, Return (PIN‑protected) |
| Barcode Login | Scan library card via device camera |
| Themes | Dark/Light toggle (persistent) |
| Languages | EN/ES/FR (dynamic, no reload) |
| Notifications | Due date reminders, Overdue alerts |
| Offline | Service Worker caching |
| **REST API** | 9 endpoints (books, patrons, loans, checkout, return, renew, stats) |

---

## Total Development Time

| Metric | Value |
|--------|-------|
| **Total days** | 8 days (April 23 – April 30, 2026) |
| **Total hours** | ~75 hours |
| **Average per day** | ~9.4 hours |
| **Lines of code (Python)** | ~8,000+ |
| **Lines of code (PWA)** | ~1,500 (HTML/CSS/JS) |
| **Desktop modules** | 25+ Python files |
| **PWA files** | 3 (index.html, manifest.json, sw.js) |
| **Database tables** | 5 (books, patrons, loans, sync_queue, devices, sync_metadata) |
| **API endpoints** | 9 |
| **Languages supported (PWA)** | 3 (EN, ES, FR) |
| **Themes** | Unlimited (custom + import/export) |

---

## Daily Breakdown Chart

```
Day 1 (Apr 23):    ████████████████  8 hrs   (Foundation)
Day 2 (Apr 24):    ██████████████████ 9 hrs   (GUI + Core Features)
Day 3 (Apr 25):    ████████████████████ 10 hrs (Circulation + Barcode)
Day 4 (Apr 26):    ████████████████████ 10 hrs (Reports + Themes)
Day 5 (Apr 27):    ████████████████████ 10 hrs (Sync Engine)
Day 6 (Apr 28):    ████████████████████ 10 hrs (PWA Part 1)
Day 7 (Apr 29):    ████████████████████ 10 hrs (PWA Part 2 + Polish)
Day 8 (Apr 30):    ████████████████  8 hrs   (Final Polish + Release)
                   ─────────────────────────────
Total:             75 hours of focused development
```

---

## Key Achievements

- Built **8,000+ lines** of production‑ready Python code
- Built **1,500+ lines** of PWA (HTML/CSS/JS) with offline support
- Integrated **full sync engine** (server + client) for multi‑device libraries
- Created **complete PWA** with patron portal + staff mode + push notifications
- Designed **5‑panel responsive GUI** with draggable splitters
- Implemented **advanced search** with regex, case‑sensitivity, whole word
- Added **real‑time circulation feed** with color‑coded activity
- Built **professional reports dashboard** with grant‑ready output
- Created **custom theme system** with 11 color slots + import/export
- Implemented **barcode scanning** (camera + manual fallback)
- Added **CSV import/export** with progress bar and error logging
- Built **REST API** (9 endpoints) for PWA and future mobile apps
- Achieved **100% dark/light theme compatibility** across all widgets
- Added **multi‑language PWA** (EN/ES/FR) without page reload
- Implemented **push notifications** for due date reminders

---

## Lessons Learned

| Challenge | Solution |
|-----------|----------|
| SQLite threading in sync server | Create new DB connection per thread |
| QDate to timestamp conversion | Helper method `qdate_to_timestamp` |
| Camera permission blocking | Explicit getUserMedia check before scanner starts |
| PWA barcode scanning without HTTPS | Use `html5-qrcode` with permission handling |
| Sync conflict detection | Timestamp + version number comparison |
| Theme not persisting across restarts | Save to config.json + QSettings |
| Patron selection signal emitting None | Change signal type to `object` to allow None |
| Circulation feed not updating in real time | Emit signal after every DB operation |

---

## Future Enhancements (v1.1 / v2.1)

- ISBN auto‑lookup via OpenLibrary API
- Batch camera scanning for inventory
- Email notifications (SMTP)
- Native Flutter mobile app (iOS/Android)
- Cloud backup (optional)
- More languages (German, Chinese, Arabic)
- Patron holds/reservations
- Reading recommendations engine

---

## Author

**Mohsen Jafari** - Creator, Developer, Designer

- GitHub: [mh3nj](https://github.com/mh3nj)
- LinkedIn: [mh3nj](https://linkedin.com/in/mh3nj)
- Websites: [Parsegan.com](https://parsegan.com) (logo design), [Dahgan.com](https://dahgan.com) (land surveying/portfolio)

---

*This project was created during internet restrictions in Iran – proof that creativity and persistence know no boundaries.*
