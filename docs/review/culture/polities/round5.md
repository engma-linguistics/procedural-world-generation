# Polities round 5: the seam, the village experiment, the nudge check (PW-1280, PW-1281, v3 done-when 4; lane 180)

## In plain words

- **The seam (PW-1280).** The history has no states yet. Three stand-ins tell its brakes how states and wars act: how far a state
  keeps its people's violence down, how much hostile country lies around each cell, and how hemmed in a people is when it quarrels.
  All three now live in one small file, `planet/lineages/history/rule.py`, and the brakes read them only through it. In v4,
  polities can replace them (PW-1434) by putting a different class in that one place. Nothing else in the history changes. No
  number moved: the runs before and after are bit for bit the same.
- **The village experiment (PW-1281): closed, not run.** It asked whether we could stop tracking every village, to save cost.
  The cost is small: the settlement ledger takes 25 seconds of a 25-minute L7 run and 47 MB on disk. Polities also need the villages
  now. About four in five settled people live in them, and they supply the confederations' people and most of a state's war strength.
- **The nudge check (v3 done-when 4):** **it fails, and the cause is the technology tree.** I changed one wish (halflings among humans, weight 0.8 -> 0.9) and
  re-ran. The peoples came out recognisably the same: shares moved by under 4.2 points, which is within lane 176's one-try chance.
  The states did not. Only about half of the 10 largest states kept their people and capital. Under a third of the ruled land kept
  its ruling people. The reason is that the tech tree redrew its dates: in one pair the humans never learned writing, and polities
  wait for writing, kingship and law. The tech tree takes all its random draws from one shared stream, so any small change reshuffles
  every date. One draft is filed. I did no tuning.

## 1. The seam

**What the stand-ins are** (before this lane, all inline in `history/counter.py`):

| stand-in | what it answers | today's rule | read by |
|---|---|---|---|
| pacification G | how much of a people's own violence a state leaves | 1 / (1 + STATE_Q x tech level x farm share) | war-torn land |
| hostile frontier F, and the hostility matrix behind it | how much of the country around a cell is held by peoples who hate this one | the tree's old enmities (the cohabitation matrix) over the presences at the step's start | war-torn land, raid losses, culling wars |
| circumscription C | how far the land next to a people bars a faction from splitting off | Carneiro's grading: free good land 0, others' land SOCIAL_Q, unlivable land 1; refreshed after each contest | in-fighting (FEUD_CUT x C x fill) |

**The interface** (`planet/lineages/history/rule.py::StandIns`, one per History at `h.rule`):
- `pacification(k, step)` returns G;
- `frontier(k)` returns F per cell, and `hostility` is the matrix;
- `circumscription(k)` returns C;
- two notes from the history, `note_habitat(k, K)` and `after_contest(l, k, K, room, crowd)`.

The brakes' own formulas stay in counter.py: LAND_Q, H_WAY and the violent-death rates, FEUD_CUT x C x fill, the raid and cull rules.
They say what a state or a war does to a people's numbers, whoever supplies G, F and C. To swap, set `CounterMixin.Rule` (or
`History.Rule`) to a subclass. A test does exactly that: a "peace" rule takes away the frontier-war, raid and in-fighting cuts, and
nothing else changes (`tests/test_lineages.py::test_polities_swap_the_state_and_war_stand_ins_through_one_seam`).

**Not moved, on purpose:** the people's own fill of its land (in-fighting's u) is a people's own numbers, not a state proxy. The
dials `meta.war` and `meta.raiders` stay in counter. Polities v0 (`planet/lineages/polities.py`) has its own `_hemmed`. It reads the
run after the fact, so it does not share the history's object.

**Bit-identical proof.** I used `tools/peoples_robust.py`'s `run_one` on the base variants dnd-s7@4360a3 and seven_meals-s7@af2677
(the lane 176 method). The probe also hashed the history's full state at the end: every line's presence `h.p`, the brakes' `lost`
shares, every event and the present summary's arrays. The old code came from `git archive HEAD` at e6813f6f. Both sides ran with
2 threads and the same scratch copy of the worlds.

