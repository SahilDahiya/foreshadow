# 07 — Architecture

Everything in this document is **proposed** unless marked otherwise.

## The insight that simplifies everything

Once written, **the scene never changes**. So the live part of the app is not a
collaborative real-time system; it is one device (the host's) broadcasting a cursor.

- **During the brainstorm**, audience phones need a form submission and a check for "has
  the round changed?" every couple of seconds.
- **During the scene**, every surface downloads the whole scene once and caches it. The sync
  channel carries only the cursor, a few bytes.
- **If the network drops mid-scene**, the host keeps going because the whole scene is on the
  device; followers show a stale line until they reconnect. Add a manual "jump to line"
  on followers, and a dropped connection becomes a shrug instead of a dead show.

The one unforgivable failure is the app going down on stage. With this design, the
failure is "a follower lags", never "the show stops".

## Stack

| Part | Choice | Why |
|---|---|---|
| Backend | **Python, FastAPI** | DSPy is Python; production runs the same programs the harness tunes |
| Live sync | **Server-Sent Events** for the cursor, plain HTTP POSTs for actions | One direction is enough; SSE reconnects by itself and survives venue proxies that break WebSockets |
| Database | **Postgres** | Shows, sets, ballots, scenes, events and ratings |
| Frontend | **TypeScript** web app, mobile first | Audience joins with no install; the host screen is the most demanding UI in the app |
| LLM | Claude API, through DSPy | |
| Hosting | One long-running container plus managed Postgres; static frontend on a CDN | See [08-reliability-and-infrastructure.md](08-reliability-and-infrastructure.md) |

Alternatives considered: Next.js on Vercel with Supabase (simpler, but the generation would
live in TypeScript away from DSPy); Partykit or Durable Objects (a show is a room, a good fit,
but a new deploy model for a sync problem that turns out to be small); a laptop server with
its own hotspot (strongest on bad venue wifi, worth revisiting once we know the venues).

## Data (sketch)

```
admins          id, login
genres          id, name, voice, conventions, suggested_engines, example_lines
sources         id, title, engine (tension, arc shape, devices)
shows           id, code, status, content_rating, created_by
sets            id, show_id, order, status, improviser_count, host_token
survey_plans    id, name, rounds (scripted questions and options; then AI slots)
rounds          id, set_id, order, slot, source (scripted|ai), question, selection_mode, closes_at
options         id, round_id, text, persona
ballots         id, round_id, participant_id, option_ids[]
decisions       round_id, option_ids[]
scenes          id, set_id, play_context, briefing, characters, model_io
lines           scene_id, idx, character, text, cue, voiced, beat
performances    set_id, cursor, updated_at
events          set_id, at, type, payload        -- append-only
ratings         scene_id, score, notes
```

`model_io` and the event log exist for the harness: every input and output is kept.

## Access

- Admin: real login.
- Host: a per-set token on the host device.
- Audience: join code; anonymous participant id in a cookie.

## Build plan

End to end first, rough but complete (decided), then improve each piece.

1. **Fake scene, real sync.** A hard-coded scene, the host screen, the follow-along screen
   and the SSE cursor. No AI yet, but the host is local-first, events carry sequence
   numbers and the cursor resumes after a reload, from the start. This proves the
   screens that are the product.
2. **Shows, sets, brainstorm.** Database, join flow, rounds with hard-coded questions,
   voting, results on phones.
3. **AI.** QuestionWriter and SceneWriter as DSPy programs, adaptive rounds, premise to scene.
4. **Stage hardening.** Reconnects, manual cursor override, screen wake lock, testing on real
   phones in a dark room, a simulated 30-person brainstorm.
5. **Harness.** Metrics, simulated audiences, the human-rated set, GEPA runs.
6. **Rehearse with real people and iterate**, mostly on the prompts.
