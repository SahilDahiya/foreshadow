# 03 — Roles and surfaces

## Roles (decided)

| Role | Scope | What they do | Access |
|---|---|---|---|
| **Admin** | The whole app, across shows | Special rights: creates shows, manages the catalogue and everything else | The only role with a real login |
| **Host** | One set | Hosting is reading. Watches the brainstorm live, then reads the scene cold: dialogue only, with delivery descriptions | The host device (proposed) |
| **Improviser** | One set | Plays a withheld character. Sees nothing of the script. | Does not use the app |
| **Audience member** | One show | Votes in each brainstorm round; sees questions and results on their own phone | QR code or short code, then the door check (below); no install, no account, no email or phone number |

- **Decided: improvisers can take turns hosting.** The same person can host one set and
  improvise in the next, so host and improviser are assignments per set, not identities.
- **Proposed: host access is per set.** Whoever hosted one set must not be able to see the
  scene for a set they improvise in.
- **Superseded: a single host device.** Every performer now has their own phone; see
  "Several hosts" below.
- **Decided: brainstorm results appear only on audience phones.** The improvisers can stay
  in the room during the brainstorm without learning the premise.
- The improviser is in the domain model (withheld characters are played by improvisers,
  and later transcripts will be attributed to them) but is not a user of the app.

## Several hosts, every performer with a phone (decided idea; design proposed)

**Decided idea:** a scene can have several hosts. The three witches are read by three
hosts, each from their own phone. Who hosts and who improvises changes from scene to
scene. Improvisers carry their phones in their pockets, not in their hands.

This replaces the single host device passed around the stage: **every performer joins
the show on their own phone** as a member of the troupe.

### Devices register as one of three kinds (decided)

**Audience**, **performer** or **admin**. A performer's phone is the same app in performer
mode: it can be made a host for a scene, or told what the scene needs from improvisers.

### Casting, scene by scene

- **Hosts are chosen at random** from the performers (decided), and each phone reveals it:
  "You're hosting: you are the FIRST WITCH."
- **One character per host** (decided). A scene with three voiced characters needs three
  hosts.
- **The other performers decide among themselves who goes on** (decided), once told how
  many improvisers the scene needs. The app can also pick at random if they want it to.
- **Each scene has a cast requirement**: which characters are read by hosts, and how many
  improvisers it needs: exactly one, exactly two, at least one, one or more.
- **Each host sees their own briefing and only their own lines.**
- **Everyone else is told what the scene needs**: "This scene needs exactly one
  improviser." Improvisers react; they don't need to know anything else.
- **Only scenes the troupe can cast are offered** to the audience: a scene needs at least
  one performer per voiced character plus its minimum number of improvisers, so a scene
  needing three hosts and two improvisers never appears for a troupe of four.

### What each phone does

| Performer | Before the scene | During the scene |
|---|---|---|
| **Host** | Their character and briefing; Start (or Ready) | Their own lines, prepare and deliver; waits while other hosts speak |
| **Improviser** | That the scene needs them; their own mime task, privately | In the pocket |

The mime task now goes to each improviser's own phone, instead of the host turning their
screen towards them.

### Taking turns between hosts

The script is one sequence of lines, and each line belongs to one host.

- **You can only deliver your line when it is next.** Until then your screen shows your
  upcoming line and who speaks before you ("after SECOND WITCH").
- **Prepare is private; deliver is shared.** When the line before yours is delivered, your
  screen moves to prepare, and you swipe to deliver when the moment comes.
- **Back undoes only your own last delivery.**
- Pacing becomes shared: each host controls the gap before their own lines.



A surface is a screen. Roles are people; surfaces are views.

### Host screen: read the line, choose the moment (decided goal; details proposed)

**Decided: the phone is not part of the play.** The improvisers ignore the phone in the
host's hand, and the script never mentions one ([05](05-scene-writing.md)).

**Decided: keep the host simple.** The host only delivers dialogue, with a description
of how to deliver it.

