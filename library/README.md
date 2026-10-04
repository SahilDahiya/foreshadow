# Foreshadow play library

Turns public-domain plays into structured data for the app. Design:
[../docs/10-play-library.md](../docs/10-play-library.md).

```
uv sync
uv run library build      # fetch Gutenberg #100 once (cached), parse all 38 plays, report
uv run library candidates # find and rank the stretches of scenes that suit the show
uv run library render-candidates   # write the strongest candidates in today's English
uv run library scenes     # turn rendered candidates into scenes the app can play
uv run library lab        # open the preference lab: A/B vote on renderings, improve the prompt
uv run library render macbeth/1/7   # write a scene in today's English with the champion prompt
uv run library publish    # copy the library into app/public/data/library
uv run pytest
```

Layout:

```
src/foreshadow_library/
  domain.py               the text-layer model (Pydantic)
  repository.py           raw-text and play repositories (files today)
  sources/gutenberg.py    fetch, cache, strip the Gutenberg boilerplate
  parsers/shakespeare.py  parser for the Gutenberg #100 edition
  analyse.py              scene stats, two-hander detection, the index
  perform.py              a rendered candidate → a scene in the app's format
  candidates.py           stretches that suit the show: two speakers, host opens and closes, sized
  render.py               today's-English rendering (a DSPy program; the prompt is its instruction)
  lab/                    the preference lab: passages, challenger proposer, rounds, local voting page
  cli.py                  build, render, lab and publish
lab/                      the lab's data, committed: prompts, rounds and your votes
data/                     generated, not committed
.cache/                   downloaded sources, not committed
```

The lab and rendering call Claude and need `ANTHROPIC_API_KEY`, read from the repository's `.env`.
Design: [../docs/11-preference-lab.md](../docs/11-preference-lab.md).
