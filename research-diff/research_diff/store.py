"""Local persistence for tracked research objects and their snapshots over time."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .client import SearchResult

DEFAULT_ROOT = Path.home() / ".research-diff"


class ResearchObject:
    def __init__(self, root: Path, name: str):
        self.name = name
        self.dir = root / name
        self.meta_path = self.dir / "meta.json"
        self.snapshots_dir = self.dir / "snapshots"

    @property
    def exists(self) -> bool:
        return self.meta_path.exists()

    def create(self, query: str, mock_fixture: Optional[str] = None) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        meta = {"name": self.name, "query": query, "mock_fixture": mock_fixture}
        self.meta_path.write_text(json.dumps(meta, indent=2))

    def load_meta(self) -> dict:
        return json.loads(self.meta_path.read_text())

    def snapshot_paths(self) -> list[Path]:
        return sorted(self.snapshots_dir.glob("*.json"))

    def call_count(self) -> int:
        return len(self.snapshot_paths())

    def save_snapshot(self, result: SearchResult, timestamp: str) -> Path:
        # Sequence prefix guarantees a unique, orderable filename even when
        # consecutive runs land within the same wall-clock second.
        seq = self.call_count() + 1
        path = self.snapshots_dir / f"{seq:04d}_{timestamp}.json"
        path.write_text(json.dumps(result.to_dict(), indent=2))
        return path

    def load_snapshot(self, path: Path) -> SearchResult:
        return SearchResult.from_dict(json.loads(path.read_text()))


def list_objects(root: Path = DEFAULT_ROOT) -> list[str]:
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir())
