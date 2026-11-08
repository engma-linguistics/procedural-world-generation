# Polities round 6: keyed draws, and lane 180's nudge check again (PW-1459; lane 182)

## In plain words

- **What changed.** The tech tree used to take every random number from one shared stream, in loop order. Any small change
  anywhere (one wish weight) shifted every later number, so every people's tech dates were redrawn. Now each number is worked out
  from what it is for: a pair's contact front from (seed, giver, taker), an invention test from (seed, people, tech, step). The
  settlement ledger's draws (where in its cell a place sits, and "the river moved away") are keyed the same way, on slot, cell and
  year. Polities' fall and war draws used the run's random folder id, so every rebuild had new luck. They now use the run's seed and
  the seat's cell and founding year. The odds of every draw are unchanged; only which number a draw gets has changed.
- **The nudge check, again** (halflings among humans, wish weight 0.8 -> 0.9, seeds 7 and 10, world 899985 at L7). The tech tree
  holds now. On seed 7 every people but the humans keeps exactly the same dates. The humans, the nudged people, moved their
  kingship by 400-600 years. On seed 10, three more dates moved by 100-300 years (leonin and orc kingship, orc writing), likely by
  contact with the humans. Lane 180 saw shifts of 1-3 thousand years. The states hold better than in lane 180's check: now 5-8 of the 10 largest
  keep their people and capital (lane 180: 3-6), and 41-44% of ruled land keeps its ruling people (lane 180: 21-38%). A different
  seed keeps 0-2 of 10 and 3%. That is better, but it is not yet "the same map". About half of the ruled land still changes hands.
  One draft is filed for that remaining spread.
- **Still plausible.** The peoples history is bit-for-bit the same on old and new code, so the peoples' shares are identical.
  Only the tech-tree luck differs. On seed 10 the world looks like the old one (93 against 108 states 1,000 years ago; 4 against 3
  polities over 1 Mkm² now). On seed 7 the new luck is a rare draw in which the humans never learn writing. With 39% of all people
  unlettered, chiefdoms and states arrive late, and only 15 Mkm² is ruled now (old luck: 39 Mkm²). The same draw happens 1 time in 12
  on the old code too (the 12-seed sweep below). So it is the existing distribution, not something the fix broke.

## 1. What is keyed

| step | before | now |
|---|---|---|
| `techtree.build`, contact front per pair | `rng.exponential` from `default_rng((seed, 675))`, in loop order | `-log1p(-keyed(seed, "front", giver, taker))` |
| `techtree.build`, invention test | `rng.random()` from the same stream, drawn only when the hazard was > 0 | `keyed(seed, "invent", people, tech, step)` |
| `settlements`, a place's spot in its cell | 4 streams (one per slot), in founding order | `keyed(seed, "settle", "spot", slot, cell, year, j)` |
| `settlements`, "the river moved away" | the same slot streams | `keyed(seed, "settle", "river", slot, cell, year)` |
| `polities`, falls and wars | `crc32(run folder id, "s<ledger index>", step, what)` | `crc32("try<seed>", "c<cell>@<founded kyr>", step, what)` |

`techtree.keyed(seed, *key)` is blake2b (8 bytes) of the key, giving a uniform number in [0, 1) at 53 bits. Polities keep their
`crc32` `draw`. Only the key it hashes has changed.

**The odds are the same.** I ran `techtree.anchor_check` with 41 seeds of isolated anchor peoples:

| tech | old: median lag, share found | new | Earth's lag |
|---|---|---|---|
| writing | 2.84 kyr, 1.00 | 3.09 kyr, 0.98 | 3.3 |
| kingship | 0.82, 1.00 | 0.89, 1.00 | 0.8 |
| law | 1.47, 1.00 | 1.37, 1.00 | 1.2 |
| pottery | 44.0, 1.00 | 43.1, 1.00 | 40 |
| bronze | 0.55, 1.00 | 0.55, 1.00 | 0.45 |

I also rebuilt the tech tree of one stored history (the s7 base run) with 12 seeds (7000-7011) on each code:

