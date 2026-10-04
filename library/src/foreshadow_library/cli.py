"""library build | library candidates | library render-candidates | library render <scene id> | library lab | library publish

build:   fetch Gutenberg #100 (cached), parse every Shakespeare play, analyse, save, report.
candidates: find the stretches of scenes that suit the show (two speakers, host opens and
         closes), ranked, and save them.
render-candidates: write the strongest candidates in today's English, for judging them.
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


def candidates_command() -> int:
    import json

    from .candidates import find

    repo = FilePlayRepository(DATA)
    plays = [p for p in (repo.get(i) for i in repo.list_ids()) if p]
    found, counts = find(plays)
    (DATA / "candidates.json").write_text(
        json.dumps({"counts": counts, "candidates": [c.model_dump(mode="json") for c in found]}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    scenes = len({c.scene_id for c in found})
    print(f"{counts['scenes']} scenes → {counts['two_speaker_runs']} two-speaker runs → {counts['pieces']} pieces → {len(found)} candidates, from {scenes} scenes in {len({c.play_id for c in found})} plays.")
    for size in ("small", "medium", "big"):
        of_size = [c for c in found if c.size == size]
        print(f"\n{size}: {len(of_size)}")
        for c in of_size[:6]:
            print(f"  {c.score:5.1f}  {c.metrics.minutes:4.1f} min  {c.play_title} {c.scene_id.split('/', 1)[1]}: {c.host_name.title()} (host) and {c.partner_name.title()}")
    return 0


def render_candidates(small: int, medium: int, big: int) -> int:
    """Render the strongest candidates in today's English with the lab's champion prompt.

    One rendering per scene covers every chosen candidate in it (cuts and both host
    choices share the same text), saved as a stretch: renditions/<scene>/stretch-<a>-<b>.json.
    """
    import json
    from concurrent.futures import ThreadPoolExecutor
    from datetime import UTC, datetime

    from .domain import Candidate, Rendition
    from .lab import rounds
    from .render import check, language_model, model_name, render_passage_detailed

    load_env()
    repo = FilePlayRepository(DATA)
    found = [Candidate.model_validate(c) for c in json.loads((DATA / "candidates.json").read_text(encoding="utf-8"))["candidates"]]
    chosen: list[Candidate] = []
    for size, n in (("big", big), ("medium", medium), ("small", small)):
        scenes: set[str] = set()
        for c in found:  # best first
            if c.size == size and c.scene_id not in scenes and len(scenes) < n:
                scenes.add(c.scene_id)
                chosen.append(c)
    spans: dict[str, tuple[int, int]] = {}
    for c in chosen:
        a, b = spans.get(c.scene_id, (c.start, c.end))
        spans[c.scene_id] = (min(a, c.start), max(b, c.end))
    index_path = DATA / "stretch_renditions.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else []
    have = {(e["scene_id"], e["start"], e["end"]) for e in index}
    todo = [(s, a, b) for s, (a, b) in spans.items() if not any(hs == s and ha <= a and hb >= b for hs, ha, hb in have)]
    prompt = rounds.champion()
    print(f"{len(chosen)} candidates in {len(spans)} scenes; {len(todo)} stretches to render with prompt {prompt.id} on {model_name()}.")
    plays: dict = {}

    def one(job: tuple[str, int, int]) -> dict | None:
        scene_id, start, end = job
        play_id = scene_id.split("/")[0]
        play = plays.setdefault(play_id, repo.get(play_id))
        scene = next(s for s in play.scenes if s.id == scene_id)
        for attempt in range(2):  # a rendering out of step with the original gets one more try
            try:
                blocks, prediction = render_passage_detailed(play, scene, start, end, prompt=prompt.text, lm=language_model())
            except Exception as error:
                print(f"  {scene_id}: {type(error).__name__}")
                continue
            warnings = check(scene, start, end, blocks)
            if not any(w.startswith("blocks out of step") for w in warnings):
                rendition = Rendition(
                    id=f"{scene_id}#{start}-{end}", play_id=play_id, scene_id=scene_id, world="original",
                    language="todays-english", model=model_name(), prompt_version=prompt.id,
                    created_at=datetime.now(UTC).isoformat(timespec="seconds"), blocks=blocks, check_warnings=warnings,
                )
                path = DATA / "renditions" / scene_id / f"stretch-{start}-{end}.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(rendition.model_dump_json(), encoding="utf-8")
                usage = next(iter((prediction.get_lm_usage() or {}).values()), {})
                return {"scene_id": scene_id, "start": start, "end": end, "file": f"renditions/{scene_id}/stretch-{start}-{end}.json",
                        "prompt": prompt.id, "tokens_in": usage.get("prompt_tokens", 0), "tokens_out": usage.get("completion_tokens", 0)}
        print(f"  {scene_id}: could not be rendered in step with the original")
        return None

    with ThreadPoolExecutor(max_workers=6) as pool:
        done = [r for r in pool.map(one, todo) if r]
    index += done
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    tokens_in, tokens_out = sum(r["tokens_in"] for r in done), sum(r["tokens_out"] for r in done)
    # Claude Opus 5.5: $4 per million input tokens, $20 per million output tokens.
    print(f"Rendered {len(done)} of {len(todo)}. {tokens_in:,} tokens in, {tokens_out:,} out: about ${tokens_in * 4e-6 + tokens_out * 20e-6:.2f}.")
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
    sub.add_parser("candidates", help="find and rank the stretches of scenes that suit the show")
    rc = sub.add_parser("render-candidates", help="write the strongest candidates in today's English")
    rc.add_argument("--small", type=int, default=30)
    rc.add_argument("--medium", type=int, default=20)
    rc.add_argument("--big", type=int, default=9)
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
    if args.command == "candidates":
        sys.exit(candidates_command())
    if args.command == "render-candidates":
        sys.exit(render_candidates(args.small, args.medium, args.big))
    if args.command == "render":
        sys.exit(render(args.scene_id, args.model))
    if args.command == "lab":
        sys.exit(lab(args.port, not args.no_browser))
    sys.exit(publish())
