# 10 — The play library

An internal service that turns public-domain plays into structured data the app can use.
It supplies version 1's real scenes ([05](05-scene-writing.md)) and, later, the source
plays the AI works from. Code: [`library/`](../library).

**Decided:** start with Shakespeare, hyperfocused on one edition; abstract to other
sources later. **Built:** all 38 plays from Project Gutenberg #100.

## Three layers

| Layer | What it is | Status |
|---|---|---|
| **Text** | The play as written, faithful to its source: acts, scenes, speeches, stage directions, characters | Built |
| **Rendition** | The same scene in today's English, speech for speech, in the original world or a modern one the room chooses, written by AI and approved by a person | Proposed |
| **Performable scene** | A curated cut of a rendition for the show: host character, lines, mime task, briefing (the app's `Scene`) | Next |

Each layer points back to the one below, so everything can be traced to the original,
re-done when a prompt or the parser improves, and shown side by side.

## Renditions: today's English (decided idea; design proposed)

**Decided idea:** the archaic language is a barrier for a host reading cold and for an
audience following along, so the performed text is in today's English. This is where AI
first comes in, and the play stays grounded in the original.

Why it is a good first job for AI:

- **Low risk.** The story, characters, structure and meaning are fixed by Shakespeare. The
  AI only changes the language, which is far easier to judge than invention.
- **Done offline, once per scene, and reviewed by a person** before any show. No live
  generation, no waiting, nothing unseen reaches a stage.
- **It does the line splitting too.** Today's English can be written as short, speakable
  sentences, which the host screen needs anyway.

### Today's world too: the room chooses it (decided idea; design proposed)

**Decided idea:** the setting can move to today as well. The king becomes a CEO, a
president, or an MP in a parliament, and the room chooses which: "Tonight, the king
is…". This is proven: Vishal Bhardwaj's *Omkara* is Othello in the politics and gangs of
Uttar Pradesh, *Maqbool* is Macbeth in the Mumbai underworld, *Haider* is Hamlet in
Kashmir. The plot, characters and their relationships stay; the world around them
changes.

**A world mapping** makes it consistent: one per play and world, written once and reused
for every scene of that play.

| Original (Macbeth) | A tech company | A national government |
|---|---|---|
| King Duncan | The founder and CEO | The President |
| Macbeth | The COO, his star executive | The Vice President |
| Lady Macbeth | Macbeth's wife, a board member | The Vice President's chief of staff and wife |
| Banquo | The CFO | The Secretary of State |
| The three witches | Three analysts with an uncanny forecast | Three pollsters |
| The crown | The CEO's chair | The presidency |
| Inverness, Macbeth's castle | Macbeth's lake house, the company retreat | The Vice President's residence |

**Everything the room can choose is rendered before the show.** The admin picks three or
four worlds per scene; each scene is rendered in each world offline and approved by a
person. A dozen scenes in four worlds is about fifty renditions: manageable, and it keeps
the rule that nothing unseen reaches the stage. Free-form worlds generated live come
later, with the AI pipeline ([06](06-ai-pipeline.md)).

**The phone tension.** Modern worlds are full of phones, emails and texts, and the play
must still never mention them ([05](05-scene-writing.md)). Lady Macbeth's letter in 1.5
becomes something spoken or remembered ("your message last night"), never read off a
screen. The checks enforce it.

### Rules (proposed)

- **Change the language and, when chosen, the world; never the story.** Plot, events,
  relationships and order stay. In the original world, names, places and period stay too.
  Nobody gains a phone ([05](05-scene-writing.md)).
- **The world mapping is followed exactly**, so every scene of a play agrees.
- **Speech for speech.** Every original speech gets exactly one modern speech, by the same
  speaker, in the same order. Nothing is added, nothing dropped.
- **Faithful meaning, natural speech.** Plain, contemporary, speakable English: not slang,
  not a summary.
- **Each character keeps a voice.** Lady Macbeth stays sharper than Macbeth.
- **Stage directions are modernised too**; the host's become delivery descriptions later.
- **Famous lines** ("Is this a dagger which I see before me") may stay as written; open.

### Model (proposed)

```
World           id, name ("A tech company"), description
WorldMapping    play_id, world_id, roles (character → modern role), places, objects, notes
Rendition       id, play_id, scene_id, world_id (or "original"), language ("today's
                English"), model, prompt version, created at, approved by / at, blocks[]
RenderedBlock   source_block (index into the text scene), speaker_ids, parts[]
```

Renditions sit beside the text, never over it: `renditions/<play>/<scene>/<version>.json`
through the same repository pattern, keyed by world:
`renditions/<play>/<scene>/<world>/<version>.json`.

### How it is made (proposed)

- **One call per scene**, so the voice stays consistent, returning structured output keyed
  by block number, which makes the speech-for-speech rule checkable by code.
- **A DSPy program** (`ModerniseScene`), the first one built: its checks are clear
  (every speech present, same speakers, sentence length, no modern objects) and its judge
  compares meaning with the original. It becomes the first use of the harness
  ([06](06-ai-pipeline.md)).
- **Start small:** the version 1 shortlist and the two-handers, measure cost and quality per
  scene, then decide how much of the canon to render.
- **Review in the library browser:** original and modern side by side, with an approve
  button.

## Domain model (text layer)

```
Play          id, title, author, genre, source, characters[], scenes[]
Source        provider (gutenberg), ebook id, url, retrieved at, sha256
Character     id, name (as printed), description, in dramatis personae?
Scene         id ("macbeth/1/7"), act, number, division (scene | prologue | induction |
              epilogue | chorus), heading, location, blocks[], stats
Block         Speech       speaker ids, speaker label, parts[]
              StageDirection   text
SpeechPart    VerseLine        text            (line breaks kept: verse is verse)
              InlineDirection  text            ("Enter Lady Macbeth." mid-speech)
SceneStats    words, lines, speeches, speakers[] (share of each), two-hander?
```

Acts are a property of each scene rather than a level of nesting, because not
everything sits inside an act (inductions, choruses, epilogues).

A **two-hander** is a scene where two speakers carry at least 90% of the words, the
second has at least 15%, and the scene has at least 150 words: the best candidates for one
host and one improviser.

## The pipeline

```
acquire ──▶ strip ──▶ split ──▶ parse ──▶ validate ──▶ analyse ──▶ save ──▶ publish
Gutenberg   licence   38 plays  domain    scene counts  stats,      repository  app static
(cached)    removed   (poems    model     vs contents   two-handers             files
                      skipped)
```

| Stage | What it does |
|---|---|
| **Acquire** | Downloads the ebook once, caches it with its retrieval time and checksum |
| **Strip** | Removes everything outside Project Gutenberg's START/END markers, so its name and licence are not reused |
| **Split** | Uses the edition's contents list to find each work; keeps the 38 plays, skips the poems |
| **Parse** | An edition-specific parser builds the domain model |
| **Validate** | Compares the scenes found with each play's own contents list; reports likely errors (warnings) separately from handled oddities (notes) |
| **Analyse** | Word and line counts per speaker, two-hander detection, the library index |
| **Save** | Writes through the repository |
| **Publish** | Copies the library into the app's static files |

### Edition quirks handled

Gutenberg #100 is not perfectly consistent: some plays indent stage directions and some
don't; a few lines of dialogue are indented like directions; some scene headings are
"Scene" rather than "SCENE"; Richard II has no contents list and no "Dramatis Personæ"
heading, and its contents list sits at the end of Pericles; Gower's choruses in Pericles
have no scene heading; "PROLOGUE" is sometimes a heading and sometimes a speaker. Each
is handled explicitly, and tests pin the behaviour.

## Repositories

The pipeline and the app depend on interfaces, not on storage:

| Interface | Today | Later |
|---|---|---|
| `RawTextRepository` (Python) | Files in `library/.cache/` | R2 |
| `PlayRepository` (Python) | `library/data/plays/<id>.json`, `index.json` | D1 or R2 |
| `LibraryRepository` (app) | Static files at `/data/library/` | An API in the Worker |

The generated data is not committed: it is rebuilt from the cached source with
`library build` and copied into the app with `library publish`.

## The library browser

An internal page in the app, at `/library`:

- **All plays**, with genre, scene count, two-hander count and length.
- **A play's scenes**: location, who speaks most (with shares), words, two-hander badge, and
  a "two-handers only" filter.
- **A scene's text** as parsed: speakers, verse lines, stage directions inline.

## What it found

38 plays, 791 scenes and sections, 146 two-handers. Examples: Macbeth 1.7 ("We will proceed no
further") and 2.2 (after the murder); Romeo and Juliet 2.2 (the balcony).

Some great two-person moments sit inside bigger scenes (Helena and Demetrius in A
Midsummer Night's Dream 2.1 is surrounded by fairies), so they don't show up as
two-handers. The next step finds them.

## Cast analysis (proposed)

With several hosts, a scene's cast size matters as much as two-handers: the witches'
scene in Macbeth 1.3 suits three hosts and two improvisers. Analysis will report, per
scene or segment, the speaking characters and their shares, so curation can choose which
characters hosts read and the survey can offer only scenes the troupe can cast.

## Next

1. **Segments.** Split scenes into stretches between entrances and exits, and find
   two-person segments inside larger scenes.
2. **Performable scenes.** The curation layer: choose a scene or segment and the host's
   character; split long speeches into lines; turn the host's stage directions into
   delivery descriptions; apply cuts; add the mime task and briefing. Produces the app's
   `Scene`, which the host and follow-along screens already play.
3. **More sources.** Other Gutenberg plays (Wilde, Ibsen, Shaw, Marlowe) through their own
   parsers into the same domain model; check translators' rights first.
4. **Generated types.** TypeScript types generated from the Pydantic models instead of
   kept in step by hand.
