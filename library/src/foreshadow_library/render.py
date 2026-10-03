"""Render a passage or a scene in today's English: speech for speech, the story untouched.

The instruction is the DSPy signature's docstring, so it is the thing the preference lab
and DSPy's optimisers improve (docs/11-preference-lab.md). The model answers block by
block, keyed by block number, which lets code check that nothing was added or dropped.
"""

from __future__ import annotations

import os
import re
from datetime import UTC, datetime
from typing import Literal

import dspy
from pydantic import BaseModel

from .domain import Play, RenderedBlock, RenderedPart, Rendition, Scene

DEFAULT_MODEL = "claude-opus-5-5"
MAX_WORDS_PER_LINE = 28

# The first prompt. The lab's champion replaces it once votes have picked a better one.
SEED_PROMPT = """\
You are rendering part of a classic play into today's English, for a live show. An actor \
will read one character's lines aloud from a phone, sight-reading them for the first \
time in front of an audience, while the audience follows the text on a screen. So the \
result has to be easy to say at first sight and easy to follow at a glance, and it must \
still be the same scene: the audience knows this play and should recognise it.

Change the language, never the story:
- Keep every event, every piece of information, every image that matters, and the order \
of everything. Keep names, places and the period exactly as they are.
- Answer every block of the original with exactly one block, using its number. A speech \
stays a speech by the same speaker; a stage direction stays a stage direction. Do not \
merge, split, add or drop blocks.
- Write plain, natural, contemporary English that a person would actually say. It should \
not sound like a summary, a study guide, or slang. Keep the heat of the original: when a \
line is cruel, tender or frightened, the modern line is too.
- Give each character their own voice, and keep it steady through the scene.
- Break each speech into short lines of one or two sentences. Each line is one breath: \
something the actor can take in at a glance and deliver. A long speech becomes several \
lines; a short reply stays one line.
- Inside a speech, a stage direction that interrupts it ("Enter Lady Macbeth.") stays in \
place as a direction part, in plain modern wording.
- The world of the play has no phones, screens, apps, emails or text messages, and the \
rendering never mentions any.
"""


class Part(BaseModel):
    kind: Literal["line", "direction"]
    text: str


class Block(BaseModel):
    source_block: int
    parts: list[Part]


class RenderPassage(dspy.Signature):
    """(replaced by the prompt being used)"""

    setting: str = dspy.InputField(desc="the play, the scene, and who speaks in it")
    original: str = dspy.InputField(desc="the passage, block by block; each block has a number in [brackets]")
    blocks: list[Block] = dspy.OutputField(desc="one entry per original block, in order, with the same numbers")


def model_name(model: str | None = None) -> str:
    return model or os.environ.get("FORESHADOW_RENDITION_MODEL", DEFAULT_MODEL)


def language_model(model: str | None = None) -> dspy.LM:
    # Current Claude models reject a sampling temperature, so none is sent.
    return dspy.LM(f"anthropic/{model_name(model)}", max_tokens=16000, temperature=None)


def passage_as_prompt(play: Play, scene: Scene, start: int, end: int) -> tuple[str, str]:
    """(setting, original) for blocks start..end-1 of a scene."""
    names = {c.id: c for c in play.characters}
    blocks = scene.blocks[start:end]
    cast = sorted({sid for b in blocks if b.kind == "speech" for sid in b.speaker_ids})
    setting = (
        f"Play: {play.title}, by {play.author}.\n"
        f"Scene: {scene.heading} {scene.location or ''}".strip()
        + "\nSpeakers: "
        + "; ".join(names[c].name + (f" ({names[c].description})" if names[c].description else "") for c in cast)
    )
    lines: list[str] = []
    for i, block in enumerate(blocks, start=start):
        if block.kind == "direction":
            lines.append(f"[{i}] STAGE DIRECTION\n{block.text}\n")
        else:
            lines.append(f"[{i}] SPEECH by {block.speaker_label}")
            lines += [p.text if p.kind == "line" else f"(direction: {p.text})" for p in block.parts]
            lines.append("")
    return setting, "\n".join(lines)


FORBIDDEN = re.compile(r"\b(phone|smartphone|screen|app|email|e-mail|text message|texted|online|internet)\b", re.I)


def check(scene: Scene, start: int, end: int, blocks: list[RenderedBlock]) -> list[str]:
    """Code checks. Any warning means the rendering needs a second look."""
    warnings: list[str] = []
    got, want = [b.source_block for b in blocks], list(range(start, end))
    if got != want:
        warnings.append(f"blocks out of step with the original: expected {want}, got {got}")
    for block in blocks:
        if not start <= block.source_block < end:
            continue
        source = scene.blocks[block.source_block]
        lines = [p for p in block.parts if p.kind == "line"]
        if source.kind == "speech" and not lines:
            warnings.append(f"block {block.source_block}: a speech with no lines")
        if source.kind == "direction" and lines:
            warnings.append(f"block {block.source_block}: a stage direction rendered as speech")
        for part in block.parts:
            if m := FORBIDDEN.search(part.text):
                warnings.append(f"block {block.source_block}: mentions {m.group(0)!r}")
            if part.kind == "line" and len(part.text.split()) > MAX_WORDS_PER_LINE:
                warnings.append(f"block {block.source_block}: a line of {len(part.text.split())} words")
    return warnings


def render_passage(
    play: Play, scene: Scene, start: int, end: int, *, prompt: str, lm: dspy.LM
) -> list[RenderedBlock]:
    setting, original = passage_as_prompt(play, scene, start, end)
    with dspy.context(lm=lm):
        result = dspy.Predict(RenderPassage.with_instructions(prompt))(setting=setting, original=original)
    return [
        RenderedBlock(source_block=b.source_block, parts=[RenderedPart(kind=p.kind, text=p.text) for p in b.parts])
        for b in result.blocks
    ]


def render_scene(play: Play, scene: Scene, *, prompt: str, prompt_version: str, model: str | None = None) -> Rendition:
    blocks = render_passage(play, scene, 0, len(scene.blocks), prompt=prompt, lm=language_model(model))
    world = "original"
    return Rendition(
        id=f"{scene.id}/{world}",
        play_id=play.id,
        scene_id=scene.id,
        world=world,
        language="todays-english",
        model=model_name(model),
        prompt_version=prompt_version,
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        blocks=blocks,
        check_warnings=check(scene, 0, len(scene.blocks), blocks),
    )
