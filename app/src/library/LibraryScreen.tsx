import { useEffect, useState } from "react";
import type { LibraryScene, PlaySummary, SceneSummary } from "../../shared/library";
import { staticLibrary } from "./repository";
import "./library.css";

// Internal browser for the play library: every play, every scene, and the text as parsed.
// Routes: /library, /library/<play>, /library/<play>/<act>/<scene>
export function LibraryScreen({ path }: { path: string[] }) {
  const [playId, ...rest] = path;
  if (!playId) return <LibraryHome />;
  if (rest.length === 0) return <PlayPage playId={playId} />;
  return <ScenePage playId={playId} sceneId={`${playId}/${rest.join("/")}`} />;
}

function useLoad<T>(load: () => Promise<T>, key: string) {
  const [state, setState] = useState<{ data?: T; error?: string }>({});
  useEffect(() => {
    let live = true;
    setState({});
    load().then(
      (data) => live && setState({ data }),
      (e: Error) => live && setState({ error: e.message }),
    );
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  return state;
}

function Status({ error }: { error?: string }) {
  return <p className="muted">{error ? `Couldn't load: ${error}` : "Loading…"}</p>;
}

function LibraryHome() {
  const { data, error } = useLoad(() => staticLibrary.index(), "index");
  const [twoHandersOnly, setTwoHandersOnly] = useState(false);
  if (!data) return <main className="library"><Status error={error} /></main>;

  const twoHanders = (p: PlaySummary) => p.scene_summaries.filter((s) => s.stats.two_hander).length;
  const plays = twoHandersOnly ? data.plays.filter((p) => twoHanders(p) > 0) : data.plays;
  const totalScenes = data.plays.reduce((n, p) => n + p.scenes, 0);
  const totalTwo = data.plays.reduce((n, p) => n + twoHanders(p), 0);

  return (
    <main className="library">
      <header>
        <p className="label">Library</p>
        <h1>Shakespeare</h1>
        <p className="muted">
          {data.plays.length} plays · {totalScenes} scenes · {totalTwo} two-handers (two speakers carry the
          scene)
        </p>
        <label className="toggle">
          <input type="checkbox" checked={twoHandersOnly} onChange={(e) => setTwoHandersOnly(e.target.checked)} />
          Only plays with two-handers
        </label>
      </header>
      <ul className="cards">
        {plays.map((p) => (
          <li key={p.id}>
            <a href={`/library/${p.id}`} className="card">
              <span className="title">{p.title}</span>
              <span className="muted small">
                {p.genre} · {p.scenes} scenes · {twoHanders(p)} two-handers · {p.words.toLocaleString()} words
              </span>
            </a>
          </li>
        ))}
      </ul>
    </main>
  );
}

function sceneLabel(s: { act: number | null; number: number | null; division: string }) {
  if (s.division !== "scene") return s.act ? `Act ${s.act} ${s.division}` : s.division;
  return `${s.act}.${s.number}`;
}

function PlayPage({ playId }: { playId: string }) {
  const { data, error } = useLoad(() => staticLibrary.play(playId), playId);
  const [twoHandersOnly, setTwoHandersOnly] = useState(false);
  if (!data) return <main className="library"><Status error={error} /></main>;

  const names = new Map(data.characters.map((c) => [c.id, c.name]));
  const scenes = data.scenes.filter((s) => !twoHandersOnly || s.stats?.two_hander);

  return (
    <main className="library">
      <a href="/library" className="back">← All plays</a>
      <header>
        <p className="label">{data.genre}</p>
        <h1>{data.title}</h1>
        <p className="muted small">
          {data.author} · Project Gutenberg #{data.source.ebook_id} · {data.characters.length} characters
        </p>
        <label className="toggle">
          <input type="checkbox" checked={twoHandersOnly} onChange={(e) => setTwoHandersOnly(e.target.checked)} />
          Only two-handers
        </label>
      </header>
      <table className="scenes">
        <thead>
          <tr>
            <th>Scene</th>
            <th>Where</th>
            <th>Who speaks most</th>
            <th className="num">Words</th>
          </tr>
        </thead>
        <tbody>
          {scenes.map((s) => (
            <SceneRow key={s.id} scene={s as unknown as SceneSummary} names={names} />
          ))}
        </tbody>
      </table>
    </main>
  );
}

function SceneRow({ scene, names }: { scene: SceneSummary; names: Map<string, string> }) {
  const speakers = scene.stats.speakers;
  const total = scene.stats.words || 1;
  return (
    <tr className={scene.stats.two_hander ? "two" : ""}>
      <td>
        <a href={`/library/${scene.id}`}>{sceneLabel(scene)}</a>
        {scene.stats.two_hander && <span className="badge">two-hander</span>}
      </td>
      <td className="muted">{scene.location}</td>
      <td>
        {speakers.slice(0, 3).map((sp) => (
          <span key={sp.character_id} className="speaker">
            {names.get(sp.character_id) ?? sp.character_id} {Math.round((100 * sp.words) / total)}%
          </span>
        ))}
        {speakers.length > 3 && <span className="muted"> +{speakers.length - 3}</span>}
      </td>
      <td className="num">{scene.stats.words.toLocaleString()}</td>
    </tr>
  );
}

function ScenePage({ playId, sceneId }: { playId: string; sceneId: string }) {
  const { data, error } = useLoad(() => staticLibrary.play(playId), playId);
  if (!data) return <main className="library"><Status error={error} /></main>;
  const index = data.scenes.findIndex((s) => s.id === sceneId);
  if (index === -1) return <main className="library"><p>No such scene: {sceneId}</p></main>;
  const scene: LibraryScene = data.scenes[index];
  const prev = data.scenes[index - 1];
  const next = data.scenes[index + 1];

  return (
    <main className="library reader">
      <a href={`/library/${playId}`} className="back">← {data.title}</a>
      <header>
        <p className="label">{sceneLabel(scene)} · {scene.heading}</p>
        <h1>{scene.location ?? data.title}</h1>
        {scene.stats && (
          <p className="muted small">
            {scene.stats.words.toLocaleString()} words · {scene.stats.speeches} speeches ·{" "}
            {scene.stats.speakers.length} speakers{scene.stats.two_hander ? " · two-hander" : ""}
          </p>
        )}
      </header>
      <div className="text">
        {scene.blocks.map((block, i) =>
          block.kind === "direction" ? (
            <p key={i} className="direction">{block.text}</p>
          ) : (
            <div key={i} className="speech">
              <p className="speaker-name">{block.speaker_label}</p>
              {block.parts.map((part, j) =>
                part.kind === "line" ? (
                  <p key={j} className="verse">{part.text}</p>
                ) : (
                  <p key={j} className="direction inline">{part.text}</p>
                ),
              )}
            </div>
          ),
        )}
      </div>
      <nav className="pager">
        {prev ? <a href={`/library/${prev.id}`}>← {sceneLabel(prev)}</a> : <span />}
        {next ? <a href={`/library/${next.id}`}>{sceneLabel(next)} →</a> : <span />}
      </nav>
    </main>
  );
}
