import { Fragment, useEffect, useState } from "react";
import type {
  Block,
  Candidate,
  LibraryScene,
  PlaySummary,
  SceneSummary,
  SpeechPart,
  StretchIndexEntry,
} from "../../shared/library";
import { staticLibrary } from "./repository";
import "./library.css";

// Internal browser for the play library: every play, every scene, and the text as parsed.
// Routes: /library, /library/<play>, /library/<play>/<act>/<scene>
export function LibraryScreen({ path }: { path: string[] }) {
  const [playId, ...rest] = path;
  if (!playId) return <LibraryHome />;
  if (playId === "candidates") return <CandidatesPage />;
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
        <p>
          <a href="/library/candidates">Scene candidates for the show →</a>
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

const GENRES = ["all", "tragedy", "comedy", "history", "romance"];
const SIZES = [
  { id: "all", label: "any length" },
  { id: "small", label: "small · about 5 min" },
  { id: "medium", label: "medium · about 10 min" },
  { id: "big", label: "big · about 20 min" },
];

function covering(index: StretchIndexEntry[], sceneId: string, start: number, end: number) {
  return index.find((e) => e.scene_id === sceneId && e.start <= start && e.end >= end);
}

function candidateLink(c: Candidate) {
  return `/library/${c.scene_id}?start=${c.start}&end=${c.end}&host=${encodeURIComponent(c.host)}`;
}

// Stretches of scenes that could be performed: two speakers, the host opening and closing.
function CandidatesPage() {
  const { data, error } = useLoad(() => staticLibrary.candidates(), "candidates");
  const rendered = useLoad(() => staticLibrary.stretchIndex(), "stretch-index").data ?? [];
  const [modernOnly, setModernOnly] = useState(true);
  const [genre, setGenre] = useState("all");
  const [size, setSize] = useState("all");
  const [onePerScene, setOnePerScene] = useState(true);
  if (!data) return <main className="library"><Status error={error} /></main>;

  let list = data.candidates.filter((c) => (genre === "all" || c.genre === genre) && (size === "all" || c.size === size));
  const hasModern = (c: Candidate) => Boolean(covering(rendered, c.scene_id, c.start, c.end));
  if (modernOnly && rendered.length) list = list.filter(hasModern);
  if (onePerScene) {
    const seen = new Set<string>();
    list = list.filter((c) => (seen.has(c.scene_id) ? false : (seen.add(c.scene_id), true)));
  }
  return (
    <main className="library">
      <a href="/library" className="back">← All plays</a>
      <header>
        <p className="label">Candidates</p>
        <h1>Scenes for the show</h1>
        <p className="muted">
          {data.counts.scenes} scenes searched · {data.candidates.length} stretches pass: two speakers, the host opens and
          closes, the improviser gets enough turns, nobody enters or leaves. Monologues are allowed. Running times are
          estimates. Ranked by structure only; nobody has judged the content yet.
        </p>
        <div className="filters">
          {SIZES.map((s) => (
            <button key={s.id} className={s.id === size ? "chip on" : "chip"} onClick={() => setSize(s.id)}>{s.label}</button>
          ))}
        </div>
        <div className="filters">
          {GENRES.map((g) => (
            <button key={g} className={g === genre ? "chip on" : "chip"} onClick={() => setGenre(g)}>{g}</button>
          ))}
          <label className="toggle">
            <input type="checkbox" checked={onePerScene} onChange={(e) => setOnePerScene(e.target.checked)} />
            Best one per scene
          </label>
          <label className="toggle">
            <input type="checkbox" checked={modernOnly} onChange={(e) => setModernOnly(e.target.checked)} />
            Only those rendered in today’s English ({rendered.length} scenes)
          </label>
        </div>
        <p className="muted small">Showing {list.length}.</p>
      </header>
      <table className="scenes">
        <thead>
          <tr>
            <th className="num">Score</th>
            <th>Scene</th>
            <th>Host reads · improviser plays</th>
            <th>Opens with / closes with</th>
            <th className="num">Minutes</th>
            <th className="num">Turns</th>
            <th className="num">Monologues</th>
          </tr>
        </thead>
        <tbody>
          {list.map((c) => (
            <tr key={c.id} title={c.reasons.join(" · ")}>
              <td className="num">{c.score.toFixed(0)}</td>
              <td>
                <a href={candidateLink(c)}>{c.play_title} {c.scene_id.split("/").slice(1).join(".")}</a>
                <div className="muted small">{c.genre} · {c.size}{c.cut ? " (a shorter cut)" : ""}</div>
                {hasModern(c) && <span className="badge">today’s English</span>}
              </td>
              <td>
                <strong>{c.host_name}</strong>
                <div className="muted small">with {c.partner_name}</div>
              </td>
              <td className="lines">
                <div>“{c.first_line}”</div>
                <div className="muted">… “{c.last_line}”</div>
              </td>
              <td className="num">{c.metrics.minutes.toFixed(0)}</td>
              <td className="num">{c.metrics.host_speeches}</td>
              <td className="num">{c.metrics.monologues || ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
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

function PartsView({ parts }: { parts: SpeechPart[] }) {
  return (
    <>
      {parts.map((part, j) =>
        part.kind === "line" ? (
          <p key={j} className="verse">{part.text}</p>
        ) : (
          <p key={j} className="direction inline">{part.text}</p>
        ),
      )}
    </>
  );
}

function BlockView({ block, className = "" }: { block: Block; className?: string }) {
  return block.kind === "direction" ? (
    <p className={"direction " + className}>{block.text}</p>
  ) : (
    <div className={"speech " + className}>
      <p className="speaker-name">{block.speaker_label}</p>
      <PartsView parts={block.parts} />
    </div>
  );
}

// A candidate stretch: the original beside today's English when a rendering exists.
function StretchView(props: { scene: LibraryScene; start: number; end: number; host: string | null; hostName: string; playId: string }) {
  const { scene, start, end, host } = props;
  const index = useLoad(() => staticLibrary.stretchIndex(), "stretch-index").data;
  const entry = index ? covering(index, scene.id, start, end) : undefined;
  const modern = useLoad(() => (entry ? staticLibrary.stretch(entry.file) : Promise.resolve(null)), entry?.file ?? "none").data;
  const byBlock = new Map(modern?.blocks.map((b) => [b.source_block, b.parts]) ?? []);
  const rows = scene.blocks.map((block, i) => ({ block, i })).filter(({ i }) => i >= start && i < end);

  return (
    <>
      <p className="stretch-note">
        The host reads <strong>{props.hostName}</strong> (amber) and opens and closes the scene. The improviser plays the
        other part (blue) without ever seeing it.{" "}
        {modern
          ? `Today’s English is on the right (prompt ${modern.prompt_version}).`
          : index && !entry
            ? "This stretch has not been rendered in today’s English yet."
            : ""}{" "}
        <a href={`/library/${scene.id}`}>See the whole scene</a>
      </p>
      <div className={modern ? "pair-grid" : "text"}>
        {modern && (
          <>
            <p className="label">Original</p>
            <p className="label">Today’s English</p>
          </>
        )}
        {rows.map(({ block, i }) => {
          const cls = block.kind === "speech" && block.speaker_ids[0] === host ? "host-part" : "ghost-part";
          const parts = byBlock.get(i);
          return (
            <Fragment key={i}>
              <BlockView block={block} className={cls} />
              {modern &&
                (block.kind === "direction" ? (
                  <p className={"direction " + cls}>{parts?.map((p) => p.text).join(" ") ?? ""}</p>
                ) : (
                  <div className={"speech modern " + cls}>
                    <p className="speaker-name">{block.speaker_label}</p>
                    {parts ? <PartsView parts={parts} /> : <p className="muted">(not rendered)</p>}
                  </div>
                ))}
            </Fragment>
          );
        })}
      </div>
    </>
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
  // A candidate link carries the stretch to show and which character the host reads.
  const query = new URLSearchParams(window.location.search);
  const stretch = query.has("start")
    ? { start: Number(query.get("start")), end: Number(query.get("end")), host: query.get("host") }
    : null;
  const hostName = stretch ? data.characters.find((c) => c.id === stretch.host)?.name : null;

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
      {stretch ? (
        <StretchView scene={scene} start={stretch.start} end={stretch.end} host={stretch.host} hostName={hostName ?? ""} playId={playId} />
      ) : (
        <div className="text">
          {scene.blocks.map((block, i) => (
            <BlockView key={i} block={block} />
          ))}
        </div>
      )}
      <nav className="pager">
        {prev ? <a href={`/library/${prev.id}`}>← {sceneLabel(prev)}</a> : <span />}
        {next ? <a href={`/library/${next.id}`}>{sceneLabel(next)} →</a> : <span />}
      </nav>
    </main>
  );
}
