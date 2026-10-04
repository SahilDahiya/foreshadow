# What each number means

Every rendering is compared, blind, with a frozen reference: the rendering the baseline
prompt produced for that passage before any changes. The judge is Claude Sonnet 5.5; the
writer is Claude Opus 5.5.

| Metric | Meaning |
|---|---|
| **Win vs ref** (headline) | 1 = the judge prefers this rendering to the reference, 0 = prefers the reference, 0.5 = tie or both bad. The baseline scores about 0.5 by construction. |
| Preference | The same verdict weighted by how strong the judge said it was (slight, clear, strong). 0.5 is neutral. |
| Checks pass | Code checks: every original block answered once and in order, speeches stay speeches, no phones or screens, no line over 28 words. A rendering out of step with the original loses outright. |
| Faithful | Nothing dropped, softened, added or reassigned. A guardrail: it must not fall. |
| Speakable | Each line can be read aloud at first sight in one breath. |
| Natural | Sounds like a person today; no leftover archaic syntax, no slang. |
| Alive | Keeps the heat and the images that still land; not a flat paraphrase. |
| Voice | Speakers sound different where the original makes them different; status is audible. |
| Both bad | Share of passages where the judge said neither rendering should go on stage. |

The owner's own votes in the preference lab are not used here, by the owner's choice.
