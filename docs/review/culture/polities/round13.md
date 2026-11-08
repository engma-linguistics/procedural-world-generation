# Polities round 13: a revolt brings the harsh fate back (PW-1513, desk D67 option B, switch; lane 215)

**Baseline:** the same code with the switch off (`polity_live.REVOLT = False`, the default), which is main at 96dd22aa. The off runs
reproduce round 12's branch numbers exactly (seed 7: 184 kept, 9 submitted, 4 thinned, 104,673 heads lost; seed 10: 578,717; seed 3:
941,806). World 899985 (L7), dnd tree, seeds 7, 10 and 3, round 10's six strong invasion rows, polities in the history on.
Script `round13/live_run.py` (round 12's with the switch), measured by `round12/measure.py` and `round13/revolt.py`.

## In plain words

- **What the switch does.** A people that submitted to a conqueror and later **rises against it** has broken its terms. When the same
  ruling people next takes land it lives on, it may not submit again: it meets the fate the winner's attitudes give it then (thinned,
  driven out or razed, or kept if the winner is mild by then). This is Herat (spared, rebelled, massacred in 1222).
- **What "rises" means in the model.** There is no faction-split event in the history (the in-fighting brake is a smooth cut, not an
  event), so the rising is read from the polities themselves: the submitted people seats a polity of its own on a cell its ruler held
  last century, while that ruler's polity still stands. No new number. After the retaking, the mark is spent: the people may submit
  again later.
- **How often.** Submitted peoples that later rose, of the people-ruler pairs that submitted: 4 of 6 (seed 7), 7 of 13 (seed 10),
  9 of 21 (seed 3). Most risings were retaken by the same ruler: 3, 14 and 9 retakings.
- **What it costs.** Heads lost to conquest over the run, switch off → on:
  - seed 7: 0.10 M → 0.11 M (one dwarf thinning; the hobgoblins kept the others).
  - seed 10: 0.58 M → 2.14 M. Razings 17 → 21. The orcs razed humans who had risen against them (1.12 M heads in one retaking, at
    600 years ago) and hobgoblins (0.23 M).
  - seed 3: 0.94 M → 1.00 M. The retakings there were mostly by tolerant humans, who kept the risers (5 of 9 kept).
- **So it does what D67 B asked, where it matters:** a martial winner (seed 10's orcs, leonins and dwarves) now razes peoples that
  rose against it, and a tolerant winner still keeps them. Submission stays the first answer (42-58 submissions per run with it on).
- **The present population does not move:** 856.0 / 856.0 M (seed 7), 928.0 / 928.0 M (seed 10), 1,013.6 / 1,013.7 M (seed 3).
- **Default: off**, until Daniel rules on D67.

## Numbers (history, switch off / on)

| seed | run | kept | submitted | thinned | expelled (moved) | razed | heads lost | heads moved |
|---|---|---|---|---|---|---|---|---|
| 7 | off a1d20f | 184 | 9 | 4 | 0 | 0 | 104,673 | 0 |
| 7 | on bcafb5 | 184 | 8 | 5 | 0 | 0 | 107,201 | 0 |
| 10 | off 5d2be3 | 175 | 52 | 7 | 1 | 17 | 578,717 | 13,905 |
| 10 | on 58e554 | 175 | 42 | 12 | 2 | 21 | 2,142,800 | 41,074 |
| 3 | off 00b2a5 | 365 | 60 | 18 | 23 | 0 | 941,806 | 8,267,399 |
| 3 | on 19c123 | 373 | 58 | 20 | 23 | 0 | 1,004,712 | 8,267,399 |

The switch's own record (on runs; `polities_live.json` "revolt"):

| seed | submissions (pairs) | risings (pairs) | retaken | retaken fates | heads lost / moved in retakings |
|---|---|---|---|---|---|
| 7 | 8 (6) | 4 (4) | 3 | kept 2, thinned 1 | 2,528 / 0 |
| 10 | 42 (13) | 16 (7) | 14 | razed 6, thinned 6, expelled 1, kept 1 | 1,585,917 / 27,169 |
| 3 | 58 (21) | 11 (9) | 9 | kept 5, thinned 3, expelled 1 | 170,846 / 36,394 |

- Risers on seed 10: humans against the orcs and leonins, hobgoblins against the orcs, dwarves and leonins, orcs against the dwarves
  and leonins. One pair can rise more than once (humans against the orcs: 5 times), after each retaking spends the mark.
- Counts other than the retakings move a little between off and on because the history diverges after the first harsher fate.

## Caveats

- The rising is the polities' own seat-and-claim rule, which is coarse: a ruler whose reach shrinks (a fall to chiefdom, a lost
  province) can leave a submitted people's town free to seat, which the rule reads as a rising. It is the only discrete "against the
  ruler" event the model has.
- FATE_MAX (10% of a people's heads per step) still caps every cut; seed 10's 1.12 M is within it.

## Files

- `planet/lineages/history/polity_live.py`: `REVOLT`, `LivePolities._risings`, the submit test in `_fates`; the record in `doc()`
  (only with the switch on).
- `round13/live_run.py`, `round13/revolt.py`; `round12/measure.py` (unchanged). Runs were in the lane's scratch data root, gone after.
