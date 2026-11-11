# Polities round 27: dragon realms per dragon culture inside the history (PW-1687 B; lane 281d) — HAND-OFF STATE

Lane 281d, coordinator ruling B on PW-1687: a dragon people seats one realm per region of its range, the regions cut the way the
cultures engine cuts a people, cheaply inside the history; bar: live dragon realms within ~25 % of the read-out on the same history
(five-step averages) on the five pairs, then the flip (PW-1596). **Status at hand-off (~115 tool calls): the rule is in place and
committed, measured on three L6 pairs one revision back; the last revision (fdae6ce9) is not yet measured; not flipped.**

All runs: dnd, 30 kyr, languages skipped, `round19/live_run.py` (or `round27/live_run_dc.py`, the same run with the live dragon
cultures logged per frame), scratch root /data/personal/scratch/lane281d/root (worlds 4360a3, 899985 and runs ea33de, a19366,
cdc275, fc5311 all **copied**, no links). Measures: `round26/measure.py`; avg5 = mean of the five steps around 2,000 / 1,000 / 0 ya.
RO-on = the read-out on the switch-on run's own history.

## 1. How the cultures engine cuts a dragon kind (what the rule mirrors)

- demes.py cuts each people's stored frames: a dragon kind is megafauna, so its reach is megafauna.LINK_KM (1,500 km) over land and
  sea alike (gaps up to that wide do not cut it); a piece reached by no labelled cell is a new deme ("crossing") if at least
  demes.MIN_KM2 (125,000 km2, 10 cells at L6), else the nearest deme's; a deme whose land falls into pieces of MIN_KM2 that stay
  apart demes.PERSIST (4) frames splits ("split_gap", dated when the gap opened); a deme wider than SPLIT_KM x LINK_KM / JUMP_KM
  (13,125 km) halves. Frames from demes.WINDOW_KYR (300 kyr) ago.
- cultures.py: a people's first demes are one founding culture; a later deme is a culture of its own if it lives
  cultures.t_apart (0.6 kyr in the stone age); two cultures of a people on neighbouring cells merge, the younger into the older,
  after MERGE_CONTACT_KYR x (1 - cohesion) side by side (dragons 0.9: one frame).
- On L6 4360a3 seed 7 (run d59fa2) the read-out's 43 dragon cultures alive now began as 25 split_gap, 10 first (founding), 5
  crossing and 3 split_distance demes; 15 of them date from the window's first frames (~300 kyr). The read-out seats a realm on
  about half of them (the rest have no settled people within DRAGON_KM of their core).

## 2. The rule (planet/lineages/history/polity_live.py: dragon_regions, DragonCultures, LivePolities._dragon_cultures)

