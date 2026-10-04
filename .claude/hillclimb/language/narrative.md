# Language transformation hill-climb

| round | change (one line) | test pref | train pref | Δ test vs baseline | faithful (test) | natural (test) | speakable (test) | checks (test) | s/run | $/run | spend |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | baseline (seed prompt) | 0.504 | 0.521 | | 0.44 | 0.56 | 0.53 | 100% | 5.3 | $1.81 | $2.46 |
| 1 | stay as close as a translator would (reverted) | 0.492 | 0.483 | −0.012 ± 0.096 | 0.90 | 0.09 | 0.36 | 100% | 7.0 | $2.41 | $4.87 |
| 2 | what is said is fixed, how it is said is new (**kept, best**) | **0.629** | 0.592 | **+0.125 ± 0.097** | 0.96 | 0.38 | 0.65 | 95% | 8.4 | $2.58 | $7.45 |
| 3 | translate by the whole sentence (reverted) | 0.596 | 0.579 | +0.092 ± 0.091 | 0.94 | 0.29 | 0.60 | 97.5% | 7.1 | $2.39 | $9.84 |

Best so far: round 2 (test 0.629). Round 3 against round 2 on test: −0.033 ± 0.073, inside the noise.

Round 1 showed the prompt could buy faithfulness, but only by leaving the original's wording standing.
Round 2 separated content from wording and kept the faithfulness while making the lines more speakable
and alive; it is the one change that cleared the noise floor on the held-out passages. Round 3 tried
to win back naturalness by rebuilding whole sentences; it changed nothing measurable, and in one run
it broke the line rule badly, so it is reverted. Naturalness has now resisted two rounds: the judge
keeps calling the looser reference more natural even when it also marks it as less faithful, which
suggests part of that criterion is the price of faithfulness rather than something a prompt can fix.
The remaining gains are estimated at about the size of the noise, so the eval at 20 held-out passages
and two repeats can no longer tell a good change from a neutral one.
