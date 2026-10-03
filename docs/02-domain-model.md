# 02 — Domain model

## What we're creating, fundamentally

**A scene with a part missing.** The AI writes a scene, and the lines of the
improvisers' characters are withheld. The improviser fills a hole that has a specific
shape: in the original show, every scripted line was written as a reply to something,
so it carried the ghost of the missing half.

## Hierarchy

```
Admin ──manages──▶ Catalogue (Genres, Sources)
  │
  └─creates─▶ Show
                └─ Set (one per scene; several per show)
                     ├─ Brainstorm ─▶ Rounds ─▶ Decisions ─▶ Premise
                     ├─ Scene  (written from the Premise; never changes)
                     │    └─ Lines
                     └─ Performance  (one run of the Scene)
                          └─ Events
```

## Vocabulary

| Term | Meaning | Status |
|---|---|---|
| **Show** | One live event (one evening). Created by the admin. Has a join code. | Decided |
| **Set** | One brainstorm, scene and performance inside a show. A show holds several, and the host rotates between them. "Set" is a placeholder name. | Proposed |
| **Genre** | The overarching register of a play and scene: Shakespearean, Greek, Bollywood, soap opera, reality TV, surreal, anime, and many more. Stored as a genre card in the catalogue. | Decided (cards proposed) |
| **Source** | A well-known public-domain play the scene is grounded in: its plot, characters, world and famous moments. Grouped by tradition (Shakespeare, Goethe, Greek, Indian classics, surreal). | Decided |
| **World** | Where the play is set when performed: as written, or transposed to today (a tech company, a national government, a parliament). Chosen by the room. | Decided (idea) |
| **World mapping** | For one play and world: who each character becomes, and what each place and object becomes. Written once, reused for every scene. | Proposed |
| **Rendition** | A scene in today's English, in a chosen world, speech for speech with the original, approved by a person before use. | Proposed |
| **Twist** | One deliberate change to a known fact of the source ("Macbeth has a twin he doesn't know about"), chosen by the room. The source is the order, the twist the chaos. | Decided (kinds proposed) |
| **Moment** | A famous point in the source play where the scene is set (the banquet, the balcony). | Proposed |
| **Brainstorm** | The ordered series of rounds in which the audience shapes the scene. | Decided |
| **Survey plan** | Which rounds the admin scripts (question and options written by hand) and where the AI takes over. Saved as reusable templates. | Decided (templates proposed) |
| **Round** | One question, its options, the ballots cast, and the resulting decision. | Decided |
| **Question** | Written by the admin (scripted rounds) or by AI (the rest). Single or multiple selection. Fills one **slot** (see [04](04-brainstorm.md)). | Decided (slots proposed) |
| **Option** | One of a question's multiple choices. Written by AI, possibly by a **persona**. Audience members never type free text. | Decided |
| **Persona** | An AI voice that writes questions and options. What exactly a persona is remains open. | Open |
| **Door check** | The questions a joining audience member answers to prove they are human and present (for example, the host's shirt colour). Answers set at the doors by the host or admin. | Decided (design proposed) |
| **Door question** | A multiple-choice question written by the admin, with one or more correct options. Either a *venue* question (reusable at every show there) or a *live* question (set at the doors for one show). | Decided (kinds proposed) |
| **Admission** | What passing the door check grants: a signed token for one show, kept on the phone and carried by every ballot. | Proposed |
| **Device** | A phone registered to a show as audience, performer or admin. | Decided |
| **Performer** | A member of the troupe, joined on their own phone. Hosts in some scenes (chosen at random, one character each), improvises in others (performers decide who goes on). | Decided |
| **Cast requirement** | What a scene needs: the characters read by hosts, and how many improvisers (exactly n, at least n). | Proposed |
| **Casting** | For one set: which performer hosts which character, and which performers improvise. | Proposed |
| **Ballot** | One audience member's selection in one round. | Decided |
| **Decision** | The winning option or options of a round. It is a **promise**: the scene must pay it off. | Proposed |
| **Premise** | The source, the play's context and all the decisions. The contract between the room and the playwright, and the input to scene writing. | Proposed |
| **Play** | The backdrop: title, what it is about, who is in it. **Never written out**; it exists so the scene has something to belong to. | Decided |
| **Opening task** | A simple physical activity each improviser is doing when the scene starts. Written by the AI; reveals nothing. | Decided (details proposed) |
| **Scene provenance** | Where a scene's text comes from: a real play (source, act and scene, edition; version 1) or the AI (later versions). | Proposed |
| **Scene** | The text the host reads: one place, one continuous stretch of time, a few characters. Written once, never changed. | Decided |
| **Character** | A part in the scene, either **voiced** (read by the host) or **withheld** (played by an improviser). | Proposed |
| **Line** | One line of dialogue, with a delivery description. Every line is delivered; none is optional. See below. | Decided (fields proposed) |
| **Briefing** | What the host sees before starting: their character and what the play is about, only what is essential to deliver the dialogue. | Decided |
| **Ghost line** | A line belonging to a withheld character: what the script says the improviser "should" say. | Proposed |
| **Performance** | One run of a scene: the cursor plus a log of events. | Proposed |
| **Event** | Something that happened in a performance: started, prepared, delivered, back, ended. Append-only. | Proposed |
| **Rating** | The host's verdict on a scene after performing it. Training data for the harness. | Proposed |

Naming note: **Role** means a person's job in a show (admin, host, improviser, audience
member); see [03](03-roles-and-surfaces.md). A part in the scene is a **Character**.

## Line

**Decided: the host only delivers dialogue.** There is no narration and no stage
direction. A line may carry a **delivery description** telling the host how to say it
("whispering", "furious", "cutting them off").

So everything the improvisers learn (who they are, where they are, what is happening)
has to arrive inside the host's dialogue. See [05-scene-writing.md](05-scene-writing.md).

**Proposed fields:**

```
Line
  idx           position in the scene
  character     who speaks
  text
  cue           optional delivery description for the host
  voiced        true = the host reads it; false = ghost line
  beat          which part of the arc: setup | escalation | turn | ending
                (for writing and the harness; not shown to the host)
```

## Performance and cursor

**Proposed:** the scene is a flat ordered list of lines. Each voiced line goes through two
phases on the host device, **prepare** and **deliver** (colours are a later design idea); see
[03](03-roles-and-surfaces.md).

The host device holds the full position: the line and its phase. The shared cursor is
only the **last delivered line**, which changes when the host swipes into deliver (or steps
back out of it). The prepare phase is private to the host. Everything on the audience
screens is derived from the shared cursor:

- Lines up to the cursor are **past**; the cursor line is **being said now**.
- Ghost lines right after the cursor are **the open gap**: the improviser is filling it.

Every phase change is still logged as an event. The moment of each swipe into deliver is the
exact delivery time of the line, which gives the gap length for every line: useful for
the harness, and later for speech sync.

The event log is append-only. Later, when improvisers are miked, an improvised line is
just another event placed by timestamp, so "the full scene that actually happened" becomes
a query over the log instead of a redesign.

## Lifecycle of a set (proposed)

```
brainstorming ─▶ writing ─▶ briefing ─▶ performing ─▶ done
```
