import type { Scene } from "./scene";

// Hard-coded until the AI writes scenes. Macbeth engine, soap opera genre.
// No phones, screens or apps: the host's phone is not part of the play.
export const DEMO_SCENE: Scene = {
  title: "The Last Loaf",
  genre: "Soap opera",
  about:
    "Two sisters run their late mother's failing bakery. A fortune teller tells one of them the bakery will soon be hers alone.",
  briefing:
    "You are MARGOT, the older sister. You run the till, believe every word the fortune teller on the pier tells you, and have spent twelve years in the shadow of your sister DIANA's bread.",
  hostCharacter: "MARGOT",
  openingTasks: [{ character: "DIANA", task: "Icing a cake" }],
  lines: [
    { character: "MARGOT", voiced: true, beat: "setup", cue: "breathless, bursting in", text: "Diana. Put down the piping bag. Madame Zara has spoken." },
    { character: "DIANA", voiced: false, beat: "setup", text: "Not the fortune teller on the pier again. It's five in the morning, Margot." },
    { character: "MARGOT", voiced: true, beat: "setup", cue: "reciting, trembling", text: "\"By the next full moon, the bakery becomes yours… once the other is gone.\" She meant me, Diana. You are the other." },
    { character: "DIANA", voiced: false, beat: "setup", text: "I'm also the one who bakes. You do the till." },
    { character: "MARGOT", voiced: true, beat: "escalation", cue: "wounded, then cold", text: "Twelve years I've done the till. Twelve years of your sourdough getting the reviews." },
    { character: "DIANA", voiced: false, beat: "escalation", text: "People like sourdough. Where's the cream cheese?" },
    { character: "MARGOT", voiced: true, beat: "escalation", cue: "far too quickly", text: "Don't go in the walk-in freezer." },
    { character: "DIANA", voiced: false, beat: "escalation", text: "Why not? What's in the freezer, Margot?" },
    { character: "MARGOT", voiced: true, beat: "escalation", cue: "whispering, glancing at the door", text: "Nothing. A swan. It's nothing. It's a swan." },
    { character: "DIANA", voiced: false, beat: "escalation", text: "A live swan? In the freezer?" },
    { character: "MARGOT", voiced: true, beat: "escalation", cue: "defensive", text: "Madame Zara said a white bird would carry away my rival. I took initiative." },
    { character: "DIANA", voiced: false, beat: "escalation", text: "You can't own a swan. They all belong to the King." },
    { character: "MARGOT", voiced: true, beat: "turn", cue: "freezing, staring into the distance", text: "Then let the King come for his swan." },
    { character: "DIANA", voiced: false, beat: "turn", text: "I'm calling Dad." },
    { character: "MARGOT", voiced: true, beat: "turn", cue: "a sharp intake of breath", text: "Dad can't help you now. Dad signed the bakery over to me last night." },
    { character: "DIANA", voiced: false, beat: "turn", text: "He would never. He promised it to both of us." },
    { character: "MARGOT", voiced: true, beat: "turn", cue: "unfolding an invisible paper, slowly", text: "He promised it to both of us. He signed it to one of us. Madame Zara was right, Diana. She always is." },
    { character: "DIANA", voiced: false, beat: "ending", text: "You manipulated him with a fortune teller." },
    { character: "MARGOT", voiced: true, beat: "ending", cue: "breaking, almost tender", text: "I did it so that someone would finally look at me instead of your bread." },
    { character: "DIANA", voiced: false, beat: "ending", text: "Margot… is the swan okay?" },
    { character: "MARGOT", voiced: true, beat: "ending", cue: "aside, to the audience, then back", text: "The swan is fine. The swan is thriving. I, Diana, am not." },
    { character: "DIANA", voiced: false, beat: "ending", text: "Then come here. We'll ice this one together." },
    { character: "MARGOT", voiced: true, beat: "ending", cue: "taking the piping bag; a slow, cold smile", text: "Together. Of course. What's your star sign again, Diana?" },
  ],
};
