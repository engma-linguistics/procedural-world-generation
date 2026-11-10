# Polities round 24: why the first state's date differs with polities in the history on and off (PW-1596, PW-1597; lane 281)

## 1. Diagnosis from the code (written before any run; main caa44c4d)

**Where each "first state" comes from.** The measure (`round16/measure_v1.py` -> `round14/measure.py::one`) takes the oldest step
whose map holds a state or empire. With the switch on, `polities.derive` (polities.py:476-477) returns `_from_live`: the map is the
one the history drew step by step (`history/polity_live.py::LivePolities._step`). With the switch off, `derive` makes its own map
after the run from the settlement ledger (polities.py:478-...). So the two first states come from **two different seat tests on
two different inputs**, not one gate run twice.

**The gate is the same rule.** Both make a seat a state when its people knows kingship or law and real writing, it is not cooling
after a fall, and its place is at least `city_min x (1 - HEMMED_X x hemmed)` (polities.py:571-575; polity_live.py:536-541). The
live test also asks for the `cities` tech outright (polity_live.py:537); the ledger asks it implicitly by capping a town of a people
without `cities` at TOWN_CAP 5,000 (settlements.py:89, 715), which passes the need only at hemmed = 1 exactly. A near-equivalence,
not a likely cause.

**The inputs differ in three ways:**

1. **The place's size.** Live: the history's own central place this step, SHARE x the hinterland's sedentary heads x site factor
   at a best-of-ring cell (polity_live.py:236-267, 511-519). Off: the ledger site's stored population series
   (`polities._site_tables`, polities.py:424-437). The ledger keeps SERIES_KEEP = 40 points per site plus each turn of its size
   class (settlements.py:104, 187, 1000-1003), and `_site_tables` reads it back **by straight lines between the kept points**
   (`np.interp`, polities.py:434). Round 23 kept the town and city turns, so a place reads back on the right side of town_min and
   city_min. But **a state's need is not a size class**: for a hemmed seat it is anywhere between 5,000 and 10,000
   (`city_min x (1 - 0.5 x hemmed)`). A site that grows past that need between two thinned points (40 points over a site's life:
   gaps of several centuries for an old town) reads across it early or late by up to the gap. The same look-ahead round 23 removed
   from the town footprint, at a threshold round 23 did not keep. Over a long-lived town's growth this can be centuries.
2. **The calendar.** Live: the live tree (`LivePolities.knows` -> `tech_live`). Off: the after-run tree (meta.techtree). Round 23
   brought the 12 largest peoples' writing *median* within a tree step; the first state reads the *earliest* people to hold kingship
   or law, writing and a city, a tail, which the median does not bound.
3. **The history itself.** On and off share their history until about 7,000 years ago (round 23 section 1; the first state on all
   five pairs comes after 7 kyr), and then the live polities feed it (pacification, wars, fates, the frontier). Who is big where at
   3.5-6.8 kyr can legitimately differ.

**Time sampling.** Both step on the century grid; live tests at the start of the step (`begin_step`, on the state the last step
ended with), derive at each step's frame at or before it (`_Run.frame_of`) and the ledger's series at that ago. No look-ahead here
other than item 1.

**Candidate fixes**

- A (item 1, accounting): keep the series points where the site crosses any state need, or simplest, read `_site_tables` at the
  kept point at or before each step (held), as the footprint and tracks already are (lane 265, round 23). Moves only the default
  (switch off), always later or equal.
- B (item 2): none needed if the measure shows the first-state people learns its gate techs at the same step in both calendars.
- C (item 3): legitimate if the after-run read-out run on the switch-on history (same calendar, same ledger) gives the switch-off
  first state: then the gap is live polities changing the history, not either gate.

**The measure that separates them** (L7 899985 seed 7 first, the 800-year pair): run on and off; then rebuild the read-out
(`derive` with the live map hidden) on the switch-on run: (i) as is, (ii) with `_site_tables` held at or before. (i) vs on = the
gate's inputs on one history; (i) vs off = the history; (i) vs (ii) = the interpolation.

## 2. Measured (L7 899985 seed 7, dnd, 30 kyr, languages skipped; `round19/live_run.py`, `round16/measure_v1.py`, `round24/first_state.py`)

