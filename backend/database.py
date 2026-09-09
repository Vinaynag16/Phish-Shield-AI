import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phishshield.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            target TEXT NOT NULL,
            prediction TEXT NOT NULL,
            threat_level TEXT NOT NULL,
            score TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_scan(scan_type, target, prediction, threat_level, score):
    conn = get_connection()
    conn.execute(
        "INSERT INTO scans (type, target, prediction, threat_level, score, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (scan_type, target[:500], prediction, threat_level, score, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_stats():
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]

    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    rows = conn.execute(
        "SELECT DATE(timestamp) as day, COUNT(*) as count FROM scans WHERE timestamp >= ? GROUP BY day ORDER BY day",
        (thirty_days_ago,)
    ).fetchall()
    scans_per_day = [{"date": r["day"], "count": r["count"]} for r in rows]

    phish_count = conn.execute("SELECT COUNT(*) FROM scans WHERE prediction = 'phishing'").fetchone()[0]
    detection_rate = round((phish_count / total) * 100, 1) if total > 0 else 0

    threat_rows = conn.execute(
        "SELECT threat_level, COUNT(*) as count FROM scans GROUP BY threat_level"
    ).fetchall()
    threat_distribution = {r["threat_level"]: r["count"] for r in threat_rows}

    top_domain_rows = conn.execute(
        "SELECT target, COUNT(*) as count FROM scans WHERE prediction = 'phishing' GROUP BY target ORDER BY count DESC LIMIT 10"
    ).fetchall()
    top_domains = [{"domain": r["target"], "count": r["count"]} for r in top_domain_rows]

    recent_rows = conn.execute(
        "SELECT type, target, prediction, threat_level, score, timestamp FROM scans ORDER BY id DESC LIMIT 20"
    ).fetchall()
    recent_scans = [dict(r) for r in recent_rows]

    conn.close()

    return {
        "total_scans": total,
        "scans_per_day": scans_per_day,
        "detection_rate": detection_rate,
        "threat_distribution": threat_distribution,
        "top_domains": top_domains,
        "recent_scans": recent_scans
    }
