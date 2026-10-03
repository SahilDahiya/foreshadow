"""The voting page: a small local web server. `library lab` starts it."""

from __future__ import annotations

import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ..repository import PlayRepository
from . import rounds, store

PAGE = Path(__file__).with_name("page.html")


class Lab:
    """Server state: the play repository, and whatever long job is running."""

    def __init__(self, repo: PlayRepository):
        self.repo = repo
        self.working = False
        self.message = ""
        self.error = ""
        self.lock = threading.Lock()

    def start_round(self, guidance: str = "") -> None:
        with self.lock:
            if self.working:
                return
            self.working, self.error = True, ""

        def run() -> None:
            try:
                rounds.prepare(self.repo, progress=self._progress, guidance=guidance)
            except Exception as error:
                self.error = f"{type(error).__name__}: {error}"
            finally:
                self.working = False

        threading.Thread(target=run, daemon=True).start()

    def _progress(self, message: str) -> None:
        self.message = message
        print(message)

    def view(self) -> dict:
        rnd = rounds.current_round()
        payload: dict = {"working": self.working, "message": self.message, "error": self.error, "round": None}
        payload["champion"] = rounds.champion().id
        if rnd is None:
            return payload
        votes = store.votes(rnd.number)
        decided = rnd.outcome is not None
        payload["round"] = {
            "number": rnd.number,
            "items": [
                {
                    "id": item.id,
                    "where": item.where,
                    "original": [o.model_dump() for o in item.original],
                    "a": _blocks(item, item.a),
                    "b": _blocks(item, item.b),
                    "vote": (v.model_dump() if (v := votes.get((rnd.number, item.id))) else None),
                    # Which prompt made which side stays hidden until the round is decided.
                    "reveal": {"a": item.a.prompt_id, "b": item.b.prompt_id} if decided else None,
                }
                for item in rnd.items
            ],
            "outcome": rnd.outcome.model_dump() if rnd.outcome else None,
            "champion": rnd.champion if decided else None,
            "challenger": rnd.challenger if decided else None,
            "rationale": store.prompt(rnd.challenger).rationale if decided else None,
        }
        return payload


def _blocks(item: store.Item, version: store.Version) -> list[dict]:
    speakers = {item.start + i: o.speaker for i, o in enumerate(item.original)}
    return [
        {"speaker": speakers.get(b.source_block), "parts": [p.model_dump() for p in b.parts]} for b in version.blocks
    ]


def serve(repo: PlayRepository, port: int = 8765, open_browser: bool = True) -> None:
    lab = Lab(repo)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args) -> None:  # keep the terminal for progress messages
            pass

        def _json(self, data: object, status: int = 200) -> None:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _body(self) -> dict:
            length = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(length) or b"{}")

        def do_GET(self) -> None:
            if self.path == "/api/state":
                return self._json(lab.view())
            body = PAGE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            data = self._body()
            rnd = rounds.current_round()
            if self.path == "/api/vote" and rnd and rnd.outcome is None:
                reject = bool(data.get("reject_both"))
                score = None if reject else data.get("score")
                note = str(data.get("note", "")).strip()
                if data.get("item") not in {i.id for i in rnd.items}:
                    return self._json({"error": "no such passage"}, 400)
                if not reject and (not isinstance(score, int) or not 0 <= score <= 7):
                    return self._json({"error": "a vote is 0 to 7, or reject both"}, 400)
                if not note:
                    return self._json({"error": "every vote needs a reason"}, 400)
                store.add_vote(
                    store.Vote(round=rnd.number, item=data["item"], score=score, reject_both=reject, note=note, at=store.now())
                )
            elif self.path == "/api/decide" and rnd and rnd.outcome is None:
                try:
                    rounds.decide(rnd)
                except ValueError as error:
                    return self._json({"error": str(error)}, 400)
            elif self.path == "/api/next" and (rnd is None or rnd.outcome is not None):
                lab.start_round(guidance=str(data.get("guidance", "")).strip())
            else:
                return self._json({"error": "not possible right now"}, 400)
            self._json(lab.view())

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}"
    print(f"The preference lab is at {url}  (Ctrl+C to stop)")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
