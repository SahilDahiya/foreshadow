import { useEffect, useRef, useState, type RefObject } from "react";

const THRESHOLD = 60; // px of travel before a swipe counts
const EDGE = 32; // px near the top and bottom where the phone's own gestures live
const COOLDOWN = 250; // ms after a swipe during which another one is ignored

// Vertical swipes only. A swipe counts on release, once it has travelled far
// enough; a shorter drag springs back. Taps do nothing.
export function useSwipe(
  ref: RefObject<HTMLElement | null>,
  handlers: { onUp: () => void; onDown: () => void },
  enabled: boolean,
) {
  const [offset, setOffset] = useState(0);
  const latest = useRef(handlers);
  latest.current = handlers;

  useEffect(() => {
    const el = ref.current;
    if (!el || !enabled) return;
    let startY: number | null = null;
    let lastSwipe = 0;

    const down = (e: PointerEvent) => {
      if (e.clientY < EDGE || e.clientY > window.innerHeight - EDGE) return;
      startY = e.clientY;
      el.setPointerCapture(e.pointerId);
    };
    const move = (e: PointerEvent) => {
      if (startY === null) return;
      // Follow the finger, damped, so the screen feels attached to it.
      setOffset((e.clientY - startY) * 0.35);
    };
    const up = (e: PointerEvent) => {
      if (startY === null) return;
      const dy = e.clientY - startY;
      startY = null;
      setOffset(0);
      const now = Date.now();
      if (Math.abs(dy) < THRESHOLD || now - lastSwipe < COOLDOWN) return;
      lastSwipe = now;
      if (dy < 0) latest.current.onUp();
      else latest.current.onDown();
    };
    const cancel = () => {
      startY = null;
      setOffset(0);
    };

    el.addEventListener("pointerdown", down);
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerup", up);
    el.addEventListener("pointercancel", cancel);
    return () => {
      el.removeEventListener("pointerdown", down);
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerup", up);
      el.removeEventListener("pointercancel", cancel);
    };
  }, [ref, enabled]);

  return offset;
}
