"""Project Gutenberg as a source: fetch once, cache, strip the boilerplate.

The plays are public domain; the Project Gutenberg name, header, footer and licence are
not ours to reuse, so everything outside the START/END markers is removed.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime

import httpx

from ..domain import Source
from ..repository import RawTextRepository

USER_AGENT = "foreshadow-library (one-time download of public-domain plays)"
START = re.compile(r"^\*\*\* START OF TH(E|IS) PROJECT GUTENBERG EBOOK.*\*\*\*\s*$", re.M)
END = re.compile(r"^\*\*\* END OF TH(E|IS) PROJECT GUTENBERG EBOOK.*\*\*\*\s*$", re.M)


def url_for(ebook_id: int) -> str:
    return f"https://www.gutenberg.org/cache/epub/{ebook_id}/pg{ebook_id}.txt"


def fetch(ebook_id: int, raw: RawTextRepository, *, refresh: bool = False) -> tuple[str, Source]:
    """The full ebook text and its provenance. Downloads only when not cached."""
    key = f"gutenberg/{ebook_id}.txt"
    meta_key = f"gutenberg/{ebook_id}.meta.json"
    text = None if refresh else raw.get(key)
    meta = None if refresh else raw.get(meta_key)
    if text is None or meta is None:
        response = httpx.get(url_for(ebook_id), headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=60)
        response.raise_for_status()
        text = response.text.replace("\r\n", "\n")
        meta = json.dumps({"retrieved_at": datetime.now(UTC).isoformat(timespec="seconds")})
        raw.put(key, text)
        raw.put(meta_key, meta)
    source = Source(
        provider="gutenberg",
        ebook_id=ebook_id,
        url=url_for(ebook_id),
        retrieved_at=json.loads(meta)["retrieved_at"],
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )
    return text, source


def strip_boilerplate(text: str) -> str:
    start, end = START.search(text), END.search(text)
    if not start or not end:
        raise ValueError("Project Gutenberg START/END markers not found")
    return text[start.end() : end.start()].replace("\r\n", "\n")
