# Foreshadow app

One Vite project: the React frontend (every screen), the Cloudflare Worker, and the
`ShowRoom` Durable Object (one per show). See [../docs/07-architecture.md](../docs/07-architecture.md).

```
npm install
npm run dev          # local dev on Cloudflare's runtime (Worker + Durable Object + frontend)
npm run typecheck
npm run deploy       # build and deploy to Cloudflare
npm run cf-typegen   # regenerate worker types after changing wrangler.jsonc
```

Layout:

```
src/      React frontend
worker/   Worker entry (index.ts) and the ShowRoom Durable Object
```

Deployed at https://foreshadow.dahiya-sahil-89.workers.dev
