# Polities round 26: confederations on the ledger, one dragon realm per dragon people, the five pairs, and the flip (PW-1596; lane 281c)

Lane 281c follows round 25 section 4: (1) the live confederations read the ledger's places (PW-1671); (2) the five pairs on and
off on one commit; (3) the same seed twice; (4) the flip if the bar holds.

## 1. Confederations read the ledger's places (PW-1671), commit c489e2ca

Step 1b of the live polities (`LivePolities._confederations`) now reads town_cells' places (`_ledger_places`): each cell's chief
place and second people's own place, any size, each its holder line's; a line's heads on a cell are its places there summed over
both slots, as the read-out sums a people's sites, and each place is a candidate seat as the read-out's sites are (last step's seats
first, then the biggest). `_places`, `_second_places` and `_site` are gone. Tests: the confederation test now passes the two slots
(same 12,000 / 9,600 cases, plus one where a second-slot place of the same people tops the sum up to a city's worth); the PW-1587
test now grows town_cells' places from nothing with and without a harbour (a harbour marked on land changes nothing; the harbour
beside a coast is a town, the best of its ring, and bigger by the site factor). Not-slow suite 2020 passed, 15 skipped; lineages /
polities / settlements / techtree files incl. slow 233 passed.

Measured on L7 899985 seed 7 (section 3, run 4f36cb): standing confederations live / read-out on the same history 4 / 4 at 2,000
ya, 16 / 16 at 1,000 ya, 16 / 19 now (round 25 on 8ba3d691, run 560796: 4 / 9, 11 / 23, 17 / 21). The gap is closed.

## 2. A bug found on the way: the dragon realms (commit 06187f53)

Round 25's dragon fix (`is_dragon`) made the history seat dragon realms for the first time, one per *connected piece* of a dragon
people's range. On L6 4360a3 seed 7 (switch on, c489e2ca, run 22b8f9, now deleted) that seated **290-310 dragon realms** at 2,000 /
1,000 / 0 ya against the read-out's 22-25 on the same history; the live states fell to 54 / 130 / 189 (five-step averages) against
62 / 176 / 233 for the read-out on the same history, because 300 realms each claim DRAGON_KM of settled land. The keys also moved with
each piece's densest cell every step, so no realm kept its record. A dragon people's stored range (`round26/dragon_ranges.py` on
22b8f9) is 600-1,200 scattered pieces; joining pieces within a dragon's flight still leaves ~300 (wider joins: 100 at ~720 km); the
read-out's 45 dragon cultures alive (the cultures engine's clusters) make its 22-25 realms. The history has no cultures.

