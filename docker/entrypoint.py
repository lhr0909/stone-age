#!/usr/bin/env python3
"""Prepare isolated writable state and run one legacy process as PID 1."""
import os
from pathlib import Path
import re
import shutil
import socket
import sys

role = sys.argv[1]
state = Path('/state')
state.mkdir(exist_ok=True)
os.chdir(state)

def env(name, default):
    value = os.environ.get(name, default)
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,15}', value):
        raise SystemExit(f'{name} must be 1–15 ASCII letters, digits, _, . or -')
    return value

if role == 'saac':
    for name in ('char', 'char_sleep', 'log', 'mail', 'db', 'lock'):
        Path(name).mkdir(exist_ok=True)
    if not Path('data').exists():
        shutil.copytree('/opt/stoneage/account-data', 'data')
    for name in ('family', 'fmpointdir', 'fmsmemodir', 'wklog'):
        Path('data', name).mkdir(exist_ok=True)
    Path('db/herolist').mkdir(exist_ok=True)
    Path('badpetstring.txt').touch(exist_ok=True)
    # This legacy SQL configuration has a 16-byte host field.
    host = socket.gethostbyname(os.environ.get('DB_HOST', 'db'))
    Path('acserv.cf').write_text(f'''sql_IP {host}
sql_Port 3306
sql_ID {env('DB_USER', 'stoneage')}
sql_PS {env('DB_PASSWORD', 'localdb')}
sql_DataBase {env('DB_NAME', 'stoneage')}
sql_Table user_table
sql_LOCK user_lock
sql_NAME Name
sql_PASS Pass
AutoReg 1
port 9300
pass {env('ACCOUNT_PASSWORD', 'local-game')}
logdir log
chardir char
dbdir db
maildir mail
familydir data/family
fmpointdir data/fmpointdir
fmsmemodir data/fmsmemodir
Total_Charlist 3600
Expired_mail 600
Del_Family_or_Member 3600
Write_Family 600
''')
elif role == 'gmsv':
    if not Path('data').exists():
        shutil.copytree('/opt/stoneage/world/data', 'data')
    Path('log').mkdir(exist_ok=True)
    Path('Dengon').mkdir(exist_ok=True)
    Path('Schedule').mkdir(exist_ok=True)
    shutil.copyfile('/opt/stoneage/world/log.cf', 'log.cf')
    shutil.copyfile('/opt/stoneage/world/log.cf', 'log/log.cf')
    config = Path('/opt/stoneage/world/setup.cf').read_bytes()
    values = {
        b'acserv': socket.gethostbyname(os.environ.get('ACCOUNT_HOST', 'saac')).encode(),
        b'acpasswd': env('ACCOUNT_PASSWORD', 'local-game').encode(),
        b'gameservname': b'StoneAge25', b'gameservid': b'local25',
        b'storedir': b'/accounts/char', b'fdnum': b'128',
    }
    for key, value in values.items():
        config, count = re.subn(rb'(?m)^' + key + rb'=[^\r\n]*', key+b'='+value, config)
        if count != 1:
            raise SystemExit(f'Expected one configuration key {key!r}, got {count}')
    Path('setup.cf').write_bytes(config)
else:
    raise SystemExit('Expected saac or gmsv')
os.execv('/opt/stoneage/' + role, [role])
