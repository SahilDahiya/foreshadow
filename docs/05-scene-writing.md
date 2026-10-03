# 05 — Scene writing

## The north star (decided)

**The AI's job is to write the best possible play that the audience would want to see,
through their votes.** It writes for the audience, never for the improvisers.

- **Nothing in the script accommodates the improvisers.** No lines engineered to be easy to
  justify, no openings that set them up, no collisions planned with what they might do.
- **It is assumed nothing will go according to plan.** The improvisers know nothing, and
  the script will not match what they do.
- **That is their craft.** Justifying, holding the scene and holding the audience is what
  improvisers are trained for. The format trusts their skill.
- So every writing decision is judged by one question: **does this make a better play for
  the room that voted for it?**

## The phone is not in the play (decided)

**The phone in the host's hand is not part of the scene.** The improvisers ignore it, the
way actors at a staged reading ignore the script in a colleague's hand. So the play must
never mention it, or anything that would make the improvisers justify it.

- **No phones, screens, apps, texts or calls** in any line, ghost line, delivery
  description, briefing or opening task. A character can't "check a message", "read
  something on a screen" or "take a call".
- **Delivery descriptions are performable with one hand**, since the other holds the phone:
  "unfolding an invisible letter" works; "clapping" or "holding her face in both hands"
  does not.
- **Prophecies, letters and messages come from the world of the play** instead: a fortune
  teller, a letter, a newspaper, a voice from the next room.

## Decided

- **The unit is a scene, written like a sketch, not a whole play.** Knowing what the play is
  about makes the scene much easier to write well.
- **Scenes can be inspired by well-known public-domain plays** that everybody knows.
- It doesn't have to be over the top.
- The host only delivers dialogue, each line with an optional description of how to
  deliver it. There is no narration and no stage direction.
- The scene is written once, after the brainstorm, and never rewritten.

## The AI writes both sides (proposed)

The AI writes the whole scene, including the improvisers' characters, and then withholds
the improvisers' lines. This is how the original show worked: the scripted lines were
written as replies to a real scene partner, so they carry implied context. Lines written
into a void come out generic. The ghost lines exist to make the play good, not to help
the improvisers.

The one constraint: **the host's character carries the plot.** If the key information sits
in the withheld lines, the host is left with "Yes." "What?" "I know."

## Version 1: real scenes, performed as written (decided direction; details proposed)

**Decided direction:** the first version doesn't generate anything. The room chooses a
real scene from a public-domain play, and the host performs it as written. This is
exactly the show that inspired Foreshadow: one actor reading a real play word for word,
an improviser who doesn't know it.

Why it goes first:

- **No story-quality risk.** Shakespeare, Wilde and Ibsen are already compelling
  ([09](09-story-quality.md)).
- **The whole loop works end to end, soon**: join, vote, host, follow along, with no AI.
- **It tests the format itself** (the host's flow, the room following along, the
  dramatic irony) before money and time go into AI.
- **AI is added later as layers**: version 2 applies a room-chosen twist to a real scene;
  version 3 writes scenes from scratch (below).

### The source: Project Gutenberg

[Project Gutenberg's drama bookshelf](https://www.gutenberg.org/ebooks/bookshelf/642) has
the plays as plain text: Shakespeare, Wilde, Ibsen, Shaw, Sophocles, Aristophanes,
Marlowe, Goethe, Synge, Glaspell.

- **Remove Project Gutenberg's header, footer and name.** The plays are public domain; the
  Gutenberg name and licence text are not ours to reuse.
- **Download each play once**, by hand or with a small script, and store our curated
  version. No repeated automated fetching.
- **Translations need checking.** A translator who died less than 70 years ago may still
  hold rights outside the US (for example, Gilbert Murray's Sophocles until 2028 in the
  EU). Shakespeare, Wilde, Marlowe and Shaw written in English are safe.

### In today's English (decided idea)

The host performs the scene in today's English, rendered by AI from the original, speech
for speech, and approved by a person before any show. The play stays grounded in the
original; only the language changes. See [10](10-play-library.md), "Renditions".

### From play text to a scene (proposed)

Plays are not written for one person reading cold from a phone, so each scene is curated
once into the Scene format ([02](02-domain-model.md)):

- **Pick the scene and the host's character**: usually two characters (host plus one
  improviser), brisk exchanges, and a host character who drives the scene.
