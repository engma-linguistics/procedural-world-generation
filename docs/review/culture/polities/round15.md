# Polities round 15: the read-out draws the live map (PW-1575; lane 238)

## In plain words

- **Before:** with polities in the history switched on (`params.POLITIES_LIVE`), a run had two polity maps. One was the live map
  (`polities_live.json`), whose polities fought inside the history and decided which peoples were kept, thinned or expelled. The
  other was the read-out (`polities.derive`), a second set that the viewer's Polities layer, the state cards, the religion
  read-out's rulers and the nudge checks showed.
- **Now:** when a run has `polities_live.json`, `derive` draws those polities (`polities._from_live`). It keeps the history's steps,
  maps, tiers, falls and conquests as they were. The read-out adds only its own part:
  - the capital's town from the ledger;
  - the ruling culture per step (`_ruler_culture`);
  - the subject cultures and settled people;
  - names, colours and why each polity fell.
  Polity ids are the same in both files, so polity N in the history is card N in the viewer. With the switch off there is no file,
  and the read-out is byte-identical to before (section 2).
- **What the history now records (format `procgen-polities-live/2`):**
  - Each map entry carries the people holding the seat and its provinces (the cells taken in war, by the polity they were taken from).
  - Each conquest carries the loser's record id.
  - A conquered record carries `fell_by`.
  - Each invasion log's "took" row carries both record ids.
  All of this is record-keeping only. The history's dynamics are unchanged: Daniel's D56, D59, D61 and D67 are untouched.
- **The card** now also says how the peoples on the land each conquest took fared ("the conquered: X: the kobolds expelled
  (~100 lost) (~20 fled)"). That is v4's done-when 2.
- **Invasions:** the read-out shows the rows the history ran with. If authored.json has changed since, the read-out says that a
  changed row acts only when the peoples are run again.
- **The switch stays off.** The single pair measured (section 3) does not support flipping it: on, the states are fewer and much
  smaller. That is filed as a draft (`draft-live-polities-stay-small.md`).

## 1. Proof: the viewer, the cards and gods name the live polities

Switch-on run f4fb14 (world 4360a3, L6, dnd tree, seed 7, 30 kyr; scratch, lane 238). `round15/check.py` reads it read-only:

- 83 live steps and 2,171 live polities. The read-out has 126 steps (43 empty ledger steps before the first live polity, 8.2 kyr
  ago) and the same 2,171 polities, key for key.
- Map steps that differ from the live map (polity, tier, cells): **0 of 83**.
- `/api/polities` (server.polities, in process): 200 with 2,171 cards. At ago=0, 324 polities. Each of the five largest has the same
  cells as the live map, and its card is named for the live seat's people. For example, #1997 "South-east of Gugiki (humans) 12" is
  live key c29742, people human, and its ruling culture is "first humans of the south-east of Gugiki".
- Conquests on the cards: 93, as in the live file. 72 of them name the fates of the peoples on the taken land; the rest took land
  where only the winner's own kin lived.
- How the polities fell: collapsed 574, faded 1,180, conquered 93; 324 still stand.
- gods.py's `rule_table` on this doc: 62 realms now, **all of them live polities**, each ruled by its live seat people's culture.
- Tests: `tests/test_polities.py::test_with_polities_in_the_history_the_read_out_draws_the_live_map` (a stand-in run: the map,
  names, rulers, subjects, provinces, the fall "conquered by", the fates on the card, step_view and gods' rule_table) and
  `::test_the_read_out_refuses_an_older_live_file`.

## 2. Switch off: nothing changes

The read-out of the switch-off run 6418c8 (same world, tree and seed) is hashed with main's code and with this branch's code, after
dropping `made_s`. Both give `672cb57c…` (9,304 polities). The goldens did not move.

## 3. On and off, one column each (round 14's measure.py)

| run | first state | states 2,000 / 1,000 / 0 ya | largest, last 3 kyr: median / peak / now (Mkm²) | most > 1 Mkm² | writing (12 largest) |
|---|---|---|---|---|---|
| f4fb14, on (live = read-out) | 2,500 ya | 40 / 57 / 68 | 0.21 / 0.44 / 0.22 | 0 | 11/12, median 2,511 ya |
| 6418c8, off (read-out) | 2,800 ya | 66 / 116 / 120 | 0.40 / 2.28 / 1.57 | 4 | 12/12, median 2,899 ya |

On the switch-on run, measure.py's "live" and "readout" rows are now identical (PW-1575's second box). On vs off: the history's
states form about 300 years later and are about half as many. Their largest is about half the off median and a fifth of the off peak.
One seed on L6 only; lane 234's L7 queue (seeds 7 and 10, on and off) will tell whether this holds. The history has no
confederations (polities' step 1b), which is one candidate (draft).

## 4. PW-1488 (two attitude walks)

PW-1488 is now unblocked, but it was not done here. Option A (gods.py takes each culture's temperament from its people's walk in the
history) does not fall out of this change, for three reasons:
- the history samples each people's axes only every TRACK_KYR (0.5 kyr);
- the history has no town term (PW-1520's URBAN_TOL is gods-only) and no religious-tolerance memory of missionary faiths;
- the history's contact term counts peoples, not cultures.
So Option A needs these judgement calls first: keep gods.py's own contact and town terms on top of the people's value, or not; and
should the history record its walk every century? Noted on PW-1488.
