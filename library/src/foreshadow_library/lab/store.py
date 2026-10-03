"""What the lab keeps on disk, under library/lab/. All of it is committed: the votes are
the project's most valuable data."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from ..domain import RenderedBlock

ROOT = Path(__file__).resolve().parents[3]  # library/
# Tests point this somewhere else so they never touch the real votes.
LAB = Path(os.environ.get("FORESHADOW_LAB_DIR", ROOT / "lab"))
TASK = "todays-english"


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class Prompt(BaseModel):
    id: str  # "v1", "v2", …
    task: str
    text: str
    origin: Literal["seed", "proposed"]
    parent: str | None = None  # the champion it was written to beat
    rationale: str | None = None  # why the proposer thinks it is better
    created_at: str


class OriginalBlock(BaseModel):
    speaker: str | None  # None for a stage direction
    parts: list[dict]  # {"kind": "line" | "direction", "text": …}


class Version(BaseModel):
    prompt_id: str
    blocks: list[RenderedBlock]


class Item(BaseModel):
    id: str
    play_title: str
    scene_id: str
    where: str  # "Macbeth 1.7"
    start: int
    end: int
    original: list[OriginalBlock]
    a: Version  # which prompt is A and which is B is shuffled per item
    b: Version


class Outcome(BaseModel):
    decided_at: str
    challenger_wins: int
    champion_wins: int
    both_rejected: int = 0  # passages where the owner rejected both versions
    mean_preference: float  # −1 (champion, strongly) … +1 (challenger, strongly)
    promoted: bool


class Round(BaseModel):
    number: int
    task: str
    champion: str
    challenger: str
    model: str
    created_at: str
    items: list[Item]
    outcome: Outcome | None = None


class Vote(BaseModel):
    round: int
    item: str
    score: int | None  # 0 = A by a long way … 7 = B by a long way; None when both are rejected
    reject_both: bool = False  # neither version is good enough
    note: str  # the owner's reason: required with every vote
    at: str


class State(BaseModel):
    champion: str


# --- prompts ---------------------------------------------------------------------------
def _prompt_dir() -> Path:
    return LAB / "prompts" / TASK


def prompts() -> list[Prompt]:
    files = sorted(_prompt_dir().glob("*.json"), key=lambda p: int(p.stem[1:]))
    return [Prompt.model_validate_json(f.read_text(encoding="utf-8")) for f in files]


def prompt(prompt_id: str) -> Prompt:
    return Prompt.model_validate_json((_prompt_dir() / f"{prompt_id}.json").read_text(encoding="utf-8"))


def save_prompt(p: Prompt) -> None:
    _write(_prompt_dir() / f"{p.id}.json", p.model_dump_json(indent=1))


def next_prompt_id() -> str:
    return f"v{len(prompts()) + 1}"


# --- state -----------------------------------------------------------------------------
def state() -> State | None:
    path = LAB / "state.json"
    return State.model_validate_json(path.read_text(encoding="utf-8")) if path.exists() else None


def save_state(s: State) -> None:
    _write(LAB / "state.json", s.model_dump_json(indent=1))


# --- rounds ----------------------------------------------------------------------------
def rounds() -> list[Round]:
    files = sorted((LAB / "rounds").glob(f"{TASK}-*.json"))
    return [Round.model_validate_json(f.read_text(encoding="utf-8")) for f in files]


def save_round(r: Round) -> None:
    _write(LAB / "rounds" / f"{TASK}-{r.number:03}.json", r.model_dump_json(indent=1))


# --- votes -----------------------------------------------------------------------------
def votes(round_number: int | None = None) -> dict[tuple[int, str], Vote]:
    """The latest vote for each (round, item): a later vote replaces an earlier one."""
    path = LAB / "votes.jsonl"
    latest: dict[tuple[int, str], Vote] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                v = Vote.model_validate_json(line)
                if round_number is None or v.round == round_number:
                    latest[(v.round, v.item)] = v
    return latest


def add_vote(v: Vote) -> None:
    path = LAB / "votes.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(v.model_dump(), ensure_ascii=False) + "\n")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")
