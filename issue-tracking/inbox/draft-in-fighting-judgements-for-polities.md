---
title: "In-fighting for every people: its size and its state rule are judgements, parked for the war and polities work"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane101
blocked_by: []
relates: [PW-1240, PW-1172, PW-1241, PW-661]
refs: [planet/lineages/history/counter.py, planet/lineages/history/params.py, docs/review/peoples-leader/data.json]
---

## Description
**In plain words.** Every people now fights itself where it has filled its land and has nowhere to split off to (your D31: "humans
ought also be infighting"). The mechanism comes from sources lane 101 read; the sizes do not. You said to stop fiddling with this
until war and polities are in, so these are parked for that work, not for now:
- **How big** (FEUD_CUT 0.35): a people that fills its land and is walled in all round loses up to a third of it. That is lane 97's
  size for the kobolds at the default, carried to everyone. In practice a people settles at about 1 / (1 + 0.35 x C) of its land, C its
  circumscription (0 to 1).
- **How leaky other peoples' land is** (SOCIAL_Q 0.5): land held by other peoples counts as half a wall, sea and land nobody can live
  on as a full wall. Carneiro 2012 says social circumscription is "generally less tight" than a physical one; the half is a judgement.
- **States**: in-fighting is not damped by states (the war-torn-land term is). Turchin's cycles say crowded agrarian states do fight
  inside; Gomez et al. 2016 say states pacify. The polities work should decide how a state changes it.
- **Its dial**: in-fighting now sits under "how warlike the peoples are" (meta.war), for everyone; the raiders' dial keeps the raids
  and culls only.
- **The leader brake through war deaths** (PW-1172's deaths, built and measured by lane 101, then dropped on your ruling): at the
  sourced violent-death rates it took 0-0.2% of any people's numbers and did not move the commonest share. The life tables already
  hold the violence of the peoples they were measured on, and state farmers (the humans) are the least violent row. Plague (PW-1167)
  is the sourced brake on a dense farming leader if one is wanted later.

- [ ] revisit with the war and polities work (PW-1172, PW-661)

## Updates
- 2026-10-31: Created by lane 101.
