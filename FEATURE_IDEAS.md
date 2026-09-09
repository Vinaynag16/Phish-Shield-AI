# PhishShield AI v2.0 — Feature Ideas & Roadmap

Generated from project architecture analysis on 2026-09-03.

---

## Overview

PhishShield AI is a phishing detection platform combining LSTM neural networks, deterministic whitelisting, NLP-based text analysis, and WHOIS forensics. The backend is built with FastAPI + TensorFlow, and the frontend is a vanilla JS/CSS dark-themed dashboard.

After reviewing the full codebase — including the backend API, model inference layer, training pipeline, frontend scanner, chatbot, and news feed — I identified several existing issues that should be fixed first, followed by seven feature proposals ranked by impact and effort.

---

## Known Issues to Fix First

Before building new features, there are five bugs and gaps in the current codebase that need attention. Some are security risks, others affect accuracy and performance.

**Critical:** The NewsData.io API key is hardcoded directly in `frontend/js/news.js` at line 9. Anyone who opens the browser dev tools can see and steal this key. It should be moved to a `.env` file and proxied through the backend.

**High:** The `features.html` page has broken HTML — a `<div>` is left unclosed and `<li>` elements are misplaced inside it, which breaks the navigation bar on that page.

**High:** The "Engine Breakdown" section in the scanner results (Domain Integrity and Structural Entropy bars) currently displays random values instead of real scores from the model. This undermines the tool's credibility and should return actual feature scores from the URL analysis.

**Medium:** The whitelist file (`whitelist.txt` with 1M+ domains) is read from disk on every single API request. This is a performance bottleneck — it should be loaded once at server startup and cached in memory.

**Low:** There are two elements with `id="chat-toggle"` in `index.html`, which causes duplicate DOM elements.

| # | Issue | Location | Severity | Fix |
|---|-------|----------|----------|-----|
| 1 | API key hardcoded in frontend | `frontend/js/news.js:9` | Critical | Move to `.env`, proxy via backend |
| 2 | Broken nav HTML in features page | `frontend/features.html:21-27` | High | Fix HTML structure |
| 3 | Analysis bars show random data | `frontend/js/script.js:375-383` | High | Return real scores from backend |
| 4 | Whitelist read from disk per request | `backend/main.py:64-66` | Medium | Cache in memory at startup |
| 5 | Duplicate `id="chat-toggle"` | `frontend/index.html:129,133` | Low | Remove duplicate element |

---

## Feature Proposals

Here are seven feature ideas, each solving a specific problem in the current system. I've grouped them by priority and included a summary table at the end.

| # | Feature | Priority | Impact | Effort |
|---|---------|----------|--------|--------|
| F1 | Real-Time Dashboard Analytics | P1 | High | 1-2 days |
| F2 | Batch URL Scanner | P1 | High | 3-4 hours |
| F3 | User Auth + Scan Persistence | P2 | Medium | 2-3 days |
| F4 | Phishing URL Reporting / Community Feed | P2 | Medium | 1-2 days |
| F5 | Email Header Analyzer | P2 | Medium | 1 day |
| F6 | Browser Extension | P3 | Nice to have | 3-5 days |
| F7 | Model Retraining Pipeline | P3 | Nice to have | 2-3 days |

---

### F1 — Real-Time Dashboard Analytics

Right now, the scanner gives you a verdict for a single URL and that's it. There's no way to see trends over time — how many URLs you've scanned, what percentage were phishing, what threat levels are most common, or which domains get flagged the most. For a tool that positions itself as "SOC-style," this is a big gap.

This feature would add a dedicated analytics dashboard page that visualizes scan data in real time. Think of it as the "home base" view for a security analyst using the tool daily.

**What it would look like:**
- Scans per day (line chart)
- Detection rate percentage (gauge or number card)
- Threat level distribution (pie chart: High / Medium / Low)
- Top 10 most flagged domains (bar chart)
- Recent scan activity feed

**Implementation approach:**
The backend would need a new `GET /stats` endpoint that queries a scan log table (SQLite or similar) and returns aggregated data. The frontend would use Chart.js or a similar lightweight library to render the visualizations. The scan log would be written to on every `/predict/url` and `/predict/text` call.

