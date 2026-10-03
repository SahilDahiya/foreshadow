# 08 — Reliability, speed and infrastructure

**Decided:** design, architecture and infrastructure are all critical. The app must be
reliable and fast, and the infrastructure solid.

Everything below is **proposed** unless marked otherwise.

## Where it matters most

Everything should be good, but not everything carries the same risk, so effort is ranked.

| Tier | What | Standard |
|---|---|---|
| **0: on stage** | The host advancing lines; followers staying in sync | Must never stop the show |
| **1: in front of the audience** | Joining, voting, moving between rounds, writing the scene | Fast, and recovers by itself |
| **2: offstage** | Admin console, catalogue, harness, ratings | Solid, but a failure costs no show |

## Targets

| Moment | Target |
|---|---|
| Host swipes → host screen shows the next line | Instant: no network on this path |
| Host swipes → followers update | Under 250 ms (95th percentile) on venue wifi |
| Scan QR → first question visible | Under 3 s on 4G |
| Tap a vote → acknowledged | Instant on the phone; server under 200 ms |
| One round → the next | No visible wait (next question written ahead) |
| Last vote → scene ready | Under 15 s; hard time limit, then fallback |
| Audience per show | At least 200 phones |

Scale is small: a few hundred phones, a few shows at once. The hard problem is one room
working perfectly, not millions of users. So we engineer for reliability, not for scale.

## Principles

### 1. The host is local-first

The host device holds the whole scene. Advancing changes the screen immediately and then
tells the server. If the network is gone, the host carries on and the device catches the
server up when it returns. The network is never between the host and their next line.

### 2. One writer per set

Only the host device moves the cursor. Each event carries a sequence number and is
idempotent, so repeated or late messages can't scramble the order. With a single writer
there are no conflicts to resolve.

### 3. Everything can resume

The cursor and events live in Postgres. Any screen that reloads, any phone that
reconnects and the server after a restart all resume at the exact line. SSE clients
reconnect with the last event id they saw and receive what they missed.

### 4. There is always an understudy scene

Each source in the catalogue has pre-written backup scenes, prepared offstage. If the
LLM is slow, down, or returns something that fails its checks, the show goes on with the
closest understudy, and the audience sees a scene instead of an error.

### 5. Nothing slow sits on the request path

Writing the scene runs as a background task with a hard time limit. Progress reaches
the host over SSE. Questions for the next round are written ahead while voting is open,
and the first round's question doesn't depend on any vote, so it is prepared before the
set starts.

### 6. Generated text is checked before anyone sees it

Structured output is validated, and the code-checkable metrics from the harness (line
length, line count, names present, beats in order) run as a gate. A failure triggers one
rewrite, then the understudy.

## Failure modes

| Failure | What happens |
|---|---|
| Venue wifi dies | The host continues from the local scene. Audience phones mostly use their own mobile data. The host device should have mobile data too, with a hotspot as backup. |
| Server restarts mid-scene | The state is in Postgres; clients reconnect and resume. No deploys during show times. |
| LLM slow or down | Time limit, one retry, then the understudy scene. |
| LLM output fails checks | One rewrite, then the understudy scene. |
| Host phone locks, crashes or runs flat | Screen wake lock while performing. On reload, the host screen resumes from local storage or the server. A second device can take over with the same set token. |
| Repeated swipes, late messages | Sequence numbers and idempotent events. |
| Someone votes twice | One ballot per participant per round; a new vote replaces the old one. |
| Clocks disagree | The server decides when a round closes. |

## Infrastructure

| Part | Choice | Why |
|---|---|---|
| App server | **One long-running container** (Python, FastAPI) on a host like Fly.io, in the region where shows happen | SSE needs long-lived connections and generation needs long tasks; serverless platforms are poor at both. One instance needs no message bus for fan-out. |
| Database | **Managed Postgres** with backups | The source of truth for resuming. |
| Frontend | **Static files on a CDN**, with a service worker caching the app | Fast first load; the host screen reloads even without a network. The audience bundle stays tiny. |
| Scale-out, if ever needed | Postgres LISTEN/NOTIFY or Redis for fan-out between instances | Not needed at this size. |

## Seeing what is happening

- **Error tracking** (for example Sentry) on the server and on every screen.
- **Structured logs** for every show, which also feed the harness.
- **A live show panel** for the admin: connected phones, sync delay, round status, scene
  writing progress.
- **Uptime checks** on the server and on the LLM provider.

## Proving it works

- **Load test** with simulated audiences: 200 phones joining and voting at once. The
  harness's simulated audience personas can drive it.
- **Chaos rehearsal:** turn off wifi mid-scene, restart the server, slow the LLM down, kill
  the host's browser, and confirm the show carries on each time.
- **Preflight screen** before every show: host device checks (wake lock, connection,
  battery), the LLM is reachable, understudy scenes exist for the catalogue.
- **CI with tests, a staging copy, and a deploy freeze during shows.**

## Fitting this into "end to end first"

Some reliability work is cheap at the start and expensive to add later, so it goes in
from step 1: the local-first host, sequence numbers on events, the cursor stored in the
database, resuming on reconnect, time limits on the LLM, and the understudy scene.

Other work can wait until the system runs end to end: the live show panel, the load test,
the chaos rehearsal, and scale-out.
