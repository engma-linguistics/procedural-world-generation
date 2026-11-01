# Peoples: in-fighting for everyone, a floor that holds, D31 A as a check (lane 101)

Lane 101, 2026-10-31. Written by the coordinator from the lane's final report (the lane could not write report files).
Charts: [commonest-by-stage.png](commonest-by-stage.png), [top6-by-stage.png](top6-by-stage.png). Data: [data.json](data.json).

## In plain words

Every people now fights among itself when it is crowded and walled in, humans included, as Daniel asked (D31). The brakes can
no longer end a people: they can thin it, but never take its land. Daniel's D31 A (the commonest people usually under half,
never over 70% with five or more peoples) is now a reported check in the stress suite, not a failure.

**The finding:** in-fighting for everyone does not shrink the leader; it grows it a little. Humans hold the most open country,
so they are walled in least and pay least (8% of their land, against 9-12% for elves, dwarves, hobgoblins and kobolds). The
commonest share in the full dnd tree went from a median of 47% to 56%. Per Daniel, peoples-share work now stops until war and
polities are built. The lever that brings the leader down belongs there.

## What was built

- **In-fighting** for every people: on each cell a people keeps 1 − war × 0.35 × C × u of its land. u is how full the people
  has made the land it lives on. C is how walled in it is, over the cells next to its land: free good country 0, land other
  peoples hold 0.5, sea (for a people that does not sail) or unlivable land 1. It sits under the "how warlike" dial; the
  raiders' dial now covers raids and culls only. Sources read: Carneiro 2012 (circumscription comes in degrees; walls of
  neighbours leak more than physical ones), Chagnon's PNAS profile 2014, Walker and Hill 2014 (abstract only). The 0.35 and
  0.5 are judgements, parked for war and polities.
- **The floor holds numbers:** on a cell a people holds, the brakes never cut its habitat below 0.24 (BRAKE_HOLD). No people
  was lost to a brake.
- **D31 A, reported:** median commonest share, share of tries under half, share of 5+-people tries at or under 70%.
- **War deaths through the life tables** (PW-1172): built, measured (0-0.2% of any people, no move in the commonest share),
  dropped and parked, per Daniel.

## Stress suite (86 tries, 82 counted)

| | main 79ad5aa5 | raiders only | every people (merged) |
|---|---|---|---|
| commonest, dnd 4360a3 / af2677 | 61 / 31% | 66 / 27% | 64 / 37% |
| commonest, Seven Meals 4360a3 / af2677 | 43 / 30% | 42 / 35% | 46 / 34% |
| commonest, dnd3 4360a3 / af2677 | 100 / 90% | 100 / 88% | 99 / 86% |
| commonest, dnd5 4360a3 / af2677 | 62 / 57% | 62 / 57% | 67 / 60% |
| invariant fails | 5 | 4 | 7 |
| brittle peoples, dnd / Seven Meals | 10 / 4 | 10 / 2 | 9 / 5 |
| D31, all tries: median / under half / 5+ at or under 70% | 52% / 49% / 94% | 50% / 49% / 96% | 53% / 48% / 86% |
| D31, full dnd tree (34 tries) | 47% / 53% / 94% | 46% / 53% / 100% | 56% / 47% / 85% |

The seven fails: four dnd3 tries (humans 86-100%), and three Seven Meals tries on af2677 where the half-orcs are never
founded (they found only where humans and orcs meet 10 kyr ago, and the orcs there are tiny). No brake kills them.

## PW-1239 (after the inland pits), on re-rolled draws

48 tries a side, before and after PW-1229. The humans' brittleness is chance (one or two bad af2677 jitters in both codes).
Seven Meals on 4360a3 37 → 40% is chance (p 0.37). Seven Meals on af2677, humans 24 → 29%, is real (p 0.01). The three-people
tree on 4360a3 is 99% human even with the raiders' dial off: that comes from the land, not the brakes.

## Drafts

- in-fighting judgements, parked for war and polities
- half-orcs never founded when their parents do not meet
- dnd3 on 4360a3: humans 99% without brakes
- Seven Meals af2677: humans up after the pits
