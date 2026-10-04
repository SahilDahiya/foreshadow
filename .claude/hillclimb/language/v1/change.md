Adds a "stay as close as a translator would" section that names the five kinds of small drift from the original (added, swapped, lost, feeling moved, hard phrase guessed) and ties closeness to line length, so compact originals are not unpacked into explanations and long sentences are split rather than stacked.

## The behaviour

The prompt's only faithfulness instruction is "keep every event, every piece of information, every image that matters". The model satisfies that at the level of the scene and then paraphrases freely at the level of the phrase. Almost every rendering contains one or two small departures: an inferred detail supplied, an image or title swapped for a neighbour, a forceful word dropped, a feeling shifted in kind, or an obscure Elizabethan phrase rendered by guess. The judge reads both renderings against the original and, because the two are otherwise near-identical, these phrase-level departures are what it decides on. The same looseness shows in length: a compact figure gets unpacked into an explanatory sentence, or a long original sentence is carried over as one long modern line, and the judge marks that down as hard to say.

## How often, and what it costs

- 18 of the 20 train passages show at least one judge-flagged drift of this kind in the candidate or the reference (both made by this prompt); the other two (Romeo and Juliet 2.2, Cymbeline 1.4) show only mild cases. The judge's reasoning mentions an addition, swap, loss or misreading in 36 of 40 runs, and a long or tangled line in 28 of 40.
- `faithful` is the criterion that tracks the overall verdict most closely: it was non-tied in 32 of 40 runs and agreed with the overall winner in 26 of the 36 decided runs (speakable 21, alive 18, natural 15, voice 4). Several verdicts say so outright ("Faithfulness decides it").
- Since the reference carries the same drifts at the same rate, a candidate that has none should win most of the comparisons that currently split by chance on which side happened to drift.

## Evidence

Added (inferred detail supplied):
- `baseline/traces/henry-iv-part-1_2_3_8-15_rep0.json`: "to claim his right to the crown, and he's sent for you". Judge: "adds an explanation not in the original (a mild invention, though historically plausible)". Same in `baseline/traces/henry-iv-part-1_2_3_8-15_rep1.json`: "stirring things up about his claim to the crown"; judge: "a mild over-specification".
- `baseline/traces/richard-iii_5_5_2-5_rep1.json`: "This crown, stolen and worn so long by the wrong man,". Judge: "adds 'wrong man', a small embellishment, and the line is long and clumsy to read aloud".
- `baseline/traces/the-two-gentlemen-of-verona_4_3_1-7_rep1.json`: "(Silvia appears above, at her window.)". Judge: "A adds 'at her window', a small invention."
- `baseline/traces/the-two-noble-kinsmen_2_1_15-19_rep0.json`: "They won't want to be stared at by the likes of us." Judge: "adds a class tone not in the original".
- `baseline/traces/king-lear_3_3_1-4_rep0.json` and `_rep1.json` (reference side): judge: "B adds a stage direction '(He leaves.)' that the original lacks, which is an invention"; in rep1 this alone decided the verdict ("B slightly ahead because it adds nothing").
- `baseline/traces/henry-vi-part-1_4_5_2-6_rep0.json` and `_rep1.json` (reference side): judge: "A's 'Father' is invented, though harmless ... slight edge to B for faithfulness (no invented word)".
- `baseline/traces/hamlet_1_4_3-8_rep0.json`: "to celebrate how well he drinks a toast." Judge: "invents a meaning, since the pledge is the toast itself".

