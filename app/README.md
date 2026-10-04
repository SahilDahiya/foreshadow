# Foreshadow app

One Vite project: the React frontend (every screen), the Cloudflare Worker, and the
`ShowRoom` Durable Object (one per show). See [../docs/07-architecture.md](../docs/07-architecture.md).

```
npm install
npm run dev          # local dev on Cloudflare's runtime (Worker + Durable Object + frontend)
npm run typecheck
npm test             # unit tests (vitest)
npm run deploy       # build and deploy to Cloudflare
npm run cf-typegen   # regenerate worker types after changing wrangler.jsonc
```

Layout:

```
src/      React frontend: host/ (host screen), watch/ (follow-along), room.ts (connection)
worker/   Worker entry (index.ts) and the ShowRoom Durable Object
shared/   Code used by both: scene types, the demo scene, the sync protocol
```

Deployed at https://foreshadow.dahiya-sahil-89.workers.dev

- Host a scene: the home page makes a room code, or go to `/host/<code>`; pick a scene from the catalogue
- Follow along: `/watch/<code>`
- Play library: `/library` (data from `../library`: run `library build` and `library publish` first)

Any name works in place of `demo`; each name is its own room.
