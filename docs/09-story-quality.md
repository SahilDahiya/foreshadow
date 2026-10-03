# 09 — Story quality: the critical risk

**Decided:** the AI has to write a really compelling story. A dull, generic or cringe
scene, read aloud in front of a room that voted for it, is the most likely way this
format embarrasses everyone. "Compelling" therefore has to be **defined**, not hoped for.

Everything below is **proposed** until the owner confirms it.

## One definition, used three ways

The definition of a compelling scene is written once, as a short standard with examples,
and used as:

1. **The writing guidance** inside the scene-writing prompt.
2. **The judge's rubric**, which scores every scene before anyone sees it.
3. **The rating sheet** people use in rehearsals and after shows.

If the three ever disagree, the human ratings win, and the other two are corrected.

## What compelling means here

The scene is judged from the audience's seat. Its job is not to be funny on its own; the
collision with the improvisers provides most of the comedy. Its job is to be **a story the
room wants to see happen**.

| # | Criterion | Passes | Fails |
|---|---|---|---|
| 1 | **Want, now** | The host's character wants something specific and urgent, clear within three lines | Characters chat; nobody needs anything |
| 2 | **Obstacle** | The other character stands in the way, or holds the key | Everyone agrees; conflict resolved early |
| 3 | **Escalation** | Every host line raises the stakes or reveals something | Lines repeat the same beat; the middle sags |
| 4 | **Specific** | Concrete, surprising details: a swan in the freezer | "I feel so betrayed"; generic places and feelings |
| 5 | **The room's choices are the engine** | Every decision drives the plot | Mentioned once and dropped |
| 6 | **A turn** | A reveal that changes what the scene was about | It ends where it started |
| 7 | **A button** | The last line lands with a sting | A soft, hedged or moral ending |
| 8 | **A heart** | A real feeling under the plot: MARGOT wants to be seen | All mechanism, no person |
| 9 | **Played straight** | The genre is committed to, sincerely | The script tries to be funny: puns, winks, randomness |
| 10 | **Speakable** | Short lines with rhythm, good aloud and read cold | Long, written-sounding sentences |

### Played straight (open, recommended)

The script is the robot, and the robot should be **sincere**. Comedy comes from the
improvisers justifying, and from the audience's absurd choices taken seriously. A script
that tries to be funny competes with the improvisers, and AI attempts at jokes are where
cringe lives. Recommended: the scene is written as committed drama in its genre.

### Known AI failure modes to design against

Clichés ("little did they know"), characters announcing their feelings, therapy-speak,
exposition dumps, everyone being reasonable, conflict resolved too soon, soft or moral
endings, randomness standing in for humour, puns, mention-and-drop of choices, repetition,
and every scene having the same shape (repeat audiences notice).

## Defence in depth

No single call can guarantee quality, so the risk is reduced at every stage.

0. **Ground it in a known play** ([05](05-scene-writing.md)). A proven plot, characters and
   famous moments, with one twist, give the AI far less room to fail than an invented story.
1. **Upstream: good inputs.** Bad options make bad scenes. The brainstorm offers options
   that are story-productive; the admin scripts the opening rounds; genre cards and the source
   play give strong structure. The narrower and richer the inputs, the more reliable the
   output.
2. **Plan before writing.** Premise, then a beat outline (want, obstacle, escalation, turn,
   button, payoffs), then lines. Structure is decided before words.
3. **Several candidates, best one wins.** Write three to five scenes in parallel and let the
   judge pick. In parallel, it takes about as long as writing one.
4. **A quality gate.** If the best candidate scores below the bar: one revision using the
   judge's feedback, and if that fails, the understudy scene.
5. **Understudy scenes.** Hand-approved by the owner, matched as closely as possible to
   the room's choices. Losing some ownership beats an embarrassing scene.
6. **The strongest model for the scene.** Quality over speed here; the reveal and the mime
   opening cover some of the wait.
7. **Optional emergency brake.** The admin, if present, sees the chosen scene's logline and
   score and can switch to the understudy. Off by default, since the host reads cold.

## Measuring it

- **Before going live:** run 50 simulated brainstorms, read the scenes, and count how many
  the owner would happily perform. Go live only above an agreed bar (for example 9 in 10).
- **After every show:** the host rates the scene, and the audience gets a one-tap rating
  on their phones when the scene ends. Real rooms are the final judge, and the data feeds
  the harness ([06](06-ai-pipeline.md)).

## Version 1 sidesteps the risk

The first version performs real scenes from public-domain plays as written
([05](05-scene-writing.md)), so the story-quality risk only arrives with version 2. By
then the format, the screens and the room's reactions will have been tested with
material that is already good, and real scenes become the bar AI scenes must meet.

The one AI job in version 1, rendering scenes in today's English, is low risk for the
same reason: the story is fixed, only the language changes, and every rendition is
approved by a person before a show ([10](10-play-library.md)).

## De-risk it before AI goes live

This is the riskiest assumption in the project, so it is tested before more of the app is
built: a **scene lab** that generates scenes from sample brainstorms, outside the app, for
the owner to read aloud, rate and iterate on until the bar is met. See the build plan in
[07](07-architecture.md).

## What the owner decides

1. The criteria above: keep, cut, add.
2. **Reference scenes**: five to ten scenes, sketches or films the owner loves (and a few
   they hate), to anchor taste. Taste can't be derived; it has to be given.
3. **Played straight**, or should the script itself be funny?
4. **The bar** for going live.
5. **Cost:** several candidates per scene on the strongest model costs more per scene
   than one call on a fast model. Is that acceptable?