Swapped (image, title or shape of thought replaced):
- `baseline/traces/a-midsummer-nights-dream_1_2_3-6_rep0.json`: "Well, our play is called The Most Tragic Comedy and Most Cruel Death of Pyramus and Thisbe." Judge: "a needless alteration of a title the audience knows". Same in `_rep1.json`. Lost both reps (pref 0.17).
- `baseline/traces/macbeth_2_2_12-19_rep0.json`: "as if they'd seen me standing there with these butcher's hands." Judge (on the same wording in rep1): "changes the image; a hangman is not a butcher".
- `baseline/traces/antony-and-cleopatra_1_3_11-18_rep0.json`: "What, has your wife said you can go?" Judge (rep1, same wording on the reference side): "loses the contempt".
- `baseline/traces/alls-well-that-ends-well_2_2_9-13_rep1.json`: "from the lowest duke down to the lowest constable." Judge: "a muddled invention that distorts the meaning".
- `baseline/traces/alls-well-that-ends-well_4_2_8-11_rep1.json`: "But look how I've sworn to you!" Judge (rep0): "changes it into a claim of abundant oaths".
- `baseline/traces/antony-and-cleopatra_3_4_2-4_rep0.json` (reference side): judge: "'I'll be standing between you' also changes the sense"; "'stripped of everything I am' adds something not in the original".

Feeling moved / casual idiom:
- `baseline/traces/the-two-noble-kinsmen_3_1_9-11_rep0.json` and `_rep1.json` (reference side): judge: "'I couldn't care less what you think' is a casual idiom that changes disdain into indifference".
- `baseline/traces/henry-iv-part-2_3_1_13-15_rep0.json`: "Staying up at these unhealthy hours can only make your sickness worse." Judge: "'unhealthy' shifts the meaning slightly".

Hard phrase guessed:
- `baseline/traces/pericles_1_3_5-8_rep0.json` and `_rep1.json` (reference side): judge: "'out of love for you' misreads 'unlicensed of your loves' and bends the meaning". The candidate's own attempt in rep0, "and why he'd leave without asking your permission, without the blessing of his loving people,", was called "redundant and long".
- `baseline/traces/the-two-noble-kinsmen_2_1_15-19_rep0.json`: judge: "Both render 'lower of the twain' as 'shorter', which is a misreading shared by both".

Lost:
- `baseline/traces/henry-iv-part-1_3_2_7-9_rep0.json` (reference side): judge: "B drops 'foul play' entirely, losing that content."

Length (unpacking, or one long line):
- `baseline/traces/antony-and-cleopatra_3_4_2-4_rep0.json`: the candidate's ""Husband, win!" "Brother, win!" Each prayer destroys the other." beat the reference's unpacked version, which the judge said "is longer and explains rather than speaks". Best train result (pref 0.83 both reps).
- `baseline/traces/a-midsummer-nights-dream_1_2_3-6_rep0.json`: "Here's the list of every man's name in all of Athens who's thought good enough to act in our play." Judge: "one long line, which is harder to say in one breath".
- `baseline/traces/cymbeline_1_4_7-10_rep0.json` and `_rep1.json`: "before you stopped following him with your eyes." closes one long opening sentence. Judge: "A runs the opening into one long line ... The split is easier to say at sight". Lost both reps on this alone.
- `baseline/traces/richard-iii_5_5_2-5_rep0.json`: "I pulled it off the dead head of this bloody wretch, to put it on yours." Judge: "one long line to say in a breath ... B splits it into two lines".
- `baseline/traces/the-merchant-of-venice_1_3_35-37_rep0.json`: "When did friendship ever squeeze a profit out of a friend from metal that can't breed?" Judge: "tangled and needs a second read".

## Possible regressions

- Passages where the judge liked a rendering that clarified a dense image: in `baseline/traces/the-merchant-of-venice_1_3_35-37_rep0.json` and `_rep1.json` the reference won with a line the judge admitted "adds the word 'interest'" because it was clearer. A stricter no-additions rule could cost a little there.
- Passages where the looser side won on `alive`: Macbeth 2.2 and Hamlet 1.4, where the judge called the less faithful wording "more alive" or "livelier". Closer renderings may give up a little on `alive` and `natural` (the judge sometimes calls the faithful option "slightly stiff" or "a bit dated", as in The Two Gentlemen of Verona 4.3 and Pericles 1.3). The final paragraph of the new section is there to limit this.
- `valid` should not move: the block, speaker, direction and banned-word rules are unchanged, and the added line-length guidance pushes lines shorter, away from the 28-word limit.
