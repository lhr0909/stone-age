#!/usr/bin/env python3
"""Check the listener, and for gmsv an established account connection.

Gameplay/login is checked separately by the integration client.
"""
from pathlib import Path
import sys
role = sys.argv[1]
port = 9300 if role == 'saac' else 9065
rows = [line.split() for line in Path('/proc/net/tcp').read_text().splitlines()[1:]]
listening = any(int(r[1].split(':')[1], 16) == port and r[3] == '0A' for r in rows)
account = role == 'saac' or any(int(r[2].split(':')[1], 16) == 9300 and r[3] == '01' for r in rows)
sys.exit(0 if listening and account else 1)
