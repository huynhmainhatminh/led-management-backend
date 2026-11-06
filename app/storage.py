import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class JsonRepository:
    def __init__(self, path: Path, lock: Optional[threading.RLock] = None):
        self.path = Path(path)
        self.lock = lock or threading.RLock()
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._write([])

    def _read(self) -> list:
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def _write(self, items: list) -> None:
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
        except BaseException:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise

    def all(self) -> list:
        with self.lock:
            return self._read()

    def get(self, item_id: int) -> Optional[dict]:
        return next((i for i in self.all() if i["id"] == item_id), None)

    def insert(self, data: dict) -> dict:
        with self.lock:
            items = self._read()
            new_id = max((i["id"] for i in items), default=0) + 1
            ts = now_iso()
            record = {"id": new_id, **data, "createdAt": ts, "updatedAt": ts}
            items.append(record)
            self._write(items)
            return record

    def update(self, item_id: int, changes: dict) -> Optional[dict]:
        with self.lock:
            items = self._read()
            for idx, item in enumerate(items):
                if item["id"] == item_id:
                    items[idx] = {**item, **changes, "updatedAt": now_iso()}
                    self._write(items)
                    return items[idx]
            return None
