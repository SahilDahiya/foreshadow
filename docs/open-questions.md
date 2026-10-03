# Open questions

## Format

1. **Where does the audience follow along: on their phones, on a projector, or both?**
2. **When do ghost lines appear to the audience:** ahead of time, when the gap opens, or
   after it closes? Proposed: when the gap opens, as a show setting to try in rehearsal.
3. **How close to the source play?** Proposed: borrow only its engine (core tension and
   arc shape); everything else original. Owner's lean: as original as possible.
4. **Plays only, or also fairy tales and myths?**
5. **How long is one scene?** Five to seven minutes, or the original fifteen?
6. **Does the host play one character, or several?**
7. **With several improvisers, how does the dialogue tell each one who they are?** With no
   narration, the host's lines must name or address each withheld character.
8. **Is "Set" the right name** for one brainstorm, scene and performance inside a show?

## Brainstorm

29. **Round timing defaults:** about 8 s minimum, 25 s maximum, close early at 85% of active
    phones or when the result can't change, then a 3 s last call. Right ballpark?
30. **Should voters ever see the live tally before the round closes?** Proposed: no; only
    "34 of 52 have voted".

26. **How do the improvisers receive their mime task?** Proposed: the host shows them a
    task card on the phone before Start. Should the audience also see it?

23. **Is the audience told which play inspired the scene?** Never, up front, or as a reveal
    after the scene ("you just wrote Macbeth")?
24. **Who picks the source play:** the room, the admin per show, or chosen at random?
25. **How many twist questions per scene?** Proposed: one, asked late.

9. **What is an AI persona?** An author of options (Robot versus Pirate), a simulated
   audience member for the harness, or something else?
10. **Does "believe in it" mean ownership plus credibility**, or closer to "the script is
    fixed and the host isn't steering it"?
11. **Are adaptive questions core or optional?** Recommended: core.
12. **How many options win a multiple-selection round?**

## Running a show

20. **Who sets the target length of a scene: the admin per show, or the host per set?**
21. **Is the target length a soft guide, or a hard limit?** Proposed: a soft guide; the host
    always decides.

13. **Who starts each set: the host from the host device, or the admin?** Proposed: the host.
14. **Where will shows run, and how reliable is the wifi?** This decides between hosted and
    a laptop server with a hotspot.
15. **Is the host's own judgment the right answer to "when do I deliver the next line?"**
    Proposed in [03-roles-and-surfaces.md](03-roles-and-surfaces.md#timing-when-does-the-host-deliver-the-next-line-proposed).

## Technical

18. **How big are audiences, and how many shows run at once?** Targets assume at least
    200 phones per show and a few shows at a time.
19. **Do venues have decent mobile signal?** The plan assumes audience phones mostly use
    their own data, not the venue wifi.

16. **Python backend (FastAPI) with a TypeScript frontend**, or a TypeScript app calling a
    separate Python service for generation?
17. **Will there be early rehearsals with real people?** Their ratings make the harness
    trustworthy.

## Resolved

- **What is the opening task?** A mimed physical activity, done while the host silently
  reads the first delivery description; then the host swipes and says the first line.

- **Who picks the genre?** The admin can script the first few rounds (typically the genre),
  and the AI takes over from there.
- **Do the improvisers know the genre?** No. They know nothing; the host opens with
  dialogue and the improvisers start with a task.
- **Style or genre?** Genre.

- **Can the host skip lines or jump to the ending?** No. Nothing is optional; every line
  is delivered. Pacing is the gaps alone.
- **Does the host see the beats of the arc?** No; keep it simple. One small counter
  (line, total, time elapsed) instead.

- **Does the host read narration and direction?** No. Dialogue only, each line with an
  optional delivery description.
- **Does the host see ghost lines?** Proposed no, to keep the host screen simple.
- **What does the host see before the scene?** A briefing: their character and what the
  play is about, only what is essential to deliver the dialogue, then a Start button.
