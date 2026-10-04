"""Find stretches of scenes that suit the show: two speakers, the host opening and closing.

Structure only: everything here is decided by code from the parsed text. Judgement (does
it stand alone, is there a want and a turn) comes after, on the stretches that pass.

A stretch is a maximal run of speeches by exactly two characters. For each of the two as
the host's character, the run is trimmed so that character speaks first and last. Hard
limits then drop the unusable; a score ranks the rest.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .analyse import WORD
from .domain import Candidate, CandidateMetrics, Play, Scene

CAST_CHANGE = re.compile(r"\b(Enter|Re-enter|Exit|Exeunt|Exits|Enters)\b")
SECOND_PERSON = re.compile(r"\b(you|your|yours|thou|thee|thy|thine|ye)\b", re.I)


# Running time is an estimate until real performances are logged: the host's words at a
# reading pace, plus the improviser's reply after each host speech.
HOST_WORDS_PER_MINUTE = 130
MINUTES_PER_IMPROVISED_REPLY = 0.3  # about 18 seconds
MONOLOGUE_WORDS = 100

# name → (shortest, target, longest) minutes
SIZES = {"small": (3.0, 5.0, 7.5), "medium": (7.5, 10.0, 15.0), "big": (15.0, 20.0, 30.0)}


@dataclass(frozen=True)
class Limits:
    """Hard limits. A stretch outside any of them is not a candidate.

    Long host speeches are allowed: a monologue gives the improviser a lot to play with.
    What is required is that the improviser still gets enough turns.
    """

    min_host_speeches: int = 6
    min_partner_speeches: int = 5
    min_minutes: float = 3.0
    max_minutes: float = 30.0
    min_host_share: float = 0.30
    max_host_share: float = 0.85
    max_cast_changes: int = 0


def minutes_of(host_words: int, partner_speeches: int) -> float:
    return host_words / HOST_WORDS_PER_MINUTE + partner_speeches * MINUTES_PER_IMPROVISED_REPLY


def size_of(minutes: float) -> str | None:
    for name, (low, _, high) in SIZES.items():
        if low <= minutes < high or (name == "big" and minutes == high):
            return name
    return None


def _speech_words(block) -> int:
    return sum(len(WORD.findall(p.text)) for p in block.parts if p.kind == "line")


def _speech_text(block) -> str:
    return " ".join(p.text for p in block.parts if p.kind == "line")


def _has_cast_change(block) -> bool:
    if block.kind == "direction":
        return bool(CAST_CHANGE.search(block.text))
    return any(p.kind == "direction" and CAST_CHANGE.search(p.text) for p in block.parts)


def two_speaker_runs(scene: Scene) -> list[tuple[int, int, tuple[str, str]]]:
    """Maximal (start, end, speakers) runs in which only two characters speak."""
    speeches = [(i, b.speaker_ids[0]) for i, b in enumerate(scene.blocks) if b.kind == "speech"]
    runs: list[tuple[int, int, tuple[str, str]]] = []
    n = 0
    while n < len(speeches):
        pair: list[str] = []
        m = n
        while m < len(speeches):
            speaker = speeches[m][1]
            if speaker not in pair:
                if len(pair) == 2:
                    break
                pair.append(speaker)
            m += 1
        if len(pair) == 2:
            runs.append((speeches[n][0], speeches[m - 1][0] + 1, (pair[0], pair[1])))
        # Start the next run at the last speech before the third speaker that belongs to
        # only one of the pair, so overlapping pairs (A–B then B–C) are both found.
        if m >= len(speeches):
            break
        back = m - 1
        last = speeches[back][1]
        while back > n and speeches[back - 1][1] == last:
            back -= 1
        n = back if back > n else m
    return runs


def _measure(play: Play, scene: Scene, start: int, end: int, host: str, partner: str) -> Candidate | None:
    """The stretch with its metrics, whatever its length (used to find shorter cuts)."""
    return _candidate(play, scene, start, end, host, partner, any_length=True)


def _candidate(
    play: Play, scene: Scene, start: int, end: int, host: str, partner: str, cut: bool = False, any_length: bool = False
) -> Candidate | None:
    names = {c.id: c.name for c in play.characters}
    host_blocks = [i for i in range(start, end) if scene.blocks[i].kind == "speech" and scene.blocks[i].speaker_ids[0] == host]
    if not host_blocks:
        return None
    start, end = host_blocks[0], host_blocks[-1] + 1  # the host opens and closes
    blocks = scene.blocks[start:end]
    host_speeches = [b for b in blocks if b.kind == "speech" and b.speaker_ids[0] == host]
    partner_speeches = [b for b in blocks if b.kind == "speech" and b.speaker_ids[0] == partner]
    host_counts = [_speech_words(b) for b in host_speeches]
    host_words, partner_words = sum(host_counts), sum(_speech_words(b) for b in partner_speeches)
    if not host_words or not partner_speeches:
        return None
    partner_name = names.get(partner, partner)
    # Match the partner's name as a spoken word: "Macbeth", not "LADY MACBETH" in full.
    name_words = [w for w in re.findall(r"[A-Za-z’']+", partner_name) if len(w) > 3]
    name_pattern = re.compile(r"\b(" + "|".join(re.escape(w) for w in name_words) + r")\b", re.I) if name_words else None
    texts = [_speech_text(b) for b in host_speeches]
    metrics = CandidateMetrics(
        host_speeches=len(host_speeches),
        partner_speeches=len(partner_speeches),
        host_words=host_words,
        partner_words=partner_words,
        host_share=round(host_words / (host_words + partner_words), 3),
        mean_host_words=round(host_words / len(host_speeches), 1),
        median_host_words=float(sorted(host_counts)[len(host_counts) // 2]),
        max_host_words=max(host_counts),
        monologues=sum(n > MONOLOGUE_WORDS for n in host_counts),
        minutes=round(minutes_of(host_words, len(partner_speeches)), 1),
        questions=round(sum("?" in t for t in texts) / len(texts), 3),
        address=round(sum(bool(SECOND_PERSON.search(t)) for t in texts) / len(texts), 3),
        names=sum(bool(name_pattern.search(t)) for t in texts) if name_pattern else 0,
        directions=sum(1 for b in blocks if b.kind == "direction") + sum(1 for b in blocks if b.kind == "speech" for p in b.parts if p.kind == "direction"),
        cast_changes=sum(_has_cast_change(b) for b in blocks),
    )
    size = size_of(metrics.minutes)
    if size is None:
        if not any_length:
            return None
        size = "big"
    score, reasons = score_of(metrics)
    return Candidate(
        id=f"{scene.id}#{start}-{end}@{host}",
        play_id=play.id,
        play_title=play.title,
        genre=play.genre,
        scene_id=scene.id,
        start=start,
        end=end,
        host=host,
        host_name=names.get(host, host),
        partner=partner,
        partner_name=partner_name,
        first_line=texts[0][:160],
        last_line=texts[-1][:160],
        metrics=metrics,
        size=size,  # type: ignore[arg-type]
        cut=cut,
        score=score,
        reasons=reasons,
    )


def passes(m: CandidateMetrics, limits: Limits) -> bool:
    return (
        m.host_speeches >= limits.min_host_speeches
        and m.partner_speeches >= limits.min_partner_speeches
        and limits.min_minutes <= m.minutes <= limits.max_minutes
        and limits.min_host_share <= m.host_share <= limits.max_host_share
        and m.cast_changes <= limits.max_cast_changes
    )


def score_of(m: CandidateMetrics) -> tuple[float, list[str]]:
    """0–100. Each part is a plain idea about what helps the improviser and the host."""
    exchanges = min(m.host_speeches, m.partner_speeches)
    parts = {
        "back-and-forth": 30 * min(exchanges, 14) / 14,  # many turns for the improviser
        "speaks to the partner": 20 * m.address,  # lines aimed at them, not at the air
        "asks questions": 15 * min(m.questions, 0.5) / 0.5,  # hands them the scene
        "says their name": 10 * min(m.names, 3) / 3,  # tells them who they are
        # The typical host line is easy to sight-read; a monologue or two doesn't count against it.
        "readable lines": 15 * max(0.0, 1 - max(0.0, m.median_host_words - 12) / 40),
        "host carries it": 10 * max(0.0, 1 - abs(m.host_share - 0.55) / 0.25),  # the script holds the story
    }
    reasons = [f"{name}: {value:.0f}" for name, value in parts.items()]
    return round(sum(parts.values()), 1), reasons


def pieces(scene: Scene, start: int, end: int) -> list[tuple[int, int]]:
    """Cut a run at every entrance or exit: what remains between the cuts is judged piece by
    piece, so the good stretch inside a famous scene isn't lost to the messenger who
    interrupts it."""
    out: list[tuple[int, int]] = []
    piece_start: int | None = None
    for i in range(start, end):
        if _has_cast_change(scene.blocks[i]):
            if piece_start is not None:
                out.append((piece_start, i))
            piece_start = None
        elif piece_start is None:
            piece_start = i
    if piece_start is not None:
        out.append((piece_start, end))
    return out


def shorter_cuts(scene: Scene, full: Candidate) -> list[int]:
    """Block indexes at which a long stretch could end early to make a smaller size: the
    host speech where the running time is closest to each smaller size's target."""
    ends: list[int] = []
    words = replies = 0
    timeline: list[tuple[int, float]] = []  # (end index after a host speech, minutes so far)
    for i in range(full.start, full.end):
        block = scene.blocks[i]
        if block.kind != "speech":
            continue
        if block.speaker_ids[0] == full.host:
            words += _speech_words(block)
            timeline.append((i + 1, minutes_of(words, replies)))
        else:
            replies += 1
    for name, (low, target, high) in SIZES.items():
        if full.metrics.minutes < high:  # the full stretch is already this size or smaller
            break
        inside = [(abs(m - target), e) for e, m in timeline if low <= m < high]
        if inside:
            ends.append(min(inside)[1])
    return ends