| known from (years ago) | old: known in, median | new: known in, median |
|---|---|---|
| humans: writing | 11/12, 2,797 | 11/12, 2,698 |
| humans: law | 11/12, 1,574 | 11/12, 1,753 |
| hobgoblins: kingship | 12/12, 3,064 | 12/12, 3,728 |
| leonin: kingship | 12/12, 3,176 | 12/12, 3,408 |
| orcs: kingship | 12/12, 2,798 | 12/12, 3,597 |

The old code's seed 7000 gives lane 180's s7 base dates exactly (writing 3,865, law 1,691; hobgoblin kingship 1,413; leonin 576).
So the history under it is the one lane 180 ran. On the new code, seed 7000 is the 1-in-12 draw in which the humans never write.
Kingship medians sit 200-800 years earlier on the new code. That is within the spread of 12 draws: each column runs over 2-5 kyr.

**A test** (`tests/test_techtree.py::test_a_nudge_elsewhere_leaves_a_peoples_dates_alone`) changes one people's size and adds a
newcomer, then asks that an unrelated people's dates stay identical. The old code fails it on both seeds; the new code passes.

## 2. The nudge check, re-run

**Set-up, as in round 5 section 3.** World 899985 (time zoom fc5311, the inputs of b4d502), copied into a scratch data root, at L7.
The tree is dnd.toml with one try per run, tree seeds 7 and 10. The nudge is the halflings-among-humans wish, weight 0.8 -> 0.9.
Polities come from `polities.derive`. Every run used 4 threads, one at a time: 20-27 min each, 7.2-8.7 GB peak.

**Baselines.** "Base vs nudge" compares the same seed on the same code (new). The reference "not the same" is base seed 7 against
base seed 10. "Before" is lane 180's table (round 5, old code). The old-code arms (s7old, s10old) are the new runs' histories with
everything downstream of the history re-derived on the old code (`git archive` of 3d7b05bb): tech tree, land use, fuels, cultures,
settlements and polities. The history does not read the tech tree. A rebuild on the new code reproduced the stored tech tree
exactly, so this is the same as an old-code run.

**My measures**, which may differ in detail from lane 180's: "top 10 kept" counts the 10 largest states and empires of one run that
have a state or empire of the same ruling people (groups rolled up) within 300 km of their capital in the other run, read both
ways. "Same ruler" is the share of the cells ruled by a state, empire or dragon realm in either run that have the same ruling
people in both. "State land moved" is half the summed difference of each people's share of state land, in points.

| pair | top 10 kept, 1,000 ago | top 10 kept, now | same ruler, 1,000 ago / now | state land moved, 1,000 ago / now |
|---|---|---|---|---|
| **before (lane 180):** s7 base vs nudge | 6/10, 6/10 | 3/10, 5/10 | 16% / 21% | 50 / 31 pt |
| **before (lane 180):** s10 base vs nudge | 6/10, 5/10 | 6/10, 6/10 | 30% / 38% | 29 / 18 pt |
| **before (lane 180):** reference s7 vs s10 | 3/10, 3/10 | 4/10, 1/10 | 10% / 11% | 53 / 34 pt |
| **now:** s7 base vs nudge | none to keep (0 states either side) | 7/10, 8/10 | 13% / 41% | 0 / 8 pt |
| **now:** s10 base vs nudge | 5/10, 8/10 | 5/10, 6/10 | 36% / 44% | 13 / 9 pt |
| **now:** reference s7 vs s10 | none to keep | 2/10, 0/10 | 0% / 3% | 50 / 62 pt |
| old code, my measures: reference s7 vs s10 | 4/10, 3/10 | 5/10, 1/10 | 7% / 9% | 52 / 42 pt |

On s7, 1,000 years ago, both runs have dragon realms only (the humans-never-write draw), so "same ruler" there compares dragon
realms. **How much is the polities key?** The new runs with the old polities (random run id, ledger index) give s7 now 6/10, 5/10
and 33%; s10 1,000 ago 3/10, 3/10 and 28%, now 5/10, 4/10 and 34%. So about half of the gain is the tech tree and half is
polities' luck.

**Tech dates (years ago), base -> nudge, new code:**