Before the scene, the **briefing** (decided):

- Who their character is, and what the play is about in general: only what is essential
  to deliver the dialogue.
- **The task card** (proposed): the host turns the phone to the improvisers, which shows
  only each improviser's mime task in big text ("ICING A CAKE"). Nothing else about the
  scene is visible.
- A **Start** button.

How the scene opens (decided):

```
Start ─▶ PREPARE line 1 ──────────────────────────▶ swipe ─▶ DELIVER line 1 ─▶ …
         host reads the delivery description           host says the first line
         in silence; improvisers mime their task
```

- After Start, the host is in the prepare phase of line 1, reading its delivery description
  silently. Meanwhile the improvisers begin miming their physical task.
- The host swipes into deliver and says the first line. The scene has begun.
- **The silent opening is the host's first pacing choice:** they decide how long the room
  watches the mime before the first line lands.

During the scene, **each line has two phases** (decided): prepare, then deliver.
**Showing the phase by screen colour (blue / yellow) is an idea, to design later.**

| Phase | Colour idea | What the host does | What the screen shows |
|---|---|---|---|
| **Prepare** | Blue | Reads the delivery description in silence and gets ready, while the improviser is talking | The description, large; the dialogue below it, so they can prepare it (proposed) |
| **Deliver** | Yellow | Says the dialogue aloud | The dialogue, huge; the description small above it |

The loop (decided; the gesture is proposed):

```
Start ─▶ PREPARE line 1 ─swipe─▶ DELIVER line 1 ─swipe─▶ PREPARE line 2 ─swipe─▶ DELIVER line 2 ─▶ …
```

- **Swiping into deliver means "I'm saying this now".** This is the only moment the
  audience screens move. The prepare phase is private to the host.
- **Swiping out of deliver means "I've said it".** The host moves to prepare the next line
  while the improviser answers.
- **Every line is delivered** (decided). Nothing in the script is optional, so there is no
  skip and no jump to the ending.

