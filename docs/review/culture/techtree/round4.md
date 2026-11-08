# Tech tree round 4: "towns or chiefdoms" for taking up state techs (D60 B wording, D62 A; lane 208)

**Baseline:** main at e6cb463c (arm S as lane 207 built it: a state tech needs a town of the people's own). The variant is main plus
`Calendar.may_take`:
- a people holding the **chiefdoms tech** may take up, share or keep a state tech without a town;
- inventing one still needs a town (D62 A).

Both trees are rebuilt over the stored runs with lane 207's `round3/lag.py`: 8 draws each on 0141d1 and 3e0eb4 (D&D, world 899985)
and on 07c755 (Seven Meals, measured only). `round4/chiefs.py` reads the JSONs.

## In plain words

- **The variant would undo the gate, so it is not built.**
  - In the model, the "chiefdoms" tech is held by almost everyone by 500 years ago: 96% of peoples with hands on 07c755, and 100%
    on 0141d1 and 3e0eb4. It is ranked leadership as know-how, and it spreads like any other know-how (it needs villages and
    feasting).
  - So "holds chiefdoms" lets nearly every people without a town take writing up:
    - Writing held 500 years ago, main → variant: 62% → 94% of peoples (07c755), 79% → 97% (0141d1, 3e0eb4).
    - Among peoples without a town of their own within living memory: 6% → 89% (07c755), 33% → 89% (0141d1), 40% → 90% (3e0eb4).
    - Mobile peoples (foragers, herders, sea nomads) without towns: 7% → 93% on 07c755 (13 of 14 hold chiefdoms), and the single
      one on each D&D run goes 0% → 100%.
  - That is the opposite of the record. Writing was taken up by peoples with chiefs (runes, Ogham, the Tuareg), but not by
    nearly every forager band (`writing_without_towns.md`).
- **The wording is still right; the model's "chiefdom" is the wrong reading of it.** Daniel's "towns or chiefdoms of its own" means
  a people that **is** a chiefdom: one with a chief's seat and ranked rule over land. It does not mean one that merely knows the
  idea. The model has that thing too: the polities' chiefdom tier (`polities.derive`, and the live polities' seats). But it is not
  wired into the calendar's footprint.
- **Where it stands.** Main's rule (towns only) is unchanged. The choice is in the inbox draft `draft-chiefdom-seat-uptake.md`
  (needs-decision, lean: read a chiefdom seat of its own).

## Numbers

Median of 8 draws [min-max]; shares of peoples with hands at 0.5 kyr ago. "Not settled" is arm S's own reading at 0.5 kyr ago
(`settled_05` in lag.py): no town of its own within living memory; a group or overlay as its hosts.

| | 07c755 main | 07c755 variant | 0141d1 main | 0141d1 variant | 3e0eb4 main | 3e0eb4 variant |
|---|---|---|---|---|---|---|
| writing | 62% [58-62] | 94% [88-94] | 79% [21-79] | 97% [21-97] | 79% [79-83] | 97% [97-97] |
| kingship | 62% [58-62] | 94% [88-94] | 79% [3-79] | 97% [3-97] | 79% [69-83] | 97% [86-97] |
| chiefdoms | 96% [90-96] | 96% | 100% | 100% | 100% | 100% |
| not settled: peoples | 18 | 18 | 9 | 9 | 10 | 10 |
| not settled: writing | 6% | 89% [83-89] | 33% [11-33] | 89% [11-89] | 40% [40-50] | 90% |
| not settled, without chiefdoms: peoples | 1 [1-2] | 1 | 0 | 0 | 0 | 0 |
| not settled, mobile way: peoples | 14 | 14 | 1 | 1 | 1 | 1 |
| not settled, mobile: writing | 7% | 93% [86-93] | 0% | 100% [0-100] | 0% | 100% |

- 0141d1's low draw (21% writing on both trees) is lane 207's known late-writing draw (round3.md, section 2b), unchanged.
- The not-settled peoples that write on main (33-40% on the D&D runs) are groups and overlays settled as their hosts, or peoples
  whose towns lapsed after they took writing up. Knowledge already held is never lost.

## Files

- `round4/chiefs.py`: the table.
- Runs: `round3/lag.py` from main e6cb463c and from the variant, 8 draws per run. The JSONs were in the lane's scratch and are gone
  after it; re-run with `PLANET_DATA=<main checkout> python round3/lag.py RUN 8 out.json 2`.
- The variant's code was `Calendar.may_take` (lane 208 commit d90f8d64, reverted in the same lane):
  `"chiefdoms" in self.known[lid] or self.settled(lid, ago)`, read for uptake, sharing, keeping and carrying, not for inventing.
