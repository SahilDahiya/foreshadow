"""Run the language-transformation eval for one variant of the rendering prompt.

    uv run python -m foreshadow_library.evals.run --variant baseline
    uv run python -m foreshadow_library.evals.run --variant v1 --reps 2

Each (case, rep) renders the passage with the variant's prompt through the app's real
entry point (render.render_passage_detailed), runs the code checks, and has the judge
compare it, blind, with a frozen reference rendering. Rows are written as they complete;
re-running resumes where it stopped. Layout and field names follow the hill-climb
report contract: <flow>/<variant>/{results.jsonl, errors.jsonl, traces/, prompt.txt}.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path

import anthropic
import dspy

from ..cli import DATA, load_env
from ..domain import RenderedBlock
from ..render import check, model_name, passage_as_prompt, render_passage_detailed
from ..repository import FilePlayRepository
from . import cases as case_set
from . import judge as judging

REPO = Path(__file__).resolve().parents[4]
FLOW = REPO / ".claude" / "hillclimb" / "language"
LIBRARY = Path(__file__).resolve().parents[3]
VARIANT_NAME = __import__("re").compile(r"^(baseline|v\d+)$")


# --- helpers ----------------------------------------------------------------------------
def as_text(blocks: list[RenderedBlock], speakers: dict[int, str | None]) -> str:
    """A rendering as the judge and the trace show it: SPEAKER, then one line per row."""
    out: list[str] = []
    for block in blocks:
        speaker = speakers.get(block.source_block)
        if speaker:
            out.append(f"{speaker}:")
        out += [f"  {p.text}" if p.kind == "line" else f"  ({p.text})" for p in block.parts]
    return "\n".join(out)


def original_text(scene, start: int, end: int) -> tuple[str, dict[int, str | None]]:
    speakers: dict[int, str | None] = {}
    out: list[str] = []
    for i in range(start, end):
        block = scene.blocks[i]
        if block.kind == "direction":
            speakers[i] = None
            out.append(f"  ({block.text})")
        else:
            speakers[i] = block.speaker_label
            out.append(f"{block.speaker_label}:")
            out += [f"  {p.text}" if p.kind == "line" else f"  ({p.text})" for p in block.parts]
    return "\n".join(out), speakers


def state() -> dict:
    return json.loads((FLOW / "_state.json").read_text(encoding="utf-8"))


def harness_sha() -> str:
    """A change detector over the runner, the judge, the cases and the lockfile."""
    paths = [Path(__file__), LIBRARY / "uv.lock"] + [REPO / p for p in state().get("harness_paths", [])]
    digest = hashlib.sha256()
    for path in sorted(set(paths)):
        digest.update(str(path.relative_to(REPO)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def check_harness(approve: bool) -> None:
    current, st = harness_sha(), state()
    if approve:
        st["harness_sha"] = current
        (FLOW / "_state.json").write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
        print(f"Harness approved: {current[:12]}")
        return
    if st.get("harness_sha") != current:
        print(
            "The eval harness (runner, judge, cases or lockfile) changed since it was last approved.\n"
            "Review the change, then approve it yourself with:\n"
            "  uv run python -m foreshadow_library.evals.run --approve-harness",
            file=sys.stderr,
        )
        sys.exit(2)


# --- one case ---------------------------------------------------------------------------
class Runner:
    def __init__(self, variant: str, prompt: str, reference_dir: Path, model: str | None):
        self.variant, self.prompt, self.reference_dir = variant, prompt, reference_dir
        self.model = model_name(model)
        self.repo = FilePlayRepository(DATA)
        self.plays: dict = {}
        self.judge_client = anthropic.Anthropic()
        self.lock = threading.Lock()
        self.out = FLOW / variant
        (self.out / "traces").mkdir(parents=True, exist_ok=True)

    def play(self, play_id: str):
        with self.lock:
            if play_id not in self.plays:
                self.plays[play_id] = self.repo.get(play_id)
            return self.plays[play_id]

    def render(self, case: dict) -> dict:
        """Render one case. Returns the rendering with everything needed to record it."""
        play = self.play(case["play_id"])
        scene = next(s for s in play.scenes if s.id == case["scene_id"])
        # One LM object per call, uncached: reps must be fresh samples, and this call's
        # served model and usage can be read without another thread's in between.
        lm = dspy.LM(f"anthropic/{self.model}", max_tokens=16000, temperature=None, cache=False)
        started = time.monotonic()
        blocks, _ = render_passage_detailed(play, scene, case["start"], case["end"], prompt=self.prompt, lm=lm)
        latency = time.monotonic() - started
        call = lm.history[-1]
        served = call.get("response_model") or ""
        if not served.startswith(self.model):
            raise ModelMismatch(f"asked for {self.model}, served by {served!r}")
        usage = call.get("usage") or {}
        details = usage.get("prompt_tokens_details") or {}
        original, speakers = original_text(scene, case["start"], case["end"])
        setting, passage = passage_as_prompt(play, scene, case["start"], case["end"])
        finish = getattr(call["response"], "finish_reason", None)
        return {
            "blocks": blocks,
            "text": as_text(blocks, speakers),
            "original": original,
            "user_prompt": f"{setting}\n\n{passage}",
            "warnings": check(scene, case["start"], case["end"], blocks),
            "model": served,
            "stop_reason": finish,
            "latency_s": round(latency, 2),
            "usage": {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "cache_read_input_tokens": details.get("cached_tokens") or 0,
                "cache_creation_input_tokens": details.get("cache_creation_tokens") or 0,
            },
        }

    def run(self, case: dict, rep: int) -> dict:
        rendered = self.render(case)
        reference = json.loads((self.reference_dir / f"{case['id']}.json").read_text(encoding="utf-8"))["text"]
        words = len(rendered["text"].split())
        row = {
            "prompt_id": case["id"],
            "rep": rep,
            "prompt": rendered["user_prompt"],
            "tags": case["tags"],
            "status": "truncated" if rendered["stop_reason"] == "length" else "ok",
            "stop_reason": rendered["stop_reason"],
            "model": rendered["model"],
            "usage": rendered["usage"],
            "latency_s": rendered["latency_s"],
            "out_words": words,
            "meta": {"scene_id": case["scene_id"], "blocks": [case["start"], case["end"]]},
        }
        trace = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": rendered["user_prompt"]},
            {"role": "assistant", "content": rendered["text"]},
        ]
        valid = 0.0 if rendered["warnings"] else 1.0
        out_of_step = any(w.startswith("blocks out of step") for w in rendered["warnings"])
        if out_of_step or row["status"] == "truncated":
            # A rendering that dropped, added or reordered blocks can't go on stage: it
            # loses outright, and the judge isn't asked to compare a broken text.
            grade = {"win": 0.0, "pref": 0.0, "both_bad": 0.0, "valid": 0.0, **{c: 0.0 for c in judging.CRITERIA}}
            row["explanation"] = {"win": "code checks failed: " + "; ".join(rendered["warnings"])}
        else:
            # Shuffle which side the candidate is on; fixed per (case, rep) so a resumed
            # run judges the same way round.
            candidate_side = random.Random(f"{case['id']}:{rep}").choice(["a", "b"])
            a, b = (rendered["text"], reference) if candidate_side == "a" else (reference, rendered["text"])
            verdict, judge_model, judge_usage = judging.judge(self.judge_client, rendered["original"], a, b)
            if not judge_model.startswith(judging.JUDGE_MODEL):
                raise ModelMismatch(f"judge: asked for {judging.JUDGE_MODEL}, served by {judge_model!r}")
            grade = {**judging.grade(verdict, candidate_side), "valid": valid}
            row["judge_model"], row["judge_usage"] = judge_model, judge_usage
            row["explanation"] = {
                "win": f"[candidate was {candidate_side.upper()}] {verdict.reasoning}",
                "valid": "; ".join(rendered["warnings"]) or "all code checks pass",
            }
            trace += [
                {"role": "tool_call", "name": "judge", "content": f"candidate shown as {candidate_side.upper()}; reference as the other side"},
                {"role": "tool_result", "content": verdict.model_dump_json(indent=2)},
            ]
        row["grade"] = grade
        (self.out / "traces" / f"{case['id']}_rep{rep}.json").write_text(
            json.dumps(trace, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        return row


class ModelMismatch(RuntimeError):
    pass


def classify(error: Exception) -> str:
    if isinstance(error, FutureTimeout):
        return "timeout"
    if isinstance(error, ModelMismatch):
        return "served_model_mismatch"
    return "harness_or_serving_error"


# --- commands ---------------------------------------------------------------------------
def make_reference(prompt_file: Path, model: str | None, concurrency: int, timeout_s: int) -> int:
    """Render every case once with the baseline prompt and freeze it. Never regenerated."""
    reference_dir = FLOW / "baseline" / "ref"
    cases = case_set.load()
    missing = [c for c in cases if not (reference_dir / f"{c['id']}.json").exists()]
    if not missing:
        print("The reference already exists and is frozen.")
        return 0
    reference_dir.mkdir(parents=True, exist_ok=True)
    runner = Runner("baseline", prompt_file.read_text(encoding="utf-8"), reference_dir, model)
    failed = 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(runner.render, c): c for c in missing}
        for future, case in futures.items():
            try:
                rendered = future.result(timeout=timeout_s)
                if any(w.startswith("blocks out of step") for w in rendered["warnings"]):
                    raise RuntimeError("reference rendering out of step with the original")
                (reference_dir / f"{case['id']}.json").write_text(
                    json.dumps({"text": rendered["text"], "model": rendered["model"], "usage": rendered["usage"]}, ensure_ascii=False, indent=1),
                    encoding="utf-8",
                )
            except Exception as error:
                failed += 1
                print(f"  reference failed for {case['id']}: {type(error).__name__}: {error}")
    print(f"Reference: {len(missing) - failed} written, {failed} failed. Re-run to retry failures.")
    return 1 if failed else 0


def run_variant(variant: str, reps: int, model: str | None, concurrency: int, timeout_s: int, limit: int | None) -> int:
    out = FLOW / variant
    prompt_file = out / "prompt.txt"
    if not prompt_file.exists():
        print(f"{prompt_file} is missing: each variant carries the prompt it tests.", file=sys.stderr)
        return 1
    cases = case_set.load()[:limit] if limit else case_set.load()
    results_path, errors_path = out / "results.jsonl", out / "errors.jsonl"
    done = set()
    if results_path.exists():
        for line in results_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            done.add((row["prompt_id"], row["rep"]))
    todo = [(c, r) for c in cases for r in range(reps) if (c["id"], r) not in done]
    runner = Runner(variant, prompt_file.read_text(encoding="utf-8"), FLOW / "baseline" / "ref", model)
    print(
        f"{variant}: {len(cases)} cases x {reps} reps = {len(cases) * reps} runs "
        f"({len(done)} already done, {len(todo)} to run); writer {runner.model}, judge {judging.JUDGE_MODEL}; "
        f"{concurrency} at a time"
    )
    started, finished, errors = time.monotonic(), 0, 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [(pool.submit(runner.run, c, r), c, r) for c, r in todo]
        for future, case, rep in futures:
            try:
                row = future.result(timeout=timeout_s)
                with results_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            except Exception as error:
                errors += 1
                with errors_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps({"prompt_id": case["id"], "rep": rep, "class": classify(error), "error": f"{type(error).__name__}: {error}"[:500], "at": time.time()}) + "\n")
            finished += 1
            if finished % 10 == 0 or finished == len(todo):
                elapsed = time.monotonic() - started
                line = f"{finished}/{len(todo)} done, {errors} errors, {elapsed:.0f}s elapsed"
                (out / "progress.txt").write_text(line + "\n", encoding="utf-8")
                print(line)
    summarise(variant)
    return 0


def summarise(variant: str) -> None:
    rows = [json.loads(line) for line in (FLOW / variant / "results.jsonl").read_text(encoding="utf-8").splitlines()]
    ok = [r for r in rows if r["status"] == "ok"]
    st = state()
    for name, ids in (("train", set(st.get("train_ids", []))), ("test", set(st.get("test_ids", []))), ("all", None)):
        subset = [r for r in ok if ids is None or r["prompt_id"] in ids]
        if not subset:
            continue
        # Mean over cases of each case's mean over reps, with a normal-approximation interval
        # across cases.
        by_case: dict[str, list[float]] = {}
        for r in subset:
            by_case.setdefault(r["prompt_id"], []).append(r["grade"]["win"])
        means = [sum(v) / len(v) for v in by_case.values()]
        mean = sum(means) / len(means)
        sd = (sum((m - mean) ** 2 for m in means) / max(1, len(means) - 1)) ** 0.5
        half = 1.96 * sd / len(means) ** 0.5
        valid = sum(r["grade"]["valid"] for r in subset) / len(subset)
        print(f"  {name:5} win {mean:.3f} ± {half:.3f}  (n={len(means)} cases, {len(subset)} runs)  valid {valid:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="evals.run")
    parser.add_argument("--variant", help="baseline or vN")
    parser.add_argument("--reps", type=int)
    parser.add_argument("--model", help="the writer model (default: the app's)")
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--timeout-s", type=int, default=240, help="hard wall-clock ceiling per case")
    parser.add_argument("--limit", type=int, help="only the first N cases (for a pilot)")
    parser.add_argument("--make-reference", action="store_true", help="freeze the baseline's renderings as the reference")
    parser.add_argument("--approve-harness", action="store_true", help="record the current harness as reviewed (for the owner to run)")
    args = parser.parse_args()
    load_env()
    if args.approve_harness:
        check_harness(approve=True)
        return
    check_harness(approve=False)
    if args.make_reference:
        sys.exit(make_reference(FLOW / "baseline" / "prompt.txt", args.model, args.concurrency, args.timeout_s))
    if not args.variant or not VARIANT_NAME.match(args.variant):
        parser.error("--variant must be 'baseline' or 'vN'")
    sys.exit(run_variant(args.variant, args.reps or state().get("reps", 2), args.model, args.concurrency, args.timeout_s, args.limit))


if __name__ == "__main__":
    main()
