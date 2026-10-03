# Foreshadow play library

Turns public-domain plays into structured data for the app. Design:
[../docs/10-play-library.md](../docs/10-play-library.md).

```
uv sync
uv run library build      # fetch Gutenberg #100 once (cached), parse all 38 plays, report
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
  cli.py                  build and publish
data/                     generated, not committed
.cache/                   downloaded sources, not committed
```
