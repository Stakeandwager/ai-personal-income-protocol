# APIP Windows desktop starter

This is the first desktop shell increment. It provides a local opportunity queue, SQLite persistence, status tracking, and CSV export.

**Not yet included:** live web crawling, automatic opportunity scoring, AI integration, outbound messaging, payment integration, or verified income collection. Do not interpret manually entered ideas as discovered or validated opportunities.

## Run from source (Windows)

Requires Python 3.11 or later with Tkinter available.

From the repository root:
```bat
py desktop\apip_desktop.py
```

The local database is stored in `%LOCALAPPDATA%\APIP\apip.sqlite3`, so it is separate from the application executable and source checkout.

## Build the executable

Double-click `desktop\build_windows.bat` on a Windows machine with Python and internet access. It installs PyInstaller and builds `dist\APIP.exe`. The build script exits with an error if a step fails.

The build has **not been verified on Windows yet**. Only call this a release after the executable is built, opened successfully, and tested for persistence and CSV export. Rebuild on Windows; do not copy an executable built for another operating system.

## Safe iteration

- Keep the source code and database separate.
- Export important records periodically.
- Do not put credentials or private customer data in opportunity notes.
- Discovery adapters must use permitted public sources, honor rate limits and terms, and preserve source URLs and timestamps.
- External messages, paid services, purchases, contracts, and money movement require the appropriate owner authorization.
