import { useEffect, useRef, useState } from "react";
import type { Scene } from "../../shared/scene";
import { deliveredLine, initialShowState, type ShowState } from "../../shared/protocol";
import { useShowRoom } from "../room";
import "./watch.css";

// The audience's script. It scrolls itself to keep the line being said at a
// fixed height, so a glance down finds it and eyes go back to the stage.
export function WatchScreen({ showId }: { showId: string }) {
  const [scene, setScene] = useState<Scene | null>(null);
  const [state, setState] = useState<ShowState>(initialShowState);

  const [welcomed, setWelcomed] = useState(false);
  const { connected } = useShowRoom(showId, (message) => {
    if (message.type === "welcome") {
      setScene(message.scene);
      setWelcomed(true);
    }
    setState((current) => (message.state.seq >= current.seq ? message.state : current));
  });

  const delivered = scene ? deliveredLine(scene, state.position) : null;
  const lineRefs = useRef<(HTMLElement | null)[]>([]);
  const scroller = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const box = scroller.current;
    const el = delivered === null ? null : lineRefs.current[delivered];
    if (!box) return;
    const top = el ? el.offsetTop - box.clientHeight * 0.35 : 0;
    box.scrollTo({ top, behavior: "smooth" });
  }, [delivered]);

  if (!scene) {
    return (
      <main className="watch loading">
        {!connected ? "Connecting…" : welcomed ? "Waiting for the host to choose a scene." : "Loading…"}
      </main>
    );
  }

  const { stage } = state.position;
  // A ghost line appears once the gap it fills has opened: when the host has
  // delivered the line before it.
  const gapEnd = nextVoicedAfter(scene, delivered);

  return (
    <div ref={scroller} className="watch">
      <header className="watch-header">
        <p className="label">{scene.genre}</p>
        <h1>{scene.title}</h1>
        <p className="muted">{scene.about}</p>
        {stage === "briefing" && (
          <div className="opening">
            <p className="label">About to begin. Watch:</p>
            {scene.openingTasks.map((t) => (
              <p key={t.character}>
                <strong>{t.character}</strong> is {t.task.toLowerCase()}
              </p>
            ))}
          </div>
        )}
      </header>

      <ol className="script">
        {scene.lines.map((line, i) => {
          const visible = line.voiced || (stage !== "briefing" && i < gapEnd);
          const status =
            delivered === null || i > delivered ? "upcoming" : i === delivered ? "current" : "past";
          const ghostOpen = !line.voiced && visible && status === "upcoming";
          return (
            <li
              key={i}
              ref={(el) => {
                lineRefs.current[i] = el;
              }}
              className={[
                "line",
                line.voiced ? "voiced" : "ghost",
                status,
                ghostOpen ? "open" : "",
              ].join(" ")}
            >
              <span className="who">{line.character}</span>
              {visible ? (
                <>
                  {line.cue && <span className="cue">{line.cue}</span>}
                  <span className="text">{line.text}</span>
                </>
              ) : (
                <span className="text hidden">· · ·</span>
              )}
            </li>
          );
        })}
      </ol>
      {stage === "ended" && <p className="the-end">The end</p>}
      <div className="spacer" />
    </div>
  );
}

function nextVoicedAfter(scene: Scene, delivered: number | null): number {
  const from = delivered === null ? 0 : delivered + 1;
  const next = scene.lines.findIndex((line, i) => i >= from && line.voiced);
  return next === -1 ? scene.lines.length : next;
}
