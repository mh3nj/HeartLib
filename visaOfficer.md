# HeartLib – Technical Portfolio Document

**prepared for:** visa application review
**applicant:** mohsen jafari
**github:** [github.com/mh3nj](https://github.com/mh3nj)
**project repository:** [github.com/mh3nj/heartlib](https://github.com/mh3nj/heartlib)
**document date:** june 8, 2026
**development period:** april 23 – april 30, 2026

<img src="resources/Asset 1.png" alt="HeartLib's Logo" width="25%" >

## what is heartlib

heartlib is a professional library management system. it manages books, patrons, checkouts, returns, due dates, and circulation history. it includes a desktop application for librarians and a progressive web app for patrons. it supports multi device sync over local networks with no cloud dependency.

the project was conceived, designed, and built entirely by mohsen jafari, solo, over the course of eight days, under significant technical constraints due to internet restrictions in iran.

it is not a prototype or a concept. it is a complete, stable, working desktop application used for real library management.

**verified by cloning and running:**

```bash
git clone https://github.com/mh3nj/heartlib.git
cd heartlib
pip install -r requirements.txt
python main.py
```


## the problem it solves

library management software falls into two categories. expensive enterprise systems that cost thousands of dollars per year and require dedicated servers. or free options that are poorly maintained, missing critical features, or store patron data on third party servers.

small libraries cannot afford the enterprise options. public libraries should not trust third party clouds with patron reading histories. most free options lack basic features like barcode scanning, reports, or multi device sync.

heartlib takes a different approach. everything stays local. the database lives on the library's own computer. no cloud. no telemetry. no subscription. the fine system is disabled by default because kindness works better than punishment.

the application was built because no existing solution combined offline first architecture, modern features, professional reports, and completely local operation without subscription fees or patron tracking.


## technical scope

| metric | value |
|--------|-------|
| total lines of code | 9500 plus (python, qss, html, css, javascript) |
| python files | 25 plus |
| pwa files | 3 |
| development period | april 23 – april 30, 2026 |
| total active development hours | 75 hours |
| platform | windows, mac, linux |
| primary language | python 3.10 plus |
| database | sqlite |
| pwa framework | vanilla html, css, javascript |
| sync protocol | custom tcp over local network |
| internet required | no |


## architecture overview

heartlib consists of three main components that work together or independently.

the desktop application is built with pyqt6. it provides the full library management interface. librarians add books, register patrons, check out and return items, generate reports, and configure settings.

the sync engine runs inside the desktop application. one computer acts as the server. other computers on the same local network connect as clients. changes made on any device are queued and synced automatically. conflicts are detected and presented for manual resolution.

the rest api and pwa are optional. when enabled, the desktop application starts a flask server. patrons scan a qr code at the front desk and access the pwa from their phones. they can search the catalog, view their loans, and renew books. no app store required. no special software. just a browser.

all three components share the same database schema and the same encryption methods. data flows from desktop to sync to pwa without ever touching the internet.


## security and privacy

patron data never leaves the library. the database is stored locally. no cloud backup is forced. no telemetry is collected. no analytics are sent anywhere.

sync happens over the local network only. the server does not need to be exposed to the internet. discovery uses mDNS broadcasts that never leave the building.

the pwa connects to the desktop api server over http. in a library setting with trusted users on a private network, this is acceptable. for libraries that require encryption, https can be enabled with a self signed certificate.

passwords for staff mode are stored as plain text in settings by design. this is a deliberate choice because the system assumes physical access to the computer is already controlled. staff pins are meant to prevent accidental actions, not to provide military grade security. for libraries that need stronger authentication, the system can be extended to support full password hashing.


## feature implementation

### desktop application

the main window uses a three column splitter layout. the left column contains patron spotlight and quick actions. the middle column contains search results and circulation feed. the right column contains the details panel. all three columns are resizable. the layout persists across sessions.

patron spotlight shows the currently selected patron. it displays the patron's name, barcode, email, and active loan count. librarians can select a patron by scanning their barcode or searching the database.

quick actions provides five buttons. scan barcode opens the camera scanner. add book opens the new book dialog. switch patron opens the patron search dialog. return book opens the return dialog. sync now triggers manual synchronization.

search results displays books in a table. columns include title, author, isbn, available copies, and location. users can search by title, author, or isbn. advanced filters include match case, whole word, and regex. double clicking a book shows its details in the right panel.

circulation feed shows real time activity. every checkout and return appears as a colored entry. green for checkout, blue for return, red for overdue. librarians can click any entry to see details. the feed can be cleared manually.

details panel is context sensitive. when a book is selected, it shows title, author, isbn, copies, location, status, and description. when a patron is selected, it shows name, email, phone, barcode, join date, and active loans. edit and delete buttons appear when appropriate.

add book dialog collects title, author, isbn, total copies, location, and description. title is required. other fields are optional. after saving, the book appears in search results.

add patron dialog collects name, email, phone, and barcode. name is required. if barcode is left empty, one is generated automatically. after saving, the patron can be selected for checkout.

checkout dialog requires a patron and a book. librarians can search for either. after selecting both, they set a due date. the default is fourteen days from today. confirming the checkout reduces available copies and creates a loan record.

return dialog lists all active loans. librarians can search by book title or patron name. selecting a loan and confirming return increases available copies and closes the loan record.

barcode scanner uses opencv and pyzbar. when the use camera button is clicked, the application requests camera permission. if granted, it starts scanning. detected barcodes are emitted as signals. the main window then searches for a matching book or patron. if no camera is available, librarians can fall back to manual entry.

csv import and export supports books and patrons. export writes all records to a csv file. import reads from a csv file, validates each row, and adds new records. a progress bar shows import status. errors are logged and displayed at the end.

reports dashboard has five tabs. overview shows key statistics in card format. popular books shows most borrowed titles with period selector. overdue items lists all loans past their due date. circulation history shows checkout and return events filtered by date range. grant report generates a formatted report suitable for grant applications or board meetings.

theme manager supports light mode, dark mode, and custom themes. custom themes let librarians pick colors for eleven different ui elements. themes can be saved, exported as .hth files, and imported from other libraries. the selected theme persists across application restarts.

settings dialog configures library information, loan periods, fine policies, backup schedules, and sync options. library information appears in grant reports. loan period defaults to fourteen days. fines are disabled by default. backups can be automatic or manual. sync can be enabled with configurable intervals.

help dialog provides an in app tutorial. it covers getting started, quick actions, managing books, managing patrons, circulation, and advanced features. each section explains the relevant interface elements and workflows.

### sync engine

the sync engine is built on top of the existing crud operations. every insert, update, and delete operation is also written to a sync queue table. each queue entry includes a unique id, device id, table name, record id, operation type, old data, new data, timestamp, and sync status.

when sync is triggered, the client pulls all unsynced changes from the server. it then pushes its own unsynced changes. the server applies incoming changes and marks them as synced.

conflicts occur when the same record was modified on two devices after their last sync. the server detects conflicts by comparing timestamps. when a conflict is detected, both versions are kept and a conflict flag is set. the next time a librarian opens the application on either device, they are presented with a side by side comparison and asked to choose which version to keep.

sync can be automatic or manual. automatic sync runs every thirty minutes by default. the interval is configurable in settings. manual sync is available as a quick action button and a menu item.

the sync protocol uses plain tcp sockets. the server listens on a configurable port. clients discover the server using mDNS broadcasts or by connecting to a known ip address. all communication happens over the local network. no internet connection is required.

### rest api and pwa

the api server is built with flask. it provides endpoints for searching books, getting patron information, listing loans, checking out books, returning books, renewing loans, and fetching library statistics. cors is enabled so the pwa can connect from any device on the network.

the pwa is a single html file with embedded css and javascript. it includes a service worker for offline caching and push notifications. patrons can install it to their home screen. it works on any modern browser, including mobile safari and chrome.

the pwa has two modes. patron mode requires scanning a library card barcode. after login, patrons can search the catalog, view their active loans, and renew books. staff mode requires a pin code. after authentication, staff can check out and return books directly from their phones.

the pwa supports dark and light themes. the theme preference is stored in local storage and persists across sessions. it also supports three languages. english, spanish, and french. language selection happens instantly with no page reload.

push notifications are implemented using the web push api. patrons who grant permission receive notifications when books are due in three days and when books become overdue. the desktop application includes a scheduler that checks for due and overdue loans once per day and sends notifications to all subscribed devices.


## development timeline

### version 2.0 – april 23–30, 2026

| date | hours | work completed |
|------|-------|----------------|
| april 23 | 8 | project architecture, database schema, gui skeleton, five panel layout |
| april 24 | 9 | books and patrons crud, search functionality, status bar stats |
| april 25 | 10 | checkout and return system, circulation feed, barcode scanner |
| april 26 | 10 | csv import export, reports dashboard, theme manager |
| april 27 | 10 | sync engine, server, client, discovery, conflict detection |
| april 28 | 10 | pwa catalog, loans, barcode login, theme and language switcher |
| april 29 | 10 | pwa staff mode, push notifications, settings dialog, help system |
| april 30 | 8 | final polish, bug fixes, documentation, release preparation |

**version 2.0 total: 75 hours across 8 days**


## development context

this project was developed under significant constraints.

iran experienced widespread internet restrictions during this period. access to github, pypi, stack overflow, and most standard development resources was blocked. the majority of the work was completed offline. dependencies were researched and downloaded during brief windows of connectivity. documentation was consulted from locally cached copies. problems were solved from first principles when no reference was available.

this affected not just convenience but fundamental development workflow. version control pushes, dependency management, and documentation access required planning and timing around unpredictable connectivity windows.

the application was built anyway. it works. it is documented. it can be cloned and run by anyone.


## code quality indicators

all database operations use parameterized queries. no sql string concatenation. no risk of injection.

the sync queue prevents duplicate sync operations by tracking timestamps and device ids. each change is applied at most once.

the pwa uses a service worker to cache assets. offline access works after the first load.

the desktop application uses logging for debugging. sensitive information is never written to logs.

error handling is explicit. no bare except clauses. every exception is caught, logged, and presented to the user when appropriate.

the database schema uses foreign keys with cascade rules where appropriate. referential integrity is enforced at the database level.

the sync engine uses optimistic concurrency control. conflicts are detected and presented for manual resolution. data is never silently overwritten.


## third party dependencies

| library | version | purpose |
|---------|---------|---------|
| pyqt6 | 6.5.0 plus | desktop interface |
| opencv python | 4.8.0 plus | camera access for barcode scanning |
| pyzbar | 0.1.9 plus | barcode decoding |
| requests | 2.31.0 plus | isbn lookup (optional) |
| flask | 2.3.0 plus | rest api for pwa |
| flask cors | 4.0.0 plus | cross origin requests |
| cryptography | 41.0.0 plus | encryption (future) |
| pillow | 10.0.0 plus | image processing |


## verification instructions

the authenticity and functionality of this project can be verified directly.

clone the repository: `git clone https://github.com/mh3nj/heartlib.git`

install dependencies: `pip install -r requirements.txt`

run the application: `python main.py`

add a book. add a patron. check out the book to the patron. return the book. generate a report. change the theme. export books to csv. import them back.

the full application launches and operates exactly as documented. no binaries. no compiled executables. every line of code is readable in the repository.


## known limitations

barcode scanning requires a camera. on computers without a camera, manual entry is available.

sync requires all devices to be on the same local network. the server computer must be running for clients to sync.

the pwa api server uses http by default. for libraries that require encryption, https can be enabled with a self signed certificate.

isbn lookup requires an internet connection. the openlibrary api is rate limited but sufficient for small libraries.

the fine system is disabled by default. enabling it requires changing a setting and configuring the daily fine amount.


## about the author

mohsen jafari is a full time developer based in iran, with professional experience in frontend development, backend systems, and desktop applications. he has been programming in python for several years and has contributed to multiple open source projects.

heartlib was built to solve a real need. library software that does not cost money, does not track patrons, and treats librarians with respect.

github: [github.com/mh3nj](https://github.com/mh3nj)
xing: [xing.com/profile/Mohsen_Jafari093223](https://www.xing.com/profile/Mohsen_Jafari093223/)
logo design: [parsegan.com](https://parsegan.com)
portfolio: [dahgan.com](https://dahgan.com)


## declaration

i, mohsen jafari, confirm that the information in this document is accurate. heartlib was built by me, solo, over the period of april 23 to april 30, 2026. the source code is available at the github repository listed above. the application works as described.


this project was built during internet restrictions in iran. no stack overflow. no documentation access. no reliable connectivity. just whatever was cached, whatever could be reasoned through, and the determination to ship something real.

seventy five hours. ninety five hundred lines of code. twenty five python files. three pwa files. one library system. one developer.

proof that creativity and persistence do not require a stable connection.

heartlib because libraries have hearts, not just barcodes.

mh3nj