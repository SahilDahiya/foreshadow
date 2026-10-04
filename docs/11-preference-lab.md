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

## Where DSPy's optimisers come in (researched October 2026, DSPy 3.4)

**Today the lab uses DSPy to run the prompts, not to optimise them.** The
champion-and-challenger loop is hand-written: one AI call writes a challenger from the
votes. That is a stopgap for the first few rounds, while votes are scarce.

DSPy's optimisers need a metric they can call hundreds of times, which a person can't be.
What the research shows is the standard way round that, and it is the Level 2 plan above:

| Step | DSPy optimiser | What it uses | Needs |
|---|---|---|---|
| **1. Examples the owner liked** | `LabeledFewShot` / `KNNFewShot` | Every vote yields (original, preferred rendering); the best become examples shown to the renderer | Usable from about 10 votes |
| **2. A judge that votes like the owner** | `GEPA` on a judge program | Votes as labels, **the owner's reasons as GEPA's feedback text** | 30–50 votes, some held back for testing |
| **3. Optimise the renderer** | `GEPA` on `RenderPassage` | The judge as the metric (score plus feedback), passages from the library as training data | No more votes; hundreds of AI calls |
| **4. Confirm with the owner** | the lab | Champion against GEPA's best, voted blind | One round |

What the research found:

- **GEPA** evolves instructions by reflection: a strong model reads failed examples plus
  written feedback from the metric and rewrites the instruction. It keeps a *Pareto
  frontier*: prompts that are best on different kinds of example, not one overall winner.
  That suits this task, where one prompt wins on comic prose and another on formal verse.
  It is still marked experimental in DSPy.
- **Aligning a judge with human labels is established practice.** Dropbox tuned its
  relevance judge with GEPA and MIPROv2 against human scores and explanations; MLflow
  ships a GEPA "alignment optimizer" for judges, which asks for at least 10 labelled
  examples and strongly recommends a written rationale with each. The lab's required
  reason is exactly that data.
- **Known pitfalls:** the optimiser copies specifics from examples into the prompt instead
  of generalising (guard against it in the instructions and check on held-back votes),
  and it can quietly change the task (keep the fixed rules checked by code).
- **Other optimisers:** `MIPROv2` tunes instructions and examples together but wants 50–200+
  examples; `InferRules` turns examples into explicit rules, which may suit "what the owner
  likes"; `BootstrapFinetune` trains model weights and doesn't apply to Claude.

So the reason attached to each vote matters twice: it guides the next challenger now, and
it becomes the feedback GEPA learns from later. A reason of "idk" teaches neither.

Sources: [DSPy GEPA overview](https://dspy.ai/current/getting-started/gepa-optimization/),
[Dropbox: optimising a relevance judge with DSPy](https://dropbox.tech/machine-learning/optimizing-dropbox-dash-relevance-judge-with-dspy),
[MLflow GEPA alignment optimizer](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/gepa/),
[GEPA paper](https://arxiv.org/abs/2507.19457).

## Optimising after every round (decided)

**Decided:** optimisation starts now and runs after each feedback round, rather than
waiting for dozens of votes.

Proposed loop, replacing the hand-written challenger:

```
votes in ──▶ refit the judge on every vote so far ──▶ GEPA improves the prompt against
   ▲          (the owner's votes and reasons as its       the judge, on fresh passages
   │           examples; tested on held-back votes)              │
   └────────── owner votes: champion vs GEPA's best ◀────────────┘
```

- **The judge starts weak and improves.** With a handful of votes it is mostly the owner's
  reasons read back; each round adds five more. Its agreement with the owner on held-back
  votes is reported every round, so its reliability is visible.
- **The owner stays the final check.** GEPA's best prompt is only ever a challenger; it
  becomes champion when the owner prefers it in a blind round. A wrong judge costs a
  wasted round, never a bad champion.
- **Cost and time per optimisation** are set by a budget (the number of renderings GEPA may
  try). An early estimate, not yet measured: a small run is a few dollars and a few
  minutes.

## The two things to test first (decided)

### 1. Language transformation: Shakespeare's English to today's

One variable per experiment, so a vote answers a question:

| Question | A | B |
|---|---|---|
| How literal? | Close to the original's wording | Free: what a person would say now |
| Imagery | Keep every image | Keep only images that still land |
| Famous lines | As Shakespeare wrote them | Modernised like the rest |
| Line breaks | Short breath-lines | Fuller sentences |
| Status and register | Everyone speaks alike | Kings formal, servants casual |
| Wordplay | Explain the pun's meaning | Replace it with a joke that works today |
| Verse | Plain prose | A hint of rhythm kept |
| Model | The strongest | A cheaper, faster one |

Also tested, less often: a **whole scene**, since passages can't show whether voices stay
consistent from start to finish.

### 2. World transformation: the play in a world of today

Two things are tested separately:

**The world mapping** (who and what becomes what): the owner sees a play's cast and two
mapping tables, and votes.

**The passage in that world**: the original, the mapping, and two renderings.

| Question | A | B |
|---|---|---|
| Names | Keep Macbeth, Lady Macbeth | Modern names |
| Events | Literal: the king is murdered | Modern equivalent: a boardroom coup |
| Depth | Light: titles and places change | Deep: the world's own jargon, objects, habits |
| Recognition | Stays close to the original's lines | Rewritten freely inside the new world |
| Which world | A tech company | A government, a parliament, others |

The phone rule ([05](05-scene-writing.md)) is checked by code in every modern world.

### Two kinds of round

- **Question rounds** settle a design choice: A and B differ in exactly one deliberate way
  from the tables above. The answer becomes a rule in the prompt.
- **Optimisation rounds** improve the prompt within the rules: the champion against GEPA's
  best.

Open design questions (names, literal events, which worlds; see
[open-questions.md](open-questions.md)) become question rounds, decided by votes rather
than by argument.

## Built: the language evaluation and the first hill-climb

Alongside the lab there is now an automatic evaluation for the language transformation,
used to hill-climb the prompt without the owner's votes (the owner's choice, for now).

- **40 passages** from 40 two-person scenes in 23 plays: twelve chosen deliberately, 28
  drawn at random across genres. 20 are *train* (read when proposing changes), 20 are
  *test* (never read; the headline score). Listed in `.claude/hillclimb/language/inputs.md`.
- **Scoring:** code checks, then Claude Sonnet 5.5 compares each rendering, blind, with a
  frozen rendering from the starting prompt, on five criteria (faithful, speakable,
  natural, alive, voice) plus an overall preference. Definitions: `metrics.md` there.
- **Runner:** `uv run python -m foreshadow_library.evals.run --variant <baseline|vN>`. It
  refuses to run if the scoring code changed since the owner last approved it.
- **Each round:** a fresh analyser reads only the train results and proposes one change;
  it is kept only if the test score improves beyond noise. The record is `narrative.md`
  and `report.html` in the same folder.

**First climb (three rounds, about $10):** the winner separates *what is said* (fixed,
phrase for phrase) from *how it is said* (rebuilt from the meaning as speech). The judge
preferred it to the starting prompt in 75% of held-out comparisons (preference 0.50 →
0.63, +0.125 ± 0.097): more faithful, more speakable, more alive, and less natural. Two
other changes were tried and reverted. The remaining gains are about the size of the
eval's noise at this size.

**The winner is a challenger, not the champion.** It entered the lab as prompt v3 for the
owner's blind vote, because the judge's taste is not the owner's: the judge rewards
closeness to the original, while the owner's own notes favoured vivid, playable lines.

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
