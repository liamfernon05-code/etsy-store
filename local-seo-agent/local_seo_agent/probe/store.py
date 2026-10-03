"""SQLite store for probe runs. Every run keeps provider, model version, prompt, location and timestamp so a
'ranking drop' can be separated from an assistant update (re-baseline when the model version changes)."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  wave TEXT NOT NULL, provider TEXT NOT NULL, model TEXT NOT NULL,
  prompt_id TEXT NOT NULL, prompt_kind TEXT NOT NULL, prompt_text TEXT NOT NULL,
  location TEXT NOT NULL, ts REAL NOT NULL,
  ok INTEGER NOT NULL, error TEXT DEFAULT '',
  verified INTEGER DEFAULT 0, name_match INTEGER DEFAULT 0, cited INTEGER DEFAULT 0, method TEXT DEFAULT '',
  entities TEXT DEFAULT '[]', cited_urls TEXT DEFAULT '[]',
  response_text TEXT DEFAULT '', cost REAL DEFAULT 0, leak INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS runs_wave ON runs(wave, provider, prompt_kind);
"""


class Store:
    def __init__(self, path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        cols = {r[1] for r in self.db.execute("PRAGMA table_info(runs)")}
        if "leak" not in cols:  # migrate databases created before UK support
            self.db.execute("ALTER TABLE runs ADD COLUMN leak INTEGER DEFAULT 0")
            self.db.commit()

    def add(self, **r) -> None:
        self.db.execute(
            "INSERT INTO runs (wave,provider,model,prompt_id,prompt_kind,prompt_text,location,ts,ok,error,verified,"
            "name_match,cited,method,entities,cited_urls,response_text,cost,leak) VALUES "
            "(:wave,:provider,:model,:prompt_id,:prompt_kind,:prompt_text,:location,:ts,:ok,:error,:verified,"
            ":name_match,:cited,:method,:entities,:cited_urls,:response_text,:cost,:leak)",
            {"ts": time.time(), "ok": 1, "error": "", "verified": 0, "name_match": 0, "cited": 0, "method": "",
             "entities": "[]", "cited_urls": "[]", "response_text": "", "cost": 0.0, "leak": 0, **r})
        self.db.commit()

    def rows(self, wave: str | None = None, provider: str | None = None, kind: str = "nonbranded") -> list[sqlite3.Row]:
        q, args = "SELECT * FROM runs WHERE prompt_kind=?", [kind]
        if wave:
            q += " AND wave=?"
            args.append(wave)
        if provider:
            q += " AND provider=?"
            args.append(provider)
        return list(self.db.execute(q, args))

    def waves(self) -> list[str]:
        return [r[0] for r in self.db.execute("SELECT wave FROM runs GROUP BY wave ORDER BY MIN(ts)")]

    def models_seen(self, provider: str, wave: str) -> set[str]:
        return {r[0] for r in self.db.execute("SELECT DISTINCT model FROM runs WHERE provider=? AND wave=?", (provider, wave))}

    def total_cost(self) -> float:
        return float(self.db.execute("SELECT COALESCE(SUM(cost),0) FROM runs").fetchone()[0])

    @staticmethod
    def dump(v) -> str:
        return json.dumps(v)

    def close(self) -> None:
        self.db.close()
