import { describe, expect, it } from "vitest";
import { DEMO_SCENE } from "./demo-scene";
import { deliveredLine, isShowState, step, voicedLines, type HostPosition } from "./protocol";

const scene = DEMO_SCENE;
const voiced = voicedLines(scene);

function walkForward(): HostPosition[] {
  const positions: HostPosition[] = [{ stage: "briefing" }];
  let p = step(scene, positions[0], "forward");
  while (p.stage !== "ended") {
    positions.push(p);
    p = step(scene, p, "forward");
  }
  positions.push(p);
  return positions;
}

describe("step", () => {
  it("passes every voiced line through prepare then deliver, in order", () => {
    const playing = walkForward().filter((p) => p.stage === "playing");
    expect(playing).toHaveLength(voiced.length * 2);
    playing.forEach((p, i) => {
      expect(p).toEqual({ stage: "playing", voiced: Math.floor(i / 2), phase: i % 2 ? "deliver" : "prepare" });
    });
  });

  it("going back retraces forward exactly", () => {
    const forward = walkForward();
    for (let i = forward.length - 1; i > 1; i--) {
      expect(step(scene, forward[i], "back")).toEqual(forward[i - 1]);
    }
  });

  it("stops at the first prepare and at the end", () => {
    const first: HostPosition = { stage: "playing", voiced: 0, phase: "prepare" };
    expect(step(scene, first, "back")).toEqual(first);
    expect(step(scene, { stage: "ended" }, "forward")).toEqual({ stage: "ended" });
  });
});

describe("deliveredLine", () => {
  it("moves only when a line is delivered", () => {
    expect(deliveredLine(scene, { stage: "briefing" })).toBeNull();
    expect(deliveredLine(scene, { stage: "playing", voiced: 0, phase: "prepare" })).toBeNull();
    expect(deliveredLine(scene, { stage: "playing", voiced: 0, phase: "deliver" })).toBe(voiced[0]);
    expect(deliveredLine(scene, { stage: "playing", voiced: 1, phase: "prepare" })).toBe(voiced[0]);
    expect(deliveredLine(scene, { stage: "ended" })).toBe(voiced.at(-1));
  });
});

describe("isShowState", () => {
  it("accepts valid states and rejects junk", () => {
    expect(isShowState({ position: { stage: "briefing" }, seq: 1, startedAt: null })).toBe(true);
    expect(isShowState({ position: { stage: "playing", voiced: 2, phase: "deliver" }, seq: 3, startedAt: 5 })).toBe(true);
    expect(isShowState({ position: { stage: "playing", voiced: "2", phase: "deliver" }, seq: 3, startedAt: 5 })).toBe(false);
    expect(isShowState({ position: { stage: "dancing" }, seq: 1, startedAt: null })).toBe(false);
    expect(isShowState(null)).toBe(false);
  });
});
