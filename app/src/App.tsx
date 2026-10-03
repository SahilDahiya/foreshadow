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

function Home() {
  return (
    <main className="home">
      <h1>Foreshadow</h1>
      <p className="muted">Prototype: a hard-coded scene, kept in sync.</p>
      <a className="pill" href="/host/demo">Host the demo scene</a>
      <a className="pill secondary" href="/watch/demo">Follow along</a>
      <a className="pill secondary" href="/library">Play library</a>
    </main>
  );
}
