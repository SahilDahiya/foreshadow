import { useState } from "react";
import usePartySocket from "partysocket/react";

type RoomMessage =
  | { type: "presence"; count: number }
  | { type: "ping"; from: string };

// Skeleton: proves the path phone → Worker → Durable Object → every phone.
export function App() {
  const [connected, setConnected] = useState(false);
  const [phones, setPhones] = useState(0);
  const [pings, setPings] = useState(0);

  const socket = usePartySocket({
    party: "show-room",
    room: "demo",
    onOpen: () => setConnected(true),
    onClose: () => setConnected(false),
    onMessage: (event) => {
      const message = JSON.parse(event.data as string) as RoomMessage;
      if (message.type === "presence") setPhones(message.count);
      if (message.type === "ping") setPings((n) => n + 1);
    },
  });

  return (
    <main>
      <h1>Foreshadow</h1>
      <p className={connected ? "status on" : "status off"}>
        {connected ? "Connected to the room" : "Connecting…"}
      </p>
      <p className="big">{phones}</p>
      <p>{phones === 1 ? "phone in the room" : "phones in the room"}</p>
      <button onClick={() => socket.send("ping")} disabled={!connected}>
        Ping every phone
      </button>
      <p className="muted">Pings received: {pings}</p>
    </main>
  );
}
