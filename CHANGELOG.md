# Changelog

## [Unreleased]

### Changed

**Scan delay reduced from 2s to 750ms** (`frontend/app.js`)
- `SCAN_DELAY` constant lowered from `2000` to `750` ms
- The status indicator now briefly shows "Processing..." instead of a second-by-second countdown, since the delay is sub-second

**Duplicate scan detection rewritten** (`frontend/app.js`)
- Removed the time-based 30-second per-student cooldown (`COOLDOWN_DURATION`, `cooldownCache`, `addToCooldown`, `checkCooldown`, `clearCooldown`, `cleanupCooldown`)
- Duplicate detection now checks directly against the `scannedStudents` array: if a student ID is already in the session list, an "Already Scanned" warning is shown immediately with no time restriction
- Removed the periodic `setInterval` cleanup that ran every 5 seconds
- `loadScannedStudents` no longer needs to rebuild a cooldown cache on page restore

**Submission results modal** (`frontend/app.js`, `frontend/scanner.html`, `frontend/styles.css`)
- Replaced the native `alert()` dialog with a styled modal overlay
- Modal shows a summary bar: Total / Marked / Not Found / Failed
- Students that were not found or failed to mark are listed individually with their ID and name (resolved from the in-memory scanned list) and a colored badge
- All data comes from the existing batch API response — no additional API calls
- Modal closes on the Done button, the × button, or clicking the backdrop

### Fixed

- Removed an orphan `}` in `frontend/styles.css` (pre-existing syntax error near the `.scanner-container` block)
