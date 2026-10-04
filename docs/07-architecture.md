# 07 — Architecture

**Decided:** Cloudflare as much as possible; GCP is available too.
Everything else in this document is **proposed** unless marked otherwise.

## The insight that simplifies everything

Once written, **the scene never changes**. So the live part of the app is not a
collaborative real-time system; it is one device (the host's) broadcasting a cursor.

- **During the brainstorm**, phones send votes and receive round changes.
- **During the scene**, every surface downloads the whole scene once and caches it. The sync
  channel carries only the cursor, a few bytes.
- **If the network drops mid-scene**, the host keeps going because the whole scene is on the
  device; followers show a stale line until they reconnect. Add a manual "jump to line"
  on followers, and a dropped connection becomes a shrug instead of a dead show.

The one unforgivable failure is the app going down on stage. With this design, the
failure is "a follower lags", never "the show stops".

## The shape

```
 phones (audience, host, followers)
        │  HTTPS + WebSocket
        ▼
 ┌──────────────────────── Cloudflare ─────────────────────────┐
 │  Worker: static frontend + API + routing                     │
 │     │                                                        │
 │     ├──▶ Durable Object, one per show: "the room"            │
 │     │      live state, votes, round timers, cursor,          │
 │     │      WebSocket fan-out to every phone                  │
 │     │            │                                           │
 │     │            ▼                                           │
 │     │      AI service (Python, DSPy) in a Container          │
 │     │            │                                           │
 │     │            ▼                                           │
 │     │      AI Gateway ──▶ Claude                             │
 │     │                                                        │
 │     ├──▶ D1: catalogue, survey plans, shows, archive, ratings│
 │     └──▶ R2: logs and datasets for the harness               │
 │  Access: protects the admin console                          │
 └──────────────────────────────────────────────────────────────┘
 GCP: backup host for the AI container (Cloud Run); compute for long harness runs
```

## Why a Durable Object fits so well

A Durable Object is a single-threaded object with its own storage that many clients
connect to. A show is exactly that: a room.

- **One writer, no conflicts.** Every vote and every cursor move goes through the same
  object, in order. This is principle 2 in [08](08-reliability-and-infrastructure.md) for
  free.
- **Round timers.** A Durable Object can set an alarm, so the server decides when a round
  closes ([04](04-brainstorm.md), "Round timing") without a separate scheduler.
- **Built-in storage** (SQLite per object). The cursor, ballots and event log live with the
  room and survive restarts, so everything resumes.
- **WebSockets with hibernation.** Hundreds of phones stay connected cheaply; the object
  sleeps between messages.
- **Placement.** An object can be created with a location hint, near the venue.

## Stack

| Part | Choice | Why |
|---|---|---|
| Frontend | **TypeScript, React + Vite**, served as Worker static assets | Mobile first, no install; one app with a route per surface, split so the audience bundle stays small. The largest ecosystem for gestures and animation, which the host and follow-along screens depend on |
| Build and dev | **Cloudflare Vite plugin** | Frontend, Worker and Durable Object in one Vite project; local dev runs on Cloudflare's own runtime |
| Live connection | **partysocket / partyserver** (Cloudflare's PartyKit libraries) | A WebSocket that reconnects with backoff and buffers messages, and a Durable Object base class for rooms |
| Offline host screen | **Service worker** (for example vite-plugin-pwa) | The app loads with no network; installed to the home screen, full screen |
| API and routing | **Cloudflare Worker** (TypeScript) | At the edge, near every phone |
| Live state and sync | **Durable Object per show**, WebSockets | See above. Replaces the earlier plan of a FastAPI server with SSE |
| Shared data | **D1** | Catalogue (genres, sources), survey plans, shows, finished scenes, ratings |
| Logs and datasets | **R2** | Every model input and output and every performance log, exported for the harness |
| AI service | **Python, FastAPI, DSPy, in a Cloudflare Container** | DSPy is Python; production runs the same programs the harness tunes. Containers are GA since April 2026 |
| Model access | **AI Gateway in front of Claude** | Logging of every call, retries, fallbacks, cost and latency analytics, with no code beyond a base URL |
| Admin auth | **Cloudflare Access** | A login in front of the admin console without writing auth code |
| Backup and batch | **GCP Cloud Run** | The same AI container image runs there unchanged if needed; long optimisation runs too |

### Why not run DSPy in a Python Worker

Python Workers exist and support packages such as FastAPI and Pydantic, but they run on
Pyodide, and DSPy pulls in a large dependency tree. A container runs ordinary Python with no
surprises. Revisit later if Python Workers prove able to run it.

### Why the AI service is a plain Docker image

The same image runs in a Cloudflare Container, on GCP Cloud Run, or on a laptop. If one
host has trouble, the others are a configuration change away. That portability is what
makes it safe to use a newer platform.

### One contract between TypeScript and Python

The AI service's inputs and outputs (questions, premise, scene, lines) are defined once as
Pydantic models. JSON Schema is generated from them, and TypeScript types from that, so the
two languages can't drift apart.

## Where each piece of data lives

| Data | Lives in | Why |
|---|---|---|
| Live show: rounds, ballots, decisions, scene, cursor, events | The show's Durable Object | Consistent, ordered, next to the connections |
| Catalogue, survey plans, list of shows | D1 | Shared across shows |
| Finished performances: scene, decisions, events, ratings | Copied from the Durable Object to D1 when a set ends | For the admin, and as harness data |
| Model calls, exported datasets | R2 (and AI Gateway logs) | Large, append-only, for the harness |
| Understudy scenes | D1 | Read when the AI fails |

### Data sketch

```
D1
  genres          id, name, voice, conventions, suggested_engines, example_lines
  sources         id, tradition, title, plot, characters, moments[], suggested_twists[]
  survey_plans    id, name, rounds (scripted questions and options; then AI slots)
  venues          id, name, city
  door_questions  id, venue_id (null = live), text, options, correct_option_ids[]
  shows           id, code, status, content_rating, survey_plan_id, venue_id,
                  door_question_ids[], created_by
  archive_sets    id, show_id, premise, scene, decisions, events, delivered_at[]
  ratings         set_id, score, notes
  understudies    id, genre_id, source_id, scene

Durable Object (per show)
  performers      id, name, device token                      -- the troupe, joined once per show
  sets            id, order, status
  casting         set_id, performer_id, role (host|improviser), character_id
  rounds          id, set_id, order, slot, source (scripted|ai), question, selection_mode,
                  opened_at, min_s, max_s, threshold, closes_at
  options         id, round_id, text, persona
  ballots         round_id, participant_id, option_ids[]
  decisions       round_id, option_ids[]
  scenes          set_id, premise, briefing, characters, opening_tasks, lines
  cursor          set_id, line_idx, seq
  events          set_id, seq, at, type, payload        -- append-only
```

## Access

- **Admin:** Cloudflare Access in front of the admin console.
- **Host:** a per-set token on the host device.
- **Audience:** join code, then the door check ([04](04-brainstorm.md)) and Turnstile. Passing
  issues a signed admission token for the show, kept on the phone and sent with every vote.
  No email, no phone number, no personal data.

## Repository layout

```
foreshadow/
  docs/
  app/         one Vite project: React frontend (all surfaces) + Worker + Durable Object
  ai/          AI service and harness (Python, uv): DSPy programs, FastAPI, metrics
  library/     the play library service (Python, uv): Gutenberg → parsed plays
  contracts/   Pydantic models → JSON Schema → TypeScript types
```

## Development loop: quick and sure

- **Deploy from day one.** The first thing built is a hello-world that goes through the
  whole path (Worker, Durable Object, Container, AI Gateway) to production.
- **A preview URL for every branch**, so every change can be tried on real phones at once.
- **CI on every push** (GitHub Actions): type checks, tests, then deploy.
- **Local development:** `wrangler dev` runs the Worker and Durable Object locally; the AI
  service runs in Docker.

## Build plan

End to end first, rough but complete (decided), then improve each piece. Each step is
deployed and tried on real phones before the next.

0. **The skeleton.** Repository, CI, preview deploys, and a hello-world through every piece
   of the infrastructure.
*Status: steps 0–2 are done as a rehearsal prototype (host a room, pick a scene from
the catalogue, others follow along); the show flow in step 3 is next.*

1. **Fake scene, real sync.** A hard-coded scene, the host screen with swipes, the
   follow-along screen, and the cursor through the Durable Object. The host is local-first,
   events carry sequence numbers and everything resumes after a reload, from the start.
2. **Real scenes catalogue** ([05](05-scene-writing.md), version 1). The play library
   ([10](10-play-library.md)): done for all 38 Shakespeare plays. Next: segments and
   performable scenes, and the first shortlist approved.
3. **Shows, sets, brainstorm.** Join flow, survey plans with scripted rounds only, voting,
   round timing with alarms, results on phones.
4. **Stage hardening.** Reconnects, manual cursor override, screen wake lock, real phones
   in a dark room, a simulated 30-person brainstorm.
5. **Version 1 live:** rehearse and perform with real scenes, learn what the format needs.
6. **Scene lab, then AI in the app** ([09](09-story-quality.md)): version 2 (a twist on a real
   scene), then version 3 (generated scenes). The DSPy programs in the container, through AI Gateway: adaptive rounds,
   premise, scene, the understudy fallback.
7. **Harness.** Metrics, simulated audiences, the human-rated set, GEPA runs.
8. **Rehearse with real people and iterate**, mostly on the prompts.

## Sources

- [Cloudflare Containers GA (April 2026)](https://developers.cloudflare.com/changelog/2026-04-13-containers-sandbox-ga)
- [Python Workers](https://developers.cloudflare.com/workers/languages/python/)
- [AI Gateway](https://developers.cloudflare.com/ai-gateway)
