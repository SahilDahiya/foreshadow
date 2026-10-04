Moves the unit of translation from the phrase to the whole sentence: read the sentence through, settle what is being told, say it from scratch with your own subject, verb and order, then count the content back in; lines are cut from those sentences rather than from the original's clauses, and the 28-word limit is restated.

## The behaviour

Round 2 fixed the words. The candidate's vocabulary is now ordinary almost everywhere. What the judge still marks down on `natural` is the frame of the sentence: the candidate replaces each old phrase with a modern one and leaves them standing in the original's grammar, so one or two sentences per passage come out with modern words on an old skeleton. The reference (and the baseline) says the same thing with the sentence rebuilt.

The kinds, with the candidate's line, the judge's comment, and what the judge preferred:

A noun or participle where speech uses a clause:
- `v2/traces/macbeth_2_2_12-19_rep0.json`: "Listening to their fear, I couldn't say "Amen"". Judge: "a bit literary"; the reference's "I listened to how scared they were" is "smoother". Same trace: "That's a foolish thing to think, calling it a miserable sight." Judge: "a bit awkward" (rep1: "a bit clunky").
- `v2/traces/richard-iii_5_5_2-5_rep0.json`: "to set it on your brow and honor you." Judge: "a bit stiff"; "Look, here is the crown, so long usurped." Judge: "a slightly formal word"; the reference's "he stole and held so long" is "natural and speakable". Lost.
- `v2/traces/antony-and-cleopatra_1_3_11-18_rep1.json`: "I'm sorry to have to say out loud what I intend—". Judge: "a bit awkward, while B's 'tell you what I'm planning' is smoother".

A passive or a roundabout person kept as built:
- `v2/traces/henry-iv-part-1_2_3_8-15_rep0.json`: "A weasel doesn't have half the temper / that you're tossed about by." Judge: "a slightly awkward leftover ... its wording is less natural". Rep1: "as much temper / as the fits that toss you around." Judge: "also awkward". Lost both reps.
- `v2/traces/the-two-noble-kinsmen_3_1_9-11_rep0.json`: "It's no use saying it to the ear of one who now scorns you." Judge: "a bit long and slightly awkward"; "the whole week isn't fine / if it rains on any day of it." Judge: "a bit stiff"; the reference's "if it rains a single day, you can't call the whole week fine" is "more natural and speakable".
- `v2/traces/pericles_1_3_5-8_rep1.json`: "why he'd leave, as it were, without the permission of you who love him,". Judge: "faithful but clunky and long to say ... awkward".
- `v2/traces/the-two-gentlemen-of-verona_4_3_1-7_rep1.json`: "There's some important business she means to give me." Judge: "a little stilted, while B's 'needs me for' is natural". Lost.

An aside or condition left wedged where the original had it:
- `v2/traces/alls-well-that-ends-well_2_2_9-13_rep1.json`: "Do you really have, I'm asking you, an answer that suits every question?" Judge: "awkward and carries the archaic 'I say' word for word, which would trip an actor". Lost. Rep0 of the same passage moved the aside to the front ("I'm asking you: do you really have an answer that fits every question?") and won clearly (0.83).
- `v2/traces/king-lear_3_3_1-4_rep0.json`: "They ordered me, or lose their favour forever," Judge: "ungrammatical and tangled"; "and they've threatened me with nothing less" Judge: "clumsy"; the reference's "longer lines hold together as spoken sentences". Lost. Rep1 rebuilt the same sentences and won clearly (0.83).
- `v2/traces/henry-iv-part-2_3_1_13-15_rep0.json`: "And once these wars at home were dealt with, / we would go, dear lords, to the Holy Land." Judge: "slightly awkward mixed tense".

The old sentence cut into line-sized pieces, so the pieces no longer say what the sentence said:
- `v2/traces/a-midsummer-nights-dream_1_2_3-6_rep0.json`: "All the men in Athens thought fit to act in our play." Judge: "reads as though every man in Athens was chosen, which distorts the meaning"; "And that way work up to the point." Judge: "a bit awkward". Rep1: "who's thought fit, in all of Athens," Judge: "a bit stilted when broken across lines".
- `v2/traces/hamlet_1_4_3-8_rep0.json`: "He's holding a drinking party. / He reels through the wild, swaggering dances." Judge: "makes the King himself reel and adds a redundant line". Lost.
- `v2/traces/antony-and-cleopatra_1_3_11-18_rep1.json`: "My body will split at the sides. It can't bear it." Judge: "a vivid but wrong image ... would confuse listeners"; the reference's "My body can't take it" is "accurate". Lost. The hard phrase was carried word for word and then guessed at.
- `v2/traces/alls-well-that-ends-well_4_2_8-11_rep0.json`: "would you believe my oaths, / when my love for you meant you harm?" Judge: "garbles" the original; "flimsy terms, and never sealed" Judge: "slightly odd". Lost.

