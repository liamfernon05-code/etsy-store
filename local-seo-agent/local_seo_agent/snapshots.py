"""SQLite store for time-series data that needs history: competitor place snapshots (review velocity) and geo-grid runs."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS place_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, query TEXT NOT NULL, rank INTEGER,
  place_id TEXT NOT NULL, name TEXT, rating REAL, review_count INTEGER, primary_type TEXT, types TEXT DEFAULT '[]',
  website TEXT DEFAULT '', phone TEXT DEFAULT '', is_client INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ps_place ON place_snapshots(place_id, ts);
CREATE TABLE IF NOT EXISTS grid_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, wave TEXT NOT NULL, keyword TEXT NOT NULL,
  provider TEXT NOT NULL, size INTEGER, spacing_km REAL, points TEXT NOT NULL, arp REAL, solv REAL, coverage REAL, cost REAL DEFAULT 0
);
"""


class Snapshots:
    def __init__(self, path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def add_place(self, **r) -> None:
        self.db.execute(
            "INSERT INTO place_snapshots (ts,query,rank,place_id,name,rating,review_count,primary_type,types,website,phone,is_client) "
            "VALUES (:ts,:query,:rank,:place_id,:name,:rating,:review_count,:primary_type,:types,:website,:phone,:is_client)",
            {"ts": time.time(), "rank": None, "name": "", "rating": None, "review_count": None, "primary_type": "",
             "types": "[]", "website": "", "phone": "", "is_client": 0, **r})
        self.db.commit()

    def latest_per_place(self) -> list[sqlite3.Row]:
        return list(self.db.execute(
            "SELECT * FROM place_snapshots WHERE id IN (SELECT MAX(id) FROM place_snapshots GROUP BY place_id)"))

    def history(self, place_id: str) -> list[sqlite3.Row]:
        return list(self.db.execute("SELECT * FROM place_snapshots WHERE place_id=? ORDER BY ts", (place_id,)))

    def add_grid(self, wave: str, keyword: str, provider: str, size: int, spacing_km: float, points: list[dict],
                 agg: dict, cost: float) -> None:
        self.db.execute(
            "INSERT INTO grid_runs (ts,wave,keyword,provider,size,spacing_km,points,arp,solv,coverage,cost) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (time.time(), wave, keyword, provider, size, spacing_km, json.dumps(points), agg["arp"], agg["solv"], agg["coverage"], cost))
        self.db.commit()

    def grids(self, wave: str | None = None) -> list[sqlite3.Row]:
        if wave:
            return list(self.db.execute("SELECT * FROM grid_runs WHERE wave=? ORDER BY ts", (wave,)))
        return list(self.db.execute("SELECT * FROM grid_runs ORDER BY ts"))

    def total_cost(self) -> float:
        return float(self.db.execute("SELECT COALESCE(SUM(cost),0) FROM grid_runs").fetchone()[0])
