# 06 — AI pipeline and optimisation

**Decided:** the AI part has two phases, **collecting information** (an adaptive survey)
and **writing the scene**, with **determining the play** somewhere in between. They need
not run strictly in that order. **DSPy** is used to optimise the prompts.

Everything below is **proposed** unless marked otherwise.

## DSPy in brief (as of DSPy 3.3, August 2026)

- **A signature** declares a step's inputs and outputs, with types (Pydantic models work).
  Its docstring is the instruction; that is the prompt DSPy optimises.
- **A module** runs a signature (`Predict`, `ChainOfThought`, …). A **program** is modules
  composed in ordinary Python.
- **`dspy.LM`** is provider-neutral, so Claude models plug in directly.
- **Async** (`acall`) suits a FastAPI server. **Streaming** (`streamify` with a
  `StreamListener`) works for **string** output fields only.
- **Optimisers** rewrite instructions and pick examples against a **metric**. The flagship
  is **GEPA**: a reflection model reads failed runs plus written feedback from the metric,
  and proposes better instructions. It works with small datasets and optimises every
  module in a multi-step program.
- **An optimised program is saved as JSON** and loaded in production. Production runs the
  same program the harness tuned.

In production the programs run in a Python service in a Cloudflare Container, and every
model call goes through Cloudflare AI Gateway, which logs it for the harness. See
[07](07-architecture.md).

## The objective (decided)

Every module serves one goal: **the best possible play the audience would want to see,
through their votes.** Nothing is optimised for the improvisers; they are trusted to
justify whatever happens. See [05](05-scene-writing.md).

## The shape: one evolving premise

"Determining the play" is not a separate step. It is the **premise**, a state that grows
with every decision until it is complete enough to write from.

```
                 ┌────────────── survey (phase 1) ──────────────┐
source ──▶ QuestionWriter ─▶ round ─▶ votes ─▶ decision ─▶ premise so far ─┐
               ▲                                                          │
               └─────────────────── next slot ◀───────────────────────────┘
                                         │ complete
                                         ▼
                                  PremiseWriter  ─▶  premise  ─▶  SceneWriter  ─▶  scene
                                  (determine the play)            (phase 2)
```

## Phase 1: the survey

### Slots form a dependency graph

The slots (play, moment, who, wants, turn; see [04](04-brainstorm.md)) depend on each
other. "What does each of them want" needs "who is in the room"; "who is in the room"
does not need "what is the turn". So:

- **Dependent slots are asked one at a time**, each adapting to the decisions before it.
- **Independent slots can be asked as a batch, in a row**, written together in one call,
  because none needs the other's answer.

This answers "adapt each question, or a bunch in a row": the graph decides. The graph is
plain code, not AI, so it is predictable and testable.

### Scripted rounds first

The admin may script the first few rounds ([04](04-brainstorm.md)). The QuestionWriter
starts where the script ends and treats scripted decisions exactly like its own.

### Grounded in a source play

The scene is grounded in a known play, with a twist the room chooses (see
[05](05-scene-writing.md)). The QuestionWriter sees the source's plot, characters and
famous moments, so its options (play-plus-twist pairs, moments) stay true to the play
while the twist brings the chaos.

### Genre as an input

Every module takes the genre card as an input. One optimised program serves every
genre; adding a genre never means re-optimising. Datasets are spread across genres so the
program doesn't learn to suit only a few.

### The twist round

One late round is deliberately out of the ordinary (see [04](04-brainstorm.md)). It is
the same QuestionWriter with a different slot and instructions: wild options, but each
one something the playwright could make matter.

### QuestionWriter

```
QuestionWriter
  in:  genre card, source play (plot, characters, moments), slot, decisions so far, content rating, persona (if used)
  out: question        short enough to read on a phone at a glance
       options         3 or 4, short
       selection_mode  single | multiple
```

- **Write ahead:** while a round is open, write the next question for every option in
  parallel and keep the one that matches the winner. No visible wait between rounds.
  Must finish within a round's minimum time (about 8 s); see "Round timing" in
  [04](04-brainstorm.md).
- **The first round** depends on no vote, so it is written before the set starts.
- A fast model is enough here; the wait is hidden anyway.

### Personas (open)

Two places a persona fits, and both could be used:

- **Option authors:** each option is written by a different persona, for example one leaning
  to order (the robot) and one to chaos (the pirate), so every vote is the room choosing
  between them.
- **Simulated audience members:** personas that vote, used only by the harness (below).

## Determining the play: PremiseWriter

