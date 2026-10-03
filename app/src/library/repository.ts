import type { LibraryIndex, LibraryRepository, Play } from "../../shared/library";

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
};