- **Long speeches are split** at sentence boundaries into several lines, one swipe each, so
  each is short enough to read cold. The words stay the same.
- **Stage directions** become delivery descriptions when they concern the host's
  character; the rest are dropped (there is no narration).
- **Light cuts are allowed** to fit the target length; nothing is rewritten.
- **A mime task and a briefing** are written for each scene, following the usual rules.

A small import tool does the mechanical part (strip, split, assign lines); a person does
the judgement (which scene, which cuts) and approves the result.

### A first shortlist (proposed)

| Play | Scene | Host plays | Why |
|---|---|---|---|
| The Importance of Being Earnest | Act 1: Lady Bracknell interviews Jack | Lady Bracknell | Iconic, brisk, comic; easy to read cold |
| Macbeth | Act 1 Scene 7: "We will proceed no further" | Lady Macbeth | A persuasion scene with a clear want |
| Macbeth | Act 2 Scene 2: after the murder | Lady Macbeth | Short, tense lines |
| Hamlet | Act 3 Scene 1: the nunnery scene | Hamlet | A famous confrontation |
| Romeo and Juliet | Act 2 Scene 2: the balcony | Juliet | The most famous scene there is; needs splitting |
| A Midsummer Night's Dream | Act 2 Scene 1: Helena chases Demetrius | Helena | "I am your spaniel": comic and brisk |
| Pygmalion | Act 4: Eliza and Higgins after the ball | Eliza | A row with a heart |
| A Doll's House | Act 3: Nora leaves | Nora | One of drama's great endings (translation to check) |

### The survey in version 1