| | s7 | s10 |
|---|---|---|
| humans: writing | never -> never | 2,698 -> 2,797 |
| humans: law | never -> never | 1,518 -> 1,518 |
| humans: kingship | 1,315 -> 1,884 | 1,817 -> 2,255 |
| hobgoblins: kingship | 2,603 -> 2,603 | 1,753 -> 1,753 |
| leonin: kingship | 2,098 -> 2,098 | 1,363 -> 1,518 |
| orcs: kingship | 2,255 -> 2,255 | 2,337 -> 2,024 |
| hobgoblins, leonin, orcs: writing | the same | the same, but orcs 2,698 -> 2,603 |

Lane 180's shifts were 1-2 kyr, and "never" against 3,865. Now the dates that move belong to the humans (whose numbers the nudge
changes) or to peoples that took a tech up from them. That is a real effect of the nudge, not noise.

**What still moves.** The tech dates are now stable, but 56-59% of ruled land still changes its ruling people under a +12.5%
wish. The peoples themselves move (humans 39.0 -> 43.1% on s7, halflings 11.1 -> 8.4%), so towns found in other cells and seats rank
in another order. I have not split that further. A draft is filed:
`issue-tracking/inbox/draft-nudge-states-still-half-move.md`.

## 3. Old code against new code, base arm (is the world still plausible?)

The baseline is the same history (same seed, same run) with the old code's tech tree, settlements and polities.

| run | peoples (share of all people, top 5) | states and empires, 1,000 ago / now | over 1 Mkm², 1,000 ago / now | largest now | ruled now | most state land now (Mkm²) |
|---|---|---|---|---|---|---|
| s7 old | humans 39.0, hobgoblins 11.9, halflings 11.1, orcs 8.9, kenku 7.1 | 108 / 134 | 1 / 2 | 2.29 Mkm² | 39.3 Mkm² | humans 10.9, hobgoblins 4.3, leonin 3.0 |
| s7 new | the same (bit-identical history) | 0 / 58 | 0 / 0 | 0.82 | 15.0 | hobgoblins 4.0, orcs 1.9, tabaxi 0.7 |
| s10 old | humans 29.8, hobgoblins 20.8, leonin 16.8, elves 7.9, kenku 6.8 | 108 / 148 | 0 / 3 | 3.49 | 41.8 | hobgoblins 8.7, elves 4.6, leonin 3.6 |
| s10 new | the same | 93 / 153 | 1 / 4 | 1.58 | 40.9 | elves 6.2, hobgoblins 5.1, humans 4.8 |

s10 is the same kind of world. s7 is the rare unlettered-humans draw (section 1: 1 in 12 on either code), and it is thin: the
largest people has no states, and the first states arrive within the last 1,000 years. That is how the tech tree's odds already
were. Whether "the most numerous people never writes in 12 kyr" should happen 1 time in 12 is a question for the tech tree's
calibration, not for this ticket.

## 4. Other shared streams (checked, not changed)

- `history/animals.py`: one stream per stock (`(seed, 691, bit)`), drawn conditionally each step. A nudge that changes who lives
  near a wild herd shifts that stock's later draws (when and where a taming happens). It feeds the tech tree's forced tamings. It
  is per stock, so the reach is small.
- `crossing.py` (sea crossings) is passed one generator by its caller and draws conditionally in step order: the same pattern,
  inside the history.
- `history/hunts.py` has one stream for all hunts (`(seed, 1206)`).
- `gods.py` has one stream per run (`(seed, 1358)`). It reads out gods, not states.
- `History.rng` (`default_rng(seed)`, model.py) is defined, and no use of it turned up.
- Settlements' `tieb` and the mining lags are whole arrays drawn once at a fixed size: not order-dependent.

The peoples moved by under 4.2 points under the nudge in lane 180's check and in this one. The in-history streams are not what
moves the states, so I left them alone.

## Files

- `planet/lineages/techtree.py`: `keyed`; build's two draws.
- `planet/lineages/settlements.py`: the spot and river draws keyed.
- `planet/lineages/polities.py`: the fall and war luck on the run's seed and the seat's place.
- `tests/test_techtree.py`: the nudge test.
- `issue-tracking/inbox/draft-nudge-states-still-half-move.md`.
- Goldens: none moved (`tests/test_golden.py` covers the sim and climate, not peoples).
