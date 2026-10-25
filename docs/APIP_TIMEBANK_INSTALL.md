# APIP TimeBank — Local MVP Installation

1. Download or clone the APIP repository feature branch containing browser-extension/timebank/.
2. Open Chrome or a compatible Chromium browser.
3. Navigate to chrome://extensions.
4. Enable Developer mode.
5. Select Load unpacked.
6. Choose the browser-extension/timebank/ directory.
7. Open the APIP TimeBank extension from the browser toolbar.
8. Enter an activity label, explicitly check consent, and select Start session. Select Stop and save to record the elapsed time locally.
9. Use Export CSV to export local history. Use Delete history to erase saved history and an active session after confirming.

The extension uses local browser storage and requests the storage permission only. The current implementation does not submit data to a server, verify attention, calculate live subscriber payments, or promise earnings. An interrupted session after browser restart is marked with unknown duration and is excluded from rewards.

To remove the extension, use the browser's extension management page. To remove its stored data, use the extension's Delete history control before uninstalling.

## Test status
These instructions describe the intended manual procedure. They are not evidence that a real browser installation has already been performed.
