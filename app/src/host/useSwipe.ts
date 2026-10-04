import { useEffect, useRef, useState, type RefObject } from "react";

const SWIPE_DISTANCE = 45; // px sideways before a swipe counts
const SIDEWAYS_RATIO = 1.2; // sideways travel must beat vertical travel by this much
const EDGE = 24; // px at the left and right edges, where the phone's own back gesture lives
const COOLDOWN = 250; // ms after an action during which another is ignored
const TAP_MOVE = 12; // px: more than this and it wasn't a tap
const TAP_TIME = 300; // ms: a tap is shorter than this
const DOUBLE_TAP_GAP = 350; // ms between the two taps
const DOUBLE_TAP_DISTANCE = 40; // px between the two taps

interface Handlers {
  /** Swipe left, or double tap: the next screen. */
  onForward: () => void;
  /** Swipe right: the previous screen. */
  onBack: () => void;
}

// Sideways swipes, like turning a page, and a double tap for "next". A single tap does
// nothing, and a drag that is short or mostly vertical does nothing.
//
// Touch is read from touch events, not pointer events: the screen can scroll up and down
// (touch-action: pan-y), and once the browser starts a scroll it cancels the pointer but
// keeps sending touch events, so a slightly diagonal swipe is still seen to its end.
export function useSwipe(ref: RefObject<HTMLElement | null>, handlers: Handlers, enabled: boolean) {
  const [offset, setOffset] = useState(0);
  const latest = useRef(handlers);
  latest.current = handlers;

  useEffect(() => {
    const el = ref.current;
    if (!el || !enabled) return;
    let start: { x: number; y: number; t: number } | null = null;
    let lastAction = 0;
    let lastTap: { x: number; y: number; t: number } | null = null;

    const act = (which: "forward" | "back") => {
      const now = Date.now();
      if (now - lastAction < COOLDOWN) return;
      lastAction = now;
      if (which === "forward") latest.current.onForward();
      else latest.current.onBack();
    };

    const begin = (x: number, y: number) => {
      start = x < EDGE || x > window.innerWidth - EDGE ? null : { x, y, t: Date.now() };
    };
    const drag = (x: number, y: number) => {
      if (!start) return;
      const dx = x - start.x;
      // Follow the finger, damped, once the movement is clearly sideways.
      setOffset(Math.abs(dx) > Math.abs(y - start.y) ? dx * 0.35 : 0);
    };
    const finish = (x: number, y: number) => {
      setOffset(0);
      if (!start) return;
      const dx = x - start.x;
      const dy = y - start.y;
      const now = Date.now();
      const held = now - start.t;
      start = null;
      if (Math.abs(dx) >= SWIPE_DISTANCE && Math.abs(dx) > Math.abs(dy) * SIDEWAYS_RATIO) {
        lastTap = null;
        act(dx < 0 ? "forward" : "back");
        return;
      }
      if (Math.abs(dx) <= TAP_MOVE && Math.abs(dy) <= TAP_MOVE && held <= TAP_TIME) {
        if (lastTap && now - lastTap.t <= DOUBLE_TAP_GAP && Math.hypot(x - lastTap.x, y - lastTap.y) <= DOUBLE_TAP_DISTANCE) {
          lastTap = null;
          act("forward");
        } else {
          lastTap = { x, y, t: now };
        }
      }
    };
    const cancel = () => {
      start = null;
      setOffset(0);
    };

    const touchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) begin(e.touches[0].clientX, e.touches[0].clientY);
      else cancel(); // two fingers is not a swipe
    };
    const touchMove = (e: TouchEvent) => drag(e.touches[0].clientX, e.touches[0].clientY);
    const touchEnd = (e: TouchEvent) => finish(e.changedTouches[0].clientX, e.changedTouches[0].clientY);

    // A mouse, for rehearsing on a laptop. Touch input is handled above.
    const mouseDown = (e: PointerEvent) => e.pointerType === "mouse" && begin(e.clientX, e.clientY);
    const mouseMove = (e: PointerEvent) => e.pointerType === "mouse" && drag(e.clientX, e.clientY);
    const mouseUp = (e: PointerEvent) => e.pointerType === "mouse" && finish(e.clientX, e.clientY);

    const passive = { passive: true } as const;
    el.addEventListener("touchstart", touchStart, passive);
    el.addEventListener("touchmove", touchMove, passive);
    el.addEventListener("touchend", touchEnd, passive);
    el.addEventListener("touchcancel", cancel, passive);
    el.addEventListener("pointerdown", mouseDown);
    el.addEventListener("pointermove", mouseMove);
    el.addEventListener("pointerup", mouseUp);
    return () => {
      el.removeEventListener("touchstart", touchStart);
      el.removeEventListener("touchmove", touchMove);
      el.removeEventListener("touchend", touchEnd);
      el.removeEventListener("touchcancel", cancel);
      el.removeEventListener("pointerdown", mouseDown);
      el.removeEventListener("pointermove", mouseMove);
      el.removeEventListener("pointerup", mouseUp);
    };
  }, [ref, enabled]);

  return offset;
}
