# Tech tree round 5: "a chief seat of its own" for taking up state techs (PW-1512 option C; lane 215)

**Baseline:** main at 96dd22aa (arm S: a state tech needs a town of the people's own). Option C was **measured, not built**: the
variant is main plus "a people that rules land as a chiefdom or higher in `polities.derive` within its living memory may take up,
share and keep a state tech; inventing still needs a town". Both trees are rebuilt over the stored runs with lane 207's
`round3/lag.py`, 8 draws each, on 0141d1 and 3e0eb4 (D&D, world 899985) and 07c755 (Seven Meals).

## In plain words

- **Option C changes nothing, so it is not built.** On all three runs, writing among peoples without towns, among mobile peoples
  and overall is the same as main's, within one people in a few draws.
- **Why: in the model, a chiefdom seat *is* a town.** `polities.derive` seats a chiefdom only at a living place of town size held by
  the people (the same places and the same town size the town footprint reads; `planet/lineages/polities.py` step 1). So "rules
  land as a chiefdom" is almost the same set of peoples as "has a town". The live polities seat the same way (`polity_live._step`).
- **Derive's chiefdoms are not near-universal** (the brief's stop test): at 500 years ago 20 of 48 peoples with hands rule land on
  07c755, 20 of 29 on 0141d1 and 17 of 29 on 3e0eb4. Every one of the 20 / 18 / 16 that have a town counts already.
- **The few rulers without a town already write.** Among the peoples without a town at 500 years ago (18, 9 and 10), only 0, 2 and
  1 rule land: goblins and sea elves on 0141d1, dragonborn on 3e0eb4. They rule as confederations (polities step 1b), which need
  real writing first. On 3e0eb4 the variant moves one of the ten in a few draws (40% → 45% median).
- **The peoples the gate is about have no places at all.** Every people without a town that does not write on these runs (giants,
  and on 07c755 the foragers, fisher-foragers, herders, sea nomads and transhumants) holds **no place of any size** in the settlement
  ledger at 500 years ago (`round5/camps.py`). The ledger books no camps for mobile peoples. So nothing read from places, seats or
  polities can tell a Tuareg-like chiefly herder from a band: both are absent from it.
- **Where it stands.** Main's rule (towns only) is unchanged. PW-1512 stays open with this result; making mobile chiefdoms visible
  is a model change (a people-level reading, or camps in the ledger), a judgement for Daniel (see the ticket's update).

## Numbers

Median of 8 draws [min-max]; shares of peoples with hands at 0.5 kyr ago. "No town" is arm S's own reading at 0.5 kyr ago
(`settled_05` in lag.py). `round4/chiefs.py` reads the JSONs.

| | 07c755 main | 07c755 C | 0141d1 main | 0141d1 C | 3e0eb4 main | 3e0eb4 C |
|---|---|---|---|---|---|---|
| writing, all | 62% [58-62] | 62% [58-62] | 79% [21-79] | 79% [21-79] | 79% [79-83] | 81% [79-83] |
| kingship | 62% [58-62] | 62% [58-62] | 79% [3-79] | 79% [3-79] | 79% [69-83] | 79% [72-83] |
| no town: peoples | 18 | 18 | 9 | 9 | 10 | 10 |
| no town: writing | 6% | 6% | 33% [11-33] | 33% [11-33] | 40% [40-50] | 45% [40-50] |
| no town, mobile way: peoples | 14 | 14 | 1 | 1 | 1 | 1 |
| no town, mobile: writing | 7% | 7% | 0% | 0% | 0% | 0% |

Main's numbers at 96dd22aa equal lane 208's at e6cb463c (round4.md) on every row: the trade lanes since did not move the tree.

Who rules land (`round5/seats.py`, `polities.derive` on the stored tree; at 0.5 kyr ago, within living memory):

| run | peoples with hands | with a town | rule land | rule land, no town | rule-steps (all time) without a town |
|---|---|---|---|---|---|
| 07c755 | 48 | 30 | 20 | 0 | 1 of 1,327 |
| 0141d1 | 29 | 20 | 20 | 2 (goblin, sea elf: both write) | 18 of 1,012 |
| 3e0eb4 | 29 | 19 | 17 | 1 (dragonborn: writes) | 21 of 1,099 |

## Caveats

- Derive reads the stored tree, so its seats already reflect main's writing gate (a chiefdom seat needs proto-writing or writing,
  its own or a neighbour's). In a built version the live polities would read the calendar as it runs; that cannot add peoples
  without places, which is where the gap is.

## Files

- `round5/seats.py`: who rules land against who has a town (one run; `PLANET_DATA` = the main checkout; ~90 s for derive).
- `round5/camps.py`: the places (any size) of the peoples without a town, from the settlement ledger.
- `round5/variant.py`: lag.py with option C patched in (not shipped code). Run as `variant.py RUN 8 out.json 2`.
- `round3/lag.py` (lane 207) and `round4/chiefs.py` (lane 208), unchanged. The JSONs were in the lane's scratch and are gone.