| Component | Details |
|-----------|---------|
| New Backend Endpoint | `GET /stats` — returns aggregated scan metrics |
| New Frontend Page | `dashboard.html` with Chart.js visualizations |
| Database | SQLite table: `scans(id, type, target, prediction, threat_level, timestamp)` |
| Dependencies | `chart.js` (CDN), SQLite (built into Python) |

---

### F2 — Batch URL Scanner

The current system only accepts one URL at a time. In real-world phishing investigations — like when a SOC team receives a report with 20 suspicious links — you'd have to scan them one by one. That's slow and tedious.

This feature adds a batch scanning mode where users can paste multiple URLs (one per line) and get a consolidated report showing which are safe, which are phishing, and which are suspicious. It's essentially a loop over the existing `/predict/url` logic, but presented as a single action with a summary.

**Implementation approach:**
A new `POST /predict/batch` endpoint would accept a JSON array of URLs, run the existing prediction logic on each (potentially in parallel using `asyncio.gather`), and return a results array plus a summary object. The frontend would add a new "Batch Scanner" tab with a textarea input and a results table.

| Component | Details |
|-----------|---------|
| New Backend Endpoint | `POST /predict/batch` — accepts `{ "urls": [...] }`, returns results + summary |
| New Frontend Tab | "Batch Scanner" tab in `scanner.html` with textarea input |
| Performance | Use `asyncio.gather` for parallel inference to keep latency low |
| Dependencies | None — reuses existing URL prediction logic |

---

### F3 — User Authentication + Scan Persistence

Scan history is currently stored in `localStorage`, which means it's tied to a single browser and gets wiped if the user clears their cache. For an "enterprise-grade" tool, this isn't acceptable — users need their scan history to persist across sessions and devices.

This feature would add JWT-based authentication and a backend database to store scan history per user. It would also unlock the ability to have user-specific settings, saved scans, and eventually a shared team view.

**Implementation approach:**
Add SQLAlchemy + SQLite (or PostgreSQL) for user accounts and scan records. Use `python-jose` for JWT tokens and `passlib` for password hashing. The frontend would get login/register pages, and the scan history would be fetched from the backend instead of localStorage.

| Component | Details |
|-----------|---------|
| New Backend Endpoints | `POST /auth/register`, `POST /auth/login`, `GET /scans` |
| New Frontend Pages | `login.html`, `register.html`, updated history section |
| Database | SQLite: `users(id, email, password_hash)`, `scans(id, user_id, type, target, result, timestamp)` |
| Dependencies | `python-jose`, `passlib`, `sqlalchemy` |

---

### F4 — Phishing URL Reporting / Community Feed

PhishShield currently detects phishing passively — it analyzes what you give it. But there's no way for users to contribute known phishing URLs back to the system. This feature would let users flag URLs they've confirmed as phishing, creating a community-driven intelligence layer.

Over time, this reported data could be used to supplement the whitelist/blacklist, improve model retraining, and build a public feed of active phishing campaigns.

**Implementation approach:**
Add a `POST /report` endpoint that accepts a URL and reason from authenticated users. Store reports in a SQLite table with status (pending/approved/rejected). The frontend would add a "Report Phishing" button on scan results. An optional admin panel could review and approve reports.

| Component | Details |
|-----------|---------|
| New Backend Endpoints | `POST /report` (submit URL), `GET /reported` (list reports) |
| New Frontend | "Report Phishing" button on scan results, optional admin review page |
| Database | SQLite: `reports(id, user_id, url, reason, status, created_at)` |
| Dependencies | Optional admin auth for review panel |

---

### F5 — Email Header Analyzer

Phishing doesn't just happen through URLs — it arrives via email. A huge part of phishing defense is analyzing email headers to detect SPF/DKIM failures, spoofed sender addresses, and suspicious routing. PhishShield doesn't currently handle this.

This feature would add a new scanner tab where users can paste raw email headers. The backend would parse them using Python's built-in `email` module and apply heuristic rules to flag authentication failures, mismatched senders, and suspicious relay chains.

