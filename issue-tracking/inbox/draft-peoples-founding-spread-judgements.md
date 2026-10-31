---
title: "Owner call: a new people founds at 3 sites within one jump length (800 km) of each other; denning peoples live in thin dens off broken country"
type: task
status: needs-decision
parent: PW-917
milestone: v2
subsystem: timezoom
effort: xs
impact: med
found_by: lane97
blocked_by: []
relates: [PW-1218, PW-1217, PW-1207]
refs: [planet/lineages/history/origins.py, planet/lineages/history/params.py, docs/review/peoples-brakes/report.md]
---

## Description
**In plain words.** Your D27 idea is in: a new people now starts at three places spread over one landmass, not one spot. Each place is
within one long walk (800 km, your 10-27 walking jump) of the first, so the founder region spans up to about 1,600 km. The founders are
as many as before, shared among the three places. On the stress suite it cut the runs that break a rule from 4 to 1, and the peoples
flagged as brittle in the full dnd tree from 12 to 8 (humans are no longer one of them). I also took your option C for the kobolds and
goblins: away from mountains and hills they live in thin dens (a quarter of their density) instead of hardly at all. Numbers:
docs/review/peoples-brakes/report.md, stage 1.

Judgement calls in it, each with what was screened (one try per seed, seeds 7 and 10, both worlds):
- **3 sites.** Five sites over 1.5 jump lengths did no better on balance: it rescued the one five-people try with humans at 1-3%
  (to 20%), but lost the kobolds' rescue in the three-people tree. 3 is in the spirit of the few regional groups behind our species
  (Scerri et al. 2018; Ragsdale et al. 2023), not a measured number.
- **One jump length.** Half a jump length founds at one site on the L6 grid (the sites must clear each other's founding blobs), so it
  is the same as before.
- **Thin dens (PW-1218 C).** Screened on the founding spread: the three-people tree's kobolds went from 1-2% to 17-20% in two of
  four tries; in the full tree they stayed at 2-5%. Lane 83b's worry (thin dens contesting open country with everyone) did not show.
- **Kept: the filled-people jump (PW-1217 A).** The five-people try that put humans at 2.6% (af2677, seed 7) is still there at 1.3%
  with the founding spread; with five sites it was 20%. It is a draw on where the humans are born, not the jump rule alone, so I kept
  the rule and did not build B (B is close to the existing JUMP_HEMMED test, which already blocks jumps while there is room next door).

Options:
- A. Keep all of it.
- B. Five sites over 1.5 jump lengths.
- C. Back to lane 83's habitat cut for denning peoples.
Lean: A.
