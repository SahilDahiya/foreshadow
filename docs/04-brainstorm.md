# 04 — Brainstorm

## Decided

- The audience joins on their phones (web, no install) and takes part in a short
  brainstorm, about two minutes.
- It is a real story brainstorm, not random weird prompts.
- **Responses are multiple choice only.** A question is single or multiple selection.
  Audience members never type free text.
- **The questions and options are written by AI**, through AI personas.
- **Maybe:** the AI writes each next question based on the earlier questions and answers.
- **Results are shown only on audience phones.**
- The host watches the brainstorm live.
- The audience must believe in the scene that comes out of it.

## Belief: the requirement everything is tested against

"Believes in it" is taken to mean two things (still to confirm, see open questions):
the audience believes **the scene is theirs**, and believes **it is real**.

### Believing it is theirs (proposed)

- **Every decision shows up in the scene**, recognisably and in the words the audience voted
  on. Each winning option is a promise the playwright has to keep.
- **The opening pays them back.** The first few lines of dialogue make what the room chose
  recognisable within about thirty seconds.
- **Options are real forks.** Each option leads to a visibly different scene; otherwise the
  vote is decoration.
- **Adaptive questions prove the system is listening.** When round 2 asks "Who arrives at
  the lighthouse at 3am?", the room sees its last answer already in use. Recommended as
  core, not "maybe".
- **Few, heavy decisions.** Three or four rounds that the audience can remember and watch
  land.

### Believing it is real (proposed)

- **Options are grounded**: things a playwright would seriously consider. Random wackiness
  reads as a party game.
- **The writing is specific**: names, objects, concrete detail.
- **A proven engine helps.** Borrowing the dramatic engine of a known play (its core
  tension and shape) gives an original scene real stakes and direction. See
  [05-scene-writing.md](05-scene-writing.md).

## Slots (proposed)

The slots are fixed and the AI writes each round's wording and options, adapting to
earlier decisions. Every brainstorm therefore yields a complete premise. The source play
supplies only the engine (see [05](05-scene-writing.md)); everything the slots collect is
original.

0. **The genre:** usually a round the admin scripts (see below).
1. **The world:** where and when.
2. **Who is in the room.**
3. **What each of them wants.**
4. **The twist:** a deliberately out-of-the-ordinary question (see below).
5. **The turn:** the one thing that changes before the scene ends.

Slots may be merged to get down to three or four rounds. Which source is used, and who
picks it, is open.

## Scripted opening, then the AI takes over (decided)

**The admin can set up the first few rounds themselves, and the AI takes over from
there.** A set's survey is therefore a **plan**:

```
[ scripted round ] [ scripted round ] ─▶ [ AI round ] [ AI round ] [ AI round ]
   written by the admin                     written by the QuestionWriter, adapting
```

- Typically the admin scripts the genre round (for example: Bollywood, Greek, reality TV,
  anime) and perhaps the world, and the AI writes the rest, adapting to every decision so
  far, the scripted ones included.
- The number of scripted rounds is up to the admin, from none (all AI) to all (no AI).
- **Proposed benefits beyond control:** scripted rounds need no AI call, so the opening of
  every survey is instant and can never fail; and themed nights ("Bollywood night") are
  simply a plan whose genre round has one option, or is skipped.
- Proposed: the admin saves plans as reusable **templates**, and picks one per show or set.

## The twist question (decided idea; rules proposed)

**Decided:** the survey can deliberately ask out-of-domain, out-of-the-ordinary questions
to give the scene a twist.

This is the robot, the pirate and the ninja again: most questions build the story
(order), the twist question breaks it (chaos), and the playwright has to make both work
together.

Proposed rules:

- **Ask it late**, once the story has a shape, so the twist has something to collide with.
- **One per scene, two at most.** More turns the survey into a party game, which costs
  belief.
- **The options are wild; the payoff is serious.** Whatever wins has to matter in the
  scene and be justified inside the story, not mentioned once and dropped. A twist the
  scene takes seriously is funny; a random gag is not.
