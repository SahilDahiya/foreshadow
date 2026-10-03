import type { Scene } from "./scene";

// Where the host is. The host device is the only writer of this state.
export type HostPosition =
  | { stage: "briefing" }
  | { stage: "playing"; voiced: number; phase: "prepare" | "deliver" }
  | { stage: "ended" };

export interface ShowState {
  position: HostPosition;
  /** Increases with every change. The higher sequence number always wins. */
  seq: number;
  /** Host clock, when Start was pressed. Only the host displays it. */
  startedAt: number | null;
}

export type ClientMessage =
  | { type: "state"; state: ShowState }
  | { type: "reset" };

export type ServerMessage =
  | { type: "welcome"; scene: Scene; state: ShowState }
  | { type: "state"; state: ShowState };

export const initialShowState = (): ShowState => ({
  position: { stage: "briefing" },
  seq: 0,
  startedAt: null,
});

/** Indexes into scene.lines of the lines the host reads. */
export function voicedLines(scene: Scene): number[] {
  return scene.lines.flatMap((line, i) => (line.voiced ? [i] : []));
}

/**
 * The shared cursor: the index of the last delivered line, or null before the
 * first one. The prepare phase is private to the host, so it doesn't move this.
 */
export function deliveredLine(scene: Scene, position: HostPosition): number | null {
  const voiced = voicedLines(scene);
  switch (position.stage) {
    case "briefing":
      return null;
    case "ended":
      return voiced.at(-1) ?? null;
    case "playing": {
      const v = position.phase === "deliver" ? position.voiced : position.voiced - 1;
      return v >= 0 ? voiced[v] : null;
    }
  }
}

/**
 * One swipe moves exactly one phase. Forward from briefing is not a swipe
 * (the host presses Start), and every line passes through deliver.
 */
export function step(scene: Scene, position: HostPosition, direction: "forward" | "back"): HostPosition {
  const last = voicedLines(scene).length - 1;
  if (direction === "forward") {
    switch (position.stage) {
      case "briefing":
        return { stage: "playing", voiced: 0, phase: "prepare" };
      case "ended":
        return position;
      case "playing":
        if (position.phase === "prepare") return { ...position, phase: "deliver" };
        if (position.voiced === last) return { stage: "ended" };
        return { stage: "playing", voiced: position.voiced + 1, phase: "prepare" };
    }
  }
  switch (position.stage) {
    case "briefing":
      return position;
    case "ended":
      return { stage: "playing", voiced: last, phase: "deliver" };
    case "playing":
      if (position.phase === "deliver") return { ...position, phase: "prepare" };
      if (position.voiced === 0) return position;
      return { stage: "playing", voiced: position.voiced - 1, phase: "deliver" };
  }
}

export function isShowState(value: unknown): value is ShowState {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  const p = v.position as Record<string, unknown> | undefined;
  return (
    typeof v.seq === "number" &&
    (v.startedAt === null || typeof v.startedAt === "number") &&
    typeof p === "object" &&
    p !== null &&
    (p.stage === "briefing" ||
      p.stage === "ended" ||
      (p.stage === "playing" &&
        typeof p.voiced === "number" &&
        (p.phase === "prepare" || p.phase === "deliver")))
  );
}
