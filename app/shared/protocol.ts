import type { Scene } from "./scene";

// Where the host is. The host device is the only writer of this state.
export type HostPosition =
  | { stage: "briefing" }
  /** The host is on this line: it is on their screen (with its direction, if any) and being said. */
  | { stage: "playing"; voiced: number }
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
  /** Put a scene in the room. Everyone gets it, and the show goes back to the briefing. */
  | { type: "load"; scene: Scene }
  | { type: "reset" };

export type ServerMessage =
  /** scene is null until the host has chosen one. */
  | { type: "welcome"; scene: Scene | null; state: ShowState }
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
 * The shared cursor: the index of the line the host is on, or null before the scene
 * starts. One screen per line: the swipe that shows a line to the host is the moment it
 * is said, and the audience's screens move with it.
 */
export function deliveredLine(scene: Scene, position: HostPosition): number | null {
  const voiced = voicedLines(scene);
  switch (position.stage) {
    case "briefing":
      return null;
    case "ended":
      return voiced.at(-1) ?? null;
    case "playing":
      return voiced[position.voiced] ?? null;
  }
}

/**
 * One swipe, one line, and every line is reached in order: nothing can be skipped.
 * Forward from the briefing is not a swipe: the host presses Start.
 */
export function step(scene: Scene, position: HostPosition, direction: "forward" | "back"): HostPosition {
  const last = voicedLines(scene).length - 1;
  if (direction === "forward") {
    switch (position.stage) {
      case "briefing":
        return { stage: "playing", voiced: 0 };
      case "ended":
        return position;
      case "playing":
        return position.voiced >= last ? { stage: "ended" } : { stage: "playing", voiced: position.voiced + 1 };
    }
  }
  switch (position.stage) {
    case "briefing":
      return position;
    case "ended":
      return { stage: "playing", voiced: last };
    case "playing":
      return position.voiced === 0 ? position : { stage: "playing", voiced: position.voiced - 1 };
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
      (p.stage === "playing" && typeof p.voiced === "number"))
  );
}
