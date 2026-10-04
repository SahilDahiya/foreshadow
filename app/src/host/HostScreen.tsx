import { useCallback, useEffect, useRef, useState } from "react";
import { DEMO_SCENE } from "../../shared/demo-scene";
import type { Scene, SceneSummary } from "../../shared/scene";
import { loadScene, sceneCatalogue } from "../catalogue";
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
  const [welcomed, setWelcomed] = useState(false);
  const [picking, setPicking] = useState(false);

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
      setWelcomed(true);
      setPicking(false);
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
  const offset = useSwipe(surface, { onForward: forward, onBack: back }, state.position.stage !== "briefing");
  useWakeLock(playing);

  // Arrow keys, for rehearsing on a laptop.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === "ArrowUp") forward();
      if (e.key === "ArrowLeft" || e.key === "ArrowDown") back();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (!scene && !welcomed) {
    return <main className="host loading">{connected ? "Loading…" : "Connecting…"}</main>;
  }
  if (!scene || picking) {
    return (
      <ScenePicker
        onPick={(picked) => send({ type: "load", scene: picked })}
        onCancel={scene ? () => setPicking(false) : undefined}
      />
    );
  }

  const { position } = state;
  return (
    <div ref={surface} className={`host ${position.stage}`}>
      <div className="host-inner" style={{ transform: `translateX(${offset}px)` }}>
        {position.stage === "briefing" && (
          <Briefing
            scene={scene}
            showId={showId}
            onStart={() => move(step(scene, position, "forward"))}
            onChoose={() => setPicking(true)}
          />
        )}
        {position.stage === "playing" && (
          <Playing scene={scene} position={position} startedAt={state.startedAt} connected={connected} />
        )}
        {position.stage === "ended" && (
          <Ended onReset={() => send({ type: "reset" })} onChoose={() => setPicking(true)} />
        )}
      </div>
    </div>
  );
}

const SIZE_LABEL = { small: "small · about 5 min", medium: "medium · about 10 min", big: "big · about 20 min" };

// Choose what to perform: the catalogue of scenes from the play library.
function ScenePicker({ onPick, onCancel }: { onPick: (scene: Scene) => void; onCancel?: () => void }) {
  const [catalogue, setCatalogue] = useState<SceneSummary[] | null>(null);
  const [size, setSize] = useState<"small" | "medium" | "big">("small");
  const [loading, setLoading] = useState<string | null>(null);
  useEffect(() => {
    sceneCatalogue().then(setCatalogue, () => setCatalogue([]));
  }, []);
  const pick = async (id: string) => {
    setLoading(id);
    try {
      onPick(await loadScene(id));
    } finally {
      setLoading(null);
    }
  };
  const list = (catalogue ?? []).filter((s) => s.size === size);
  return (
    <main className="picker">
      <header>
        <p className="label">Choose a scene</p>
        <div className="sizes">
          {(["small", "medium", "big"] as const).map((s) => (
            <button key={s} className={s === size ? "chip on" : "chip"} onClick={() => setSize(s)}>
              {SIZE_LABEL[s]}
            </button>
          ))}
        </div>
        {onCancel && <button className="link" onClick={onCancel}>← Back</button>}
      </header>
      {catalogue === null && <p className="muted">Loading the catalogue…</p>}
      <ul>
        {list.map((s) => (
          <li key={s.id}>
            <button className="scene-card" disabled={loading !== null} onClick={() => pick(s.id)}>
              <span className="title">{s.title}</span>
              <span className="muted small">{s.about}</span>
              <span>
                You read <strong>{s.host}</strong>, with {s.partner} · about {Math.round(s.minutes)} min · {s.hostLines} lines
              </span>
              <span className="muted small">“{s.opens}”</span>
              {loading === s.id && <span className="muted small">Loading…</span>}
            </button>
          </li>
        ))}
        <li>
          <button className="scene-card" disabled={loading !== null} onClick={() => onPick(DEMO_SCENE)}>
            <span className="title">{DEMO_SCENE.title} (demo)</span>
            <span className="muted small">The original test scene: an invented soap opera, not from the library.</span>
          </button>
        </li>
      </ul>
    </main>
  );
}

function Briefing({ scene, showId, onStart, onChoose }: { scene: Scene; showId: string; onStart: () => void; onChoose: () => void }) {
  return (
    <section className="briefing">
      <p className="label">Your briefing</p>
      <h1>{scene.hostCharacter}</h1>
      <p>{scene.briefing}</p>
      <p className="muted">
        {scene.title}. {scene.about}
        {scene.minutes ? ` About ${Math.round(scene.minutes)} minutes.` : ""}
      </p>
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
      <p className="muted small">After Start: swipe left (or double tap) for your next turn, swipe right to go back.</p>
      <p className="muted small">
        Others follow along at {window.location.host}/watch/{showId} ·{" "}
        <button className="link" onClick={onChoose}>choose another scene</button>
      </p>
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

  // One screen per line: the line, with its direction (if any) in a slot of its own above it.
  return (
    <section className={`playing ${turnSize(line.text)}`}>
      <header className="counter">
        <span className={connected ? "dot on" : "dot off"} aria-label={connected ? "online" : "offline"} />
        {position.voiced + 1} / {voiced.length} · <Elapsed since={startedAt} />
      </header>
      {/* The direction has its own slot above the line. The slot is empty for most lines,
          so the line always starts at the same height, and anything appearing in the slot
          reads at once as "how", not "what". */}
      <div className="direction-slot">
        {line.cue && (
          <div className="direction-note">
            <p className="direction-label">How to say it</p>
            <p className="direction-text">{line.cue}</p>
          </div>
        )}
      </div>
      {/* The whole turn on one screen. Longer turns use smaller type, and scroll if they must. */}
      <div className="dialogue" key={position.voiced}>
        {line.text.split("\n").map((row, i) =>
          /^\[.*\]$/.test(row) ? (
            <p key={i} className="inline-direction">{row.slice(1, -1)}</p>
          ) : (
            <p key={i}>{row}</p>
          ),
        )}
      </div>
    </section>
  );
}

// How much there is to say decides how large it can be set.
function turnSize(text: string): "turn-short" | "turn-medium" | "turn-long" | "turn-speech" {
  const length = text.length;
  if (length <= 110) return "turn-short";
  if (length <= 260) return "turn-medium";
  if (length <= 600) return "turn-long";
  return "turn-speech";
}

function Ended({ onReset, onChoose }: { onReset: () => void; onChoose: () => void }) {
  return (
    <section className="ended">
      <h1>Scene complete</h1>
      <p className="muted">Swipe right to go back to the last line.</p>
      <button className="pill" onClick={onChoose}>
        Choose another scene
      </button>
      <button className="pill secondary" onClick={onReset}>
        Play this one again
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
