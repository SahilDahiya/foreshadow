# Open questions

## Format

44. **Names in a modern world:** keep Macbeth and Lady Macbeth (recognisable), or give them
    modern names, as *Omkara* did?
45. **Violence in a modern world:** do events stay literal (Duncan is murdered, as in
    *Maqbool*) or become their modern equivalent (ousted in a boardroom coup)?
46. **Which worlds first?** Proposed: a tech company, a national government, a parliament,
    and as written.

41. **How modern?** Plain, faithful contemporary English (proposed), or looser and more
    colloquial?
42. **Do famous lines stay as Shakespeare wrote them** ("To be, or not to be")?
43. **Can the audience switch the follow-along screen to the original text?**

38. **Version 1 shortlist:** which scenes first? Proposed: the eight in
    [05-scene-writing.md](05-scene-writing.md), starting with Earnest and Macbeth.
39. **Cuts:** may scenes be lightly cut to fit the time, as long as nothing is rewritten?
40. **Does the room also choose which character the host plays,** or is it fixed per scene?

1. **Where does the audience follow along: on their phones, on a projector, or both?**
2. **When do ghost lines appear to the audience:** ahead of time, when the gap opens, or
   after it closes? Proposed: when the gap opens, as a show setting to try in rehearsal.
4. **Plays only, or also fairy tales and myths?**
5. **How long is one scene?** Five to seven minutes, or the original fifteen?
6. **Does the host play one character, or several?**
7. **With several improvisers, how does the dialogue tell each one who they are?** With no
   narration, the host's lines must name or address each withheld character.
8. **Is "Set" the right name** for one brainstorm, scene and performance inside a show?

## Brainstorm

36. **Which traditions and plays go in the first catalogue?** Proposed: Shakespeare first.
37. **Is Bollywood a tradition (Devdas, Shakuntala) or a genre applied to any play (Macbeth
    as Bollywood)?** Proposed: both are possible; keep them as separate rounds.

29. **Round timing defaults:** about 8 s minimum, 25 s maximum, close early at 85% of active
    phones or when the result can't change, then a 3 s last call. Right ballpark?
30. **Should voters ever see the live tally before the round closes?** Proposed: no; only
    "34 of 52 have voted".

26. **How do the improvisers receive their mime task?** Proposed: the host shows them a
    task card on the phone before Start. Should the audience also see it?

25. **How many twist questions per scene?** Proposed: one, asked late.

9. **What is an AI persona?** An author of options (Robot versus Pirate), a simulated
   audience member for the harness, or something else?
10. **Does "believe in it" mean ownership plus credibility**, or closer to "the script is
    fixed and the host isn't steering it"?
11. **Are adaptive questions core or optional?** Recommended: core.
12. **How many options win a multiple-selection round?**

## Running a show

## Technical

33. **Frontend framework:** proposed React + Vite with the Cloudflare Vite plugin (Svelte
    the main alternative). The choice changes none of the app's design.

31. **Cloudflare account:** is it on the Workers Paid plan (needed for Containers), and is
    there a domain to use?
32. **Claude access:** directly from Anthropic, or through Vertex AI on GCP?

18. **How big are audiences, and how many shows run at once?** Targets assume at least
    200 phones per show and a few shows at a time.
19. **Do venues have decent mobile signal?** The plan assumes audience phones mostly use
    their own data, not the venue wifi.

17. **Will there be early rehearsals with real people?** Their ratings make the harness
    trustworthy.

## Resolved

- **Who assigns hosts?** The app, at random. Devices register as audience, performer or
  admin.
- **Who improvises?** The performers who aren't hosting decide among themselves, told how
  many the scene needs; the app can pick at random if asked.
- **Several characters per host?** No: one character per host.

- **How close to the source?** Grounded in the known play (characters, plot, moments) with
  one twist chosen by the room. Replaces "engine only".
- **Is the audience told the play?** Yes, from the start; they choose it.

- **Is the host's phone part of the scene?** No. The improvisers ignore it and the play
  never mentions phones, screens or apps.


- **Who writes the door questions?** The admin, any multiple-choice question (for example,
  how many stairs you took to reach the show: 0, 5, −5, 8+).

- **Infrastructure:** Cloudflare as much as possible (Workers, Durable Objects, D1, R2,
  Containers, AI Gateway, Access); GCP for backup and batch work. TypeScript everywhere
  except the Python AI service.

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