| run | state sha256, before | after | run_one numbers |
|---|---|---|---|
| dnd-s7@4360a3 | 1ce8426a...3d60d6 (1,464 events) | the same | identical (only `runtime_s` differs) |
| sm-s7@af2677 | a9c72d14...42e2758b8 (639 events) | the same | identical (only `runtime_s` differs) |

## 2. The village experiment (PW-1281): closed

The ticket's three arms were: A, villages tracked throughout; B, villages only in the last 200 years; C, B plus villages made on
demand from town data. The worry behind it was that tracking every village on the 100-year step is too granular. It is not worth
running now, for two reasons:

1. **Cost.** The ledger is cheap.

   | run | ledger build | whole run | settlements.json |
   |---|---|---|---|
   | 3c1caf (Seven Meals, L7) | 25.1 s | 1,534 s | 47 MB |
   | a2b637 (D&D, L7) | 21.3 s | 1,117 s | 32 MB |

   (Read from `meta.settlements.generated_in_s` and `meta.generated_in_s`.)
2. **Polities need the villages, every century.** On 3c1caf, from the ledger's own series and town thresholds (read-only):

   | years ago | villages | their people | share of settled people | towns and cities |
   |---|---|---|---|---|
   | 5,000 | 12,971 | 6.2 M | 68% | 1,484 (2.8 M) |
   | 3,000 | 20,523 | 14.6 M | 78% | 1,144 (4.0 M) |
   | 1,000 | 40,116 | 30.3 M | 82% | 1,963 (6.9 M) |
   | the present | 47,766 | 39.8 M | 82% | 2,388 (8.7 M) |

   Polities v0 reads this. A polity's strength in war is its settled people, villages included. A confederation is a people's villages
   and camps banded together: 6 of the 8 polities over 1 Mkm² at the present on 3c1caf are confederations (round 4), and so is the
   antelope-kin empire. Under arm B, every confederation and most of every state's strength would vanish before 200 years ago, and
   v4 (polities inside the history) would have nothing to work with. Arm C would have to regenerate the same numbers it threw away.

So the answer for v4 is "keep tracking villages". There is no sharper question to ask, and I filed no draft.

## 3. The nudge check (v3 done-when 4)

**Set-up.** World 899985 (time zoom fc5311, the inputs of b4d502), copied into a scratch data root, at L7. The tree is dnd.toml
with one try per run. The nudge is the halfling-among-human wish, weight 0.8 -> 0.9 (+12.5%). There are two tries per arm, tree
seeds 7 and 10. Polities come from `polities.derive` on each run. **The baseline for every comparison is the base arm at the same
seed, on today's code.** As a reference for "not the same", I also compare base seed 7 with base seed 10: same world, a different
seed. Seed 7 ran two at a time on 2 threads each; seed 10 ran one at a time on 4 threads. Each pair shares one setting.

**The peoples (share of all people at the present):**

| | humans | hobgoblins | halflings | orcs | leonin | largest move of any top-8 people |
|---|---|---|---|---|---|---|
| s7 base -> nudge | 38.3 -> 42.5% | 11.6 -> 12.6 | 10.9 -> 8.2 | 8.7 -> 8.9 | 6.5 -> 6.7 | 4.2 pt |
| s10 base -> nudge | 29.3 -> 27.5 | 20.5 -> 20.0 | 4.2 -> 6.0 | 5.5 -> 5.5 | 16.6 -> 16.3 | 1.8 pt |

**The polities:**

