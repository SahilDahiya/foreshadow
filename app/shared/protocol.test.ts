import { describe, expect, it } from "vitest";
import { DEMO_SCENE } from "./demo-scene";
import { deliveredLine, isShowState, step, voicedLines, type HostPosition } from "./protocol";

const scene = DEMO_SCENE;
const voiced = voicedLines(scene);

function walk(): HostPosition[] {
  const path: HostPosition[] = [{ stage: "briefing" }];
  while (path.at(-1)!.stage !== "ended") path.push(step(scene, path.at(-1)!, "forward"));
  return path;
}

describe("step", () => {
  it("is one swipe per line, every line in order", () => {
    expect(walk().slice(1, -1)).toEqual(voiced.map((_, i) => ({ stage: "playing", voiced: i })));
  });

  it("going back retraces forward exactly", () => {
    const forward = walk();
    for (let i = forward.length - 1; i > 1; i--) {
      expect(step(scene, forward[i], "back")).toEqual(forward[i - 1]);
    }
  });

  it("stops at the first line and at the end", () => {
    const first: HostPosition = { stage: "playing", voiced: 0 };
    expect(step(scene, first, "back")).toEqual(first);
    expect(step(scene, { stage: "ended" }, "forward")).toEqual({ stage: "ended" });
  });
});

describe("deliveredLine", () => {
  it("is the line the host is on", () => {
    expect(deliveredLine(scene, { stage: "briefing" })).toBeNull();
    expect(deliveredLine(scene, { stage: "playing", voiced: 0 })).toBe(voiced[0]);
    expect(deliveredLine(scene, { stage: "playing", voiced: 3 })).toBe(voiced[3]);
    expect(deliveredLine(scene, { stage: "ended" })).toBe(voiced.at(-1));
  });
});

describe("isShowState", () => {
  it("accepts valid states and rejects junk", () => {
    expect(isShowState({ position: { stage: "briefing" }, seq: 1, startedAt: null })).toBe(true);
    expect(isShowState({ position: { stage: "playing", voiced: 2 }, seq: 3, startedAt: 5 })).toBe(true);
    expect(isShowState({ position: { stage: "playing", voiced: "2" }, seq: 3, startedAt: 5 })).toBe(false);
    expect(isShowState({ position: { stage: "dancing" }, seq: 1, startedAt: null })).toBe(false);
    expect(isShowState(null)).toBe(false);
  });
});
