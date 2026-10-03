# Foreshadow — design docs

Foreshadow is an app for AI-scripted improv shows. Its flagship format is **Spoiler Alert**.

These documents record the design conversation held before any code was written.
Each document marks its points with one of three labels:

- **Decided**: settled by the project owner.
- **Proposed**: recommended during design but not yet confirmed.
- **Open**: still to be answered (collected in [open-questions.md](open-questions.md)).

| Doc | What it covers |
|---|---|
| [01-vision.md](01-vision.md) | What we're building and why: the philosophy, the inspiration, the core idea |
| [02-domain-model.md](02-domain-model.md) | The vocabulary and entities: Show, Set, Brainstorm, Scene, Line, Performance |
| [03-roles-and-surfaces.md](03-roles-and-surfaces.md) | Who uses the app, and the screens each one sees |
| [04-brainstorm.md](04-brainstorm.md) | How the audience shapes the scene: questions, options, voting, belief |
| [05-scene-writing.md](05-scene-writing.md) | How the AI writes the scene, and what makes a scene playable |
| [06-ai-pipeline.md](06-ai-pipeline.md) | The AI pipeline (survey, premise, scene) and optimising it with DSPy |
| [07-architecture.md](07-architecture.md) | Stack, sync, data and the build plan |
| [08-reliability-and-infrastructure.md](08-reliability-and-infrastructure.md) | Targets, failure modes, infrastructure, and how we prove it works |
| [09-story-quality.md](09-story-quality.md) | The critical risk: defining a compelling scene, and defending against a bad one |
| [10-play-library.md](10-play-library.md) | The internal service that turns public-domain plays into data the app uses |
| [open-questions.md](open-questions.md) | Everything still to decide |

Working principle (decided): get the whole system working end to end first, rough but
complete, then improve the individual pieces.
