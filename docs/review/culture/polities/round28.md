# Polities round 28: dragon realms per culture measured on the five pairs; one more mirror pass; not flipped (PW-1687 B, PW-1596; lane 281e)

Lane 281e follows round 27 section 4: run the five switch-on pairs on fdae6ce9, measure live dragon realms against the read-out on
the same history; if any pair is still under, one more pass mirroring the demes' split by distance and the cultures engine's merge
order (no new number), then measure again; flip `POLITIES_LIVE` only if dragon realms are within ~25 % of the read-out on all five
pairs and the states gap is no wider than round 26's (worst -14 % at a single five-step date).

**Result: one more pass done (f11aeeac). Dragon realms are within 25 % on 13 of 15 five-step dates, but three dates miss (L6 seed 10
at 1,000 ya -28 %, L7 seed 7 at 1,000 ya -29 % and now -28 %). The brief says stop after that pass: not flipped.**
`POLITIES_LIVE` stays False; the test asserting it is off is unchanged; goldens untouched.

All runs: dnd, 30 kyr, languages skipped, `round27/live_run_dc.py` (round19/live_run.py logging the live dragon cultures), switch on,
scratch root /data/personal/scratch/lane281d/root (worlds 4360a3 and 899985, runs ea33de, a19366, cdc275 and fc5311 all copied, no
links), each run pinned to 4 cores. Measures: `round26/measure.py`. avg5 = mean of the five steps around 2,000 / 1,000 / 0 years
ago. RO-on = the read-out on the switch-on run's own history (derive with the live map hidden). Off = round 26's off runs, which
stand: the off path does not import polity_live, and round 27 checked off L6 s7 on fd234c2c (fea1cb) equal to b84d29.

## 1. fdae6ce9 (round 27's last revision), the three L6 pairs

| pair | run | dragons live avg5 | dragons RO-on avg5 | live vs RO-on | states avg5 |
|---|---|---|---|---|---|
| L6 4360a3 s7 | 14d701 | 17.0 / 19.8 / 20.8 | 21.2 / 23.2 / 22.8 | -20 / -15 / -9 % | 55.4 / 164.4 / 218.8 |
| L6 4360a3 s3 | dc479d | 18.2 / 19.0 / 22.2 | 16.8 / 19.8 / 22.4 | +8 / -4 / -1 % | 169.8 / 209.2 / 240.4 |
| L6 4360a3 s10 | 6bf882 | 11.8 / 13.0 / 12.8 | 20.6 / 24.0 / 21.4 | -43 / -46 / -40 % | 117.6 / 150.4 / 205.2 |

fdae6ce9 fixed L6 s7 (round 27 on 0a519fc8: -26 / -18 / -3 %) but not L6 s10 (round 27: -45 / -51 / -41 %). The L7 pairs were not
run on it: s10 needed the next pass anyway.

## 2. The pass (commit f11aeeac, planet/lineages/history/polity_live.py, DragonCultures)

A replay of the live rule on a finished run's stored frames (`round28/replay.py`: the same presence the history cut, offline, a few
minutes) reproduced the live count (6bf882 now: 25 live cultures against 26 logged in the run) and showed where it parted from the
read-out's 45. Per people on 6bf882 (`replay.py dump`): blue dragons 3 live cultures against 10; the read-out's ten are 1 founding,
2 split by distance and 7 split by a gap; the live rule saw the early gap splits and sent most of them back, and never saw the
late ones (18.5, 12.5, 11.5, 6.5 kyr ago) at all. Three changes, each the demes' or the cultures engine's own rule:

1. **A piece that goes back is its label's again** (a bug in the mirror). The cells of a piece that rejoined kept the piece's label
   (resolved to its source only through `into`), so the source and the returned piece were two labels; a later gap between them
   was a label in one region each, never a split. The demes have one deme there, and see the next gap. Now the piece's cells take
   the source label back, and a later gap splits it anew.
2. **When a piece goes back: the demes' `multi`.** It goes back when the source label with the piece is no longer in two parts of
   MIN_KM2 (demes.Demes._cut: a deme apart until its land is in fewer than two big pieces), not when the two share any region
   (a stray patch of the source near the piece sent it back before).
3. **The split by distance** (demes.Demes._diameters and _halve): each label's cells and the gaps a dragon crosses (the reach cells
   of its piece, each taking the nearest label, demes.grow), two sweeps at a dragon's cost of 1 a km; wider than demes.SPLIT_KM x
   LINK_KM / JUMP_KM (13,125 km) halves from the two ends; the half whose cells were settled earlier on average keeps the label, the
   other is a new piece of its culture (a culture after t_apart; it does not go back); up to demes.SPLIT_ITER rounds a frame.
