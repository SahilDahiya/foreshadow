"""Stats per scene, and the library index the app browses."""

from __future__ import annotations

import re
from collections import defaultdict

from .domain import LibraryIndex, Play, PlaySummary, Scene, SceneStats, SceneSummary, SpeakerStats

WORD = re.compile(r"[A-Za-z’']+")

# A scene is a two-hander when two speakers carry this share of the words…
TWO_HANDER_SHARE = 0.9
# …the second of them has a real share (not a soliloquy with interruptions)…
TWO_HANDER_SECOND_SHARE = 0.15
# …and it is long enough to perform.
TWO_HANDER_MIN_WORDS = 150


def scene_stats(scene: Scene) -> SceneStats:
    speeches = defaultdict(int)
    lines = defaultdict(int)
    words = defaultdict(int)
    for block in scene.blocks:
        if block.kind != "speech":
            continue
        speaker = block.speaker_ids[0]
        speeches[speaker] += 1
        for part in block.parts:
            if part.kind == "line":
                lines[speaker] += 1
                words[speaker] += len(WORD.findall(part.text))
    speakers = sorted(
        (SpeakerStats(character_id=c, speeches=speeches[c], lines=lines[c], words=words[c]) for c in speeches),
        key=lambda s: -s.words,
    )
    total_words = sum(words.values())
    top_two = sum(s.words for s in speakers[:2])
    return SceneStats(
        words=total_words,
        lines=sum(lines.values()),
        speeches=sum(speeches.values()),
        speakers=speakers,
        two_hander=len(speakers) >= 2
        and total_words >= TWO_HANDER_MIN_WORDS
        and top_two >= TWO_HANDER_SHARE * total_words
        and speakers[1].words >= TWO_HANDER_SECOND_SHARE * total_words,
    )


def analyse(play: Play) -> Play:
    for scene in play.scenes:
        scene.stats = scene_stats(scene)
    return play


def summarise(play: Play) -> PlaySummary:
    return PlaySummary(
        id=play.id,
        title=play.title,
        author=play.author,
        genre=play.genre,
        scenes=len(play.scenes),
        characters=len(play.characters),
        words=sum(s.stats.words for s in play.scenes if s.stats),
        scene_summaries=[
            SceneSummary(
                id=s.id, act=s.act, number=s.number, division=s.division, location=s.location, stats=s.stats
            )
            for s in play.scenes
            if s.stats
        ],
    )


def build_index(plays: list[Play]) -> LibraryIndex:
    return LibraryIndex(plays=[summarise(p) for p in sorted(plays, key=lambda p: p.title)])
