import subprocess, time, httpx, sys, json

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8099'],
    cwd=r'C:\Users\nagav\Desktop\phishing project\backend',
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT
)

time.sleep(10)

client = httpx.Client(timeout=30)

tests = [
    ("google.com", {"url": "https://google.com"}, "/predict/url"),
    ("bankofamerica", {"url": "https://www.bankofamerica.com/login/sign-in"}, "/predict/url"),
    ("text scan", {"text": "Urgent: verify your account now"}, "/predict/text"),
]

for name, payload, endpoint in tests:
    print(f"=== {name} ===")
    try:
        r = client.post(f"http://127.0.0.1:8099{endpoint}", json=payload)
        print(f"Status: {r.status_code}")
        data = r.json()
        for k, v in data.items():
            val = str(v)[:120]
            print(f"  {k}: {val}")
    except Exception as e:
        print(f"ERROR: {e}")
    print()

# Check DB
print("=== DB scan count ===")
import sqlite3
db = sqlite3.connect(r'C:\Users\nagav\Desktop\phishing project\backend\phishshield.db')
count = db.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
print(f"Total scans in DB: {count}")
last3 = db.execute("SELECT type, target, prediction, threat_level FROM scans ORDER BY id DESC LIMIT 3").fetchall()
for row in last3:
    print(f"  {row}")
db.close()

proc.terminate()