4. **Merge order** (cultures.Cultures._contacts): contacts are tried smallest pair first (the two cultures' cells), a culture
   merging at most once a frame (was: label order).

No new number. Still not mirrored: the demes' fusion (FUSE_KM) and niche learning (split_adapted; no dragon culture is adapted on
these runs). Replay, live cultures against the read-out's at 2,000 / 1,000 / 0 ya: 6bf882 37 / 34 / 33 against 48 / 46 / 45 (was 25
now); 14d701 42 / 42 / 42 against 44 / 43 / 43; dc479d 44 / 43 / 43 against 39 / 38 / 39. Tests: the two dragon tests pass
unchanged.

## 3. The five pairs on f11aeeac (switch on)

| pair | run | first state (RO-on) | writing | states avg5 | vs off avg5 | confeds avg5 (RO-on) | dragons avg5 | dragons RO-on avg5 | live vs RO-on |
|---|---|---|---|---|---|---|---|---|---|
| L6 4360a3 s7 | 91c10c | 2,600 (2,600) | 3,231 | 56.2 / 164.4 / 218.6 | -1 / -14 / -7 % | 4.4 / 11.4 / 17.4 (5.8 / 15.4 / 19.8) | 17.2 / 22.0 / 22.6 | 22.4 / 24.0 / 21.4 | -23 / -8 / +6 % |
| L6 4360a3 s3 | 8e517f | 7,100 (7,100) | 6,278 | 174.0 / 207.8 / 240.8 | -0 / -2 / -3 % | 18.0 / 18.8 / 20.0 (15.2 / 14.6 / 20.8) | 18.4 / 20.0 / 24.0 | 18.6 / 18.4 / 23.6 | -1 / +9 / +2 % |
| L6 4360a3 s10 | 1a7fae | 5,300 (5,300) | 4,882 | 114.4 / 152.2 / 202.0 | -5 / -11 / -11 % | 12.8 / 10.8 / 14.6 (16.8 / 13.6 / 14.0) | 15.0 / 17.0 / 19.0 | 18.2 / 23.6 / 21.6 | -18 / **-28** / -12 % |
| L7 899985 s7 | a1c6ed | 5,100 (5,100) | 5,438 | 93.0 / 170.0 / 216.6 | -3 / -8 / -7 % | 5.8 / 12.4 / 16.6 (4.8 / 13.0 / 16.6) | 17.2 / 15.8 / 11.6 | 21.0 / 22.2 / 16.2 | -18 / **-29** / **-28** % |
| L7 899985 s10 | a80cfe | 5,500 (5,700) | 4,970 | 143.4 / 180.6 / 237.8 | -5 / -12 / -9 % | 9.6 / 13.2 / 19.4 (10.4 / 18.8 / 20.0) | 20.6 / 18.4 / 17.0 | 25.6 / 21.0 / 18.8 | -20 / -12 / -10 % |

Single steps at 2,000 / 1,000 / 0 ya, live (RO-on): states L6 s7 57 / 138 / 236 (65 / 156 / 227), s3 195 / 221 / 270 (183 / 189 / 231),
s10 106 / 144 / 200 (107 / 164 / 195), L7 s7 78 / 151 / 213 (94 / 172 / 224), L7 s10 147 / 154 / 236 (138 / 182 / 259); dragon
realms L6 s7 18 / 21 / 26 (22 / 22 / 18), s3 20 / 19 / 24 (19 / 16 / 24), s10 14 / 15 / 20 (19 / 23 / 20), L7 s7 17 / 18 / 13
(22 / 21 / 18), L7 s10 20 / 20 / 21 (23 / 20 / 20).

Off baselines (round 26, states avg5; first state / writing): L6 s7 b84d29 56.8 / 191.0 / 236.2 (2,600 / 3,288); L6 s3 073429
174.6 / 212.6 / 247.4 (7,100 / 6,278); L6 s10 e4a8a9 120.8 / 171.2 / 227.6 (5,500 / 4,882); L7 s7 599ac3 96.2 / 184.2 / 232.8
(5,100 / 5,438); L7 s10 e0f453 150.8 / 205.2 / 260.4 (5,100 / 4,970). Round 26's on runs (one realm per dragon people, 06187f53):
dragons avg5 4.0-6.0 on every pair; states vs off worst -13 % (L6 s7 1,000 ya), -12 % (L6 s10 now, L7 s10 now).