On main caa44c4d (same code on and off). Lane 278's numbers (3,500 / 4,300 on 9306190c) have moved with the merges since.

| run | first state | who, where | writing median of the 12 largest |
|---|---|---|---|
| switch on, as stored (232c82) | 3,400 ya | dwarves (kingship 3.47, cities 3.597 kyr ago in the live calendar), chief places | 5,340 ya |
| switch off (11a7fe) | 5,100 ya | gnomes: their halls, kind `minority` (second people's places), 10,000-14,000 people; law 5.152, writing 6.391, `cities` only 2.175 | 5,438 ya |
| after-run read-out on the switch-on history (232c82, live map hidden, live calendar) | **5,100 ya** | the same gnome halls, same cells | - |

**The cause.** On one history and one calendar the after-run read-out seats the first state at 5,100 years ago and the live
polities at 3,400: the whole 1,700 years is the live seat test's inputs, not the history, not the calendar, and not the
series interpolation (candidate A: the gnome halls cross 10,000 between kept points 5.7 -> 5.6 kyr, not near 5.1).
The live seat test (polity_live.py `_step` step 1, before this lane) differed from the ledger in two ways that both bar the
gnomes:
- it sized places from the history's farmers only (`_heads`' sedentary heads; `_second_places` says "No fishers or holds"),
  so a mining people's halls (settlements' HOLD_SHARE of its heads, levelling at HOLD_MAX; PW-1117: a hold may grow into a
  city) never counted: the gnomes' second-people places stayed at most MINORITY_MAX 2,000;
- it asked for the `cities` tech by name (old polity_live.py:537), where the ledger lets a mining people's `delving` or
  `fortifications` stand for cities (settlements.py:598-601), as the history's own `_allowed` does.
So the live gate is the one missing a mechanism; the read-out is the ledger's rule as designed (PW-1117). Not a legitimate
history effect: the bar's "written reason" route does not apply.

**The fix (by mechanism, one rule).** `LivePolities.town_cells` already keeps the ledger's own places step by step (PW-1608:
chief place and second people's own place per cell, halls and the miners' city rule included). The seats now read those:
`_seat_places` takes the bigger of a cell's two places, of town size for its holder's stage (x HOLD for last step's seat), as
derive seats a ledger site; the state test is the same (kingship or law, writing, cool, city_min x (1 - HEMMED_X x hemmed)),
with no `cities`-by-name check (the ledger's stage cap does it, as in derive). `end_step` now keeps the places with or without
D52's town arms. The confederations (1b) still read the history's own places (unchanged; a candidate follow-up). The seats read
the places as at the end of the last step (one step behind the ledger's step, as the tree's footprint, PW-1612 B).

## 3. State at hand-off (lane 281, ~100 tool calls)

- The fix is **not committed under planet/**: two fixtures (`test_polities_in_the_history_seat_claim_and_conquer_with_the_winners_tolerance`,
  `test_live_polities_send_a_strong_rows_expedition_across_a_gap`) seat nothing now, because `_live_setup` (tests/test_lineages.py)
  builds a bare History whose `town_cells` places never found (the fake land use's farmers are 0; forcing farm 100 was not
  enough, not found why). The diff is `round24/live_seats.patch` (`git apply` it on caa44c4d), with the test warm-up started.
  Next: make `_live_setup` grow ledger places (or give the fixture `_towns_st` directly: act/pop/holder on folk's cells), then
  the not-slow suite, then the five pairs, then the flip.
- The switch is **not flipped**: the first-state bar fails on main (1,700 years on L7 seed 7) and the fix is unmeasured on the
  five pairs.

**The fix, measured (L7 899985 seed 7, patch on caa44c4d, switch on, run e65944 against off 11a7fe on caa44c4d; the switch-off
path does not touch polity_live, so 11a7fe stands for off on the patch too):** first state **5,100 ya on, 5,100 off** (the same
gnome hall, cell 135111, site 562); writing median 5,340 against 5,438 (within a tree step). States 2,000 / 1,000 / 0 ya:
75 / 148 / 212 on against 90 / 182 / 240 off (before the patch, on: 95 / 179 / 219): the counts now run 17-19% under off at
2,000 and 1,000 years ago, 12% now. Not diagnosed; check on the five pairs with the first states before the flip.
Scratch runs deleted after the lane.