Fix: one realm per dragon people (the read-out's one per dragon culture; a dragon kind is one culture for now), at the core of its
range by the read-out's own rule (`polities._core`), keyed by the people. With a test. This **under**-seats against the read-out:
4-6 live realms against 16-26 (table). That is the main open gap (section 5, draft 1).

## 3. The five pairs (dnd, 30 kyr, languages skipped; `round19/live_run.py`; scratch root /data/personal/scratch/lane281c/root)

On: commit 06187f53. Off: commit c489e2ca; the off path does not import `polity_live`, and neither commit after it touches anything
else, so these stand for off on 06187f53 (round 25's argument). Off L6 seed 7 and L7 seed 7 equal round 25's off runs fdee9d and
5f4b2e in every number, which checks that. States = states and empires; avg5 = mean of the five steps around the date (2.2-1.8,
1.2-0.8, 0.4-0 kyr ago). RO-on = the read-out on the switch-on run's own history (derive with the live map hidden). Measures:
`round26/measure.py`.

| pair | run | first state | writing median (12 largest) | states 2,000 / 1,000 / 0 ya | states avg5 | confederations | confeds avg5 | dragon realms | dragons avg5 |
|---|---|---|---|---|---|---|---|---|---|
| L6 4360a3 s7 | off b84d29 | 2,600 | 3,288 | 53 / 214 / 232 | 56.8 / 191.0 / 236.2 | 8 / 14 / 24 | 5.6 / 11.0 / 17.8 | 23 / 23 / 25 | 22.0 / 24.0 / 25.6 |
| | on 242ac7 | 2,500 | 3,231 | 56 / 141 / 241 | 56.0 / 166.8 / 224.6 | 3 / 13 / 18 | 3.8 / 11.2 / 18.6 | 4 / 4 / 4 | 5.2 / 5.2 / 5.4 |
| | RO-on 242ac7 | 2,600 | | 66 / 153 / 232 | 61.4 / 178.4 / 235.0 | 8 / 13 / 18 | 5.8 / 14.2 / 20.2 | 23 / 21 / 22 | 21.8 / 22.4 / 22.8 |
| L6 4360a3 s3 | off 073429 | 7,100 | 6,278 | 166 / 208 / 256 | 174.6 / 212.6 / 247.4 | 19 / 18 / 28 | 17.8 / 15.4 / 22.2 | 17 / 20 / 24 | 17.0 / 21.2 / 21.8 |
| | on 2f4a37 | 7,100 | 6,278 | 198 / 224 / 264 | 171.6 / 205.4 / 231.8 | 10 / 19 / 17 | 14.8 / 16.4 / 16.6 | 5 / 5 / 7 | 4.0 / 6.0 / 5.8 |
| | RO-on 2f4a37 | 7,100 | | 174 / 199 / 239 | 170.2 / 204.6 / 239.0 | 16 / 20 / 17 | 14.0 / 17.4 / 19.8 | 18 / 17 / 26 | 17.6 / 19.2 / 24.8 |
| L6 4360a3 s10 | off e4a8a9 | 5,500 | 4,882 | 114 / 161 / 215 | 120.8 / 171.2 / 227.6 | 18 / 13 / 17 | 15.8 / 16.8 / 18.8 | 15 / 23 / 22 | 20.2 / 24.0 / 22.4 |
| | on 09d261 | 5,300 | 4,882 | 102 / 157 / 202 | 116.0 / 156.8 / 201.0 | 9 / 13 / 14 | 10.8 / 10.2 / 13.6 | 6 / 6 / 4 | 4.0 / 4.4 / 4.4 |
| | RO-on 09d261 | 5,300 | | 110 / 160 / 197 | 117.4 / 169.0 / 215.6 | 17 / 13 / 8 | 15.0 / 14.4 / 12.6 | 16 / 23 / 21 | 20.4 / 23.0 / 22.0 |
| L7 899985 s7 | off 599ac3 | 5,100 | 5,438 | 90 / 182 / 240 | 96.2 / 184.2 / 232.8 | 6 / 15 / 18 | 4.4 / 14.6 / 17.0 | 19 / 18 / 14 | 19.0 / 17.8 / 14.2 |
| | on 4f36cb | 5,100 | 5,340 | 78 / 154 / 215 | 92.4 / 174.6 / 223.0 | 5 / 16 / 16 | 4.0 / 13.4 / 16.4 | 5 / 3 / 5 | 4.4 / 4.0 / 4.2 |
| | RO-on 4f36cb | 5,100 | | 92 / 180 / 225 | 101.8 / 178.2 / 218.6 | 4 / 16 / 19 | 3.4 / 14.4 / 16.8 | 23 / 21 / 18 | 21.4 / 22.0 / 16.4 |
| L7 899985 s10 | off e0f453 | 5,100 | 4,970 | 135 / 181 / 263 | 150.8 / 205.2 / 260.4 | 9 / 14 / 25 | 12.4 / 16.8 / 22.6 | 26 / 16 / 20 | 25.6 / 20.0 / 19.6 |
| | on a96680 | 5,700 | 4,970 | 141 / 161 / 234 | 139.2 / 184.2 / 229.2 | 6 / 11 / 9 | 6.4 / 12.2 / 11.4 | 6 / 6 / 4 | 5.0 / 4.0 / 5.4 |
| | RO-on a96680 | 5,700 | | 143 / 163 / 255 | 152.4 / 191.2 / 249.6 | 15 / 17 / 19 | 11.2 / 18.6 / 15.8 | 20 / 18 / 18 | 24.2 / 18.0 / 16.0 |

On against off, states avg5: L6 s7 -1 % / -13 % / -5 %; L6 s3 -2 % / -3 % / -6 %; L6 s10 -4 % / -8 % / -12 %; L7 s7 -4 % / -5 % /
-4 %; L7 s10 -8 % / -10 % / -12 %.

**Same seed twice** (L6 4360a3 seed 7, switch on, 06187f53): 242ac7 and 0abc47 are identical: settlements.json, every layer, the lineages and the live polities' steps, maps and records byte for byte; only the timings (`made_s`, `tech_s`) differ. Deterministic.

## 4. What the numbers say (plain words)

- **When states begin and writing arrives: on track where the histories agree.** The first state is the same on L6 seed 3 and
  L7 seed 7, one century earlier on L6 seed 7, two centuries later on L6 seed 10 and six centuries *earlier* on L7 seed 10 (5,700
  against 5,100). On both of the last two the read-out on the switch-on history starts on the same date as the live polities, so
  it is the switch-on history itself (its peoples and calendar; round 23 found L7 seed 10's on and off histories part early), not
  the live seats. Writing is equal on three pairs and
  57-98 years earlier on the other two: within one tree step everywhere.
- **Confederations: closer.** With the ledger's places, live confederations are within a few of the read-out on the same
  history on four pairs; on L7 seed 10 they are still about a third under (6.4 / 12.2 / 11.4 against 11.2 / 18.6 / 15.8, five-step
  averages). The places are the same now, so what is left there is the seats and claims one step behind (round 25's lag) and which
  seats are states first; PW-1671's accounting gap is closed.
- **States: mostly within 10 %, two dates not.** On average over five steps, live states run 1-8 % under off on most dates, and
  13 % under at 1,000 ya on L6 seed 7, 12 % under now on L6 seed 10 and on L7 seed 10 (8 / 10 / 12 % under). Against the read-out
  on the same history, live is within 9 % at every date of these three (166.8 / 178.4; 201.0 / 215.6; 139.2 / 152.4, 229.2 / 249.6), so most of the gap is the switch-on history and round 25's one-step lag
  (the live seats read places as at the end of the last step), not a missing rule.
- **Dragon realms: far too few now.** One realm per dragon people gives 4-6 live realms against 16-26 in the read-out (on and off).
  That is visible on the map and in the cards (Daniel: dragons are sapient, so their realms are polities that matter), and it
  frees land the read-out gives to dragons. The read-out cuts dragons into realms by the cultures engine's clusters, which the
  history does not have; a stand-in that matches needs a design decision (draft 1).

## 5. The flip: NOT flipped

The bar (lane brief): first state within one tree step on all five pairs or an evidenced reason; writing within one step; five-step
state averages within ~10 % of off or explained; no hard failures; deterministic.

- First state: L6 seed 10 two steps later and L7 seed 10 six steps earlier, both explained (the read-out on the same history
  agrees: the history, not the seats). Pass.
- Writing: pass.
- States: four dates over 10 % (L6 s7 1,000 ya -13 %, L6 s10 now -12 %, L7 s10 1,000 ya -10 % and now -12 %), within 9 % of the
  read-out on the same history; live is under off on all 15 dates. Arguably explained (the switch-on history and the one-step
  lag), but a consistent sign.
- Determinism: pass (242ac7 = 0abc47).
- **Dragon realms 4-6 against 16-26: a hard, visible mismatch.** Flipping now would put a quarter of the read-out's dragon realms on
  every map. Not flipped. `POLITIES_LIVE` stays False; tests/test_lineages.py's off assertion is unchanged; goldens untouched.

What is left, in order: (1) decide how the history cuts a dragon people into realms (draft
`draft-live-dragon-realms-per-people-too-few.md`), then (2) re-run the five switch-on pairs (the off numbers here stand while the off path is unchanged: re-make the off runs only if a comparison needs the runs themselves) and flip.

## 6. Scratch and a slip

Runs in /data/personal/scratch/lane281c/root (symlinks to the owner's worlds 4360a3, 899985 and runs ea33de, a19366, read-only).
**Slip:** at first the time-zoom runs cdc275 and fc5311 were symlinked too, and the first L6 run rewrote the climate cache
`runs/cdc275/recent_rain.npz` in the owner's runs folder through the link (`recent._clim_write`; the cache is keyed by the
lineages code hash, which this lane's change moved). It is a cache, rebuilt on a key mismatch, so nothing is lost, but it is a
write into the owner's runs. The links were then replaced by copies in scratch. Lanes that build a scratch root should copy the
time-zoom run, not link it. Scratch: symlinks unlinked, then the whole scratch root deleted at hand-off (all runs above are gone; their numbers are this table).

Scripts: `round26/measure.py` (the table), `round26/dragon_ranges.py` (realms per cutting rule on a run's stored frames).
