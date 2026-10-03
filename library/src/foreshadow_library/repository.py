"""Repositories: where raw texts and parsed plays are kept.

The pipeline only talks to these interfaces. Today they are files on disk; later the same
interfaces can be backed by R2 or D1 without touching the parsers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from .domain import LibraryIndex, Play, Rendition


class RawTextRepository(Protocol):
    def get(self, key: str) -> str | None: ...
    def put(self, key: str, text: str) -> None: ...


class PlayRepository(Protocol):
    def list_ids(self) -> list[str]: ...
    def get(self, play_id: str) -> Play | None: ...
    def save(self, play: Play) -> None: ...
    def get_index(self) -> LibraryIndex | None: ...
    def save_index(self, index: LibraryIndex) -> None: ...


class FileRawTextRepository:
    def __init__(self, root: Path):
        self.root = root

    def get(self, key: str) -> str | None:
        path = self.root / key
        return path.read_text(encoding="utf-8") if path.exists() else None

    def put(self, key: str, text: str) -> None:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class FilePlayRepository:
    """plays/<id>.json and index.json under one root."""

    def __init__(self, root: Path):
        self.root = root

    def list_ids(self) -> list[str]:
        return sorted(p.stem for p in (self.root / "plays").glob("*.json"))

    def get(self, play_id: str) -> Play | None:
        path = self.root / "plays" / f"{play_id}.json"
        return Play.model_validate_json(path.read_text(encoding="utf-8")) if path.exists() else None

    def save(self, play: Play) -> None:
        self._write(self.root / "plays" / f"{play.id}.json", play.model_dump(mode="json"))

    def get_index(self) -> LibraryIndex | None:
        path = self.root / "index.json"
        return LibraryIndex.model_validate_json(path.read_text(encoding="utf-8")) if path.exists() else None

    def save_index(self, index: LibraryIndex) -> None:
        self._write(self.root / "index.json", index.model_dump(mode="json"))

    @staticmethod
    def _write(path: Path, data: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Compact, but one play per file keeps diffs readable enough.
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


class RenditionRepository(Protocol):
    def get(self, scene_id: str, world: str) -> Rendition | None: ...
    def save(self, rendition: Rendition) -> None: ...


class FileRenditionRepository:
    """renditions/<play>/<act>/<scene>/<world>.json under the library root."""

    def __init__(self, root: Path):
        self.root = root

    def _path(self, scene_id: str, world: str) -> Path:
        return self.root / "renditions" / scene_id / f"{world}.json"

    def get(self, scene_id: str, world: str) -> Rendition | None:
        path = self._path(scene_id, world)
        return Rendition.model_validate_json(path.read_text(encoding="utf-8")) if path.exists() else None

    def save(self, rendition: Rendition) -> None:
        path = self._path(rendition.scene_id, rendition.world)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendition.model_dump_json(indent=1), encoding="utf-8")
