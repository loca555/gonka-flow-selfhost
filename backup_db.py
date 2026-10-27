"""Execute inside the Flow container, as uid 10001. Prints a relative file name."""
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3

base = Path('/data/flow')
source = base / 'wgnk.sqlite3'
if not source.is_file():
    raise RuntimeError('Flow database does not exist yet')
directory = base / 'backups'
directory.mkdir(mode=0o700, exist_ok=True)
target = directory / ('flow-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.sqlite3')
fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
os.close(fd)
with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as src:
    with sqlite3.connect(target) as dst:
        src.backup(dst)
        if dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise RuntimeError('Backup integrity check failed')
print(target.relative_to(base))
