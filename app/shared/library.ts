// The play library, as published by library/ (Python). Mirrors
// library/src/foreshadow_library/domain.py; keep the two in step until the types are
// generated from the Pydantic models.

export interface Character {
  id: string;
  name: string;
  description: string | null;
  in_dramatis_personae: boolean;
}

export type SpeechPart = { kind: "line"; text: string } | { kind: "direction"; text: string };

export type Block =
  | { kind: "speech"; speaker_ids: string[]; speaker_label: string; parts: SpeechPart[] }
  | { kind: "direction"; text: string };

export interface SpeakerStats {
  character_id: string;
  speeches: number;
  lines: number;
  words: number;
}

export interface SceneStats {
  words: number;
  lines: number;
  speeches: number;
  speakers: SpeakerStats[];
  two_hander: boolean;
}

export type Division = "scene" | "prologue" | "induction" | "epilogue" | "chorus";

export interface LibraryScene {
  id: string;
  act: number | null;
  number: number | null;
  division: Division;
  heading: string;
  location: string | null;
  blocks: Block[];
  stats: SceneStats | null;
}

export interface Play {
  id: string;
  title: string;
  author: string;
  genre: string | null;
  source: { provider: string; ebook_id: number; url: string; retrieved_at: string; sha256: string };
  characters: Character[];
  scenes: LibraryScene[];
}

export interface SceneSummary {
  id: string;
  act: number | null;
  number: number | null;
  division: Division;
  location: string | null;
  stats: SceneStats;
}

export interface PlaySummary {
  id: string;
  title: string;
  author: string;
  genre: string | null;
  scenes: number;
  characters: number;
  words: number;
  scene_summaries: SceneSummary[];
}

export interface LibraryIndex {
  plays: PlaySummary[];
}

export interface CandidateMetrics {
  host_speeches: number;
  partner_speeches: number;
  host_words: number;
  partner_words: number;
  host_share: number;
  mean_host_words: number;
  median_host_words: number;
  max_host_words: number;
  monologues: number;
  minutes: number;
  questions: number;
  address: number;
  names: number;
  directions: number;
  cast_changes: number;
}

/** A two-person stretch of a scene, trimmed so the host's character opens and closes it. */
export interface Candidate {
  id: string;
  play_id: string;
  play_title: string;
  genre: string | null;
  scene_id: string;
  start: number;
  end: number;
  host: string;
  host_name: string;
  partner: string;
  partner_name: string;
  first_line: string;
  last_line: string;
  metrics: CandidateMetrics;
  size: "small" | "medium" | "big";
  cut: boolean;
  score: number;
  reasons: string[];
}

export interface CandidateList {
  counts: Record<string, number>;
  candidates: Candidate[];
}

/** A stretch of a scene rendered in today's English, block for block with the original. */
export interface StretchRendition {
  scene_id: string;
  prompt_version: string;
  model: string;
  blocks: { source_block: number; parts: SpeechPart[] }[];
  check_warnings: string[];
}

export interface StretchIndexEntry {
  scene_id: string;
  start: number;
  end: number;
  file: string;
}

/** Where the app gets plays. Static files today; an API backed by D1 or R2 later. */
export interface LibraryRepository {
  index(): Promise<LibraryIndex>;
  play(id: string): Promise<Play>;
  candidates(): Promise<CandidateList>;
  stretchIndex(): Promise<StretchIndexEntry[]>;
  stretch(file: string): Promise<StretchRendition>;
}
