"""Build the language-transformation eval set: short passages from two-person scenes.

Twelve are chosen deliberately (famous exchanges, each starting at a known line); the
rest are drawn at random, evenly across genres, one passage per scene. The set is fixed
once written: `evals/language/cases.jsonl` is the source of truth, not this script.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from ..domain import Play, Scene
from ..lab.passages import _window
from ..repository import PlayRepository

CASES = Path(__file__).resolve().parents[3] / "evals" / "language" / "cases.jsonl"
N_CASES = 40
SEED = 20261003

# scene id → words that begin the passage
CHOSEN = {
    "macbeth/1/7": "We will proceed no further",
    "macbeth/2/2": "I have done the deed",
    "romeo-and-juliet/2/2": "How cam’st thou hither",
    "hamlet/3/4": "Now, mother, what’s the matter",
    "richard-iii/1/2": "Lady, you know no rules of charity",
    "king-lear/1/5": "If a man’s brains were in’s heels",
    "much-ado-about-nothing/3/1": "But are you sure",
    "the-tempest/3/1": "Admir’d Miranda",
    "antony-and-cleopatra/1/3": "I am sick and sullen",
    "the-merchant-of-venice/1/3": "Signior Antonio, many a time",
    "henry-iv-part-1/2/3": "O my good lord, why are you thus alone",
    "twelfth-night/1/4": "Thou know’st no less but all",
}


def _find(scene: Scene, phrase: str) -> int | None:
    for i, block in enumerate(scene.blocks):
        if block.kind == "speech" and any(p.kind == "line" and phrase in p.text for p in block.parts):
            return i
    return None


def _case(play: Play, scene: Scene, start: int, end: int, how: str) -> dict:
    return {
        "id": f"{scene.id.replace('/', '_')}_{start}-{end}",
        "play_id": play.id,
        "scene_id": scene.id,
        "start": start,
        "end": end,
        # tags[0] is the grouping key: the genre.
        "tags": [play.genre or "other", play.title, how],
    }


def build(repo: PlayRepository) -> list[dict]:
    rng = random.Random(SEED)
    plays = {pid: repo.get(pid) for pid in repo.list_ids()}
    cases: list[dict] = []
    used: set[str] = set()

    for scene_id, phrase in CHOSEN.items():
        play = plays[scene_id.split("/")[0]]
        scene = next(s for s in play.scenes if s.id == scene_id)
        found = _find(scene, phrase)
        if found is None:
            raise ValueError(f"{scene_id}: phrase not found: {phrase!r}")
        # Walk forward to the first start that makes a full passage.
        window = next(((s, e) for s in range(found, len(scene.blocks)) if (e := _window(scene, s))), None)
        if window is None:
            raise ValueError(f"{scene_id}: no passage from {phrase!r}")
        cases.append(_case(play, scene, *window, "chosen"))
        used.add(scene_id)

    by_genre: dict[str, list[tuple[Play, Scene]]] = {}
    for play in plays.values():
        for scene in play.scenes:
            if scene.stats and scene.stats.two_hander and scene.id not in used:
                by_genre.setdefault(play.genre or "other", []).append((play, scene))
    genres = sorted(by_genre)
    for pool in by_genre.values():
        rng.shuffle(pool)
    turn = 0
    while len(cases) < N_CASES:
        pool = by_genre[genres[turn % len(genres)]]
        turn += 1
        while pool:
            play, scene = pool.pop()
            starts = [i for i, b in enumerate(scene.blocks) if b.kind == "speech"]
            rng.shuffle(starts)
            window = next(((s, e) for s in starts if (e := _window(scene, s))), None)
            if window:
                cases.append(_case(play, scene, *window, "random"))
                break
    return cases


def write(repo: PlayRepository) -> list[dict]:
    cases = build(repo)
    CASES.parent.mkdir(parents=True, exist_ok=True)
    CASES.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in cases) + "\n", encoding="utf-8")
    return cases


def load() -> list[dict]:
    return [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines() if line.strip()]
