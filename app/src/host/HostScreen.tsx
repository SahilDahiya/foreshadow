import { useCallback, useEffect, useRef, useState } from "react";
import type { Scene } from "../../shared/scene";
import {
  initialShowState,
  step,
  voicedLines,
  type HostPosition,
  type ServerMessage,
  type ShowState,
} from "../../shared/protocol";
import { storage, useShowRoom } from "../room";
import { useSwipe } from "./useSwipe";
import { useWakeLock } from "./useWakeLock";
import "./host.css";

// Local-first: every swipe changes this screen immediately and is saved on the
// device, then sent to the room. The network is never between the host and
// their next line.
export function HostScreen({ showId }: { showId: string }) {
  const stateKey = `foreshadow:host:${showId}:state`;
  const sceneKey = `foreshadow:host:${showId}:scene`;
  const [scene, setScene] = useState<Scene | null>(() => storage.get<Scene>(sceneKey));
  const [state, setState] = useState<ShowState>(() => storage.get<ShowState>(stateKey) ?? initialShowState());
  const stateRef = useRef(state);

  const adopt = useCallback(
    (next: ShowState) => {
      stateRef.current = next;
      setState(next);
      storage.set(stateKey, next);
    },
    [stateKey],
  );

  const sendRef = useRef<(state: ShowState) => void>(() => {});
  const reconcile = (server: ShowState) => {
    const local = stateRef.current;
    if (server.seq > local.seq) adopt(server); // another host device, or a reset
    else if (local.seq > server.seq) sendRef.current(local); // we changed things while offline
  };

  const { connected, send } = useShowRoom(showId, (message: ServerMessage) => {
    if (message.type === "welcome") {
      setScene(message.scene);
      storage.set(sceneKey, message.scene);
    }
    reconcile(message.state);
  });
  sendRef.current = (s) => send({ type: "state", state: s });

  const move = useCallback(
    (position: HostPosition) => {
      const current = stateRef.current;
      if (JSON.stringify(position) === JSON.stringify(current.position)) return;
      const startedAt = current.startedAt ?? (position.stage === "playing" ? Date.now() : null);
      const next = { position, seq: current.seq + 1, startedAt };
      adopt(next);
      sendRef.current(next);
    },
    [adopt],
  );

  const forward = () => scene && state.position.stage === "playing" && move(step(scene, state.position, "forward"));
  const back = () => scene && state.position.stage !== "briefing" && move(step(scene, state.position, "back"));

  const surface = useRef<HTMLDivElement>(null);
  const playing = state.position.stage === "playing";
  const offset = useSwipe(surface, { onUp: forward, onDown: back }, state.position.stage !== "briefing");
  useWakeLock(playing);

  // Arrow keys, for rehearsing on a laptop.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowUp") forward();
      if (e.key === "ArrowDown") back();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (!scene) {
    return <main className="host loading">{connected ? "Loading the scene…" : "Connecting…"}</main>;
  }

  const { position } = state;
  return (
    <div ref={surface} className={`host ${position.stage === "playing" ? position.phase : position.stage}`}>
      <div className="host-inner" style={{ transform: `translateY(${offset}px)` }}>
        {position.stage === "briefing" && (
          <Briefing scene={scene} onStart={() => move(step(scene, position, "forward"))} />
        )}
        {position.stage === "playing" && (
          <Playing scene={scene} position={position} startedAt={state.startedAt} connected={connected} />
        )}
        {position.stage === "ended" && <Ended onReset={() => send({ type: "reset" })} />}
      </div>
    </div>
  );
}

function Briefing({ scene, onStart }: { scene: Scene; onStart: () => void }) {
  return (
    <section className="briefing">
      <p className="label">Your briefing</p>
      <h1>{scene.hostCharacter}</h1>
      <p>{scene.briefing}</p>
      <p className="muted">{scene.about}</p>
      <div className="task-card">
        <p className="label">Show this to the improvisers</p>
        {scene.openingTasks.map((t) => (
          <p key={t.character} className="task">
            {t.task}
          </p>
        ))}
      </div>
      <button className="start" onClick={onStart}>
        Start
      </button>
      <p className="muted small">After Start: swipe up to move on, swipe down to go back.</p>
    </section>
  );
}

function Playing({
  scene,
  position,
  startedAt,
  connected,
}: {
  scene: Scene;
  position: Extract<HostPosition, { stage: "playing" }>;
  startedAt: number | null;
  connected: boolean;
}) {
  const voiced = voicedLines(scene);
  const line = scene.lines[voiced[position.voiced]];
  const nextIdx = voiced[position.voiced + 1];
  const next = nextIdx === undefined ? null : scene.lines[nextIdx];
  const preparing = position.phase === "prepare";

  return (
    <section className="playing">
      <header className="counter">
        <span className={connected ? "dot on" : "dot off"} aria-label={connected ? "online" : "offline"} />
        {position.voiced + 1} / {voiced.length} · <Elapsed since={startedAt} />
      </header>
      <p className="label phase">{preparing ? "Prepare" : "Say it"}</p>
      {preparing ? (
        <>
          {line.cue && <p className="cue large">{line.cue}</p>}
          <p className="dialogue medium">{line.text}</p>
        </>
      ) : (
        <>
          {line.cue && <p className="cue">{line.cue}</p>}
          <p className="dialogue huge">{line.text}</p>
        </>
      )}
      {preparing && next && <p className="peek">Next: {next.text}</p>}
    </section>
  );
}

function Ended({ onReset }: { onReset: () => void }) {
  return (
    <section className="ended">
      <h1>Scene complete</h1>
      <p className="muted">Swipe down to go back to the last line.</p>
      <button className="pill secondary" onClick={onReset}>
        Reset the demo
      </button>
    </section>
  );
}

function Elapsed({ since }: { since: number | null }) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);
  const seconds = since ? Math.max(0, Math.floor((now - since) / 1000)) : 0;
  return (
    <>
      {Math.floor(seconds / 60)}:{String(seconds % 60).padStart(2, "0")}
    </>
  );
}