On each frame the history stores from WINDOW_KYR ago (end_step, glacial and recent passes), per dragon people: regions = its held
cells joined within LINK_KM (dilate LINK_KM / 2 each side), a region under MIN_KM2 to the nearest; each held cell keeps a label,
new cells take the nearest label of their region; the first range is one founding culture (other regions its first demes); a
region with no label is a crossing piece of the nearest culture, its own culture after t_apart; a label's part in another region
(MIN_KM2 or more) is a split piece, back to the label it split from if it shares a region with it within PERSIST frames, else its
own culture after PERSIST frames and t_apart; cultures on neighbouring cells merge after MERGE_CONTACT_KYR x (1 - cohesion) (the
tree's cohesion, cultures.cohesion). The live polities seat one dragon realm per culture (key `d<people>` for the founding one,
`d<people>.<n>` after; stable from step to step), at polities._core of its cells, reading the last frame's cultures as the
read-out reads the latest frame at or before each step. **No new number**: LINK_KM, MIN_KM2, PERSIST, WINDOW_KYR, t_apart,
MERGE_CONTACT_KYR and cohesion are the engines' own. Not mirrored: the split by distance (3 of 43 cultures on d59fa2) and niche
learning (split_adapted). Tests: `test_dragon_cultures_cut_a_range_as_the_demes_and_cultures_cut_a_dragon_kind`,
`test_live_dragon_people_seats_a_realm_per_culture` (tests/test_lineages.py; replace lane 281c's one-per-people test).

## 3. Measured, revision by revision (dragon realms avg5 live / RO-on; states avg5)

Baseline check: main d6d44153 (lane 281c's one realm per people) re-run on L6 s7, run **34d321**: every number equals round 26's
242ac7 (dragons 5.2 / 5.2 / 5.4 against RO-on 21.8 / 22.4 / 22.8). **Off path:** this lane touches only polity_live.py (not
imported with the switch off) and tests; planet/ changes since round 26's off commit c489e2ca are export, humanuse and zoom
only. Off L6 s7 re-run on fd234c2c (run **fea1cb**) equals round 26's b84d29 in every number, so round 26's off
runs stand.

| commit | rule | pair | run | dragons live | dragons RO-on | states live | states RO-on |
|---|---|---|---|---|---|---|---|
| fd234c2c | one per region (LINK_KM join, MIN_KM2), every step | L6 s7 | 064056 | 42.4 / 50.0 / 44.2 | 20.6 / 24.0 / 20.8 | 55.6 / 158.8 / 215.6 | 62.0 / 177.0 / 236.6 |
| c3e287a2 | per culture, cut every step | L6 s7 | 9fd701 | 15.8 / 16.6 / 15.4 | 22.0 / 24.4 / 23.4 | 55.8 / 163.2 / 221.4 | 60.8 / 178.0 / 235.6 |
| 0a519fc8 | per culture, cut on stored frames | L6 s7 | d59fa2 | 16.8 / 19.6 / 21.2 (-26 / -18 / -3 %) | 22.6 / 23.8 / 21.8 | 56.0 / 164.0 / 219.8 | 61.0 / 180.6 / 240.8 |
| 0a519fc8 | same | L6 s3 | 9d1c76 | 17.2 / 18.0 / 17.8 (+2 / -5 / -14 %) | 16.8 / 19.0 / 20.6 | 170.4 / 211.4 / 237.4 | 168.4 / 210.0 / 238.4 |
| 0a519fc8 | same | L6 s10 | 3806da | 10.8 / 11.2 / 12.8 (-45 / -51 / -41 %) | 19.6 / 23.0 / 21.8 | 118.0 / 148.6 / 204.2 | 118.6 / 165.8 / 220.8 |
| fdae6ce9 | piece goes back only to its own source label; crossing waits t_apart only | — | **not yet run** | | | | |

Off (round 26, stand): L6 s7 b84d29 = fea1cb states 56.8 / 191.0 / 236.2; L6 s3 073429 174.6 / 212.6 / 247.4; L6 s10 e4a8a9
120.8 / 171.2 / 227.6. First state and writing on 0a519fc8: L6 s7 2,600 / 3,231 ya, s3 7,100 / 6,278, s10 5,300 / 4,882
(round 26's on runs: 2,500 / 3,231; 7,100 / 6,278; 5,300 / 4,882).

Live cultures against the read-out's (logged, `round27/live_run_dc.py`): c3e287a2 L6 s7 (e637d5) 29 against 44 (cut every step,
passing contacts merged cultures that never touch on a frame: fixed in 0a519fc8); 0a519fc8 L6 s7 34 against 43-44; L6 s10 24-29
against 45-49 with 7-8 pieces never confirmed: a piece went back to its culture when it shared a region with *any* of that
culture's land, and the founding culture's first demes lie everywhere, so most gap splits of the founding culture went back.
fdae6ce9 sends a piece back only to the label it split from (the demes' rule: a deme's own pieces rejoining within PERSIST), and
lets a crossing be a culture after t_apart without PERSIST (a crossing is a deme at once). Expected to raise the live counts,
most on L6 s10; unmeasured.

Cost: live polities' made_s on L6 s7 11.5 s (34d321) -> 37.3 s with the per-step cut (9fd701); the frame cut runs ~1/5 as often.

## 4. Next (for the lane picking this up)

1. Run the five pairs on fdae6ce9 (or later), switch on, with `round27/live_run_dc.py` (env L281D_DC=<log>.jsonl): L6 4360a3
   seeds 7, 3, 10; L7 899985 seeds 7, 10 (L7 ~35-50 min each; at most 2 at once; wait while load > 30: other lanes kept it at
   45-60 from 22:05). Measure with `round26/measure.py`; compare live cultures with the read-out's per people as in section 3.
2. If dragons are within ~25 % on all five (avg5), and states not worse than round 26 against off: same seed twice on one L6 pair;
   run `uv run pytest -m "not slow" -n 2` and the lineages / polities / settlements / techtree files incl. slow (not yet run on
   this lane's code: only the three dragon tests); then flip POLITIES_LIVE in its own commit, update tests/test_lineages.py's
   off assertion (~line 3750), re-run the tests, update goldens if outputs changed on purpose.
3. If L6 s10 stays under: the next mirror candidates are the split by distance (3 of 43 cultures on d59fa2) and the sort and
   one-merge-per-frame order of cultures._contacts (pairs by their combined size; a culture merges at most once a frame).
4. Write the table, the plain-words conclusions and the flip decision here.

Scratch at hand-off: /data/personal/scratch/lane281d/root holds **copies** only (no symlinks; `find -P ... -type l` empty) of the
two worlds and four source runs, kept for the next lane; this lane's output runs were deleted (their numbers are this table).
Logs: /data/personal/scratch/lane281d/logs. Delete the whole /data/personal/scratch/lane281d when done.

Scripts: `round27/per_people.py` (per dragon people: regions, cultures, live and read-out realms at a run's frames),
`round27/live_run_dc.py` (round19/live_run.py logging the live dragon cultures).
