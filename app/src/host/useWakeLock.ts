import { useEffect } from "react";

// Keeps the screen on while the scene runs. The lock is released whenever the
// page is hidden, so it is requested again when the page comes back.
export function useWakeLock(active: boolean) {
  useEffect(() => {
    if (!active || !("wakeLock" in navigator)) return;
    let lock: WakeLockSentinel | null = null;
    const request = () => {
      if (document.visibilityState !== "visible") return;
      navigator.wakeLock.request("screen").then(
        (l) => (lock = l),
        () => {},
      );
    };
    request();
    document.addEventListener("visibilitychange", request);
    return () => {
      document.removeEventListener("visibilitychange", request);
      lock?.release();
    };
  }, [active]);
}
