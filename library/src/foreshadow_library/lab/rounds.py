"""Rounds: prepare one (challenger, passages, both renderings), and decide it from the votes."""

from __future__ import annotations

import random
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from ..render import SEED_PROMPT, language_model, model_name, render_passage
from ..repository import PlayRepository
from . import store
from .passages import Passage, sample
from .propose import preference_for_challenger, propose

ITEMS_PER_ROUND = 5
# The challenger takes over when it wins most passages, and by a real margin.
PROMOTE_WIN_SHARE = 0.6
PROMOTE_MEAN_PREFERENCE = 0.15

Progress = Callable[[str], None]


def champion() -> store.Prompt:
    state = store.state()
    if state is None:
        seed = store.Prompt(id="v1", task=store.TASK, text=SEED_PROMPT, origin="seed", created_at=store.now())
        store.save_prompt(seed)
        store.save_state(store.State(champion=seed.id))
        return seed
    return store.prompt(state.champion)


def current_round() -> store.Round | None:
    all_rounds = store.rounds()
    return all_rounds[-1] if all_rounds else None


def prepare(
    repo: PlayRepository, progress: Progress = print, guidance: str = "", items_wanted: int = ITEMS_PER_ROUND
) -> store.Round:
    """Write a challenger, pick fresh passages, and render each with both prompts."""
    lm = language_model()
    champ = champion()
    progress(f"Writing a challenger to beat {champ.id}…")
    challenger = propose(champ, lm, guidance)

    number = len(store.rounds()) + 1
    used = {f"{i.scene_id}#{i.start}-{i.end}" for r in store.rounds() for i in r.items}
    passages = sample(repo, items_wanted + 4, seed=number, used=used)
    progress(f"Rendering {len(passages)} passages with {champ.id} and {challenger.id}…")

    rng = random.Random(number)

    def build(passage: Passage) -> store.Item | None:
        try:
            versions = {
                p.id: render_passage(passage.play, passage.scene, passage.start, passage.end, prompt=p.text, lm=lm)
                for p in (champ, challenger)
            }
        except Exception as error:  # a failed rendering just drops the passage
            progress(f"  skipped {passage.where}: {type(error).__name__}")
            return None
        if any(out_of_step(passage, v) for v in versions.values()):
            progress(f"  skipped {passage.where}: a rendering was out of step with the original")
            return None
        first, second = (champ.id, challenger.id) if rng.random() < 0.5 else (challenger.id, champ.id)
        return store.Item(
            id=passage.key,
            play_title=passage.play.title,
            scene_id=passage.scene.id,
            where=passage.where,
            start=passage.start,
            end=passage.end,
            original=[
                store.OriginalBlock(
                    speaker=b.speaker_label if b.kind == "speech" else None,
                    parts=[p.model_dump() for p in b.parts] if b.kind == "speech" else [{"kind": "direction", "text": b.text}],
                )
                for b in passage.scene.blocks[passage.start : passage.end]
            ],
            a=store.Version(prompt_id=first, blocks=versions[first]),
            b=store.Version(prompt_id=second, blocks=versions[second]),
        )

    with ThreadPoolExecutor(max_workers=6) as pool:
        items = [item for item in pool.map(build, passages) if item is not None][:items_wanted]

    rnd = store.Round(
        number=number,
        task=store.TASK,
        champion=champ.id,
        challenger=challenger.id,
        model=model_name(),
        created_at=store.now(),
        items=items,
    )
    store.save_round(rnd)
    progress(f"Round {number} is ready: {len(items)} passages.")
    return rnd


def out_of_step(passage: Passage, blocks) -> bool:
    return [b.source_block for b in blocks] != list(range(passage.start, passage.end))


def decide(rnd: store.Round) -> store.Outcome:
    """Tally the votes; promote the challenger if it clearly won."""
    votes = store.votes(rnd.number)
    cast = [votes[(rnd.number, item.id)] for item in rnd.items if (rnd.number, item.id) in votes]
    if len(cast) < len(rnd.items):
        raise ValueError(f"{len(rnd.items) - len(cast)} passages still need a vote")
    # A passage where both versions were rejected is a win for nobody: it counts against
    # the challenger's share, so a challenger can't be promoted on a few passages alone.
    preferences = [preference_for_challenger(rnd, item, votes[(rnd.number, item.id)]) for item in rnd.items]
    wins = sum(1 for p in preferences if p > 0)
    losses = sum(1 for p in preferences if p < 0)
    mean = sum(preferences) / len(preferences)
    promoted = wins >= PROMOTE_WIN_SHARE * len(preferences) and mean >= PROMOTE_MEAN_PREFERENCE
    rnd.outcome = store.Outcome(
        decided_at=store.now(),
        challenger_wins=wins,
        champion_wins=losses,
        both_rejected=sum(1 for v in cast if v.reject_both),
        mean_preference=round(mean, 3),
        promoted=promoted,
    )
    store.save_round(rnd)
    if promoted:
        store.save_state(store.State(champion=rnd.challenger))
    return rnd.outcome
