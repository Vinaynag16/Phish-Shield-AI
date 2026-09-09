# Scanner UI Bug — Diagnosis (Sep 9, 2026)

## Problem
After submitting a scan on the scanner page, the result/details don't display in the UI.

## Root Cause
`log_scan()` call in `predict_url` (`backend/main.py:275`) is unprotected by any try/except.
If the SQLite write fails, it crashes the endpoint with HTTP 500 before the response is returned.
The frontend catches the 500 and shows a generic alert, hiding the real error.

## Key Findings

### Backend
- **`backend/main.py:173-286`** — `predict_url` has NO try/except wrapping. `log_scan()` at line 275 can crash the endpoint.
- **`backend/main.py:313`** — `predict_text` calls `log_scan()` inside try/except, so failures return an error JSON instead of crashing.
- **`backend/database.py:31-38`** — `log_scan()` has zero error handling. Any SQLite failure propagates uncaught.
- **`backend/main.py:261`** — `url_engine.predict_url()` is also unprotected in `predict_url`.

### Frontend
- **`frontend/js/script.js:163-174`** — URL scan catch block hides actual error behind generic alert.
- **`frontend/js/script.js:258-266`** — Text scan catch block does the same.
- **`frontend/js/script.js:278`** — `displayResult()` is structurally fine, never receives data when backend 500s.
- No `console.error()` calls exist — errors invisible in DevTools.

### Database
- `backend/phishshield.db` exists (12KB, last modified Sep 9 21:43).

## Fix Needed
1. Wrap `log_scan()` calls in try/except in both `predict_url` and `predict_text`.
2. Add error handling inside `log_scan()` itself in `database.py`.
3. Add error handling around `url_engine.predict_url()` in `predict_url`.
4. Add `console.error(error)` in frontend catch blocks for visibility.
