"""library build | library publish

build:   fetch Gutenberg #100 (cached), parse every Shakespeare play, analyse, save, report.
publish: copy the built library into the app's static files.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .analyse import analyse, build_index
from .parsers import shakespeare
from .repository import FilePlayRepository, FileRawTextRepository
from .sources import gutenberg

ROOT = Path(__file__).resolve().parents[2]  # library/
DATA = ROOT / "data"
CACHE = ROOT / ".cache"
APP_LIBRARY = ROOT.parent / "app" / "public" / "data" / "library"


def build(refresh: bool) -> int:
    raw = FileRawTextRepository(CACHE)
    repo = FilePlayRepository(DATA)
    text, source = gutenberg.fetch(100, raw, refresh=refresh)
    works = shakespeare.split_works(gutenberg.strip_boilerplate(text))
    plays, problems = [], 0
    for title, body in works:
        play, report = shakespeare.parse_play(title, body, source)
        repo.save(analyse(play))
        plays.append(play)
        mark = "ok  " if report.ok else "WARN"
        two = sum(1 for s in play.scenes if s.stats and s.stats.two_hander)
        listed = report.scenes_in_contents if report.scenes_in_contents is not None else "?"
        print(f"{mark} {play.id:32} {report.scenes_found:3}/{listed:<3} scenes  {two:2} two-handers  {len(play.characters):3} characters  {len(report.notes):3} notes")
        for warning in report.warnings[:5]:
            print(f"       - {warning}")
        if len(report.warnings) > 5:
            print(f"       … and {len(report.warnings) - 5} more")
        problems += 0 if report.ok else 1
    repo.save_index(build_index(plays))
    print(f"\n{len(plays)} plays saved to {DATA}; {problems} with warnings.")
    return 0


def publish() -> int:
    if APP_LIBRARY.exists():
        shutil.rmtree(APP_LIBRARY)
    shutil.copytree(DATA, APP_LIBRARY)
    print(f"Published {DATA} → {APP_LIBRARY}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="library")
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="fetch, parse, analyse and save every play")
    b.add_argument("--refresh", action="store_true", help="download again instead of using the cache")
    sub.add_parser("publish", help="copy the built library into the app")
    args = parser.parse_args()
    sys.exit(build(args.refresh) if args.command == "build" else publish())
