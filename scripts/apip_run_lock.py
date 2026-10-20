"""Fail-closed exclusive lease for recurring APIP engineering runs.

Interrupted runs leave the lock in place. A human must confirm the prior run
has stopped before removing it; this intentionally prefers a missed run over
concurrent edits to the shared working tree.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = ROOT / "data" / "private-spending" / "engineering-run.lock"


class LockError(RuntimeError):
    pass


def acquire(path: Path = LOCK_FILE, run_id: str | None = None) -> str:
    token = run_id or secrets.token_urlsafe(24)
    payload = json.dumps({"run_id": token, "started_at_utc": datetime.now(timezone.utc).isoformat()})
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        try:
            owner = json.loads(path.read_text(encoding="utf-8"))
            summary = f"active run {owner.get('run_id', '<unknown>')} started {owner.get('started_at_utc', '<unknown>')}"
        except (OSError, json.JSONDecodeError):
            summary = "unreadable lock; manual inspection required"
        raise LockError(f"APIP run lock is held ({summary}); do not edit project files.") from None
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(payload + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return token


def release(path: Path, run_id: str) -> None:
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise LockError("Cannot release an absent or unreadable APIP run lock; inspect it manually.") from None
    if not secrets.compare_digest(str(current.get("run_id", "")), run_id):
        raise LockError("Run ID does not own the APIP run lock; lock preserved.")
    path.unlink()


def status(path: Path = LOCK_FILE) -> dict | None:
    if not path.exists():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict) or not record.get("run_id"):
            raise ValueError("required run_id is missing")
        return record
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise LockError(f"APIP run lock is corrupt ({exc}); manual inspection required.") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("acquire", "release", "status"))
    parser.add_argument("run_id", nargs="?")
    args = parser.parse_args()
    try:
        if args.action == "acquire":
            if args.run_id:
                raise LockError("Do not reuse an existing run ID when acquiring a lock.")
            print(acquire())
        elif args.action == "release":
            if not args.run_id:
                raise LockError("release requires the run ID printed by acquire.")
            release(LOCK_FILE, args.run_id)
            print("APIP run lock released.")
        else:
            record = status()
            print(json.dumps(record) if record else "No APIP run lock is held.")
        return 0
    except LockError as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