- **Example:** after the room has built two sisters and a failing bakery: "What is hidden
  in the walk-in freezer?" with options such as "a live swan", "their father's will",
  "a second, identical bakery".

## The brainstorm creates the irony (proposed)

The audience leaves the brainstorm knowing things the improvisers don't: the world they
built, the twist they chose and the turn. They then wait for those things to arrive.

## Personas (open)

What a persona is hasn't been settled. Two interpretations so far:

- **Option authors:** different personas write the options. For example a Robot offers the
  structurally sound choice and a Pirate offers the chaotic one, so each vote is the room
  choosing between order and chaos.
- **Simulated audiences:** personas that vote, used by the harness to generate test
  brainstorms. See [06-ai-pipeline.md](06-ai-pipeline.md).

## Round timing: when does a round close? (proposed)

Each AI question depends on earlier answers, so a round must close before the next
question can be chosen. Waiting for everybody never works (someone is always at the bar),
and a fixed timer wastes time when the room answered in five seconds. So a round closes on
whichever comes first, within a minimum and a maximum.

### The rule

```
round opens
  │
  ├─ minimum time: long enough to read the question and options (at least ~8 s,
  │  longer for longer text). Nothing closes before this.
  │
  ├─ then the round closes early if either:
  │    • most of the room has voted (about 85% of active phones), or
  │    • the result can no longer change (the remaining voters can't overturn the leader)
  │  → a short "last call" countdown (3 s) on every phone, then close
  │
  ├─ otherwise it closes at the maximum time (about 25 s)
  │
  └─ the host can always close now, or add 10 s, from the host device
```

- **"Active phones"** means phones that have been in touch with the server in the last few
  seconds, not everyone who ever joined. People who wander off stop counting.
- **The "last call"** is fair to the slow and theatrical: everyone sees "3, 2, 1".
- **The server's clock decides.** Phones show a countdown computed from the server's time,
  so every phone closes together.
- **Late joiners** vote in the round that is open when they arrive.
- **Changing your mind** is allowed until the round closes; the new vote replaces the old.
- **Minimum, maximum, threshold and last call are set per round** in the survey plan, with
  these as defaults.

### What voters see while waiting

- After voting: their choice, and **"34 of 52 have voted"**, which nudges the rest and
  builds anticipation.
- **No live tally for voters.** Seeing which option is ahead makes people follow the
  crowd, and spoils the reveal. The host sees the live tally.
- **The reveal:** when the round closes, every phone shows the winner and the split of
  votes for about 3 seconds. That is the moment the next question needs anyway.

### Ties

A tie is broken at random, and the reveal says so ("Tie! Fate chose the swan"). It is
fair, quick, and a small moment of its own.

### Not every question has to wait: sync points

The slot dependency graph ([06](06-ai-pipeline.md)) decides where the room has to wait:

- **Dependent questions are sync points.** Everyone waits for the round to close, because
  the next question is built from its result.
- **Independent questions can run as a group.** Each person moves through them at their
  own pace, one screen after another, and the group closes together under the same rule.
  This saves time and feels quicker on the phone.

### Hiding the AI behind the timing

- **Write ahead:** when a round opens, the follow-up question for every option is written in
  parallel. With a fast model, that finishes within the minimum time, so the next question
  is ready the moment the round closes. If not, the 3-second reveal covers it.
- **Multiple-selection rounds** have too many possible results to write ahead for. So
  either they are used only where nothing depends on them, or their follow-up is written
  after closing, during the reveal. How many options win one is open.

### The whole survey

With about five rounds, each taking 8 to 25 seconds plus a 3-second reveal, a survey runs
roughly one to two and a half minutes. The survey plan has a target length; if the
survey is running long, later rounds get shorter maximums.

## Content safety (proposed)

The host reads cold, so no person checks the text before the audience sees it. This is
acceptable because the audience only picks from AI-written options and never types. The
safeguard is a **content rating** set by the admin per show, which the question and scene
prompts both follow.
