import type {
  CandidateList,
  LibraryIndex,
  LibraryRepository,
  Play,
  StretchIndexEntry,
  StretchRendition,
} from "../../shared/library";

const BASE = "/data/library";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE}/${path}`);
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return (await response.json()) as T;
}

// Reads the files `library publish` copies into app/public/data/library.
export const staticLibrary: LibraryRepository = {
  index: () => getJson<LibraryIndex>("index.json"),
  play: (id) => getJson<Play>(`plays/${encodeURIComponent(id)}.json`),
  candidates: () => getJson<CandidateList>("candidates.json"),
  // No renderings published yet is not an error: the list is just empty.
  stretchIndex: () => getJson<StretchIndexEntry[]>("stretch_renditions.json").catch(() => []),
  stretch: (file) => getJson<StretchRendition>(file),
};