L7 s7 per people (`round27/per_people.py` on a1c6ed): live realms 18 / 13 at 1,000 / 0 ya against the read-out's 21 / 18; the replay
gives 34 / 33 live cultures there against the read-out's 41 / 40 (-17 %), so on this pair about half the gap is fewer cultures and
half is fewer of them seating a realm (a realm needs settled peoples within DRAGON_KM of the culture's core).

**Same seed twice** (L6 4360a3 seed 7, f11aeeac): 91c10c and 22afa5 are identical: every layer byte for byte; cultures.json,
demes.json and settlements.json equal; polities_live.json, gods.json, taboos.json and run.json differ only in timings (`made_s`,
`tech_s`, `generated_in_s`) and the run's id, name and date (`round28/same_seed.py` and a leaf-by-leaf compare). Deterministic.

## 4. What the numbers say (plain words)

- **Dragon realms: from a quarter of the read-out's to most of it.** Round 26 seated 4-6 dragon realms where the read-out seats
  16-26. Now the history follows each dragon kind's cultures as the cultures engine does, and seats 12-26: within a fifth of the
  read-out on most dates, a few over on L6 seed 3. Three dates are still about 28 % short: L6 seed 10 at 1,000 years ago (17 against
  24) and L7 seed 7 at 1,000 years ago and now (16 against 22, 12 against 16). On L7 seed 7 about half of that is the history
  finding fewer dragon cultures than the cultures engine (34 against 41), half fewer of them sitting near settled land.
- **States: unchanged in kind.** Live states against off, five-step averages: 0-5 % under at 2,000 ya, 2-14 % under at 1,000 ya,
  3-11 % under now. The worst date is L6 seed 7 at 1,000 ya, -13.9 % (round 26: -12.7 % there, its worst). Against round 26 some
  dates are a little worse (L6 seed 10 at 1,000 ya -11 % against -8 %, L7 seed 10 at 1,000 ya -12 % against -10 %) and some better
  (L7 seed 10 now -9 % against -12 %): the dragon realms now take their share of settled land, as in the read-out. Within the
  brief's "not past -14 %", just.
- **First state and writing: as round 26.** First states on the same date as the read-out on the same history on four pairs; L7
  seed 10 two centuries earlier than that read-out (5,500 against 5,700; off 5,100: the switch-on history differs there, round 26).
  Writing is the off date on four pairs and 57 years earlier on L6 seed 7 (3,231 against 3,288), within one tree step.
- **Confederations:** within a few of the read-out on the same history on most dates; L7 seed 10 at 1,000 ya 13.2 against 18.8.

## 5. The flip: NOT flipped

The bar: dragon realms within ~25 % of the read-out on all five pairs (five-step averages), states gap no wider than round 26's.
States pass (worst -13.9 %). Dragon realms miss on three dates (-28 %, -29 %, -28 %) after the one extra pass the brief allowed, so
this lane stops. Whether ~28 % on three of fifteen dates is close enough is a call for the coordinator (draft
`draft-live-dragon-realms-three-dates-short.md`); if it is, the flip is one commit: `POLITIES_LIVE = True` in
planet/lineages/history/params.py, tests/test_lineages.py's `assert HP.POLITIES_LIVE is False` (in
test_polities_in_the_history_seat_claim_and_conquer_with_the_winners_tolerance) turned or dropped, the tests and goldens re-run.

Tests on f11aeeac pass (section 6).

## 6. Tests, scratch

On f11aeeac: `uv run pytest -m "not slow" -n 2` 2034 passed, 15 skipped; tests/test_lineages.py, test_lineages_split.py,
test_polities.py, test_settlements.py, test_settlements_bands.py, test_settlements_war.py and test_techtree.py incl. slow: 248
passed. Goldens not touched (the switch is off, and the off path does not import polity_live).

Scratch: /data/personal/scratch/lane281d (round 27's and this lane's) deleted at the end after unlinking symlinks (there were none).
The runs above are gone with it; their numbers are this file. Slip: the L7 seed 7 run was launched at load 57 (the wait loop had
been skipped once); every other launch waited for load under 30.

Scripts: `round28/replay.py` (the live dragon cultures replayed on a run's stored frames against the read-out's; `dump` lists one
people's labels), `round28/same_seed.py` (two runs compared without timings and ids).
