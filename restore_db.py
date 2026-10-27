"""Execute as root in a one-off Flow container with an empty data volume."""
import os
from pathlib import Path
import sqlite3
import sys
import uuid

source = Path(sys.argv[1]).resolve(strict=True)
if not source.is_relative_to(Path('/restore')) or not source.is_file():
    raise RuntimeError('Source must be a database in the read-only /restore mount')
base = Path('/data/flow')
if base.is_symlink():
    raise RuntimeError('Data directory must not be a symlink')
base.mkdir(mode=0o700, parents=True, exist_ok=True)
target = base / 'wgnk.sqlite3'
if any((base / name).exists() for name in ('wgnk.sqlite3', 'wgnk.sqlite3-wal', 'wgnk.sqlite3-shm')):
    raise RuntimeError('Restore is allowed only into an empty database location')
temporary = base / ('.restore-' + uuid.uuid4().hex + '.sqlite3')
with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as src:
    if src.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
        raise RuntimeError('Source integrity check failed')
    with sqlite3.connect(temporary) as dst:
        src.backup(dst)
        if dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise RuntimeError('Restored database integrity check failed')
os.chown(base, 10001, 10001)
os.chown(temporary, 10001, 10001)
os.chmod(temporary, 0o600)
# Atomic create without overwriting a database that appeared meanwhile.
os.link(temporary, target)
temporary.unlink()
print('Database restored and checked; existing database was not overwritten')
