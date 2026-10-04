"""The library's domain model: a play as written, faithful to its source.

This is the text layer. Curated, performable scenes (docs/05-scene-writing.md) are built
on top of it later and always point back here.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Source(BaseModel):
    """Where the text came from, so every play can be traced and re-fetched."""

    provider: Literal["gutenberg"]
    ebook_id: int
    url: str
    retrieved_at: str
    sha256: str


class Character(BaseModel):
    id: str  # slug, unique within the play: "lady-macbeth"
    name: str  # as speech headings print it: "LADY MACBETH"
    description: str | None = None  # from the dramatis personae, when listed there
    in_dramatis_personae: bool


class VerseLine(BaseModel):
    kind: Literal["line"] = "line"
    text: str


class InlineDirection(BaseModel):
    """A stage direction inside a speech: "Enter Lady Macbeth.", "Aside."."""

    kind: Literal["direction"] = "direction"
    text: str


SpeechPart = Annotated[VerseLine | InlineDirection, Field(discriminator="kind")]


class Speech(BaseModel):
    kind: Literal["speech"] = "speech"
    speaker_ids: list[str]  # usually one; "BOTH." resolves to the label's own character
    speaker_label: str  # the heading exactly as printed, without the full stop
    parts: list[SpeechPart]


class StageDirection(BaseModel):
    kind: Literal["direction"] = "direction"
    text: str


Block = Annotated[Speech | StageDirection, Field(discriminator="kind")]


class SpeakerStats(BaseModel):
    character_id: str
    speeches: int
    lines: int
    words: int


class SceneStats(BaseModel):
    words: int
    lines: int
    speeches: int
    speakers: list[SpeakerStats]  # most words first
    two_hander: bool  # two speakers carry almost all of it: a candidate for the show


class Scene(BaseModel):
    id: str  # "macbeth/1/7"; divisions use their name: "henry-iv-part-2/induction"
    act: int | None  # None for divisions outside the acts (induction, epilogue)
    number: int | None
    division: Literal["scene", "prologue", "induction", "epilogue", "chorus"]
    heading: str  # "SCENE VII." or "EPILOGUE"
    location: str | None
    blocks: list[Block]
    stats: SceneStats | None = None


class Play(BaseModel):
    id: str  # slug: "macbeth"
    title: str  # "The Tragedy of Macbeth"
    author: str
    genre: Literal["comedy", "tragedy", "history", "romance"] | None
    source: Source
    characters: list[Character]
    scenes: list[Scene]  # in order; acts are a property of each scene


class SceneSummary(BaseModel):
    id: str
    act: int | None
    number: int | None
    division: str
    location: str | None
    stats: SceneStats


class PlaySummary(BaseModel):
    id: str
    title: str
    author: str
    genre: str | None
    scenes: int
    characters: int
    words: int
    scene_summaries: list[SceneSummary]


class LibraryIndex(BaseModel):
    plays: list[PlaySummary]


# --- Renditions: a scene in today's English (docs/10-play-library.md) ---------------


class RenderedPart(BaseModel):
    kind: Literal["line", "direction"]
    text: str


class RenderedBlock(BaseModel):
    """One block of the rendition. It always answers exactly one block of the text scene."""

    source_block: int  # index into the text scene's blocks
    parts: list[RenderedPart]


class Rendition(BaseModel):
    id: str  # "<scene id>/<world>"
    play_id: str
    scene_id: str
    world: str  # "original", or a modern world the room can choose
    language: str  # "todays-english"
    model: str
    prompt_version: str
    created_at: str
    approved_at: str | None = None  # nothing reaches a show until a person approves it
    blocks: list[RenderedBlock]
    check_warnings: list[str] = []


# --- Candidates: stretches of a scene that could be performed (docs/10-play-library.md) --


class CandidateMetrics(BaseModel):
    host_speeches: int
    partner_speeches: int
    host_words: int
    partner_words: int
    host_share: float  # of all words in the stretch
    mean_host_words: float  # per host speech
    median_host_words: float
    max_host_words: int
    monologues: int  # host speeches over 100 words: allowed, and worth knowing about
    minutes: float  # estimated running time on stage (see candidates.py)
    questions: float  # share of host speeches that ask something
    address: float  # share of host speeches that speak to the partner directly (you, thou…)
    names: int  # host speeches that say the partner's name
    directions: int  # stage directions inside the stretch
    cast_changes: int  # entrances and exits inside the stretch


class Candidate(BaseModel):
    """A two-person stretch of a scene, trimmed so the host's character opens and closes it."""

    id: str  # "<scene id>#<start>-<end>@<host character id>"
    play_id: str
    play_title: str
    genre: str | None
    scene_id: str
    start: int  # block index, inclusive
    end: int  # block index, exclusive
    host: str  # character id the host would read
    host_name: str
    partner: str  # character id the improviser would play
    partner_name: str
    first_line: str
    last_line: str
    metrics: CandidateMetrics
    size: Literal["small", "medium", "big"]  # about 5, 10 or 20 minutes on stage
    cut: bool = False  # True: a shorter cut of a longer stretch, ending early on a host line
    score: float  # 0–100, higher is better for the show
    reasons: list[str] = []  # why it scored as it did, in plain words