**The gesture is a swipe, not a tap** (proposed, following the owner's suggestion):

- **A swipe is deliberate.** A tap can come from gripping the phone, brushing the screen or
  a gesture while acting. Since a line can never be skipped, moving forward should take
  intent.
- **Swipe up: forward one phase.** The script moves up like a teleprompter, the same
  direction the audience's follow-along scrolls.
- **Swipe down: back one phase** (decided that going back is easy): deliver back to prepare
  for the same line, or prepare back to the previous deliver. Stepping back out of deliver
  tells the audience screens to undo the delivery.
- **Taps do nothing during the scene.** That removes accidental advances entirely.
- **One swipe moves one phase, however fast or long it is.** A flick can't pass a line
  unsaid; every line goes through deliver before the next can be reached.
- **The swipe counts on release**, once it has travelled far enough. A half-swipe that is
  let go springs back, so the host can change their mind mid-gesture.
- **Swipes start anywhere in the middle of the screen**, away from the edges, where the
  phone's own gestures live (home, back, notifications).
- **The host device runs the app installed to the home screen, full screen**, so the
  browser's own swipe-to-go-back can't fire mid-scene.
- Which direction feels right (up or sideways, like turning a page) is worth trying both
  ways in the first rehearsal.

- **Colour ideas, for later:** never show the phase by colour alone (add a label and a
  short vibration); use muted tones suited to a dark room.
- **The peek:** in blue, the line after this one is shown small at the bottom.
- **Ghost lines are not shown to the host** (proposed, to keep the screen simple).
- **No menus during the scene.** Settings sit behind a long press.
- **The phone never sleeps or locks** while the scene runs.
- **Pacing tools:** see "Pacing" below.
- After the last line, the swipe out of deliver ends the scene.

When to deliver the next line: see "Timing" below.

During the brainstorm:

- Each question and the live vote count as votes arrive, and one button to close the
  round. The host doesn't vote.

### Pacing: the host's real job (decided)

**The host paces the scene.** The script is the robot (order), the improvisers bring the
chaos, and the host decides how long each stretch of chaos runs before order returns.
In the terms of [01-vision.md](01-vision.md), **the host is the ninja.**

Pacing works at two levels:

| Level | What the host controls | How |
|---|---|---|
| **The gap** | How long the improviser runs before the next line | The swipe into deliver: entirely the host's choice |
| **The arc and the clock** | Whether the scene builds and lands on time | Letting gaps run long or keeping them tight |

**Decided: nothing in the script is optional, and the host's tools stay simple.** Every
line is delivered, as in the original show where the scripted actor read everything word
for word. The robot commits fully; the host's only lever is the gap.

Proposed design rules:

- **The app never paces for the host.** No auto-advance, no countdown, no nagging.
- **One small counter is the only pacing aid:** for example `12 / 30 · 4:10`, the line
  number, the total and the time elapsed. It tells the host both where they are in the
  scene and whether to stretch or tighten the gaps.
- **The host also paces the brainstorm** by closing each round from the host device.

Because every line is said, the scene's length is the number of lines plus the gaps. The
AI has to write the right number of lines, and the logged delivery time of every line,
from rehearsals and shows, is how we learn what that number is.

### Timing: when does the host deliver the next line? (proposed)

**The host's judgment, using ordinary turn-taking.** This is how the original show worked:
the scripted actor waited for the partner to finish, then said the next line. People do
this naturally in any conversation; the app doesn't need to tell them when.

The app's job is to make sure the line is already there when the moment comes, and to
support the judgment in three ways:

- **The next line is always ready.** The blue phase happens while the improviser is
  talking, so when the host's turn comes they are already prepared and only need to swipe
  and speak.
- **Delivery descriptions can carry timing.** "Cutting them off" or "after a long silence"
  tells the host when, not only how.
- **The counter** tells the host whether to leave the gaps long or tighten them.

Rules of thumb for hosts, taught before the show rather than shown on screen:

- Wait for the improviser to finish a thought.
- If they commit hard to something, come in right after: that is the punchline.
- If they are floundering or the scene drifts, come in sooner: that is the lifeline.
- Never speak over a laugh; wait for it to peak and start to fade.

Later, with speech sync, the app could notice when the improviser has stopped talking.
That is out of scope for the MVP.

### Audience brainstorm screen: vote and feel part of it (proposed)

- One question per screen, big options, one tap to vote.
- The result on their phone, with the split of votes; close votes are exciting.
- A waiting screen between rounds that builds anticipation instead of looking idle.

### Audience follow-along (decided goal; where it lives is open)

The audience can follow the full script. Whether that happens on their phones, on a
shared projector, or both, is still open.

If on phones (proposed):

- **Glance, don't read.** The current line stays at a fixed height, so a glance down finds
  it in under a second and eyes go straight back to the stage.
- **It scrolls itself**, in sync with the host; nobody touches it.
- **Dark and dim.** Eighty bright phones would ruin a dark room, so a dark theme is
  mandatory.

If on a projector (proposed):

- A scrolling script page laid out like a published play: delivered lines dimmed, the
  current line highlighted, upcoming lines visible below (the foreshadowing).
- Dialogue with character names; delivery descriptions small and in italics.
- During the brainstorm it shows only the join QR and a countdown.
- **Staging constraint:** the improvisers must not be able to see it, so it sits behind
  them or angled away.

On either surface:

- **Before the first line**, followers show the improvisers' mime tasks, so the audience
  knows what they are watching (proposed).
- **Ghost lines look visibly different**, so the room reads them as "what the improviser is
  supposed to say here". When they appear is open: ahead of time, when the gap opens, or
  after it closes. Proposed default: when the gap opens, as a show setting to try in
  rehearsal.

### Admin console (proposed)

Create shows, manage the catalogue of sources, set the content rating per show, view
logs and ratings.