```
PremiseWriter
  in:  genre card, source play (plot, characters, moments), decisions (question + winning options), content rating, number of improvisers
  out: play          title; what the play is about, in a sentence or two
       situation     where and when this scene happens in the play
       characters    name; voiced or withheld; what they want; one fact about them
       turn          what changes before the scene ends
       payoffs       for each decision: how the scene will honour it
       briefing      what the host sees before the scene: only what they need
```

`payoffs` makes every decision's promise explicit before any line is written, so the scene
writer can't forget one and the harness can check each.

## Phase 2: the scene

```
SceneWriter
  in:  premise, target number of lines, content rating
  out: opening_tasks   one per improviser: a physical activity that reveals nothing
       lines           each: character, text, delivery description, voiced or ghost, beat
```

- **Writes both sides**: the host's lines and the improvisers' ghost lines.
- **Outline first, then lines** ([09](09-story-quality.md)): want, obstacle, escalation, turn,
  button and payoffs are decided before any line is written. Whether this beats a single
  step is still measured, not assumed.
- **Several candidates, best one wins:** three to five scenes written in parallel; the judge
  picks the best; below the bar, one revision, then the understudy.
- **Checked before use:** the code checks below run as a gate. A failure gets one rewrite,
  then the understudy scene ([08](08-reliability-and-infrastructure.md)).
- **Streaming**, if needed: DSPy streams string fields only, so the lines would come as one
  text field in a simple line format, parsed as it arrives. Measure first; a short scene
  may not need it.
- The strongest model that meets the 15-second target writes the scene.

## Optimisation

### Metrics, per module

Every metric returns a **score and written feedback**, because GEPA learns from the
feedback text. Code checks produce feedback for free ("line 14 is 41 words; the limit is
25").

| Module | Checked by code | Judged by an LLM |
|---|---|---|
| **QuestionWriter** | Lengths; option count; slot filled; no phone-related options | Options are real forks; grounded (twist round: surprising yet usable); builds on earlier decisions; within the content rating |
| **PremiseWriter** | Every decision has a payoff; characters match the improviser count; characters and moment exist in the source | Coherent; specific; the briefing has only what the host needs |
| **SceneWriter** | No phones, screens, apps, texts or calls anywhere; no long quotations from the source; line count against target; line length; a delivery description on every line; the dialogue carries who, where and what for the audience; beats present and in order | The genre is recognisable, conventions not caricature; delivery descriptions performable with one hand; true to the source play except for the twist; the twist matters to the scene; every payoff lands; readable cold; no filler; the host's lines carry the scene; within the content rating |
| **Whole pipeline** | | "Would the room believe this scene is theirs?" |

### Data

- **Simulated audiences.** A voter module plays a persona (age, taste, mood, a lean towards
  order or chaos) and picks options. A crowd of them walks the survey, producing realistic
  decision paths. Hundreds of runs cost little with a fast model.
- **Training examples** are snapshots from those runs: the inputs each module saw. GEPA
  works with tens of examples, not thousands.
- **Three splits:** training and validation for GEPA, and a held-out test set that no
  optimiser ever sees.
- **Real shows** add host ratings and logged delivery times.

### Keeping the judge honest

An LLM judge can be wrong, and an optimiser will exploit it. So:

1. The owner rates a first set of scenes by hand (about 30).
2. Measure how often the judge agrees with those ratings.
3. Improve the judge (it is a DSPy module too) until it agrees well.
4. Only then optimise the writers against it, and keep checking the winners by hand.

### Order of work

1. **Seed programs.** Write the signatures, with the rules from
   [05-scene-writing.md](05-scene-writing.md) in their docstrings. Run end to end in the app,
   unoptimised.
2. **Metrics.** Code checks, judge rubrics and the simulated audience.
3. **Gold set.** The owner rates about 30 scenes; calibrate the judge.
4. **Optimise SceneWriter** with GEPA (light budget first); compare against the seed on the
   held-out set.
5. **Optimise QuestionWriter and PremiseWriter.**
6. **Rehearsals feed the loop:** ratings and delivery times from real performances.
7. **Understudy scenes** are written offline with the best program and reviewed by a person.

## Sources

- [DSPy GEPA tutorial](https://dspy.ai/current/getting-started/gepa-optimization/)
- [DSPy 3.3.1 release notes](https://newreleases.io/project/github/stanfordnlp/dspy/release/3.3.1)
- [DSPy streaming](https://dspy.ai/tutorials/streaming/)