| run | states and empires, 1,000 years ago / now | over 1 Mkm², 1,000 ago / now | largest, 1,000 ago / now (Mkm²) | most state land now |
|---|---|---|---|---|
| s7 base | 108 / 137 | 0 / 4 | 0.47 / 1.56 | humans 9.9 Mkm², hobgoblins 5.1 |
| s7 nudge | 47 / 109 | 1 / 1 | 1.65 / 2.19 | leonin 3.4, hobgoblins 2.5, humans 1.9 |
| s10 base | 100 / 158 | 0 / 1 | 0.44 / 2.16 | hobgoblins 8.1, elves 4.6, humans 4.5 |
| s10 nudge | 92 / 161 | 1 / 4 | 1.01 / 1.59 | humans 6.5, hobgoblins 6.3, leonin 4.7 |

**Same or not.** "Top 10 kept" counts the 10 largest states of the first run that have a state of the same ruling people within
300 km of their capital in the second run, read both ways. "Same ruler" is the share of ruled cells (states, empires, dragon realms)
with the same ruling people in both runs. "State land moved" is the share of state land that changed people.

| pair | top 10 kept, 1,000 ago | top 10 kept, now | same ruler, 1,000 ago / now | state land moved, 1,000 ago / now |
|---|---|---|---|---|
| s7 base vs nudge | 6/10, 6/10 | 3/10, 5/10 | 16% / 21% | 50 / 31 pt |
| s10 base vs nudge | 6/10, 5/10 | 6/10, 6/10 | 30% / 38% | 29 / 18 pt |
| reference: s7 base vs s10 base | 3/10, 3/10 | 4/10, 1/10 | 10% / 11% | 53 / 34 pt |

So the nudged map sits between "the same world" and "a different seed". On seed 7 it is nearly as different as a new seed: at
1,000 years ago the states fall from 108 to 47, and the human states go from the largest bloc (3.6 Mkm²) to almost none.

**Why: the technology tree.** The peoples barely move, but the dates the tech tree hands out move by thousands of years:

| known from (years ago) | s7 base | s7 nudge | s10 base | s10 nudge |
|---|---|---|---|---|
| humans: writing | 3,865 | never | 1,315 | 4,006 |
| humans: law | 1,691 | never | 740 | 1,953 |
| hobgoblins: kingship | 1,413 | 3,865 | 4,462 | 2,423 |
| leonin: kingship | 576 | 3,229 | 2,337 | 2,098 |

Polities v0 gates chiefdoms on writing and states on kingship or law, so the states follow these dates.
`planet/lineages/techtree.py::build` takes every draw from one generator, `default_rng((seed, 675))`: each pair's contact front and
each invention test, in loop order. A small change in who meets whom shifts every later draw. That is a strong suspicion, not a
proof: a fix and a re-run would show it. Draft: `issue-tracking/inbox/draft-techtree-keyed-draws.md` (key each draw on what it is
for, as `polities.draw` already does).

**What "recognisably the same" turned out to mean.** For the peoples it holds: the same peoples lead, and shares move by a few
points. For the states it should mean that most of the largest states keep their people and capital, within the spread a second
try shows. Today about half do. A different seed keeps 1-4 in 10, so the nudge does keep some structure, but nothing like "the
same". It fails on both tries, so this is not the dwarves' one-try bistability lane 176 found. Don't tune polities for it. The
tech-tree draws come first, then re-run this check.

**Cost.** Each L7 run took 20-33 minutes, with 7-8.7 GB peak memory. Running two at once on seed 7 peaked near 17 GB, over this
lane's 12 GB budget. Seed 10 then ran one at a time. The scratch runs were deleted at the end.

## Files

- `planet/lineages/history/rule.py` (new): `StandIns`, the seam.
- `planet/lineages/history/counter.py`: the brakes read G, F, C and the hostility matrix through `self.rule`; `CounterMixin.Rule`.
- `tests/test_lineages.py`: the brake tests read through `h.rule`; a new test swaps in a peace rule.
- `issue-tracking/inbox/draft-techtree-keyed-draws.md`.
