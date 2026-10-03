// The scene as the AI will eventually produce it. See docs/02-domain-model.md.

export type Beat = "setup" | "escalation" | "turn" | "ending";

export interface Line {
  character: string;
  text: string;
  /** Silent description of how to deliver the line. */
  cue?: string;
  /** true: the host reads it. false: a ghost line, played by an improviser. */
  voiced: boolean;
  beat: Beat;
}

export interface OpeningTask {
  character: string;
  /** A physical activity the improviser mimes before the first line. */
  task: string;
}

export interface Scene {
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
