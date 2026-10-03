"""library build | library render <scene id> | library lab | library publish

build:   fetch Gutenberg #100 (cached), parse every Shakespeare play, analyse, save, report.
render:  write a scene in today's English with Claude (needs ANTHROPIC_API_KEY, read from
         the repository's .env if present).
lab:     open the preference lab, to A/B vote on renderings and improve the prompt.
publish: copy the built library into the app's static files.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .analyse import analyse, build_index
from .parsers import shakespeare
from .repository import FilePlayRepository, FileRawTextRepository, FileRenditionRepository
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


def load_env() -> None:
    """Read KEY=value lines from the repository's .env without overriding the environment."""
    import os

    env = ROOT.parent / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def render(scene_id: str, model: str | None) -> int:
    from .lab import rounds
    from .render import render_scene

    load_env()
    play = FilePlayRepository(DATA).get(scene_id.split("/")[0])
    scene = next((s for s in play.scenes if s.id == scene_id), None) if play else None
    if play is None or scene is None:
        print(f"No such scene: {scene_id}. Run `library build` first, and use an id like macbeth/1/7.")
        return 1
    prompt = rounds.champion()  # the best prompt the lab has found so far
    rendition = render_scene(play, scene, prompt=prompt.text, prompt_version=prompt.id, model=model)
    FileRenditionRepository(DATA).save(rendition)
    print(f"Rendered {scene_id} with {rendition.model}, prompt {prompt.id}: {len(rendition.blocks)} blocks.")
    for warning in rendition.check_warnings:
        print(f"  check: {warning}")
    return 0


def lab(port: int, open_browser: bool) -> int:
    from .lab.server import serve

    load_env()
    serve(FilePlayRepository(DATA), port=port, open_browser=open_browser)
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
    r = sub.add_parser("render", help="write a scene in today's English")
    r.add_argument("scene_id", help="for example macbeth/1/7")
    r.add_argument("--model", help="override the model (default: claude-opus-5-5)")
    lab_parser = sub.add_parser("lab", help="open the preference lab")
    lab_parser.add_argument("--port", type=int, default=8765)
    lab_parser.add_argument("--no-browser", action="store_true")
    sub.add_parser("publish", help="copy the built library into the app")
    args = parser.parse_args()
    if args.command == "build":
        sys.exit(build(args.refresh))
    if args.command == "render":
        sys.exit(render(args.scene_id, args.model))
    if args.command == "lab":
        sys.exit(lab(args.port, not args.no_browser))
    sys.exit(publish())
