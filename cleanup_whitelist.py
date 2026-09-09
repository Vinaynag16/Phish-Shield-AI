"""
One-time cleanup: strip malformed lines from whitelist.txt.
Valid format: number,domain  (exactly 2 comma-separated fields)
"""

import os

WHITELIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "whitelist.txt")

with open(WHITELIST_PATH, "r") as f:
    lines = f.readlines()

original_count = len(lines)

clean_lines = []
removed = 0

for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if not stripped:
        removed += 1
        continue
    parts = stripped.split(",", 1)
    if len(parts) == 2:
        clean_lines.append(line)
    else:
        removed += 1
        print(f"Removing line {i} ({len(parts)} fields): {stripped[:80]}")

with open(WHITELIST_PATH, "w") as f:
    f.writelines(clean_lines)

new_count = len(clean_lines)
print(f"\nDone. {original_count} -> {new_count} lines ({removed} removed)")
