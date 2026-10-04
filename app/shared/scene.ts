// The scene as the AI will eventually produce it. See docs/02-domain-model.md.

export type Beat = "setup" | "escalation" | "turn" | "ending";

export interface Line {
  character: string;
  /**
   * One turn: everything said before the other side speaks. Rows are separated by line
   * breaks; a row in [square brackets] is a direction that falls in the middle of the turn.
   */
  text: string;
  /** Silent description of how to deliver the line. */
  cue?: string;
  /** true: the host reads it. false: a ghost line, played by an improviser. */
  voiced: boolean;
  beat?: Beat;
}

export interface OpeningTask {
  character: string;
  /** A physical activity the improviser mimes before the first line. */
  task: string;
}

export interface Scene {
  /** Catalogue id; absent on the built-in demo. */
  id?: string;
  size?: "small" | "medium" | "big";
  /** Estimated running time. */
  minutes?: number;
  title: string;
  genre: string;
  /** What the play is about, in a sentence or two. */
  about: string;
  /** What the host needs to know about their character, and nothing more. */
  briefing: string;
  hostCharacter: string;
  openingTasks: OpeningTask[];
  lines: Line[];
}

/** One row of the catalogue of playable scenes (library/data/scenes/index.json). */
export interface SceneSummary {
  id: string;
  title: string;
  about: string;
  genre: string;
  host: string;
  partner: string;
  size: "small" | "medium" | "big";
  minutes: number;
  hostLines: number;
  score: number;
  opens: string;
}