What the baseline does on the same sentences: "I listened to how scared they were, and I couldn't say "Amen"" (`baseline/traces/macbeth_2_2_12-19_rep0.json`); "They ordered me, or I'd lose their favour forever, not to speak of him" (`baseline/traces/king-lear_3_3_1-4_rep0.json`); "There's something important she needs me for." (`baseline/traces/the-two-gentlemen-of-verona_4_3_1-7_rep0.json`); "If you're willing, we can go there now." (`baseline/traces/richard-iii_5_5_2-5_rep1.json`). None of these adds or drops anything. The baseline's own losses come from elsewhere (long single lines, invented details), which v2 already fixed.

## Hypothesis

v2's own wording steers the model to work phrase by phrase: "Each phrase of the original has its counterpart", "For each phrase, settle what this person is telling this listener", "in the same order with everything still in them". The model obeys: it swaps phrases and keeps the frame, then cuts the frame into lines at clause boundaries. Word-level naturalness improved (that is what v2 named), sentence-level did not. Where the model happened to rebuild the sentence (the winning rep of All's Well 2.2 and of King Lear 3.3) the same passage went from a loss to a clear win with `faithful` still 1.0, so the stiffness is not what buys the faithfulness.

The change: content is still fixed, but it is counted per sentence after the sentence has been composed, not mapped phrase to phrase while composing. The prompt names the frame-level carry-overs (noun for verb, opening participle, passive, wedged aside, roundabout person, old-style comparison), gives the procedure (read to the end, settle the meaning including the hard part, put the original away, say it from scratch, count back), grants freedom over grammar inside a sentence while fixing the order of sentences, and tells the model to split a long sentence only when the pieces say the same thing. Cut to make room: v2's list of word-level failures (that work is done), the standalone "work out what it means" sentence (folded into the procedure), and "each character still sounds like themselves" (`voice` has been 0.5 in every round with or without it). The 28-word limit is restated in the lines paragraph as a fixed-rule repair. Length is 758 words against v2's 743.

## How often and what it costs

The candidate loses `natural` outright in 22 of 40 runs, across 15 of the 20 passages; it wins it in 2. The judge names a carried-over construction as stiff, awkward, clunky, stilted or tangled in 19 of 20 passages in at least one rep (all but Henry VI Part 1 4.5).

Cost on `pref`:
- Of the 11 lost runs, 9 are decided or tipped by such a sentence: Romeo and Juliet rep0, Antony and Cleopatra 1.3 rep1, Henry IV Part 1 2.3 both reps, All's Well 2.2 rep1, Richard III rep0, King Lear rep0, All's Well 4.2 rep0, Two Gentlemen rep1, plus the two mis-cut sentences in Midsummer Night's Dream rep0 and Hamlet rep0 (all 11 with those; Henry IV Part 1 2.3 also carries a separate invented detail).
- Of the 26 won runs, 17 are "slight" (0.67) and 9 "clear" (0.83); 3 runs are ties, and in most the judge's sentence is some form of "A more faithful, B reads more easily".

Turning half the slight wins into clear ones is worth about +0.03 on `pref`; recovering half the phrase-decided losses is worth about +0.04 to +0.05. A full fix is therefore around +0.08 to +0.10, at or just above the ±0.09 noise floor; a partial fix will not show clearly.

Part of the `natural` deficit is not recoverable. In about five passages the phrase the judge calls more natural in the reference is one it also marks as an invention or a shift: "stupid thing to say" and "butcher's hands" (Macbeth), "I couldn't care less what you think" (Two Noble Kinsmen 3.1), "your wife" (Antony and Cleopatra 1.3), "raging away" (Merchant), "stole and held so long" (Richard III). The candidate should not chase those. I would expect `natural` to rise to roughly 0.4 to 0.5, not above.

## Expected regressions

- `faithful` is the risk: freedom to rebuild a sentence is freedom to drift. Passages where a close construction is what currently wins the fidelity point: The Two Noble Kinsmen 3.1 (the indirect way the speaker refers to himself), Pericles 1.3 (the hedged, odd permission phrase), Henry IV Part 2 3.1 (the wistful conditional in the last couplet, which a speaker "now" would flatten into a plain future, as the reference did and was marked down for), Antony and Cleopatra 3.4 (the compact figure). The count-back step and the unchanged "what is said" paragraph are there for this; I would still expect `faithful` to give back a little, to about 0.7.
- `speakable` may slip on King Lear 3.3 and Antony and Cleopatra 3.4, where "keep it whole and break it across lines" could yield longer lines than v2's very short ones. The judge rewarded v2's short lines repeatedly; the fifteen-word guidance is kept.
- Macbeth 2.2 and Henry VI Part 1 4.5 are already near today's English; rebuilding sentences that did not need it could lose the closeness the judge credited.
- `valid` should not move; the 28-word ceiling is now explicit again.
