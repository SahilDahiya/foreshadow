"""Turn a rendered candidate into a scene the app can play.

The app's scene (app/shared/scene.ts) is a flat list of lines: the host's are voiced, the
improviser's are ghost lines. One line is one turn: everything the host says before the
improviser speaks is a single line, shown on a single screen, with its rendered lines kept
as line breaks. A direction before the speech becomes its delivery description; a
direction in the middle of it stays in place, in brackets, on a row of its own. An
improviser's whole speech is one ghost line. There is no narration
(docs/05-scene-writing.md).

The briefing and the mime task are mechanical placeholders for now.
"""

from __future__ import annotations

import hashlib
import re

from .domain import Candidate, Play, Rendition, Scene

# Placeholder mime tasks: neutral, physical, and revealing nothing about the scene.
MIME_TASKS = [
    "Sweeping the floor",
    "Folding laundry",
    "Lighting candles",
    "Writing a letter",
    "Mending a torn sleeve",
    "Setting a table",
    "Pacing and counting steps",
    "Polishing boots",
    "Warming hands at a fire",
    "Packing a travelling bag",
    "Looking for something lost",
    "Pouring a drink",
]


def scene_slug(candidate: Candidate) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", candidate.scene_id.lower()).strip("-")
    return f"{base}-{candidate.host}-{candidate.size}"


def _describe(play: Play, character_id: str) -> str:
    c = next((c for c in play.characters if c.id == character_id), None)
    if c is None:
        return character_id.upper()
    return f"{c.name}, {c.description}" if c.description else c.name


def to_app_scene(play: Play, scene: Scene, candidate: Candidate, rendition: Rendition) -> dict:
    rendered = {b.source_block: b.parts for b in rendition.blocks}
    lines: list[dict] = []
    cue: str | None = None  # a direction waiting for the next host line
    for i in range(candidate.start, candidate.end):
        block = scene.blocks[i]
        parts = rendered.get(i, [])
        if block.kind == "direction":
            cue = " ".join(p.text for p in parts) or cue
            continue
        if block.speaker_ids[0] == candidate.host:
            rows: list[str] = []
            for part in parts:
                if part.kind == "line":
                    rows.append(part.text)
                elif not rows:
                    cue = part.text  # a direction before the first words: how to say the turn
                else:
                    rows.append(f"[{part.text.rstrip('.')}]")  # mid-speech: stays where it falls
            if not rows:
                continue
            if lines and lines[-1]["voiced"]:
                # The improviser's character said nothing between two host speeches (their
                # reply was only a stage direction): it is still one turn for the host.
                lines[-1]["text"] += "\n" + "\n".join(rows)
            else:
                line = {"character": candidate.host_name, "text": "\n".join(rows), "voiced": True}
                if cue:
                    line["cue"] = cue.rstrip(".")
                lines.append(line)
            cue = None
        else:
            cue = None  # a direction for the improviser's character is not the host's to read
            text = " ".join(p.text for p in parts if p.kind == "line")
            if text:
                lines.append({"character": candidate.partner_name, "text": text, "voiced": False})
    where = f"Act {scene.act}, scene {scene.number}" if scene.division == "scene" else scene.heading.title()
    task = MIME_TASKS[int(hashlib.sha256(candidate.id.encode()).hexdigest(), 16) % len(MIME_TASKS)]
    return {
        "id": scene_slug(candidate),
        "title": play.title,
        "genre": (play.genre or "play").capitalize(),
        "about": f"{where}. {scene.location or ''}".strip(),
        "briefing": (
            f"You are {_describe(play, candidate.host)}. "
            f"You are speaking with {_describe(play, candidate.partner)}. "
            "You open the scene and you have the last line."
        ),
        "hostCharacter": candidate.host_name,
        "openingTasks": [{"character": candidate.partner_name, "task": task}],
        "size": candidate.size,
        "minutes": candidate.metrics.minutes,
        "source": {"candidate": candidate.id, "rendition": rendition.id, "prompt": rendition.prompt_version},
        "lines": lines,
    }


def summary(app_scene: dict, candidate: Candidate) -> dict:
    voiced = sum(1 for line in app_scene["lines"] if line["voiced"])
    return {
        "id": app_scene["id"],
        "title": app_scene["title"],
        "about": app_scene["about"],
        "genre": app_scene["genre"],
        "host": candidate.host_name,
        "partner": candidate.partner_name,
        "size": candidate.size,
        "minutes": candidate.metrics.minutes,
        "hostLines": voiced,
        "score": candidate.score,
        "opens": next(line["text"] for line in app_scene["lines"] if line["voiced"]),
    }