**Implementation approach:**
A new `POST /predict/email` endpoint would parse the raw header text, extract key fields (From, Received, Return-Path, Authentication-Results), and apply a scoring system based on SPF pass/fail, DKIM status, sender domain mismatch, and number of hops. The frontend would add an "Email Header Analyzer" tab to the scanner.

| Component | Details |
|-----------|---------|
| New Backend Endpoint | `POST /predict/email` — accepts raw email header text |
| New Frontend Tab | "Email Header Analyzer" tab in `scanner.html` |
| Parsing | Python `email` stdlib + custom heuristic scoring rules |
| Dependencies | None — uses stdlib only |

---

### F6 — Browser Extension

Currently, users have to manually copy a URL and paste it into the PhishShield scanner. A browser extension would eliminate this friction by auto-scanning URLs as the user browses — showing a green or red badge in the toolbar based on the verdict.

This is a longer-term feature that would significantly expand the tool's reach and usability, making it feel like a real security product rather than just a web app.

**Implementation approach:**
Build a Chrome extension using Manifest V3. A background service worker would intercept navigation events, send the URL to the existing `/predict/url` endpoint, and update the extension badge icon accordingly. A popup UI would show the last scan result and allow manual scanning.

| Component | Details |
|-----------|---------|
| New Product | Chrome extension (Manifest V3) |
| Backend Changes | None — reuses existing `/predict/url` endpoint |
| New Frontend | Extension popup UI (HTML/CSS/JS) |
| Dependencies | Chrome Web Store developer account |

---

### F7 — Model Retraining Pipeline

The LSTM model was trained once on a static dataset. Phishing patterns evolve constantly — new obfuscation techniques, new TLDs, new brand impersonation tactics emerge weekly. Without retraining, the model's accuracy will degrade over time.

You already have training scripts in `training/` (LSTM detector, hyperparameter tuning, cross-validation). This feature would automate the retraining process on a schedule, pulling fresh data from sources like OpenPhish and PhishTank, and versioning models so you can roll back if a new version performs worse.

**Implementation approach:**
Set up a scheduled job (APScheduler or cron) that periodically fetches new phishing URLs from OpenPhish/PhishTank, merges them with existing training data, retrains the model, evaluates it against a holdout set, and only deploys it if accuracy improves. Model files would be versioned (e.g., `phishshield_lstm_v3.h5`).

| Component | Details |
|-----------|---------|
| New Backend Endpoint | `POST /retrain` (admin only) or scheduled cron job |
| New Frontend | Admin panel showing model version, last trained date, accuracy |
| Data Sources | OpenPhish API, PhishTank API |
| Dependencies | `apscheduler`, existing training scripts in `training/` |

---

## Recommended Implementation Order

The features should be implemented in phases. Phase 0 is critical — it fixes security and UX issues before adding anything new. Phase 1 delivers the two highest-impact features quickly. Subsequent phases expand scope and add enterprise capabilities.

| Phase | What | Timeline | Why This Order |
|-------|------|----------|----------------|
| **Phase 0** | Fix all known issues (Section 1) | Day 1 | Security risk + broken UX must be resolved first |
| **Phase 1** | F2 (Batch Scanner) + F1 (Dashboard) | Week 1 | Highest impact, lowest effort — makes the tool dramatically more useful |
| **Phase 2** | F5 (Email Header) + F4 (URL Reporting) | Week 2 | Expands detection scope and adds community intelligence |
| **Phase 3** | F3 (Auth + Persistence) | Week 3 | Enterprise-readiness; requires database setup |
| **Phase 4** | F7 (Retraining) + F6 (Extension) | Week 4+ | Long-term sustainability and broader reach |

---

## Effort vs Impact

For a quick visual reference, here's where each feature lands:

- **Quick Wins (low effort, high impact):** Batch Scanner, Dashboard Analytics
- **Solid Investments (medium effort, high impact):** Auth + Persistence
- **Expansions (medium effort, medium impact):** Email Header Analyzer, URL Reporting
- **Long-term Plays (high effort, nice to have):** Browser Extension, Model Retraining

---

*This document was generated from a full codebase review. Update the status of each feature as it moves from Proposed → In Progress → Complete.*
