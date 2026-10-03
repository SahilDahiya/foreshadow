import { useCallback, useRef, useState } from "react";
import usePartySocket from "partysocket/react";
import type { ClientMessage, ServerMessage } from "../shared/protocol";

// The connection to a show's room. partysocket reconnects with backoff and
// queues messages sent while offline.
export function useShowRoom(showId: string, onMessage: (message: ServerMessage) => void) {
  const [connected, setConnected] = useState(false);
  const handler = useRef(onMessage);
  handler.current = onMessage;

  const socket = usePartySocket({
    party: "show-room",
    room: showId,
    onOpen: () => setConnected(true),
    onClose: () => setConnected(false),
    onMessage: (event) => handler.current(JSON.parse(event.data as string) as ServerMessage),
  });

  const send = useCallback((message: ClientMessage) => socket.send(JSON.stringify(message)), [socket]);
  return { connected, send };
}

/** localStorage that never throws: private windows and blocked storage just skip it. */
export const storage = {
  get<T>(key: string): T | null {
    try {
      const raw = localStorage.getItem(key);
      return raw ? (JSON.parse(raw) as T) : null;
    } catch {
      return null;
    }
  },
  set(key: string, value: unknown) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Ignore: the room still has the state.
    }
  },
};
