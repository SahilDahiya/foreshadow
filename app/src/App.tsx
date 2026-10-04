import { useState } from "react";
import { HostScreen } from "./host/HostScreen";
import { LibraryScreen } from "./library/LibraryScreen";
import { WatchScreen } from "./watch/WatchScreen";

// A router is overkill for three routes.
export function App() {
  const [, route, showId, ...rest] = window.location.pathname.split("/").map(decodeURIComponent);
  if (route === "library") return <LibraryScreen path={[showId, ...rest].filter(Boolean)} />;
  if (route === "host" && showId) return <HostScreen showId={showId} />;
  if (route === "watch" && showId) return <WatchScreen showId={showId} />;
  return <Home />;
}

// A short code people can read out and type: no vowels, so no accidental words.
function newRoomCode() {
  const letters = "BCDFGHJKLMNPQRSTVWXZ";
  return Array.from(crypto.getRandomValues(new Uint8Array(4)), (n) => letters[n % letters.length]).join("");
}

function Home() {
  const [code, setCode] = useState("");
  const follow = code.trim().toUpperCase();
  return (
    <main className="home">
      <h1>Foreshadow</h1>
      <p className="muted">Rehearsal prototype: pick a scene, read it, others follow along.</p>
      <a className="pill" href={`/host/${newRoomCode()}`}>Host a scene</a>
      <form
        className="follow"
        onSubmit={(e) => {
          e.preventDefault();
          if (follow) window.location.href = `/watch/${follow}`;
        }}
      >
        <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="Room code" aria-label="Room code" maxLength={8} />
        <button className="pill secondary" disabled={!follow}>Follow along</button>
      </form>
      <a className="pill secondary" href="/library">Play library</a>
    </main>
  );
}
