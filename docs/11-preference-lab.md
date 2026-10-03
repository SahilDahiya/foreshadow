# 11 — The preference lab: improving prompts with the owner's votes

**Decided:** prompts are improved by A/B testing with the owner as the judge, using DSPy.
The owner sees two versions and votes from 0 to 7: **0 means "I strongly prefer A",
7 means "I strongly prefer B"**, and everything in between is a matter of degree. This is
reinforcement learning from human feedback in spirit: human preferences shape what the AI
produces.

Everything below is **proposed** unless marked otherwise.

## The scale

| Vote | Meaning |
|---|---|
| 0 | A, by a long way |
| 1–2 | A, clearly / somewhat |
| 3 | A, slightly |
| 4 | B, slightly |
| 5–6 | B, somewhat / clearly |
| 7 | B, by a long way |

Eight points with no middle: every vote leans one way, so there are no ties.

**Every vote needs a reason (decided).** The owner justifies each vote in a sentence ("B
sounds like a real person; A is still stiff"). The reason is worth more than the number,
because it tells the AI *why*.

**Both can be rejected (decided).** When neither version is good enough, the owner rejects
both, again with a reason. A rejected passage is a win for nobody; it counts against the
challenger's share, so a challenger can't be promoted on a handful of passages. Rejections
are the most useful evidence for the next challenger, because they show what neither
prompt gets right yet.

## What a vote looks at

- **The original passage** on top, then **version A** and **version B** below it.
- **Blind and shuffled.** Which prompt produced A and which produced B is random per item
  and hidden, so the owner can't favour a known version or a side.
- **Short passages**, a handful of speeches each, not whole scenes: quick to judge, and
  cheap to render twice.
- **Spread across the canon**: comic and tragic, short replies and long speeches, different
  characters, so a prompt can't win by suiting one kind of line.

## Two levels, the same shape as RLHF

```
Level 1                                   Level 2
owner votes ──▶ pick the better prompt    owner votes ──▶ train a judge that votes like the owner
     ▲                    │                                      │
     └── new challenger ◀─┘                judge scores thousands of renderings ──▶ DSPy optimises
         written from the votes                                  the prompt against the judge
         and notes
```

### Level 1: champion and challenger (start here)

1. The current best prompt is the **champion**.
2. A **challenger** is written by an AI that reads the owner's votes and notes from earlier
   rounds and proposes a better instruction.
3. Both render the same ten or so passages; the owner votes.
4. Each vote becomes a preference for the challenger between −1 and +1. If the challenger
   wins clearly (most passages, and by a real margin), it becomes the champion.
5. Repeat. About ten votes a round, a few minutes each.

### Level 2: a judge that votes like the owner

DSPy's optimisers need hundreds of scored examples, far more than a person can vote on.
So the votes are used to build a **judge**: a DSPy program that reads the original and two
versions and predicts the owner's 0–7 vote.

- The judge is itself optimised with DSPy against the owner's real votes.
- It is trusted only once it sides with the owner on votes it has never seen (target: at
  least 8 in 10).
- Then DSPy (GEPA) optimises the rendering prompt against the judge at scale, and the
  owner keeps voting on samples so the judge stays honest.

In RLHF terms: the owner's votes are the human feedback, the judge is the reward model,
and the rendering prompt is the policy.

## What it applies to

First the today's-English renditions ([10](10-play-library.md)). The same lab then serves
every other AI step: world mappings, twists, and later generated scenes. It can also
compare **models** instead of prompts (is Opus worth it over Sonnet for this?), with the
same votes.

## Data

Every vote is kept: the passage, both versions, which prompt and model made each, the
vote or rejection, the reason, and when. The votes are the project's most valuable data, so they are
committed to the repository.

## Built: level 1

`uv run library lab` (in `library/`) opens the voting page on the owner's own computer. It
is a local tool, separate from the app.

- **A round** is ten passages. Each is rendered by the champion and the challenger, shown as
  A and B in a random, hidden order beside the original.
- **Voting:** write the reason first (required), then click 0–7 or press the number key, or
  reject both (`x`). Arrow keys move between passages; votes can be changed until the
  round is decided.
- **The result** shows how often the challenger was preferred, how often both were rejected,
  reveals which side was which, and explains what the challenger was trying. The challenger becomes champion if
  it won at least 6 in 10 passages and by a real margin.
- **The next round** starts from the result page. An optional box takes guidance in the
  owner's own words; the AI writes the new challenger from that plus every vote and note.
- **Data** lives in `library/lab/`: `prompts/`, `rounds/`, `votes.jsonl`, `state.json`.
- `library render <scene>` always uses the current champion.

Level 2 (the judge) comes once there are enough votes to train and test it: a few rounds.

## Verified

DSPy 3.4 runs against Claude Opus 5.5 (sampling temperature left unset, as that model
requires).
