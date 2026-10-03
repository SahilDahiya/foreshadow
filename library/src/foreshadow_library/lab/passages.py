"""Pick short passages to vote on: a few speeches each, spread across the plays."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..analyse import WORD
from ..domain import Play, Scene
from ..repository import PlayRepository

MIN_WORDS, MAX_WORDS = 70, 190
MAX_BLOCKS = 7


@dataclass(frozen=True)
class Passage:
    play: Play
    scene: Scene
    start: int
    end: int

    @property
    def key(self) -> str:
        return f"{self.scene.id}#{self.start}-{self.end}"

    @property
    def where(self) -> str:
        s = self.scene
        return f"{self.play.title} {s.act}.{s.number}" if s.division == "scene" else f"{self.play.title}, {s.division}"


def _words(scene: Scene, i: int) -> int:
    block = scene.blocks[i]
    if block.kind != "speech":
        return 0
    return sum(len(WORD.findall(p.text)) for p in block.parts if p.kind == "line")


def _window(scene: Scene, start: int) -> int | None:
    """The end of a passage beginning at `start`: an exchange between two or more speakers."""
    words, speakers = 0, set()
    for end in range(start, min(start + MAX_BLOCKS, len(scene.blocks))):
        block = scene.blocks[end]
        words += _words(scene, end)
        if words > MAX_WORDS:
            return None
        if block.kind == "speech":
            speakers.update(block.speaker_ids)
        if words >= MIN_WORDS and len(speakers) >= 2 and block.kind == "speech":
            return end + 1
    return None


def sample(repo: PlayRepository, n: int, *, seed: int, used: set[str]) -> list[Passage]:
    """Up to n passages not voted on before, cycling through genres so no kind dominates."""
    rng = random.Random(seed)
    by_genre: dict[str, list[Play]] = {}
    for play_id in repo.list_ids():
        play = repo.get(play_id)
        if play:
            by_genre.setdefault(play.genre or "other", []).append(play)
    genres = sorted(by_genre)
    picked: list[Passage] = []
    attempts = 0
    while len(picked) < n and attempts < n * 60:
        play = rng.choice(by_genre[genres[attempts % len(genres)]])
        attempts += 1
        scene = rng.choice(play.scenes)
        starts = [i for i, b in enumerate(scene.blocks) if b.kind == "speech"]
        if not starts:
            continue
        start = rng.choice(starts)
        end = _window(scene, start)
        if end is None:
            continue
        passage = Passage(play, scene, start, end)
        if passage.key in used or any(p.scene.id == scene.id for p in picked):
            continue
        picked.append(passage)
    return picked