All rounds are scripted from the catalogue: choose the play, choose the scene, then
choose the world ("Tonight, the king is… a CEO · a president · an MP · as Shakespeare
wrote it"). Every option has a rendition prepared and approved before the show, so the
survey needs no live AI. The survey-plan machinery ([04](04-brainstorm.md)) already
supports this.

## Grounded in a known play, with a twist (decided direction; details proposed)

*This is version 2 onwards: the AI changes one fact of a real scene, or writes a new
scene in a known play's world.*

**Decided:** to make the story compelling, ground it in an already written, freely
available play that people know, for example Shakespeare. This replaces the earlier lean
towards "as original as possible" (borrowing only a play's engine).

It is order and chaos again:

- **Order: the known play.** Its characters, world, plot and famous moments are proven
  drama, and the audience arrives already knowing them.
- **Chaos: the twist.** One deliberate change to a known fact ("Macbeth has an identical
  twin he doesn't know about yet"), chosen by the room.
- **Originality comes from the twist and the room's choices**, not from inventing a story.

### Why this de-risks story quality

- **The plot is proven.** Centuries of audiences have found Macbeth compelling; the AI no
  longer has to invent stakes from nothing ([09](09-story-quality.md)).
- **Recognition is instant.** The room knows what *should* happen, so it watches the twist
  collide with the original, on top of the improvisers colliding with the script.
- **Belief comes free.** The world, characters and stakes are already credible.
- **AI writes known-play pastiche well**, and has far less room to wander.
- **The improvisers recognise the play too** once they hear "Macbeth". That gives them a
  world to justify inside, while the twist and the specifics still surprise them.

### How close to keep it: the dial, revisited

| Closeness | What is borrowed | Status |
|---|---|---|
| Retelling | Names, plot, world, unchanged | Too safe: no chaos |
| **Retelling plus a twist** | **Names, plot, world, famous moments, with one fact changed** | **Proposed** |
| Transposition | The plot, moved to a new world | Possible as a twist ("Macbeth, in a bakery") |
| Engine only | The core tension and shape | The earlier proposal, now replaced |

### Twists

A twist changes **one** known fact, and the scene takes it completely seriously (played
straight; see [09](09-story-quality.md)). Kinds of twist that work on almost any play:

| Kind | Example |
|---|---|
| Hidden identity | Macbeth has an identical twin he doesn't know about yet |
| Wrong object of love | Romeo is still in love with Rosaline, and Juliet is about to find out |
| Swapped roles | Lady Macbeth wants to call it all off; Macbeth is the one pushing |
| The dead aren't dead | Banquo survived, and is very annoyed |
| The trusted one lies | Hamlet's ghost is lying |
| New world | Romeo and Juliet, but the feud is between two rival bakeries |

More Romeo twists, as asked: Romeo is in love with Tybalt, the man he has to fight;
Romeo is in love with Juliet's Nurse; Romeo is in love with Lady Capulet. Rosaline is
the strongest because it is grounded in the original play, where Romeo loved Rosaline
before he met Juliet; fans get an extra layer.

### The catalogue: traditions, plays, moments (proposed)

The admin's catalogue now stores each play's plot, characters and **famous moments**
(the banquet, the balcony, the dagger), not only its engine. The scene is set at a moment,
altered by the twist.

| Tradition | Plays (public domain) |
|---|---|
| Shakespeare | Macbeth, Romeo and Juliet, Hamlet, Othello, King Lear, A Midsummer Night's Dream, Twelfth Night, The Tempest |
| Goethe | Faust (best known to German-speaking audiences) |
| Greek | Oedipus, Medea, Antigone, Lysistrata |
| Indian classics, for Bollywood | Devdas (1917 novel, the archetypal Bollywood story), Shakuntala, Laila and Majnu, Heer and Ranjha, episodes of the Ramayana and Mahabharata |
| Surreal and absurd | Ubu Roi (Jarry, 1896, itself a parody of Macbeth), Six Characters in Search of an Author (Pirandello), A Dream Play (Strindberg), Alice in Wonderland |

**Waiting for Godot is not public domain.** Beckett died in 1989 and his estate is
famously strict. The absurd plays above cover the same ground and are free to use.
Public-domain status varies by country, so the catalogue should hold only works that are
free everywhere shows run (as a rule of thumb, authors who died more than 70 years ago).

### Tradition and genre are separate choices

"Shakespeare" and "Goethe" are sources; "Bollywood" is a genre. Keeping them apart allows
combinations: **Macbeth as Bollywood** is a proven idea (Vishal Bhardwaj's film *Maqbool*
did exactly that; his *Omkara* is Othello and *Haider* is Hamlet). So a survey can pick
the play from one round and the genre from another.

### An example survey

1. **Whose world tonight?** Shakespeare · Goethe · Bollywood *(scripted by the admin)*
   → 60% Shakespeare, 40% Bollywood
2. **Which story, and what's wrong with it?** *(AI-written play-plus-twist options)*
   - Macbeth, who has an identical twin he doesn't know about yet
   - Romeo, still in love with Rosaline, and Juliet is about to find out
   - Hamlet, whose father's ghost is lying
3. **Which moment?** The banquet · the night before the battle · the letter arrives
4. A late pirate detail, if wanted ([04](04-brainstorm.md), the twist question)

The audience already knows the story, so revealing which play it is from the start is
part of the pleasure. The earlier question of hiding the source is settled.

## How a scene opens (decided)

**The improvisers know nothing. The host always opens with dialogue, and the improvisers
start with a task.**

Decided: the task is a mimed physical activity the improvisers are already doing
when the scene begins (folding laundry, waiting for a bus, icing a cake). Starting in the
middle of an activity is an old improv principle: it gives the improvisers something to do
before they know anything.

Proposed rules:

- **The AI writes the opening task** as part of the scene, one per improviser.
- **It fits the scene but reveals nothing**: no names, no relationship, no genre. "Icing a
  cake", not "icing your sister's wedding cake".
- **The script does not plan around it** (decided). The first line is written for the
  play, not to connect with the mime; the improvisers justify whatever happens.
- **The task is mimed** (decided): a physical activity, done in silence while the host
  reads the first delivery description, until the host says the first line. See
  [03](03-roles-and-surfaces.md).
- **It must be mimeable**: something physical and recognisable without props or words.
- How the improvisers receive the task is proposed in [03](03-roles-and-surfaces.md): the
  host shows them a task card on the phone before Start.

## Genre: the overarching register (decided idea; design proposed)

**Decided:** every play and scene has an overarching genre, from a list that is
effectively limitless: Shakespearean, Greek, Bollywood, soap opera, reality TV, surreal,
anime, and more (film noir, telenovela, Western, period drama, sitcom, musical theatre,
K-drama, courtroom drama, nature documentary, horror, superhero, kung fu film…).

### Three independent layers

| Layer | What it decides | Comes from |
|---|---|---|
| **Genre** | How it sounds and which conventions it follows | A genre card (catalogue) |
| **Source** | The story: plot, characters, famous moments | A known play (catalogue) |
| **Twist and choices** | What is changed, and the specifics | The room's votes |

They combine freely, and the combinations are where much of the comedy is: Macbeth, as
reality TV, with a twin he doesn't know about.

Genres often suggest their own twists (soap opera has the secret twin and the amnesia;
Greek tragedy has the prophecy), so a genre card can list twists that suit it.

### Genre lives in the dialogue and the delivery descriptions

With no narration, a genre can only show up in what the host says and how. Many genres
rely on conventions that are not dialogue; each one has to be translated into something
one person can perform:

| Genre | Convention | How the host performs it |
|---|---|---|
| Reality TV | Confessional to camera | Delivery description: "turning to the audience, confessional" |
| Soap opera | Dramatic zoom on a reveal | "freezing, staring into the distance" |
| Greek | The chorus | A line addressed to the audience as fate or the gods |
| Anime | Inner monologue, named attacks | "inner voice, to the audience"; a shouted name for an ordinary action |
| Bollywood | Family honour, the song that breaks out | Lines about honour; "beginning to sing" |
| Shakespearean | Verse, asides | Heightened language; "aside, to the audience" |

### Genre cards: limitless genres without new prompts (proposed)

Each genre is a card in the admin's catalogue, not a prompt:

- **Voice:** diction, rhythm, sentence length.
- **Conventions:** its tropes, and how each becomes dialogue or a delivery description.
- **Suggested twists.**
- **A few example lines**, which double as examples for the AI.

Adding a genre means adding a card. The AI programs take the card as an input, so they are
optimised once for every genre instead of once per genre.

### Conventions, not caricature (proposed)

Some genres come from real cultures (Bollywood, anime, telenovela). Write the genre's
conventions (the dramatic reveal, the family honour, the power of friendship), never the
people: no accents, no ethnic stereotypes. The cards and the checks enforce this.

## What makes a good scene (proposed rules for the prompt)

- **Every decision is paid off**, and the first few lines make them recognisable early.
- **The genre is recognisable from the first line**, through the host's dialogue and
  delivery descriptions.
- **Dialogue does all the work.** With no narration, the audience learns who these people
  are, where they are and what is going on from the dialogue alone: names, places and
  specific facts, written as a good play would carry them.
- **Lines are short** enough to sight-read; one or two sentences, with a few deliberate
  longer moments.
- **Delivery descriptions are short and actionable**, and can carry timing ("cutting them
  off", "after a long silence").
- **Written as a real two-sided scene.** The host's lines answer the ghost lines, as in any
  play. The script is deaf to what the improvisers actually say, and that is fine.
- **Nothing is optional** (decided). Every line will be delivered, so every line must earn
  its place: no filler, and exactly the number of lines the target length needs.
- **Beats, marked:** every line belongs to a beat (setup, escalation, turn, ending). This
  shapes the writing and lets the harness check the arc; the host doesn't see it.
- **A briefing for the host:** the scene comes with a short note of who the host's
  character is and what the play is about, only what they need to deliver the dialogue.

## Length (open)

The original brief targeted a 15-minute scene of 30 to 50 lines. With several sets per
show and rotating hosts, five to seven minutes per scene may fit better; a sketch usually
runs about five.

## Output (proposed)

Structured output: the play's context (title, what it is about), the characters (voiced or
withheld), then the ordered lines with the fields in [02-domain-model.md](02-domain-model.md).

## Generation time (proposed)

Writing a scene may take 20 to 40 seconds, which is dead air after the last vote. Since the
host reads line by line, the scene could stream: the host starts on the first line
while the rest is being written. Streaming structured output through DSPy is more awkward
than a plain API call, so measure generation time first; for a short scene, streaming may
not be needed.