def find(plays: list[Play], limits: Limits = Limits()) -> tuple[list[Candidate], dict[str, int]]:
    """Every candidate that passes the limits, best first, and how many fell at each stage."""
    counts = {"scenes": 0, "two_speaker_runs": 0, "pieces": 0, "passed": 0}
    found: dict[str, Candidate] = {}
    for play in plays:
        for scene in play.scenes:
            counts["scenes"] += 1
            for start, end, (x, y) in two_speaker_runs(scene):
                counts["two_speaker_runs"] += 1
                for piece_start, piece_end in pieces(scene, start, end):
                    for host, partner in ((x, y), (y, x)):
                        counts["pieces"] += 1
                        # Measure the whole piece first (it may be longer than any size), then
                        # offer it at every size it can fill.
                        ends = [piece_end]
                        whole = _measure(play, scene, piece_start, piece_end, host, partner)
                        if whole is not None:
                            ends += shorter_cuts(scene, whole)
                        for n, cut_end in enumerate(ends):
                            c = _candidate(play, scene, piece_start, cut_end, host, partner, cut=n > 0)
                            if c is not None and passes(c.metrics, limits):
                                found[c.id] = c
    out = sorted(found.values(), key=lambda c: -c.score)
    counts["passed"] = len(out)
    return out, counts
