"""Write a challenger prompt from the owner's votes and notes."""

from __future__ import annotations

import dspy

from . import store

# Used once, before there are any votes, from the first rendering reviewed in conversation.
FIRST_GUIDANCE = (
    "The first rendering (Macbeth 1.7) was faithful and speakable, but too literal in "
    "places. Lines such as \"Bear only boy children\" and \"letting 'I don't dare' follow "
    "'I want to', like the poor cat in the proverb\" are accurate, but nobody talks like "
    "that. Try a version that sounds like people speak today, while keeping the story, the "
    "images that matter and the heat."
)


class ProposePrompt(dspy.Signature):
    """You are improving the instruction given to a model that renders passages of classic
    plays into today's English for a live show: an actor sight-reads one character's lines
    aloud from a phone while the audience follows the text on a screen.

    One person, the show's owner, judges the results. They compare two renderings of the
    same passage, made with two different instructions, and vote from 0 to 7 on which they
    prefer. You are given the instruction that is currently best (the champion), and the
    evidence so far: for each passage, the original, the champion's rendering, the
    challenger's rendering, how strongly the owner preferred one, and the reason they gave.
    The owner can also reject both renderings when neither is good enough; those passages
    matter most, because they show where the champion and the challenger fail together.

    Work out what this owner values: read their reasons closely, and look at what the
    renderings they preferred have in common and what the ones they rejected share. Then
    write a new, complete instruction that would produce renderings this owner prefers
    more often than the champion's.

    The new instruction must keep the fixed rules of the task, because code checks them
    and the show depends on them: every original block is answered by exactly one block
    with the same number; speeches stay speeches by the same speaker and stage directions
    stay stage directions; nothing is added or dropped; names, places, period and events
    are unchanged; each speech is broken into short lines an actor can deliver in one
    breath; and no phones, screens, apps, emails or text messages are ever mentioned.

    Write the instruction as you would brief a skilled translator: explain the situation
    and what good looks like and why, in plain prose. Describe the qualities wanted
    rather than quoting lines from the evidence, so the instruction works for any passage
    of any play, not only the ones seen here."""

    champion_instruction: str = dspy.InputField()
    guidance: str = dspy.InputField(desc="what the owner has said they want, in their own words or as observed")
    evidence: str = dspy.InputField(desc="votes on earlier passages, most recent round first; may be empty")
    rationale: str = dspy.OutputField(desc="what the owner seems to value and what the new instruction changes: three or four plain sentences, no lists or markdown")
    new_instruction: str = dspy.OutputField(desc="the complete new instruction, ready to use as it is")


def _render_text(blocks, original) -> str:
    out = []
    for block in blocks:
        speaker = original[block.source_block] if block.source_block in original else "?"
        text = " / ".join(p.text if p.kind == "line" else f"({p.text})" for p in block.parts)
        out.append(f"{speaker}: {text}")
    return "\n".join(out)


def evidence(max_rounds: int = 3) -> str:
    """The owner's votes as text, un-blinded: champion against challenger."""
    sections: list[str] = []
    for rnd in reversed(store.rounds()[-max_rounds:]):
        votes = store.votes(rnd.number)
        for item in rnd.items:
            vote = votes.get((rnd.number, item.id))
            if vote is None:
                continue
            speakers = {
                item.start + i: (o.speaker or "STAGE DIRECTION") for i, o in enumerate(item.original)
            }
            original = "\n".join(
                f"{o.speaker or 'STAGE DIRECTION'}: " + " / ".join(p["text"] for p in o.parts) for o in item.original
            )
            champion, challenger = (item.a, item.b) if item.a.prompt_id == rnd.champion else (item.b, item.a)
            if vote.reject_both:
                verdict = "rejected both renderings: neither is good enough"
            else:
                preference = preference_for_challenger(rnd, item, vote)
                verdict = (
                    f"preferred the {'challenger' if preference > 0 else 'champion'} "
                    f"({abs(preference):.0%} of the way to 'by a long way')"
                )
            sections.append(
                f"--- Round {rnd.number}, {item.where}\n"
                f"ORIGINAL\n{original}\n\n"
                f"CHAMPION ({rnd.champion})\n{_render_text(champion.blocks, speakers)}\n\n"
                f"CHALLENGER ({rnd.challenger})\n{_render_text(challenger.blocks, speakers)}\n\n"
                f'The owner {verdict}. Their reason: "{vote.note}"'
            )
    return "\n\n".join(sections)


def preference_for_challenger(rnd: store.Round, item: store.Item, vote: store.Vote) -> float:
    """−1 (champion, by a long way) … +1 (challenger, by a long way); 0 when both are rejected."""
    if vote.reject_both or vote.score is None:
        return 0.0
    toward_b = (vote.score - 3.5) / 3.5
    return toward_b if item.b.prompt_id == rnd.challenger else -toward_b


def propose(champion: store.Prompt, lm: dspy.LM, guidance: str = "") -> store.Prompt:
    seen = evidence()
    with dspy.context(lm=lm):
        result = dspy.Predict(ProposePrompt)(
            champion_instruction=champion.text,
            guidance=guidance or (FIRST_GUIDANCE if not seen else "No guidance beyond the votes and notes."),
            evidence=seen or "No votes yet.",
        )
    new = store.Prompt(
        id=store.next_prompt_id(),
        task=store.TASK,
        text=result.new_instruction.strip(),
        origin="proposed",
        parent=champion.id,
        rationale=result.rationale.strip(),
        created_at=store.now(),
    )
    store.save_prompt(new)
    return new
