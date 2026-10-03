"""Parser for Project Gutenberg ebook #100, The Complete Works of William Shakespeare.

Deliberately specific to this one edition's layout: hyperfocus first, abstract later.
Other sources get their own parser producing the same domain model.

The layout, as observed:
- a global contents list names every work; each work starts with its title on a line;
- each play has its own contents list, then "Dramatis Personæ", then the text;
- "ACT I" and "SCENE VII. The same. A Lobby in the Castle." headings;
- "LADY MACBETH." on its own line starts a speech;
- a line indented by exactly one space is a stage direction, even mid-speech;
- "[_Exit._]" marks a direction inline or on its own line; songs are indented further.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..domain import (
    Block,
    Character,
    InlineDirection,
    Play,
    Scene,
    Source,
    Speech,
    SpeechPart,
    StageDirection,
    VerseLine,
)

AUTHOR = "William Shakespeare"

# Title as printed in the edition → (id, display title, genre). Poems are left out.
PLAYS: dict[str, tuple[str, str, str]] = {
    "ALL’S WELL THAT ENDS WELL": ("alls-well-that-ends-well", "All’s Well That Ends Well", "comedy"),
    "THE TRAGEDY OF ANTONY AND CLEOPATRA": ("antony-and-cleopatra", "Antony and Cleopatra", "tragedy"),
    "AS YOU LIKE IT": ("as-you-like-it", "As You Like It", "comedy"),
    "THE COMEDY OF ERRORS": ("the-comedy-of-errors", "The Comedy of Errors", "comedy"),
    "THE TRAGEDY OF CORIOLANUS": ("coriolanus", "Coriolanus", "tragedy"),
    "CYMBELINE": ("cymbeline", "Cymbeline", "romance"),
    "THE TRAGEDY OF HAMLET, PRINCE OF DENMARK": ("hamlet", "Hamlet", "tragedy"),
    "THE FIRST PART OF KING HENRY THE FOURTH": ("henry-iv-part-1", "Henry IV, Part 1", "history"),
    "THE SECOND PART OF KING HENRY THE FOURTH": ("henry-iv-part-2", "Henry IV, Part 2", "history"),
    "THE LIFE OF KING HENRY THE FIFTH": ("henry-v", "Henry V", "history"),
    "THE FIRST PART OF HENRY THE SIXTH": ("henry-vi-part-1", "Henry VI, Part 1", "history"),
    "THE SECOND PART OF KING HENRY THE SIXTH": ("henry-vi-part-2", "Henry VI, Part 2", "history"),
    "THE THIRD PART OF KING HENRY THE SIXTH": ("henry-vi-part-3", "Henry VI, Part 3", "history"),
    "KING HENRY THE EIGHTH": ("henry-viii", "Henry VIII", "history"),
    "THE LIFE AND DEATH OF KING JOHN": ("king-john", "King John", "history"),
    "THE TRAGEDY OF JULIUS CAESAR": ("julius-caesar", "Julius Caesar", "tragedy"),
    "THE TRAGEDY OF KING LEAR": ("king-lear", "King Lear", "tragedy"),
    "LOVE’S LABOUR’S LOST": ("loves-labours-lost", "Love’s Labour’s Lost", "comedy"),
    "THE TRAGEDY OF MACBETH": ("macbeth", "Macbeth", "tragedy"),
    "MEASURE FOR MEASURE": ("measure-for-measure", "Measure for Measure", "comedy"),
    "THE MERCHANT OF VENICE": ("the-merchant-of-venice", "The Merchant of Venice", "comedy"),
    "THE MERRY WIVES OF WINDSOR": ("the-merry-wives-of-windsor", "The Merry Wives of Windsor", "comedy"),
    "A MIDSUMMER NIGHT’S DREAM": ("a-midsummer-nights-dream", "A Midsummer Night’s Dream", "comedy"),
    "MUCH ADO ABOUT NOTHING": ("much-ado-about-nothing", "Much Ado About Nothing", "comedy"),
    "THE TRAGEDY OF OTHELLO, THE MOOR OF VENICE": ("othello", "Othello", "tragedy"),
    "PERICLES, PRINCE OF TYRE": ("pericles", "Pericles", "romance"),
    "KING RICHARD THE SECOND": ("richard-ii", "Richard II", "history"),
    "KING RICHARD THE THIRD": ("richard-iii", "Richard III", "history"),
    "THE TRAGEDY OF ROMEO AND JULIET": ("romeo-and-juliet", "Romeo and Juliet", "tragedy"),
    "THE TAMING OF THE SHREW": ("the-taming-of-the-shrew", "The Taming of the Shrew", "comedy"),
    "THE TEMPEST": ("the-tempest", "The Tempest", "romance"),
    "THE LIFE OF TIMON OF ATHENS": ("timon-of-athens", "Timon of Athens", "tragedy"),
    "THE TRAGEDY OF TITUS ANDRONICUS": ("titus-andronicus", "Titus Andronicus", "tragedy"),
    "TROILUS AND CRESSIDA": ("troilus-and-cressida", "Troilus and Cressida", "tragedy"),
    "TWELFTH NIGHT; OR, WHAT YOU WILL": ("twelfth-night", "Twelfth Night", "comedy"),
    "THE TWO GENTLEMEN OF VERONA": ("the-two-gentlemen-of-verona", "The Two Gentlemen of Verona", "comedy"),
    "THE TWO NOBLE KINSMEN": ("the-two-noble-kinsmen", "The Two Noble Kinsmen", "romance"),
    "THE WINTER’S TALE": ("the-winters-tale", "The Winter’s Tale", "romance"),
}

ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}
ACT = re.compile(r"^ACT ([IVXL]+)\.?(\s.*)?$")
SCENE = re.compile(r"^(?:SCENE|Scene) ([IVXL]+)\.?\s*(.*)$")
DIVISION = re.compile(r"^(PROLOGUE|EPILOGUE|INDUCTION|CHORUS)\.?$")
SPEAKER = re.compile(r"^([A-Z][A-Z0-9’'\-,&. ]*[A-Z0-9’])\.$")
DIRECTION_WORD = re.compile(r"^(Enter|Re-enter|Exit|Exeunt|Flourish|Alarum|Sennet|Thunder|Music)\b")
BRACKET = re.compile(r"\[_?(.+?)_?\]")
PERSONA = re.compile(r"^([A-Z][A-Z’'\-]+(?: [A-Z’'\-]+)*)\b[,.]?\s*(.*)$")
CONTENTS_SCENE = re.compile(r"^\s*Scene [IVXL]+\.", re.I)


def roman(numeral: str) -> int:
    total = 0
    for a, b in zip(numeral, numeral[1:] + " "):
        value = ROMAN[a]
        total += -value if b != " " and ROMAN.get(b, 0) > value else value
    return total


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower().replace("’", "").replace("'", "")).strip("-")


def clean_direction(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("_", "")).strip().strip("[]").strip()


@dataclass
class ParseReport:
    play_id: str
    scenes_found: int = 0
    scenes_in_contents: int | None = None  # None when the play has no contents list
    warnings: list[str] = field(default_factory=list)  # likely parse errors
    notes: list[str] = field(default_factory=list)  # handled oddities, for review

    @property
    def ok(self) -> bool:
        return not self.warnings


def split_works(body: str) -> list[tuple[str, str]]:
    """(title, text) for every play in the edition, in order."""
    lines = body.split("\n")
    contents_at = next(i for i, line in enumerate(lines) if line.strip() == "Contents")
    titles: list[str] = []
    i = contents_at + 1
    while i < len(lines) and (not lines[i].strip() or not titles or lines[i].startswith("    ")):
        if lines[i].strip():
            titles.append(lines[i].strip())
        i += 1
        if titles and not lines[i - 1].strip() and not lines[i].strip():
            break
    starts: list[tuple[int, str]] = []
    cursor = i
    for title in titles:
        at = next(j for j in range(cursor, len(lines)) if lines[j].strip() == title and not lines[j].startswith(" "))
        starts.append((at, title))
        cursor = at + 1
    works = []
    for n, (at, title) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        if title in PLAYS:
            works.append((title, "\n".join(lines[at:end])))
    return works


def parse_play(title: str, text: str, source: Source) -> tuple[Play, ParseReport]:
    play_id, display_title, genre = PLAYS[title]
    report = ParseReport(play_id)
    lines = text.replace("\r\n", "\n").split("\n")

    # The play's own contents list says how many scenes to expect. A few plays have no
    # contents and no "Dramatis Personæ" heading: the cast list follows the title.
    personae_at = next((i for i, line in enumerate(lines) if line.strip().startswith("Dramatis Person")), 0)
    listed = sum(1 for line in lines[:personae_at] if CONTENTS_SCENE.match(line))
    report.scenes_in_contents = listed or None

    body_at = next(i for i in range(personae_at + 1, len(lines)) if _is_heading(lines, i))
    # In a few places the next work's contents list comes before its title, so it ends
    # up at the bottom of this one. Cut it off.
    trailing = next((i for i in range(body_at, len(lines)) if lines[i].strip() == "Contents"), None)
    if trailing is not None:
        lines = lines[:trailing]
    characters = _parse_personae(lines[personae_at + 1 : body_at])

    builder = _Builder(play_id, characters, report)
    i = body_at
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        next_blank = i + 1 >= len(lines) or not lines[i + 1].strip()

        if not line:
            builder.blank()
        elif m := ACT.match(line):
            builder.act(roman(m.group(1)))
        elif m := SCENE.match(line):
            builder.scene(roman(m.group(1)), line.split(".")[0] + ".", m.group(2) or None)
        elif (m := DIVISION.match(line)) and next_blank:
            builder.division(m.group(1).lower(), m.group(1))
        elif "[" in line and "]" not in line and "[_" in line:
            # A bracketed direction that wraps onto following lines.
            joined = line
            while "]" not in joined and i + 1 < len(lines):
                i += 1
                joined += " " + lines[i].strip()
            builder.text(joined)
        elif raw.startswith(" ") and not raw.startswith("  ") and not builder.awaiting_first_line:
            # One leading space: a stage direction. It may wrap onto more indented lines.
            parts = [line]
            while i + 1 < len(lines) and lines[i + 1].startswith(" ") and not lines[i + 1].startswith("  ") and lines[i + 1].strip():
                i += 1
                parts.append(lines[i].strip())
            builder.direction(" ".join(parts))
        elif (m := SPEAKER.match(line)) and not next_blank:
            builder.speech(m.group(1))
        elif DIRECTION_WORD.match(line) and builder.after_blank:
            # An unindented direction paragraph ("Enter Leonato, Hero, Beatrice and others,
            # / with a Messenger."): some plays in this edition don't indent directions.
            parts = [line]
            while i + 1 < len(lines) and lines[i + 1].strip() and not SPEAKER.match(lines[i + 1].strip()):
                i += 1
                parts.append(lines[i].strip())
            builder.direction(" ".join(parts))
        else:
            builder.text(line)
        i += 1

    builder.finish()
    report.scenes_found = sum(1 for s in builder.scenes if s.division == "scene")
    if report.scenes_in_contents is not None and report.scenes_found != report.scenes_in_contents:
        report.warnings.append(
            f"found {report.scenes_found} scenes, contents lists {report.scenes_in_contents}"
        )
    play = Play(
        id=play_id,
        title=display_title,
        author=AUTHOR,
        genre=genre,  # type: ignore[arg-type]
        source=source,
        characters=list(builder.characters.values()),
        scenes=builder.scenes,
    )
    return play, report


def _is_heading(lines: list[str], i: int) -> bool:
    line = lines[i].strip()
    next_blank = i + 1 >= len(lines) or not lines[i + 1].strip()
    return bool(ACT.match(line) or SCENE.match(line) or (DIVISION.match(line) and next_blank))


def _parse_personae(lines: list[str]) -> dict[str, Character]:
    characters: dict[str, Character] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("SCENE"):
            continue
        m = PERSONA.match(line)
        if not m or len(m.group(1)) < 2:
            continue
        name = m.group(1).strip()
        description = m.group(2).strip().rstrip(".").strip(", ") or None
        cid = slug(name)
        if cid and cid not in characters:
            characters[cid] = Character(id=cid, name=name, description=description, in_dramatis_personae=True)
    return characters


class _Builder:
    """Accumulates scenes, speeches and directions as lines arrive."""

    def __init__(self, play_id: str, characters: dict[str, Character], report: ParseReport):
        self.play_id = play_id
        self.characters = characters
        self.report = report
        self.scenes: list[Scene] = []
        self.current_act: int | None = None
        self.scene_obj: Scene | None = None
        self.speech_obj: Speech | None = None
        self.pending: list[str] = []  # directions not yet known to be inline or standalone
        self.after_blank = True

    @property
    def awaiting_first_line(self) -> bool:
        """Right after a speech heading: the next line is words, even if mis-indented."""
        return self.speech_obj is not None and not self.speech_obj.parts and not self.pending

    # --- structure -------------------------------------------------------------------
    def act(self, number: int) -> None:
        self._close_speech()
        self.current_act = number
        self.after_blank = False

    def scene(self, number: int, heading: str, location: str | None) -> None:
        self._close_scene()
        self.scene_obj = Scene(
            id=f"{self.play_id}/{self.current_act}/{number}",
            act=self.current_act,
            number=number,
            division="scene",
            heading=heading,
            location=location,
            blocks=[],
        )
        self.after_blank = False

    def division(self, kind: str, heading: str) -> None:
        self._close_scene()
        prefix = f"{self.play_id}/{self.current_act}" if self.current_act else self.play_id
        base = f"{prefix}/{kind}"
        existing = {s.id for s in self.scenes}
        sid, n = base, 2
        while sid in existing:
            sid, n = f"{base}-{n}", n + 1
        self.scene_obj = Scene(
            id=sid, act=self.current_act, number=None, division=kind, heading=heading, location=None, blocks=[]  # type: ignore[arg-type]
        )
        self.after_blank = False

    # --- content ---------------------------------------------------------------------
    def speech(self, label: str) -> None:
        self._close_speech()
        cid = slug(label)
        if cid not in self.characters:
            self.characters[cid] = Character(id=cid, name=label, in_dramatis_personae=False)
        self.speech_obj = Speech(speaker_ids=[cid], speaker_label=label, parts=[])
        self.after_blank = False

    def direction(self, text: str) -> None:
        self.pending.append(clean_direction(text))
        self.after_blank = False

    def text(self, line: str) -> None:
        directions = [clean_direction(d) for d in BRACKET.findall(line)]
        rest = BRACKET.sub("", line).strip()
        if self.speech_obj is None:
            self.pending.extend(directions)
            if not rest:
                pass
            elif self.scene_obj is not None and self.scene_obj.division != "scene" and self.scene_obj.location is None and not self.scene_obj.blocks:
                self.scene_obj.location = rest  # the line after INDUCTION: "Warkworth. Before the castle."
            elif not self.after_blank and self.pending:
                self.pending[-1] += " " + rest  # the paragraph continues
            else:
                # Unattributed text: an unindented direction ("Desdemona in bed asleep"),
                # or a song with no singer named. Kept, flagged for review.
                self.pending.append(rest)
                self.report.notes.append(f"{self._where()}: unattributed text kept as a direction: {rest[:50]!r}")
            self.after_blank = False
            return
        parts: list[SpeechPart] = [InlineDirection(text=d) for d in self.pending]
        self.pending = []
        # A bracket at the start of the line comes before the words; otherwise after.
        leading = line.lstrip().startswith("[")
        if leading:
            parts += [InlineDirection(text=d) for d in directions]
        if rest:
            parts.append(VerseLine(text=rest))
        if not leading:
            parts += [InlineDirection(text=d) for d in directions]
        self.speech_obj.parts.extend(parts)
        self.after_blank = False

    def blank(self) -> None:
        self.after_blank = True

    def finish(self) -> None:
        self._close_scene()

    # --- internals -------------------------------------------------------------------
    def _blocks(self) -> list[Block]:
        if self.scene_obj is None:
            # Content before an act's first scene heading: a chorus (Gower in Pericles).
            self.report.notes.append(f"act {self.current_act}: text before the first scene, kept as a chorus")
            self.scene_obj = Scene(
                id=f"{self.play_id}/{self.current_act}/chorus", act=self.current_act, number=None,
                division="chorus", heading="CHORUS", location=None, blocks=[],
            )
        assert self.scene_obj is not None
        return self.scene_obj.blocks

    def _close_speech(self) -> None:
        if self.speech_obj is not None:
            if not any(p.kind == "line" for p in self.speech_obj.parts):
                self.report.warnings.append(f"{self._where()}: empty speech by {self.speech_obj.speaker_label}")
            self._blocks().append(self.speech_obj)
            self.speech_obj = None
        if self.pending:
            blocks = self._blocks()
            blocks.extend(StageDirection(text=d) for d in self.pending)
            self.pending = []

    def _close_scene(self) -> None:
        self._close_speech()
        if self.scene_obj is not None:
            self.scenes.append(self.scene_obj)
            self.scene_obj = None

    def _where(self) -> str:
        return self.scene_obj.id if self.scene_obj else self.play_id
