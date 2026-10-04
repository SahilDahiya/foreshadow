Splits the brief into "what is said is fixed" (round 1's faithfulness rules, compressed to one paragraph) and "how it is said is entirely new" (work from the meaning, not the wording: no carried-over old words, word-for-word figures, old courtesy forms or old sentence order), with one thought per line and a two-pass check.

## Why round 1 failed to move pref

Round 1 got its faithfulness by not translating. Told that every phrase must be traceable to the original and that nothing may be added, swapped or lost, the model took the safest route: it left the original's words and sentence shapes standing and only tidied the grammar. The judge then gave it `faithful` and took away `natural` and `speakable` in the same breath, usually naming the very phrase that had been carried over. The verdicts are nearly all "slight" either way, which is why pref did not move: one criterion was traded for two.

What the judge disliked in round 1's renderings, verbatim from the candidate with the judge's comment:

Old words kept because they are still in the dictionary:
- `v1/traces/antony-and-cleopatra_1_3_11-18_rep1.json`: "I am sick and sullen." / "The body's frame won't hold up under it." / "I'm sorry to have to put into words what I intend". Judge: "is stiff ... is awkward"; of the reference: "'My body can't take it' is easy to say aloud".
- `v1/traces/hamlet_1_4_3-8_rep0.json`: "reeling through the swaggering upspring dance." Judge: "an obscure Elizabethan term that an actor would stumble on and a listener might not understand". In rep1, "trumpeting the triumph of his toast." Judge: "a tongue-twister".
- `v1/traces/henry-iv-part-1_2_3_8-15_rep1.json`: "I'm afraid my brother Mortimer is stirring about his title. And he's sent for you to back his enterprise." Judge: "leftover archaic phrasing that is unclear, and 'back his enterprise' is stiff". Clear loss both reps (pref 0.17).
- `v1/traces/cymbeline_1_4_7-10_rep1.json`: "I would have broken my eyestrings, cracked them, just to look at him," Judge: "'eyestrings' is archaic and may confuse a listener".
- `v1/traces/alls-well-that-ends-well_2_2_9-13_rep1.json`: "if the learned would tell the truth about it." / "It must be an answer of monstrous size". Judge: "faithful but slightly archaic-sounding and a bit stiff ... a bit formal".
- `v1/traces/romeo-and-juliet_2_2_12-15_rep0.json`: "So your kinsmen are no obstacle to me." / "Stone boundaries can't keep love out." Judge: "'Stone boundaries' is a bit stiff"; of the reference: "'So your family can't stop me' is punchy and speakable".

Figures carried across word for word:
- `v1/traces/the-merchant-of-venice_1_3_35-37_rep0.json`: "When did friendship ever take interest from a friend, breeding barren metal?" / "take the penalty with a clearer face." Judge: "(literal, odd) ... garbled syntax ... needs a second read".
- `v1/traces/alls-well-that-ends-well_4_2_8-11_rep0.json`: "would you believe my oaths, when my love for you was bad?" Judge: "awkward"; "'poor terms' ... a bit stiff".
- `v1/traces/antony-and-cleopatra_3_4_2-4_rep1.json`: "Better I weren't yours at all than yours with my branches lopped off like that." Judge: "a muddled image ... the listener may be confused".
- `v1/traces/henry-iv-part-1_3_2_7-9_rep0.json`: "Your face is full of haste." Judge: "stays close to the original but is a little odd"; of the reference: "'You look like you've come in a hurry' ... more natural".
- `v1/traces/the-two-noble-kinsmen_2_1_15-19_rep0.json`: "They wouldn't want to make us the thing they look at." Judge: "a little clumsy".
- `v1/traces/pericles_1_3_5-8_rep1.json`: "as if without your loving permission". Judge: "clumsy and a bit muddled"; reference "easier to say aloud and sounds more natural".

Old courtesy forms, oaths and moods left in place:
- `v1/traces/henry-iv-part-2_3_1_13-15_rep0.json`: "If it please your Grace, go to bed." / "Upon my soul, my lord," / "And once these wars at home were finished, dear lords, we would go to the Holy Land." Judge: "retain archaic flavor ... less natural"; "a slightly odd tense ... sounds stilted". Clear loss (pref 0.17).
- `v1/traces/richard-iii_5_5_2-5_rep0.json`: "Brave Richmond, you have done well!" / "If it please you, we can go there now." Judge (rep1): "slightly more archaic ... 'withdraw there now' is stiff".
- `v1/traces/the-two-gentlemen-of-verona_4_3_1-7_rep0.json`: "I'm here to learn what service you'd like to command me in." Judge: "'command me in' is a bit stiff".

The old sentence carried over as one long line (the `speakable` loss):
- `v1/traces/richard-iii_5_5_2-5_rep0.json`: "I have pulled it off the dead head of this bloody wretch, to grace your brow with it." Judge: "one long line, which is hard to say in one breath and slightly stiff"; the reference "splits it into two lines, which is easier to read at sight".
- `v1/traces/henry-iv-part-1_2_3_8-15_rep0.json`: "A weasel doesn't have as much temper as the temper that's tossing you about." Judge: "clumsy and repetitive".
- `v1/traces/cymbeline_1_4_7-10_rep0.json`: "just to look at him, till the distance had shrunk him to a point as sharp as my needle." Judge: "long ... a bit awkward in one breath".

## What the baseline does that the judge calls natural

It re-says the thought in a sentence a person would say, usually shorter and split: "My body can't take it", "You look like you've come in a hurry" (`baseline/traces/henry-iv-part-1_3_2_7-9_rep0.json`), "Staying up at these unhealthy hours can only make your sickness worse" (`baseline/traces/henry-iv-part-2_3_1_13-15_rep0.json`), "I'll find out what you're up to" (`baseline/traces/henry-iv-part-1_2_3_8-15_rep0.json`), "the dancing's wild and reeling" (reference in `baseline/traces/hamlet_1_4_3-8_rep0.json`; judge: "smoother to speak"). None of these needed the drift that the baseline also commits; the naturalness and the drift are separate things.

## The two can be had together

Everything the judge credited round 1 for on `faithful` is content, not old wording: no invented address or exit (`v1/traces/henry-vi-part-1_4_5_2-6_rep0.json`, `v1/traces/king-lear_3_3_1-4_rep1.json`), the pointed epithet kept (`v1/traces/antony-and-cleopatra_1_3_11-18_rep0.json`), the image not swapped (`v1/traces/macbeth_2_2_12-19_rep0.json`), the question left a question (`v1/traces/alls-well-that-ends-well_4_2_8-11_rep1.json`), the compact figure not unpacked (`v1/traces/antony-and-cleopatra_3_4_2-4_rep0.json`), the positional word not misread (`v1/traces/the-two-noble-kinsmen_2_1_15-19_rep0.json`). None of those wins depended on a stiff phrase. Where round 1 was faithful and plain at once it won on everything: `v1/traces/henry-vi-part-1_4_5_2-6_rep0.json` and `_rep1.json` (pref 0.83 both; judge: "more faithful and just as speakable and natural").

## Hypothesis

The model treats closeness to the original as closeness of wording. Give it the distinction explicitly: content is fixed phrase by phrase, wording and sentence shape are wholly replaced, and a carried-over word or construction is named as a failure ("untranslated") rather than as the safe option. Add the mechanism (settle what the person is telling the listener, then say exactly that as speech), a rule per failure kind (surviving words, figures, unknown terms, formality), one thought per line with long sentences split, and a two-pass check that tests sound first and content second. Round 1's five drift kinds are kept but compressed into one paragraph; the prompt is shorter than round 1's.

## How often

Carried-over wording that the judge flags as stiff, archaic, literal, awkward or tangled appears in 19 of the 20 train passages in round 1 (all but Henry VI Part 1 4.5, the one passage it won cleanly). The candidate lost or tied `natural` in 40 of 40 runs (lost 37) and lost `speakable` in 27 of 40. In the baseline the same passages lose `natural` in 14 runs and `speakable` in 19, mostly on single long lines.

## Expected regressions

- A Midsummer Night's Dream 1.2 and Macbeth 2.2: lines that are already today's English and that the judge wants left nearly intact; a model keen to re-say everything may reword what did not need it. The "survives where it is still the word people use" sentence is there for this.
- The Merchant of Venice 1.3 and Antony and Cleopatra 3.4: dense figures where "keep the picture, do not explain" and "lands at first hearing" pull against each other; the judge has rewarded both a compact figure and a clarifying gloss on these.
- `faithful` will probably fall from round 1's 0.875 toward 0.7 or so as re-saying reintroduces some small shifts; it should stay above the baseline's 0.55 because the no-additions and no-swaps rules are retained and checked last.
- `valid` should not move: block, speaker, direction and banned-word rules are unchanged and lines get shorter.
